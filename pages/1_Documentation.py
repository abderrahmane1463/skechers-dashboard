"""
pages/1_Documentation.py — Guide d'utilisation du dashboard Footland.
"""

import streamlit as st

st.set_page_config(
    page_title="Documentation — Footland",
    page_icon="📖",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #0a0a0a !important; color: #ffffff !important;
}
[data-testid="stSidebar"] { background: #111111 !important; border-right: 1px solid #222222 !important; }
[data-testid="stSidebar"] * { color: #eeeeee !important; }
p, span, li, label, h1, h2, h3, h4 { color: #ffffff !important; }
small { color: #71717a !important; }
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
.section-card {
    background: #161616;
    border: 1px solid #262626;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
}
.section-title {
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
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
}
.badge-fb  { background: rgba(24,119,242,0.15); color: #4a90e2 !important; }
.badge-ig  { background: rgba(232,66,10,0.15);  color: #E8420A !important; }
.badge-bst { background: rgba(52,199,89,0.15);  color: #34c759 !important; }
.tab-label {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    background: #262626;
    color: #a1a1aa !important;
    margin-right: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="doc-hero">
  <h1>📖 Guide du Dashboard</h1>
  <p>Ce guide explique chaque indicateur (KPI) affiché dans le dashboard Footland — ce qu'il mesure, comment il est calculé, et comment l'interpréter.</p>
</div>
""", unsafe_allow_html=True)

# ── Navigation rapide ─────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.info("🔵 **Facebook** — Audience, Engagement, Visibilité, Publications, Communauté")
with col2:
    st.info("📸 **Instagram** — Audience, Engagement, Visibilité, Publications")
with col3:
    st.info("🚀 **Boost** — Campagnes payantes, Conversions, Démographie, Géographie")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔵 Facebook</div>', unsafe_allow_html=True)

tab_overview, tab_audience, tab_engagement, tab_visibility, tab_content, tab_community = st.tabs([
    "Vue d'ensemble", "👥 Audience", "💬 Engagement", "📡 Visibilité", "🏆 Top Contenu", "🤝 Communauté"
])

with tab_overview:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">👥 Followers</td><td class="kpi-desc">Nombre total d'abonnés à la page Facebook à la fin de la période sélectionnée.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">➕ Nouveaux followers</td><td class="kpi-desc">Nombre de nouveaux abonnements enregistrés pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">➖ Désabonnements</td><td class="kpi-desc">Nombre de personnes qui ont arrêté de suivre la page pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📊 Taux d'engagement</td><td class="kpi-desc">Interactions totales divisées par la portée totale × 100. Mesure la qualité de l'engagement par rapport à l'audience touchée.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">👁️ Spectateurs (Reach)</td><td class="kpi-desc">Nombre de comptes uniques qui ont vu au moins une fois un contenu de la page pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📢 Impressions</td><td class="kpi-desc">Nombre total d'affichages du contenu (un même compte peut être compté plusieurs fois).</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">🤝 Content Interactions</td><td class="kpi-desc">Toutes les interactions directes sur les publications : réactions, commentaires, partages, clics.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📝 Publications</td><td class="kpi-desc">Nombre de posts publiés pendant la période sélectionnée.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Somme des réactions, commentaires et partages sur tous les posts de la période.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des réactions (J'aime, J'adore, Haha, Wow, Triste, Grr) sur les posts.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires laissés sur les posts de la période.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">🔁 Partages</td><td class="kpi-desc">Total des fois où les posts ont été partagés par des utilisateurs.</td><td>Meta API</td></tr>
</table>
""", unsafe_allow_html=True)

with tab_audience:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">➡️ Net follows</td><td class="kpi-desc">Différence entre les nouveaux abonnements et les désabonnements. Un nombre positif signifie que la page gagne des abonnés net.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">↗️ Unfollows</td><td class="kpi-desc">Nombre total de désabonnements pendant la période. À surveiller si la tendance est à la hausse.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">👤 Followers (Lifetime)</td><td class="kpi-desc">Évolution du total des abonnés jour par jour sous forme de graphique.</td><td>Meta Insights</td></tr>
</table>
""", unsafe_allow_html=True)

with tab_engagement:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">⚡ Total interactions</td><td class="kpi-desc">Somme de toutes les interactions sur la page (réactions, commentaires, partages, clics sur les liens) pour la période. Reflète l'activité globale générée.</td><td>Meta Insights</td></tr>
</table>
<br>
<p style="color:#a1a1aa;font-size:13px;">Le graphique montre l'évolution des interactions jour par jour pour identifier les pics d'activité.</p>
""", unsafe_allow_html=True)

with tab_visibility:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">📏 Avg Daily Reach</td><td class="kpi-desc">Moyenne de comptes uniques touchés par jour sur la période. Indicateur de régularité de la diffusion.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">🏔️ Peak Reach Day</td><td class="kpi-desc">Le jour où la portée a été la plus élevée de la période, avec la valeur atteinte ce jour-là.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">📊 Total Impressions</td><td class="kpi-desc">Nombre total d'affichages sur toute la période. Toujours supérieur au Reach car un même compte peut voir le contenu plusieurs fois.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">🎯 Pic</td><td class="kpi-desc">Meilleure journée en termes d'impressions sur la période sélectionnée.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">📈 Moy. journalière</td><td class="kpi-desc">Moyenne d'impressions par jour. Utile pour comparer des périodes de longueurs différentes.</td><td>Calculé</td></tr>
</table>
""", unsafe_allow_html=True)

with tab_content:
    st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Cet onglet affiche les publications les plus performantes de la période, classées par portée et par engagement.</p>
<br>
<table class="kpi-table">
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td class="kpi-name">Portée</td><td class="kpi-desc">Nombre de comptes uniques ayant vu ce post.</td></tr>
  <tr><td class="kpi-name">Impressions</td><td class="kpi-desc">Nombre total d'affichages du post.</td></tr>
  <tr><td class="kpi-name">Réactions / Commentaires / Partages</td><td class="kpi-desc">Interactions directes sur le post.</td></tr>
</table>
""", unsafe_allow_html=True)

with tab_community:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">🆕 Nouveaux contacts</td><td class="kpi-desc">Nombre de nouvelles conversations initiées en message privé (DM) pendant la période.</td><td>Meta Insights</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSTAGRAM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📸 Instagram</div>', unsafe_allow_html=True)

ig_overview, ig_audience, ig_engagement, ig_visibility, ig_content = st.tabs([
    "Vue d'ensemble", "👥 Audience", "💬 Engagement", "📡 Visibilité", "🏆 Top Contenu"
])

with ig_overview:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Source</th></tr>
  <tr><td class="kpi-name">👥 Followers</td><td class="kpi-desc">Nombre total d'abonnés au compte Instagram à ce jour.</td><td>Meta Graph API</td></tr>
  <tr><td class="kpi-name">📈 Net Follower Change</td><td class="kpi-desc">Variation nette des abonnés sur la période : nouveaux abonnés moins désabonnements.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📝 Publications</td><td class="kpi-desc">Nombre de posts publiés pendant la période sélectionnée.</td><td>Meta API</td></tr>
  <tr><td class="kpi-name">📊 Taux d'engagement</td><td class="kpi-desc">Total interactions ÷ portée totale × 100. Mesure à quel point l'audience réagit au contenu.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">👁️ Couvertures (Reach)</td><td class="kpi-desc">Nombre de comptes uniques ayant vu au moins un post pendant la période.</td><td>Meta Insights</td></tr>
  <tr><td class="kpi-name">📢 Impressions (Posts)</td><td class="kpi-desc">Nombre total d'affichages de tous les posts. Calculé à partir des données individuelles de chaque post.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Nombre de fois où les posts ont été sauvegardés par des utilisateurs. Indicateur fort d'intérêt pour le contenu.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Somme des réactions, commentaires, partages et enregistrements sur tous les posts.</td><td>Calculé</td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des "J'aime" reçus sur les posts de la période.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur les posts de la période.</td><td>Meta API (par post)</td></tr>
  <tr><td class="kpi-name">↗️ Partages</td><td class="kpi-desc">Nombre de fois où les posts ont été partagés (Stories, messages directs, etc.).</td><td>Meta API (par post)</td></tr>
</table>
""", unsafe_allow_html=True)

with ig_audience:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">👥 Nouveaux followers</td><td class="kpi-desc">Nombre de nouveaux abonnés gagnés pendant la période. Reflète la croissance de la communauté.</td></tr>
  <tr><td class="kpi-name">👤 Followers (Lifetime)</td><td class="kpi-desc">Graphique montrant l'évolution du total des abonnés au fil du temps.</td></tr>
</table>
""", unsafe_allow_html=True)

with ig_engagement:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">🔥 Total interactions</td><td class="kpi-desc">Ensemble des interactions (likes + commentaires + enregistrements) sur la période.</td></tr>
  <tr><td class="kpi-name">❤️ Réactions</td><td class="kpi-desc">Total des likes sur tous les posts.</td></tr>
  <tr><td class="kpi-name">💬 Commentaires</td><td class="kpi-desc">Total des commentaires sur tous les posts.</td></tr>
  <tr><td class="kpi-name">🔖 Enregistrements</td><td class="kpi-desc">Total des sauvegardes. Un taux élevé indique que le contenu a une forte valeur perçue.</td></tr>
</table>
""", unsafe_allow_html=True)

with ig_visibility:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">👁️ Total Reach</td><td class="kpi-desc">Nombre total de comptes uniques touchés par les posts sur la période.</td></tr>
  <tr><td class="kpi-name">🎯 Pic</td><td class="kpi-desc">Meilleure journée en portée ou en impressions selon la section.</td></tr>
  <tr><td class="kpi-name">📏 Moy. journalière</td><td class="kpi-desc">Moyenne de portée ou d'impressions par jour. Utile pour comparer des périodes inégales.</td></tr>
  <tr><td class="kpi-name">📊 Total Impressions</td><td class="kpi-desc">Somme de tous les affichages des posts. Calculé depuis les métriques individuelles de chaque post.</td></tr>
</table>
""", unsafe_allow_html=True)

with ig_content:
    st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Affiche les posts les plus performants de la période, classés par impressions et par engagement total.</p>
<br>
<table class="kpi-table">
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td class="kpi-name">Impressions</td><td class="kpi-desc">Nombre d'affichages du post.</td></tr>
  <tr><td class="kpi-name">Reach</td><td class="kpi-desc">Comptes uniques ayant vu le post.</td></tr>
  <tr><td class="kpi-name">Likes / Commentaires / Partages / Enregistrements</td><td class="kpi-desc">Interactions détaillées par type.</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# BOOST
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🚀 Boost (Campagnes Payantes)</div>', unsafe_allow_html=True)

boost_global, boost_conv, boost_table, boost_demo = st.tabs([
    "📊 Global", "🎯 Conversion", "📋 Toutes les campagnes", "👥 Démographie & Géo"
])

with boost_global:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th><th>Interprétation</th></tr>
  <tr><td class="kpi-name">📁 Total campagnes</td><td class="kpi-desc">Nombre de campagnes actives ou diffusées pendant la période.</td><td>—</td></tr>
  <tr><td class="kpi-name">🖱️ Clics sur le lien</td><td class="kpi-desc">Nombre de clics sur les liens inclus dans les publicités (CTA, lien vers le site, etc.).</td><td>Plus c'est élevé, plus les annonces incitent à l'action.</td></tr>
  <tr><td class="kpi-name">👁️ Comptes touchés</td><td class="kpi-desc">Nombre de personnes uniques qui ont vu au moins une publicité.</td><td>Mesure la portée réelle de la campagne.</td></tr>
  <tr><td class="kpi-name">📢 Impressions</td><td class="kpi-desc">Nombre total d'affichages des publicités (une même personne peut voir plusieurs fois).</td><td>Toujours ≥ Reach.</td></tr>
  <tr><td class="kpi-name">💸 Coût par clic (CPC)</td><td class="kpi-desc">Budget dépensé divisé par le nombre de clics. Exprimé en euros.</td><td>Plus le CPC est bas, plus la campagne est efficace en termes de trafic.</td></tr>
  <tr><td class="kpi-name">📈 CTR</td><td class="kpi-desc">Click-Through Rate : clics ÷ impressions × 100. Mesure le taux de clic sur les publicités.</td><td>Un bon CTR pour Facebook/Instagram est généralement entre 1% et 3%.</td></tr>
  <tr><td class="kpi-name">💰 Montant dépensé</td><td class="kpi-desc">Budget total consommé par toutes les campagnes sur la période.</td><td>—</td></tr>
  <tr><td class="kpi-name">🔁 Répétition</td><td class="kpi-desc">Nombre moyen de fois qu'une même personne a vu la publicité. Impressions ÷ Reach.</td><td>Une répétition > 3 peut indiquer de la saturation de l'audience.</td></tr>
</table>
""", unsafe_allow_html=True)

with boost_conv:
    st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Cette section filtre uniquement les campagnes ayant un <strong>objectif de conversion</strong> (ventes, achats, etc.).</p>
<br>
<table class="kpi-table">
  <tr><th>Indicateur</th><th>Description</th></tr>
  <tr><td class="kpi-name">🎁 Coût par vente</td><td class="kpi-desc">Budget dépensé divisé par le nombre de conversions. Indique combien coûte en moyenne chaque vente générée par les publicités.</td></tr>
  <tr><td class="kpi-name">✅ Commandes (conv.)</td><td class="kpi-desc">Nombre total de conversions (achats, inscriptions, etc.) attribuées aux publicités sur la période.</td></tr>
</table>
""", unsafe_allow_html=True)

with boost_table:
    st.markdown("""
<p style="color:#a1a1aa;font-size:14px;">Tableau récapitulatif de toutes les campagnes avec leurs métriques détaillées. Les campagnes peuvent être triées par n'importe quelle colonne.</p>
<br>
<table class="kpi-table">
  <tr><th>Colonne</th><th>Description</th></tr>
  <tr><td class="kpi-name">Campagne</td><td class="kpi-desc">Nom de la campagne publicitaire.</td></tr>
  <tr><td class="kpi-name">Objectif</td><td class="kpi-desc">Objectif défini pour la campagne (Conversion, Trafic, Notoriété, etc.).</td></tr>
  <tr><td class="kpi-name">Dépensé (€)</td><td class="kpi-desc">Budget consommé par cette campagne.</td></tr>
  <tr><td class="kpi-name">Impressions</td><td class="kpi-desc">Nombre total d'affichages des publicités de cette campagne.</td></tr>
  <tr><td class="kpi-name">Portée</td><td class="kpi-desc">Comptes uniques touchés par cette campagne.</td></tr>
  <tr><td class="kpi-name">Clics</td><td class="kpi-desc">Nombre de clics sur les annonces.</td></tr>
  <tr><td class="kpi-name">CTR (%)</td><td class="kpi-desc">Taux de clic de cette campagne.</td></tr>
  <tr><td class="kpi-name">CPC (€)</td><td class="kpi-desc">Coût moyen par clic.</td></tr>
  <tr><td class="kpi-name">Répétition</td><td class="kpi-desc">Fréquence d'affichage moyenne par personne.</td></tr>
  <tr><td class="kpi-name">Commandes</td><td class="kpi-desc">Conversions attribuées à cette campagne.</td></tr>
  <tr><td class="kpi-name">Coût/vente (€)</td><td class="kpi-desc">Coût par conversion pour cette campagne.</td></tr>
</table>
""", unsafe_allow_html=True)

with boost_demo:
    st.markdown("""
<table class="kpi-table">
  <tr><th>Section</th><th>Description</th></tr>
  <tr><td class="kpi-name">👥 Démographie</td><td class="kpi-desc">Répartition Hommes / Femmes par tranche d'âge parmi les personnes touchées par les publicités. Utile pour vérifier que la cible correspond au public visé.</td></tr>
  <tr><td class="kpi-name">🌍 Géographie</td><td class="kpi-desc">Top villes ou régions en termes de portée. Montre où les publicités ont le plus diffusé géographiquement.</td></tr>
  <tr><td class="kpi-name">🧠 Analyse automatique</td><td class="kpi-desc">Évaluation automatique du CTR, CPC et taux de conversion par rapport à des benchmarks du secteur. Un indicateur rouge signale une performance en dessous de la norme.</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Glossaire
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("📚 Glossaire — Termes clés"):
    st.markdown("""
| Terme | Définition |
|---|---|
| **Reach (Portée)** | Nombre de comptes **uniques** ayant vu un contenu. Chaque personne est comptée une seule fois. |
| **Impressions** | Nombre total d'**affichages**. Une même personne peut générer plusieurs impressions. |
| **Engagement** | Toute interaction active d'un utilisateur : like, commentaire, partage, clic, enregistrement. |
| **Taux d'engagement** | Engagement ÷ Reach × 100. Mesure la qualité de la relation avec l'audience. |
| **CTR** | Click-Through Rate. Clics ÷ Impressions × 100. |
| **CPC** | Coût Par Clic. Budget ÷ Clics. |
| **CPA** | Coût Par Acquisition (ou coût par vente). Budget ÷ Conversions. |
| **Répétition / Fréquence** | Impressions ÷ Reach. Nombre moyen de fois qu'une même personne voit une pub. |
| **Conversion** | Action souhaitée réalisée par l'utilisateur après avoir vu une publicité (achat, inscription, etc.). |
| **Organique** | Contenu diffusé sans budget publicitaire, uniquement via l'algorithme. |
| **Payant (Boost)** | Contenu promu via un budget publicitaire Meta Ads. |
""")

with st.expander("🔄 Fréquence de mise à jour des données"):
    st.markdown("""
| Source | Fréquence |
|---|---|
| **Données pré-chargées** (périodes standard : 7j, 30j, 90j, mois en cours, mois précédent) | Toutes les **6 heures** via GitHub Actions |
| **Plages personnalisées** | Chargées **en direct** depuis Meta API au premier accès, puis sauvegardées |
| **Bouton "Refresh Data"** | Force un rechargement immédiat depuis Meta API |

> Les données Instagram et Facebook proviennent de **Meta Graph API v19.0**. Les données Boost proviennent de **Meta Marketing API**.
""")
