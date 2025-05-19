import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 8
EMAIL_REGEX = re.compile(
    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|[a-zA-Z0-9_.+-]+\s*\[at\]\s*[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
)

def extract_emails_from_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        if 'text/html' not in resp.headers.get('Content-Type', ''):
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text()
        raw_emails = EMAIL_REGEX.findall(text)
        cleaned = list(set(e.replace("[at]", "@").replace(" ", "") for e in raw_emails))
        return cleaned
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
        if homepage.status_code != 200 or '<script' in homepage.text[:1000].lower():
            print(f"⚠️ Skipping JS-heavy or unreachable site: {domain_url}")
            return "Failed"

        # Step 1: Try homepage
        emails = extract_emails_from_url(domain_url)
        if emails:
            print(f"📬 Found {len(emails)} on homepage → {emails}")
            return ", ".join(emails)

        # Step 2: Get internal links
        internal_links = get_internal_links(domain_url, homepage.text)
        internal_links = prioritize_links(internal_links, homepage.text)

        # Step 3: Scan internal pages
        for link in internal_links:
            time.sleep(1)
            emails = extract_emails_from_url(link)
            if emails:
                print(f"📬 Found {len(emails)} on {link} → {emails}")
                return ", ".join(emails)

        # Step 4: Fallback guess
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

def enrich_csv(csv_path="output/results.csv"):
    df = pd.read_csv(csv_path)

    if "Email" not in df.columns:
        df["Email"] = "Not found"

    for idx, row in df.iterrows():
        raw_url = row.get("Website", "")
        if pd.isna(raw_url) or "google.com" in raw_url or raw_url.strip() == "N/A":
            continue

        clean_domain = clean_url(raw_url)
        if not clean_domain:
            continue

        if row["Email"] in ["Not found", "Failed"]:
            email = enrich_email(clean_domain)
            print(f"{row['Name']} → {email}")
            df.at[idx, "Email"] = email
            time.sleep(1.5)

        if idx % 25 == 0:
            df.to_csv("output/results_with_deepcrawl.csv", index=False)

    df.to_csv("output/results_with_deepcrawl.csv", index=False)
    print("✅ Saved to output/results_with_deepcrawl.csv")

if __name__ == "__main__":
    enrich_csv()