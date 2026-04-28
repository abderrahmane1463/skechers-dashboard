"""
views/boost.py — Boost (Ads Performance) dashboard tab.

Data contract
─────────────
All functions accept a `data` dict whose shape mirrors what the
Meta Marketing API (v19.0) would return.  Pass the placeholder
produced by `empty_boost_data()` until the real API integration
is wired up.

TODO: replace `empty_boost_data()` calls in views/facebook.py with
      a call to api/boost.py → fetch_boost_insights(ad_account_id, since, until)
      once the Marketing API access token is available.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from components.charts import CHART_LAYOUT


# ─── Placeholder data structure ───────────────────────────────────────────────
def empty_boost_data() -> dict:
    """
    Returns a zero-filled data structure that matches the shape expected by
    render_boost_tab().  Replace this with real Meta Marketing API data.

    Shape reference (Meta Marketing API fields):
      campaigns[*].insights → impressions, reach, clicks (link_clicks),
                               spend, cpc, ctr, frequency,
                               actions[action_type=purchase].value,
                               cost_per_action_type[action_type=purchase].value
    """
    return {
        # ── Totals across all active campaigns ──────────────────────────────
        # TODO: aggregate from ad_account/insights?fields=impressions,reach,
        #       clicks,spend,cpc,ctr,frequency&date_preset=...
        "totals": {
            "campaigns_count":  0,
            "link_clicks":      0,
            "reach":            0,
            "impressions":      0,
            "cpc":              0.0,   # €
            "ctr":              0.0,   # %
            "spend":            0.0,   # €
            "frequency":        0.0,
        },

        # ── Conversion-objective campaigns only ──────────────────────────────
        # TODO: filter by effective_status=ACTIVE & objective=CONVERSIONS
        "conversions": {
            "campaigns_count":       0,
            "link_clicks":           0,
            "reach":                 0,
            "impressions":           0,
            "cpc":                   0.0,
            "ctr":                   0.0,
            "spend":                 0.0,
            "frequency":             0.0,
            "cost_per_conversion":   0.0,  # cost_per_action_type[purchase]
            "total_conversions":     0,    # actions[purchase]
        },

        # ── Per-campaign detail (used for Top Campaigns chart) ───────────────
        # TODO: /act_{ad_account_id}/campaigns?fields=name,objective,
        #       insights{impressions,reach,clicks,spend,actions,cpc,ctr}
        "campaigns": [
            # {
            #     "name":        "Nom de la campagne",
            #     "objective":   "CONVERSIONS",
            #     "spend":       0.0,
            #     "conversions": 0,
            #     "cpa":         0.0,
            #     "clicks":      0,
            #     "reach":       0,
            # }
        ],
    }


# ─── Internal helpers ──────────────────────────────────────────────────────────
def _fmt_currency(value: float) -> str:
    return f"€{value:,.2f}"


def _fmt_pct(value: float) -> str:
    return f"{value:.2f}%"


def _fmt_int(value: int) -> str:
    return f"{value:,}"


def _kpi_card(icon: str, label: str, value: str, color: str = "#ffffff") -> str:
    return (
        f'<div style="background:rgba(255,255,255,0.05);border-radius:12px;'
        f'padding:0.9rem 1rem;text-align:center;">'
        f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.45);'
        f'margin-bottom:0.25rem;">{icon} {label}</div>'
        f'<div style="font-size:1.3rem;font-weight:800;color:{color};'
        f'white-space:nowrap;">{value}</div>'
        f'</div>'
    )


def _no_data_banner(msg: str = "Aucune donnée publicitaire disponible pour cette période."):
    st.markdown(
        f'<div style="background:rgba(255,165,0,0.08);border:1px solid rgba(255,165,0,0.25);'
        f'border-radius:10px;padding:1rem 1.2rem;color:rgba(255,165,0,0.9);'
        f'font-size:0.85rem;margin:0.5rem 0 1rem;">'
        f'⚠️ {msg}</div>',
        unsafe_allow_html=True,
    )


def _section_header(title: str):
    st.markdown(
        f'<div style="font-size:0.68rem;color:rgba(255,255,255,0.35);'
        f'text-transform:uppercase;letter-spacing:0.08em;'
        f'margin:1.2rem 0 0.6rem;border-bottom:1px solid rgba(255,255,255,0.08);'
        f'padding-bottom:0.4rem;">{title}</div>',
        unsafe_allow_html=True,
    )


# ─── Section renderers ─────────────────────────────────────────────────────────
def _render_global_kpis(totals: dict):
    """Top-level ad account KPI row."""
    _section_header("📊 Performance globale — tous campaigns")

    no_data = totals.get("campaigns_count", 0) == 0

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Campagnes actives",  _fmt_int(totals.get("campaigns_count", 0)))}
  {_kpi_card("🖱️", "Link clicks",        _fmt_int(totals.get("link_clicks", 0)))}
  {_kpi_card("👁️", "Portée (comptes)",   _fmt_int(totals.get("reach", 0)))}
  {_kpi_card("📢", "Impressions",         _fmt_int(totals.get("impressions", 0)))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("💸", "CPC",         _fmt_currency(totals.get("cpc", 0.0)), "#facc15")}
  {_kpi_card("📈", "CTR",         _fmt_pct(totals.get("ctr", 0.0)),      "#4ade80")}
  {_kpi_card("💰", "Dépenses",    _fmt_currency(totals.get("spend", 0.0)), "#f97316")}
  {_kpi_card("🔁", "Fréquence",   f"{totals.get('frequency', 0.0):.2f}x")}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)

    if no_data:
        _no_data_banner(
            "Données Marketing API non connectées. "
            "Connectez votre compte publicitaire pour afficher vos KPIs."
        )


def _render_conversion_campaigns(conv: dict):
    """Conversion-objective campaigns subsection."""
    _section_header("🎯 Campagnes de conversion")

    no_data = conv.get("campaigns_count", 0) == 0

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Nb campagnes conv.",    _fmt_int(conv.get("campaigns_count", 0)))}
  {_kpi_card("🖱️", "Link clicks",           _fmt_int(conv.get("link_clicks", 0)))}
  {_kpi_card("👁️", "Portée",                _fmt_int(conv.get("reach", 0)))}
  {_kpi_card("📢", "Impressions",            _fmt_int(conv.get("impressions", 0)))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("💸", "CPC",                   _fmt_currency(conv.get("cpc", 0.0)),              "#facc15")}
  {_kpi_card("📈", "CTR",                   _fmt_pct(conv.get("ctr", 0.0)),                   "#4ade80")}
  {_kpi_card("💰", "Dépenses",              _fmt_currency(conv.get("spend", 0.0)),             "#f97316")}
  {_kpi_card("🎁", "Coût / conversion",     _fmt_currency(conv.get("cost_per_conversion", 0.0)), "#fb7185")}
  {_kpi_card("✅", "Conversions (achats)", _fmt_int(conv.get("total_conversions", 0)),         "#a78bfa")}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)

    if no_data:
        _no_data_banner("Aucune campagne de conversion détectée pour la période sélectionnée.")


def _render_top_campaigns(campaigns: list[dict]):
    """Top-3 campaigns bar chart + summary table."""
    _section_header("🏆 Top campagnes par conversions")

    if not campaigns:
        _no_data_banner("Aucune campagne à afficher. Les données apparaîtront ici une fois la Meta Marketing API connectée.")
        return

    # Sort by conversions desc, take top 3
    top = sorted(campaigns, key=lambda c: c.get("conversions", 0), reverse=True)[:3]

    names       = [c["name"][:32] + "…" if len(c["name"]) > 32 else c["name"] for c in top]
    conversions = [c.get("conversions", 0) for c in top]
    spends      = [c.get("spend", 0.0)     for c in top]
    cpas        = [c.get("cpa", 0.0)       for c in top]

    bar_colors = ["#6366f1", "#8b5cf6", "#a78bfa"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names,
        y=conversions,
        marker_color=bar_colors[:len(top)],
        text=[f"{v:,}" for v in conversions],
        textposition="outside",
        textfont=dict(color="rgba(255,255,255,0.8)", size=13, family="Inter"),
        hovertemplate="<b>%{x}</b><br>Conversions: %{y:,}<extra></extra>",
    ))
    fig.update_layout(
        **CHART_LAYOUT,
        height=280,
        title=dict(text="Top 3 campagnes — achats / conversions", font=dict(size=13), x=0),
        yaxis=dict(showticklabels=False, gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(tickfont=dict(size=11)),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary mini-table
    col_n, col_c, col_s, col_cpa = st.columns([3, 1, 1, 1])
    col_n.markdown(  "**Campagne**",         unsafe_allow_html=True)
    col_c.markdown(  "**Conversions**",      unsafe_allow_html=True)
    col_s.markdown(  "**Dépenses**",         unsafe_allow_html=True)
    col_cpa.markdown("**CPA**",              unsafe_allow_html=True)

    for c in top:
        col_n, col_c, col_s, col_cpa = st.columns([3, 1, 1, 1])
        col_n.write(c["name"])
        col_c.write(f"{c.get('conversions', 0):,}")
        col_s.write(_fmt_currency(c.get("spend", 0.0)))
        col_cpa.write(_fmt_currency(c.get("cpa", 0.0)))


def _render_insights_panel(totals: dict, conv: dict):
    """Automated interpretation: CTR, CPC efficiency, conversion rate."""
    _section_header("🧠 Analyse automatique")

    ctr   = totals.get("ctr", 0.0)
    cpc   = totals.get("cpc", 0.0)
    cpa   = conv.get("cost_per_conversion", 0.0)
    clicks = totals.get("link_clicks", 0)
    total_conv = conv.get("total_conversions", 0)
    cvr   = round(total_conv / clicks * 100, 2) if clicks else 0.0

    insights: list[tuple[str, str, str]] = []

    # CTR benchmark (Meta average: 0.9–1.5 % for feed ads)
    if ctr == 0:
        insights.append(("⚪", "CTR", "Données non disponibles."))
    elif ctr >= 2.0:
        insights.append(("🟢", "CTR excellent",  f"{_fmt_pct(ctr)} — bien au-dessus de la moyenne (>2 %)."))
    elif ctr >= 1.0:
        insights.append(("🟡", "CTR correct",    f"{_fmt_pct(ctr)} — dans la norme (1–2 %). Optimisation possible."))
    else:
        insights.append(("🔴", "CTR faible",     f"{_fmt_pct(ctr)} — en dessous de 1 %. Revoir les visuels / ciblage."))

    # CPC benchmark
    if cpc == 0:
        insights.append(("⚪", "CPC", "Données non disponibles."))
    elif cpc <= 0.50:
        insights.append(("🟢", "CPC très efficace", f"{_fmt_currency(cpc)} — coût par clic très bas."))
    elif cpc <= 1.50:
        insights.append(("🟡", "CPC modéré",        f"{_fmt_currency(cpc)} — acceptable selon le secteur."))
    else:
        insights.append(("🔴", "CPC élevé",          f"{_fmt_currency(cpc)} — envisager d'affiner le ciblage."))

    # Conversion rate
    if cvr == 0:
        insights.append(("⚪", "Taux de conversion", "Données non disponibles."))
    elif cvr >= 3.0:
        insights.append(("🟢", "Conversion excellente", f"{_fmt_pct(cvr)} — page de destination très performante."))
    elif cvr >= 1.0:
        insights.append(("🟡", "Conversion correcte",   f"{_fmt_pct(cvr)} — marge d'optimisation sur la landing page."))
    else:
        insights.append(("🔴", "Conversion faible",     f"{_fmt_pct(cvr)} — vérifier l'expérience post-clic."))

    # CPA
    if cpa > 0:
        insights.append(("💡", "Coût / achat", f"{_fmt_currency(cpa)} — comparez à la valeur moyenne d'une commande."))

    rows_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:0.6rem;'
        f'background:rgba(255,255,255,0.03);border-radius:8px;'
        f'padding:0.55rem 0.8rem;margin-bottom:0.35rem;">'
        f'<span style="font-size:1rem;line-height:1.4;">{dot}</span>'
        f'<div><span style="font-size:0.78rem;font-weight:700;color:rgba(255,255,255,0.75);">{label}</span>'
        f'<span style="font-size:0.78rem;color:rgba(255,255,255,0.45);"> — {text}</span></div>'
        f'</div>'
        for dot, label, text in insights
    )
    st.markdown(rows_html, unsafe_allow_html=True)


# ─── Public entry point ────────────────────────────────────────────────────────
def render_boost_tab(data: dict | None = None):
    """
    Render the full Boost (Ads Performance) tab.

    Parameters
    ----------
    data : dict
        Output of fetch_boost_insights() (future) or empty_boost_data().
        If None, empty_boost_data() is used automatically.

    TODO: pass real data from api/boost.py once the Marketing API is
          connected:
              from api.boost import fetch_boost_insights
              data = fetch_boost_insights(AD_ACCOUNT_ID, since, until)
    """
    if data is None:
        data = empty_boost_data()

    totals    = data.get("totals",      {})
    conv      = data.get("conversions", {})
    campaigns = data.get("campaigns",   [])

    # Header
    st.markdown(
        '<p style="font-size:1.4rem;font-weight:800;letter-spacing:0.08em;'
        'color:#fff;margin:0 0 0.2rem;">BOOST — ADS PERFORMANCE</p>'
        '<p style="font-size:0.8rem;color:rgba(255,255,255,0.35);margin:0 0 1rem;">'
        'Performances publicitaires payantes · Meta Marketing API</p>',
        unsafe_allow_html=True,
    )

    _render_global_kpis(totals)
    st.divider()
    _render_conversion_campaigns(conv)
    st.divider()
    _render_top_campaigns(campaigns)
    st.divider()
    _render_insights_panel(totals, conv)
