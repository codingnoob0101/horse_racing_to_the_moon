from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def fetch_products(url, headless=True, delay=3):
    """
    Fetch product names and prices from the given Oxylabs sandbox URL.
    Returns a pandas DataFrame with columns ['Name', 'Price'].
    """
    # Configure Chrome options
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        # Allow JavaScript to render
        time.sleep(delay)
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        names = []
        prices = []
        for card in soup.find_all(class_="product-card"):
            h4 = card.find("h4")
            pw = card.find("div", class_="price-wrapper")
            names.append(h4.text.strip() if h4 else "")
            prices.append(pw.text.strip() if pw else "")

        return pd.DataFrame({"Name": names, "Price": prices})

    finally:
        driver.quit()