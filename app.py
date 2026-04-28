"""
app.py — Footland Organic Social Analytics Dashboard
Entry point. Organic data only. No ad account data.
"""

import streamlit as st
from datetime import datetime, timezone

from config import LOG_FILE_PATH
from components.sidebar import render_sidebar
from views.facebook import render_facebook_dashboard
from views.instagram import render_instagram_dashboard

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Footland Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark warm background matching Footland brand */
.stApp { background: linear-gradient(135deg, #1a0a00, #2d1200, #1a0a00); }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1c0d00 0%, #2a1500 100%);
    border-right: 1px solid rgba(232,66,10,0.15);
}

/* Metric cards */
[data-testid="metric-container"] {
    background: rgba(232,66,10,0.07);
    border: 1px solid rgba(232,66,10,0.2);
    border-radius: 16px;
    padding: 20px;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(232,66,10,0.08);
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #E8420A, #C1320A) !important;
    color: white !important;
}

/* Post card */
.post-card {
    background: rgba(232,66,10,0.06);
    border: 1px solid rgba(232,66,10,0.15);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.post-card:hover { border-color: rgba(232,66,10,0.5); }

/* Brand header */
.brand-header {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(90deg, #E8420A, #FF6B35, #C1320A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.brand-sub { font-size: 12px; color: rgba(255,255,255,0.4); margin-bottom: 24px; }

/* Section header */
.section-header {
    font-size: 18px;
    font-weight: 600;
    color: rgba(255,255,255,0.9);
    margin: 16px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(232,66,10,0.2);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #E8420A, #C1320A) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #FF6B35, #E8420A) !important;
    transform: translateY(-1px);
}

/* Divider */
hr { border-color: rgba(232,66,10,0.2) !important; }

/* Selectbox / Radio accent */
[data-testid="stRadio"] label[data-checked="true"] { color: #FF6B35 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Logging Helper ───────────────────────────────────────────────────────────
def log_refresh(platform: str, period: str, status: str, notes: str = ""):
    """Appends a refresh entry to AI_CONTEXT_LOG.md."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    entry = (
        f"\n### [{timestamp} UTC] — Data Refresh\n"
        f"- **Platform:** {platform}\n"
        f"- **Period:** {period}\n"
        f"- **Status:** {status}\n"
    )
    if notes:
        entry += f"- **Notes:** {notes}\n"
    entry += "---\n"
    try:
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass


# ─── Sidebar ─────────────────────────────────────────────────────────────────
platform, period_label, days, start_date, end_date = render_sidebar(log_refresh)

# ─── Page Title ───────────────────────────────────────────────────────────────
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown(f"## {'🔵 Facebook' if platform == 'Facebook' else '📸 Instagram'} — {period_label}")
with col_t2:
    st.caption(f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")

# ─── Dashboard routing ────────────────────────────────────────────────────────
if platform == "Facebook":
    render_facebook_dashboard(period_label, days, start_date, end_date, log_refresh)
else:
    render_instagram_dashboard(period_label, days, start_date, end_date, log_refresh)
