import os
import time
import re
import pandas as pd
from playwright.sync_api import sync_playwright
from app.enrichment.enrich_with_deepcrawl import run_email_enrichment
from app.utils.s3 import upload_csv_to_s3

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\(?\d{3}\)?[\s.\-]?\d{3}[\s.\-]?\d{4}"

def run_gmaps_scraper(keywords: list[str]) -> list[dict]:
    results = []
    os.makedirs("output", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        def scroll_page():
            for _ in range(20):
                page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                time.sleep(2)

        def safe_text(selector):
            try:
                return page.locator(selector).first.text_content().strip()
            except:
                return "N/A"

        def scrape_full_listing():
            name = safe_text("h1")
            phone = "N/A"

            try:
                phone_elem = page.locator("button[aria-label*='Phone'], button[aria-label*='Call']").first
                raw = phone_elem.get_attribute("aria-label")
                phone = raw.split(":")[-1].strip() if raw else "N/A"
            except:
                try:
                    text = page.inner_text("body")
                    match = re.search(PHONE_REGEX, text)
                    phone = match.group() if match else "N/A"
                except:
                    pass

            website = page.get_attribute("a[aria-label*='Website']", "href") or "N/A"
            address = safe_text("button[aria-label*='Address']")
            rating = page.get_attribute("span[aria-label*='stars']", "aria-label") or "N/A"
            category = safe_text("button[aria-label*='Category']")

            return name, phone, website, address, rating, category

        for keyword in keywords:
            search_url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
            print(f"\n🔍 Opening: {search_url}")
            page.goto(search_url, timeout=60000)
            time.sleep(5)
            scroll_page()

            links = set()
            try:
                hrefs = page.locator("a[href*='/place/']").evaluate_all("els => els.map(e => e.href)")
                for href in hrefs:
                    if href.startswith("https://www.google.com/maps/place/"):
                        links.add(href)
            except Exception as e:
                print(f"❌ Failed getting business links: {e}")

            if not links:
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
                        "GoogleMapsURL": page.url
                    })
                except Exception as e:
                    print(f"❌ Direct scrape error: {e}")
            else:
                for link in links:
                    try:
                        page.goto(link, timeout=60000)
                        page.wait_for_selector("h1", timeout=10000)
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
                        print(f"❌ Failed on listing: {link} → {e}")

        context.close()
        browser.close()

    output_path = "output/results_clickin_v3.csv"
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"✅ Saved initial scrape to {output_path}")

    print("📬 Starting email enrichment...")
    run_email_enrichment(output_path)

    enriched = pd.read_csv("output/results_with_deepcrawl_v3.csv")
    enriched.fillna("", inplace=True)
    print(f"✅ Enriched scrape complete with {len(enriched)} entries")

    s3_key = f"leads_exports/{int(time.time())}_leads.csv"
    upload_csv_to_s3("output/results_with_deepcrawl_v3.csv", s3_key)

    return enriched.to_dict(orient="records")
