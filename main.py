from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# 🧠 Replace these with your real logic
from app.scraper.scraper import scrape_business_info
from app.generator.generate_emails import generate_email_from_data

app = FastAPI()

class InputPayload(BaseModel):
    input: str  # Company name or domain

class OutputResponse(BaseModel):
    email: str
    enriched: Optional[dict] = None

@app.post("/generate-email/", response_model=OutputResponse)
def generate_email(payload: InputPayload):
    try:
        # Step 1: Scrape or enrich from input (e.g., business name or URL)
        enriched_data = scrape_business_info(payload.input)

        # Step 2: Generate email from enriched data
        email = generate_email_from_data(enriched_data)

        return {
            "email": email,
            "enriched": enriched_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
