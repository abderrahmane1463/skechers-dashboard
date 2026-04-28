# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
pip install -r requirements.txt
export FOOTLAND_TOKEN="<meta-graph-api-long-lived-page-access-token>"
streamlit run app.py
```

The dashboard runs at `http://localhost:8501`.

## Architecture

Three layers with a strict organic-only constraint:

```
app.py  (Streamlit UI)
  └─> api_client.py  (Meta Graph API wrapper)
        └─> config.py  (constants, credentials, metric names)
              └─> Meta Graph API v19.0
```

**`app.py`** — All UI logic. Sidebar controls (platform selector FB/IG, date range picker, refresh button) drive the entire dashboard. Main content is split into 5 Streamlit tabs per platform: Audience, Engagement, Visibility, Top Content, Community Management. Ten `@st.cache_data(ttl=900)` wrapper functions sit between the UI and `api_client`. Charts are Plotly figures styled with a shared `CHART_LAYOUT` dict.

**`api_client.py`** — All HTTP calls. `_get()` implements exponential-backoff retry (3 attempts, multiplier=2.0). Every endpoint runs through `_assert_not_blocked()` which raises `ValueError` if the URL contains a blocklisted ad account ID — this enforces the organic-only constraint. Per-post insight fetching uses `ThreadPoolExecutor(max_workers=10)`. API calls use fallback metric names when primary names fail (e.g. `page_daily_follows` → `page_fan_adds`).

**`config.py`** — Constants only. `ACCESS_TOKEN` reads from the `FOOTLAND_TOKEN` environment variable. Metric name arrays (`FB_AUDIENCE_METRICS`, `IG_ENGAGEMENT_METRICS`, etc.) used by api_client live here. `BLOCKED_AD_ACCOUNTS` contains the hardcoded ad account IDs that `_assert_not_blocked()` enforces.

## Tab Data Sources

Each tab pulls from specific Graph API endpoints:

| Tab | Facebook endpoints | Instagram endpoints |
|-----|-------------------|---------------------|
| **Audience** | `/{page-id}/insights` → `page_fans`, `page_fan_adds`, `page_fan_removes` | `/{ig-user-id}?fields=followers_count` + `/insights` → `follower_count` |
| **Engagement** | `/insights` → `page_post_engagements`, `page_actions_post_reactions_total` | `/insights` → `likes`, `comments`, `shares`, `saves` |
| **Visibility** | `/insights` → `page_impressions_unique`, `page_impressions`, `page_views_total` | `/insights` → `impressions`, `reach`, `profile_views` |
| **Top Content** | `/{page-id}/posts` with `insights.metric(post_impressions_unique, post_engaged_users, ...)` | `/{ig-user-id}/media` with `like_count`, `comments_count`, `insights` |
| **Community** | `/{page-id}/conversations` (message threads) + `/{page-id}/feed` (comment threads) | — |

**KPI Header row** (4 `st.metric` columns above all tabs):
- Total Followers — delta vs. start of selected period
- Engagement Rate — delta vs. previous equivalent period
- Total Reach — delta vs. previous equivalent period
- Page Views — delta vs. previous equivalent period

## Key Calculations

```python
# Audience tab
net_growth[day] = fan_adds[day] - fan_removes[day]
cumulative = baseline + cumsum(net_growth)

# Engagement tab
engagement_rate = (reactions + comments + shares) / reach * 100
rolling_avg = pd.Series(engagement_rate).rolling(7).mean()

# Visibility tab — peak detection
peaks = df[df['reach'] > df['reach'].mean() + df['reach'].std()]

# Top Content tab
total_interactions = reactions + comments + shares
top_by_reach = posts_df.nlargest(3, 'reach')
top_by_engagement = posts_df.nlargest(3, 'total_interactions')

# Community tab
response_rate = replied_threads / total_threads * 100
avg_time = mean([reply.timestamp - first_msg.timestamp for thread in threads])
```

## Error Handling

| HTTP error | UI response |
|-----------|-------------|
| 401 Unauthorized | `st.error("Token expired — please refresh your access token")` |
| 403 Forbidden | `st.warning(...)` + show available data |
| 429 Rate Limited | Exponential backoff (3 retries) + `st.info("Rate limited — retrying...")` |
| Network error | Use cached data + `st.warning("Using cached data")` |
| Empty response | `st.info("No data available for this period")` |

## Caching

- 15-minute TTL for most metrics (`CACHE_TTL_SECONDS = 900`)
- 60-minute TTL for demographics (slow/stable data)
- The "Refresh Data" button calls `st.cache_data.clear()` to force a full reload
- `log_refresh()` in app.py appends every refresh event to `AI_CONTEXT_LOG.md`

## Key Constraints

- **Organic-only**: `act_765947885726761` is blocklisted. Never fetch or display paid/ad metrics.
- **No database**: all data comes from Meta Graph API v19.0; no persistence layer exists.
- **Date handling**: all date calculations use `datetime.now(timezone.utc)`; keep this consistent.

## Scratch Utilities

`scratch/` contains one-off diagnostic scripts (`check_ads.py`, `deep_diag_ig.py`, etc.). These are not part of the app and should not be imported.
