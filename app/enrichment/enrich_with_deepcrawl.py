import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 8
EMAIL_REGEX = re.compile(
    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|[a-zA-Z0-9_.+-]+\s*\[at\]\s*[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
)

def get_rendered_html(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=15000)
            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"❌ Playwright failed at {url}: {e}")
        return None

def extract_emails_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    raw_emails = EMAIL_REGEX.findall(text)
    cleaned = list(set(e.replace("[at]", "@").replace(" ", "") for e in raw_emails))
    return cleaned

def extract_emails_from_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200 or 'text/html' not in resp.headers.get('Content-Type', ''):
            return []
        return extract_emails_from_html(resp.text)
    except Exception as e:
        print(f"❌ Email extraction failed at {url}: {e}")
        return []

def get_internal_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if href.startswith("mailto:") or href.startswith("tel:"):
            continue
        absolute = urljoin(base_url, href)
        if urlparse(absolute).netloc == urlparse(base_url).netloc:
            links.add(absolute)
    return list(links)

def prioritize_links(links, html):
    priority = ["contact", "about", "team", "staff", "leadership", "book", "appointment", "connect", "schedule", "info", "support"]
    soup = BeautifulSoup(html, "html.parser")

    def score(link):
        href_score = min([link.lower().find(k) if k in link.lower() else 999 for k in priority])
        anchor_text = next((a.text.lower() for a in soup.find_all("a", href=True) if a['href'] == link), "")
        text_score = min([anchor_text.find(k) if k in anchor_text else 999 for k in priority])
        return min(href_score, text_score)

    return sorted(set(links), key=score)[:MAX_PAGES]

def enrich_email(domain_url):
    try:
        print(f"🔍 Scanning {domain_url}")
        homepage = requests.get(domain_url, headers=HEADERS, timeout=10)

        html = homepage.text if homepage.status_code == 200 else None
        if not html or '<script' in html.lower():
            print("⚠️ Falling back to Playwright rendering")
            html = get_rendered_html(domain_url)
            if not html:
                return "Failed"

        emails = extract_emails_from_html(html)
        if emails:
            print(f"📬 Found {len(emails)} on homepage → {emails}")
            return ", ".join(emails)

        internal_links = get_internal_links(domain_url, html)
        internal_links = prioritize_links(internal_links, html)

        for link in internal_links:
            time.sleep(1)
            link_html = get_rendered_html(link) or requests.get(link, headers=HEADERS, timeout=10).text
            emails = extract_emails_from_html(link_html)
            if emails:
                print(f"📬 Found {len(emails)} on {link} → {emails}")
                return ", ".join(emails)

        fallback = f"info@{urlparse(domain_url).netloc}"
        print(f"⚠️ No email found. Fallback guessed: {fallback}")
        return f"Guessed: {fallback}"

    except Exception as e:
        print(f"❌ Error with {domain_url}: {e}")
        return "Failed"

def clean_url(url):
    try:
        base = url.split("?")[0].strip()
        parsed = urlparse(base)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}"
        return None
    except:
        return None

def run_email_enrichment(csv_path="output/results_clickin_v3.csv"):

    df = pd.read_csv(csv_path)

    if "Email" not in df.columns:
        df["Email"] = "Not found"

    seen_domains = {}

    for idx, row in df.iterrows():
        raw_url = row.get("Website", "")
        if pd.isna(raw_url) or "google.com" in raw_url or raw_url.strip() == "N/A":
            continue

        clean_domain = clean_url(raw_url)
        if not clean_domain:
            continue

        if clean_domain in seen_domains:
            df.at[idx, "Email"] = seen_domains[clean_domain]
            print(f"🔁 Skipping repeat domain {clean_domain}, reused → {seen_domains[clean_domain]}")
            continue

        if row["Email"] in ["Not found", "Failed"]:
            email = enrich_email(clean_domain)
            print(f"{row['Name']} → {email}")
            df.at[idx, "Email"] = email
            seen_domains[clean_domain] = email
            time.sleep(1.5)

        if idx % 25 == 0:
            df.to_csv("output/results_with_deepcrawl_v3.csv", index=False)

    df.to_csv("output/results_with_deepcrawl_v3.csv", index=False)
    print("✅ Saved to output/results_with_deepcrawl_v3.csv")

if __name__ == "__main__":
    run_email_enrichment()

