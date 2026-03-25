import os
import json
from tavily import TavilyClient
from groq import Groq


class ContactFinderAgent:
    """
    Agent 02 - Contact Finder
    Input: company name, location, profile, email already known from Excel
    Output: {phone, email, whatsapp, source_url}
    """

    def __init__(self):
        self.tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def run(self, company_name: str, location: str, profile: dict, known_email: str = "Not found") -> dict:
        queries = [
            f"{company_name} {location} phone number",
            f"{company_name} IndiaMART OR Justdial contact",
        ]

        all_results = []
        for query in queries:
            try:
                r = self.tavily.search(query=query, max_results=3, search_depth="basic")
                all_results.extend(r.get("results", []))
            except Exception:
                continue

        raw = "\n\n".join([
            f"Source: {r.get('url','')}\nContent: {r.get('content','')}"
            for r in all_results
        ])

        if not raw.strip():
            return {
                "phone": "Not found",
                "email": known_email,
                "whatsapp": "Not found",
                "source_url": "No sources found"
            }

        prompt = f"""Extract contact details for this company from search results.

Company: {company_name}
Location: {location}

Search Results:
{raw}

Return ONLY valid JSON:
{{
  "phone": "phone number if found, else 'Not found'",
  "whatsapp": "WhatsApp number if explicitly mentioned, else 'Not found'",
  "source_url": "URL where contact info was found, else 'Not found'"
}}

Rules:
- Only extract info actually present in results
- Do NOT invent numbers
- If multiple phones, pick the most prominent one"""

        try:
            resp = self.groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}  # Force JSON output
            )
            content = resp.choices[0].message.content.strip()
            result = json.loads(content)
            result["email"] = known_email
            return result
        except Exception as e:
            return {
                "phone": "Not found",
                "email": known_email,
                "whatsapp": "Not found",
                "source_url": f"Extraction failed: {e}"
            }