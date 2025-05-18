from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import re

# Keywords to loop through
keywords = [
    "gyms near Cook County Illinois",
    "medical offices near Cook County Illinois",
    "dentists near Cook County Illinois",
    "churches near Cook County Illinois",
    "nail salons near Cook County Illinois",
    "hair salons near Cook County Illinois",
    "manufacturing facilities near Cook County Illinois",
    "gyms near Will County Illinois",
    "medical offices near Will County Illinois",
    "dentists near Will County Illinois",
    "churches near Will County Illinois",
    "nail salons near Will County Illinois",
    "hair salons near Will County Illinois",
    "manufacturing facilities near Will County Illinois",
    "gyms near DuPage County Illinois",
    "medical offices near DuPage County Illinois",
    "dentists near DuPage County Illinois",
    "churches near DuPage County Illinois",
    "nail salons near DuPage County Illinois",
    "hair salons near DuPage County Illinois",
    "manufacturing facilities near DuPage County Illinois",
    "gyms near Chicago Illinois",
    "medical offices near Chicago Illinois",
    "dentists near Chicago Illinois",
    "churches near Chicago Illinois",
    "nail salons near Chicago Illinois",
    "hair salons near Chicago Illinois",
    "manufacturing facilities near Chicago Illinois"
]

# Chrome driver config
options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless=new")  # Optional headless mode

driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)

def scroll_page():
    try:
        scrollable = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
        )
        last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable)

        for _ in range(20):  # Scroll more times
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
            name_elem = card.find_element(By.CLASS_NAME, "qBF1Pd")  # new selector
            name = name_elem.text.strip()
        except:
            try:
                name = card.text.split("\n")[0].strip()
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

        # Only add if at least name or website is valid
        if name != "N/A" or website != "N/A":
            results.append({
                "Keyword": keyword,
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
    all_data = []

    for keyword in keywords:
        search_url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
        print(f"\n🔍 Opening: {search_url}")
        driver.get(search_url)

        print("⏳ Waiting 5 seconds for browser load...")
        time.sleep(5)


        print("🔎 Scraping cards...")
        data = scrape_cards(keyword)
        all_data.extend(data)

    save_to_csv(all_data)
    driver.quit()

if __name__ == "__main__":
    main()


