# app/scraper/scrape_website.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re, time, os

# ─── Brave + Driver Config ─────────────────────────────────────────────
BRAVE_PATH = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
CHROMEDRIVER_PATH = os.path.join(os.getcwd(), "chromedriver-mac-arm64", "chromedriver")


options = Options()
options.binary_location = BRAVE_PATH
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=options)

# ─── Regex Extractors ──────────────────────────────────────────────────
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

def extract_contacts(lines):
    emails, phones, names = [], [], []

    for line in lines:
        email_match = re.search(EMAIL_REGEX, line)
        phone_match = re.search(PHONE_REGEX, line)
        name = line.strip()

        if email_match:
            emails.append(email_match.group())

        if phone_match:
            phones.append(phone_match.group())

        # Filter potential names (simple rule-based)
        if len(name.split()) >= 2 and name[0].isupper():
            names.append(name)

    return names, phones, emails

# ─── Scraper Function ──────────────────────────────────────────────────
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_website_info(url: str):
    print(f"🌐 Scraping website: {url}")
    driver.get(url)
    time.sleep(5)

    contacts = {}

    def extract_page_contacts():
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lines = [line.strip() for line in page_text.split("\n") if line.strip()]
        print("🔎 Line sample:", lines[:10])

        for i, line in enumerate(lines):
            email_match = re.search(EMAIL_REGEX, line)
            phone_match = re.search(PHONE_REGEX, line)

            if email_match or phone_match:
                name = ""

                for offset in range(1, 4):
                    if i - offset >= 0:
                        candidate = lines[i - offset]
                        if (
                            len(candidate.split()) >= 2
                            and candidate[0].isupper()
                            and not re.search(EMAIL_REGEX, candidate)
                            and not re.search(PHONE_REGEX, candidate)
                            and not any(char.isdigit() for char in candidate)
                        ):
                            name = candidate
                            break

                if not name:
                    continue

                if name not in contacts:
                    contacts[name] = {"Name": name, "Phone": "", "Email": ""}

                if phone_match:
                    contacts[name]["Phone"] = phone_match.group()
                if email_match:
                    contacts[name]["Email"] = email_match.group()

    try:
        # Grab all dropdown options first (by value)
        select_xpath = "//select"
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, select_xpath)))
        select_element = Select(driver.find_element(By.XPATH, select_xpath))
        option_values = [opt.get_attribute("value") for opt in select_element.options]
        print(f"🔽 Found {len(option_values)} page ranges")

        for val in option_values:
            # Refetch fresh select each time
            select_element = Select(driver.find_element(By.XPATH, select_xpath))
            select_element.select_by_value(val)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//body[contains(., '@') or contains(., '403')]"))
            )

            print(f"➡️ Processing range: {val}")
            extract_page_contacts()
            time.sleep(1)

        final_results = list(contacts.values())
        print(f"✅ Final merged contacts: {final_results[:5]}...")
        return final_results if final_results else [{"Name": "", "Phone": "", "Email": ""}]

    except Exception as e:
        return [{"Name": "", "Phone": "", "Email": f"Error: {str(e)}"}]
