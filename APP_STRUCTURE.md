# APP_STRUCTURE.md
## Footland Dashboard — UI Layout & Data-Flow Specification

**Last Updated:** 2026-04-23  

---

## 1. Application Layout Overview

```
┌──────────────────────────────────────────────────────────────────┐
│  SIDEBAR                        │  MAIN CONTENT AREA             │
│  ─────────────────              │  ──────────────────────────    │
│  🏷️ Footland Logo               │  Page Title + Last Refresh     │
│                                 │                                │
│  📱 Platform Selector           │  ┌─────────────────────────┐  │
│     ○ Facebook                  │  │  KPI Row (st.metric ×4) │  │
│     ○ Instagram                 │  └─────────────────────────┘  │
│                                 │                                │
│  📅 Date Range Picker           │  Tab 1: Audience              │
│     [Last 7d / 30d / 90d]       │  Tab 2: Engagement            │
│                                 │  Tab 3: Visibility            │
│  🔄 Refresh Button              │  Tab 4: Top Content           │
│                                 │  Tab 5: Community Mgmt        │
│  ─────────────────              │                                │
│  ℹ️ Connection Status            │                                │
│  ⚙️ API Health Badge             │                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Sidebar Logic

| Element | Type | Behavior |
|---------|------|----------|
| Footland Brand Header | `st.markdown` | Static logo + brand name |
| Platform Selector | `st.radio` | Switches all data sources between FB/IG |
| Date Range | `st.selectbox` | `["Last 7 Days", "Last 30 Days", "Last 90 Days"]` — maps to `period` param in API calls |
| Refresh | `st.button` | Clears `st.cache_data` and re-fetches all data, then appends to `AI_CONTEXT_LOG.md` |
| Connection Status | `st.success / st.error` | Shows API health (green = connected, red = error) |

---

## 3. KPI Header Row

Rendered immediately below the page title using `st.columns(4)` + `st.metric`:

| Column | Metric | Delta logic |
|--------|--------|-------------|
| Col 1 | **Total Followers** | vs. start of selected period |
| Col 2 | **Engagement Rate** | vs. previous equivalent period |
| Col 3 | **Total Reach** | vs. previous equivalent period |
| Col 4 | **Page Views** | vs. previous equivalent period |

---

## 4. Tab Sections

### Tab 1 — Audience
**Goal:** Understand follower growth and churn trends.

**Data Sources:**
- Facebook: `GET /{page-id}/insights` → `page_fans`, `page_fan_adds`, `page_fan_removes`
- Instagram: `GET /{ig-user-id}?fields=followers_count` + `GET /{ig-user-id}/insights` → `follower_count`

**Components:**
- `st.line_chart` — Daily net follower change (adds − removes) over selected period
- `st.area_chart` — Cumulative follower count over time
- `st.columns(3)` — Three metrics: Total Followers | New Followers | Unfollows

**Logic:**
```python
# Net growth per day
net_growth[day] = fan_adds[day] - fan_removes[day]
# Cumulative from start of period
cumulative = baseline + cumsum(net_growth)
```

---

### Tab 2 — Engagement
**Goal:** Track reactions, comments, and shares at the daily level.

**Data Sources:**
- Facebook: `GET /{page-id}/insights` → `page_post_engagements`, `page_actions_post_reactions_total`
- Instagram: `GET /{ig-user-id}/insights` → `likes`, `comments`, `shares`, `saves`

**Components:**
- Plotly stacked bar chart — Reactions / Comments / Shares per day
- `st.metric` row — Total Reactions | Total Comments | Total Shares | Engagement Rate
- `st.line_chart` — 7-day rolling average engagement rate

**Logic:**
```python
engagement_rate = (reactions + comments + shares) / reach * 100
rolling_avg = pd.Series(engagement_rate).rolling(7).mean()
```

---

### Tab 3 — Visibility
**Goal:** Analyze reach and page view fluctuations (peaks at mid-month / end-of-month).

**Data Sources:**
- Facebook: `page_impressions_unique`, `page_impressions`, `page_views_total`
- Instagram: `impressions`, `reach`, `profile_views`

**Components:**
- Plotly dual-axis line chart — Reach (left axis) + Page Views (right axis) over time
- Vertical annotations at detected peak dates
- `st.metric` row — Avg Daily Reach | Peak Reach Day | Total Impressions | Profile Views

**Peak Detection Logic:**
```python
import numpy as np
peaks = df[df['reach'] > df['reach'].mean() + df['reach'].std()]
# Annotate on chart with plotly shapes
```

---

### Tab 4 — Top Content
**Goal:** Rank the Top 3 posts by visibility and interaction.

**Data Sources:**
- Facebook: `GET /{page-id}/posts` with `fields=message,created_time,full_picture,insights.metric(post_impressions_unique,post_engaged_users,post_reactions_by_type_total,post_comments,post_shares)`
- Instagram: `GET /{ig-user-id}/media` with `fields=caption,media_type,thumbnail_url,media_url,timestamp,like_count,comments_count,insights`

**Components:**
- Two sub-columns: "Top by Reach" | "Top by Engagement"
- Each post rendered as a card: Thumbnail + Caption snippet + 3 KPI badges
- `st.expander` — "View all posts" table

**Ranking Logic:**
```python
top_by_reach = posts_df.nlargest(3, 'reach')
top_by_engagement = posts_df.nlargest(3, 'total_interactions')
total_interactions = reactions + comments + shares
```

---

### Tab 5 — Community Management
**Goal:** Measure response rates and response timing stats.

**Data Sources:**
- Facebook: `GET /{page-id}/conversations` → message threads + timestamps
- Facebook: `GET /{page-id}/feed` → comment threads + reply timestamps

**Components:**
- `st.metric` row — Response Rate % | Avg Response Time | Total Conversations | Unread Count
- Plotly heatmap — Engagement hour-of-day × day-of-week (shows peak interaction windows)
- `st.dataframe` — Recent unanswered comments/messages

**Logic:**
```python
# Response rate
response_rate = replied_threads / total_threads * 100

# Avg response time (minutes)
avg_time = mean([reply.timestamp - first_msg.timestamp for thread in threads])

# Heatmap
heatmap_data = df.groupby(['hour', 'weekday'])['interactions'].sum().unstack()
```

---

## 5. Data-Flow Diagram

```
[Meta Graph API]
      │
      ▼
[api_client.py]  ←── config.py (token, IDs, constants)
      │
      │   fetch_page_insights()
      │   fetch_ig_insights()
      │   fetch_posts()
      │   fetch_conversations()
      │
      ▼
[app.py]  ←── st.cache_data (TTL=15min)
      │
      ├── Sidebar (platform/date controls)
      ├── KPI Header
      ├── Tab: Audience
      ├── Tab: Engagement
      ├── Tab: Visibility
      ├── Tab: Top Content
      └── Tab: Community
            │
            ▼
      [AI_CONTEXT_LOG.md]  ←── log_refresh() called on every data load
```

---

## 6. Error Handling Strategy

| Error Type | Handling |
|-----------|----------|
| `401 Unauthorized` | Display `st.error("Token expired — please refresh your access token")` |
| `403 Forbidden` | Display `st.warning("Insufficient permissions for this metric")` + show available data |
| `429 Rate Limited` | Exponential backoff (3 retries), show `st.info("Rate limited — retrying...")` |
| Network Error | Use cached data if available, show `st.warning("Using cached data")` |
| Empty Response | Show empty state components with `st.info("No data available for this period")` |
