"""
TARA — Screen renderers for the experiment flow.

Each function renders one screen and returns True when the user
has completed it (so the flow controller can advance).  All state
mutations go through st.session_state.

No business logic here — just UI.  Config values are imported,
never hardcoded.
"""

from __future__ import annotations

import time
import streamlit as st
from typing import Optional

from core.config import (
    # Consent
    CONSENT_TITLE,
    CONSENT_TEXT,
    # OCEAN
    OCEAN_ITEMS,
    OCEAN_SCALE_MIN,
    OCEAN_SCALE_MAX,
    OCEAN_SCALE_LABELS,
    # Baseline
    BASELINE_DURATION_SECONDS,
    # Practice
    PRACTICE_TASK_PROMPT,
    # Trials
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    AD_SIDE_PANEL_MODES,
    # Post-trial survey
    POST_TRIAL_SCALE_MIN,
    POST_TRIAL_SCALE_MAX,
    POST_TRIAL_ITEMS,
    # Final survey
    FINAL_SURVEY_ITEMS,
    FINAL_OPEN_ENDED_PROMPT,
)
from core.ad_injection import get_ad, get_injector
from core.conversation import ConversationManager


# ═══════════════════════════════════════════════════════════════
# SCREEN 1 — CONSENT
# ═══════════════════════════════════════════════════════════════

def render_consent() -> bool:
    """Show consent form. Returns True when user agrees and clicks Start."""
    st.header(CONSENT_TITLE)
    st.markdown(CONSENT_TEXT)
    st.divider()
    agreed = st.checkbox("I have read and understood the above. I agree to participate.")
    if agreed and st.button("Start", type="primary"):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 2 — DEMOGRAPHICS
# ═══════════════════════════════════════════════════════════════

def render_demographics() -> Optional[dict]:
    """
    Collect basic demographics. Returns dict on submit, None otherwise.
    """
    st.header("About You")
    st.caption("All fields are optional.")

    age = st.number_input("Age", min_value=0, max_value=120, value=0, step=1)
    gender = st.selectbox("Gender", ["Prefer not to say", "Female", "Male", "Non-binary", "Other"])
    ai_experience = st.slider(
        "How experienced are you with AI assistants? (1 = never used, 5 = daily user)",
        min_value=1,
        max_value=5,
        value=3,
    )

    if st.button("Continue", type="primary"):
        return {
            "age": age if age > 0 else None,
            "gender": gender,
            "ai_experience": ai_experience,
        }
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 3 — OCEAN PERSONALITY (BFI-10)
# ═══════════════════════════════════════════════════════════════

def render_ocean() -> Optional[list[int]]:
    """
    Render BFI-10 questionnaire with progress bar.
    Returns list of 10 raw Likert responses on submit, None otherwise.
    """
    st.header("Personality Questionnaire")
    st.caption(
        "For each statement, indicate how much you agree or disagree. "
        "There are no right or wrong answers."
    )

    n = len(OCEAN_ITEMS)
    responses: list[int] = []
    all_answered = True

    for i, (text, _trait, _rev) in enumerate(OCEAN_ITEMS):
        # Progress
        st.progress((i + 1) / n, text=f"Question {i + 1} of {n}")

        value = st.radio(
            text,
            options=list(range(OCEAN_SCALE_MIN, OCEAN_SCALE_MAX + 1)),
            format_func=lambda v: f"{v} — {OCEAN_SCALE_LABELS.get(v, '')}",
            horizontal=True,
            index=None,
            key=f"ocean_{i}",
        )
        if value is None:
            all_answered = False
            responses.append(0)  # placeholder
        else:
            responses.append(value)

    st.divider()
    if all_answered and st.button("Continue", type="primary"):
        return responses
    elif not all_answered:
        st.info("Please answer all questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 4 — BASELINE
# ═══════════════════════════════════════════════════════════════

def render_baseline() -> bool:
    """
    Relaxation baseline screen with countdown.
    Returns True when time is up and user clicks Continue.
    """
    st.header("Baseline Recording")
    st.markdown(
        "Please **relax** and look at the screen. "
        "This will take about 2 minutes."
    )

    # Use session state to track start time
    if "baseline_start" not in st.session_state:
        st.session_state.baseline_start = time.time()

    elapsed = time.time() - st.session_state.baseline_start
    remaining = max(0, BASELINE_DURATION_SECONDS - elapsed)

    if remaining > 0:
        mins, secs = divmod(int(remaining), 60)
        st.markdown(
            f"<div style='text-align:center; font-size:3em; padding:60px 0;'>"
            f"⏳ {mins:02d}:{secs:02d}"
            f"</div>",
            unsafe_allow_html=True,
        )
        # Auto-refresh every 1 second
        time.sleep(1)
        st.rerun()
    else:
        st.success("✓ Baseline recording complete.")
        if st.button("Continue", type="primary"):
            del st.session_state.baseline_start
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 5 — PRACTICE
# ═══════════════════════════════════════════════════════════════

def render_practice(manager: ConversationManager) -> bool:
    """
    Practice chat (no ads, no experiment logging).
    Returns True when user clicks 'Done practising'.
    """
    st.header("Practice Round")
    st.info(PRACTICE_TASK_PROMPT)

    # Chat history
    for msg in manager.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if user_input := st.chat_input("Send a message..."):
        manager.process_user_message(user_input)
        st.rerun()

    # Allow ending practice at any time after ≥1 exchange
    if manager.turn_count >= 1:
        st.divider()
        if st.button("Done practising — start the experiment", type="primary"):
            return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 6 — TRIAL INTRO
# ═══════════════════════════════════════════════════════════════

def render_trial_intro(trial_number: int, total_trials: int, task_prompt: str) -> bool:
    """Show task description before a trial starts."""
    st.header(f"Conversation {trial_number} of {total_trials}")
    st.markdown(
        f"<div style='text-align:center; font-size:1.2em; padding:40px 20px; "
        f"background:#1a1d24; border-radius:12px; margin:20px 0;'>"
        f"{task_prompt}"
        f"</div>",
        unsafe_allow_html=True,
    )
    if st.button("Start conversation", type="primary"):
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# SCREEN 7 — TRIAL CHAT (core screen)
# ═══════════════════════════════════════════════════════════════

def render_trial_chat(manager: ConversationManager, ad_mode: str) -> bool:
    """
    Main chat interface. Returns True when the trial ends
    (user ends after min turns, or max turns reached).
    """
    # Task reminder at top
    if manager.task:
        st.caption(f"📝 {manager.task.participant_prompt}")

    # Turn progress in sidebar
    with st.sidebar:
        progress = min(manager.turn_count / MAX_TURNS_PER_TRIAL, 1.0)
        st.progress(progress, text=f"Turn {manager.turn_count} / {MAX_TURNS_PER_TRIAL}")

        if manager.can_end:
            st.success(
                f"✓ Minimum of {MIN_TURNS_PER_TRIAL} turns reached. "
                "You can keep chatting or end the conversation."
            )
            if st.button("✅ End Conversation"):
                return True

    # Chat layout
    show_side = ad_mode in AD_SIDE_PANEL_MODES
    if show_side:
        col_main, col_side = st.columns([3, 1])
    else:
        col_main, col_side = st.columns([1, 0.001])

    with col_main:
        for msg in manager.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Side-panel ads (only rendered on ad turns)
    if show_side and manager.should_inject_ad:
        ad = get_ad()
        injector = get_injector(ad_mode)
        result = injector.inject(ad, manager.messages)
        if result.display_payload:
            _render_ad_card(col_side, result.display_payload)

    # Suggestion ads
    if ad_mode == "3_suggestions" and manager.should_inject_ad:
        ad = get_ad()
        injector = get_injector(ad_mode)
        result = injector.inject(ad, manager.messages)
        if result.suggestions:
            st.markdown("### 🔍 Sponsored Suggestions")
            for suggestion in result.suggestions:
                if st.button(suggestion, key=f"sug_{suggestion[:20]}"):
                    manager.process_user_message(suggestion)
                    st.rerun()

    # Max turns reached → auto-end
    if manager.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        return True

    # Chat input
    if user_input := st.chat_input("Send a message..."):
        manager.process_user_message(user_input)
        st.rerun()

    return False


def _render_ad_card(container, payload: dict):
    """Dark-mode styled ad card."""
    with container:
        st.markdown(
            f"""
            <div style="background-color: #2a1f0e; border-left: 4px solid #ff9800;
                        padding: 12px; border-radius: 8px; margin-top: 8px;">
                <h4 style="margin: 0 0 6px 0; color: #e0e0e0;">{payload['header']}</h4>
                <p style="font-weight: bold; margin: 0 0 4px 0; color: #f5f5f5;">{payload['title']}</p>
                <p style="margin: 0; color: #bbb;">{payload['text']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════
# SCREEN 8 — POST-TRIAL SURVEY
# ═══════════════════════════════════════════════════════════════

def render_post_trial_survey(trial_number: int) -> Optional[dict]:
    """
    Likert survey after each trial.
    Returns dict of {item_id: score} on submit, None otherwise.
    """
    st.header(f"Post-Conversation Survey (Trial {trial_number})")
    st.caption("Please rate the following statements about the conversation you just had.")

    responses: dict[str, int] = {}
    all_answered = True

    for item in POST_TRIAL_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(POST_TRIAL_SCALE_MIN, POST_TRIAL_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"post_trial_{trial_number}_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    if all_answered and st.button("Continue", type="primary"):
        return responses
    elif not all_answered:
        st.info("Please answer all questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 9 — FINAL SURVEY
# ═══════════════════════════════════════════════════════════════

def render_final_survey() -> Optional[dict]:
    """
    Global end-of-session survey + open-ended debrief question.
    Returns dict on submit, None otherwise.
    """
    st.header("Final Survey")
    st.caption("Please reflect on the entire session.")

    responses: dict[str, int | str] = {}
    all_answered = True

    for item in FINAL_SURVEY_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(POST_TRIAL_SCALE_MIN, POST_TRIAL_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"final_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    st.subheader("Debrief")
    open_text = st.text_area(FINAL_OPEN_ENDED_PROMPT, key="final_open_ended")
    responses["open_ended"] = open_text

    if all_answered and st.button("Submit", type="primary"):
        return responses
    elif not all_answered:
        st.info("Please answer all Likert questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 10 — DONE
# ═══════════════════════════════════════════════════════════════

def render_done():
    """Thank-you screen."""
    st.balloons()
    st.header("🎉 Thank you!")
    st.markdown(
        "You have completed the study. Your data has been saved.\n\n"
        "Please let the researcher know you are finished."
    )
