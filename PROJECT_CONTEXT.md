# PROJECT_CONTEXT.md
## Skechers Algeria — Social Analytics Dashboard
**Last updated:** 2026-06-09 | **Status:** Production

---

## 1. Project Purpose

Internal analytics dashboard for the **Skechers Algeria** social media team. Aggregates
organic Facebook, organic Instagram, paid Meta campaigns (Boost), and Google Analytics 4
website data into a single Streamlit interface. The team uses it to track KPIs, interpret
trends, and monitor community management response rates.

The project started **2026-04-23** as a scaffold and reached production that same day.

---

## 2. Architecture

```
app.py  (entry point, routing, prefetch threads)
  ├── components/sidebar.py   (platform nav, date picker, chatbot UI)
  ├── components/charts.py    (shared Plotly helpers)
  ├── components/skeleton.py  (loading skeleton HTML)
  ├── views/facebook.py       (Facebook dashboard)
  ├── views/instagram.py      (Instagram dashboard)
  ├── views/boost.py          (Paid campaigns dashboard)
  ├── views/analytics.py      (Google Analytics 4 dashboard)
  ├── views/login.py          (Supabase Auth login form)
  ├── views/documentation.py  (in-app docs tab)
  ├── db.py                   (Supabase cache layer)
  ├── auth.py                 (Supabase Auth helpers)
  ├── fetcher.py              (background prefetch coordinator)
  ├── config.py               (constants, credentials, metric names)
  └── api/
        ├── base.py           (HTTP client, date utils, chunked insights)
        ├── facebook.py       (Facebook Graph API functions)
        ├── instagram.py      (Instagram Graph API functions)
        ├── boost.py          (Meta Marketing API functions)
        └── ga4.py            (Google Analytics 4 Data API)
```

### Data flow
```
Browser → Streamlit → db._get(metric_key, api_fn, days, start, end)
                           ↓ cache hit?
                    Supabase (permanent)  ←→  Meta Graph API v22+
                                              Meta Marketing API
                                              GA4 Data API v1beta
```

### Key architectural decision: Supabase as permanent cache
The original design (see CLAUDE.md) used `@st.cache_data(ttl=900)`. This was replaced with
**Supabase as a permanent cache** keyed by `(metric_key, period_start, period_end)`.

- Rolling periods (`Last 7 Days`, `Last 30 Days`, etc.) use **stable keys** `("rolling", "last_Xd")` — the same Supabase row is reused across all users and sessions. The cache never expires; only a manual "Refresh Data" click wipes it.
- Fixed/calendar ranges use the actual ISO dates as keys.
- The cache key logic lives in `api/base.py:_cache_key_range()`.

**Why:** Meta API rate limits and slow per-post insight calls (N+1 pattern, up to 100 posts × 2 API calls each) made the app unusable without a persistent cache. Supabase's free tier provides enough storage.

---

## 3. Credentials & Environment Variables

| Variable | Purpose | Where used |
|----------|---------|------------|
| `SKECHERS_TOKEN` | Meta Graph API long-lived Page Access Token (organic) | `config.py` → `ACCESS_TOKEN` |
| `SKECHERS_ADS_TOKEN` | Meta User Access Token with `ads_read` scope (Boost tab) | `config.py` → `ADS_ACCESS_TOKEN` |
| `SUPABASE_URL` | Supabase project REST endpoint | `db.py`, `auth.py` |
| `SUPABASE_KEY` | Supabase anon/service key | `db.py`, `auth.py` |
| `GROQ_API_KEY` | Groq API key for chatbot LLM | `components/chatbot.py` |
| `GEMINI_API_KEY` | Legacy — was the original chatbot provider, now unused | `config.py` (dead code) |

The tokens are also **hardcoded as fallbacks** in `config.py` lines 15–23 (Page token) and 21–23 (Ads token). This is a security risk in public repos — they should be moved to env/secrets only.

### Meta Asset IDs (hardcoded in config.py)
- **Facebook Page ID:** `707444622669651`
- **Instagram User ID:** `17841408456074839`
- **Ad Account:** `act_765947885726761` (blocklisted for organic endpoints; Boost tab's single authorised source)
- **GA4 Property ID:** `313002599`

---

## 4. API Details

### 4.1 Meta Graph API (Organic — Facebook & Instagram)
- **Version:** v22+ (config.py still says v19.0 but instagram.py was updated to v22+ patterns)
- **Base URL:** `https://graph.facebook.com/v19.0/`
- **HTTP client:** `api/base.py:_get()` — exponential backoff, 3 retries, 30s timeout
- **Block guard:** `_assert_not_blocked()` raises `ValueError` if the ad account ID appears in any endpoint URL, enforcing the organic-only constraint

#### Facebook endpoints used
| Endpoint | Purpose |
|----------|---------|
| `/{page-id}/insights/page_fans` | Total fan count (lifetime) |
| `/{page-id}/insights` + `page_fan_adds` / `page_daily_follows` | Daily follower adds |
| `/{page-id}/insights` + `page_fan_removes` / `page_daily_unfollows` | Daily follower removes |
| `/{page-id}/insights` + `page_post_engagements` | Daily engagement |
| `/{page-id}/insights` + `page_actions_post_reactions_total` | Daily reaction breakdown |
| `/{page-id}/insights` + `page_posts_impressions` | Daily impressions (replaces deprecated `page_impressions`) |
| `/{page-id}/insights` + `page_impressions_unique` | Unique reach (period=day/week/month) |
| `/{page-id}/insights` + `page_views_total` | Page views |
| `/{page-id}/insights` + `page_messages_new_conversations_unique` | New DM conversations |
| `/{page-id}/posts` | Post list with inline engagement |
| `/{post-id}/insights` | Per-post reach, reactions, video views |
| `/{page-id}/conversations` | DM threads for Community Management |
| `/{page-id}` + `fan_count` | Fallback follower count |

#### Instagram endpoints used
| Endpoint | Purpose |
|----------|---------|
| `/{ig-user-id}` + `followers_count,username` | Total followers snapshot |
| `/{ig-user-id}/insights` + `reach` + `metric_type=total_value` | Period reach (deduplicated, ≤30 day limit) |
| `/{ig-user-id}/insights` + `views` + `metric_type=total_value` | Period total views (posts+stories+reels) |
| `/{ig-user-id}/insights` + `likes/comments/shares/saves` + `metric_type=total_value` | Period interaction totals |
| `/{ig-user-id}/insights` + `total_interactions` + `metric_type=total_value` | Period total interactions |
| `/{ig-user-id}/insights` + `reach/views/profile_views` + `metric_type=time_series` | Daily series charts |
| `/{ig-user-id}/media` + field expansion | Posts with all metrics in 1 call |
| `/{ig-user-id}/stories` + `insights.metric(impressions,reach)` | Story impressions |
| `/{page-id}/conversations?platform=instagram` | IG DM threads |

#### Chunking for wide date ranges
`api/base.py:_get_insights_chunked()` splits requests > 88 days into consecutive chunks.
This is required because the Meta Insights API silently returns nothing for windows > ~92 days.
Used for all Facebook Audience, Engagement, Visibility daily series calls.

### 4.2 Meta Marketing API (Boost tab)
- **Token:** `ADS_ACCESS_TOKEN` (separate User token, requires `ads_read`)
- **HTTP client:** `api/boost.py:_get_ads()` — bypasses `_assert_not_blocked()` intentionally
- **Ad Account:** `act_765947885726761`
- **Campaign identification:** Filters by `SKECHERS_CAMPAIGN_KEYWORDS` = `["707444622669651", "SKX ", "Skechers"]` — must match campaign name. Update if agency changes naming convention.

Campaign data is fetched at 3 levels:
- Account-level: deduplicated reach only (cannot sum per-campaign reach)
- Campaign-level: spend, impressions, clicks, CTR, CPC, conversions, ROAS
- Adset-level + Ad-level: detailed breakdown for the Ads Manager export tab

**Conversion objectives** tracked: `CONVERSIONS`, `OUTCOME_SALES`

### 4.3 Google Analytics 4
- **Client:** `google.analytics.data_v1beta.BetaAnalyticsDataClient` (service account)
- **Auth:** Service account JSON from `ga4_token.json` (local) or `st.secrets["ga4"]["token_json"]` (Streamlit Cloud)
- **Property ID:** `313002599`
- **Note:** Streamlit Cloud TOML may deliver `\n` as literal `\\n` in `private_key` — `api/ga4.py` normalises this.

Data fetched in a single credential refresh via `fetch_all_ga4_data(start, end)`:
- Overview metrics (users, sessions, engagement rate, bounce rate)
- Traffic sources by channel group
- Top pages
- Geography (countries + cities)
- Devices
- Purchase funnel: `session_start → view_item → add_to_cart → begin_checkout → purchase`
- E-commerce items (viewed/cart/purchased per product)
- All events table

---

## 5. Known API Limitations & Workarounds

### Instagram
| Limitation | Workaround applied |
|-----------|-------------------|
| Per-post `like_count` is privacy-filtered by Meta (API returns e.g. 88 but real count is 2,500+) | Nothing can be done — API limitation. Chatbot system prompt documents this. |
| `impressions` metric deprecated in v22+ for IMAGE and CAROUSEL posts | Use `views` metric for per-post visibility. For account-level daily series, `views` replaces `impressions`. |
| `views` metric does NOT support `metric_type=time_series` | Fetch via `metric_type=time_series` with fallback to legacy `period=day` |
| `reach` API only accepts windows ≤ 30 days for `metric_type=total_value` | Dashboard shows "—" for Couverture when period > 30 days |
| No daily breakdown for `views` | Only total_value aggregate available |
| `impressions` metric on stories is separate from account-level insights | Fetched separately via `/{ig-user-id}/stories` |
| Follower daily series: metric name varies by API version | Try `follower_count`, `profile_follows`, `total_followers_count` in sequence, then `metric_type=total_value` fallback |
| `until` timestamp for daily series needs +1 day so single-day periods (e.g. Yesterday) return data | Two separate `until_ts` values: `until_ts` (+1 day for series) and `until_ts_exact` (exact, for total_value reach ≤30d) |

### Facebook
| Limitation | Workaround applied |
|-----------|-------------------|
| `page_impressions` blocked for New Page Experience pages (returns `#100` error) | Use `page_posts_impressions` — confirmed working, returns expected value |
| `page_impressions_fan` and `page_impressions_paid` deprecated for New Page Experience | Try `page_posts_impressions_fan` / `page_posts_impressions_nonviral`; fail silently |
| `page_fans_gender_age` blocked for New Page Experience | Demographics uses Marketing API paid reach as proxy |
| `post_impressions`, `post_impressions_organic` (aggregate) return `#100` for this page type | Request only `_unique` variants: `post_impressions_unique`, `post_impressions_organic_unique`, etc. |
| One bad metric in a batch call silently kills all other metrics in the same call | Split into separate API calls per metric group (reach metrics + dict metrics) |
| Insights API silently returns nothing for windows > ~92 days | `_get_insights_chunked()` splits into ≤88-day chunks |
| `page_impressions_unique` (deduplicated reach) only has exact API mapping for 1d, 7d, 28-31d windows | For other window sizes (14d, 60d, 90d, quarters), dashboard shows "—" instead of a misleading approximation |
| `/conversations` endpoint ignores `since`/`until` parameters | Filter threads client-side by `updated_time` date prefix; stop pagination when oldest thread is before `since` |

---

## 6. Supabase Schema

### Table: `metric_cache`
| Column | Type | Notes |
|--------|------|-------|
| `id` | int (PK) | Auto-increment |
| `metric_key` | text | e.g. `"ig_profile"`, `"fb_audience"` |
| `period_start` | text | ISO date or `"rolling"` |
| `period_end` | text | ISO date or `"last_30d"` |
| `data` | jsonb | Raw API result as JSON |
| `fetched_at` | timestamptz | When the row was written |

Unique constraint on `(metric_key, period_start, period_end)`.
`db.save()` does POST then PATCH on 409.

### Metric keys
- `ig_profile`, `ig_engagement`, `ig_posts`, `ig_post_totals`
- `fb_audience`, `fb_engagement`, `fb_visibility`, `fb_demographics`, `fb_posts`, `fb_post_totals`, `fb_conversations`, `fb_messaging`
- `boost_insights`, `boost_adset_ad`

### In-memory invalidation registry (`db._INVALIDATED`)
Refresh button calls `db.delete_period(start, end)` which does a hard DELETE.
Per-platform soft invalidation via `db.invalidate(platform, start, end)` marks keys in
`_INVALIDATED` dict; `db.load()` skips rows fetched before the invalidation timestamp.

### Table: `profiles`
| Column | Notes |
|--------|-------|
| `user_id` | FK to Supabase auth.users |
| `role` | `"admin"` or `"viewer"` |
| `display_name` | Shown in sidebar |

---

## 7. Authentication

`auth.py` wraps Supabase Auth (`/auth/v1/token?grant_type=password`).
Login returns `{user_id, email, access_token, role, display_name}` stored in `st.session_state["user"]`.

- **admin** role: sees Supabase health indicator in sidebar, sees "Connecté" label
- **viewer** role: same dashboard, no admin widgets
- Logout: `del st.session_state["user"]` + `st.rerun()`

---

## 8. Chatbot

### LLM Stack
- **Provider:** Groq (not Gemini — `config.py` still has a dead `GEMINI_API_KEY` constant)
- **Primary model:** `llama-3.3-70b-versatile`
- **Fallback model:** `llama-3.1-8b-instant` (on 429 rate limit)
- **Temperature:** 0.7 | **Max tokens:** 1024

### Location
The chat UI is rendered inside `components/sidebar.py` (not `chatbot.py`).
`chatbot.py:render_chatbot()` is a no-op stub kept for backward compatibility.
The actual logic functions `_get_groq_response()` and `_build_data_context()` are imported
from `chatbot.py` into `sidebar.py`.

### Dynamic data injection
`_build_data_context()` reads from `st.session_state`:
- `ctx_instagram` — written by `views/instagram.py` when the IG tab loads
- `ctx_facebook` — written by `views/facebook.py` when the FB tab loads
- `ctx_boost` — written by `views/boost.py` when the Boost tab loads
- `ctx_ga4` — written by `views/analytics.py` when the GA4 tab loads

The full system prompt + live dashboard data is injected on every API call.
Conversation history is stored in `st.session_state.chat_history`.

### System prompt scope
The bot is constrained to dashboard-related questions only.
Responds in the user's language (French / English / Arabic).
Documents known API limitations (privacy-filtered likes, reach window limits, deprecated metrics).

---

## 9. Background Prefetch

`app.py` spawns two daemon threads on load:
- `_prefetch_facebook(days, start, end)` — calls all 7 Facebook db getters
- `_prefetch_instagram(days, start, end)` — calls all 4 Instagram db getters

These pre-populate the Supabase cache so tab switches are instant.
Threads are fire-and-forget; errors are silently swallowed.

---

## 10. Key Calculations

```python
# Audience (Facebook)
net_growth[day] = fan_adds[day] - fan_removes[day]
cumulative = baseline + cumsum(net_growth)

# Engagement rate (Instagram)
engagement_rate = total_interactions / reach * 100  # reach = period_reach

# Boost: Frequency (correct — NOT a simple average)
frequency = total_impressions / deduplicated_reach

# Boost: Weighted CPC
cpc = total_spend / total_link_clicks

# Boost: ROAS
roas = purchase_value / spend

# Community Management
response_rate = replied_threads / total_threads * 100
avg_response_time = mean(response_times_minutes)
```

---

## 11. Error Handling

| HTTP error | UI response |
|-----------|-------------|
| 401 Unauthorized | `st.error("Token expired")` |
| 403 Forbidden | `st.warning(...)` + show available data |
| 429 Rate Limited | Exponential backoff (3 retries) + `st.info("Rate limited — retrying...")` |
| Network error | Use cached Supabase data + `st.warning("Using cached data")` |
| Empty response | `st.info("No data available for this period")` |

---

## 12. Running the App

```bash
pip install -r requirements.txt

# Required env vars
export SKECHERS_TOKEN="<meta-graph-api-long-lived-page-access-token>"
export SKECHERS_ADS_TOKEN="<meta-marketing-api-user-token>"
export SUPABASE_URL="https://<project>.supabase.co"
export SUPABASE_KEY="<anon-or-service-key>"
export GROQ_API_KEY="<groq-key>"

# GA4 service account — either place file locally OR configure Streamlit secrets
# Local: place ga4_token.json in project root
# Cloud: add [ga4] token_json = '...' to .streamlit/secrets.toml

streamlit run app.py
```

Dashboard runs at `http://localhost:8501`.

---

## 13. Pending Tasks & Known Issues

### High priority
- [ ] **Token hardcoded in config.py** — The Meta Page token and Ads token are hardcoded as fallback values (lines 15–23). This is a security risk. They should be env-only with no fallback hardcode.
- [ ] **`chatbot.py` dead code** — The large `if False:` block (lines 267–436) and `_render_chatbot_sidebar()` stub should be deleted. The old floating-panel CSS is dead weight.
- [ ] **`config.py:GEMINI_API_KEY`** — Dead constant from the original chatbot provider. Remove.
- [ ] **`GRAPH_API_VERSION = "v19.0"`** — Config still says v19.0 but the Instagram API code targets v22+ patterns (metric_type, views replacing impressions). Should be updated to `"v22.0"`.

### Medium priority
- [ ] **README.md is empty** — Only contains `# SKECHERS DASHBOARD`. Should at minimum link to this file.
- [ ] **AI_CONTEXT_LOG.md is noisy** — 2,500+ lines of repetitive refresh events. The auto-append `log_refresh()` function in `app.py` writes every single refresh. Should be rate-limited (e.g. one entry per day per platform) or the file should be rotated.
- [ ] **Demographics tab uses paid data as proxy** — `fetch_fb_demographics()` uses the Marketing API because `page_fans_gender_age` is blocked for New Page Experience pages. This should be documented in the UI for the team.
- [ ] **IG daily `views` series not available** — `metric_type=time_series` is not supported for the `views` metric. The daily chart falls back to `impressions` which may be deprecated. Needs UI note.
- [ ] **Boost tab: `SKECHERS_CAMPAIGN_KEYWORDS`** — The agency can change campaign naming at any time. If campaigns disappear from the Boost tab, check this list first.

### Low priority
- [ ] **`fetcher.py`** — File exists but its role vs. the inline `_prefetch_*` functions in `app.py` is unclear. Needs audit.
- [ ] **`db_setup.py`** — File exists but is not imported anywhere. Likely a one-time Supabase schema setup script. Should be moved to `scratch/` or documented.
- [ ] **`ga4_auth.py`** — File exists at root. Its relationship to `api/ga4.py:_get_credentials()` is unclear. Needs audit.
- [ ] **`ga4_token_fixed.json`** — Untracked file in git status. Likely a development credential file. Should be confirmed gitignored.
- [ ] **`test.pem`** — Untracked file in git status. Unknown purpose. Should be confirmed gitignored.
- [ ] **`scratch/` scripts** — `check_ads.py`, `deep_diag_ig.py`, `diag_post_likes.py`, `test_ig_followers.py` are diagnostic scripts from development. Safe to delete if no longer needed.

---

## 14. Architecture Decisions Log

| Decision | Rationale |
|----------|-----------|
| Streamlit over React/Vue | Speed of development for internal tool; team comfort level; sufficient for the use case |
| Supabase permanent cache instead of `st.cache_data` TTL | Meta API rate limits + slow N+1 per-post insight calls made the original TTL-based approach unusable |
| Groq/LLaMA 3.3 instead of OpenAI or Gemini | Groq's free tier is fast; LLaMA 3.3 70B is sufficient for dashboard Q&A; Gemini was the original choice (hence dead `GEMINI_API_KEY`) |
| Organic constraint enforced at HTTP layer (`_assert_not_blocked`) | Prevents any accidental ad account queries even if new API functions are added |
| Separate `ADS_ACCESS_TOKEN` for Boost | The page token does not have `ads_read` scope; a separate User token is required for the Marketing API |
| Field expansion for IG posts (`insights.metric(...)`) | Eliminates N+1 per-post API calls — all post metrics in 1 call |
| ThreadPoolExecutor for FB per-post insights | 20 concurrent workers; per-post API calls cannot be batched via field expansion on the FB side |
| `_get_insights_chunked()` for wide date ranges | Meta Insights API silently fails for windows > ~92 days; 88-day chunks are safe |
| Stable cache keys for rolling periods | Prevents unbounded Supabase row growth; same key reused indefinitely, refreshed only on demand |
| Chatbot context from `st.session_state` | The bot needs the current numbers to answer "what was our reach this month?" — injected per-call so always current |
