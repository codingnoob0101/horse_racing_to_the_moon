# horse_racing_to_the_moon

Data collection:
- response.text from requests.get() return no desired info with 'tr' tag, the website is likely to be loaded with js instead html
- requests and bs4 may not be suitable to extract the informations. Can try selenium to scrape dynamically after rendering JS content.
- 'race_scraper.ipynb' scrape the data and store them into the 'data' file


- rating of horses can be scraped from' https://www.hkjc.com/home/chinese/index.aspx'

