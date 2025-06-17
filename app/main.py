from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from app.scraper.scraper import scrape_business_info
from app.scraper.scrape_website import scrape_website_info

# ─── App Init ────────────────────────────────────────────────────────
app = FastAPI()

# ─── CORS Middleware ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Models ─────────────────────────────────────────────────
class LeadInput(BaseModel):
    input: str  # business name, domain, or Google search keyword

class LeadRecord(BaseModel):
    Keyword: str
    Name: str
    Link: str
    Phone: str
    Website: str

# ─── Google Maps Scraper Route ───────────────────────────────────────
@app.post("/scrape-lead/", response_model=List[LeadRecord])
def scrape_lead(payload: LeadInput):
    try:
        print(f"📥 Received scrape request for: {payload.input}")
        results = scrape_business_info(payload.input)
        if not results:
            raise HTTPException(status_code=404, detail="No results found")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Website Scraper Route ───────────────────────────────────────────
@app.post("/scrape-website/")
def scrape_website(payload: LeadInput):
    try:
        result = scrape_website_info(payload.input)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))