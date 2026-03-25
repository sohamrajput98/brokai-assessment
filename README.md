# Brokai Lead Intelligence System

A multi-agent pipeline that autonomously researches companies, finds contact information, and generates personalised cold outreach messages — built as a take-home assessment for Brokai Labs.

**Live URL:** _[Add your deployed URL here]_

---

## What It Does

Three specialised agents work in sequence for each company:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **01 — Researcher** | Searches the web to build a business profile | Company name + location | Summary, digital presence, CRM usage |
| **02 — Contact Finder** | Locates phone, email, WhatsApp from directories | Business profile | Contact card with source URL |
| **03 — Outreach Writer** | Generates a personalised WhatsApp-style cold message | Profile + contact card | Ready-to-send message |

---

## Stack

- **Backend:** FastAPI (Python)
- **LLM:** Groq (Llama 3 8B) — free tier
- **Web Search:** Tavily — free tier
- **Frontend:** Vanilla HTML/CSS/JS
- **Deployment:** Render (free tier)

---

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/your-username/brokai-assessment.git
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
# Edit .env and add your keys
```

**4. Add the companies Excel file**
```bash
mkdir data
# Copy Take_home_assesment.xlsx into the data/ folder
```

**5. Run the server**
```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` and click **Run on All Companies**.

---

## Environment Variables

```
GROQ_API_KEY=gsk_...        # From console.groq.com
TAVILY_API_KEY=tvly-...     # From app.tavily.com
```

See `.env.example` for the template.

---

## Deploy on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect repo
3. Add `GROQ_API_KEY` and `TAVILY_API_KEY` as environment variables
4. Deploy — the `render.yaml` handles the rest

---

## Design Decisions & Tradeoffs

- **Agents are plain Python classes** — no LangChain overhead. Each agent has a single `run()` method with a clear input/output contract. This keeps the architecture readable and debuggable.
- **Graceful failure at every step** — if search fails, LLM extraction fails, or a company has no public data, the system returns a `failed` row with honest fallback values rather than crashing or skipping.
- **Tavily for search** — free tier, returns clean structured results without scraping complexity. Sufficient for the volume of this task.
- **Groq (Llama 3 8B)** — fast and free. Temperature set low (0.1–0.2) for extraction agents for consistency, higher (0.7) for the outreach writer for natural-sounding messages.
