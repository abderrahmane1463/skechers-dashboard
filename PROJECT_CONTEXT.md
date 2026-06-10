# PROJECT_CONTEXT.md
## Skechers Algeria — Social Analytics Dashboard
**Last updated:** 2026-06-10 | **Status:** Production

> This is the **single source of truth** for this project's architecture, data flow, schema,
> known issues, and pending work. `CLAUDE.md` is intentionally short and points here.
> **This file must be kept up to date with every change** — architecture, endpoints, schema,
> env vars, limitations, UI structure, pending tasks — without needing to be asked.

---

## 1. Project Purpose

Internal analytics dashboard for the **Skechers Algeria** social media team. Aggregates
organic Facebook, organic Instagram, paid Meta campaigns (Boost), and Google Analytics 4
website data into a single Streamlit interface, plus an in-app AI assistant and documentation
tab. The team uses it to track KPIs, interpret trends, and monitor community management
response rates.

The project started **2026-04-23** as a scaffold and reached production that same day.

---

## 2. File Index

```
app.py                      Entry point — page config, theme CSS, auth guard, routing,
                             prefetch orchestration, chatbot mount point
auth.py                      Supabase Auth helpers (login, profile lookup)
config.py                     Constants, credentials, metric name lists, blocklist
db.py                          Supabase REST cache layer (load/save/get_* getters)
db_setup.py                  ⚠️ One-time Supabase schema creation script (psycopg2). Not
                             imported by the app — run manually once.
fetcher.py                    GitHub Actions cron script — pre-warms Supabase cache for
                             every sidebar period preset (runs every 6h)
ga4_auth.py                  ⚠️ One-time OAuth bootstrap for local GA4 dev (writes
                             ga4_token.json). Not imported by the app.

api/
  __init__.py                 Re-exports fetch_* functions for `import api`
  base.py                      _get() (retry+backoff), _assert_not_blocked(),
                             _date_range/_cache_key_range/_prev_date_range,
                             _get_insights_chunked(), check_api_health()
  facebook.py                  Facebook Graph API: audience, engagement, visibility,
                             posts, post totals, conversations, messaging, demographics
  instagram.py                 Instagram Graph API: profile, engagement, posts, totals
  boost.py                      Meta Marketing API: campaign/adset/ad insights,
                             Skechers campaign ID resolution + 3-tier caching
  ga4.py                        Google Analytics 4 Data API (service account auth)

components/
  __init__.py
  sidebar.py                  Platform nav, date range picker, Refresh Data button,
                             Assistant IA toggle, theme init, admin health panel, logout
  charts.py                     Shared Plotly CHART_LAYOUT / get_chart_layout(),
                             series_to_df, safe_sum/safe_last, render_top3_podium()
  skeleton.py                  Shimmer loading-skeleton HTML builders
  chatbot.py                    Groq-powered floating chat assistant (see §9)

views/
  __init__.py
  login.py                      Login page (Supabase Auth form)
  facebook.py                  Facebook dashboard (5 tabs)
  instagram.py                  Instagram dashboard (2 tabs)
  boost.py                       Boost / paid campaigns dashboard (6 tabs)
  analytics.py                  Google Analytics 4 dashboard (4 tabs)
  documentation.py              In-app "Guide du Dashboard" tab

assets/
  skechers_logo.png             Logo shown on login page and sidebar
  footland_logo.png             Unused — leftover from another client project

scratch/                       (gitignored) one-off diagnostic scripts, e.g.
                             check_rate_limit.py — checks Meta API rate-limit headers

.github/workflows/
  fetch.yml                     Cron (every 6h) — runs fetcher.py to pre-warm Supabase
  keepalive.yml                 Daily ping to keep Supabase project from pausing

CLAUDE.md                       Short quick-start + pointer to this file
PROJECT_CONTEXT.md              This file
AI_CONTEXT_LOG.md                Auto-appended refresh log
README.md                        Currently 1 line
requirements.txt                  Python dependencies
```

---

## 3. Architecture

```
app.py  (Streamlit UI, routing, theme, auth guard)
  ├── components/sidebar.py   (platform nav, date picker, refresh, chatbot toggle)
  ├── components/charts.py    (shared Plotly helpers, Top-3 podium)
  ├── components/skeleton.py  (loading skeleton HTML)
  ├── components/chatbot.py   (Groq floating assistant)
  ├── views/login.py          (Supabase Auth login form)
  ├── views/facebook.py       (Facebook dashboard)
  ├── views/instagram.py      (Instagram dashboard)
  ├── views/boost.py          (Paid campaigns dashboard)
  ├── views/analytics.py      (Google Analytics 4 dashboard)
  ├── views/documentation.py  (in-app docs tab)
  ├── db.py                   (Supabase cache layer)
  ├── auth.py                 (Supabase Auth helpers)
  ├── fetcher.py              (background prefetch coordinator — GitHub Actions cron)
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
                    Supabase (permanent)  ←→  Meta Graph API v19.0
                                              Meta Marketing API
                                              GA4 Data API v1beta
```

### Key architectural decision: Supabase as permanent cache
The original design (see old `CLAUDE.md`) used `@st.cache_data(ttl=900)`. This was replaced
with **Supabase as a permanent cache** keyed by `(metric_key, period_start, period_end)`.

- Rolling periods (`Last 7 Days`, `Last 30 Days`, etc.) use **stable keys**
  `("rolling", "last_Xd")` — the same Supabase row is reused across all users and sessions.
  The cache never expires; only a manual "Refresh Data" click wipes it.
- Fixed/calendar ranges use the actual ISO dates as keys.
- The cache key logic lives in `api/base.py:_cache_key_range()`.

**Why:** Meta API rate limits and slow per-post insight calls (N+1 pattern, up to 100 posts ×
2 API calls each) made the app unusable without a persistent cache. Supabase's free tier
provides enough storage.

---

## 4. UI / Theming

### Authentication gate (`app.py`)
- `if "user" not in st.session_state: render_login(); st.stop()` — blocks the entire app
  until login succeeds.
- `views/login.py` renders a centered card with the Skechers logo (`assets/skechers_logo.png`,
  base64-embedded) and a Supabase Auth email/password form. On success, stores the session
  dict (`user_id`, `email`, `access_token`, `role`, `display_name`) in
  `st.session_state["user"]`.

### Theme system
- `st.session_state.theme` defaults to `"dark"`. No UI toggle currently exists for switching
  themes — it's read by `app.py`, `components/charts.py`, `components/chatbot.py`, and
  `views/documentation.py` to pick CSS variants.
- `app.py` injects one of two large inline `<style>` blocks (`_DARK_CSS` / `_LIGHT_CSS`)
  covering: Inter font, app/sidebar backgrounds, metric cards, tab styling, post cards,
  brand header gradient, buttons, and a mobile `@media (max-width: 768px)` block (2-column
  KPI grids, horizontal-scroll tabs, smaller section headers).
- The light theme additionally overrides many hardcoded dark inline styles (`rgba(255,255,255,…)`)
  used throughout the custom HTML cards in views — this is fragile (string-matching CSS
  selectors) but functional.
- A small inline `<script>` block fixes the mobile viewport meta tag.

### Page routing (`app.py`)
`render_sidebar()` returns `(platform, period_label, days, start_date, end_date)`. Routing:
- `"Documentation"` → `render_documentation()`
- `"Facebook"` → `render_facebook_dashboard(...)` + background prefetch of IG/Boost
- `"Instagram"` → `render_instagram_dashboard(...)` + background prefetch of FB/Boost
- `"Google Analytics"` → fetches `fetch_all_ga4_data(start, end)` directly (not via `db.py`,
  no Supabase caching for GA4) → `render_analytics_tab(...)`
- `"Boost"` (else branch) → computes previous-period dates for delta comparisons, uses
  `@st.cache_data(ttl=900)` wrappers around `db.get_boost_insights`, `db.get_fb_demographics`,
  `db.get_adset_ad_insights`, shows `skeleton_boost_html()` while loading, then
  `render_boost_tab(...)` + background prefetch of FB/IG
- `render_chatbot()` is called unconditionally at the very end of `app.py` (it no-ops
  internally if the chat panel isn't open)

---

## 5. Sidebar (`components/sidebar.py`)

Order of elements (top to bottom):
1. Platform selector (Facebook / Instagram / Boost / Google Analytics / Documentation)
2. Date range controls — rolling presets (`PERIOD_DAYS`) + calendar presets
   (`CALENDAR_PERIODS`: Today, Yesterday, This Week, Last Week, This Month, Last Month,
   This Quarter, Last Quarter)
3. **🔄 Refresh Data** button — calls `db.delete_period()` for the current cache key,
   `st.cache_data.clear()`, `log_refresh()`, then `st.rerun()`
4. **💬 Assistant IA** toggle button (placed immediately after Refresh Data) — flips
   `st.session_state.chat_open`; label becomes "✕ Fermer l'assistant" when open
5. **🗑️ Effacer la conversation** — only shown when chat is open and history is non-empty;
   clears `st.session_state.chat_history`
6. Theme init (`st.session_state.theme = "dark"` if unset)
7. Admin-only: Supabase health indicator (`check_api_health()` via `_get_health()`),
   "Cache permanent • Supabase" caption
8. Admin-only: "Connecté : {display_name|email}" caption
9. **🚪 Se déconnecter** — `del st.session_state["user"]` + `st.rerun()`

---

## 6. Credentials & Environment Variables

| Variable | Purpose | Where used |
|----------|---------|------------|
| `SKECHERS_TOKEN` | Meta Graph API long-lived Page Access Token (organic) | `config.py` → `ACCESS_TOKEN` |
| `SKECHERS_ADS_TOKEN` | Meta User Access Token with `ads_read` scope (Boost tab) | `config.py` → `ADS_ACCESS_TOKEN` |
| `SUPABASE_URL` | Supabase project REST endpoint | `db.py`, `auth.py` |
| `SUPABASE_KEY` | Supabase anon/service key | `db.py`, `auth.py` |
| `SUPABASE_DB_URL` | Postgres connection string (one-time setup only) | `db_setup.py` |
| `GROQ_API_KEY` | Groq API key for chatbot LLM | `components/chatbot.py` |
| `GEMINI_API_KEY` | Legacy constant from the original chatbot provider; no longer used by `components/chatbot.py` (which uses `GROQ_API_KEY`) | `config.py` |

**Note**: `ACCESS_TOKEN` and `ADS_ACCESS_TOKEN` currently have live Meta tokens hardcoded as
fallback values in `config.py` (lines ~14–24), used only if the env vars are unset.

### Meta Asset IDs (hardcoded in `config.py`)
- **Facebook Page ID:** `707444622669651`
- **Instagram User ID:** `17841408456074839`
- **Ad Account:** `act_765947885726761` (blocklisted for organic endpoints; Boost tab's single
  authorised source)
- **GA4 Property ID:** `313002599`

### `.gitignore` status
Currently ignores: `.env`, `__pycache__/`, `*.pyc`, `*.pyo`, `.streamlit/secrets.toml`,
`scratch/`, `ga4_token.json`, `oauth_client.json`.

---

## 7. API Details

### 7.1 Meta Graph API (Organic — Facebook & Instagram)
- **Version:** `GRAPH_API_VERSION = "v19.0"` in `config.py`, though `api/instagram.py` calls
  use v22+ patterns (`metric_type`, `views` replacing `impressions`).
- **Base URL:** `https://graph.facebook.com/{GRAPH_API_VERSION}/`
- **HTTP client:** `api/base.py:_get()` — exponential backoff, 3 retries, 30s timeout
- **Block guard:** `_assert_not_blocked()` raises `ValueError` if the ad account ID appears
  in any endpoint URL, enforcing the organic-only constraint

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

### 7.2 Meta Marketing API (Boost tab)
- **Token:** `ADS_ACCESS_TOKEN` (separate User token, requires `ads_read`)
- **HTTP client:** `api/boost.py:_get_ads()` — bypasses `_assert_not_blocked()` intentionally
- **Ad Account:** `act_765947885726761`
- **Campaign identification:** Filters by `SKECHERS_CAMPAIGN_KEYWORDS` =
  `["707444622669651", "SKX ", "Skechers"]` — must match campaign name. Update if agency
  changes naming convention.

#### Skechers campaign ID resolution & caching (3-tier)
`api/boost.py:_get_skechers_ids()`:
1. **In-memory** (`_MEM_IDS` / `_MEM_IDS_AT`) — valid for 24h, process lifetime
2. **Supabase** (`metric_cache` row, `metric_key="skechers_campaign_ids"`) — 24h TTL via
   `_supabase_load_ids()` / `_supabase_save_ids()`
3. **Live scan** — paginates `/ads` filtering on `creative.object_story_spec.page_id`,
   saves result to tiers 1+2. On scan failure, falls back to stale Supabase IDs if available
   (intentional — restored at user request after a brief removal).

This avoids re-scanning all ads on every refresh (previously caused Marketing API CPU-time
rate limiting — error 80004 / subcode 2446079).

Campaign data is fetched at 3 levels:
- Account-level: deduplicated reach only (cannot sum per-campaign reach)
- Campaign-level: spend, impressions, clicks, CTR, CPC, conversions, ROAS
- Adset-level + Ad-level: detailed breakdown for the Ads Manager export tab

**Conversion objectives** tracked: `CONVERSIONS`, `OUTCOME_SALES`

### 7.3 Google Analytics 4
- **Client:** `google.analytics.data_v1beta.BetaAnalyticsDataClient` (service account,
  `google.oauth2.service_account.Credentials` — not OAuth)
- **Auth:** Service account JSON from `ga4_token.json` (local) or
  `st.secrets["ga4"]["token_json"]` (Streamlit Cloud)
- **Property ID:** `313002599`
- **Note:** Streamlit Cloud TOML may deliver `\n` as literal `\\n` in `private_key` —
  `api/ga4.py` normalises this.
- ⚠️ GA4 data is **not** routed through `db.py`/Supabase — `app.py` calls
  `fetch_all_ga4_data()` directly on every page load for the GA4 tab (no persistent cache).

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

## 8. Known API Limitations & Workarounds

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

### Boost (Meta Marketing API)
| Situation | Explanation |
|---|---|
| Delivery status = "—" | Campaign archived/deleted — API doesn't return inactive campaigns by default |
| End = "—" | Adset has no planned end date (runs until paused manually) |
| Cost per add-to-cart/checkout = 0 | Meta doesn't always return these at ad level — dashboard falls back to `spend ÷ count` |
| Objective = "—" on old dates | Archived campaigns aren't in the default API list |
| Budget = 0 | Adset uses parent campaign's budget |
| Marketing API CPU-time rate limit (80004 / 2446079) | Caused by repeated full `/ads` pagination scans — fixed via 3-tier ID caching (§7.2). If it recurs, check `scratch/check_rate_limit.py` and wait for `estimated_time_to_regain_access` |

---

## 9. Components

### `components/charts.py`
- `CHART_LAYOUT` — static dark Plotly layout dict (legacy, prefer `get_chart_layout()`)
- `get_chart_layout()` — theme-aware Plotly layout (reads `st.session_state.theme`)
- `series_to_df(series, value_col)` — converts `[{"date":..., "value":...}]` → sorted DataFrame
- `safe_sum(series)` / `safe_last(series)` — null-safe aggregation helpers
- `render_top3_podium(posts, sort_key, title, view_label, metrics)` — renders the 3-card
  "🏆 Top Content" podium (gold/silver/bronze styling, thumbnail, caption, metrics grid,
  link to post). Used by Facebook and Instagram Top Content tabs and Boost Top-3 Campaigns.

### `components/skeleton.py`
Shimmer loading-skeleton HTML (CSS `@keyframes _skel_shimmer`), builders:
- `skeleton_dashboard_html(n_kpis=5)` — generic tab skeleton
- `skeleton_boost_html()` — Boost-specific skeleton (used in `app.py` while Boost data loads)
- `skeleton_charts_html(n_charts, n_cards)`
- `render_skeleton_boost()` — convenience wrapper returning an `st.empty()` placeholder

---

## 10. Authentication

`auth.py` wraps Supabase Auth (`/auth/v1/token?grant_type=password`).
`auth.login(email, password)` returns
`{user_id, email, access_token, role, display_name}` stored in `st.session_state["user"]`.

- **admin** role: sees Supabase health indicator + "Connecté" label in sidebar
- **viewer** role: same dashboard, no admin widgets
- Logout: `del st.session_state["user"]` + `st.rerun()`

### Table: `profiles`
| Column | Notes |
|--------|-------|
| `user_id` | FK to Supabase `auth.users` |
| `role` | `"admin"` or `"viewer"` |
| `display_name` | Shown in sidebar |

---

## 11. Supabase Schema

### Table: `metric_cache`
| Column | Type | Notes |
|--------|------|-------|
| `id` | int (PK) | Auto-increment |
| `metric_key` | text | e.g. `"ig_profile"`, `"fb_audience"`, `"skechers_campaign_ids"` |
| `period_start` | text | ISO date, `"rolling"`, or `"static"` (for the campaign-ID cache row) |
| `period_end` | text | ISO date, `"last_30d"`, or `"static"` |
| `data` | jsonb | Raw API result as JSON |
| `fetched_at` | timestamptz | When the row was written |

Unique constraint on `(metric_key, period_start, period_end)`.
`db.save()` does POST then PATCH on 409. Schema created once via `db_setup.py`.

### Metric keys
- `ig_profile`, `ig_engagement`, `ig_posts`, `ig_post_totals`
- `fb_audience`, `fb_engagement`, `fb_visibility`, `fb_demographics`, `fb_posts`,
  `fb_post_totals`, `fb_conversations`, `fb_messaging`
- `boost_insights`, `boost_adset_ad`, `skechers_campaign_ids`

### Cache-poisoning guards (`db.py`)
`get_boost_insights()` and `get_adset_ad_insights()` treat a cached entry with **zero
campaigns/spend/ads/adsets** as a cache miss and re-fetch — prevents a rate-limit failure
from being permanently cached as "all zeros".

### In-memory invalidation registry (`db._INVALIDATED`)
Refresh button calls `db.delete_period(start, end)` which does a hard DELETE.
Per-platform soft invalidation via `db.invalidate(platform, start, end)` marks keys in
`_INVALIDATED` dict; `db.load()` skips rows fetched before the invalidation timestamp.

---

## 12. Chatbot (`components/chatbot.py`)

### LLM Stack
- **Provider:** Groq (not Gemini — `config.py` still has a dead `GEMINI_API_KEY` constant)
- **Primary model:** `llama-3.3-70b-versatile`
- **Fallback model:** `llama-3.1-8b-instant` (auto-switches on 429 / rate-limit error)
- **Temperature:** 0.7 | **Max tokens:** 1024

### Location & wiring
- The toggle button ("💬 Assistant IA" / "✕ Fermer l'assistant") and the
  "🗑️ Effacer la conversation" button live in `components/sidebar.py`, right after
  "🔄 Refresh Data" (see §5).
- The actual floating chat panel is rendered by `components/chatbot.py:render_chatbot()`,
  called unconditionally at the end of `app.py`. It no-ops if `st.session_state.chat_open`
  is `False`.
- `components/chatbot.py` lines ~494–665 are inside an `if False:` block (an old chat UI
  implementation that is never executed).

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
Documents known API limitations (privacy-filtered likes, reach window limits, deprecated
metrics).

### Documented in-app
`views/documentation.py` has a "🤖 Assistant IA" section (feature table + limitations
expander) describing this to end users in French.

---

## 13. Documentation tab (`views/documentation.py`)

In-app "📖 Guide du Dashboard" — explains every KPI, its calculation, and its API endpoint,
organized by platform:
- **Facebook**: Vue d'ensemble, Audience, Visibilité, Engagement, Top Contenu, Communauté
- **Instagram**: Vue d'ensemble, Visibilité, Engagement
- **Boost**: Global, Conversion, Par Objectif, Top #3 Campagnes, Tableau Ads, Démographie & Géo
- **Google Analytics 4**: Vue d'ensemble, E-commerce, Événements, Audience
- **🤖 Assistant IA**: feature table + limitations expander
- Shared expanders: "⚠️ Limitations & Données Indisponibles", "📚 Glossaire", and
  (admin-only) "🔄 Fréquence de mise à jour"

The Endpoint column in KPI tables is hidden via CSS for non-admin (`viewer`) users.

---

## 14. Background Prefetch

`app.py` spawns daemon threads on load via `_start_prefetch(platform, days, start, end)`:
- `_prefetch_facebook` — calls all 7 Facebook db getters
- `_prefetch_instagram` — calls all 4 Instagram db getters
- `_prefetch_boost` — calls `db.get_boost_insights` + `db.get_fb_demographics`

Whichever platform tab is **not** currently active gets prefetched, so switching tabs is
instant (data already in Supabase). Threads are fire-and-forget; errors are silently
swallowed.

Separately, `fetcher.py` runs via GitHub Actions (`.github/workflows/fetch.yml`, every 6h)
and pre-warms Supabase for every sidebar period preset (rolling + calendar), independent of
user activity. Both this and the in-app prefetch threads populate the same `metric_cache`
table via the same cache keys.

---

## 15. Key Calculations

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

## 16. Error Handling

| HTTP error | UI response |
|-----------|-------------|
| 401 Unauthorized | `st.error("Token expired")` |
| 403 Forbidden | `st.warning(...)` + show available data |
| 429 Rate Limited | Exponential backoff (3 retries) + `st.info("Rate limited — retrying...")` |
| Network error | Use cached Supabase data + `st.warning("Using cached data")` |
| Empty response | `st.info("No data available for this period")` |

---

## 17. Running the App

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

## 18. Architecture Decisions Log

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
| 3-tier campaign ID caching (memory → Supabase 24h → live scan) | Live `/ads` pagination scans on every refresh caused Marketing API CPU-time rate limiting (80004/2446079) |
| `CLAUDE.md` kept short, `PROJECT_CONTEXT.md` is the single source of truth | Avoids two large docs drifting out of sync and bloating AI context windows |
