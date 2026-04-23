# PROJECT_OVERSIGHT.md
## Footland — Organic Social Analytics Dashboard

**Last Updated:** 2026-04-23  
**Status:** 🟡 In Development  
**Owner:** Footland Social Media Team  

---

## 1. Project Scope

This dashboard provides a **real-time, organic-only** social media analytics view for the Footland brand across Facebook and Instagram. It connects directly to the **Meta Graph API** and surfaces audience, engagement, reach, and content performance metrics in a clean Streamlit interface.

> ⚠️ **Strict Constraint:** Ad Account `act_765947885726761` and all paid/benchmark data are explicitly excluded. Only organic page and profile data is surfaced.

---

## 2. Connected Assets

| Platform   | Asset          | ID                    |
|------------|----------------|-----------------------|
| Facebook   | Footland Page  | `144124252311741`     |
| Instagram  | Footland Profile | `1784140300085491`  |
| Meta API   | Access Token   | Stored in `config.py` / `.env` |

---

## 3. Core Metrics

### 3.1 Audience
| Metric | Description | API Field |
|--------|-------------|-----------|
| Total Followers | Current total fan/follower count | `page_fans` / `followers_count` |
| Follower Growth | Net new followers over date range | `page_fan_adds` |
| Follower Churn | Unfollows/unlikes over date range | `page_fan_removes` |
| Net Growth | Adds minus removes | Calculated |

### 3.2 Engagement
| Metric | Description | API Field |
|--------|-------------|-----------|
| Reactions | Likes, loves, etc. on posts | `post_reactions_by_type_total` |
| Comments | Comments on posts | `post_comments` |
| Shares | Post shares | `post_activity_by_action_type` |
| Engagement Rate | (Reactions + Comments + Shares) / Reach × 100 | Calculated |

### 3.3 Visibility / Reach
| Metric | Description | API Field |
|--------|-------------|-----------|
| Page Reach | Unique accounts reached | `page_impressions_unique` |
| Post Impressions | Total impressions across posts | `page_impressions` |
| Page Views | Profile page visits | `page_views_total` |

### 3.4 Top Content
| Metric | Description |
|--------|-------------|
| Top 3 Posts by Reach | Posts sorted by unique reach |
| Top 3 Posts by Engagement | Posts sorted by total interactions |
| Post Type Breakdown | Photo, Video, Reel, Story |

### 3.5 Community Management
| Metric | Description |
|--------|-------------|
| Response Rate | % of comments/messages replied to |
| Avg. Response Time | Mean time to first reply |
| Peak Engagement Hours | Hours with most interactions |

---

## 4. Technical Constraints

- **Language:** Python 3.9+
- **Frontend:** Streamlit
- **API Client:** `requests` library (no SDK)
- **Auth:** Long-lived Page Access Token via Meta Graph API v19.0
- **No paid data:** Ad Account and benchmark endpoints are blocked at the API client level
- **Date Granularity:** Daily metrics, default window = last 30 days
- **Rate Limits:** Respect Meta's 200 calls/hour per token limit; implement caching with `st.cache_data` (TTL = 15 min)

---

## 5. Deliverables

- [x] `PROJECT_OVERSIGHT.md` — This document
- [x] `APP_STRUCTURE.md` — UI layout and data-flow specification
- [x] `AI_CONTEXT_LOG.md` — Rolling change log
- [x] `app.py` — Main Streamlit application
- [x] `api_client.py` — Meta Graph API data-fetching module
- [x] `config.py` — Credentials and constants
- [x] `requirements.txt` — Python dependencies

---

## 6. Success Criteria

1. Dashboard loads without errors and authenticates against the Meta API.
2. All five sections (Audience, Engagement, Visibility, Top Content, Community) display real or gracefully degraded data.
3. No ad account or paid benchmark data is ever fetched or displayed.
4. `AI_CONTEXT_LOG.md` is automatically updated on every data refresh.
5. Dashboard is navigable between Facebook and Instagram via sidebar.
