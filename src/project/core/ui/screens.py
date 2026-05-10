"""
Screen renderers for the experiment flow.

Each function renders one screen and returns True when the user
has completed it (so the flow controller can advance).  All state
mutations go through st.session_state.

No business logic here — just UI.  Config values are imported,
never hardcoded.
"""

from __future__ import annotations

import time
import random
import threading
import streamlit as st
from typing import Optional

from core.config import (
    DEFAULT_MAX_TOKENS,
    OLLAMA_API_BASE,
    # Spinner
    SPINNER_PHRASES,
    SPINNER_ROTATE_MIN_SEC,
    SPINNER_ROTATE_MAX_SEC,
    # Consent
    CONSENT_TITLE,
    CONSENT_TEXT,
    # Baseline
    BASELINE_DURATION_SECONDS,
    # Practice
    PRACTICE_TASK_PROMPT,
    # Trials
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    AD_SIDE_PANEL_MODES,
)
from core.experiment.surveys import (
    # OCEAN
    OCEAN_ITEMS,
    OCEAN_SCALE_MIN,
    OCEAN_SCALE_MAX,
    OCEAN_SCALE_LABELS,
    OCEAN_INSTRUCTIONS,
    get_ocean_items,
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
from core.conversation.ollama_stats import estimate_eta, record_timing


# ═══════════════════════════════════════════════════════════════
# LLM SPINNER HELPER
# ═══════════════════════════════════════════════════════════════

# CSS-only spinner injected once per Streamlit app lifetime.
_SPINNER_CSS = """
<style>
@keyframes llm-spin {
    0%   { transform: rotate(0deg);   }
    100% { transform: rotate(360deg); }
}
.llm-spinner {
    display: inline-block;
    width: 18px; height: 18px;
    border: 3px solid rgba(255,255,255,.15);
    border-top-color: #58a6ff;
    border-radius: 50%;
    animation: llm-spin .8s linear infinite;
    flex-shrink: 0;
}
.llm-thinking {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 10px;
    background: #1a1d24; color: #e0e0e0;
    font-size: 0.95em; margin: 8px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,.3);
}
.llm-thinking .phrase {
    flex: 1;
}
.llm-thinking .elapsed {
    font-variant-numeric: tabular-nums;
    font-size: 0.8em;
    opacity: 0.55;
}
</style>
"""


def _call_llm_with_spinner(manager: ConversationManager, user_input: str) -> None:
    """
    Call manager.process_user_message in a background thread while
    showing a live spinner with rotating "thinking" phrases and an
    optional ETA derived from Ollama /api/ps.
    """
    model = getattr(manager, "model", None)
    eta_secs = estimate_eta(
        max_tokens=DEFAULT_MAX_TOKENS,
        model=model,
        base_url=OLLAMA_API_BASE,
    )

    exc_holder: list = []
    t0 = time.perf_counter()

    def _run() -> None:
        try:
            manager.process_user_message(user_input)
        except Exception as e:  # noqa: BLE001
            exc_holder.append(e)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()

    # Inject CSS once
    st.markdown(_SPINNER_CSS, unsafe_allow_html=True)

    placeholder = st.empty()
    phrases = list(SPINNER_PHRASES)
    random.shuffle(phrases)
    phrase_idx = 0
    next_switch = t0 + random.uniform(SPINNER_ROTATE_MIN_SEC, SPINNER_ROTATE_MAX_SEC)

    while thread.is_alive():
        now = time.perf_counter()
        elapsed = now - t0

        # Rotate phrase
        if now >= next_switch:
            phrase_idx = (phrase_idx + 1) % len(phrases)
            next_switch = now + random.uniform(SPINNER_ROTATE_MIN_SEC, SPINNER_ROTATE_MAX_SEC)

        phrase = phrases[phrase_idx]

        # ETA / elapsed label
        if eta_secs is not None:
            remaining = max(0.0, eta_secs - elapsed)
            timer = f"{elapsed:.0f}s / ~{elapsed + remaining:.0f}s"
        else:
            timer = f"{elapsed:.0f}s"

        placeholder.markdown(
            f"""<div class='llm-thinking'>
                <div class='llm-spinner'></div>
                <span class='phrase'>{phrase}</span>
                <span class='elapsed'>{timer}</span>
            </div>""",
            unsafe_allow_html=True,
        )
        time.sleep(0.15)

    thread.join()
    elapsed = time.perf_counter() - t0
    placeholder.empty()

    # Update rolling tokens/s estimate for future ETA predictions
    if manager.messages:
        last_reply = next(
            (m["content"] for m in reversed(manager.messages) if m["role"] == "assistant"),
            "",
        )
        record_timing(elapsed=elapsed, reply=last_reply)

    if exc_holder:
        raise exc_holder[0]


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
        if age < 0 or age > 120:
            st.error("Please enter a valid age (0–120).")
            return None
        return {
            "age": age if age > 0 else None,
            "gender": gender,
            "ai_experience": ai_experience,
        }
    return None


# ═══════════════════════════════════════════════════════════════
# SCREEN 3 — OCEAN PERSONALITY (BFI-44 or BFI-10)
# ═══════════════════════════════════════════════════════════════

def render_ocean(bfi_version: str = "10") -> Optional[list[int]]:
    """
    Render BFI questionnaire (all questions at once).

    Parameters
    ----------
    bfi_version : "10" for BFI-10 (10 items, default) or "44" for BFI-44 (44 items).

    Returns list of raw Likert responses on submit, None otherwise.
    """
    items = get_ocean_items(bfi_version)
    n = len(items)

    st.header("Personality Questionnaire")
    st.info(OCEAN_INSTRUCTIONS)

    responses: list[int] = []
    answered = 0

    for i, (text, _trait, _rev) in enumerate(items):
        value = st.radio(
            f"**{i + 1}.** {text}",
            options=list(range(OCEAN_SCALE_MIN, OCEAN_SCALE_MAX + 1)),
            format_func=lambda v: f"{v} — {OCEAN_SCALE_LABELS.get(v, '')}",
            horizontal=True,
            index=None,
            key=f"ocean_{i}",
        )
        if value is None:
            responses.append(0)  # placeholder; submission blocked below
        else:
            responses.append(value)
            answered += 1

    # Single progress bar reflects how many questions are answered
    st.progress(answered / n, text=f"{answered} of {n} answered")

    st.divider()
    if answered == n and st.button("Continue", type="primary"):
        return responses
    elif answered < n:
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
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            _call_llm_with_spinner(manager, user_input.strip())
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

    # Chat layout — side panel ads float next to the latest message
    show_side = ad_mode in AD_SIDE_PANEL_MODES

    if show_side:
        # Render all messages except the last assistant turn flat,
        # then render the last assistant message + ad card side-by-side
        msgs = manager.messages
        # All but last assistant message render normally
        cutoff = len(msgs)
        for i, msg in enumerate(msgs):
            # Find last assistant message to pair with ad
            if i == cutoff - 1 and msg["role"] == "assistant" and manager.should_inject_ad:
                col_msg, col_ad = st.columns([3, 1])
                with col_msg:
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                # ad rendered outside loop below
            else:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
    else:
        col_ad = None
        for msg in manager.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Side-panel ads — rendered next to the latest assistant message
    if show_side and manager.should_inject_ad:
        last_user = next(
            (m["content"] for m in reversed(manager.messages) if m["role"] == "user"),
            "",
        )
        ad = get_ad(query=last_user, context=manager.messages)
        injector = get_injector(ad_mode)
        result = injector.inject(ad, manager.messages)
        if result.display_payload:
            # col_ad was set in the loop above when last msg was assistant
            try:
                _render_ad_card(col_ad, result.display_payload)
            except Exception:
                _render_ad_card(st, result.display_payload)

    # Suggestion ads
    if ad_mode == "sponsored_conversational" and manager.should_inject_ad:
        last_user = next(
            (m["content"] for m in reversed(manager.messages) if m["role"] == "user"),
            "",
        )
        ad = get_ad(query=last_user, context=manager.messages)
        injector = get_injector(ad_mode)
        result = injector.inject(ad, manager.messages)
        if result.suggestions:
            st.markdown("### 🔍 Sponsored Suggestions")
            for suggestion in result.suggestions:
                if st.button(suggestion, key=f"sug_{suggestion[:20]}"):
                    _call_llm_with_spinner(manager, suggestion)
                    st.rerun()

    # Max turns reached → auto-end
    if manager.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        return True

    # Chat input
    if user_input := st.chat_input("Send a message..."):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            _call_llm_with_spinner(manager, user_input.strip())
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
        # Validate all values are within the expected scale before returning
        invalid = [
            iid for iid, v in responses.items()
            if not (POST_TRIAL_SCALE_MIN <= v <= POST_TRIAL_SCALE_MAX)
        ]
        if invalid:
            st.error(f"Invalid response values detected ({invalid}). Please re-select those items.")
            return None
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
        invalid = [
            iid for iid, v in responses.items()
            if isinstance(v, int) and not (POST_TRIAL_SCALE_MIN <= v <= POST_TRIAL_SCALE_MAX)
        ]
        if invalid:
            st.error(f"Invalid response values detected ({invalid}). Please re-select those items.")
            return None
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
