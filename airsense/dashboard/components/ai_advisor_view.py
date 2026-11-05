"""
AirSense — AI Health Advisor Dashboard View
File: dashboard/components/ai_advisor_view.py
Phase: 4 + 6

Renders View 5 — the AI Health Advisor chat interface:
  - Phase 6 persona quick-pills (runner / parent / asthma / commuter)
  - Suggested quick questions for non-technical users
  - Real-time AQI context injection into the RAG prompt
  - Domain-guarded chat with mandatory medical disclaimer
  - Source citation display (which WHO/CPCB docs were used)
  - Ollama status indicator
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd

from dashboard.components.chat_view import render_persona_pills, resolve_default_city


# ── Quick-Start Suggestion Prompts ────────────────────────────────────────────
SUGGESTED_QUESTIONS = [
    "Is it safe to jog outside today in Delhi?",
    "Should my child go to school when AQI is 250?",
    "What precautions should a heart patient take today?",
    "Which mask should I wear when AQI is above 200?",
    "Is Mumbai's air quality safe for a pregnant woman?",
    "What is the safest time of day to exercise in Ahmedabad?",
    "What AQI is considered dangerous for elderly people?",
    "Should I use an air purifier at home when AQI is 150?",
]


def _format_live_aqi_context(df_latest: pd.DataFrame) -> str:
    """Format current AQI readings from all cities as a readable string for the LLM prompt."""
    if df_latest is None or df_latest.empty:
        return "No live data available."
    
    lines = []
    for _, row in df_latest.iterrows():
        city = row.get("city_display_name", row.get("city", "Unknown"))
        aqi = row.get("aqi")
        pm25 = row.get("pm25")
        pm10 = row.get("pm10")
        
        line = f"- {city}: AQI = {aqi:.0f}" if aqi else f"- {city}: AQI = N/A"
        if pm25:
            line += f", PM2.5 = {pm25:.1f} µg/m³"
        if pm10:
            line += f", PM10 = {pm10:.1f} µg/m³"
        lines.append(line)
    
    return "\n".join(lines)


def render_ai_advisor_view(df_latest: pd.DataFrame | None = None) -> None:
    """
    Render the AI Health Advisor tab in the Streamlit dashboard.
    
    Parameters
    ----------
    df_latest : pd.DataFrame | None
        Latest AQI readings for all cities (to inject as live context into RAG).
    """
    # Lazy import to avoid loading at startup if not needed
    try:
        from rag.health_advisor import (
            ask_health_advisor,
            is_ollama_running,
            is_knowledge_base_ready,
        )
    except ImportError as e:
        st.error(f"RAG module could not be loaded: {e}")
        return

    st.subheader("🤖 AI Health Advisor — Powered by Local LLM + WHO/CPCB Knowledge Base")
    st.markdown(
        "Ask any air quality or health question. Answers are grounded in official **WHO 2021 Air Quality Guidelines** "
        "and **CPCB NAAQS India** standards, enhanced with your **live city AQI readings**. "
        "Everything runs **100% locally on your laptop** — no internet required for the AI."
    )
    
    # ── System Status Indicators ──────────────────────────────────────────────
    col_status1, col_status2, col_status3 = st.columns(3)
    
    ollama_ok = is_ollama_running()
    kb_ok = is_knowledge_base_ready()
    
    with col_status1:
        if ollama_ok:
            st.success("🟢 Ollama LLM: Running")
        else:
            st.info("🟡 Ollama LLM: Offline (Semantic Mode)")
    
    with col_status2:
        if kb_ok:
            st.success("🟢 Knowledge Base: Ready")
        else:
            st.warning("🟡 Knowledge Base: Not Built")
    
    with col_status3:
        live_ok = df_latest is not None and not df_latest.empty
        if live_ok:
            st.success("🟢 Live AQI: Injected")
        else:
            st.warning("🟡 Live AQI: Unavailable")
    
    # ── Setup Instructions if Not Ready ───────────────────────────────────────
    if not ollama_ok or not kb_ok:
        with st.expander("⚙️ Setup Instructions — Click to Expand", expanded=True):
            if not ollama_ok:
                st.markdown("""
                **Ollama is not running.** Start it with:
                ```powershell
                ollama serve
                ```
                Then refresh this page.
                """)
            if not kb_ok:
                st.markdown("""
                **Knowledge base not built yet.** Run once:
                ```powershell
                python rag/build_knowledge_base.py
                ```
                This indexes WHO/CPCB guidelines into ChromaDB. Takes ~30 seconds. 
                Run again only if you want to update the knowledge base.
                """)
    
    st.markdown("---")
    
    # ── Initialize Chat History in Session State ───────────────────────────────
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ── City context for persona pills ─────────────────────────────────────────
    city_options: list[str] = []
    if df_latest is not None and not df_latest.empty and "city_display_name" in df_latest.columns:
        city_options = df_latest["city_display_name"].dropna().astype(str).tolist()
    default_city = resolve_default_city(df_latest)
    if city_options:
        selected_city = st.selectbox(
            "City context for persona questions:",
            options=city_options,
            index=0,
            key="advisor_persona_city",
        )
    else:
        selected_city = default_city

    selected_aqi: float | None = None
    if df_latest is not None and not df_latest.empty and "city_display_name" in df_latest.columns:
        match = df_latest[df_latest["city_display_name"] == selected_city]
        if not match.empty and pd.notna(match.iloc[0].get("aqi")):
            selected_aqi = float(match.iloc[0]["aqi"])

    # Phase 6.4 — Persona quick-pills
    render_persona_pills(df_latest=df_latest, city=selected_city)

    st.markdown("---")
    
    # ── Suggested Quick-Start Questions ───────────────────────────────────────
    st.markdown("#### 💡 Quick Questions — Click to Ask Instantly")
    cols = st.columns(2)
    for i, question in enumerate(SUGGESTED_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"quick_q_{i}", use_container_width=True):
                st.session_state.pending_question = question
    
    st.markdown("---")
    
    # ── Chat Interface ─────────────────────────────────────────────────────────
    st.markdown("#### 💬 Ask Your Own Question")
    
    user_input = st.text_input(
        "Type your air quality or health question:",
        value=st.session_state.get("pending_question", ""),
        placeholder="e.g. Is it safe for a diabetic patient to cycle in Pune today?",
        key="chat_input",
    )
    
    # Clear pending question after it's been placed in input
    if "pending_question" in st.session_state:
        del st.session_state.pending_question
    
    send_col, clear_col = st.columns([3, 1])
    
    with send_col:
        ask_button = st.button("🔍 Ask AI Health Advisor", use_container_width=True, type="primary")
    with clear_col:
        clear_button = st.button("🗑️ Clear Chat", use_container_width=True)
    
    if clear_button:
        st.session_state.chat_history = []
        st.rerun()
    
    if ask_button and user_input.strip():
        live_context = _format_live_aqi_context(df_latest)

        # Domain-refused / static-fallback answers do not require KB or Ollama
        spinner_msg = (
            "🧠 Applying safety guardrails + generating grounded health advice..."
            if ollama_ok else
            "🔍 Retrieving WHO/CPCB guidelines (guarded mode)..."
        )
        with st.spinner(spinner_msg):
            result = ask_health_advisor(
                question=user_input.strip(),
                live_aqi_context=live_context,
                current_aqi=selected_aqi,
                city=selected_city,
            )

        if result.get("refused"):
            st.info("🛡️ Out-of-domain request blocked — no LLM call was made.")
        elif result.get("low_confidence"):
            st.warning(
                "📉 Low RAG confidence — returned verified CPCB/WHO static guidance "
                "instead of free-form generation."
            )
        elif not kb_ok and not result.get("refused"):
            st.caption("Tip: run `python rag/build_knowledge_base.py` for fuller RAG answers.")

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input.strip(),
        })
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "model": result["model_used"],
            "chunks": result["chunks_retrieved"],
            "refused": result.get("refused", False),
            "low_confidence": result.get("low_confidence", False),
        })
    
    # ── Display Chat History ───────────────────────────────────────────────────
    if st.session_state.chat_history:
        st.markdown("#### 📜 Conversation")
        
        for msg in reversed(st.session_state.chat_history):  # Most recent first
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="
                    background: #EFF6FF; 
                    border-left: 4px solid #2563EB; 
                    padding: 12px 16px; 
                    border-radius: 8px; 
                    margin: 8px 0;
                    font-size: 15px;
                ">
                    <b>🙋 You:</b> {msg['content']}
                </div>
                """, unsafe_allow_html=True)
            
            elif msg["role"] == "assistant":
                # Format the answer with source citations
                sources_html = ""
                if msg.get("sources"):
                    source_tags = " ".join([
                        f'<span style="background:#DCFCE7; color:#166534; padding:2px 8px; '
                        f'border-radius:4px; font-size:11px; margin-right:4px;">{s}</span>'
                        for s in msg["sources"]
                    ])
                    sources_html = f'<div style="margin-top:8px;">{source_tags}</div>'
                
                model_badge = (
                    f'<span style="float:right; background:#F1F5F9; color:#64748B; '
                    f'padding:2px 6px; border-radius:4px; font-size:10px;">'
                    f'🤖 {msg.get("model", "ollama")} · {msg.get("chunks", 0)} refs</span>'
                )
                
                st.markdown(f"""
                <div style="
                    background: #F8FAFC; 
                    border-left: 4px solid #10B981; 
                    padding: 14px 16px; 
                    border-radius: 8px; 
                    margin: 8px 0;
                    font-size: 14px;
                ">
                    <b>🤖 AirSense Advisor:</b> {model_badge}<br><br>
                    {msg['content'].replace(chr(10), '<br>')}
                    {sources_html}
                </div>
                """, unsafe_allow_html=True)
    else:
        # Empty state guidance
        st.info(
            "👆 Click one of the **Quick Questions** above or type your own question to get started. "
            "The AI will answer using official WHO and CPCB health guidelines."
        )
    
    # ── Knowledge Base Info ────────────────────────────────────────────────────
    with st.expander("📚 About the Knowledge Base", expanded=False):
        st.markdown("""
        The AirSense Health Advisor uses **Retrieval-Augmented Generation (RAG)** with these sources:
        
        | Source | Content | Authority |
        |--------|---------|-----------|
        | **WHO Air Quality Guidelines (2021)** | Global PM2.5, PM10, NO2, O3, SO2, CO limits | World Health Organization |
        | **CPCB NAAQS India (2009)** | India-specific 6-tier AQI categories, GRAP emergency levels | Ministry of Environment, India |
        | **AirSense Health Advisory Q&A** | Practical advice for exercise, children, elderly, asthma patients | AirSense curated knowledge |
        
        **How it works:**
        1. Your question is converted to a mathematical embedding (vector)
        2. The 4 most relevant guideline excerpts are retrieved by similarity
        3. Your live city AQI data is added as real-time context
        4. The local LLM (Ollama) generates an answer grounded in these sources
        5. No data leaves your laptop — fully private
        """)
