import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

import api_client as api
from components.charts import CHART_LAYOUT, series_to_df, safe_sum, render_top3_podium


# ─── Cached fetchers ──────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def get_ig_profile(days, start=None, end=None):
    return api.fetch_ig_profile(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_engagement(days, start=None, end=None):
    return api.fetch_ig_engagement(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_posts(days, start=None, end=None):
    return api.fetch_ig_posts(days, start, end, 100)



# ─── Main render function ─────────────────────────────────────────────────────
def render_instagram_dashboard(period_label: str, days: int, start_date, end_date, log_refresh_fn):
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

    # New followers = net change: last daily cumulative value - first daily cumulative value
    # (follower_count returns cumulative totals per day, NOT daily additions)
    if len(follower_additions) >= 2:
        ig_new_followers = follower_additions[-1]["value"] - follower_additions[0]["value"]
    elif len(follower_additions) == 1:
        ig_new_followers = 0
    else:
        ig_new_followers = None  # API returned no data

    ig_eng_rate     = round(total_ig_interactions / total_ig_reach * 100, 2) if total_ig_reach else 0.0
    ig_eng_per_post = round(total_ig_interactions / len(ig_posts), 1) if ig_posts else 0.0

    log_refresh_fn(
        "Instagram",
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

    # Format new followers display
    if ig_new_followers is None:
        _new_followers_str = "N/A"
    elif ig_new_followers >= 0:
        _new_followers_str = f"+{ig_new_followers:,}"
    else:
        _new_followers_str = f"{ig_new_followers:,}"

    ig_kpi_html = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_ig_kpi("👥", "Followers",            f"{followers:,}")}
  {_ig_kpi("➕", "Nouveaux Followers",   _new_followers_str, "#4ade80")}
  {_ig_kpi("📝", "Publications",         str(len(ig_posts)))}
  {_ig_kpi("📊", "Taux d'engagement",    f"{ig_eng_rate}%",       "#facc15")}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_ig_kpi("👁️", "Couvertures",          f"{total_ig_reach:,}")}
  {_ig_kpi("📢", "Impressions",          f"{total_ig_impressions:,}")}
  {_ig_kpi("🔖", "Enregistrements",      f"{total_ig_saves:,}",        "#60a5fa")}
  {_ig_kpi("⚡", "Engagement / Publi.",   f"{ig_eng_per_post:,}")}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_ig_kpi("🔥", "Total interactions",  f"{total_ig_interactions:,}", "#FF6B35")}
  {_ig_kpi("❤️", "Réactions",           f"{total_ig_likes:,}",        "#f87171")}
  {_ig_kpi("💬", "Commentaires",        f"{total_ig_comments:,}",     "#a78bfa")}
  {_ig_kpi("↗️", "Partages",            f"{total_ig_shares:,}",       "#34d399")}
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


