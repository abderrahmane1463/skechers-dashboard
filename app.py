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
from views.boost import render_boost_tab, empty_boost_data
from api.boost import fetch_boost_insights

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

/* ── Premium Dark Theme ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: #0a0a0a !important;
    color: #ffffff !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #111111 !important;
    border-right: 1px solid #222222 !important;
}
[data-testid="stSidebar"] * { color: #eeeeee !important; }

/* ── Main content area ── */
[data-testid="stMainBlockContainer"] { background: transparent; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #161616;
    border: 1px solid #262626;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    border-color: #E8420A;
}
[data-testid="metric-container"] label,
[data-testid="metric-container"] [data-testid="stMetricLabel"] { color: #a1a1aa !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #ffffff !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #161616;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 20px;
    font-weight: 500;
    color: #a1a1aa !important;
}
.stTabs [aria-selected="true"] {
    background: #262626 !important;
    color: #E8420A !important;
    border: 1px solid #E8420A !important;
}

/* ── Post card ── */
.post-card {
    background: #161616;
    border: 1px solid #262626;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 12px;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.post-card:hover {
    border-color: #E8420A;
    box-shadow: 0 4px 20px rgba(232,66,10,0.15);
}

/* ── Brand header ── */
.brand-header {
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(90deg, #E8420A, #FF6B35, #C1320A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}
.brand-sub { font-size: 12px; color: #71717a; margin-bottom: 24px; }

/* ── Section header ── */
.section-header {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin: 16px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid rgba(232,66,10,0.5);
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(90deg, #E8420A, #C1320A) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #FF6B35, #E8420A) !important;
    box-shadow: 0 0 15px rgba(232,66,10,0.4);
}

/* ── Divider ── */
hr { border-color: #e4e4e7 !important; }

/* ── Radio accent ── */
[data-testid="stRadio"] label[data-checked="true"] { color: #E8420A !important; }

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111111;
    border: 1px solid #262626 !important;
    border-radius: 12px !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { background: #111111; border-radius: 12px; }

/* ── General text ── */
p, span, li, label, h1, h2, h3 { color: #ffffff !important; }
small { color: #71717a !important; }
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
    _icon = {"Facebook": "🔵 Facebook", "Instagram": "📸 Instagram", "Boost": "🚀 Boost"}[platform]
    st.markdown(f"## {_icon} — {period_label}")
with col_t2:
    st.caption(f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")

# ─── Dashboard routing ────────────────────────────────────────────────────────
if platform == "Facebook":
    render_facebook_dashboard(period_label, days, start_date, end_date, log_refresh)
elif platform == "Instagram":
    render_instagram_dashboard(period_label, days, start_date, end_date, log_refresh)
else:
    # ── Boost (paid campaigns) ────────────────────────────────────────────────
    try:
        boost_data = fetch_boost_insights(days, start_date, end_date)
    except Exception as e:
        print(f"DEBUG boost: fetch failed, using placeholder: {e}")
        boost_data = empty_boost_data()
    render_boost_tab(boost_data)
