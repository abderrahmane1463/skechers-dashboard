import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

import api_client as api
from components.charts import CHART_LAYOUT, series_to_df, safe_sum, render_top3_podium


# ─── Post card helper ─────────────────────────────────────────────────────────
def _render_post_card(post: dict, link_color: str = "#6c8ebf"):
    """Renders a full-detail post card with all available metrics."""
    thumbnail        = post.get("thumbnail", "")
    text             = post.get("text", "")[:100] or "*(No caption)*"
    date             = post.get("created_time", "")
    post_id          = post.get("id", "")
    post_url         = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "#"

    reach            = post.get("reach", 0)
    total_views      = post.get("total_views", 0)
    impressions      = post.get("impressions", 0)
    imp_org          = post.get("impressions_organic", 0)
    imp_paid         = post.get("impressions_paid", 0)

    reacs            = post.get("reactions", 0)
    comms            = post.get("comments", 0)
    shars            = post.get("shares", 0)
    clicks           = post.get("clicks", 0)
    clicks_uniq      = post.get("clicks_unique", 0)
    engaged          = post.get("engaged_users", 0)
    negative         = post.get("negative_feedback", 0)
    total            = post.get("total_interactions", 0)

    reactions_by_type = post.get("reactions_by_type", {}) or {}

    video_views      = post.get("video_views", 0)
    video_uniq       = post.get("video_views_unique", 0)
    video_complete   = post.get("video_complete_views", 0)
    video_avg        = post.get("video_avg_watch_sec", 0)
    is_video         = video_views > 0

    def _cell(icon, label, value, color="#fff"):
        return (
            f'<div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">'
            f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">{icon} {label}</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{color};">{value:,}</div>'
            f'</div>'
        ) if isinstance(value, int) else (
            f'<div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">'
            f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">{icon} {label}</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{color};">{value}</div>'
            f'</div>'
        )

    if thumbnail:
        st.image(thumbnail, width="stretch")
    else:
        st.markdown(
            '<div style="height:140px;background:rgba(255,255,255,0.05);border-radius:12px;'
            'display:flex;align-items:center;justify-content:center;'
            'color:rgba(255,255,255,0.3);">📷 No image</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<p style="font-size:0.75rem;color:rgba(255,255,255,0.45);margin:0.3rem 0 0.1rem;">{date}</p>'
        f'<p style="font-size:0.82rem;color:rgba(255,255,255,0.85);line-height:1.4;margin-bottom:0.5rem;">{text}</p>',
        unsafe_allow_html=True
    )

    # ── Portée & Impressions ──
    st.markdown(
        '<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
        'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Portée & Impressions</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.35rem;">'
        f'{_cell("👁️", "Vues toutes sources", total_views)}'
        f'{_cell("📢", "Impressions totales", impressions)}'
        f'{_cell("🌱", "Organic", imp_org, "#4ade80")}'
        f'{_cell("💰", "Payé", imp_paid, "#facc15")}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Engagement ──
    st.markdown(
        '<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
        'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Engagement</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.35rem;">'
        f'{_cell("❤️", "Réactions", reacs)}'
        f'{_cell("💬", "Commentaires", comms)}'
        f'{_cell("🔁", "Partages", shars)}'
        f'{_cell("🖱️", "Clics uniques", clicks_uniq)}'
        f'{_cell("🖱️", "Clics totaux", clicks)}'
        f'{_cell("👤", "Utilisateurs engagés", engaged)}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Réactions par type ──
    if reactions_by_type:
        _REACTION_ICONS = {"like": "👍", "love": "❤️", "haha": "😂", "wow": "😮", "sad": "😢", "angry": "😡"}
        react_cells = "".join(
            f'<div style="text-align:center;background:rgba(255,255,255,0.04);'
            f'border-radius:8px;padding:0.4rem 0.3rem;">'
            f'<div style="font-size:1.1rem;">{_REACTION_ICONS.get(k, "👍")}</div>'
            f'<div style="font-size:0.85rem;font-weight:700;color:#fff;">{v:,}</div>'
            f'</div>'
            for k, v in reactions_by_type.items() if v > 0
        )
        if react_cells:
            st.markdown(
                '<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
                'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Détail réactions</div>'
                f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:0.25rem;">{react_cells}</div>',
                unsafe_allow_html=True
            )

    # ── Vidéo (si applicable) ──
    if is_video:
        avg_str = f"{video_avg:.1f}s" if video_avg else "—"
        st.markdown(
            '<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
            'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Vidéo / Reels</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.35rem;">'
            f'{_cell("▶️", "Vues (≥3s)", video_views)}'
            f'{_cell("👤", "Vues uniques", video_uniq)}'
            f'{_cell("✅", "Vues complètes", video_complete)}'
            f'<div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">'
            f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⏱️ Temps moyen</div>'
            f'<div style="font-size:1rem;font-weight:700;color:#fff;">{avg_str}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Total + feedback négatif ──
    neg_color = "#f87171" if negative > 0 else "rgba(255,255,255,0.3)"
    st.markdown(
        f'<div style="display:grid;grid-template-columns:3fr 1fr;gap:0.35rem;margin-top:0.4rem;">'
        f'<div style="background:rgba(232,66,10,0.15);border-radius:8px;padding:0.5rem 0.7rem;">'
        f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⚡ Total interactions</div>'
        f'<div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>'
        f'</div>'
        f'<div style="background:rgba(255,255,255,0.04);border-radius:8px;padding:0.5rem 0.6rem;text-align:center;">'
        f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.35);">🚫 Masqué</div>'
        f'<div style="font-size:1rem;font-weight:700;color:{neg_color};">{negative:,}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<a href="{post_url}" target="_blank" '
        f'style="font-size:0.75rem;color:{link_color};text-decoration:none;">🔗 Voir la publication</a><br><br>',
        unsafe_allow_html=True
    )


# ─── Cached fetchers ──────────────────────────────────────────────────────────
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



# ─── Main render function ─────────────────────────────────────────────────────
def render_facebook_dashboard(period_label: str, days: int, start_date, end_date, log_refresh_fn):
    with st.spinner("Loading Facebook data…"):
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

    log_refresh_fn(
        "Facebook",
        period_label,
        "✅ Data Loaded",
        f"Followers: {total_fans}, Posts: {len(posts)}, Reach: {total_reach}"
    )

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
            with cols[idx % 3]:
                _render_post_card(post, link_color="#6c8ebf")

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
            with eng_cols[idx % 3]:
                _render_post_card(post, link_color="#FF6B35")

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Audience", "💬 Engagement", "📡 Visibility", "🏆 Top Content", "🤝 Community"
    ])

    # ── TAB 1: Audience ───────────────────────────────────────────────────────
    with tab1:
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
                'DONNÉES DÉMOGRAPHIQUES</p>'
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
            'Données non disponibles via API<br>'
            '<span style="font-size:0.7rem;">(Restriction Meta — New Page Experience)</span></p>'
            '<a href="https://business.facebook.com/insights/" target="_blank" '
            'style="background:linear-gradient(90deg,#E8420A,#C1320A);color:#fff;'
            'text-decoration:none;padding:0.4rem 1rem;border-radius:8px;font-size:0.8rem;font-weight:600;">'
            '\U0001f517 Business Suite</a></div>'
        )
        with gcol1:
            st.markdown(_geo_card.format(icon="\U0001f3d9️", title="Top Villes"), unsafe_allow_html=True)
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
        if posts:
            render_top3_podium(
                posts,
                sort_key="reach",
                title="TOP #3 PUBLICATIONS PAR VISIBILITÉ",
                view_label="Vues",
            )
            st.divider()
            render_top3_podium(
                posts,
                sort_key="total_interactions",
                title="TOP #3 PUBLICATIONS PAR ENGAGEMENT",
                view_label="Vues",
            )

            with st.expander("📋 Toutes les publications"):
                posts_df = pd.DataFrame(posts)
                st.dataframe(
                    posts_df[["created_time", "text", "reach", "reactions", "comments", "shares", "total_interactions"]],
                    use_container_width=True,
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

