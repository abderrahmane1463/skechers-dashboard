<h1 align="center">Footland — Social Media Analytics Dashboard</h1>

<p align="center">
  <em>Organic Facebook and Instagram performance analytics for the Footland football brand, powered by the Meta Graph API</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Meta_Graph_API-v19.0-0866FF?style=flat-square&logo=meta&logoColor=white"/>
  <img src="https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white"/>
</p>

---

## Overview

A real-time social media analytics dashboard for Footland, an Algerian football brand. The application fetches organic Facebook and Instagram metrics directly from the Meta Graph API v19.0 and presents them in a structured multi-tab Streamlit interface. All paid/ad data is strictly excluded by design — the dashboard is organic-only.

## Features

- Dual-platform support: Facebook and Instagram metrics in separate, parallel dashboards
- Five analytics tabs per platform: Audience · Engagement · Visibility · Top Content · Community Management
- Boost tab for paid campaign performance (Meta Ads analytics)
- 15-minute data cache (TTL=900s) with one-click refresh
- Exponential-backoff retry logic (3 attempts) for robust API calls
- Concurrent per-post insight fetching via ThreadPoolExecutor (10 workers)
- Organic-only enforcement — ad account blocklist prevents any paid metric from appearing

## Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.10+ |
| Dashboard | Streamlit |
| Data Source | Meta Graph API v19.0 |
| Visualisation | Plotly |
| HTTP Client | requests |

## Getting Started

```bash
git clone https://github.com/abderrahmane1463/footland.git
cd footland
pip install -r requirements.txt
export FOOTLAND_TOKEN="<your-meta-long-lived-page-access-token>"
streamlit run app.py
```

The dashboard runs at `http://localhost:8501`.

> The `FOOTLAND_TOKEN` environment variable must be set to a valid Meta Graph API long-lived Page Access Token. Never commit this token to version control.

## Project Structure

```
footland/
├── app.py          # Streamlit UI — sidebar controls, tab rendering, cache wrappers
├── api_client.py   # Meta Graph API wrapper — HTTP calls, retry logic, blocklist enforcement
├── config.py       # Constants, metric name arrays, blocked ad account IDs
├── auth.py         # Authentication helpers
├── fetcher.py      # Data fetching utilities
├── db.py           # Local state / session helpers
├── components/     # Reusable Streamlit UI components
├── views/          # Per-tab view modules
├── api/            # API abstraction layer
└── requirements.txt
```

---

<p align="center">Made by <a href="https://github.com/abderrahmane1463">Cherfaoui Houssam Abderrahmane</a></p>
