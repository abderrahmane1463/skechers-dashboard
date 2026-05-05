import streamlit as st
import pandas as pd

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


# ─── TOP-3 PODIUM ─────────────────────────────────────────────────────────────
def _fmt_big(n: int) -> str:
    """Format large numbers like the report: 2.6M, 966.9K, 5."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def render_top3_podium(
    posts: list,
    sort_key: str,
    title: str,
    view_label: str = "Vues",
    metrics: list = None,
) -> None:
    """
    Render a 3-card podium matching the report's slide layout.

    Podium order: #2 (left)  |  #1 (centre)  |  #3 (right)

    Parameters
    ----------
    posts      : list of post dicts
    sort_key   : field to rank by (e.g. "reach" or "total_interactions")
    title      : section header text
    view_label : label for the first metric when using default Facebook layout
    metrics    : optional list of (icon, label, field) tuples to override the
                 default metrics grid. e.g. [("❤️", "Réactions", "reactions")]
    """
    _dark = st.session_state.get("theme", "dark") == "dark"
    _hdr_color  = "rgba(255,255,255,0.35)" if _dark else "#9ca3af"
    _hdr_border = "rgba(255,255,255,0.08)" if _dark else "#e5e7eb"

    # Section header
    st.markdown(
        f'<div style="font-size:0.68rem;color:{_hdr_color};'
        f'text-transform:uppercase;letter-spacing:0.08em;'
        f'margin:1.2rem 0 0.8rem;border-bottom:1px solid {_hdr_border};'
        f'padding-bottom:0.4rem;">🏆 {title}</div>',
        unsafe_allow_html=True,
    )

    if not posts:
        st.markdown(
            '<div style="background:rgba(255,165,0,0.08);border:1px solid rgba(255,165,0,0.25);'
            'border-radius:10px;padding:1rem 1.2rem;color:rgba(255,165,0,0.9);font-size:0.85rem;">'
            '⚠️ Aucune publication disponible pour cette période.</div>',
            unsafe_allow_html=True,
        )
        return

    ranked = sorted(posts, key=lambda p: p.get(sort_key, 0), reverse=True)[:3]
    while len(ranked) < 3:
        ranked.append(None)

    # Podium visual order: slot 0 = #2, slot 1 = #1, slot 2 = #3
    slots = [ranked[1], ranked[0], ranked[2]]
    ranks = ["#2", "#1", "#3"]
    rank_colors  = ["#C0C0C0", "#FFD700", "#CD7F32"]
    rank_borders = ["rgba(192,192,192,0.35)", "rgba(255,215,0,0.45)", "rgba(205,127,50,0.30)"]
    rank_bg      = ["rgba(192,192,192,0.07)", "rgba(255,215,0,0.10)", "rgba(205,127,50,0.07)"]

    cols = st.columns(3)
    for col, post, rank, color, border, bg in zip(
        cols, slots, ranks, rank_colors, rank_borders, rank_bg
    ):
        with col:
            _empty_tc = "rgba(255,255,255,0.2)" if _dark else "#d1d5db"
            if post is None:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {border};border-radius:14px;'
                    f'padding:1rem;text-align:center;color:{_empty_tc};font-size:0.8rem;">'
                    f'Données insuffisantes</div>',
                    unsafe_allow_html=True,
                )
                continue

            thumb = post.get("thumbnail", "")
            caption = post.get("text", "") or ""
            display_caption = (caption[:45] + "…") if len(caption) > 45 else caption
            date = post.get("created_time", "")
            post_id  = post.get("id", "")
            post_url = (
                post.get("permalink")
                or (f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else "#")
            )

            # ── Resolve metrics ────────────────────────────────────────────────
            _metrics = metrics or [
                ("👁️", view_label,  "reach"),
                ("❤️", "",          "reactions"),
                ("💬", "",          "comments"),
                ("🔁", "",          "shares"),
                ("🖱️", "Clics",     "clicks"),
                ("⚡", "Total",     "total_interactions"),
            ]
            _metric_lc = "rgba(255,255,255,0.65)" if _dark else "#6b7280"
            _metric_vc = "rgba(255,255,255,0.9)"  if _dark else "#111827"
            metrics_html = "".join(
                f'<div style="font-size:0.75rem;color:{_metric_lc};">'
                f'{icon} <b style="color:{_metric_vc};">{_fmt_big(post.get(field, 0))}</b>'
                f'{" " + label if label else ""}</div>'
                for icon, label, field in _metrics
            )

            # ── Thumbnail ──────────────────────────────────────────────────────
            if thumb:
                st.markdown(
                    f'<div style="border-radius:12px 12px 0 0;overflow:hidden;'
                    f'border:2px solid {border};border-bottom:none;">'
                    f'<img src="{thumb}" style="width:100%;aspect-ratio:1/1;'
                    f'object-fit:cover;display:block;" /></div>',
                    unsafe_allow_html=True,
                )
            else:
                _no_img_bg = "rgba(255,255,255,0.04)" if _dark else "#f3f4f6"
                _no_img_tc = "rgba(255,255,255,0.2)"  if _dark else "#d1d5db"
                st.markdown(
                    f'<div style="border-radius:12px 12px 0 0;background:{_no_img_bg};'
                    f'border:2px solid {border};border-bottom:none;aspect-ratio:1/1;'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'color:{_no_img_tc};font-size:2rem;">📷</div>',
                    unsafe_allow_html=True,
                )

            _caption_c = "rgba(255,255,255,0.8)" if _dark else "#111827"
            _date_c    = "rgba(255,255,255,0.4)"  if _dark else "#9ca3af"
            _link_c    = "rgba(255,255,255,0.45)" if _dark else "#6b7280"
            _link_brd  = "rgba(255,255,255,0.15)" if _dark else "#d1d5db"

            # ── Card body ──────────────────────────────────────────────────────
            st.markdown(
                f'<div style="background:{bg};border:2px solid {border};border-top:none;'
                f'border-radius:0 0 14px 14px;padding:0.75rem 0.85rem 0.85rem;">'

                # Caption
                f'<div style="font-size:0.78rem;color:{_caption_c};'
                f'font-weight:600;line-height:1.35;min-height:2.2rem;">{display_caption or "—"}</div>'

                # Date
                f'<div style="font-size:0.68rem;color:{_date_c};'
                f'margin:0.3rem 0 0.6rem;">📅 {date}</div>'

                # Metrics row
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.3rem 0.5rem;'
                f'margin-bottom:0.75rem;">'
                + metrics_html +
                f'</div>'

                # Rank badge
                f'<div style="text-align:center;font-size:1.5rem;font-weight:900;'
                f'color:{color};letter-spacing:0.04em;">{rank}</div>'

                # Post link
                f'<div style="text-align:center;margin-top:0.6rem;">'
                f'<a href="{post_url}" target="_blank" style="font-size:0.72rem;'
                f'color:{_link_c};text-decoration:none;'
                f'border:1px solid {_link_brd};border-radius:6px;'
                f'padding:3px 10px;transition:all 0.2s;">'
                f'Voir le post →</a></div>'

                f'</div>',
                unsafe_allow_html=True,
            )
