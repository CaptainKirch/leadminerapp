import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 5  # pages per site to scan

def extract_emails_from_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
        return list(set(emails))
    except:
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

def prioritize_links(links):
    # Prefer these pages first
    priority = ["contact", "about", "team", "staff", "privacy"]
    scored = sorted(links, key=lambda link: min([link.lower().find(p) if p in link.lower() else 999 for p in priority]))
    return scored[:MAX_PAGES]

def enrich_email(domain_url):
    try:
        print(f"🔍 Scanning {domain_url}")
        homepage = requests.get(domain_url, headers=HEADERS, timeout=10)
        if homepage.status_code != 200:
            return "Failed"

        # Step 1: Try homepage
        emails = extract_emails_from_url(domain_url)
        if emails:
            return emails[0]

        # Step 2: Get internal links
        internal_links = get_internal_links(domain_url, homepage.text)
        internal_links = prioritize_links(internal_links)

        # Step 3: Scan internal pages
        for link in internal_links:
            time.sleep(1)
            emails = extract_emails_from_url(link)
            if emails:
                return emails[0]

        return "Not found"
    except Exception as e:
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

def enrich_csv():
    df = pd.read_csv("output/results.csv")

    # Add Email column if missing
    if "Email" not in df.columns:
        df["Email"] = "Not found"

    for idx, row in df.iterrows():
        raw_url = row.get("Website", "")
        if pd.isna(raw_url) or "google.com" in raw_url or raw_url.strip() == "N/A":
            continue  # Skip bad rows

        clean_domain = clean_url(raw_url)
        if not clean_domain:
            continue

        # Only enrich rows with missing email
        if row["Email"] in ["Not found", "Failed"]:
            email = enrich_email(clean_domain)
            print(f"{row['Name']} → {email}")
            df.at[idx, "Email"] = email
            time.sleep(1.5)  # polite delay

    df.to_csv("output/results_with_deepcrawl.csv", index=False)
    print("✅ Saved to output/results_with_deepcrawl.csv")


if __name__ == "__main__":
    enrich_csv()
