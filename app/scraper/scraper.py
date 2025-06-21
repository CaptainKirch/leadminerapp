from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# ─── Setup Chrome for Brave in headless mode ───────────────────────────────
options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless=new")  # Headless for FastAPI scraping

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless=new")

import os
CHROMEDRIVER_PATH = os.path.abspath("chromedriver-mac-arm64/chromedriver")

driver = webdriver.Chrome(
    service=Service(CHROMEDRIVER_PATH),
    options=options
)


# ─── Helper Functions ──────────────────────────────────────────────────────
def scroll_page():
    try:
        scrollable = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)

        for _ in range(20):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
            time.sleep(2)
            new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)
            if new_height == last_height:
                break
            last_height = new_height
    except Exception as e:
        print("❌ Scroll error:", e)

def extract_phone(text):
    match = re.search(r"\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}", text)
    return match.group() if match else "N/A"

def scrape_cards(keyword):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
    )
    cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    print(f"✅ Found {len(cards)} business cards for '{keyword}'")

    results = []

    for card in cards:
        try:
            name_elem = card.find_element(By.CLASS_NAME, "qBF1Pd")
            name = name_elem.text.strip()
        except:
            name = "N/A"

        try:
            link_elem = card.find_element(By.CSS_SELECTOR, "a.hfpxzc")
            link = link_elem.get_attribute("href")
        except:
            link = "N/A"

        try:
            phone = extract_phone(card.text)
        except:
            phone = "N/A"

        try:
            website = next(
                (
                    a.get_attribute("href")
                    for a in card.find_elements(By.TAG_NAME, "a")
                    if a.get_attribute("href") and "http" in a.get_attribute("href") and "google.com" not in a.get_attribute("href")
                ),
                "N/A"
            )
        except:
            website = "N/A"

        if name != "N/A" or website != "N/A":
            results.append({
                "Keyword": keyword,
                "Name": name,
                "Link": link,
                "Phone": phone,
                "Website": website
            })

    return results

# ─── Main Entry for FastAPI ────────────────────────────────────────────────
def scrape_business_info(input_str):
    print(f"🔍 Scraping Google Maps for: {input_str}")
    search_url = f"https://www.google.com/maps/search/{input_str.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(5)
    scroll_page()
    data = scrape_cards(input_str)
    return data
