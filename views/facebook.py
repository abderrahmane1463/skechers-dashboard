import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

import db
from components.charts import get_chart_layout, series_to_df, safe_sum, render_top3_podium


# ─── Post card helper ─────────────────────────────────────────────────────────
def _render_post_card(post: dict, link_color: str = "#6c8ebf"):
    """Renders a full-detail post card with all available metrics."""
    _dark = st.session_state.get("theme", "dark") == "dark"

    thumbnail        = post.get("thumbnail", "")
    text             = post.get("text", "")[:100] or "*(No caption)*"
    date             = post.get("created_time", "")
    post_id          = post.get("id", "")
    post_url         = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "#"

    total_views      = post.get("total_views", 0)
    imp_org          = post.get("impressions_organic", 0)
    imp_paid         = post.get("impressions_paid", 0)
    reacs            = post.get("reactions", 0)
    comms            = post.get("comments", 0)
    shars            = post.get("shares", 0)
    clicks           = post.get("clicks", 0)
    total            = post.get("total_interactions", 0)
    video_views      = post.get("video_views", 0)
    video_uniq       = post.get("video_views_unique", 0)
    video_complete   = post.get("video_complete_views", 0)
    video_avg        = post.get("video_avg_watch_sec", 0)
    is_video         = video_views > 0

    # ── Theme tokens ──
    _cell_bg   = "rgba(255,255,255,0.05)" if _dark else "#f8fafc"
    _cell_brd  = "" if _dark else "border:1px solid #e5e7eb;"
    _cell_lc   = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
    _cell_vc   = "#ffffff" if _dark else "#111827"
    _date_c    = "rgba(255,255,255,0.45)" if _dark else "#9ca3af"
    _text_c    = "rgba(255,255,255,0.85)" if _dark else "#111827"
    _shdr_c    = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"
    _no_img_bg = "rgba(255,255,255,0.05)" if _dark else "#f3f4f6"
    _no_img_tc = "rgba(255,255,255,0.3)"  if _dark else "#d1d5db"
    _total_lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
    _total_bg  = "rgba(232,66,10,0.15)"   if _dark else "rgba(232,66,10,0.08)"

    def _cell(icon, label, value, color=None):
        _vc  = color if color else _cell_vc
        _val = f"{value:,}" if isinstance(value, int) else str(value)
        return (
            f'<div style="background:{_cell_bg};{_cell_brd}border-radius:8px;padding:0.5rem 0.6rem;">'
            f'<div style="font-size:0.7rem;color:{_cell_lc};">{icon} {label}</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{_vc};">{_val}</div>'
            f'</div>'
        )

    if thumbnail:
        st.image(thumbnail, width="stretch")
    else:
        st.markdown(
            f'<div style="height:140px;background:{_no_img_bg};border-radius:12px;'
            f'display:flex;align-items:center;justify-content:center;'
            f'color:{_no_img_tc};">📷 No image</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<p style="font-size:0.75rem;color:{_date_c};margin:0.3rem 0 0.1rem;">{date}</p>'
        f'<p style="font-size:0.82rem;color:{_text_c};line-height:1.4;margin-bottom:0.5rem;">{text}</p>',
        unsafe_allow_html=True
    )

    # ── Portée & Impressions ──
    st.markdown(
        f'<div style="font-size:0.68rem;color:{_shdr_c};'
        f'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Portée & Impressions</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.35rem;">'
        f'{_cell("👁️", "Reach", total_views)}'
        f'{_cell("🌱", "Organic", imp_org, "#4ade80")}'
        f'{_cell("💰", "Payé", imp_paid, "#facc15")}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Engagement ──
    st.markdown(
        f'<div style="font-size:0.68rem;color:{_shdr_c};'
        f'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Engagement</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.35rem;">'
        f'{_cell("❤️", "Réactions", reacs)}'
        f'{_cell("💬", "Commentaires", comms)}'
        f'{_cell("🔁", "Partages", shars)}'
        f'{_cell("🖱️", "Clics", clicks)}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ── Vidéo (si applicable) ──
    if is_video:
        avg_str = f"{video_avg:.1f}s" if video_avg else "—"
        st.markdown(
            f'<div style="font-size:0.68rem;color:{_shdr_c};'
            f'text-transform:uppercase;letter-spacing:0.06em;margin:0.5rem 0 0.25rem;">Vidéo / Reels</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.35rem;">'
            f'{_cell("▶️", "Vues (≥3s)", video_views)}'
            f'{_cell("👤", "Vues uniques", video_uniq)}'
            f'{_cell("✅", "Vues complètes", video_complete)}'
            f'<div style="background:{_cell_bg};{_cell_brd}border-radius:8px;padding:0.5rem 0.6rem;">'
            f'<div style="font-size:0.7rem;color:{_cell_lc};">⏱️ Temps moyen</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{_cell_vc};">{avg_str}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── Total interactions ──
    st.markdown(
        f'<div style="margin-top:0.4rem;background:{_total_bg};border-radius:8px;padding:0.5rem 0.7rem;">'
        f'<div style="font-size:0.7rem;color:{_total_lc};">⚡ Total interactions</div>'
        f'<div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>'
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
    return db.get_fb_audience(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_engagement(days, start=None, end=None):
    return db.get_fb_engagement(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_visibility(days, start=None, end=None):
    return db.get_fb_visibility(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_posts(days, start=None, end=None):
    return db.get_fb_posts(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_messaging_stats(days=30, start=None, end=None):
    return db.get_fb_messaging_stats(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_fb_post_totals(days=30, start=None, end=None):
    return db.get_fb_post_totals(days, start, end)


# ─── Main render function ─────────────────────────────────────────────────────
def render_facebook_dashboard(period_label: str, days: int, start_date, end_date, log_refresh_fn):
    with st.spinner("Loading Facebook data…"):
        fetchers = {
            "aud":         lambda: get_fb_audience(days, start_date, end_date),
            "eng":         lambda: get_fb_engagement(days, start_date, end_date),
            "vis":         lambda: get_fb_visibility(days, start_date, end_date),
            "posts":       lambda: get_fb_posts(days, start_date, end_date),
            "post_totals": lambda: get_fb_post_totals(days, start_date, end_date),
            "msg_stats":   lambda: get_fb_messaging_stats(days, start_date, end_date),
        }
        results = {}
        with ThreadPoolExecutor(max_workers=len(fetchers)) as pool:
            futures = {pool.submit(fn): key for key, fn in fetchers.items()}
            for future in as_completed(futures):
                key = futures[future]
                try:
                    results[key] = future.result()
                except Exception as e:
                    print(f"DEBUG fetch {key} error: {e}")
                    results[key] = {} if key != "posts" else []
        aud         = results["aud"]
        eng         = results["eng"]
        vis         = results["vis"]
        posts       = results["posts"]
        post_totals = results.get("post_totals", {})
        msg_stats   = results["msg_stats"]

    # ── KPI Row ──────────────────────────────────────────────────────────────
    total_fans = aud.get("fans_total") or 0
    total_adds = safe_sum(aud.get("fans_adds", []))
    total_removes = safe_sum(aud.get("fans_removes", []))
    total_reach = vis.get("period_reach", 0) or safe_sum(vis.get("reach", []))
    total_impressions = vis.get("period_impressions") or safe_sum(vis.get("impressions", []))
    total_views = safe_sum(vis.get("page_views", []))
    total_content_interactions = eng.get("period_content_interactions", 0)

    # Interactions from all posts in period (not capped at 20)
    total_reacs = post_totals.get("total_reactions", sum(p.get("reactions", 0) for p in posts))
    total_comms = post_totals.get("total_comments",  sum(p.get("comments",  0) for p in posts))
    total_shars = post_totals.get("total_shares",    sum(p.get("shares",    0) for p in posts))
    total_engagements = post_totals.get("total_interactions", total_reacs + total_comms + total_shars)

    # Reach availability — computed from the selected window size, NOT from cached data.
    # This guarantees correct display even when old Supabase rows (pre-change) are returned.
    #
    # Exact Meta API windows:
    #   1 day      → period=day   (Today, Yesterday)
    #   2–7 days   → period=week  (This Week, Last Week, Last 7 Days)
    #   28–31 days → period=month (Last 30 Days, This Month, Last Month)
    #   All others → no exact window exists → show "—"
    from datetime import datetime as _vdt
    if start_date and end_date:
        _w = (
            _vdt.strptime(end_date,   "%Y-%m-%d").date()
          - _vdt.strptime(start_date, "%Y-%m-%d").date()
        ).days + 1
    else:
        _w = days + 1   # rolling window: Last Nd covers N+1 boundaries

    _reach_unavailable = not (
        _w == 1
        or (2  <= _w <= 7)
        or (28 <= _w <= 31)
    )

    # Engagement rate: only meaningful when reach is exact
    eng_rate = (
        round(total_content_interactions / total_reach * 100, 2)
        if total_reach and not _reach_unavailable else 0.0
    )

    # KPI display
    _reach_display = "—" if _reach_unavailable else f"{total_reach:,}"
    _reach_note    = "ℹ️ Indisponible pour cette période" if _reach_unavailable else None

    log_refresh_fn(
        "Facebook",
        period_label,
        "✅ Data Loaded",
        f"Followers: {total_fans}, Posts: {len(posts)}, Reach: {total_reach}"
    )

    _dark = st.session_state.get("theme", "dark") == "dark"
    def _kpi(icon, label, value, color=None, note=None):
        _bg  = "rgba(255,255,255,0.05)" if _dark else "#ffffff"
        _brd = "none" if _dark else "1px solid #e5e7eb"
        _lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
        _nc  = "rgba(255,255,255,0.3)"  if _dark else "#9ca3af"
        _vc  = color if color else ("#ffffff" if _dark else "#111827")
        _note_html = (
            f'<div style="font-size:0.62rem;color:{_nc};margin-top:0.25rem;'
            f'white-space:normal;line-height:1.35;">{note}</div>'
        ) if note else ""
        return (
            f'<div style="background:{_bg};border:{_brd};border-radius:12px;'
            f'padding:0.9rem 1rem;text-align:center;">'
            f'<div style="font-size:0.72rem;color:{_lc};'
            f'margin-bottom:0.25rem;">{icon} {label}</div>'
            f'<div style="font-size:1.35rem;font-weight:800;color:{_vc};'
            f'white-space:nowrap;">{value}</div>'
            f'{_note_html}'
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
  {_kpi("👁️", "Spectateurs",             _reach_display, note=_reach_note)}
  {_kpi("📢", "Impressions",              f"{total_impressions:,}")}
  {_kpi("🤝", "Content Interactions",     f"{total_content_interactions:,}", "#a78bfa")}
  {_kpi("📝", "Publications",             str(len(posts)))}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi("🔥", "Total interactions (posts)",   f"{total_engagements:,}", "#FF6B35")}
  {_kpi("❤️", "Réactions",            f"{total_reacs:,}")}
  {_kpi("💬", "Commentaires",         f"{total_comms:,}")}
  {_kpi("🔁", "Partages",             f"{total_shars:,}")}
</div>
"""
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Audience", "📡 Visibility", "💬 Engagement", "🏆 Top Content", "🤝 Community"
    ])

    # ── TAB 1: Audience ───────────────────────────────────────────────────────
    with tab1:
        hcol1, hcol2 = st.columns([1, 1])
        _h1c = "#ffffff" if _dark else "#111827"
        _h2c = "rgba(255,255,255,0.6)" if _dark else "#6b7280"
        with hcol1:
            st.markdown(
                f'<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
                f'color:{_h1c};margin:0;">AUDIENCE</p>',
                unsafe_allow_html=True
            )
        with hcol2:
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:flex-end;gap:8px;">'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="#1877F2">'
                f'<path d="M24 12.073C24 5.405 18.627 0 12 0S0 5.405 0 12.073C0 18.1 4.388 23.094 10.125 24v-8.437H7.078v-3.49h3.047V9.41c0-3.025 1.792-4.697 4.533-4.697 1.312 0 2.686.236 2.686.236v2.97h-1.513c-1.491 0-1.956.93-1.956 1.886v2.268h3.328l-.532 3.49h-2.796V24C19.612 23.094 24 18.1 24 12.073z"/>'
                f'</svg>'
                f'<span style="font-size:0.85rem;font-weight:600;color:{_h2c};">FACEBOOK PERFORMANCE</span>'
                f'</div>',
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
                _gc = "rgba(255,255,255,0.06)" if _dark else "#e5e7eb"
            audience_layout = {
                    **get_chart_layout(),
                    "yaxis": dict(
                        gridcolor=_gc,
                        showline=False,
                        range=[0, max(merged["adds"].max() * 1.2, 10)]
                    ),
                    "xaxis": dict(
                        gridcolor=_gc,
                        showline=False,
                        tickmode="array",
                        tickvals=[merged["date"].iloc[i]
                                  for i in range(0, len(merged), max(len(merged)//6, 1))][:7],
                        tickangle=0,
                    ),
                    "showlegend": False,
                    "margin": dict(l=0, r=0, t=10, b=40),
                    "height": 280,
                }
                fig.update_layout(**audience_layout)
                st.plotly_chart(fig, width="stretch")

                _legend_c = "rgba(255,255,255,0.5)" if _dark else "#6b7280"
                st.markdown(
                    f'<div style="text-align:center;margin-top:-12px;">'
                    f'<span style="display:inline-block;width:28px;height:2px;'
                    f'background:#7EC8E3;vertical-align:middle;margin-right:6px;"></span>'
                    f'<span style="font-size:0.75rem;color:{_legend_c};">Follows</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with sidebar_col:
                _sb_bg  = "rgba(255,255,255,0.04)" if _dark else "#f8fafc"
                _sb_brd = "" if _dark else "border:1px solid #e5e7eb;"
                _sb_lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
                _sb_vc  = "#ffffff" if _dark else "#111827"
                st.markdown(
                    f'<div style="background:{_sb_bg};{_sb_brd}border-radius:12px;'
                    f'padding:1.2rem 1rem;display:flex;flex-direction:column;gap:1.2rem;">'

                    f'<div>'
                    f'<div style="font-size:0.7rem;color:{_sb_lc};'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Unfollows</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:{_sb_vc};">{total_unfollows:,}</div>'
                    f'{_trend_html(pct_removes)}'
                    f'</div>'

                    f'<div>'
                    f'<div style="font-size:0.7rem;color:{_sb_lc};'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Net follows</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:{_sb_vc};">{net_follows:,}</div>'
                    f'{_trend_html(pct_net)}'
                    f'</div>'

                    f'<div>'
                    f'<div style="font-size:0.7rem;color:{_sb_lc};'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Followers (Lifetime)</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:#FF6B35;">{total_fans:,}</div>'
                    f'</div>'

                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("No audience data available for this period.")

        # ── Auto-analysis text ───────────────────────────────────────────────
        if not adds_df.empty:
            net_total   = int(merged["net"].sum()) if "net" in merged.columns else 0
            peak_row    = merged.loc[merged["adds"].idxmax()]
            peak_date   = peak_row["date"].strftime("%d/%m")
            peak_val    = int(peak_row["adds"])
            direction   = "▲" if net_total >= 0 else "▼"
            dir_color   = "#4ade80" if net_total >= 0 else "#f87171"
            _ana_bg = "rgba(255,255,255,0.03)" if _dark else "#f8fafc"
            _ana_tc = "rgba(255,255,255,0.6)"  if _dark else "#4b5563"
            _ana_vc = "#ffffff" if _dark else "#111827"
            st.markdown(
                f'<div style="background:{_ana_bg};border-left:3px solid rgba(126,200,227,0.5);'
                f'border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:0.5rem 0 0.3rem;'
                f'font-size:0.82rem;color:{_ana_tc};line-height:1.6;">'
                f'Pic d\'abonnements : <b style="color:#7EC8E3;">{peak_date}</b> avec '
                f'<b style="color:{_ana_vc};">{peak_val:,}</b> nouveaux follows. '
                f'Solde net sur la période : '
                f'<b style="color:{dir_color};">{direction} {abs(net_total):,}</b>.'
                f'</div>',
                unsafe_allow_html=True
            )


    # ── TAB 2: Visibility ────────────────────────────────────────────────────
    with tab3:
        # Use daily Content Interactions series — same source as 🤝 Content Interactions KPI
        chart_df = series_to_df(eng.get("engagements", []))

        if not chart_df.empty and (start_date or days):
            _range_start = pd.Timestamp(start_date) if start_date else pd.Timestamp.now() - pd.Timedelta(days=days)
            _range_end   = pd.Timestamp(end_date)   if end_date   else pd.Timestamp.now()
            _full_range  = pd.DataFrame({"date": pd.date_range(_range_start, _range_end, freq="D")})
            chart_df = _full_range.merge(chart_df, on="date", how="left").fillna(0)

        chart_total = int(chart_df["value"].sum()) if not chart_df.empty else total_content_interactions

        if not chart_df.empty:
            fig_ci = go.Figure()
            fig_ci.add_trace(go.Scatter(
                x=chart_df["date"], y=chart_df["value"],
                name="Total interactions",
                line=dict(color="#FF6B35", width=3),
                fill="tozeroy",
                fillcolor="rgba(232,66,10,0.08)",
                mode="lines",
            ))
            _gc2 = "rgba(255,255,255,0.06)" if _dark else "#e5e7eb"
            ci_layout = {
                **get_chart_layout(),
                "yaxis": dict(
                    gridcolor=_gc2,
                    showline=False,
                    tickformat=",",
                ),
                "xaxis": dict(
                    gridcolor=_gc2,
                    showline=False,
                    tickmode="array",
                    tickvals=[chart_df["date"].iloc[i]
                              for i in range(0, len(chart_df), max(len(chart_df)//6, 1))][:7],
                    tickangle=0,
                ),
                "showlegend": False,
                "margin": dict(l=0, r=0, t=10, b=40),
                "height": 300,
            }
            fig_ci.update_layout(**ci_layout)
            st.plotly_chart(fig_ci, width="stretch")

            st.metric("🤝 Content Interactions", f"{chart_total:,}")


    # ── TAB 3: Engagement ─────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-header">Reach & Page View Fluctuations</div>', unsafe_allow_html=True)
        reach_df      = series_to_df(vis.get("reach", []))
        views_df      = series_to_df(vis.get("page_views", []))
        # Prefer page_impressions_daily (page_impressions — all placements) for the
        # chart so it matches the 📢 Impressions KPI which also uses page_impressions.
        # Fall back to the generic "impressions" key only if the primary is absent.
        impressions_df = series_to_df(
            vis.get("page_impressions_daily") or vis.get("impressions", [])
        )

        if not reach_df.empty:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=reach_df["date"], y=reach_df["value"],
                name="Unique Reach", fill="tozeroy",
                line=dict(color="#6366f1", width=2),
                fillcolor="rgba(99,102,241,0.15)"
            ))
            if len(reach_df) > 3:
                mean_r = reach_df["value"].mean()
                std_r = reach_df["value"].std()
                peaks = reach_df[reach_df["value"] > mean_r + std_r]
                for _, pk in peaks.iterrows():
                    fig4.add_vline(x=pk["date"], line_dash="dash",
                                   line_color="rgba(251,191,36,0.5)", line_width=1)

            fig4.update_layout(
                title="Reach (peaks highlighted)",
                **get_chart_layout()
            )
            st.plotly_chart(fig4, width="stretch")

            v1, v2 = st.columns(2)
            v1.metric("Avg Daily Reach", f"{int(reach_df['value'].mean()):,}")
            peak_row = reach_df.loc[reach_df["value"].idxmax()]
            v2.metric("Peak Reach Day", peak_row["date"].strftime("%b %d"), delta=f"{int(peak_row['value']):,}")

            # ── Auto-analysis text ───────────────────────────────────────────
            peak_reach_date = peak_row["date"].strftime("%d/%m")
            peak_reach_val  = int(peak_row["value"])
            avg_reach       = int(reach_df["value"].mean())
            _ana_bg2 = "rgba(255,255,255,0.03)" if _dark else "#f8fafc"
            _ana_tc2 = "rgba(255,255,255,0.6)"  if _dark else "#4b5563"
            _ana_vc2 = "#ffffff" if _dark else "#111827"
            st.markdown(
                f'<div style="background:{_ana_bg2};border-left:3px solid rgba(99,102,241,0.6);'
                f'border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:0.5rem 0 0.3rem;'
                f'font-size:0.82rem;color:{_ana_tc2};line-height:1.6;">'
                f'Pic de couverture : <b style="color:#6366f1;">{peak_reach_date}</b> avec '
                f'<b style="color:{_ana_vc2};">{peak_reach_val:,}</b> comptes uniques atteints. '
                f'Moyenne journalière : <b style="color:{_ana_vc2};">{avg_reach:,}</b>.'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("No visibility data available for this period.")

        # ── IMPRESSIONS — dedicated section ──────────────────────────────────
        if not impressions_df.empty:
            _shdr_c2  = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"
            _shdr_brd = "rgba(255,255,255,0.08)"  if _dark else "#e5e7eb"
            st.markdown(
                f'<div style="font-size:0.68rem;color:{_shdr_c2};'
                f'text-transform:uppercase;letter-spacing:0.08em;'
                f'margin:1.4rem 0 0.6rem;border-bottom:1px solid {_shdr_brd};'
                f'padding-bottom:0.4rem;">📢 IMPRESSIONS</div>',
                unsafe_allow_html=True
            )
            fig_imp = go.Figure()
            fig_imp.add_trace(go.Scatter(
                x=impressions_df["date"], y=impressions_df["value"],
                name="Impressions",
                fill="tozeroy",
                line=dict(color="#ec4899", width=2),
                fillcolor="rgba(236,72,153,0.12)",
                mode="lines+markers",
                marker=dict(size=4, color="#ec4899"),
            ))
            imp_layout = {
                **get_chart_layout(),
                "showlegend": False,
                "margin": dict(l=0, r=0, t=10, b=30),
                "height": 220,
            }
            fig_imp.update_layout(**imp_layout)
            st.plotly_chart(fig_imp, width="stretch")

            # total_impressions = KPI value (period_impressions from page_impressions
            # monthly aggregate). Use it here so the stat matches the headline KPI exactly.
            avg_imp_v    = int(impressions_df["value"].mean())
            peak_imp_row = impressions_df.loc[impressions_df["value"].idxmax()]
            peak_imp_d   = peak_imp_row["date"].strftime("%d/%m")
            peak_imp_v   = int(peak_imp_row["value"])

            pi1, pi2, pi3 = st.columns(3)
            pi1.metric("Total Impressions", f"{total_impressions:,}")
            pi2.metric("Pic", peak_imp_row["date"].strftime("%b %d"), delta=f"{peak_imp_v:,}")
            pi3.metric("Moy. journalière", f"{avg_imp_v:,}")

            _ana_bg3 = "rgba(255,255,255,0.03)" if _dark else "#f8fafc"
            _ana_tc3 = "rgba(255,255,255,0.6)"  if _dark else "#4b5563"
            _ana_vc3 = "#ffffff" if _dark else "#111827"
            st.markdown(
                f'<div style="background:{_ana_bg3};border-left:3px solid rgba(236,72,153,0.6);'
                f'border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin:0.5rem 0 0.3rem;'
                f'font-size:0.82rem;color:{_ana_tc3};line-height:1.6;">'
                f'Pic d\'impressions : <b style="color:#ec4899;">{peak_imp_d}</b> avec '
                f'<b style="color:{_ana_vc3};">{peak_imp_v:,}</b> impressions. '
                f'Total sur la période : <b style="color:{_ana_vc3};">{total_impressions:,}</b> '
                f'(moy. {avg_imp_v:,}/jour).'
                f'</div>',
                unsafe_allow_html=True
            )

    # ── TAB 4: Top Content ────────────────────────────────────────────────────
    with tab4:
        if posts:
            render_top3_podium(
                posts,
                sort_key="reach",
                title="TOP #3 PUBLICATIONS PAR VISIBILITÉ",
                view_label="Reach",
            )
            st.divider()
            render_top3_podium(
                posts,
                sort_key="total_interactions",
                title="TOP #3 PUBLICATIONS PAR ENGAGEMENT",
                view_label="Reach",
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
        st.markdown('<div class="section-header">Community Management</div>', unsafe_allow_html=True)
        new_t = msg_stats.get("new_conversations", 0)

        def _cm_kpi(icon, label, value, color=None):
            _bg  = "rgba(255,255,255,0.05)" if _dark else "#ffffff"
            _brd = "none" if _dark else "1px solid #e5e7eb"
            _lc  = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
            _vc  = color if color else ("#ffffff" if _dark else "#111827")
            return (
                f'<div style="background:{_bg};border:{_brd};border-radius:12px;'
                f'padding:0.9rem 1rem;text-align:center;">'
                f'<div style="font-size:0.72rem;color:{_lc};'
                f'margin-bottom:0.25rem;">{icon} {label}</div>'
                f'<div style="font-size:1.35rem;font-weight:800;color:{_vc};'
                f'white-space:nowrap;">{value}</div>'
                f'</div>'
            )

        st.markdown(
            f'<div style="display:grid;grid-template-columns:repeat(1,1fr);gap:0.6rem;margin-bottom:1rem;">'
            f'{_cm_kpi("🆕", "Nouveaux contacts",  f"{new_t:,}", "#4ade80")}'
            f'</div>',
            unsafe_allow_html=True
        )


