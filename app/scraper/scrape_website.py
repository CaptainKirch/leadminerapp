import os
import re
import time
import pandas as pd
from playwright.sync_api import sync_playwright
from app.utils.s3 import upload_csv_to_s3

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

def scrape_website_info(url: str):
    print(f"\U0001F310 Scraping website: {url}")
    contacts = []
    seen = set()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            time.sleep(3)

            text = page.content()
            lines = text.splitlines()

            for i, line in enumerate(lines):
                email_match = re.search(EMAIL_REGEX, line)
                phone_match = re.search(PHONE_REGEX, line)

                if email_match or phone_match:
                    name = ""
                    for offset in range(1, 4):
                        if i - offset >= 0:
                            candidate = lines[i - offset].strip()
                            if (
                                len(candidate.split()) >= 2
                                and candidate[0].isupper()
                                and not re.search(EMAIL_REGEX, candidate)
                                and not re.search(PHONE_REGEX, candidate)
                                and not any(char.isdigit() for char in candidate)
                            ):
                                name = candidate
                                break

                    email = email_match.group() if email_match else ""
                    phone = phone_match.group() if phone_match else ""
                    key = (name, phone, email)

                    if key not in seen:
                        seen.add(key)
                        contacts.append({"Name": name, "Phone": phone, "Email": email})

            browser.close()

        print(f"✅ Extracted {len(contacts)} contacts")

        if not contacts:
            return [{"Name": "", "Phone": "", "Email": ""}]

        os.makedirs("output", exist_ok=True)
        timestamp = int(time.time())
        local_path = f"output/website_scrape_{timestamp}.csv"
        pd.DataFrame(contacts).to_csv(local_path, index=False)

        s3_key = f"website_exports/{timestamp}_website.csv"
        upload_csv_to_s3(local_path, s3_key)

        return contacts

    except Exception as e:
        print(f"❌ Scraper Exception: {e}")
        return [{"Name": "", "Phone": "", "Email": f"Error: {str(e)}"}]
