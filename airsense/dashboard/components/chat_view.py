"""
AirSense — Persona Quick-Pills Chat Controls
File: dashboard/components/chat_view.py
Phase: 6

Displays 4 one-click persona buttons that auto-populate the chat input with
city-aware air-quality / health questions.
"""

from __future__ import annotations

from typing import Callable

import pandas as pd
import streamlit as st

PERSONA_PILLS: list[dict[str, str]] = [
    {
        "key": "runner",
        "label": "🏃 Morning Runner",
        "template": "Is it safe to run outside in {city} this morning?",
    },
    {
        "key": "parent",
        "label": "👶 Parent with Toddler",
        "template": "Can my toddler play in the park in {city} today?",
    },
    {
        "key": "asthma",
        "label": "🫁 Asthma Patient",
        "template": "What precautions should asthma patients take at current AQI in {city}?",
    },
    {
        "key": "commuter",
        "label": "🚴 Daily Commuter",
        "template": "Should I wear an N95 mask during my commute in {city} today?",
    },
]


def resolve_default_city(df_latest: pd.DataFrame | None, preferred: str | None = None) -> str:
    """Pick a display city for persona templates."""
    if preferred:
        return preferred
    if df_latest is not None and not df_latest.empty:
        if "city_display_name" in df_latest.columns:
            return str(df_latest.iloc[0]["city_display_name"])
        if "city" in df_latest.columns:
            return str(df_latest.iloc[0]["city"]).title()
    return "Delhi"


def build_persona_question(template: str, city: str) -> str:
    return template.format(city=city)


def render_persona_pills(
    df_latest: pd.DataFrame | None = None,
    city: str | None = None,
    on_select: Callable[[str], None] | None = None,
) -> str | None:
    """
    Render four persona quick-pill buttons.

    Returns the selected question string when a button is clicked; otherwise None.
    Also sets st.session_state['pending_question'] for the chat input binder.
    """
    selected_city = resolve_default_city(df_latest, city)

    st.markdown("#### 👤 Persona Quick-Pills")
    st.caption(
        f"One-click questions tailored to common user profiles · city context: **{selected_city}**"
    )

    cols = st.columns(4)
    clicked: str | None = None

    for idx, persona in enumerate(PERSONA_PILLS):
        question = build_persona_question(persona["template"], selected_city)
        with cols[idx]:
            if st.button(
                persona["label"],
                key=f"persona_pill_{persona['key']}",
                use_container_width=True,
                help=question,
            ):
                clicked = question
                st.session_state["pending_question"] = question
                if on_select is not None:
                    on_select(question)

    return clicked
