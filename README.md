# Skechers Dashboard

Internal Streamlit analytics dashboard for the Skechers Algeria social media team.
Aggregates organic Facebook, organic Instagram, paid Meta campaigns (Boost), and
Google Analytics 4 website data into a single interface, with an in-app AI assistant
and documentation tab.

## Quick Start

```bash
pip install -r requirements.txt

# Required env vars
export SKECHERS_TOKEN="<meta-graph-api-long-lived-page-access-token>"
export SKECHERS_ADS_TOKEN="<meta-marketing-api-user-token>"
export SUPABASE_URL="https://<project>.supabase.co"
export SUPABASE_KEY="<anon-or-service-key>"
export GROQ_API_KEY="<groq-key>"

streamlit run app.py
```

The dashboard runs at `http://localhost:8501`.

## Documentation

- [`CLAUDE.md`](./CLAUDE.md) — quick start for AI coding assistants
- [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md) — full architecture, data flow, Supabase
  schema, API endpoints, known limitations, chatbot details, and key calculations
- In-app "📖 Documentation" tab — KPI definitions and glossary for end users
