from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import csv
import os

SEARCH_URL = "https://www.google.com/maps/search/cleaning+services+in+kelowna"

options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
# options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)

def scroll_page():
    scrollable_div_xpath = '//div[@role="feed"]'
    scrollable = driver.find_element(By.XPATH, scrollable_div_xpath)
    for _ in range(10):  # Scroll 10 times
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
        time.sleep(2)

def scrape_cards():
    cards = driver.find_elements(By.XPATH, '//div[@role="article"]')
    results = []

    for card in cards:
        try:
            name = card.find_element(By.CLASS_NAME, "qBF1Pd").text
        except:
            name = "N/A"

        try:
            rating = card.find_element(By.CLASS_NAME, "MW4etd").text
        except:
            rating = "N/A"

        try:
            address = card.find_element(By.CLASS_NAME, "W4Efsd").text
        except:
            address = "N/A"

        try:
            links = card.find_elements(By.TAG_NAME, "a")
            website = next((a.get_attribute("href") for a in links if "http" in a.get_attribute("href")), "N/A")
        except:
            website = "N/A"

        try:
            phone = next((line for line in card.text.split("\n") if "(" in line and "-" in line), "N/A")
        except:
            phone = "N/A"

        results.append({
            "Name": name,
            "Rating": rating,
            "Address": address,
            "Phone": phone,
            "Website": website
        })
        print(f"Found {len(cards)} card elements on page.")
    return results

def save_to_csv(data):
    if not data:
        print("❌ No data found. CSV not saved.")
        return

    os.makedirs("output", exist_ok=True)
    with open("output/results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def main():
    print("Launching browser...")
    driver.get(SEARCH_URL)
    time.sleep(3)
    print("Scrolling to load all results...")
    scroll_page()
    print("Scraping data...")
    data = scrape_cards()
    print(f"Found {len(data)} listings. Saving to CSV...")
    save_to_csv(data)
    print("✅ Done. Check output/results.csv")
    driver.quit()
    print("Waiting for cards to load...")
    time.sleep(10)


if __name__ == "__main__":
    main()
