from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from app.scraper.gmaps_scraper import run_gmaps_scraper
from app.scraper.scrape_website import scrape_website_info
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LeadInput(BaseModel):
    input: str

class LeadRecord(BaseModel):
    Keyword: str
    Name: str
    Link: str
    Phone: str
    Website: str
    Email: str  # ✅ Add this

@app.post("/scrape-lead/", response_model=List[LeadRecord])
def scrape_lead(payload: LeadInput):
    try:
        print(f"📥 Received scrape request for: {payload.input}")
        raw_results = run_gmaps_scraper([payload.input])

        results = []
        for r in raw_results:
            results.append(LeadRecord(
                Keyword=r.get("Keyword", ""),
                Name=r.get("Name", ""),
                Link=r.get("GoogleMapsURL", ""),
                Phone=r.get("Phone", ""),
                Website=r.get("Website", ""),
                Email=r.get("Email", "")  # ✅ Populate the email
            ))
        
        if not results:
            raise HTTPException(status_code=404, detail="No results found")

        return results
    except Exception as e:
        print("❌ Scraper Error:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape-website/")
def scrape_website(payload: LeadInput):
    try:
        result = scrape_website_info(payload.input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
