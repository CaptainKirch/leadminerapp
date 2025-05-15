# 🧠 LeadMiner

**LeadMiner** is a Google Maps scraping and email enrichment pipeline for local businesses.  
It extracts business names, phone numbers, websites, and attempts to find verified emails by crawling each business's site.

---

## 🚀 Features

- 🔍 Scrapes **Google Maps listings** via Selenium (Brave browser)
- 📞 Collects **Name, Phone, Website** from each listing
- ✉️ Crawls **business websites** to find contact emails (homepage + internal pages)
- 💾 Saves all results to CSV for use in outreach campaigns or lead gen tools
- ✅ Built for local lead scraping (dental clinics, contractors, cleaners, etc.)

---

## 📦 File Structure

| File                          | Description |
|------------------------------|-------------|
| `scraper.py`                 | Scrapes Google Maps listings (Name, Link, Phone, Website) |
| `enrich_with_deepcrawl.py`   | Crawls each business website to find emails from internal pages |
| `enrich_with_emails.py`      | (Optional) Basic homepage + /contact email extraction |
| `enrich_with_selenium.py`    | (Optional) JS-rendered email extractor via headless browser |
| `output/results.csv`         | Raw scraped business data |
| `output/results_with_deepcrawl.csv` | Final enriched leads with emails |
| `chromedriver`               | Used by Selenium to control the Brave browser |

---

## ⚙️ Requirements

- Python 3.9+
- Google Chrome or Brave
- `chromedriver` matching your browser version

### 🐍 Install Python packages:

```bash
pip install selenium requests beautifulsoup4 pandas


🧭 How to Use
1. Scrape Google Maps
Edit your target search in scraper.py:

python
Copy
Edit
SEARCH_URL = "https://www.google.com/maps/search/dental+clinics+near+chicago"
Then run:

bash
Copy
Edit
python scraper.py
This saves data to: output/results.csv

2. Enrich with Emails via Website Crawl
Run the deep crawler:

bash
Copy
Edit
python enrich_with_deepcrawl.py
This outputs: output/results_with_deepcrawl.csv

🧠 How It Works
Scraper uses Selenium to extract data directly from Google Maps listings.

Phone numbers are extracted using regex.

Website URLs are parsed from the listing card.

Email enrichment is done by crawling internal pages (/contact, /about, etc.) using requests and BeautifulSoup.

🔒 Disclaimer
This tool is for educational and personal use only.
Web scraping may violate the terms of service of some platforms.
Always ensure compliance with local laws and ethical guidelines before deploying at scale.

💡 Future Improvements
Add Snov.io or Hunter API fallback

Add multi-threading for faster crawls

Auto-launch email outreach via Instantly or Lemlist

Package as a CLI or Streamlit app for clients


---

Let me know if you want a **"Getting Started" GIF**, GitHub badge bling, or versioned CLI command structure later. This README already positions it as a legit, production-level script.
