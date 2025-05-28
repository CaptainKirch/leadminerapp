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

keywords = [
    "Fairstone Financial Penticton",
    "Chamberlain Property Group Penticton",
    "Remax Property Group Penticton",
    "NeuHouzz Real Estate Group Penticton",
    "Front Street Reality Penticton",
    "Morrison Bifford Real Estate Group Penticton",
    "Century 21 Amos Realty Penticton",
    "MAAP Group Real Estate Penticton",
    "Engel and Volkers Okanagan Penticton",
    "The Tracy Robinson Mortgage Team Penticton",
    "Carolini Mortgages Penticton",
    "DLC Clear Mortgage Penticton",
    "Mortgage Alliance West Penticton",
    "Barapp Mortgage Group Penticton",
    "Commercial Mortgages Penticton",
    "Skytouch Flooring Penticton",
    "WildStone Construction Penticton",
    "Scott Mayhew Contracting Penticton",
    "GreyBack Construction Penticton",
    "Chute Creek Construction Penticton",
    "Showtime Home Builders Penticton",
    "Total Restoration Services Penticton",
    "Penticton Drywall Penticton",
    "Penticton Collision Centre Penticton",
    "Spare Room Self Storage Penticton",
    "E Storage Penticton Penticton",
    "Big Box Outlet Store Penticton",
    "Affordable Storage Centre Penticton",
    "Habitate For Humanity Penticton Penticton",
    "Wild Mountain Clinical Counselling Penticton",
    "OK Clinic Therapy Councilling Penticton",
    "South Okanagan Councilling Penticton",
    "Soul Centered Councilling and Holistics Penticton",
    "Soulists Counselling Centre Penticton",
    "Tideline Wellness Penticton",
    "Moksha Psychotherapy RCC Counseling Services Penticton",
    "Valley Reflections Councilling Penticton",
    "Rhonda Marriott M.Ed (psyc) Penticton",
    "Incentive Councilling Penticton",
    "Everden Rust Funeral Services Penticton",
    "Providence Funeral Homes Penticton",
    "Kettle Valley Memorial Penticton",
    "Arbor Funeral Chapters Penticton",
    "Bethel Church Penticton Penticton",
    "Penticton Alliance Church Penticton",
    "New Beginnings Church Penticton",
    "Penticton Vineyard Community Penticton",
    "Penticton United Church Penticton",
    "Saint Saviors Penticton Penticton",
    "St John Vianny Penticton Penticton",
    "St Annes Parish Penticton Penticton",
    "Oasis United Church Penticton",
    "Penticton First Baptist Church Penticton",
    "Penticton Seventh Day Adventist Church Penticton",
    "Concordia Lutheran Church Penticton",
    "Penticton Church of Nazarene Penticton",
    "Lutheran Church- Our Redeemer Penticton",
    "Society of St Vincent of Paul Penticton",
    "Penticton Foundry Ltd Penticton",
    "Waycon Manufactoring Penticton",
    "Moduline Industries Penticton",
    "Kieson Fabrication & Machine Ltd Penticton",
    "Sagnsters Head Office Penticton",
    "Radec Group Penticton",
    "Sota Instruments Ltd Penticton",
    "Nor-Mar Industrials Penticton",
    "Biron Construction Penticton",
    "BC Fasteners and Toold Ltd Penticton",
    "Kimco Controls Penticton Penticton",
    "IBC International Bar Coding Penticton",
    "Leavitt Machinary Penticton",
    "Rasha Tattoo Penticton",
    "Black Petal Tattoo Penticton",
    "Legacy Tattoo Culture Penticton",
    "Familia Tattoos Penticton",
    "Urge 3 Tattoos Penticton",
    "Custombilt Tattoos Penticton",
    "Beauty and the Blade Penticton",
    "Blitz Nail Salon Penticton",
    "Chairmanie Nails and Spa Penticton",
    "Henry Nail and Spa Penticton",
    "Dream Nails Penticton",
    "Peaches and Creme Studio Penticton",
    "Painted Lady Beauty Penticton",
    "Nails Time and Spa Penticton",
    "Gold Tip Nail Salon Penticton",
    "Freebird Hair and Co Penticton",
    "Stuart Bish Photography and Design Penticton",
    "Lisa Haywood Photography Penticton Penticton",
    "TumbleWeed Photography Framing Penticton",
    "Donut House Studios Penticton",
    "The Lloyd Gallery Penticton",
    "Penticton Computer Tech-Ease Penticton",
    "Pen Hi-Tech Cell Repair Penticton",
    "Alkloid Computer Networks Penticton",
    "Nothern Computer IT Services Penticton",
    "Repair Express Penticton Penticton",
    "Unity Cannabis Penticton",
    "The Pot Doctor Penticton",
    "Green House Cannabis Boutique Penticton",
    "Cannabis Cottage Penticton",
    "Elevated Cannabis Penticton",
    "Greenery Cannabis Boutique Penticton",
    "BC Cannabis Store Penticton",
    "Skaha Kannabis Penticton",
    "Classic Leisure Lifestyle Penticton"
]

options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless=new")

service = Service("./chromedriver")
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
    try:
        name = driver.find_element(By.XPATH, '//h1').text.strip()
    except:
        name = "N/A"

    # PHONE: Try XPath, fallback XPath, then regex
# PHONE: Try modern selectors and regex fallback
    phone = "N/A"
    try:
    # Try common phone button or span
        phone_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Phone") or contains(@aria-label, "Call")]')
        raw_phone = phone_elem.get_attribute("aria-label")
        phone = raw_phone.split(":")[-1].strip() if raw_phone else "N/A"
    except:
        try:
        # Try any span or div with visible phone number format
            phone_elem_alt = driver.find_element(By.XPATH, '//span[contains(text(), "(") and contains(text(), ")")]')
            phone = phone_elem_alt.text.strip()
        except:
            try:
                page_text = driver.page_source
                match = re.search(r"\(?\d{3}\)?[\s\.\-]?\d{3}[\s\.\-]?\d{4}", page_text)
                phone = match.group() if match else "N/A"
            except:
                phone = "N/A"


    if phone == "N/A":
        print("\n⚠️ DEBUG: Could not find phone, dumping HTML...")
        print(driver.page_source[:3000])

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

def main():
    results = []

    for keyword in keywords:
        search_url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
        print(f"\n🔍 Opening: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        scroll_page()

        business_links = set()
        cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')
        for card in cards:
            link = card.get_attribute("href")
            if link and link.startswith("https://www.google.com/maps/place/"):
                business_links.add(link)

        print(f"🔗 Found {len(business_links)} listings to click for '{keyword}'")

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
                print(f"✅ {name} | {phone} | {website} | {address} | {rating} | {category}")
                time.sleep(2)
            except Exception as e:
                print(f"❌ Failed to scrape listing: {link}", e)

    os.makedirs("output", exist_ok=True)
    with open("output/results_clickin_v3.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Keyword", "Name", "Phone", "Website", "Address", "Rating", "Category", "GoogleMapsURL"])
        writer.writeheader()
        writer.writerows(results)

    driver.quit()
    print("✅ Scraping complete. Results saved to output/results_clickin_v3.csv")

if __name__ == "__main__":
    main()