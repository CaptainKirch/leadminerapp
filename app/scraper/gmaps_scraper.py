import os
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.enrichment.enrich_with_deepcrawl import run_email_enrichment
from app.utils.s3 import upload_csv_to_s3

def run_gmaps_scraper(keywords: list[str]) -> list[dict]:
    results = []

    options = Options()
    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    options.add_argument("--window-size=1920,1080")
    # options.add_argument("--headless=new")

    service = Service("/Users/liamkircher/Desktop/leadminerapp/chromedriver-mac-arm64/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    def scroll_page():
        try:
            for _ in range(20):
                scrollable = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
                time.sleep(2)
        except Exception as e:
            print("❌ Scroll error:", e)

    def scrape_full_listing():
        def safe_xpath(xpath):
            try:
                return driver.find_element(By.XPATH, xpath).text.strip()
            except:
                return "N/A"

        name = safe_xpath('//h1')
        phone = "N/A"
        try:
            phone_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Phone") or contains(@aria-label, "Call")]')
            raw_phone = phone_elem.get_attribute("aria-label")
            phone = raw_phone.split(":")[-1].strip() if raw_phone else "N/A"
        except:
            try:
                phone_elem_alt = driver.find_element(By.XPATH, '//span[contains(text(), "(") and contains(text(), ")")]')
                phone = phone_elem_alt.text.strip()
            except:
                try:
                    match = re.search(r"\(?\d{3}\)?[\s\.\-]?\d{3}[\s\.\-]?\d{4}", driver.page_source)
                    phone = match.group() if match else "N/A"
                except:
                    phone = "N/A"

        try:
            website_elem = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Website")]')
            website = website_elem.get_attribute("href")
        except:
            website = "N/A"

        try:
            address_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Address")]')
            address = address_elem.get_attribute("aria-label").split(":")[-1].strip()
        except:
            address = "N/A"

        try:
            rating_elem = driver.find_element(By.XPATH, '//span[contains(@aria-label, "stars")]')
            rating = rating_elem.get_attribute("aria-label")
        except:
            rating = "N/A"

        try:
            category_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Category")]')
            category = category_elem.get_attribute("aria-label").split(":")[-1].strip()
        except:
            category = "N/A"

        return name, phone, website, address, rating, category

    for keyword in keywords:
        search_url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
        print(f"\n🔍 Opening: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        scroll_page()

        business_links = set()
        try:
            cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')
            for card in cards:
                link = card.get_attribute("href")
                if link and link.startswith("https://www.google.com/maps/place/"):
                    business_links.add(link)

            if len(business_links) == 0:
                try:
                    name, phone, website, address, rating, category = scrape_full_listing()
                    results.append({
                        "Keyword": keyword,
                        "Name": name,
                        "Phone": phone,
                        "Website": website,
                        "Address": address,
                        "Rating": rating,
                        "Category": category,
                        "GoogleMapsURL": driver.current_url
                    })
                except Exception as e:
                    print(f"❌ Failed to scrape direct page for: {keyword}", e)
            else:
                for link in business_links:
                    try:
                        driver.get(link)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1")))
                        time.sleep(6)
                        name, phone, website, address, rating, category = scrape_full_listing()
                        results.append({
                            "Keyword": keyword,
                            "Name": name,
                            "Phone": phone,
                            "Website": website,
                            "Address": address,
                            "Rating": rating,
                            "Category": category,
                            "GoogleMapsURL": link
                        })
                        time.sleep(2)
                    except Exception as e:
                        print(f"❌ Failed to scrape listing: {link}", e)
        except Exception as e:
            print(f"❌ Error during business_links processing: {e}")

    driver.quit()

    os.makedirs("output", exist_ok=True)
    output_path = "output/results_clickin_v3.csv"
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)
    print(f"✅ Saved initial scrape to {output_path}")

    print("📬 Starting email enrichment...")
    run_email_enrichment(output_path)

    enriched = pd.read_csv("output/results_with_deepcrawl_v3.csv")
    enriched.fillna("", inplace=True)
    print(f"✅ Enriched scrape complete with {len(enriched)} entries")

    # Upload to S3
    s3_key = f"leads_exports/{int(time.time())}_leads.csv"
    upload_csv_to_s3("output/results_with_deepcrawl_v3.csv", s3_key)

    return enriched.to_dict(orient="records")
