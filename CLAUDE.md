# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

## Full Architecture & Reference

**See [`PROJECT_CONTEXT.md`](./PROJECT_CONTEXT.md) for everything else** — architecture diagram,
data flow, Supabase schema, API endpoints per tab, known Meta API limitations/workarounds,
chatbot details, key calculations, error handling, and pending tasks.

## Key Constraints (always apply)

- **Organic-only**: `act_765947885726761` is blocklisted in `config.py`. Never fetch or display
  paid/ad metrics outside `api/boost.py`.
- **Date handling**: all date calculations use `datetime.now(timezone.utc)`; keep this consistent.
- **Cache**: Supabase is a *permanent* cache keyed by `(metric_key, period_start, period_end)`.
  Only the "Refresh Data" button invalidates it — see `db.py` and `api/base.py:_cache_key_range()`.

## Maintenance

- **Keep `PROJECT_CONTEXT.md` up to date.** Whenever you make a change that affects architecture,
  data flow, API endpoints, schema, env vars, or known limitations, update `PROJECT_CONTEXT.md`
  in the same change — without waiting to be asked.
- Do not duplicate architecture details back into this file — keep this file short.
