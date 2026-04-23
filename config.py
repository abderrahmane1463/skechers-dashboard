"""
config.py — Footland Dashboard Configuration & Constants
Strict Constraint: No ad account or paid benchmark data is ever used.
"""

import os

# ─── Meta Graph API ───────────────────────────────────────────────────────────
GRAPH_API_VERSION = "v19.0"
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Access token — can be overridden via environment variable FOOTLAND_TOKEN
ACCESS_TOKEN = os.environ.get(
    "FOOTLAND_TOKEN",
    "EAAXdQDmFoT8BRYOvKeaEYk9az3iqKbDnlHks3hT5WZBKmMT8cXjO7D03YX3QOelqZCxHOjKmCbZBLx6rMi7vOrcRLMbYofDwfBbPd7TNOlE2ZCbnWPkEOQ9QZAIbzpNuqpFRP9OvX3LuZC4M1lZAuDszoCxwRkGfKmZBvdeZBr1fZCx41Tv9t7AZAsXhutOo7pQfPzrPSwUpZCy11mn70VINXyXwOvIZD"
)

# ─── Asset IDs ─────────────────────────────────────────────────────────────────
FACEBOOK_PAGE_ID = "144124252311741"
INSTAGRAM_USER_ID = "17841403000855491"

# ─── Blocklisted (Paid) Assets — NEVER query these ────────────────────────────
BLOCKED_AD_ACCOUNTS = ["act_765947885726761"]

# ─── Date Period Mapping ───────────────────────────────────────────────────────
PERIOD_DAYS = {
    "Last 7 Days": 7,
    "Last 30 Days": 30,
    "Last 90 Days": 90,
}

# ─── API Settings ──────────────────────────────────────────────────────────────
REQUEST_TIMEOUT = 30        # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0         # exponential backoff multiplier
CACHE_TTL_SECONDS = 900     # 15 minutes

# ─── Facebook Insight Metrics ──────────────────────────────────────────────────
FB_AUDIENCE_METRICS = [
    "page_fans",
    "page_fan_adds",
    "page_fan_removes",
]

FB_ENGAGEMENT_METRICS = [
    "page_post_engagements",
    "page_actions_post_reactions_total",
]

FB_VISIBILITY_METRICS = [
    "page_impressions",
    "page_impressions_unique",
    "page_views_total",
]

# Fields to request for Facebook posts
FB_POST_FIELDS = "id,message,story,created_time,full_picture,shares,comments.summary(true),reactions.summary(true)"

# ─── Instagram Insight Metrics ─────────────────────────────────────────────────
IG_PROFILE_METRICS = [
    "impressions",
    "reach",
    "profile_views",
    "follower_count",
]

IG_ENGAGEMENT_METRICS = [
    "likes",
    "comments",
    "shares",
    "saves",
]

# Fields for Instagram media
IG_MEDIA_FIELDS = (
    "id,caption,media_type,thumbnail_url,media_url,"
    "timestamp,like_count,comments_count"
)

# ─── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "AI_CONTEXT_LOG.md")
