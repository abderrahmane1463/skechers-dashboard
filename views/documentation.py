"""
views/documentation.py — Guide du dashboard Footland.
"""

import streamlit as st


_DOC_CSS = """
<style>
.doc-hero {
    background: linear-gradient(135deg, #161616 0%, #1a0f0a 100%);
    border: 1px solid #262626;
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 32px;
}
.doc-hero h1 {
    font-size: 32px;
    font-weight: 800;
    background: linear-gradient(90deg, #E8420A, #FF6B35);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.doc-hero p { color: #a1a1aa !important; font-size: 15px; }
.doc-section-title {
    font-size: 20px;
    font-weight: 700;
    color: #E8420A !important;
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid #262626;
}
.kpi-table { width: 100%; border-collapse: collapse; }
.kpi-table th {
    text-align: left;
    padding: 10px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #71717a !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #262626;
}
.kpi-table td {
    padding: 10px 14px;
    font-size: 14px;
    color: #e4e4e7 !important;
    border-bottom: 1px solid #1a1a1a;
    vertical-align: top;
}
.kpi-table tr:last-child td { border-bottom: none; }
.kpi-table tr:hover td { background: #1a1a1a; }
.kpi-name { font-weight: 600; white-space: nowrap; }
.kpi-desc { color: #a1a1aa !important; }
</style>
"""


def render_documentation():
    st.markdown(_DOC_CSS, unsafe_allow_html=True)

    st.markdown("""
<div class="doc-hero">
  <h1>📖 Guide du Dashboard</h1>
  <p>Ce guide explique chaque indicateur (KPI) affiché dans le dashboard Footland — ce qu'il mesure, comment il est calculé, et comment l'interpréter.</p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🔵 **Facebook** — Audience, Engagement, Visibilité, Publications, Communauté")
    with col2:
        st.info("📸 **Instagram** — Audience, Engagement, Visibilité, Publications")
    with col3:
        st.info("🚀 **Boost** — Campagnes payantes, Conversions, Démographie, Géographie")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Facebook ──────────────────────────────────────────────────────────────
    st.markdown('<div class="doc-section-title">🔵 Facebook</div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5, t6 = st.tabs(["Vue d'ensemble", "👥 Audience", "💬 Engagement", "📡 Visibilité", "🏆 Top Contenu", "🤝 Communauté"])

    with t1:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">👥 Followers</td><td class="kpi-desc">Nombre total d'abonnés à la page Facebook à la fin de la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">➕ Nouveaux followers</td><td class="kpi-desc">Nouveaux abonnements enregistrés pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">➖ Désabonnements</td><td class="kpi-desc">Personnes ayant arrêté de suivre la page pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📊 Taux d'engagement</td><td class="kpi-desc">Interactions totales ÷ portée totale × 100. Mesure la qualité de l'engagement par rapport à l'audience touchée.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">👁️ Spectateurs (Reach)</td><td class="kpi-desc">Comptes uniques ayant vu au moins une fois un contenu de la page pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📢 Impressions</td><td class="kpi-desc">Nombre total d'affichages (un même compte peut être compté plusieurs fois).</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">🤝 Content Interactions</td><td class="kpi-desc">Interactions directes sur les publications : réactions, commentaires, partages, clics.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📝 Publications</td><td class="kpi-desc">Nombre de posts publiés pendant la période sélectionnée.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">🔥 Total interactions (posts)</td><td class="kpi-desc">Somme des réactions, commentaires et partages sur tous les posts.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des réactions (J'aime, J'adore, Haha, Wow, Triste, Grr) sur les posts.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires laissés sur les posts.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">🔁 Partages</td><td class="kpi-desc">Total des fois où les posts ont été partagés.</td><td>Meta API</td></tr>
</table>""", unsafe_allow_html=True)

    with t2:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">➡️ Net follows</td><td class="kpi-desc">Nouveaux abonnements moins désabonnements. Positif = la page gagne des abonnés.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">↗️ Unfollows</td><td class="kpi-desc">Total des désabonnements. À surveiller si la tendance est à la hausse.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">👤 Followers (Lifetime)</td><td class="kpi-desc">Évolution du total des abonnés jour par jour.</td><td>Meta Insights</td></tr>
</table>""", unsafe_allow_html=True)

    with t3:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">⚡ Total interactions</td><td class="kpi-desc">Somme de toutes les interactions sur la page (réactions, commentaires, partages, clics) pour la période.</td><td>Meta Insights</td></tr>
</table>
<br><p style="color:#a1a1aa;font-size:13px;">Le graphique montre l'évolution des interactions jour par jour pour identifier les pics d'activité.</p>""", unsafe_allow_html=True)

    with t4:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">📏 Avg Daily Reach</td><td class="kpi-desc">Moyenne de comptes uniques touchés par jour. Indicateur de régularité de la diffusion.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">🏔️ Peak Reach Day</td><td class="kpi-desc">Le jour où la portée a été la plus élevée, avec la valeur atteinte.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">📊 Total Impressions</td><td class="kpi-desc">Nombre total d'affichages. Toujours supérieur au Reach car un même compte peut voir le contenu plusieurs fois.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">🎯 Pic</td><td class="kpi-desc">Meilleure journée en impressions sur la période.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">📈 Moy. journalière</td><td class="kpi-desc">Moyenne d'impressions par jour. Utile pour comparer des périodes de longueurs différentes.</td><td>Calculé</td></tr>
</table>""", unsafe_allow_html=True)

    with t5:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Publications les plus performantes, classées par portée et par engagement.</p><br>
<table class="kpi-table">
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td class="kpi-name">Portée</td><td class="kpi-desc">Comptes uniques ayant vu ce post.</td></tr>
  <tr><td class="kpi-name">Impressions</td><td class="kpi-desc">Nombre total d'affichages du post.</td></tr>
  <tr><td class="kpi-name">Réactions / Commentaires / Partages</td><td class="kpi-desc">Interactions directes par type.</td></tr>
</table>""", unsafe_allow_html=True)

    with t6:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">🆕 Nouveaux contacts</td><td class="kpi-desc">Nouvelles conversations initiées en message privé (DM) pendant la période.</td><td>Meta Insights</td></tr>
</table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Instagram ─────────────────────────────────────────────────────────────
    st.markdown('<div class="doc-section-title">📸 Instagram</div>', unsafe_allow_html=True)

    i1, i2, i3, i4, i5 = st.tabs(["Vue d'ensemble", "👥 Audience", "💬 Engagement", "📡 Visibilité", "🏆 Top Contenu"])

    with i1:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">👥 Followers</td><td class="kpi-desc">Nombre total d'abonnés au compte Instagram à ce jour.</td><td>Meta Graph API</td></tr>
  <tr><td class="kpi-name">📈 Net Follower Change</td><td class="kpi-desc">Variation nette des abonnés : nouveaux abonnés moins désabonnements.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📝 Publications</td><td class="kpi-desc">Nombre de posts publiés pendant la période.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">📊 Taux d'engagement</td><td class="kpi-desc">Total interactions ÷ portée totale × 100.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">👁️ Couvertures (Reach)</td><td class="kpi-desc">Comptes uniques ayant vu au moins un post pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📢 Impressions (Posts)</td><td class="kpi-desc">Total d'affichages de tous les posts. Calculé depuis les données individuelles de chaque post.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Posts sauvegardés par des utilisateurs. Indicateur fort d'intérêt pour le contenu.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Somme des réactions, commentaires, partages et enregistrements.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des J'aime sur les posts.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur les posts.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">↗️ Partages</td><td class="kpi-desc">Posts partagés (Stories, messages directs, etc.).</td><td>Meta API (par post)</td></tr>
</table>""", unsafe_allow_html=True)

    with i2:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">👥 Nouveaux followers</td><td class="kpi-desc">Nouveaux abonnés gagnés pendant la période.</td></tr>
  <tr><td class="kpi-name">👤 Followers (Lifetime)</td><td class="kpi-desc">Graphique de l'évolution du total des abonnés.</td></tr>
</table>""", unsafe_allow_html=True)

    with i3:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Likes + commentaires + enregistrements sur la période.</td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des likes sur tous les posts.</td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur tous les posts.</td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Total des sauvegardes. Taux élevé = contenu à forte valeur perçue.</td></tr>
</table>""", unsafe_allow_html=True)

    with i4:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">👁️ Total Reach</td><td class="kpi-desc">Comptes uniques touchés par les posts sur la période.</td></tr>
  <tr><td class="kpi-name">🎯 Pic</td><td class="kpi-desc">Meilleure journée en portée ou impressions.</td></tr>
  <tr><td class="kpi-name">📏 Moy. journalière</td><td class="kpi-desc">Moyenne par jour. Utile pour comparer des périodes de longueurs différentes.</td></tr>
  <tr><td class="kpi-name">📊 Total Impressions</td><td class="kpi-desc">Somme de tous les affichages, calculé depuis les métriques individuelles de chaque post.</td></tr>
</table>""", unsafe_allow_html=True)

    with i5:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Posts les plus performants, classés par impressions et engagement total.</p><br>
<table class="kpi-table">
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td class="kpi-name">Impressions</td><td class="kpi-desc">Nombre d'affichages du post.</td></tr>
  <tr><td class="kpi-name">Reach</td><td class="kpi-desc">Comptes uniques ayant vu le post.</td></tr>
  <tr><td class="kpi-name">Likes / Commentaires / Partages / Enregistrements</td><td class="kpi-desc">Interactions détaillées par type.</td></tr>
</table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Boost ─────────────────────────────────────────────────────────────────
    st.markdown('<div class="doc-section-title">🚀 Boost (Campagnes Payantes)</div>', unsafe_allow_html=True)

    b1, b2, b3, b4 = st.tabs(["📊 Global", "🎯 Conversion", "📋 Toutes les campagnes", "👥 Démographie & Géo"])

    with b1:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Interprétation</th></tr>
  <tr><td class="kpi-name">📁 Total campagnes</td><td class="kpi-desc">Nombre de campagnes actives sur la période.</td><td>—</td></tr>
  <tr><td class="kpi-name">🖱️ Clics sur le lien</td><td class="kpi-desc">Clics sur les liens dans les publicités (CTA, site, etc.).</td><td>Plus c'est élevé, plus les annonces incitent à l'action.</td></tr>
  <tr><td class="kpi-name">👁️ Comptes touchés</td><td class="kpi-desc">Personnes uniques ayant vu au moins une publicité.</td><td>Mesure la portée réelle.</td></tr>
  <tr><td class="kpi-name">📢 Impressions</td><td class="kpi-desc">Total d'affichages des publicités (une même personne peut voir plusieurs fois).</td><td>Toujours ≥ Reach.</td></tr>
  <tr><td class="kpi-name">💸 Coût par clic (CPC)</td><td class="kpi-desc">Budget ÷ nombre de clics. En euros.</td><td>Plus le CPC est bas, meilleure est l'efficacité.</td></tr>
  <tr><td class="kpi-name">📈 CTR</td><td class="kpi-desc">Clics ÷ impressions × 100. Taux de clic sur les publicités.</td><td>Bon CTR FB/IG : entre 1% et 3%.</td></tr>
  <tr><td class="kpi-name">💰 Montant dépensé</td><td class="kpi-desc">Budget total consommé sur la période.</td><td>—</td></tr>
  <tr><td class="kpi-name">🔁 Répétition</td><td class="kpi-desc">Impressions ÷ Reach. Nombre moyen de fois qu'une personne a vu la pub.</td><td>Répétition > 3 = risque de saturation.</td></tr>
</table>""", unsafe_allow_html=True)

    with b2:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Filtre uniquement les campagnes avec un objectif de <strong>conversion</strong> (ventes, achats).</p><br>
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">🎁 Coût par vente</td><td class="kpi-desc">Budget ÷ nombre de conversions. Coût moyen pour générer une vente via les publicités.</td></tr>
  <tr><td class="kpi-name">✅ Commandes (conv.)</td><td class="kpi-desc">Total des conversions (achats, inscriptions) attribuées aux publicités.</td></tr>
</table>""", unsafe_allow_html=True)

    with b3:
        st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Tableau de toutes les campagnes avec leurs métriques. Triable par colonne.</p><br>
<table class="kpi-table">
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td class="kpi-name">Campagne</td><td class="kpi-desc">Nom de la campagne.</td></tr>
  <tr><td class="kpi-name">Objectif</td><td class="kpi-desc">Objectif défini (Conversion, Trafic, Notoriété, etc.).</td></tr>
  <tr><td class="kpi-name">Dépensé (€)</td><td class="kpi-desc">Budget consommé par cette campagne.</td></tr>
  <tr><td class="kpi-name">CTR (%)</td><td class="kpi-desc">Taux de clic de cette campagne.</td></tr>
  <tr><td class="kpi-name">CPC (€)</td><td class="kpi-desc">Coût moyen par clic.</td></tr>
  <tr><td class="kpi-name">Répétition</td><td class="kpi-desc">Fréquence d'affichage moyenne par personne.</td></tr>
  <tr><td class="kpi-name">Commandes</td><td class="kpi-desc">Conversions attribuées à cette campagne.</td></tr>
  <tr><td class="kpi-name">Coût/vente (€)</td><td class="kpi-desc">Coût par conversion pour cette campagne.</td></tr>
</table>""", unsafe_allow_html=True)

    with b4:
        st.markdown("""
<table class="kpi-table">
  <tr><th>Section</th><th>Description</th></tr>
  <tr><td class="kpi-name">👥 Démographie</td><td class="kpi-desc">Répartition Hommes / Femmes par tranche d'âge parmi les personnes touchées. Vérifie que la cible correspond au public visé.</td></tr>
  <tr><td class="kpi-name">🌍 Géographie</td><td class="kpi-desc">Top villes/régions en termes de portée. Montre où les publicités ont le plus diffusé.</td></tr>
  <tr><td class="kpi-name">🧠 Analyse automatique</td><td class="kpi-desc">Évaluation du CTR, CPC et taux de conversion vs benchmarks secteur. Indicateur rouge = performance en dessous de la norme.</td></tr>
</table>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Glossaire & Fréquence ─────────────────────────────────────────────────
    with st.expander("📚 Glossaire — Termes clés"):
        st.markdown("""
| Terme | Définition |
|---|---|
| **Reach (Portée)** | Comptes **uniques** ayant vu un contenu. Chaque personne comptée une seule fois. |
| **Impressions** | Nombre total d'**affichages**. Une même personne peut générer plusieurs impressions. |
| **Engagement** | Toute interaction active : like, commentaire, partage, clic, enregistrement. |
| **Taux d'engagement** | Engagement ÷ Reach × 100. |
| **CTR** | Click-Through Rate. Clics ÷ Impressions × 100. |
| **CPC** | Coût Par Clic. Budget ÷ Clics. |
| **CPA** | Coût Par Acquisition. Budget ÷ Conversions. |
| **Répétition** | Impressions ÷ Reach. Fois moyenne qu'une personne voit une pub. |
| **Conversion** | Action réalisée après avoir vu une pub (achat, inscription, etc.). |
| **Organique** | Contenu diffusé sans budget, via l'algorithme. |
| **Payant (Boost)** | Contenu promu via un budget Meta Ads. |
""")

    with st.expander("🔄 Fréquence de mise à jour"):
        st.markdown("""
| Source | Fréquence |
|---|---|
| **Périodes standard** (7j, 30j, 90j, mois en cours, mois précédent) | Toutes les **6 heures** via GitHub Actions |
| **Plages personnalisées** | En direct au premier accès, puis sauvegardées |
| **Bouton Refresh Data** | Rechargement immédiat depuis Meta API |

> Facebook et Instagram : **Meta Graph API v19.0** — Boost : **Meta Marketing API**
""")
