"""
config.py — Skechers Dashboard Configuration & Constants
Strict Constraint: No ad account or paid benchmark data is ever used.
"""

import os

# ─── Meta Graph API ───────────────────────────────────────────────────────────
GRAPH_API_VERSION = "v19.0"
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

# Page Access Token — organic data (FB posts, insights, IG)
# Can be overridden via environment variable SKECHERS_TOKEN
ACCESS_TOKEN = os.environ.get(
    "SKECHERS_TOKEN",
    "EAAVwSFsZAbnMBRlNPX2M380gVE6PpW67x5KWYGxVLfLTraVUSNe3ZBJFmWphH49KdJQtE4OBXnu1CBZAAyyyeNUnGC3P5yzL15vcLwpOoSMrNLjQA9mXZBFRVYywPGb01ospdbPGFpsF9UcrazGyoS0ECWsZAZAfNBLJbL8A06khS7r7mEoVOQ5DubSeitxfYb1j2apDDfipUwf52OZBjFMrriV"
)

# User Access Token — Marketing API only (Boost tab)
# Can be overridden via environment variable SKECHERS_ADS_TOKEN
ADS_ACCESS_TOKEN = os.environ.get(
    "SKECHERS_ADS_TOKEN",
    "EAAXdQDmFoT8BRkOmkmrG15MzkurTX3E57EPGjU5BCzOLo8MAZAgyxovCIlpzem5VvZCaZA0Xo7caUvDNt1i8k6LHRJHvZBEZCXZCdCoviXlv00S1m9EzwLp2EcvvWZCJTYC5JrqYmsq7bAs3p8WIJqp1NtazvvXryGN0gi9H9alxbX88nuZCvQcnS5IShgrTZAimgXbvrdpVSL0Vd8f6U"
)

# ─── Asset IDs ─────────────────────────────────────────────────────────────────
FACEBOOK_PAGE_ID = "707444622669651"
INSTAGRAM_USER_ID = "17841408456074839"

# ─── Boost — Skechers campaign identification keywords ────────────────────────
# The ad account (act_765947885726761) manages multiple clients.
# A campaign is considered Skechers if its name contains ANY of these strings.
# Update this list when the agency changes their naming convention.
SKECHERS_CAMPAIGN_KEYWORDS = [
    "707444622669651",  # page ID  — post-boost campaigns
    "SKX ",
    "Skechers",
]

# ─── Blocklisted (Paid) Assets — NEVER query these ────────────────────────────
BLOCKED_AD_ACCOUNTS = ["act_765947885726761"]

# ─── Date Period Mapping ───────────────────────────────────────────────────────
# Simple rolling windows (days back from today). Calendar-based periods
# (Today, Yesterday, This Week, etc.) are computed dynamically in sidebar.py.
PERIOD_DAYS = {
    "Last 7 Days":  7,
    "Last 14 Days": 14,
    "Last 30 Days": 30,
    "Last 60 Days": 60,
    "Last 90 Days": 90,
}

# Calendar-based presets resolved to (start, end) in sidebar.py
CALENDAR_PERIODS = [
    "Today",
    "Yesterday",
    "This Week",
    "Last Week",
    "This Month",
    "Last Month",
    "This Quarter",
    "Last Quarter",
]

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
    "page_media_view",               # replaces page_posts_impressions (removed 2026-06-15)
    "page_total_media_view_unique",  # replaces page_impressions_unique (removed 2026-06-15)
    "page_views_total",
]

# Fields to request for Facebook posts
FB_POST_FIELDS = "id,message,story,created_time,full_picture,shares,comments.summary(true).filter(stream),reactions.summary(true),attachments{type,media_type}"

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
    "id,caption,media_type,thumbnail_url,media_url,permalink,"
    "timestamp,like_count,comments_count"
)

# ─── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "AI_CONTEXT_LOG.md")
