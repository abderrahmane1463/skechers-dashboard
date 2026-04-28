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

import streamlit as st


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
    _section_header("📊 STATISTIQUES DU BOOST")

    no_data = totals.get("campaigns_count", 0) == 0

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Total des campagnes", _fmt_int(totals.get("campaigns_count", 0)))}
  {_kpi_card("🖱️", "Clics sur le lien",  _fmt_int(totals.get("link_clicks", 0)))}
  {_kpi_card("👁️", "Comptes touchés",    _fmt_int(totals.get("reach", 0)))}
  {_kpi_card("📢", "Impressions",         _fmt_int(totals.get("impressions", 0)))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:1rem;">
  {_kpi_card("💸", "Coût par clic",    _fmt_currency(totals.get("cpc", 0.0)),   "#facc15")}
  {_kpi_card("📈", "CTR",              _fmt_pct(totals.get("ctr", 0.0)),         "#4ade80")}
  {_kpi_card("💰", "Montant dépensé",  _fmt_currency(totals.get("spend", 0.0)), "#f97316")}
  {_kpi_card("🔁", "Répétition",       f"{totals.get('frequency', 0.0):.2f}x")}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)

    if no_data:
        _no_data_banner(
            "Données Marketing API non connectées. "
            "Connectez votre compte publicitaire pour afficher vos KPIs."
        )


def _render_conversion_campaigns(conv: dict):
    """Conversion-objective campaigns subsection."""
    _section_header("🎯 AVEC L'OBJECTIF CONVERSION")

    no_data = conv.get("campaigns_count", 0) == 0

    row1 = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("📁", "Campagnes",       _fmt_int(conv.get("campaigns_count", 0)))}
  {_kpi_card("🖱️", "Clics sur le lien", _fmt_int(conv.get("link_clicks", 0)))}
  {_kpi_card("👁️", "Comptes touchés",   _fmt_int(conv.get("reach", 0)))}
  {_kpi_card("📢", "Impressions",        _fmt_int(conv.get("impressions", 0)))}
</div>"""

    row2 = f"""
<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:0.6rem;margin-bottom:0.5rem;">
  {_kpi_card("💸", "Coût par clic",   _fmt_currency(conv.get("cpc", 0.0)),                  "#facc15")}
  {_kpi_card("📈", "CTR",             _fmt_pct(conv.get("ctr", 0.0)),                        "#4ade80")}
  {_kpi_card("💰", "Montant dépensé", _fmt_currency(conv.get("spend", 0.0)),                 "#f97316")}
  {_kpi_card("🎁", "Coût par vente",  _fmt_currency(conv.get("cost_per_conversion", 0.0)),   "#fb7185")}
  {_kpi_card("✅", "Commandes",       _fmt_int(conv.get("total_conversions", 0)),             "#a78bfa")}
</div>"""

    st.markdown(row1 + row2, unsafe_allow_html=True)

    if no_data:
        _no_data_banner("Aucune campagne de conversion détectée pour la période sélectionnée.")


def _render_top_campaigns(campaigns: list[dict]):
    """Top-3 campaigns podium cards — mirrors the report's slide 39 layout."""
    _section_header("🏆 TOP #3 CAMPAGNES PAR VENTES")

    if not campaigns:
        _no_data_banner("Aucune campagne à afficher.")
        return

    # Sort by commandes (conversions) desc, take top 3
    top = sorted(campaigns, key=lambda c: c.get("conversions", 0), reverse=True)[:3]

    # Fall back to spend ranking when no conversions are recorded
    use_commandes = any(c.get("conversions", 0) > 0 for c in top)
    if not use_commandes:
        top = sorted(campaigns, key=lambda c: c.get("spend", 0.0), reverse=True)[:3]

    # Pad to always have 3 slots
    while len(top) < 3:
        top.append({"name": "—", "conversions": 0, "spend": 0.0, "cpa": 0.0})

    # Podium style: #1 gold, #2 silver, #3 bronze
    _ranks = [
        ("#1", "#FFD700", "rgba(255,215,0,0.12)",  "rgba(255,215,0,0.35)"),   # gold
        ("#2", "#C0C0C0", "rgba(192,192,192,0.10)", "rgba(192,192,192,0.30)"), # silver
        ("#3", "#CD7F32", "rgba(205,127,50,0.10)",  "rgba(205,127,50,0.30)"),  # bronze
    ]

    cards_html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:0.5rem 0 1rem;">'

    for i, c in enumerate(top):
        rank_label, rank_color, bg_color, border_color = _ranks[i]
        name = c["name"]
        # Truncate long names to two lines visually
        display_name = name if len(name) <= 40 else name[:38] + "…"

        if use_commandes:
            metric_value = f"{c.get('conversions', 0):,}"
            metric_label = "commandes"
        else:
            metric_value = _fmt_currency(c.get("spend", 0.0))
            metric_label = "dépensé"

        spend_str = _fmt_currency(c.get("spend", 0.0))
        cpa_str   = _fmt_currency(c.get("cpa", 0.0))

        cards_html += f"""
<div style="background:{bg_color};border:1px solid {border_color};border-radius:14px;
            padding:1.2rem 1rem;text-align:center;position:relative;display:flex;
            flex-direction:column;align-items:center;gap:0.4rem;">
  <!-- Rank badge -->
  <div style="font-size:1.6rem;font-weight:900;color:{rank_color};
              line-height:1;margin-bottom:0.2rem;">{rank_label}</div>
  <!-- Campaign name -->
  <div style="font-size:0.78rem;color:rgba(255,255,255,0.75);font-weight:600;
              line-height:1.35;min-height:2.7rem;display:flex;align-items:center;
              justify-content:center;">{display_name}</div>
  <!-- Big metric number -->
  <div style="font-size:2rem;font-weight:900;color:{rank_color};
              line-height:1.1;margin:0.3rem 0 0.1rem;">{metric_value}</div>
  <div style="font-size:0.7rem;color:rgba(255,255,255,0.4);
              text-transform:uppercase;letter-spacing:0.06em;">{metric_label}</div>
  <!-- Sub-details -->
  <div style="margin-top:0.5rem;width:100%;border-top:1px solid rgba(255,255,255,0.08);
              padding-top:0.5rem;display:flex;justify-content:space-around;">
    <div style="text-align:center;">
      <div style="font-size:0.68rem;color:rgba(255,255,255,0.35);">Dépensé</div>
      <div style="font-size:0.82rem;font-weight:700;color:rgba(255,255,255,0.7);">{spend_str}</div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.68rem;color:rgba(255,255,255,0.35);">Coût / vente</div>
      <div style="font-size:0.82rem;font-weight:700;color:rgba(255,255,255,0.7);">{cpa_str}</div>
    </div>
  </div>
</div>"""

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


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
        insights.append(("⚪", "Coût par clic", "Données non disponibles."))
    elif cpc <= 0.50:
        insights.append(("🟢", "Coût par clic très efficace", f"{_fmt_currency(cpc)} — coût par clic très bas."))
    elif cpc <= 1.50:
        insights.append(("🟡", "Coût par clic modéré",        f"{_fmt_currency(cpc)} — acceptable selon le secteur."))
    else:
        insights.append(("🔴", "Coût par clic élevé",          f"{_fmt_currency(cpc)} — envisager d'affiner le ciblage."))

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
        insights.append(("💡", "Coût par vente", f"{_fmt_currency(cpa)} — comparez à la valeur moyenne d'une commande."))

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
