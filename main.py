import os
import re
import asyncio
import pandas as pd
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from agents.researcher import ResearcherAgent
from agents.contact_finder import ContactFinderAgent
from agents.outreach_writer import OutreachWriterAgent

load_dotenv()

app = FastAPI(title="Brokai Lead Intelligence")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

async def retry_with_backoff(func, max_retries=3):
    """Retry function with exponential backoff for rate limits"""
    for attempt in range(max_retries):
        try:
            return await asyncio.to_thread(func)
        except Exception as e:
            if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                await asyncio.sleep(wait_time)
            else:
                raise
    return None

def parse_email(raw: str) -> str:
    if not raw:
        return "Not found"
    clean = raw.replace("[at]", "@").replace("[dot]", ".").replace(" ", "")
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", clean, re.IGNORECASE)
    return match.group(0).lower() if match else "Not found"


def load_companies():
    try:
        df = pd.read_excel("data/companies.xlsx", header=None)
        companies = []
        for _, row in df.iterrows():
            name = str(row[2]).strip() if row[2] else None
            if not name or name == "None" or name.lower() == "nan":
                continue
            companies.append({
                "name": name,
                "location": str(row[1]).strip() if row[1] else "Rajasthan, India",
                "email_from_excel": parse_email(str(row[3]) if row[3] else "")
            })
        
        return companies
    except FileNotFoundError:
        # Excel not available in deployed env — company names only, no sensitive data
        return [
            {"name": "Yash Electricals & Civil Services", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Dayma Enterprises", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Indepletable Energy", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Solar Technocrats", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Udaipur Green Energy Solution", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Ratan Green Energy Service Pvt. Ltd", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Deepak Enterprises", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Green Power Corporation", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Skype Solar Pvt Ltd", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Kanta Solar", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Vinayakam Solution", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Shree Solar Venture Pvt. Ltd.", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Sunrise Solar and Electrical Solution", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Soratan Enterprises", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Priya Battery & Invertors", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Traurja Solutions LLP", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Vidit Solar Energy", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Neoterix Solution Pvt. Ltd.", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Go Green Solar", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Raghubir Prasad and Brothers", "location": "Rajasthan, India", "email_from_excel": "Not found"},
            {"name": "Lanch Associates", "location": "Rajasthan, India", "email_from_excel": "Not found"},
        ]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root():
    with open(os.path.join(BASE_DIR, "static", "index.html"), "r") as f:
        return f.read()

async def process_one(company: dict, researcher, contact_finder, outreach_writer) -> dict:
    name = company["name"]
    location = company["location"]
    email_from_excel = company["email_from_excel"]

    try:
        profile = await retry_with_backoff(lambda: researcher.run(name, location))
    except Exception as e:
        profile = {
            "summary": f"Research failed: {e}",
            "digital_presence": "Could not determine",
            "uses_crm_or_booking": "Unknown"
        }

    try:
        contact = await retry_with_backoff(
            lambda: contact_finder.run(name, location, profile, email_from_excel)
        )
    except Exception as e:
        contact = {
            "phone": "Not found",
            "email": email_from_excel,
            "whatsapp": "Not found",
            "source_url": f"Contact search failed: {e}"
        }

    try:
        message = await retry_with_backoff(
            lambda: outreach_writer.run(profile, contact, name)
        )
    except Exception as e:
        message = f"Message generation failed: {e}"

    has_contact = (
        contact.get("phone", "Not found") != "Not found" or
        contact.get("email", "Not found") != "Not found"
    )

    return {
        "company_name": name,
        "location": location,
        "business_summary": profile.get("summary", "Not found"),
        "digital_presence": profile.get("digital_presence", "Not found"),
        "uses_crm_or_booking": profile.get("uses_crm_or_booking", "Unknown"),
        "contact_phone": contact.get("phone", "Not found"),
        "contact_email": contact.get("email", "Not found"),
        "contact_whatsapp": contact.get("whatsapp", "Not found"),
        "contact_source_url": contact.get("source_url", "Not found"),
        "outreach_message": message,
        "status": "success" if has_contact else "partial"
    }

@app.post("/process-excel")
async def process_excel():
    try:
        companies = load_companies()
    except Exception as e:
        return {"error": f"Could not read Excel: {e}"}

    researcher = ResearcherAgent()
    contact_finder = ContactFinderAgent()
    outreach_writer = OutreachWriterAgent()

    results = []
    # Process sequentially with delays to avoid rate limits
    for i, company in enumerate(companies):
        result = await process_one(company, researcher, contact_finder, outreach_writer)
        results.append(result)
        
        # Add delay between companies to avoid rate limits
        if i < len(companies) - 1:  # Don't delay after last company
            await asyncio.sleep(2)  # 2 second delay between companies
    
    return results