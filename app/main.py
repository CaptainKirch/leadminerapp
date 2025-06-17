from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.scraper.scraper import scrape_business_info

app = FastAPI()

class LeadInput(BaseModel):
    input: str  # business name, domain, or Google search keyword

class LeadRecord(BaseModel):
    Keyword: str
    Name: str
    Link: str
    Phone: str
    Website: str

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
