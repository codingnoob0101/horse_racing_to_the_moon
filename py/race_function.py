import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Dictionaries for track conditions
turf_going_dict = {
    'Firm': 'F',
    'Good To Firm': 'G/F',
    'Good': 'G',
    'Good To Yielding': 'G/Y',
    'Yielding': 'Y',
    'Yielding To Soft': 'Y/S',
    'Soft': 'S',
    'Heavy': 'H',
}

awt_going_dict = {
    'Fast': 'FT',
    'Slow': 'SL',
    'Wet': 'WE',
    'Good': 'GD',
    'Sealed': 'SE',
    'Rain affected': 'RA',
    'Normal watering': 'NW'
}

def get_race_info(soup):
    result = soup.find('div', class_='f_fs13')
    lines = list(result.stripped_strings)

    venue = lines[1].split(',')[3].strip()
    if venue == 'Sha Tin':
        venue = 'ST'
    elif venue == 'Happy Valley':
        venue = 'HV'
    else:
        venue = 'not found'

    info = lines[2].split(',')
    track = info[0].strip()
    course = info[1].replace('"', '').replace('Course', '').strip()
    distance = info[2].replace('M', '').strip()

    if track.lower() == 'turf':
        track = info[0].strip()
        course = info[1].replace('"', '').replace('Course', '').strip()
        distance = info[2].replace('M', '').strip()
        condition = info[3].strip()
        condition = turf_going_dict.get(condition, 'Unknown')

    elif track.lower() == 'awt':
        track = info[0].strip()
        course = np.nan # store as missing
        distance = info[1].replace('M', '').strip()
        condition = info[2].strip()
        condition = awt_going_dict.get(condition, 'Unknown')
    else:
        condition = 'Unknown'
        print('track condition unknown')

    race_class = lines[3].split(',')[3].replace('Class', '').strip()

    return venue, track, course, distance, condition, race_class

def get_horse_info(soup):
    header = ['Act.Wt.', 'Jockey', 'gate_position', 'Trainer', 'Rtg.', 'Declar.Horse Wt.']
    rows = []

    table = soup.find('table', class_='starter f_tac f_fs13 draggable hiddenable')
    if not table:
        print('no table found')
        return pd.DataFrame(columns=header)

    header_row = table.find('tr')
    headers = [td.get_text(strip=True) for td in header_row.find_all('td')]

    wt_index = headers.index('Wt.')
    jockey_index = headers.index('Jockey')
    draw_index = headers.index('Draw')
    trainer_index = headers.index('Trainer')
    rtg_index = headers.index('Rtg.')
    horse_weight_index = headers.index('Horse Wt. (Declaration)')

    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) > max(wt_index, jockey_index, draw_index, trainer_index, rtg_index, horse_weight_index):
            data = [
                cells[wt_index].get_text(strip=True),
                cells[jockey_index].get_text(strip=True),
                cells[draw_index].get_text(strip=True),
                cells[trainer_index].get_text(strip=True),
                cells[rtg_index].get_text(strip=True),
                cells[horse_weight_index].get_text(strip=True)
            ]
            rows.append(data)

    return pd.DataFrame(rows, columns=header)

def get_race_horse(soup):
    all_links = []
    parti_horses = soup.find('table', class_='starter f_tac f_fs13 draggable hiddenable')
    if not parti_horses:
        print('horses table not found')
        return all_links

    header_row = parti_horses.find('tr')
    headers = [td.get_text(strip=True) for td in header_row.find_all('td')]
    if 'Horse' not in headers:
        print('no horse column found')
        return all_links

    horse_col_index = headers.index('Horse')
    for row in parti_horses.find_all('tr')[1:]:
        cells = row.find_all('td')
        if len(cells) > horse_col_index:
            td = cells[horse_col_index]
            a_tag = td.find('a', href=True)
            if a_tag:
                href = a_tag['href']
                if href.startswith('/'):
                    href = 'https://racing.hkjc.com' + href
                all_links.append(href)

    return all_links

def scrape_horses(all_links):
    header = ['Horse_name', 'Horse_id', 'Origin / Age', 'Colour / Sex', 'Import type', 'Sire', 'Dam', "Dam sire"]
    rows = []

    for ref in all_links:
        try:
            response = requests.get(ref, timeout=10)
        except Exception as e:
            print(f'Request exception for {ref}: {str(e)}')
            continue

        match = re.search(r'([A-Z]\d{3})$', ref)
        horse_id = match.group(1) if match else None

        soup = BeautifulSoup(response.content, 'html.parser')

        name_tag = soup.find('span', class_='title_text')
        horse_name = 'na'
        if name_tag:
            match = re.match(r'^([^\(]+)', name_tag.get_text())
            horse_name = match.group(1).strip() if match else name_tag.get_text()

        def get_info(label_text):
            label = soup.find('td', string=lambda text: text and label_text in text)
            return label.find_next().find_next().get_text(strip=True) if label else 'na'

        origin_info = get_info('Country of Origin')
        colour_info = get_info('Colour / Sex')
        import_info = get_info('Import Type')
        sire_info = get_info('Sire')
        dam_info = get_info('Dam')
        dam_sire_info = get_info("Dam's Sire")

        rows.append([horse_name, horse_id, origin_info, colour_info, import_info, sire_info, dam_info, dam_sire_info])

    return pd.DataFrame(rows, columns=header)

def clean_origin_age(text):
    parts = str(text).split('/')
    origin = parts[0].strip()
    age = parts[1].strip() if len(parts) > 1 else None
    return origin, age

def clean_colour_sex(text):
    parts = str(text).split('/')
    colour = parts[0].strip()
    sex = parts[-1].strip()
    return colour, sex

def obtain_odds(odds_url):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(odds_url)
        wait = WebDriverWait(driver, 20)
        odd_table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.rc-odds-table.pr')))

        header_cells = odd_table.find_element(By.CSS_SELECTOR, 'tr.rc-odds-table-header').find_elements(By.TAG_NAME, 'td')
        headers = [cell.text.strip() for cell in header_cells]

        if 'Win' not in headers:
            print('can\'t find win odds in odds url')
            return pd.DataFrame(columns=['Win Odds'])

        odds_index = headers.index('Win')
        odds = []

        rows = odd_table.find_elements(By.CSS_SELECTOR, 'tr.rc-odds-row')
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            win_cell = cells[odds_index]
            try:
                a_tag = win_cell.find_element(By.TAG_NAME, 'a')
                odds.append(a_tag.text.strip())
            except:
                odds.append('Unknown')

        df = pd.DataFrame(odds, columns=['Win Odds'])
        return df

    finally:
        driver.quit()

def scrape_current_race(race_url, odds_url):
    http_headers = {"User-Agent": "Mozilla/5.0 (compatible; HKJCScraper/1.0)"}
    response = requests.get(race_url, headers=http_headers)

    if response.status_code != 200:
        print('races not found')
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')

    venue, track, course, distance, condition, race_class = get_race_info(soup)
    df_horse_in_race = get_horse_info(soup)
    participating_horse_links = get_race_horse(soup)
    df_basic_info = scrape_horses(participating_horse_links)

    df = pd.concat([df_horse_in_race, df_basic_info], axis=1)
    df['rc'] = venue
    df['track'] = track
    df['course'] = course
    df['Dist.'] = distance
    df['track_condition'] = condition
    df['RaceClass'] = race_class

    df[['origin', 'age']] = df['Origin / Age'].apply(clean_origin_age).apply(pd.Series)
    df = df.drop(columns=['Origin / Age'])

    df[['colour', 'sex']] = df['Colour / Sex'].apply(clean_colour_sex).apply(pd.Series)
    df = df.drop(columns=['Colour / Sex'])

    odds_df = obtain_odds(odds_url)
    final_df = pd.concat([df, odds_df], axis=1)

    final_df.replace(['', 0, '0'], np.nan, inplace=True)
    final_df = final_df.dropna(how='all')

        # Define feature columns order same as training
    feature_cols = [
        'Dist.', 'track_condition', 'RaceClass', 'gate_position', 'Trainer', 'Jockey', 'Import type',
        'Sire', 'Dam', "Dam sire", 'rc', 'track', 'course', 'origin', 'age', 'colour', 'sex',
        'Rtg.', 'Win Odds', 'Act.Wt.', 'Declar.Horse Wt.', 'Horse_name'
    ]

    # Reorder columns in final_df to match training order, safely handle missing columns
    final_df = final_df.reindex(columns=feature_cols)

    return final_df

def scrape_current_race_no_odds(race_url):
    http_headers = {"User-Agent": "Mozilla/5.0 (compatible; HKJCScraper/1.0)"}
    response = requests.get(race_url, headers=http_headers)

    if response.status_code != 200:
        print('races not found')
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')

    venue, track, course, distance, condition, race_class = get_race_info(soup)
    df_horse_in_race = get_horse_info(soup)
    participating_horse_links = get_race_horse(soup)
    df_basic_info = scrape_horses(participating_horse_links)

    df = pd.concat([df_horse_in_race, df_basic_info], axis=1)
    df['rc'] = venue
    df['track'] = track
    df['course'] = course
    df['Dist.'] = distance
    df['track_condition'] = condition
    df['RaceClass'] = race_class

    df[['origin', 'age']] = df['Origin / Age'].apply(clean_origin_age).apply(pd.Series)
    df = df.drop(columns=['Origin / Age'])

    df[['colour', 'sex']] = df['Colour / Sex'].apply(clean_colour_sex).apply(pd.Series)
    df = df.drop(columns=['Colour / Sex'])

    # Define feature columns order same as training
    feature_cols = [
        'Dist.', 'track_condition', 'RaceClass', 'gate_position', 'Trainer', 'Jockey', 'Import type',
        'Sire', 'Dam', "Dam sire", 'rc', 'track', 'course', 'origin', 'age', 'colour', 'sex',
        'Rtg.', 'Act.Wt.', 'Declar.Horse Wt.', 'Horse_name', 'Horse_id'
    ]

    # Reorder columns in final_df to match training order, safely handle missing columns
    final_df = df.reindex(columns=feature_cols)

    return final_df

if __name__ == "__main__":
    # Example URLs
    race_url = 'https://racing.hkjc.com/racing/information/English/Racing/RaceCard.aspx?RaceDate=2025/09/07&Racecourse=ST&RaceNo=2'
    odds_url = 'https://bet.hkjc.com/en/racing/wp/2025-09-07/ST/2'

    df = scrape_current_race(race_url, odds_url)
    print(df)
