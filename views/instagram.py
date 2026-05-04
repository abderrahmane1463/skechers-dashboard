import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed

import db
from components.charts import CHART_LAYOUT, series_to_df, safe_sum


# ─── Cached fetchers ──────────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def get_ig_profile(days, start=None, end=None):
    return db.get_ig_profile(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_engagement(days, start=None, end=None):
    return db.get_ig_engagement(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_posts(days, start=None, end=None):
    return db.get_ig_posts(days, start, end)

@st.cache_data(ttl=900, show_spinner=False)
def get_ig_post_totals(days, start=None, end=None):
    return db.get_ig_post_totals(days, start, end)


# ─── Post card helper ─────────────────────────────────────────────────────────
def _render_ig_post_card(post: dict):
    thumbnail = post.get("thumbnail", "")
    text      = post.get("text", "")[:100] or "*(No caption)*"
    date      = post.get("created_time", "")
    reacs     = post.get("reactions", 0)
    comms     = post.get("comments", 0)
    saves     = post.get("saves", 0)
    shares    = post.get("shares", 0)
    total     = post.get("total_interactions", 0)
    imp_val   = post.get("impressions", 0)
    reach_val = post.get("reach", 0)
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

    def _cell(icon, label, value, color="#fff"):
        return (
            f'<div style="background:rgba(255,255,255,0.05);border-radius:8px;padding:0.5rem 0.6rem;">'
            f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">{icon} {label}</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{color};">{value:,}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;margin:0.5rem 0;">'
        f'{_cell("📢", "Impressions", imp_val)}'
        f'{_cell("👁️", "Couverture",  reach_val)}'
        f'{_cell("❤️", "Réactions",   reacs, "#f87171")}'
        f'{_cell("💬", "Commentaires",comms, "#a78bfa")}'
        f'{_cell("🔖", "Enregistrements", saves, "#60a5fa")}'
        f'{_cell("↗️", "Partages",    shares, "#34d399")}'
        f'</div>'
        f'<div style="background:rgba(232,66,10,0.15);border-radius:8px;padding:0.5rem 0.7rem;margin-bottom:0.5rem;">'
        f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);">⚡ Total interactions</div>'
        f'<div style="font-size:1.1rem;font-weight:800;color:#FF6B35;">{total:,}</div>'
        f'</div>'
        f'<a href="{permalink}" target="_blank" style="font-size:0.75rem;color:#6c8ebf;text-decoration:none;">'
        f'🔗 Voir la publication</a><br><br>',
        unsafe_allow_html=True
    )


# ─── Main render function ─────────────────────────────────────────────────────
def render_instagram_dashboard(period_label: str, days: int, start_date, end_date, log_refresh_fn):
    with st.spinner("Loading Instagram data…"):
        fetchers = {
            "profile":     lambda: get_ig_profile(days, start_date, end_date),
            "eng":         lambda: get_ig_engagement(days, start_date, end_date),
            "posts":       lambda: get_ig_posts(days, start_date, end_date),
            "post_totals": lambda: get_ig_post_totals(days, start_date, end_date),
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
        ig_profile   = results["profile"]
        ig_eng       = results["eng"]
        ig_posts     = results["posts"]
        ig_post_totals = results.get("post_totals", {})

    followers          = ig_profile.get("followers_count") or 0
    follower_additions = ig_profile.get("follower_additions", [])
    total_ig_reach     = ig_profile.get("period_reach", 0) or safe_sum(ig_profile.get("reach", []))

    total_ig_impressions = (
        sum(p.get("impressions", 0) for p in ig_posts)
        or ig_post_totals.get("total_impressions")
    )

    total_ig_likes    = sum(p.get("reactions", 0) for p in ig_posts)
    total_ig_comments = sum(p.get("comments", 0) for p in ig_posts)
    total_ig_shares   = sum(p.get("shares", 0) for p in ig_posts)
    total_ig_saves    = sum(p.get("saves", 0) for p in ig_posts)
    total_ig_interactions = total_ig_likes + total_ig_comments + total_ig_shares + total_ig_saves

    if follower_additions:
        ig_new_followers = sum(p["value"] for p in follower_additions)
    else:
        ig_new_followers = None

    ig_eng_rate = round(total_ig_interactions / total_ig_reach * 100, 2) if total_ig_reach else 0.0

    log_refresh_fn(
        "Instagram", period_label, "✅ Data Loaded",
        f"Followers: {followers}, Posts: {len(ig_posts)}, Reach: {total_ig_reach}"
    )

    # ── KPI Grid ──────────────────────────────────────────────────────────────
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

    _new_followers_str = (
        "N/A" if ig_new_followers is None
        else f"+{ig_new_followers:,}" if ig_new_followers >= 0
        else f"{ig_new_followers:,}"
    )

    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_ig_kpi("👥", "Followers",           f"{followers:,}")}
  {_ig_kpi("📈", "Net Follower Change",  _new_followers_str, "#4ade80")}
  {_ig_kpi("📝", "Publications",        str(len(ig_posts)))}
  {_ig_kpi("📊", "Taux d'engagement",   f"{ig_eng_rate}%", "#facc15")}
</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:0.6rem;margin-bottom:0.6rem;">
  {_ig_kpi("👁️", "Couvertures",         f"{total_ig_reach:,}")}
  {_ig_kpi("📢", "Impressions (Posts)",  f"{total_ig_impressions:,}")}
  {_ig_kpi("🔖", "Enregistrements",     f"{total_ig_saves:,}", "#60a5fa")}
</div>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_ig_kpi("🔥", "Total interactions", f"{total_ig_interactions:,}", "#FF6B35")}
  {_ig_kpi("❤️", "Réactions",          f"{total_ig_likes:,}",        "#f87171")}
  {_ig_kpi("💬", "Commentaires",       f"{total_ig_comments:,}",     "#a78bfa")}
  {_ig_kpi("↗️", "Partages",           f"{total_ig_shares:,}",       "#34d399")}
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Audience", "💬 Engagement", "📡 Visibility", "🏆 Top Content"
    ])

    # ── TAB 1: Audience ───────────────────────────────────────────────────────
    with tab1:
        fa_df = series_to_df(follower_additions)

        if not fa_df.empty:
            chart_col, stats_col = st.columns([3, 1])

            with chart_col:
                fig_aud = go.Figure()
                fig_aud.add_trace(go.Scatter(
                    x=fa_df["date"], y=fa_df["value"],
                    name="Followers",
                    line=dict(color="#7EC8E3", width=2.5),
                    fill="tozeroy",
                    fillcolor="rgba(126,200,227,0.08)",
                    mode="lines"
                ))
                fig_aud.update_layout(**{
                    **CHART_LAYOUT,
                    "yaxis": dict(gridcolor="rgba(255,255,255,0.06)", showline=False),
                    "xaxis": dict(
                        gridcolor="rgba(255,255,255,0.06)", showline=False,
                        tickmode="linear", dtick=86400000, tickangle=-45,
                    ),
                    "showlegend": False,
                    "margin": dict(l=0, r=0, t=10, b=30),
                    "height": 280,
                })
                st.plotly_chart(fig_aud, width="stretch")
                st.markdown(
                    '<div style="text-align:center;margin-top:-12px;">'
                    '<span style="display:inline-block;width:28px;height:2px;'
                    'background:#7EC8E3;vertical-align:middle;margin-right:6px;"></span>'
                    '<span style="font-size:0.75rem;color:rgba(255,255,255,0.5);">Followers</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

            with stats_col:
                _nf = _new_followers_str
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.04);border-radius:12px;'
                    f'padding:1.2rem 1rem;display:flex;flex-direction:column;gap:1.2rem;">'
                    f'<div>'
                    f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Nouveaux followers</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:#4ade80;">{_nf}</div>'
                    f'</div>'
                    f'<div>'
                    f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.45);'
                    f'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">Followers (Lifetime)</div>'
                    f'<div style="font-size:1.5rem;font-weight:800;color:#FF6B35;">{followers:,}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            # Daily series unavailable — show static summary card instead
            _net_color  = "#4ade80" if (ig_new_followers or 0) >= 0 else "#f87171"
            _net_arrow  = "▲" if (ig_new_followers or 0) >= 0 else "▼"
            _net_label  = _new_followers_str if ig_new_followers is not None else "—"
            st.markdown(
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:0.8rem;">'

                # Card 1 — current total
                f'<div style="background:rgba(255,255,255,0.05);border-radius:16px;'
                f'padding:1.4rem 1.6rem;text-align:center;">'
                f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);'
                f'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">'
                f'👥 Followers (total actuel)</div>'
                f'<div style="font-size:2.4rem;font-weight:900;color:#7EC8E3;line-height:1;">'
                f'{followers:,}</div>'
                f'</div>'

                # Card 2 — net change
                f'<div style="background:rgba(255,255,255,0.05);border-radius:16px;'
                f'padding:1.4rem 1.6rem;text-align:center;">'
                f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);'
                f'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:0.5rem;">'
                f'➕ Variation nette sur la période</div>'
                f'<div style="font-size:2.4rem;font-weight:900;color:{_net_color};line-height:1;">'
                f'{_net_arrow} {_net_label}</div>'
                f'</div>'

                f'</div>'

                # API limitation note
                f'<div style="background:rgba(255,255,255,0.03);border-left:3px solid rgba(255,255,255,0.15);'
                f'border-radius:0 8px 8px 0;padding:0.55rem 1rem;'
                f'font-size:0.76rem;color:rgba(255,255,255,0.35);line-height:1.5;">'
                f'ℹ️ La série journalière (<code>follower_count</code>) n\'est pas disponible via l\'API '
                f'Meta pour ce type de compte. Les données ci-dessus sont calculées à partir du total '
                f'de la page et de la différence entre la première et la dernière valeur de la période.'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── TAB 2: Engagement ─────────────────────────────────────────────────────
    with tab2:
        # Build daily series from posts
        _ci_d, _likes_d, _comms_d, _saves_d = {}, {}, {}, {}
        for p in ig_posts:
            d = p.get("created_time", "")[:10]
            if not d:
                continue
            _ci_d[d]    = _ci_d.get(d, 0)    + p.get("total_interactions", 0)
            _likes_d[d] = _likes_d.get(d, 0) + p.get("reactions", 0)
            _comms_d[d] = _comms_d.get(d, 0) + p.get("comments", 0)
            _saves_d[d] = _saves_d.get(d, 0) + p.get("saves", 0)

        def _make_series(mapping):
            if not mapping:
                return pd.DataFrame()
            return pd.DataFrame(
                [{"date": pd.Timestamp(k), "value": v}
                 for k, v in sorted(mapping.items())]
            )

        ci_df    = _make_series(_ci_d)
        likes_df = _make_series(_likes_d)
        comms_df = _make_series(_comms_d)
        saves_df = _make_series(_saves_d)

        # Fill full date range with zeros
        if not ci_df.empty and (start_date or days):
            _range_start = pd.Timestamp(start_date) if start_date else pd.Timestamp.now() - pd.Timedelta(days=days)
            _range_end   = pd.Timestamp(end_date)   if end_date   else pd.Timestamp.now()
            _full_range  = pd.DataFrame({"date": pd.date_range(_range_start, _range_end, freq="D")})
            ci_df    = _full_range.merge(ci_df,    on="date", how="left").fillna(0)
            likes_df = _full_range.merge(likes_df, on="date", how="left").fillna(0)
            comms_df = _full_range.merge(comms_df, on="date", how="left").fillna(0)
            saves_df = _full_range.merge(saves_df, on="date", how="left").fillna(0)

        if not ci_df.empty:
            # Dynamic Y-axis ceiling: never clip data, but keep a reasonable minimum
            _y1_max = max(
                float(ci_df["value"].max()) * 1.2 if not ci_df.empty else 0,
                float(likes_df["value"].max()) * 1.2 if not likes_df.empty else 0,
                20_000,
            )
            # Secondary axis ceiling for smaller metrics (comments, saves)
            _y2_max = max(
                float(comms_df["value"].max()) * 1.5 if not comms_df.empty else 0,
                float(saves_df["value"].max()) * 1.5 if not saves_df.empty else 0,
                500,
            )

            fig_eng = go.Figure()
            # ── Primary axis (left): Total interactions + Réactions ──────────
            fig_eng.add_trace(go.Scatter(
                x=ci_df["date"], y=ci_df["value"],
                name="Total interactions",
                line=dict(color="#FF6B35", width=3), mode="lines",
                yaxis="y1",
            ))
            fig_eng.add_trace(go.Scatter(
                x=likes_df["date"], y=likes_df["value"],
                name="Réactions",
                line=dict(color="#f87171", width=2), mode="lines",
                yaxis="y1",
            ))
            # ── Secondary axis (right): Commentaires + Enregistrements ───────
            fig_eng.add_trace(go.Scatter(
                x=comms_df["date"], y=comms_df["value"],
                name="Commentaires (→)",
                line=dict(color="#a78bfa", width=2, dash="dot"), mode="lines",
                yaxis="y2",
            ))
            fig_eng.add_trace(go.Scatter(
                x=saves_df["date"], y=saves_df["value"],
                name="Enregistrements (→)",
                line=dict(color="#60a5fa", width=2, dash="dot"), mode="lines",
                yaxis="y2",
            ))
            fig_eng.update_layout(**{
                **CHART_LAYOUT,
                "yaxis": dict(
                    gridcolor="rgba(255,255,255,0.06)", showline=False,
                    tickformat=",", range=[0, _y1_max],
                    title=dict(text="Interactions", font=dict(size=10, color="rgba(255,255,255,0.3)")),
                ),
                "yaxis2": dict(
                    overlaying="y", side="right",
                    gridcolor="rgba(255,255,255,0)", showline=False,
                    tickformat=",", range=[0, _y2_max],
                    title=dict(text="Commentaires / Enreg.", font=dict(size=10, color="rgba(255,255,255,0.3)")),
                ),
                "xaxis": dict(
                    gridcolor="rgba(255,255,255,0.06)", showline=False,
                    tickmode="array",
                    tickvals=[ci_df["date"].iloc[i]
                              for i in range(0, len(ci_df), max(len(ci_df)//6, 1))][:7],
                    tickangle=0,
                ),
                "showlegend": True,
                "legend": dict(
                    orientation="h", yanchor="bottom", y=-0.28,
                    xanchor="center", x=0.5,
                    font=dict(size=11, color="rgba(255,255,255,0.6)"),
                    bgcolor="rgba(0,0,0,0)",
                ),
                "margin": dict(l=0, r=40, t=10, b=70),
                "height": 320,
            })
            st.plotly_chart(fig_eng, width="stretch")

            ei1, ei2, ei3, ei4 = st.columns(4)
            ei1.metric("Total interactions", f"{total_ig_interactions:,}")
            ei2.metric("Réactions",          f"{total_ig_likes:,}")
            ei3.metric("Commentaires",       f"{total_ig_comments:,}")
            ei4.metric("Enregistrements",    f"{total_ig_saves:,}")
        else:
            st.info("No engagement data available for this period.")

    # ── TAB 3: Visibility ─────────────────────────────────────────────────────
    with tab3:
        reach_df       = series_to_df(ig_profile.get("reach", []))
        impressions_df = series_to_df(ig_profile.get("impressions", []))

        # ── Fallbacks: build daily series from per-post data when account-level
        #    API series are blocked/empty. Posts are grouped by publication date.
        def _posts_daily(metric: str) -> pd.DataFrame:
            """Aggregate per-post metric by date → DataFrame with date/value columns."""
            _d: dict = {}
            for p in ig_posts:
                _date = p.get("created_time", "")[:10]
                if _date:
                    _d[_date] = _d.get(_date, 0) + p.get(metric, 0)
            if not _d:
                return pd.DataFrame()
            return pd.DataFrame(
                [{"date": pd.Timestamp(k), "value": v} for k, v in sorted(_d.items())]
            )

        _reach_from_posts       = False
        _impressions_from_posts = False

        if reach_df.empty and ig_posts:
            reach_df = _posts_daily("reach")
            _reach_from_posts = not reach_df.empty

        if impressions_df.empty and ig_posts:
            impressions_df = _posts_daily("impressions")
            _impressions_from_posts = not impressions_df.empty

        # ── Reach chart ──
        if not reach_df.empty:
            _reach_src = (
                ' <span style="font-size:0.62rem;color:rgba(255,165,0,0.7);'
                'font-weight:400;letter-spacing:0;">(estimé — agrégé depuis les publications)</span>'
                if _reach_from_posts else ""
            )
            st.markdown(
                f'<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
                f'text-transform:uppercase;letter-spacing:0.08em;'
                f'margin:0 0 0.6rem;border-bottom:1px solid rgba(255,255,255,0.08);'
                f'padding-bottom:0.4rem;">👁️ COUVERTURES (REACH){_reach_src}</div>',
                unsafe_allow_html=True
            )
            fig_reach = go.Figure()
            fig_reach.add_trace(go.Scatter(
                x=reach_df["date"], y=reach_df["value"],
                name="Reach", fill="tozeroy",
                line=dict(color="#6366f1", width=2),
                fillcolor="rgba(99,102,241,0.15)",
                mode="lines+markers",
                marker=dict(size=4, color="#6366f1"),
            ))
            fig_reach.update_layout(**{
                **CHART_LAYOUT,
                "showlegend": False,
                "margin": dict(l=0, r=0, t=10, b=30),
                "height": 220,
            })
            st.plotly_chart(fig_reach, width="stretch")

            r1, r2, r3 = st.columns(3)
            r1.metric("Total Reach",       f"{total_ig_reach:,}")
            _peak_r = reach_df.loc[reach_df["value"].idxmax()]
            r2.metric("Pic", _peak_r["date"].strftime("%b %d"), delta=f"{int(_peak_r['value']):,}")
            r3.metric("Moy. journalière",  f"{int(reach_df['value'].mean()):,}")

        # ── Impressions chart ──
        if not impressions_df.empty:
            _imp_src = (
                ' <span style="font-size:0.62rem;color:rgba(255,165,0,0.7);'
                'font-weight:400;letter-spacing:0;">(estimé — agrégé depuis les publications)</span>'
                if _impressions_from_posts else ""
            )
            st.markdown(
                f'<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
                f'text-transform:uppercase;letter-spacing:0.08em;'
                f'margin:1.4rem 0 0.6rem;border-bottom:1px solid rgba(255,255,255,0.08);'
                f'padding-bottom:0.4rem;">📢 IMPRESSIONS *{_imp_src}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                '<div style="background:rgba(99,102,241,0.07);border-left:3px solid rgba(99,102,241,0.5);'
                'border-radius:0 8px 8px 0;padding:0.45rem 0.85rem;margin-bottom:0.7rem;'
                'font-size:0.76rem;color:rgba(255,255,255,0.45);line-height:1.5;">'
                '* Les impressions des <b style="color:rgba(255,255,255,0.6);">Stories passées</b> '
                'ne sont pas disponibles via l\'API Meta après 24h — ce graphique couvre '
                'uniquement le feed &amp; les Reels.'
                '</div>',
                unsafe_allow_html=True,
            )
            fig_imp = go.Figure()
            fig_imp.add_trace(go.Scatter(
                x=impressions_df["date"], y=impressions_df["value"],
                name="Impressions", fill="tozeroy",
                line=dict(color="#ec4899", width=2),
                fillcolor="rgba(236,72,153,0.12)",
                mode="lines+markers",
                marker=dict(size=4, color="#ec4899"),
            ))
            fig_imp.update_layout(**{
                **CHART_LAYOUT,
                "showlegend": False,
                "margin": dict(l=0, r=0, t=10, b=30),
                "height": 220,
            })
            st.plotly_chart(fig_imp, width="stretch")

            _total_imp_v = int(impressions_df["value"].sum())
            _peak_imp    = impressions_df.loc[impressions_df["value"].idxmax()]
            i1, i2, i3  = st.columns(3)
            i1.metric("Total Impressions", f"{_total_imp_v:,}")
            i2.metric("Pic", _peak_imp["date"].strftime("%b %d"), delta=f"{int(_peak_imp['value']):,}")
            i3.metric("Moy. journalière",  f"{int(impressions_df['value'].mean()):,}")

        if reach_df.empty and impressions_df.empty:
            st.info("No visibility data available for this period.")

    # ── TAB 4: Top Content ────────────────────────────────────────────────────
    with tab4:
        if ig_posts:
            # Top by visibility
            st.markdown(
                '<div style="text-align:center;font-size:1.1rem;font-weight:700;'
                'letter-spacing:0.1em;color:rgba(255,255,255,0.6);margin-bottom:1.2rem;">'
                '🏆 TOP PUBLICATIONS PAR VISIBILITÉ</div>',
                unsafe_allow_html=True
            )
            vis_sorted = sorted(ig_posts, key=lambda p: p.get("impressions", 0), reverse=True)[:6]
            vis_cols   = st.columns(3)
            for idx, post in enumerate(vis_sorted):
                with vis_cols[idx % 3]:
                    _render_ig_post_card(post)

            st.divider()

            # Top by engagement
            st.markdown(
                '<div style="text-align:center;font-size:1.1rem;font-weight:700;'
                'letter-spacing:0.1em;color:rgba(255,255,255,0.6);margin-bottom:1.2rem;">'
                '⚡ TOP PUBLICATIONS PAR ENGAGEMENT</div>',
                unsafe_allow_html=True
            )
            eng_sorted = sorted(ig_posts, key=lambda p: p.get("total_interactions", 0), reverse=True)[:6]
            eng_cols   = st.columns(3)
            for idx, post in enumerate(eng_sorted):
                with eng_cols[idx % 3]:
                    _render_ig_post_card(post)
        else:
            st.info("No post data available.")
