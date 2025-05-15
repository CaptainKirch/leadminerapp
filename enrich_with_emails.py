import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time

def extract_email_from_website(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        
        # Attempt homepage
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.text))

        if emails:
            return list(emails)[0]

        # Try /contact if homepage fails
        contact_url = url.rstrip("/") + "/contact"
        response = requests.get(contact_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", soup.text))

        return list(emails)[0] if emails else "Not found"
    except Exception as e:
        return "Failed"


def enrich_csv():
    df = pd.read_csv("output/results.csv")
    df["Email"] = df["Link"].apply(extract_email_from_website)
    df.to_csv("output/results_with_emails.csv", index=False)
    print("✅ Enriched CSV saved to output/results_with_emails.csv")

if __name__ == "__main__":
    enrich_csv()
