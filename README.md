# Brokai Lead Intelligence System
<br>
<p align="center">
  <img src="https://img.shields.io/badge/FASTAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
  &nbsp;
  <img src="https://img.shields.io/badge/GROQ_LLAMA_3.1-6A5ACD?style=for-the-badge&logo=ai&logoColor=white"/>
  &nbsp;
  <img src="https://img.shields.io/badge/TAVILY_SEARCH-1E90FF?style=for-the-badge&logo=search&logoColor=white"/>
  &nbsp;
  <img src="https://img.shields.io/badge/RENDER_DEPLOY-46E3B7?style=for-the-badge&logo=render&logoColor=black"/>
</p>

A multi-agent pipeline that researches solar EPC companies, 
finds contacts, and generates WhatsApp outreach messages.
<br><br>

## 🌐 Live Demo

<p align="center">
  <img src="https://img.shields.io/badge/LIVE_DEMO-333333?style=for-the-badge&logo=render&logoColor=white"/>
  &nbsp;
  <a href="https://brokai-assessment.onrender.com/">
    <img src="https://img.shields.io/badge/LAUNCH_DEMO-FF4500?style=for-the-badge&logo=render&logoColor=white"/>
  </a>
</p>

<p align="center">
  <sub>  ⚠️ Cold start: ~30–50s • Full run: ~2–3 min. Do not close the tab.</sub>
</p>

---

## Dashboard Screenshots :

![Dashboard Screenshot](assets/dashboard1.png)
<br><br>
![Dashboard Screenshot](assets/dashboard2.png)

---

## Architecture diagram :

![Architecture Diagram](assets/architecture.png)


---

## What It Does :

Three specialised agents work in sequence for each company:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **01 — Researcher** | Searches the web to build a business profile | Company name + location | Summary, digital presence, CRM usage |
| **02 — Contact Finder** | Locates phone, email, WhatsApp from directories | Business profile | Contact card with source URL |
| **03 — Outreach Writer** | Generates a personalised WhatsApp-style cold message | Profile + contact card | Ready-to-send message |
<br>

**Batch parallel processing:** 3 companies run concurrently per batch via `asyncio.gather()`, with a 3s pause between batches. Full pipeline for 21 companies completes in ~2-3 minutes instead of 7-9 minutes sequential — without hitting free tier rate limits. On a paid tier, removing the inter-batch delay gets you near-instant full runs.

---
## Key Features

- Multi-agent pipeline (Research → Contact → Outreach)
- Async batch processing with rate-limit handling
- Graceful failure and retry system
- Uses real-world data sources (Tavily search)
- Production-ready API with FastAPI
---

## Sample Output

```json
{
  "company": "ABC Solar",
  "contact": "+91XXXXXXXXXX",
  "email": "info@abcsolar.com",
  "message": "Hi, I came across your company..."
}
```
---

## Stack

- **Backend:** FastAPI (Python)
- **LLM:** Groq (Llama 3.1 8B Instant) — two accounts, split by task type
- **Web Search:** Tavily
- **Frontend:** Vanilla HTML/CSS/JS
- **Deployment:** Render (free tier)

---
## Project Structure
```
BROKAI_ASSESSMENT
├── agents/
│ ├── contact_finder.py
│ ├── llm_client.py
│ ├── outreach_writer.py
│ └── researcher.py
├── assets/
│ ├── architecture.png
│ ├── dashboard1.png
│ └── dashboard2.png
├── static/
│ └── index.html
├── .env.example
├── main.py
├── render.yaml
├── requirements.txt
└── README.md
```
---


## Run Locally :

**1. Clone the repo**
```bash
git clone https://github.com/sohamrajput98/brokai-assessment.git
cd brokai-assessment
```

**2. Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Add your API keys**
```bash
cp .env.example .env
# Edit .env and fill in your keys
```

**4. Add the companies Excel file (optional)**
```bash
mkdir data
# Copy companies.xlsx into data/ if you have it
# Without it, the pipeline runs on the hardcoded company list
```

**5. Run the server**
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` and click **Run Pipeline**.

---

## Environment Variables :

```
GROQ_API_KEY_1=gsk_...      # Groq account 1 — researcher + contact finder
GROQ_API_KEY_2=gsk_...      # Groq account 2 — outreach writer (separate daily limit)
TAVILY_API_KEY=tvly-...     # From app.tavily.com
```

See `.env.example` for the full template.

---

## Deploy on Render :

1. Push this repo to GitHub
2. Render → New Web Service → connect repo
3. Add the 3 environment variables above
4. Deploy — `render.yaml` handles the rest

The pipeline works without the Excel file on Render — company names are hardcoded as fallback so the live demo always runs.

---
## Why the Excel File Isn't in the Repo :

The companies Excel file contains real business names, emails, and contact data. Committing it publicly would expose that information.

The deployed version hardcodes company names only (no emails, no sensitive data) as a fallback in `main.py`. When the Excel file is present locally, the pipeline reads from it and passes emails directly to the contact finder — skipping LLM calls for data already in hand. When it isn't present (Render), agents research and find contacts independently. Both runs produce comparable output quality.

---

## Design Decisions & Tradeoffs :

**Plain Python classes, no LangChain.** Each agent has a single `run()` method with a clear input/output contract. No hidden abstractions, straightforward to debug and extend.

**Split Groq accounts by task type.** Researcher and contact finder are extraction tasks — low temperature, small output, high call volume. Outreach writer is a writing task — higher temperature, separate Groq account so its daily limit is never starved by the extraction agents.

**Batch parallel + exponential backoff.** Naive `asyncio.gather()` across all 21 companies hit Groq's 12K TPM limit instantly — 429 errors everywhere. Pure sequential took 7-9 minutes. The fix: batch size of 3 with a 3s inter-batch delay. Three companies run in parallel, pause, next three, repeat. Runtime drops to ~2-3 minutes with zero rate limit errors. Each agent call also retries up to 3 times with exponential backoff (1s, 2s, 4s) so transient errors don't permanently fail a company.

**Graceful failure at every step.** If Tavily search fails or returns nothing, the agent returns honest fallback values rather than crashing. If the LLM fails after retries, the row is marked `partial` and the pipeline continues. Nothing takes down the whole run.

**Low temperature for extraction, higher for writing.** Researcher and contact finder run at `temperature=0.1` for consistent structured JSON output. Outreach writer runs at `temperature=0.7` so messages sound human and vary between companies.

---

## Problems Hit & How They Were Solved :

| Problem | Fix |
|---------|-----|
| Groq model `llama3-8b-8192` deprecated | Switched to `llama-3.1-8b-instant` |
| 429 rate limit errors on parallel runs | Batch processing (size 3) + exponential backoff retry |
| LLM returning non-JSON text | Added markdown fence stripping before `json.loads()` |
| Async/sync mismatch with Tavily/Groq clients | Wrapped sync calls with `asyncio.to_thread()` |
| Excel emails being re-searched | Parse email from Excel upfront, pass directly to contact finder |
| Single Groq account hitting daily limit | Split into two accounts — one per task type |
