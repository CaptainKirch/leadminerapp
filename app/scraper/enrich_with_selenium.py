import pandas as pd
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# === Setup Brave + Selenium ===
options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service("./chromedriver"), options=options)

def extract_email_with_selenium(url):
    try:
        driver.get(url)
        time.sleep(5)  # wait for JS to load
        html = driver.page_source
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", html)
        return emails[0] if emails else "Not found"
    except:
        return "Failed"

def enrich_failed_only():
    df = pd.read_csv("output/results_with_emails.csv")

    # Only run Selenium on rows with "Not found" or "Failed"
    for idx, row in df.iterrows():
        if row["Email"] in ["Not found", "Failed"] and pd.notna(row["Link"]):
            print(f"🔍 Scraping {row['Name']}...")
            email = extract_email_with_selenium(row["Link"])
            print(f" → Found: {email}")
            df.at[idx, "Email"] = email

    df.to_csv("output/results_with_emails_selenium.csv", index=False)
    print("✅ Enriched CSV saved to output/results_with_emails_selenium.csv")

    driver.quit()

if __name__ == "__main__":
    enrich_failed_only()
