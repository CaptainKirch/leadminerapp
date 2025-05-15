from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import re  # ← Added for phone number extraction

SEARCH_URL = "https://www.google.com/maps/search/dental+clinics+near+chicago"

options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
# options.add_argument("--headless=new")  # Disable headless for now
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)

def scroll_page():
    try:
        scrollable = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
        )
        for _ in range(10):
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
            time.sleep(2)
    except Exception as e:
        print("❌ Scroll error:", e)

# ✅ More reliable phone number detection
def extract_phone(text):
    match = re.search(r"\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}", text)
    return match.group() if match else "N/A"

def scrape_cards():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "Nv2PK"))
    )

    cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    print(f"✅ Found {len(cards)} business cards")

    results = []

    for card in cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, "a.hfpxzc").text
        except:
            name = "N/A"

        try:
            link = card.find_element(By.CSS_SELECTOR, "a.hfpxzc").get_attribute("href")
        except:
            link = "N/A"

        try:
            phone = extract_phone(card.text)
        except:
            phone = "N/A"

        try:
            # Google Maps website button (if available)
            website = next(
                (
                    a.get_attribute("href")
                    for a in card.find_elements(By.TAG_NAME, "a")
                    if "http" in a.get_attribute("href") and "google.com" not in a.get_attribute("href")
                ),
                "N/A"
            )
        except:
            website = "N/A"

        results.append({
            "Name": name,
            "Link": link,
            "Phone": phone,
            "Website": website
        })

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

    print("✅ Data saved to output/results.csv")

def main():
    print("Launching browser...")
    driver.get(SEARCH_URL)

    input("📌 Browser loaded. Press Enter to begin scrolling...")

    print("Scrolling listings...")
    scroll_page()

    print("Scraping business data...")
    data = scrape_cards()

    print(f"Found {len(data)} listings. Saving...")
    save_to_csv(data)
    driver.quit()

if __name__ == "__main__":
    main()
