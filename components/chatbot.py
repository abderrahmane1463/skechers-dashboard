"""
components/chatbot.py — Gemini-powered floating chatbot for the Skechers dashboard.
Answers only dashboard-related questions.
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


SYSTEM_PROMPT = """
You are a helpful assistant for the Skechers Algeria social media analytics dashboard.
You ONLY answer questions related to this dashboard — its metrics, KPIs, data sources,
and how to interpret the numbers. If a user asks about anything unrelated to the dashboard,
politely decline and redirect them to dashboard topics.

You respond in the same language the user writes in (French or English or Arabic).

--- DASHBOARD CONTEXT ---

PLATFORMS:
- Facebook: Audience, Engagement, Visibility, Top Content, Community tabs
- Instagram: Visibility, Engagement tabs
- Boost: Paid campaigns (Meta Ads)
- Google Analytics 4: Website traffic and e-commerce

INSTAGRAM KPIs (all from Meta Graph API v22+):
- 👥 Followers: total follower count (profile field)
- 📢 Vues: total views across all content (posts+stories+reels) — from account-level insights metric=views, metric_type=total_value
- 🎯 Couverture: unique accounts reached — metric=reach, metric_type=total_value (only works for ≤30 day windows)
- 🔥 Total interactions: likes+comments+shares+saves — metric=total_interactions, metric_type=total_value
- ❤️ Réactions: total likes (NOT privacy-filtered at account level) — metric=likes, metric_type=total_value
- 💬 Commentaires: total comments — metric=comments, metric_type=total_value
- ↗️ Partages: total shares — metric=shares, metric_type=total_value
- 🔖 Enregistrements: total saves — metric=saves, metric_type=total_value
- 📊 Taux d'engagement: Total interactions ÷ Reach × 100

IMPORTANT INSTAGRAM LIMITATIONS:
- Per-post like_count is privacy-filtered by Meta (e.g. API returns 88 but real count is 2,500). Nothing can be done.
- impressions metric was deprecated by Meta in v22+ for all post types — replaced by views
- views metric_type=time_series is NOT supported — no daily breakdown available for views
- Couverture shows "—" for periods >30 days (API limitation)
- Per-post data fetched via field expansion: fields=insights.metric(views,reach,saved,shares,likes,comments,total_interactions)

FACEBOOK KPIs:
- Followers, Net follows, Unfollows from page_fans, page_fan_adds, page_fan_removes
- Reach from page_impressions_unique
- Impressions from page_impressions
- Engagement from page_post_engagements
- Top Content: podium of top 3 posts by reach and by engagement

BOOST (Paid):
- Campaigns data from Meta Marketing API
- KPIs: spend, reach, impressions, clicks, CTR, CPC, CPM, frequency, conversions
- Only Skechers campaigns (filtered by keywords: SKX, Skechers, page ID)
- Ad account act_765947885726761 is the source

GOOGLE ANALYTICS 4:
- Active users, new users, sessions, engagement rate, bounce rate
- E-commerce funnel: view_item → add_to_cart → begin_checkout → purchase
- Traffic sources, geography, device breakdown

CACHE & REFRESH:
- Data is cached in Supabase permanently
- "Refresh Data" button deletes the cache for the current period and re-fetches from Meta API
- If numbers seem stale, click Refresh Data

DATA SOURCES:
- Facebook & Instagram: Meta Graph API v22+
- Boost: Meta Marketing API
- Google Analytics: GA4 Data API v1beta
- Storage: Supabase (PostgreSQL)

--- END CONTEXT ---

Be concise, helpful, and accurate. If you're not sure about something, say so.
"""


def _get_api_key() -> str:
    """Read API key — config fallback > st.secrets > os.environ."""
    def _clean(k: str) -> str:
        return k.strip().replace("\n", "").replace("\r", "").replace(" ", "")

    # 1. config.py hardcoded fallback (always works)
    try:
        from config import GEMINI_API_KEY as _cfg_key
        if _cfg_key:
            return _clean(_cfg_key)
    except Exception:
        pass
    # 2. st.secrets
    try:
        key = _clean(str(st.secrets["GEMINI_API_KEY"]))
        if key:
            return key
    except Exception:
        pass
    # 3. env var
    return _clean(os.environ.get("GEMINI_API_KEY", ""))


def _build_data_context() -> str:
    """Build a dynamic context string from current dashboard data in session state."""
    ctx = st.session_state.get("dashboard_context")
    if not ctx:
        return "\n--- CURRENT DATA ---\nNo data loaded yet. User has not viewed any platform tab.\n"

    lines = [
        f"\n--- CURRENT DASHBOARD DATA ---",
        f"Platform: {ctx.get('platform', '?')}",
        f"Period: {ctx.get('period', '?')}",
        f"",
    ]

    platform = ctx.get("platform", "")

    if platform == "Instagram":
        prev_f = ctx.get('prev_followers', 0)
        f_delta = ctx['followers'] - prev_f if prev_f else 0
        lines += [
            f"👥 Followers: {ctx['followers']:,} ({'+' if f_delta >= 0 else ''}{f_delta:,} vs previous period)",
            f"📢 Vues: {ctx['total_views']:,} (prev: {ctx['prev_views']:,})",
            f"🎯 Couverture (Reach): {ctx['total_reach']:,} (prev: {ctx['prev_reach']:,})",
            f"🔥 Total Interactions: {ctx['total_interactions']:,} (prev: {ctx['prev_interactions']:,})",
            f"❤️ Réactions (Likes): {ctx['total_likes']:,} (prev: {ctx['prev_likes']:,})",
            f"💬 Commentaires: {ctx['total_comments']:,} (prev: {ctx['prev_comments']:,})",
            f"↗️ Partages: {ctx['total_shares']:,} (prev: {ctx['prev_shares']:,})",
            f"🔖 Enregistrements: {ctx['total_saves']:,} (prev: {ctx['prev_saves']:,})",
            f"📊 Taux d'engagement: {ctx['engagement_rate']}%",
            f"📝 Publications: {ctx['total_posts']}",
            f"",
        ]

        # Daily reach series
        reach_series = ctx.get("reach_series", [])
        if reach_series:
            lines.append("📈 Daily Reach series (date: value):")
            for pt in reach_series:
                lines.append(f"  {pt.get('date','?')}: {pt.get('value',0):,}")
            lines.append("")

        # Top 3 posts by views
        top_views = ctx.get("top3_by_views", [])
        if top_views:
            lines.append("🏆 Top 3 posts by Views:")
            for i, p in enumerate(top_views, 1):
                lines.append(f"  #{i} [{p['date']}] {p['text'][:50]}...")
                lines.append(f"     Views:{p['views']:,} | Reach:{p['reach']:,} | Likes:{p['likes']:,} | Comments:{p['comments']:,} | Shares:{p['shares']:,} | Saves:{p['saves']:,} | Total:{p['total_interactions']:,}")
            lines.append("")

        # Top 3 by engagement
        top_eng = ctx.get("top3_by_engagement", [])
        if top_eng:
            lines.append("🏆 Top 3 posts by Engagement:")
            for i, p in enumerate(top_eng, 1):
                lines.append(f"  #{i} [{p['date']}] {p['text'][:50]}...")
                lines.append(f"     Views:{p['views']:,} | Reach:{p['reach']:,} | Likes:{p['likes']:,} | Comments:{p['comments']:,} | Shares:{p['shares']:,} | Saves:{p['saves']:,} | Total:{p['total_interactions']:,}")
            lines.append("")

        # All posts summary
        all_posts = ctx.get("all_posts", [])
        if all_posts:
            lines.append(f"📋 All {len(all_posts)} posts this period:")
            for p in all_posts:
                lines.append(f"  [{p['date']}] {p['media_type']} | {p['text'][:40]}... | Views:{p['views']:,} | Reach:{p['reach']:,} | Likes:{p['likes']:,} | Total:{p['total_interactions']:,}")

    elif platform == "Facebook":
        f_delta = ctx['followers'] - ctx.get('prev_followers', 0)
        lines += [
            f"👥 Followers: {ctx['followers']:,} ({'+' if f_delta >= 0 else ''}{f_delta:,} vs previous period)",
            f"👁️ Reach: {ctx['total_reach']:,} (prev: {ctx['prev_reach']:,})",
            f"📢 Impressions: {ctx['total_impressions']:,} (prev: {ctx['prev_impressions']:,})",
            f"🔥 Total Interactions: {ctx['total_interactions']:,} (prev: {ctx['prev_interactions']:,})",
            f"❤️ Réactions: {ctx['total_reactions']:,} (prev: {ctx['prev_reactions']:,})",
            f"💬 Commentaires: {ctx['total_comments']:,} (prev: {ctx['prev_comments']:,})",
            f"🔁 Partages: {ctx['total_shares']:,} (prev: {ctx['prev_shares']:,})",
            f"📝 Publications: {ctx['total_posts']}",
            f"",
        ]

        reach_series = ctx.get("reach_series", [])
        if reach_series:
            lines.append("📈 Daily Reach series (date: value):")
            for pt in reach_series:
                lines.append(f"  {pt.get('date','?')}: {pt.get('value',0):,}")
            lines.append("")

        top_reach = ctx.get("top3_by_reach", [])
        if top_reach:
            lines.append("🏆 Top 3 posts by Reach:")
            for i, p in enumerate(top_reach, 1):
                lines.append(f"  #{i} [{p['date']}] {p['text'][:50]}...")
                lines.append(f"     Reach:{p['reach']:,} | Reactions:{p['reactions']:,} | Comments:{p['comments']:,} | Shares:{p['shares']:,} | Total:{p['total_interactions']:,}")
            lines.append("")

        top_eng = ctx.get("top3_by_engagement", [])
        if top_eng:
            lines.append("🏆 Top 3 posts by Engagement:")
            for i, p in enumerate(top_eng, 1):
                lines.append(f"  #{i} [{p['date']}] {p['text'][:50]}...")
                lines.append(f"     Reach:{p['reach']:,} | Reactions:{p['reactions']:,} | Comments:{p['comments']:,} | Shares:{p['shares']:,} | Total:{p['total_interactions']:,}")
            lines.append("")

        all_posts = ctx.get("all_posts", [])
        if all_posts:
            lines.append(f"📋 All {len(all_posts)} posts this period:")
            for p in all_posts:
                lines.append(f"  [{p['date']}] {p['text'][:40]}... | Reach:{p['reach']:,} | Reactions:{p['reactions']:,} | Total:{p['total_interactions']:,}")

    lines.append("\n--- END CURRENT DATA ---\n")
    return "\n".join(lines)


def _get_gemini_response(history: list) -> str:
    """Call Gemini API with conversation history using google-genai SDK."""
    try:
        from google import genai
        from google.genai import types

        api_key = _get_api_key()
        if not api_key:
            return "⚠️ Clé API Gemini manquante. Veuillez contacter l'administrateur."

        client = genai.Client(api_key=api_key)

        # Build conversation history for multi-turn chat
        contents = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            ))

        # Inject live dashboard data into system prompt
        dynamic_prompt = SYSTEM_PROMPT + _build_data_context()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=dynamic_prompt,
                temperature=0.7,
                max_output_tokens=1024,
            ),
        )
        return response.text
    except Exception as e:
        return f"⚠️ Erreur : {str(e)}"


def render_chatbot():
    """Render a floating chatbot button and panel."""
    _dark = st.session_state.get("theme", "dark") == "dark"

    # ── Initialize session state ──────────────────────────────────────────────
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── CSS for floating button + panel ──────────────────────────────────────
    _bg       = "#1a1a1a"   if _dark else "#ffffff"
    _border   = "#333333"   if _dark else "#e5e7eb"
    _msg_user = "#003594"
    _msg_bot  = "#262626"   if _dark else "#f3f4f6"
    _text     = "#ffffff"   if _dark else "#111827"
    _subtext  = "#a1a1aa"   if _dark else "#6b7280"

    st.markdown(f"""
<style>
/* Floating button */
#chat-fab {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #003594, #0050D0);
    color: white;
    font-size: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 4px 20px rgba(0,53,148,0.5);
    border: none;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
#chat-fab:hover {{
    transform: scale(1.1);
    box-shadow: 0 6px 28px rgba(0,53,148,0.7);
}}

/* Chat panel */
#chat-panel {{
    position: fixed;
    bottom: 96px;
    right: 28px;
    width: 360px;
    max-height: 520px;
    background: {_bg};
    border: 1px solid {_border};
    border-radius: 20px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.35);
    z-index: 9998;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}
#chat-header {{
    background: linear-gradient(90deg, #003594, #0050D0);
    padding: 14px 18px;
    color: white;
    font-weight: 700;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
}}
#chat-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 14px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 340px;
}}
.chat-msg-user {{
    background: {_msg_user};
    color: white;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    font-size: 0.85rem;
    align-self: flex-end;
    max-width: 85%;
    line-height: 1.5;
}}
.chat-msg-bot {{
    background: {_msg_bot};
    color: {_text};
    padding: 10px 14px;
    border-radius: 16px 16px 16px 4px;
    font-size: 0.85rem;
    align-self: flex-start;
    max-width: 85%;
    line-height: 1.5;
}}
.chat-msg-sub {{
    font-size: 0.7rem;
    color: {_subtext};
    margin-top: 2px;
}}
@media (max-width: 480px) {{
    #chat-panel {{ width: calc(100vw - 32px); right: 16px; }}
}}
</style>
""", unsafe_allow_html=True)

    # ── Toggle button ─────────────────────────────────────────────────────────
    col_spacer, col_btn = st.columns([10, 1])
    with col_btn:
        btn_icon = "✕" if st.session_state.chat_open else "💬"
        if st.button(btn_icon, key="chat_fab_btn", help="Assistant Dashboard"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()

    # ── Chat panel ────────────────────────────────────────────────────────────
    if st.session_state.chat_open:
        with st.container():
            st.markdown(f"""
<div id="chat-panel">
  <div id="chat-header">🤖 Assistant Dashboard &nbsp;<span style="font-size:0.75rem;opacity:0.8;">Powered by Gemini</span></div>
  <div id="chat-messages">
    {"".join([
        f'<div class="chat-msg-{"user" if m["role"]=="user" else "bot"}">{m["content"]}</div>'
        for m in (st.session_state.chat_history if st.session_state.chat_history
                  else [{"role": "bot", "content": "👋 Bonjour ! Je suis l'assistant du dashboard Skechers. Posez-moi vos questions sur les KPIs, les données ou comment interpréter les chiffres."}])
    ])}
  </div>
</div>
""", unsafe_allow_html=True)

            # Input form
            with st.form(key="chat_form", clear_on_submit=True):
                cols = st.columns([8, 1])
                user_input = cols[0].text_input(
                    "Message",
                    placeholder="Posez votre question...",
                    label_visibility="collapsed",
                )
                submitted = cols[1].form_submit_button("➤")

            if submitted and user_input.strip():
                # Add user message
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input.strip(),
                })
                # Get Gemini response
                with st.spinner("..."):
                    reply = _get_gemini_response(st.session_state.chat_history)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": reply,
                })
                st.rerun()

            # Clear chat button
            if st.session_state.chat_history:
                if st.button("🗑️ Effacer la conversation", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()
