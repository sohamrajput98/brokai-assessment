import os
import json
from tavily import TavilyClient
from agents.llm_client import call_llm_fast


class ResearcherAgent:
    """
    Agent 01 - Researcher
    Input: company name, location
    Output: {summary, digital_presence, uses_crm_or_booking}
    """

    def __init__(self):
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    def run(self, company_name: str, location: str) -> dict:
        query = f"{company_name} {location}"
        try:
            results = self.tavily.search(
                query=query,
                max_results=5,
                search_depth="basic"
            )
            raw = "\n\n".join([
                f"Source: {r.get('url','')}\nTitle: {r.get('title','')}\nContent: {r.get('content','')}"
                for r in results.get("results", [])
            ])
        except Exception as e:
            raw = f"Search failed: {e}"

        if not raw.strip():
            return {
                "summary": "No information found online.",
                "digital_presence": "No online presence found",
                "uses_crm_or_booking": "Unknown"
            }

        prompt = f"""You are a business intelligence analyst. Extract a structured profile for this company from search results.

Company: {company_name}
Location: {location}

Search Results:
{raw}

Return ONLY valid JSON with these exact keys:
{{
  "summary": "2-3 sentences: what they do, size signals, market position",
  "digital_presence": "website, social media, directory listings found — or 'No online presence found'",
  "uses_crm_or_booking": "Yes / No / Unknown — do they use any booking, CRM, or communication system?"
}}

Use honest fallbacks if info is missing. Do not invent facts."""

        try:
            content = call_llm_fast(prompt, max_tokens=500, temperature=0.1)
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content.strip())
        except Exception as e:
            return {
                "summary": "Could not retrieve profile at this time. Outreach generated from industry context.",
                "digital_presence": "Could not determine",
                "uses_crm_or_booking": "Unknown"
     }