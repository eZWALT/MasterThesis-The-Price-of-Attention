"""
Screen renderers for the experiment flow.

Each function renders one screen and returns True when the user
has completed it (so the flow controller can advance).  All state
mutations go through st.session_state.

No business logic here — just UI.  Config values are imported,
never hardcoded.
"""

from __future__ import annotations

import html as html_module
import time
import streamlit as st
from typing import Optional

from core.config import (
    DEFAULT_MAX_TOKENS,
    CONSENT_TITLE,
    CONSENT_TEXT,
    BASELINE_DURATION_SECONDS,
    BASELINE_TITLE,
    BASELINE_INSTRUCTION,
    BASELINE_COMPLETE_MESSAGE,
    BASELINE_CONTINUE_LABEL,
    AD_MODE_LABELS,
    CONDITION_LABELS,
    PRACTICE_TASK_PROMPT,
    MAX_TURNS_PER_TRIAL,
    AD_SIDE_PANEL_MODES,
)
from core.experiment.surveys import (
    OCEAN_ITEMS,
    OCEAN_SCALE_MIN,
    OCEAN_SCALE_MAX,
    OCEAN_SCALE_LABELS,
    OCEAN_INSTRUCTIONS,
    get_ocean_items,
    POST_TRIAL_SCALE_MIN,
    POST_TRIAL_SCALE_MAX,
    POST_TRIAL_ITEMS,
    POST_CONDITION_SCALE_MIN,
    POST_CONDITION_SCALE_MAX,
    POST_CONDITION_ITEMS,
    GLOBAL_EVAL_SCALE_MIN,
    GLOBAL_EVAL_SCALE_MAX,
    GLOBAL_EVAL_ITEMS,
    GLOBAL_OPEN_ENDED_PROMPT,
    FINAL_SURVEY_ITEMS,
    FINAL_OPEN_ENDED_PROMPT,
    ADS_AWARENESS_CATEGORICAL,
    ADS_AWARENESS_OPEN_ENDED,
    ADS_RECALL_CATEGORICAL,
    ADS_RECALL_LIKERT,
    ADS_RECALL_SCALE_MIN,
    ADS_RECALL_SCALE_MAX,
    ADS_PERCEPTION_LIKERT,
    ADS_PERCEPTION_OPEN_ENDED,
    ADS_PERCEPTION_SCALE_MIN,
    ADS_PERCEPTION_SCALE_MAX,
    LLM_EVAL_CATEGORIES,
    LLM_EVAL_SCALE_MIN,
    LLM_EVAL_SCALE_MAX,
    GODSPEED_SEMANTIC,
    GODSPEED_REASK_LIKERT,
    GODSPEED_SCALE_MIN,
    GODSPEED_SCALE_MAX,
    DEMOGRAPHICS_END_TEXT,
    DEMOGRAPHICS_END_CATEGORICAL,
    DECEPTION_DISCLOSURE_TEXT,
)
from core.ad_injection import get_injector
from core.ad_injection.ad_links import (
    clean_inline_assistant_display,
    detect_mentioned_ad,
    html_product_link,
    inject_ad_click_tracker,
    linkify_inline_ad_titles,
    register_click_state,
    start_ad_click_server,
)
from core.ad_injection.models import (
    Ad,
    format_products_block,
)
from core.conversation import ConversationManager


def _banner_box_style(*, explicit: bool) -> str:
    """Inline styles — Streamlit often ignores separately injected <style> blocks."""
    base = (
        "width:100%;max-width:100%;box-sizing:border-box;display:block;"
        "background:#2a1f0e;padding:12px 16px;border-radius:8px;"
        "margin:8px 0 14px 0;"
    )
    if explicit:
        return base + "border:2px solid #ff9800;border-left:6px solid #ff9800;"
    return base + "border-left:4px solid #ff9800;"


def _ad_image_html(image_url: str, *, size_px: int = 72) -> str:
    """Optional product thumbnail — omitted when no image URL exists."""
    safe_url = html_module.escape(image_url, quote=True)
    alt = html_module.escape("Product")
    return (
        f'<img src="{safe_url}" alt="{alt}" '
        f'style="width:{size_px}px;height:{size_px}px;object-fit:cover;'
        f'border-radius:6px;flex-shrink:0;background:#1a1a1a;" />'
    )


def _resolve_payload_image_url(payload: dict, ad: Ad | None) -> str | None:
    """Image URL from display payload or linked ad metadata."""
    url = payload.get("image_url")
    if isinstance(url, str) and url.strip().startswith(("http://", "https://")):
        return url.strip()
    if ad is not None:
        return ad_image_url(ad)
    return None


def _render_chat_history(manager: ConversationManager, ad_mode: str) -> None:
    """Render full message history with trackable inline/banner ad links."""
    turn = 0
    for msg in manager.messages:
        if msg.get("role") == "user":
            turn += 1
        with st.chat_message(msg["role"]):
            msg_turn = turn if msg.get("role") == "assistant" else None
            _render_chat_message(
                msg,
                ad_mode=ad_mode,
                manager=manager,
                turn=msg_turn,
            )


def _render_chat_message(
    msg: dict,
    *,
    ad_mode: str | None = None,
    manager: ConversationManager | None = None,
    turn: int | None = None,
) -> None:
    """Render one chat message; linkify inline ad product names when applicable."""
    content = msg.get("content", "")
    if (
        msg.get("role") == "assistant"
        and ad_mode == "inline_persuasive"
        and manager is not None
        and turn is not None
        and turn in manager.ads_by_turn
    ):
        ads = manager.ads_by_turn[turn]
        mentioned = detect_mentioned_ad(content, ads)
        link_ads = [mentioned] if mentioned else ads[:1]
        display = clean_inline_assistant_display(content)
        html_body = linkify_inline_ad_titles(display, link_ads)
        st.markdown(html_body, unsafe_allow_html=True)
        return

    st.markdown(content)


def _render_ad_banner(
    payload: dict,
    *,
    ad_mode: str | None = None,
    manager: ConversationManager | None = None,
    turn: int | None = None,
    ad: Ad | None = None,
) -> None:
    """Full-width ad strip: label, clickable product title, CTA."""
    from core.config import EXPLICIT_AD_LABEL

    explicit = ad_mode == "explicit_ad_block" or payload.get("header") == EXPLICIT_AD_LABEL
    box_style = _banner_box_style(explicit=explicit)
    label_style = (
        "font-size:0.72em;color:#9a9a9a;text-transform:uppercase;"
        "letter-spacing:0.06em;margin:0 0 6px 0;"
    )
    title_style = (
        "font-weight:600;font-size:1rem;color:#f5f5f5;margin:0 0 6px 0;"
        "line-height:1.25;word-wrap:break-word;"
    )
    cta_style = "color:#ff9800;font-weight:600;font-size:0.9em;margin:0;"

    label = html_module.escape(str(payload.get("header", "Sponsored")))
    title = str(payload.get("title", ""))
    cta = html_module.escape(str(payload.get("cta", "")))
    cta_html = f'<p style="{cta_style}">{cta}</p>' if cta else ""

    if manager is not None and turn is not None and (ad is not None or payload.get("source_item_id")):
        if ad is None:
            ad = Ad(
                title=title,
                text="",
                source_item_id=str(payload.get("source_item_id", "unknown")),
                cta=payload.get("cta", ""),
            )
        title_html = html_product_link(ad, label=title)
    else:
        title_html = html_module.escape(title)

    image_url = _resolve_payload_image_url(payload, ad)
    if image_url:
        body_html = (
            f'<div style="display:flex;align-items:flex-start;gap:12px;">'
            f"{_ad_image_html(image_url, size_px=72)}"
            f'<div style="flex:1;min-width:0;">'
            f'<p style="{label_style}">{label}</p>'
            f'<p style="{title_style}">{title_html}</p>'
            f"{cta_html}"
            f"</div></div>"
        )
    else:
        body_html = (
            f'<p style="{label_style}">{label}</p>'
            f'<p style="{title_style}">{title_html}</p>'
            f"{cta_html}"
        )

    st.markdown(
        f'<div class="ad-banner" style="{box_style}">{body_html}</div>',
        unsafe_allow_html=True,
    )


# Modes that show the full-width title+CTA banner above the chat input.
_AD_BANNER_MODES = frozenset({"explicit_ad_block"})


def _ad_display_state_matches_mode(manager: ConversationManager, ad_mode: str) -> bool:
    """True when cached retrieval belongs to the active ad mode."""
    cached_mode = getattr(manager, "last_retrieval_ad_mode", None)
    return (
        manager.last_retrieval is not None
        and manager.last_retrieval.has_ads
        and cached_mode == ad_mode
    )


def _render_turn_ads(
    manager: ConversationManager,
    ad_mode: str,
) -> None:
    """Render participant-visible ads for the current turn (compact, no descriptions)."""
    if not manager.should_inject_ad:
        return
    if not _ad_display_state_matches_mode(manager, ad_mode):
        return

    result = get_injector(ad_mode).inject(manager.last_retrieval, manager.messages)
    turn = manager.turn_count
    primary = manager.last_retrieval.primary

    if result.display_payload and ad_mode in _AD_BANNER_MODES:
        _render_ad_banner(
            result.display_payload,
            ad_mode=ad_mode,
            manager=manager,
            turn=turn,
            ad=primary,
        )


def _render_explicit_ad_banner(payload: dict) -> None:
    """Backward-compatible alias."""
    _render_ad_banner(payload, ad_mode="explicit_ad_block")


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

    age = st.number_input("Age", min_value=0, max_value=120, value=25, step=1)
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

_BASELINE_SESSION_KEYS = (
    "baseline_start",
    "_baseline_screen_active",
    "_baseline_user_confirmed",
)


def _format_duration_label(seconds: int) -> str:
    """Human-readable duration for baseline instructions."""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    mins, secs = divmod(seconds, 60)
    if secs:
        return (
            f"{mins} minute{'s' if mins != 1 else ''} "
            f"and {secs} second{'s' if secs != 1 else ''}"
        )
    return f"{mins} minute{'s' if mins != 1 else ''}"


def clear_baseline_session_state() -> None:
    """Drop baseline timer keys when leaving or skipping the screen."""
    for key in _BASELINE_SESSION_KEYS:
        st.session_state.pop(key, None)


def _reset_baseline_timer() -> None:
    st.session_state.baseline_start = time.time()


def render_baseline() -> bool:
    """
    Relaxation baseline screen with countdown.

    Uses a Streamlit fragment so only the timer refreshes — not the whole app.
    That avoids re-rendering prior screens (e.g. OCEAN widgets) on each tick.
    Returns True when time is up and the user clicks Continue.
    """
    if st.session_state.pop("_baseline_user_confirmed", False):
        return True

    if not st.session_state.get("_baseline_screen_active"):
        st.session_state._baseline_screen_active = True
        _reset_baseline_timer()

    st.header(BASELINE_TITLE)
    st.markdown(
        BASELINE_INSTRUCTION.format(
            duration_label=_format_duration_label(BASELINE_DURATION_SECONDS),
        )
    )

    @st.fragment(run_every=1)
    def _baseline_countdown() -> None:
        elapsed = time.time() - st.session_state.baseline_start
        remaining = max(0, int(BASELINE_DURATION_SECONDS - elapsed))
        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.markdown(
                f"<div style='text-align:center; font-size:3em; padding:60px 0;'>"
                f"⏳ {mins:02d}:{secs:02d}"
                f"</div>",
                unsafe_allow_html=True,
            )
            return

        st.success(BASELINE_COMPLETE_MESSAGE)
        if st.button(BASELINE_CONTINUE_LABEL, type="primary", key="baseline_continue"):
            clear_baseline_session_state()
            st.session_state._baseline_user_confirmed = True
            st.rerun()

    _baseline_countdown()
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
            _render_chat_message(msg)

    # Input
    if user_input := st.chat_input("Send a message..."):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            with st.chat_message("user"):
                st.markdown(user_input.strip())
            with st.chat_message("assistant"):
                st.write_stream(manager.process_user_message_stream(user_input.strip()))
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

def _render_retrieval_debug(retrieval) -> None:
    """Show HyDE passages and retrieval metrics (dev=flow and dev mode)."""
    from core.ad_injection.models import AdRetrievalResult

    if retrieval is None:
        st.caption("No retrieval yet — send a message with ad injection enabled.")
        return
    if not isinstance(retrieval, AdRetrievalResult):
        return

    diag = retrieval.diag or {}
    st.caption(f"Retrieval query ({diag.get('query_chars', '?')} chars)")
    rq = diag.get("retrieval_query")
    if rq:
        st.text(rq)

    docs = diag.get("hyde_documents") or []
    if docs:
        st.markdown(f"**HyDE documents ({len(docs)})**")
        llm_cap = diag.get("hyde_llm_max_tokens")
        token_counts = diag.get("hyde_doc_token_counts") or []
        cap_note = f" · num_predict={llm_cap}" if llm_cap else ""
        for i, doc in enumerate(docs, 1):
            tok = token_counts[i - 1] if i - 1 < len(token_counts) else None
            label = f"Doc {i} · {len(doc)} chars"
            if tok is not None:
                label += f" · {tok} tokens"
            label += cap_note if i == 1 else ""
            with st.expander(label, expanded=(i == 1)):
                st.text(doc)
    elif diag.get("hyde_used"):
        st.warning("HyDE ran but no documents were parsed from the LLM response.")

    if retrieval.has_ads:
        st.markdown("**Catalog matches (top ads)**")
        for j, ad in enumerate(retrieval.ads, 1):
            score = ad.relevance_score
            st.markdown(f"{j}. **{ad.title}** — score {score:.3f}" if score else f"{j}. **{ad.title}**")
    else:
        st.caption("No ads returned from the pipeline.")

    metrics = {k: v for k, v in diag.items() if k not in ("hyde_documents", "retrieval_query")}
    if metrics:
        with st.expander("Timing & config", expanded=False):
            st.json(metrics)


def _render_flow_ad_panel(manager: ConversationManager, ad_mode: str) -> None:
    """Dev/flow helper: surface ads even when the mode hides them (e.g. inline)."""
    st.markdown(f"**Ad mode:** {AD_MODE_LABELS.get(ad_mode, ad_mode)}")
    _render_retrieval_debug(manager.last_retrieval)

    if not _ad_display_state_matches_mode(manager, ad_mode):
        cached = getattr(manager, "last_retrieval_ad_mode", None)
        if manager.last_retrieval and manager.last_retrieval.has_ads and cached and cached != ad_mode:
            st.caption(
                f"Ad cached from **{AD_MODE_LABELS.get(cached, cached)}** — "
                "send a message to refresh for the selected mode."
            )
        else:
            st.caption("No ad retrieved yet — send a message with **Inject ad every turn** enabled.")
        return

    if ad_mode == "inline_persuasive":
        with st.expander("Candidate products shown to the LLM (title + CTA only)", expanded=True):
            st.markdown(format_products_block(manager.last_retrieval.ads))
        st.caption(
            "Inline mode weaves the ad into the assistant reply; "
            "the product name is a clickable link in the text."
        )
        return

    injector = get_injector(ad_mode)
    result = injector.inject(manager.last_retrieval, manager.messages)
    primary = manager.last_retrieval.primary if manager.last_retrieval else None

    if result.display_payload:
        primary = manager.last_retrieval.primary if manager.last_retrieval else None
        _render_ad_banner(
            result.display_payload,
            ad_mode=ad_mode,
            manager=manager,
            turn=manager.turn_count,
            ad=primary,
        )
def render_trial_chat(
    manager: ConversationManager,
    ad_mode: str,
    flow_test: bool = False,
) -> bool:
    """
    Main chat interface. Returns True when the trial ends
    (user clicks "I've finished" or max turns reached).
    """
    start_ad_click_server()
    register_click_state(manager.logger, manager, ad_mode)
    inject_ad_click_tracker()

    # Task reminder at top
    if manager.task:
        st.caption(f"📝 {manager.task.participant_prompt}")

    # Turn progress + finish button in sidebar
    with st.sidebar:
        progress = min(manager.turn_count / MAX_TURNS_PER_TRIAL, 1.0)
        st.progress(progress, text=f"Turn {manager.turn_count} / {MAX_TURNS_PER_TRIAL}")

        # "I've finished" button — visible from manager.finish_from onwards
        if manager.turn_count >= manager.finish_from:
            if manager.turn_count < manager.min_turns:
                st.info(
                    f"💬 Keep chatting — you need at least {manager.min_turns} turns "
                    "before you can finish."
                )
            else:
                st.success("You can keep chatting or finish when you're ready.")
            if st.button("🏁 I've finished", type="primary", use_container_width=True):
                return True

    _render_chat_history(manager, ad_mode)

    # Dev flow: always show what was retrieved / shown to the LLM
    if flow_test:
        with st.expander("🎯 Ad debug (dev=flow)", expanded=True):
            _render_flow_ad_panel(manager, ad_mode)

    # Compact ads above chat input (banner where applicable)
    _render_turn_ads(manager, ad_mode)

    # Max turns reached → auto-end
    if manager.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        return True

    # Chat input
    if user_input := st.chat_input("Send a message..."):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            with st.chat_message("user"):
                st.markdown(user_input.strip())
            with st.chat_message("assistant"):
                st.write_stream(manager.process_user_message_stream(user_input.strip()))
            st.rerun()

    return False


def _render_ad_card(payload: dict, container=None, *, ad_mode: str | None = None) -> None:
    """Backward-compatible alias — banner is always full width."""
    _ = container
    _render_ad_banner(payload, ad_mode=ad_mode)


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
# WORKFLOW B — INSTRUCTIONS
# ═══════════════════════════════════════════════════════════════

def render_instructions() -> bool:
    """Brief task explanation before warm-up."""
    st.header("About This Study")
    st.markdown(
        "You will chat with an AI shopping assistant across several "
        "short conversations. Each conversation will present you with "
        "a different shopping task.\n\n"
        "After each conversation, you will answer a few brief questions "
        "about your experience.\n\n"
        "Take your time and interact naturally with the assistant."
    )
    return st.button("Begin", type="primary")


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — WARM-UP CHAT
# ═══════════════════════════════════════════════════════════════

def render_warmup_chat(manager: ConversationManager) -> bool:
    """
    Warm-up conversation — no ads, no Likert after.
    Returns True when user clicks 'Done'.
    """
    st.header("Warm-Up Conversation")
    st.info(
        "This is a practice conversation to get familiar with the interface. "
        "Chat naturally with the assistant."
    )

    for msg in manager.messages:
        with st.chat_message(msg["role"]):
            _render_chat_message(msg)

    if manager.turn_count >= 1:
        st.divider()
        if st.button("Done — continue to study", type="primary"):
            return True

    if user_input := st.chat_input("Send a message..."):
        if user_input.strip():
            with st.chat_message("user"):
                st.markdown(user_input.strip())
            with st.chat_message("assistant"):
                st.write_stream(manager.process_user_message_stream(user_input.strip()))
            st.rerun()

    return False


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — FIRST IMPRESSION (non-Likert)
# ═══════════════════════════════════════════════════════════════

def render_first_impression() -> Optional[dict]:
    """
    Lightweight baseline — no Likert scales.

    Collects:
      - first_impression_text (free-text)
      - reuse_intent (Yes / Maybe / No)
      - sentiment_label (Negative / Neutral / Positive)
    """
    st.header("Your First Impression")
    st.caption("Please share your initial thoughts about the system.")

    text = st.text_area(
        "1. Please describe your first impression of the system after your initial interaction in one sentence.",
        key="first_impression_text",
    )

    sentiment = st.radio(
        "2. Overall, how would you describe your experience so far?",
        ["Negative", "Neutral", "Positive"],
        index=None,
        horizontal=True,
        key="first_impression_sentiment",
    )

    reuse = st.radio(
        "3. Based on your initial interaction, would you use this assistant again?",
        ["Yes", "Maybe", "No"],
        index=None,
        horizontal=True,
        key="first_impression_reuse",
    )

    all_filled = bool(text and reuse and sentiment)
    if all_filled and st.button("Continue", type="primary"):
        return {
            "first_impression_text": text,
            "reuse_intent": reuse,
            "sentiment_label": sentiment,
        }
    elif not all_filled:
        st.info("Please answer all questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — CONDITION INTRO
# ═══════════════════════════════════════════════════════════════

def render_condition_intro(
    condition_number: int,
    total_conditions: int,
    condition_id: str,
    task_prompt: str,
) -> bool:
    """Show which condition + task is next."""
    label = CONDITION_LABELS.get(condition_id, condition_id)
    st.header(f"Conversation {condition_number} of {total_conditions}")
    st.caption(f"Condition: {label}")
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
# WORKFLOW B — CONDITION CHAT
# ═══════════════════════════════════════════════════════════════

def render_condition_chat(
    manager: ConversationManager,
    condition_id: str,
    flow_test: bool = False,
    calibration: bool = False,
) -> bool:
    """
    Condition-aware chat interface.

    Handles no_ads (no ad injection) and ad conditions (single ad at ad_turn).
    In calibration mode, shows an early-exit button (researcher can end anytime
    after min_turns). In production/dev-flow, participants must complete all turns.
    """
    from core.config import CONDITION_AD_MODE

    ad_mode = CONDITION_AD_MODE.get(condition_id, "")
    start_ad_click_server()
    register_click_state(manager.logger, manager, condition_id)
    inject_ad_click_tracker()

    label = CONDITION_LABELS.get(condition_id, condition_id)

    if manager.task:
        st.caption(f"📝 {manager.task.participant_prompt}")

    with st.sidebar:
        progress = min(manager.turn_count / MAX_TURNS_PER_TRIAL, 1.0)
        st.progress(progress, text=f"Turn {manager.turn_count} / {MAX_TURNS_PER_TRIAL}")
        st.caption(f"Condition: {label}")

        if calibration and manager.turn_count >= manager.finish_from:
            if manager.turn_count < manager.min_turns:
                st.info(
                    f"💬 Keep chatting — you need at least {manager.min_turns} turns "
                    "before you can finish."
                )
            else:
                st.success("You can keep chatting or finish when you're ready.")
            if st.button("🏁 I've finished", type="primary", use_container_width=True):
                return True

    _render_chat_history(manager, ad_mode)

    if flow_test:
        with st.expander("🎯 Ad debug (dev=flow)", expanded=True):
            _render_flow_ad_panel(manager, ad_mode)

    if condition_id != "no_ads":
        _render_turn_ads(manager, ad_mode)

    if manager.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        return True

    if user_input := st.chat_input("Send a message..."):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            with st.chat_message("user"):
                st.markdown(user_input.strip())
            with st.chat_message("assistant"):
                st.write_stream(manager.process_user_message_stream(user_input.strip()))
            st.rerun()

    return False


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — TASK CONCLUSION
# ═══════════════════════════════════════════════════════════════

def render_condition_conclusion(
    condition_number: int,
    total_conditions: int,
    task_title: str,
    task_prompt: str,
) -> Optional[dict]:
    """
    Post-chat conclusion screen: user writes their findings/results.

    Returns dict on submit, None otherwise.
    """
    st.header(f"Conversation {condition_number} of {total_conditions} — Your Findings")
    st.caption("Before moving on, please summarise what you learned from this conversation.")

    st.markdown(
        f"<div style='text-align:center; font-size:1.1em; padding:30px 20px; "
        f"background:#1a1d24; border-radius:12px; margin:20px 0;'>"
        f"<strong>{task_title}</strong><br><br>"
        f"{task_prompt}"
        f"</div>",
        unsafe_allow_html=True,
    )

    conclusion = st.text_area(
        "What did you find? What conclusions or decisions did you reach?",
        height=250,
        placeholder="Describe what information you found, what you decided, or what you learned...",
        key=f"condition_conclusion_{condition_number}",
    )

    if st.button("Submit findings", type="primary"):
        if not conclusion.strip():
            st.warning("Please write something before submitting.")
            return None
        return {"conclusion": conclusion.strip(), "task_title": task_title}

    return None


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — POST-CONDITION SURVEY
# ═══════════════════════════════════════════════════════════════

def render_post_condition_survey(condition_number: int) -> Optional[dict]:
    """
    12-item Likert survey after each condition (4 constructs × 3 items each).
    """
    st.header(f"Post-Conversation Survey")
    st.caption("Please rate the following statements about the conversation you just had (1 = Strongly disagree, 7 = Strongly agree).")

    responses: dict[str, int] = {}
    all_answered = True

    for item in POST_CONDITION_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(POST_CONDITION_SCALE_MIN, POST_CONDITION_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"post_condition_{condition_number}_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    if all_answered and st.button("Continue", type="primary"):
        invalid = [
            iid for iid, v in responses.items()
            if not (POST_CONDITION_SCALE_MIN <= v <= POST_CONDITION_SCALE_MAX)
        ]
        if invalid:
            st.error(f"Invalid response values detected ({invalid}). Please re-select those items.")
            return None
        return responses
    elif not all_answered:
        st.info("Please answer all questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# WORKFLOW B — GLOBAL EVALUATION
# ═══════════════════════════════════════════════════════════════

def render_global_evaluation() -> Optional[dict]:
    """
    End-of-session global evaluation + open-ended debrief.
    """
    st.header("Final Evaluation")
    st.caption("Please reflect on the entire session.")

    responses: dict[str, int | str] = {}
    all_answered = True

    for item in GLOBAL_EVAL_ITEMS:
        value = st.radio(
            item["text"],
            options=list(range(GLOBAL_EVAL_SCALE_MIN, GLOBAL_EVAL_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"global_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    st.subheader("Debrief")
    open_text = st.text_area(GLOBAL_OPEN_ENDED_PROMPT, key="global_open_ended")
    responses["open_ended"] = open_text

    if all_answered and st.button("Submit", type="primary"):
        invalid = [
            iid for iid, v in responses.items()
            if isinstance(v, int) and not (GLOBAL_EVAL_SCALE_MIN <= v <= GLOBAL_EVAL_SCALE_MAX)
        ]
        if invalid:
            st.error(f"Invalid response values detected ({invalid}). Please re-select those items.")
            return None
        return responses
    elif not all_answered:
        st.info("Please answer all Likert questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# ADS AWARENESS  (Section 1 of post-experiment)
# ═══════════════════════════════════════════════════════════════

def render_ads_awareness() -> Optional[dict]:
    st.header("Ads Awareness")
    st.caption("The following questions refer to your experience during the interaction with the chatbot.")

    responses: dict = {}
    all_answered = True

    for item in ADS_AWARENESS_CATEGORICAL:
        value = st.radio(
            item["text"],
            item["options"],
            index=None,
            horizontal=True,
            key=f"ads_aware_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    for item in ADS_AWARENESS_OPEN_ENDED:
        value = st.text_area(item["text"], key=f"ads_aware_{item['id']}")
        responses[item["id"]] = value

    st.divider()
    if all_answered and st.button("Continue", type="primary"):
        return responses
    elif not all_answered:
        st.info("Please answer all questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# ADS RECALL / INTERPRETATION  (Section 2 of post-experiment)
# ═══════════════════════════════════════════════════════════════

def render_ads_recall() -> Optional[dict]:
    st.header("Ads Recall / Interpretation")
    st.caption("The following questions refer to specific pieces of content that may have appeared during your interaction.")

    responses: dict = {}
    all_answered = True

    for item in ADS_RECALL_CATEGORICAL:
        value = st.radio(
            item["text"],
            item["options"],
            index=None,
            horizontal=True,
            key=f"ads_recall_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    st.markdown("**Rate your agreement with the following:**")

    for item in ADS_RECALL_LIKERT:
        if item["id"] == "recall_rating":
            value = st.radio(
                item["text"],
                options=list(range(ADS_RECALL_SCALE_MIN, ADS_RECALL_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"ads_recall_{item['id']}",
            )
        else:
            value = st.radio(
                item["text"],
                options=list(range(ADS_RECALL_SCALE_MIN, ADS_RECALL_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"ads_recall_{item['id']}",
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
# ADS PERCEPTION  (Section 3 of post-experiment)
# ═══════════════════════════════════════════════════════════════

def render_ads_perception() -> Optional[dict]:
    st.header("Ads Perception")
    st.caption("Please rate your level of agreement with each statement.")

    responses: dict = {}
    all_answered = True

    for item in ADS_PERCEPTION_LIKERT:
        value = st.radio(
            item["text"],
            options=list(range(ADS_PERCEPTION_SCALE_MIN, ADS_PERCEPTION_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"ads_perception_{item['id']}",
        )
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    for item in ADS_PERCEPTION_OPEN_ENDED:
        value = st.text_area(item["text"], key=f"ads_perception_{item['id']}")
        responses[item["id"]] = value

    st.divider()
    if all_answered and st.button("Continue", type="primary"):
        return responses
    elif not all_answered:
        st.info("Please answer all Likert questions to continue.")
    return None


# ═══════════════════════════════════════════════════════════════
# LLM PERFORMANCE EVALUATION  (Section 4 of post-experiment)
# 5 categories × 3 items = 15 Likert items
# ═══════════════════════════════════════════════════════════════

def render_llm_evaluation() -> Optional[dict]:
    st.header("LLM Performance Evaluation")
    st.caption("Please rate your level of agreement with each statement (1 = Strongly disagree, 7 = Strongly agree).")

    responses: dict = {}
    all_answered = True

    for category, items in LLM_EVAL_CATEGORIES.items():
        st.subheader(category)
        for item in items:
            value = st.radio(
                item["text"],
                options=list(range(LLM_EVAL_SCALE_MIN, LLM_EVAL_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"llm_eval_{item['id']}",
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
# GODSPEED (simplified)  (Section 5 of post-experiment)
# 7 semantic differentials + 2 re-ask Likerts
# ═══════════════════════════════════════════════════════════════

def render_godspeed() -> Optional[dict]:
    st.header("Overall Experience")
    st.caption("Please rate your impression of the chatbot on the following scales (1 = left descriptor, 7 = right descriptor).")

    responses: dict = {}
    all_answered = True

    for item in GODSPEED_SEMANTIC:
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{item['left']}**")
        with col2:
            value = st.radio(
                item["text"],
                options=list(range(GODSPEED_SCALE_MIN, GODSPEED_SCALE_MAX + 1)),
                format_func=lambda v: f"{v}",
                horizontal=True,
                index=None,
                key=f"godspeed_{item['id']}",
                label_visibility="collapsed",
            )
        with col3:
            st.markdown(f"**{item['right']}**")
        if value is None:
            all_answered = False
        else:
            responses[item["id"]] = value

    st.divider()
    st.markdown("**Final questions about your experience:**")
    for item in GODSPEED_REASK_LIKERT:
        value = st.radio(
            item["text"],
            options=list(range(GODSPEED_SCALE_MIN, GODSPEED_SCALE_MAX + 1)),
            format_func=lambda v: f"{v}",
            horizontal=True,
            index=None,
            key=f"godspeed_{item['id']}",
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
# DEMOGRAPHICS (post-experiment, Section 6 – optional)
# ═══════════════════════════════════════════════════════════════

def render_demographics_end() -> Optional[dict]:
    st.header("Demographics and Usage")
    st.caption("All fields are optional.")

    responses: dict = {}

    for item in DEMOGRAPHICS_END_TEXT:
        value = st.text_input(item["text"], key=f"demo_end_{item['id']}")
        responses[item["id"]] = value

    for item in DEMOGRAPHICS_END_CATEGORICAL:
        value = st.radio(
            item["text"],
            item["options"],
            index=None,
            horizontal=True,
            key=f"demo_end_{item['id']}",
        )
        responses[item["id"]] = value

    st.divider()
    if st.button("Continue", type="primary"):
        return responses
    return None


# ═══════════════════════════════════════════════════════════════
# DECEPTION DISCLOSURE  (Section 7 of post-experiment)
# ═══════════════════════════════════════════════════════════════

def render_deception_disclosure() -> Optional[dict]:
    st.header("Deception Disclosure")
    st.markdown(DECEPTION_DISCLOSURE_TEXT)
    st.divider()

    withdraw = st.text_input(
        'Type "Withdraw" below if you would like to withdraw from this study. Otherwise, leave this blank and continue.',
        key="deception_withdraw",
    )

    if st.button("Continue", type="primary"):
        withdrew = withdraw.strip().lower() == "withdraw"
        return {"withdrew": withdrew, "withdraw_text": withdraw.strip() if withdrew else ""}
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
