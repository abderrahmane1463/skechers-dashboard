"""
app.py — Footland Organic Social Analytics Dashboard
Streamlit frontend. Organic data only. No ad account data.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone, timedelta
from config import PERIOD_DAYS, LOG_FILE_PATH
import api_client as api

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


# ─── Cached Data Fetchers ─────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def get_health():
    return api.check_api_health()

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_audience(days, start=None, end=None):
    return api.fetch_fb_audience(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_engagement(days, start=None, end=None):
    return api.fetch_fb_engagement(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_visibility(days, start=None, end=None):
    return api.fetch_fb_visibility(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_posts(days, start=None, end=None):
    return api.fetch_fb_posts(days, start, end, 100)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_conversations():
    return api.fetch_fb_conversations(25)

@st.cache_data(ttl=3600, show_spinner=False)
def get_fb_demographics():
    return api.fetch_fb_demographics()

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_profile(days, start=None, end=None):
    return api.fetch_ig_profile(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_engagement(days, start=None, end=None):
    return api.fetch_ig_engagement(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_posts(days, start=None, end=None):
    return api.fetch_ig_posts(days, start, end, 100)


# ─── Chart Helpers ────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.7)", family="Inter"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", showline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", showline=False),
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

def series_to_df(series: list, value_col="value") -> pd.DataFrame:
    if not series:
        return pd.DataFrame(columns=["date", value_col])
    df = pd.DataFrame(series)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df


def safe_sum(series: list) -> int:
    return sum(v.get("value", 0) for v in (series or []))


def safe_last(series: list) -> int:
    return series[-1].get("value", 0) if series else 0


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    # Footland Logo
    import base64, pathlib
    _logo_path = pathlib.Path("assets/footland_logo.png")
    if _logo_path.exists():
        _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
        st.markdown(
            f'<div style="background:#fff;border-radius:12px;padding:12px 16px;'
            f'margin-bottom:8px;text-align:center;">'
            f'<img src="data:image/png;base64,{_logo_b64}" style="max-width:160px;width:100%;"/>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="brand-header">⚽ Footland</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Organic Analytics Dashboard</div>', unsafe_allow_html=True)

    platform = st.radio("Platform", ["🔵 Facebook", "📸 Instagram"], label_visibility="collapsed")
    platform = "Facebook" if "Facebook" in platform else "Instagram"

    period_options = list(PERIOD_DAYS.keys()) + ["Custom Range"]
    period_label = st.selectbox("Date Range", period_options, index=1)
    
    start_date, end_date = None, None
    if period_label == "Custom Range":
        today = datetime.now(timezone.utc).date()
        c1, c2 = st.columns(2)
        start_val = c1.date_input("Start", today - timedelta(days=30))
        end_val = c2.date_input("End", today)
        start_date, end_date = str(start_val), str(end_val)
        days = (end_val - start_val).days
    else:
        days = PERIOD_DAYS[period_label]

    if st.button("🔄 Refresh Data", width="stretch"):
        st.cache_data.clear()
        log_refresh(platform, period_label, "🔄 Manual Refresh Triggered")
        st.rerun()

    st.divider()

    # API Health
    health = get_health()
    if health.get("status") == "ok":
        st.success(f"✅ API Connected\n\n{health.get('name', '')}")
    else:
        st.error(f"❌ API Error\n\n{health.get('message', 'Unknown error')}")

    st.caption(f"Cache TTL: 15 min • Graph API v19.0")


# ─── Page Title ───────────────────────────────────────────────────────────────
col_t1, col_t2 = st.columns([3, 1])
with col_t1:
    st.markdown(f"## {'🔵 Facebook' if platform == 'Facebook' else '📸 Instagram'} — {period_label}")
with col_t2:
    st.caption(f"Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC")


# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if platform == "Facebook":
    with st.spinner("Loading Facebook data…"):
        # Pass custom dates if available
        aud = get_fb_audience(days, start_date, end_date)
        eng = get_fb_engagement(days, start_date, end_date)
        vis = get_fb_visibility(days, start_date, end_date)
        posts = get_fb_posts(days, start_date, end_date)
        convos = get_fb_conversations()

    # ── KPI Row ──────────────────────────────────────────────────────────────
    total_fans = aud.get("fans_total") or 0
    total_adds = safe_sum(aud.get("fans_adds", []))
    total_removes = safe_sum(aud.get("fans_removes", []))
    total_reach = vis.get("period_reach", 0) or safe_sum(vis.get("reach", []))
    total_impressions = safe_sum(vis.get("impressions", []))
    total_views = safe_sum(vis.get("page_views", []))

    # Aggregate interactions from posts to exclude clicks (page_post_engagements includes clicks)
    total_reacs = sum(p.get("reactions", 0) for p in posts)
    total_comms = sum(p.get("comments", 0) for p in posts)
    total_shars = sum(p.get("shares", 0) for p in posts)
    total_engagements = total_reacs + total_comms + total_shars

    eng_rate = round(total_engagements / total_reach * 100, 2) if total_reach else 0.0

    log_refresh(
        platform, 
        period_label, 
        "✅ Data Loaded", 
        f"Followers: {total_fans}, Posts: {len(posts)}, Reach: {total_reach}"
    )

    # Total interactions (total_reacs, total_comms, total_shars calculated above)

    def _kpi(icon, label, value, color="#ffffff"):
        return (
            f'<div style="background:rgba(255,255,255,0.05);border-radius:12px;'
            f'padding:0.9rem 1rem;text-align:center;">'
            f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);'
            f'margin-bottom:0.25rem;">{icon} {label}</div>'
            f'<div style="font-size:1.35rem;font-weight:800;color:{color};'
            f'white-space:nowrap;">{value}</div>'
            f'</div>'
        )

    kpi_html = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_kpi("👥", "Followers",            f"{total_fans:,}")}
  {_kpi("➕", "Nouveaux followers",   f"+{total_adds:,}", "#4ade80")}
  {_kpi("➖", "Désabonnements",       f"-{total_removes:,}", "#f87171")}
  {_kpi("📊", "Taux d'engagement",   f"{eng_rate}%", "#facc15")}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_kpi("👁️", "Spectateurs",         f"{total_reach:,}")}
  {_kpi("📢", "Impressions",          f"{total_impressions:,}")}
  {_kpi("📝", "Publications",         str(len(posts)))}
  {_kpi("⚡", "Engagement publis.",   f"{total_engagements:,}")}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi("🔥", "Total interactions",   f"{total_engagements:,}", "#FF6B35")}
  {_kpi("❤️", "Réactions",            f"{total_reacs:,}")}
  {_kpi("💬", "Commentaires",         f"{total_comms:,}")}
  {_kpi("🔁", "Partages",             f"{total_shars:,}")}
</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)

    # ── Top Publications Section ─────────────────────────────────────────────
    if posts:
        st.markdown("---")
        st.markdown(
            '<div style="text-align:center; font-size:1.1rem; font-weight:700; '
            'letter-spacing:0.1em; color:rgba(255,255,255,0.6); margin-bottom:1.2rem;">'
            '🏆 TOP PUBLICATIONS PAR VISIBILITÉ</div>',
            unsafe_allow_html=True
        )

        sorted_posts = sorted(posts, key=lambda p: p.get("reach", 0), reverse=True)[:6]
        cols = st.columns(3)
        for idx, post in enumerate(sorted_posts):
            col = cols[idx % 3]
            with col:
                thumbnail = post.get("thumbnail", "")
                text = post.get("text", "")[:100] or "*(No caption)*"
                date = post.get("created_time", "")
                reacs = post.get("reactions", 0)
                comms = post.get("comments", 0)
                shars = post.get("shares", 0)
                total = post.get("total_interactions", 0)
                post_id = post.get("id", "")
                post_url = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "#"

                if thumbnail:
                    st.image(thumbnail, width="stretch")
                else:
                    st.markdown(
                        '<div style="height:160px;background:rgba(255,255,255,0.05);'
                        'border-radius:12px;display:flex;align-items:center;'
                        'justify-content:center;color:rgba(255,255,255,0.3);">📷 No image</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<p style="font-size:0.75rem;color:rgba(255,255,255,0.45);margin:0.3rem 0 0.1rem;">{date}</p>'
                    f'<p style="font-size:0.82rem;color:rgba(255,255,255,0.85);line-height:1.4;margin-bottom:0.5rem;">{text}</p>',
                    unsafe_allow_html=True
                )

                reach_val = post.get('reach', 0)
                st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;margin:0.5rem 0;">
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">👁️ Spectateurs</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{reach_val:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">❤️ Réactions</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{reacs:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">💬 Commentaires</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{comms:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">🔁 Partages</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{shars:,}</div>
  </div>
</div>
<div style="background:rgba(232,66,10,0.15);border-radius:8px;padding:0.5rem 0.6rem;margin-bottom:0.5rem;">
  <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⚡ Total interactions</div>
  <div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>
</div>
<a href="{post_url}" target="_blank"
   style="font-size:0.75rem;color:#6c8ebf;text-decoration:none;">
  🔗 Voir la publication
</a><br><br>
""", unsafe_allow_html=True)

    # ── Top Publications by Engagement ──────────────────────────────────────
    if posts:
        st.markdown("---")
        st.markdown(
            '<div style="text-align:center; font-size:1.1rem; font-weight:700; '
            'letter-spacing:0.1em; color:rgba(255,255,255,0.6); margin-bottom:1.2rem;">'
            '⚡ TOP PUBLICATIONS PAR ENGAGEMENT</div>',
            unsafe_allow_html=True
        )

        eng_sorted = sorted(posts, key=lambda p: p.get("total_interactions", 0), reverse=True)[:6]
        eng_cols = st.columns(3)
        for idx, post in enumerate(eng_sorted):
            col = eng_cols[idx % 3]
            with col:
                thumbnail = post.get("thumbnail", "")
                text      = post.get("text", "")[:100] or "*(No caption)*"
                date      = post.get("created_time", "")
                reacs     = post.get("reactions", 0)
                comms     = post.get("comments", 0)
                shars     = post.get("shares", 0)
                total     = post.get("total_interactions", 0)
                reach_val = post.get("reach", 0)
                post_id   = post.get("id", "")
                post_url  = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "#"

                if thumbnail:
                    st.image(thumbnail, width="stretch")
                else:
                    st.markdown(
                        '<div style="height:160px;background:rgba(255,255,255,0.05);'
                        'border-radius:12px;display:flex;align-items:center;'
                        'justify-content:center;color:rgba(255,255,255,0.3);">📷 No image</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<p style="font-size:0.75rem;color:rgba(255,255,255,0.45);margin:0.3rem 0 0.1rem;">{date}</p>'
                    f'<p style="font-size:0.82rem;color:rgba(255,255,255,0.85);line-height:1.4;margin-bottom:0.5rem;">{text}</p>',
                    unsafe_allow_html=True
                )

                st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;margin:0.5rem 0;">
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">👁️ Spectateurs</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{reach_val:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">❤️ Réactions</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{reacs:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">💬 Commentaires</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{comms:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">🔁 Partages</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{shars:,}</div>
  </div>
</div>
<div style="background:rgba(232,66,10,0.15);border-radius:8px;padding:0.5rem 0.6rem;margin-bottom:0.5rem;">
  <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⚡ Total interactions</div>
  <div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>
</div>
<a href="{post_url}" target="_blank"
   style="font-size:0.75rem;color:#FF6B35;text-decoration:none;">
  🔗 Voir la publication
</a><br><br>
""", unsafe_allow_html=True)

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Audience", "💬 Engagement", "📡 Visibility", "🏆 Top Content", "🤝 Community"
    ])

    # ── TAB 1: Audience ───────────────────────────────────────────────────────
    with tab1:
        # ── Section Header ──────────────────────────────────────────────────
        hcol1, hcol2 = st.columns([1, 1])
        with hcol1:
            st.markdown(
                '<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
                'color:#fff;margin:0;">AUDIENCE</p>',
                unsafe_allow_html=True
            )
        with hcol2:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:flex-end;gap:8px;">'
                '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#1877F2">'
                '<path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>'
                '</svg>'
                '<span style="font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.6);">FACEBOOK PERFORMANCE</span>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        adds_df = series_to_df(aud.get("fans_adds", []))
        rem_df  = series_to_df(aud.get("fans_removes", []))

        if not adds_df.empty:
            merged = adds_df.rename(columns={"value": "adds"})
            if not rem_df.empty:
                merged = merged.merge(rem_df.rename(columns={"value": "removes"}), on="date", how="outer").fillna(0)
            else:
                merged["removes"] = 0
            merged["net"] = merged["adds"] - merged["removes"]

            # ── Trend calculations (first half vs second half) ───────────────
            mid = len(merged) // 2
            def _pct_change(series, mid):
                first  = series.iloc[:mid].sum() if mid > 0 else 0
                second = series.iloc[mid:].sum()
                if first == 0:
                    return 0.0
                return round((second - first) / first * 100, 1)

            pct_removes = _pct_change(merged["removes"], mid)
            pct_net     = _pct_change(merged["net"], mid)

            net_follows     = int(merged["net"].sum())
            total_unfollows = int(merged["removes"].sum())

            def _trend_html(pct):
                arrow = "▲" if pct >= 0 else "▼"
                color = "#4ade80" if pct >= 0 else "#f87171"
                return f'<span style="color:{color};font-size:0.8rem;">{arrow} {abs(pct)}%</span>'

            # ── Main layout: chart + sidebar ────────────────────────────────
            chart_col, sidebar_col = st.columns([3, 1])

            with chart_col:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=merged["date"],
                    y=merged["adds"],
                    name="Follows",
                    line=dict(color="#7EC8E3", width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(126,200,227,0.08)",
                    mode="lines"
                ))
                audience_layout = {
                    **CHART_LAYOUT,
                    "yaxis": dict(
                        gridcolor="rgba(255,255,255,0.06)",
                        showline=False,
                        range=[0, max(merged["adds"].max() * 1.2, 10)]
                    ),
                    "xaxis": dict(
                        gridcolor="rgba(255,255,255,0.06)",
                        showline=False,
                        tickmode="array",
                        tickvals=[merged["date"].iloc[i] for i in range(0, len(merged), max(len(merged)//6, 1))][:7],
                    ),
                    "showlegend": False,
                    "margin": dict(l=0, r=0, t=10, b=30),
                    "height": 280,
                }
                fig.update_layout(**audience_layout)
                st.plotly_chart(fig, width="stretch")

                # Legend
                st.markdown(
                    '<div style="text-align:center;margin-top:-12px;">'
                    '<span style="display:inline-block;width:28px;height:2px;'
                    'background:#7EC8E3;vertical-align:middle;margin-right:6px;"></span>'
                    '<span style="font-size:0.75rem;color:rgba(255,255,255,0.5);">Follows</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

            with sidebar_col:
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.04);border-radius:12px;'
                    f'padding:1.2rem 1rem;display:flex;flex-direction:column;gap:1.2rem;">'

                    f'<div>'
                    f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Unfollows</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:#fff;">{total_unfollows:,}</div>'
                    f'{_trend_html(pct_removes)}'
                    f'</div>'

                    f'<div>'
                    f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Net follows</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:#fff;">{net_follows:,}</div>'
                    f'{_trend_html(pct_net)}'
                    f'</div>'

                    f'<div>'
                    f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Followers (Lifetime)</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:#FF6B35;">{total_fans:,}</div>'
                    f'</div>'

                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No audience data available for this period.")

        # ── Demographics Chart ───────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)

        # Header
        dh1, dh2 = st.columns([1, 1])
        with dh1:
            st.markdown(
                '<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
                'color:#fff;margin:0;">DONNÉES DÉMOGRAPHIQUES</p>'
                f'<p style="font-size:0.85rem;color:rgba(255,255,255,0.45);margin:2px 0 0;">'
                f'Followers (Lifetime): <strong style="color:#FF6B35;">{total_fans:,}</strong></p>',
                unsafe_allow_html=True
            )
        with dh2:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:flex-end;gap:8px;">'
                '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#1877F2">'
                '<path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>'
                '</svg>'
                '<span style="font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.6);">FACEBOOK PERFORMANCE</span>'
                '</div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        demo = get_fb_demographics()
        age_brackets   = demo["age_brackets"]
        men_pcts       = demo["men"]
        women_pcts     = demo["women"]
        total_men_pct  = demo["total_men_pct"]
        total_women_pct = demo["total_women_pct"]

        if any(v > 0 for v in men_pcts + women_pcts):
            fig_demo = go.Figure()
            fig_demo.add_trace(go.Bar(
                name="Men",
                x=age_brackets,
                y=men_pcts,
                marker_color="#7EC8E3",
                text=[f"{v}%" for v in men_pcts],
                textposition="outside",
                textfont=dict(size=11, color="rgba(255,255,255,0.6)"),
            ))
            fig_demo.add_trace(go.Bar(
                name="Women",
                x=age_brackets,
                y=women_pcts,
                marker_color="#1C4E80",
                text=[f"{v}%" for v in women_pcts],
                textposition="outside",
                textfont=dict(size=11, color="rgba(255,255,255,0.6)"),
            ))
            demo_layout = {
                **CHART_LAYOUT,
                "barmode": "group",
                "yaxis": dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    showline=False,
                    ticksuffix="%",
                    range=[0, 35],
                ),
                "xaxis": dict(
                    gridcolor="rgba(255,255,255,0.06)",
                    showline=False,
                ),
                "showlegend": False,
                "margin": dict(l=0, r=0, t=20, b=40),
                "height": 320,
            }
            fig_demo.update_layout(**demo_layout)
            st.plotly_chart(fig_demo, width="stretch")

            # Legend + gender totals
            st.markdown(
                f'<div style="display:flex;justify-content:center;align-items:center;gap:2rem;margin-top:-8px;">'
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="width:24px;height:12px;background:#7EC8E3;border-radius:3px;"></div>'
                f'<span style="font-size:0.8rem;color:rgba(255,255,255,0.7);">Men — <strong>{total_men_pct}%</strong></span>'
                f'</div>'
                f'<div style="display:flex;align-items:center;gap:6px;">'
                f'<div style="width:24px;height:12px;background:#1C4E80;border-radius:3px;"></div>'
                f'<span style="font-size:0.8rem;color:rgba(255,255,255,0.7);">Women — <strong>{total_women_pct}%</strong></span>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="background:rgba(232,66,10,0.08);border:1px solid rgba(232,66,10,0.25);'
                'border-radius:16px;padding:1.5rem 2rem;text-align:center;">'
                '<p style="font-size:1.1rem;font-weight:700;color:#FF6B35;margin:0 0 0.5rem;">📊 Données non disponibles via API</p>'
                '<p style="font-size:0.85rem;color:rgba(255,255,255,0.6);margin:0 0 1rem;">'
                'Meta a supprimé l\'accès aux données démographiques (âge/genre) via l\'API Graph pour les '
                'pages "New Page Experience". Ces données sont uniquement accessibles dans Meta Business Suite.'
                '</p>'
                '<a href="https://business.facebook.com/insights/" target="_blank" '
                'style="display:inline-block;background:linear-gradient(90deg,#E8420A,#C1320A);'
                'color:#fff;text-decoration:none;padding:0.5rem 1.2rem;border-radius:8px;'
                'font-size:0.85rem;font-weight:600;">🔗 Ouvrir Meta Business Suite</a>'
                '</div>',
                unsafe_allow_html=True
            )

        # ── Geographic Demographics ──────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        gh1, gh2 = st.columns([1, 1])
        with gh1:
            st.markdown(
                '<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;color:#fff;margin:0;">'
                'DONN\u00c9ES D\u00c9MOGRAPHIQUES</p>'
                '<p style="font-size:0.8rem;color:rgba(255,255,255,0.4);margin:2px 0 0;">Top villes &amp; pays</p>',
                unsafe_allow_html=True
            )
        with gh2:
            st.markdown(
                '<div style="display:flex;align-items:center;justify-content:flex-end;gap:8px;">'
                '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#1877F2">'
                '<path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 '
                '10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 '
                '2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 '
                '3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/></svg>'
                '<span style="font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.6);">FACEBOOK PERFORMANCE</span>'
                '</div>',
                unsafe_allow_html=True
            )
        st.markdown("<br>", unsafe_allow_html=True)

        gcol1, gcol2 = st.columns(2)
        _geo_card = (
            '<div style="background:rgba(232,66,10,0.08);border:1px solid rgba(232,66,10,0.2);'
            'border-radius:16px;padding:1.5rem;text-align:center;">'
            '<p style="font-size:1rem;font-weight:700;color:#FF6B35;margin:0 0 0.4rem;">{icon} {title}</p>'
            '<p style="font-size:0.78rem;color:rgba(255,255,255,0.5);margin:0 0 1rem;">'
            'Donn\u00e9es non disponibles via API<br>'
            '<span style="font-size:0.7rem;">(Restriction Meta \u2014 New Page Experience)</span></p>'
            '<a href="https://business.facebook.com/insights/" target="_blank" '
            'style="background:linear-gradient(90deg,#E8420A,#C1320A);color:#fff;'
            'text-decoration:none;padding:0.4rem 1rem;border-radius:8px;font-size:0.8rem;font-weight:600;">'
            '\U0001f517 Business Suite</a></div>'
        )
        with gcol1:
            st.markdown(_geo_card.format(icon="\U0001f3d9\ufe0f", title="Top Villes"), unsafe_allow_html=True)
        with gcol2:
            st.markdown(_geo_card.format(icon="\U0001f30d", title="Top Pays"), unsafe_allow_html=True)

    # ── TAB 2: Engagement ─────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Reactions, Comments & Shares</div>', unsafe_allow_html=True)
        eng_df = series_to_df(eng.get("engagements", []))

        if not eng_df.empty:
            eng_df["rolling_7"] = eng_df["value"].rolling(7, min_periods=1).mean()
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=eng_df["date"], y=eng_df["value"],
                                  name="Daily Engagements", marker_color="#8b5cf6", opacity=0.7))
            fig2.add_trace(go.Scatter(x=eng_df["date"], y=eng_df["rolling_7"],
                                      name="7-Day Avg", line=dict(color="#f59e0b", width=2)))
            fig2.update_layout(title="Daily Post Engagements", **CHART_LAYOUT)
            st.plotly_chart(fig2, width="stretch")

        # Reactions breakdown
        react_data = eng.get("reactions", [])
        if react_data:
            latest = react_data[-1] if react_data else {}
            react_types = {k: v for k, v in latest.items() if k != "date"}
            if react_types:
                fig3 = px.pie(
                    names=list(react_types.keys()),
                    values=list(react_types.values()),
                    title="Reaction Breakdown",
                    color_discrete_sequence=px.colors.sequential.Plasma_r
                )
                fig3.update_layout(**CHART_LAYOUT)
                st.plotly_chart(fig3, width="stretch")

        if eng_df.empty:
            st.info("No engagement data available for this period.")

    # ── TAB 3: Visibility ────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Reach & Page View Fluctuations</div>', unsafe_allow_html=True)
        reach_df = series_to_df(vis.get("reach", []))
        views_df = series_to_df(vis.get("page_views", []))
        impr_df = series_to_df(vis.get("impressions", []))

        if not reach_df.empty:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=reach_df["date"], y=reach_df["value"],
                name="Unique Reach", fill="tozeroy",
                line=dict(color="#6366f1", width=2),
                fillcolor="rgba(99,102,241,0.15)"
            ))
            if not views_df.empty:
                fig4.add_trace(go.Scatter(
                    x=views_df["date"], y=views_df["value"],
                    name="Page Views", line=dict(color="#ec4899", width=2, dash="dot"),
                    yaxis="y2"
                ))
            # Peak detection
            if len(reach_df) > 3:
                mean_r = reach_df["value"].mean()
                std_r = reach_df["value"].std()
                peaks = reach_df[reach_df["value"] > mean_r + std_r]
                for _, pk in peaks.iterrows():
                    fig4.add_vline(x=pk["date"], line_dash="dash",
                                   line_color="rgba(251,191,36,0.5)", line_width=1)

            fig4.update_layout(
                title="Reach vs Page Views (peaks highlighted)",
                yaxis2=dict(overlaying="y", side="right",
                            gridcolor="rgba(255,255,255,0.04)"),
                **CHART_LAYOUT
            )
            st.plotly_chart(fig4, width="stretch")

            v1, v2, v3 = st.columns(3)
            v1.metric("Avg Daily Reach", f"{int(reach_df['value'].mean()):,}")
            peak_row = reach_df.loc[reach_df["value"].idxmax()]
            v2.metric("Peak Reach Day", peak_row["date"].strftime("%b %d"), delta=f"{int(peak_row['value']):,}")
            v3.metric("Total Impressions", f"{safe_sum(vis.get('impressions', [])):,}")
        else:
            st.info("No visibility data available for this period.")

    # ── TAB 4: Top Content ────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">Top 3 Posts</div>', unsafe_allow_html=True)
        if posts:
            posts_df = pd.DataFrame(posts)
            top_reach = posts_df.nlargest(3, "reach")
            top_eng = posts_df.nlargest(3, "total_interactions")

            c_left, c_right = st.columns(2)

            def render_posts(col, df, label, metric_col, metric_label):
                col.markdown(f"**{label}**")
                for _, row in df.iterrows():
                    col.markdown(f"""
<div class="post-card">
  <div style="font-size:12px;color:rgba(255,255,255,0.5);">{row['created_time']} • {row.get('media_type','POST')}</div>
  <div style="margin:6px 0;font-size:14px;">{row['text'] or '(No caption)'}</div>
  <div style="display:flex;gap:16px;font-size:13px;">
    <span>🎯 {row['reach']:,} reach</span>
    <span>❤️ {row['reactions']:,}</span>
    <span>💬 {row['comments']:,}</span>
  </div>
</div>""", unsafe_allow_html=True)

            render_posts(c_left, top_reach, "🏆 Top by Reach", "reach", "Reach")
            render_posts(c_right, top_eng, "🔥 Top by Engagement", "total_interactions", "Interactions")

            with st.expander("📋 All Posts Table"):
                st.dataframe(
                    posts_df[["created_time", "text", "reach", "reactions", "comments", "shares", "total_interactions"]],
                    width="stretch"
                )
        else:
            st.info("No post data available.")

    # ── TAB 5: Community Management ───────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-header">Response Rates & Timing</div>', unsafe_allow_html=True)
        total_t = convos.get("total_threads", 0)
        replied = convos.get("replied_threads", 0)
        times = convos.get("response_times_minutes", [])
        avg_time = round(np.mean(times), 1) if times else 0
        response_rate = round(replied / total_t * 100, 1) if total_t else 0

        cm1, cm2, cm3, cm4 = st.columns(4)
        cm1.metric("Response Rate", f"{response_rate}%")
        cm2.metric("Avg Response Time", f"{avg_time} min")
        cm3.metric("Total Conversations", f"{total_t:,}")
        cm4.metric("Unanswered", f"{len(convos.get('recent_unanswered', []))}",
                   delta_color="inverse", delta=f"-{total_t - replied}")

        unanswered = convos.get("recent_unanswered", [])
        if unanswered:
            st.markdown("**Recent Unanswered Messages**")
            for item in unanswered[:5]:
                st.markdown(f"""
<div class="post-card">
  <div style="font-size:12px;color:rgba(255,255,255,0.4);">{item.get('time','')}</div>
  <div style="font-size:14px;margin-top:4px;">{item.get('text','(No message)')}</div>
</div>""", unsafe_allow_html=True)
        else:
            st.success("🎉 All conversations have been responded to!")


# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
else:
    with st.spinner("Loading Instagram data…"):
        ig_profile = get_ig_profile(days, start_date, end_date)
        ig_eng = get_ig_engagement(days, start_date, end_date)
        ig_posts = get_ig_posts(days, start_date, end_date)

    followers            = ig_profile.get("followers_count") or 0
    follower_additions   = ig_profile.get("follower_additions", [])
    total_ig_reach       = ig_profile.get("period_reach", 0) or safe_sum(ig_profile.get("reach", []))
    total_ig_impressions = safe_sum(ig_profile.get("impressions", []))
    total_ig_views       = safe_sum(ig_profile.get("profile_views", []))

    # Aggregate engagement from posts (account-level API blocked for IG)
    total_ig_likes    = sum(p.get("reactions", 0) for p in ig_posts)
    total_ig_comments = sum(p.get("comments", 0) for p in ig_posts)
    total_ig_shares   = sum(p.get("shares", 0) for p in ig_posts)
    total_ig_saves    = sum(p.get("saves", 0) for p in ig_posts)
    total_ig_interactions = total_ig_likes + total_ig_comments + total_ig_shares + total_ig_saves

    # Impressions: sum from posts if account-level is 0
    if total_ig_impressions == 0:
        total_ig_impressions = sum(p.get("impressions", 0) for p in ig_posts)

    # New followers = sum of daily additions from follower_count metric
    ig_new_followers = sum(v["value"] for v in follower_additions if v["value"] > 0)
    ig_unfollows     = 0   # Instagram API does not expose unfollows

    ig_eng_rate     = round(total_ig_interactions / total_ig_reach * 100, 2) if total_ig_reach else 0.0
    ig_eng_per_post = round(total_ig_interactions / len(ig_posts), 1) if ig_posts else 0.0

    log_refresh(
        platform,
        period_label,
        "✅ Data Loaded",
        f"Followers: {followers}, Posts: {len(ig_posts)}, Reach: {total_ig_reach}"
    )

    # ── Instagram KPI Grid ────────────────────────────────────────────────────
    def _ig_kpi(icon, label, value, color="#ffffff"):
        return (
            f'<div style="background:rgba(255,255,255,0.05);border-radius:12px;'
            f'padding:0.9rem 1rem;text-align:center;">'
            f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);'
            f'margin-bottom:0.25rem;">{icon} {label}</div>'
            f'<div style="font-size:1.35rem;font-weight:800;color:{color};'
            f'white-space:nowrap;">{value}</div>'
            f'</div>'
        )

    ig_kpi_html = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_ig_kpi("👥", "Followers",            f"{followers:,}")}
  {_ig_kpi("➕", "Nouveaux Followers",   f"+{ig_new_followers:,}", "#4ade80")}
  {_ig_kpi("➖", "Désabonnements",       f"-{ig_unfollows:,}",    "#f87171")}
  {_ig_kpi("📊", "Taux d'engagement",    f"{ig_eng_rate}%",       "#facc15")}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_ig_kpi("👁️", "Couvertures",          f"{total_ig_reach:,}")}
  {_ig_kpi("📢", "Impressions",          f"{total_ig_impressions:,}")}
  {_ig_kpi("📝", "Publications",         str(len(ig_posts)))}
  {_ig_kpi("⚡", "Engagement / Publi.",   f"{ig_eng_per_post:,}")}
</div>
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_ig_kpi("🔥", "Total interactions",  f"{total_ig_interactions:,}", "#FF6B35")}
  {_ig_kpi("❤️", "Réactions",           f"{total_ig_likes:,}",        "#f87171")}
  {_ig_kpi("💬", "Commentaires",        f"{total_ig_comments:,}",     "#a78bfa")}
  {_ig_kpi("↗️", "Partages",            f"{total_ig_shares:,}",       "#34d399")}
  {_ig_kpi("🔖", "Enregistrements",     f"{total_ig_saves:,}",        "#60a5fa")}
</div>
"""
    st.markdown(ig_kpi_html, unsafe_allow_html=True)

    st.divider()

    # ── Instagram Top Publications by Visibility ───────────────────────────
    if ig_posts:
        st.markdown(
            '<div style="text-align:center; font-size:1.1rem; font-weight:700; '
            'letter-spacing:0.1em; color:rgba(255,255,255,0.6); margin-bottom:1.2rem;">'
            '🏆 TOP PUBLICATIONS PAR VISIBILITÉ</div>',
            unsafe_allow_html=True
        )

        ig_sorted_posts = sorted(ig_posts, key=lambda p: p.get("impressions", 0), reverse=True)[:6]
        ig_cols = st.columns(3)
        for idx, post in enumerate(ig_sorted_posts):
            col = ig_cols[idx % 3]
            with col:
                thumbnail = post.get("thumbnail", "")
                text = post.get("text", "")[:100] or "*(No caption)*"
                date = post.get("created_time", "")
                reacs = post.get("reactions", 0)
                comms = post.get("comments", 0)
                saves = post.get("saves", 0)
                total = post.get("total_interactions", 0)
                permalink = post.get("permalink", "#")

                if thumbnail:
                    st.image(thumbnail, use_container_width=True)
                else:
                    st.markdown(
                        '<div style="height:160px;background:rgba(255,255,255,0.05);'
                        'border-radius:12px;display:flex;align-items:center;'
                        'justify-content:center;color:rgba(255,255,255,0.3);">📷 No image</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<p style="font-size:0.75rem;color:rgba(255,255,255,0.45);margin:0.3rem 0 0.1rem;">{date}</p>'
                    f'<p style="font-size:0.82rem;color:rgba(255,255,255,0.85);line-height:1.4;margin-bottom:0.5rem;">{text}</p>',
                    unsafe_allow_html=True
                )

                imp_val = post.get('impressions', 0)
                st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;margin:0.5rem 0;">
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">📢 Impressions</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{imp_val:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">❤️ Réactions</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{reacs:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">💬 Commentaires</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{comms:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">🔖 Enregistrements</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{saves:,}</div>
  </div>
</div>
<div style="background:rgba(232,66,10,0.15);border-radius:8px;padding:0.5rem 0.6rem;margin-bottom:0.5rem;">
  <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⚡ Total interactions</div>
  <div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>
</div>
<a href="{permalink}" target="_blank"
   style="font-size:0.75rem;color:#6c8ebf;text-decoration:none;">
  🔗 Voir la publication
</a><br><br>
""", unsafe_allow_html=True)

        st.divider()

    # ── Instagram Top Publications by Engagement ───────────────────────────
    if ig_posts:
        st.markdown(
            '<div style="text-align:center; font-size:1.1rem; font-weight:700; '
            'letter-spacing:0.1em; color:rgba(255,255,255,0.6); margin-bottom:1.2rem;">'
            '⚡ TOP PUBLICATIONS PAR ENGAGEMENT</div>',
            unsafe_allow_html=True
        )

        ig_eng_sorted = sorted(ig_posts, key=lambda p: p.get("total_interactions", 0), reverse=True)[:6]
        ig_eng_cols = st.columns(3)
        for idx, post in enumerate(ig_eng_sorted):
            col = ig_eng_cols[idx % 3]
            with col:
                thumbnail = post.get("thumbnail", "")
                text = post.get("text", "")[:100] or "*(No caption)*"
                date = post.get("created_time", "")
                reacs = post.get("reactions", 0)
                comms = post.get("comments", 0)
                saves = post.get("saves", 0)
                total = post.get("total_interactions", 0)
                permalink = post.get("permalink", "#")

                if thumbnail:
                    st.image(thumbnail, use_container_width=True)
                else:
                    st.markdown(
                        '<div style="height:160px;background:rgba(255,255,255,0.05);'
                        'border-radius:12px;display:flex;align-items:center;'
                        'justify-content:center;color:rgba(255,255,255,0.3);">📷 No image</div>',
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f'<p style="font-size:0.75rem;color:rgba(255,255,255,0.45);margin:0.3rem 0 0.1rem;">{date}</p>'
                    f'<p style="font-size:0.82rem;color:rgba(255,255,255,0.85);line-height:1.4;margin-bottom:0.5rem;">{text}</p>',
                    unsafe_allow_html=True
                )

                imp_val = post.get('impressions', 0)
                st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;margin:0.5rem 0;">
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">📢 Impressions</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{imp_val:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">❤️ Réactions</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{reacs:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">💬 Commentaires</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{comms:,}</div>
  </div>
  <div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">
    <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">🔖 Enregistrements</div>
    <div style="font-size:1rem;font-weight:700;color:#fff;">{saves:,}</div>
  </div>
</div>
<div style="background:rgba(232,66,10,0.15);border-radius:8px;padding:0.5rem 0.6rem;margin-bottom:0.5rem;">
  <div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⚡ Total interactions</div>
  <div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>
</div>
<a href="{permalink}" target="_blank"
   style="font-size:0.75rem;color:#6c8ebf;text-decoration:none;">
  🔗 Voir la publication
</a><br><br>
""", unsafe_allow_html=True)

        st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Audience", "💬 Engagement", "📡 Visibility", "🏆 Top Content"
    ])

    # ── TAB 1: Audience ───────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-header">Follower Trend</div>', unsafe_allow_html=True)
        follower_series = ig_profile.get("follower_series", [])
        if follower_series:
            df_fol = series_to_df(follower_series)
            fig = px.area(df_fol, x="date", y="value", title="Follower Count Over Time",
                          color_discrete_sequence=["#6366f1"])
            fig.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Follower time-series not available — showing current snapshot.")
            st.metric("Current Followers", f"{followers:,}")

    # ── TAB 2: Engagement ─────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Likes, Comments & Saves</div>', unsafe_allow_html=True)
        daily = ig_eng.get("daily", [])
        if daily:
            df_d = pd.DataFrame(daily)
            df_d["date"] = pd.to_datetime(df_d["date"])
            pivot = df_d.pivot_table(index="date", columns="metric", values="value", aggfunc="sum").fillna(0)
            fig5 = px.bar(pivot.reset_index(), x="date", y=pivot.columns.tolist(),
                          title="Daily Engagement Breakdown",
                          color_discrete_sequence=["#6366f1", "#ec4899", "#f59e0b", "#34d399"])
            fig5.update_layout(barmode="stack", **CHART_LAYOUT)
            st.plotly_chart(fig5, width="stretch")

        e1, e2, e3 = st.columns(3)
        e1.metric("❤️ Likes", f"{total_ig_likes:,}")
        e2.metric("💬 Comments", f"{total_ig_comments:,}")
        e3.metric("📊 Engagement Rate", f"{ig_eng_rate}%")

    # ── TAB 3: Visibility ────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="section-header">Reach & Impressions</div>', unsafe_allow_html=True)
        reach_s = ig_profile.get("reach", [])
        impr_s = ig_profile.get("impressions", [])
        if reach_s:
            df_r = series_to_df(reach_s)
            df_i = series_to_df(impr_s) if impr_s else pd.DataFrame()
            fig6 = go.Figure()
            fig6.add_trace(go.Scatter(x=df_r["date"], y=df_r["value"],
                                      fill="tozeroy", name="Reach",
                                      line=dict(color="#6366f1", width=2),
                                      fillcolor="rgba(99,102,241,0.15)"))
            if not df_i.empty:
                fig6.add_trace(go.Scatter(x=df_i["date"], y=df_i["value"],
                                          name="Impressions",
                                          line=dict(color="#ec4899", width=2, dash="dot")))
            fig6.update_layout(title="Reach vs Impressions", **CHART_LAYOUT)
            st.plotly_chart(fig6, width="stretch")
        else:
            st.info("No visibility data available for this period.")

    # ── TAB 4: Top Content ────────────────────────────────────────────────────
    with tab4:
        st.markdown('<div class="section-header">Top 3 Instagram Posts</div>', unsafe_allow_html=True)
        if ig_posts:
            df_p = pd.DataFrame(ig_posts)
            top_r = df_p.nlargest(3, "reach")
            top_e = df_p.nlargest(3, "total_interactions")

            c_l, c_r = st.columns(2)
            for col, df_top, label in [(c_l, top_r, "🏆 Top by Reach"), (c_r, top_e, "🔥 Top by Engagement")]:
                col.markdown(f"**{label}**")
                for _, row in df_top.iterrows():
                    col.markdown(f"""
<div class="post-card">
  <div style="font-size:12px;color:rgba(255,255,255,0.5);">{row['created_time']} • {row.get('media_type','')}</div>
  <div style="margin:6px 0;font-size:14px;">{row['text'] or '(No caption)'}</div>
  <div style="display:flex;gap:16px;font-size:13px;">
    <span>🎯 {row['reach']:,} reach</span>
    <span>❤️ {row['reactions']:,}</span>
    <span>💬 {row['comments']:,}</span>
  </div>
</div>""", unsafe_allow_html=True)
        else:
            st.info("No post data available.")
