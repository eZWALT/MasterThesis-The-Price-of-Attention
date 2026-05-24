"""
Developer UI: sidebar controls and free-form chat mode (?dev=true).
"""

from __future__ import annotations

import streamlit as st
from loguru import logger as log

from core.config import (
    AD_MODES,
    AD_MODE_LABELS,
    AD_SIDE_PANEL_MODES,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    MAX_TOKENS_RANGE,
    TEMPERATURE_RANGE,
    MAX_TURNS_PER_TRIAL,
)
from core.conversation import ConversationManager
from core.experiment import TASK_CATALOG, TASK_BY_ID
from core.ad_injection import get_ad, get_injector
from core.ui.screens import _render_ad_card, _call_llm_with_spinner
# DEV helpers live in participant to avoid circular imports
from core.ui.participant import _render_dev_ad_controls, _sync_dev_overrides


def render_dev_sidebar():
    with st.sidebar:
        st.markdown("## ⚙️ Developer Settings")
        model = st.text_input("Model", value=DEFAULT_MODEL)
        temperature = st.slider(
            "Temperature",
            min_value=TEMPERATURE_RANGE[0],
            max_value=TEMPERATURE_RANGE[1],
            value=DEFAULT_TEMPERATURE,
            step=0.01,
        )
        max_tokens = st.slider(
            "Max Tokens",
            min_value=MAX_TOKENS_RANGE[0],
            max_value=MAX_TOKENS_RANGE[1],
            value=DEFAULT_MAX_TOKENS,
            step=8,
        )
        st.divider()
        ad_mode = st.selectbox(
            "📊 Advertising Mode",
            AD_MODES,
            format_func=lambda k: AD_MODE_LABELS.get(k, k),
        )
        st.divider()
        task_options = ["(none)"] + [t.id for t in TASK_CATALOG]
        task_choice = st.selectbox(
            "📝 Task",
            task_options,
            format_func=lambda k: TASK_BY_ID[k].title if k in TASK_BY_ID else k,
        )
        task = TASK_BY_ID.get(task_choice) if task_choice != "(none)" else None
        st.divider()
        if st.button("🧹 Clear Chat"):
            st.session_state.dev_manager = None
            st.session_state.dev_trial_complete = False
            st.session_state.logger.clear()
            st.rerun()
        st.divider()
        mgr = st.session_state.dev_manager
        with st.expander("🎯 Ad overrides", expanded=bool(st.session_state.get("dev_force_ad"))):
            _render_dev_ad_controls(mgr=mgr)
        st.divider()
        if mgr:
            progress = min(mgr.turn_count / MAX_TURNS_PER_TRIAL, 1.0)
            st.progress(progress, text=f"Turn {mgr.turn_count} / {MAX_TURNS_PER_TRIAL}")
            st.markdown(f"**Can end:** {mgr.can_end}")
            st.markdown("**System prompt:**")
            st.code(mgr.system_prompt, language="text")
        st.divider()
        with st.expander("🧪 Debug / Logs"):
            st.json(st.session_state.logger.to_dicts())
        with st.expander("📐 Attention Shift History"):
            shifts = [e for e in st.session_state.logger.entries if e.event == "attention_shift"]
            if shifts:
                for s in shifts:
                    st.write(f"Δ = {s.data['divergence']:.6f}  ({s.data['method']})")
            else:
                st.caption("No attention shifts recorded yet.")
        if st.button("💾 Export Logs (JSONL)"):
            path = st.session_state.logger.export_jsonl()
            st.success(f"Exported to {path}")
    return model, temperature, max_tokens, ad_mode, task


def run_dev_mode():
    """Free-form chat with full developer controls."""
    model, temperature, max_tokens, ad_mode, task = render_dev_sidebar()

    mgr = st.session_state.dev_manager
    needs_new = (
        mgr is None
        or mgr.model != model
        or mgr.temperature != temperature
        or mgr.max_tokens != max_tokens
        or (task and (not mgr.task or mgr.task.id != task.id))
        or (not task and mgr.task)
    )
    if needs_new:
        mgr = ConversationManager(
            ad_mode=ad_mode,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            task=task,
            logger=st.session_state.logger,
            force_ad=st.session_state.get("dev_force_ad", False),
        )
        st.session_state.dev_manager = mgr
    elif mgr.ad_mode != ad_mode:
        # Switch ad mode in-place — preserves conversation history
        mgr.ad_mode = ad_mode
        st.session_state.dev_manager = mgr

    # Always sync force_ad / rag_mode onto the live manager
    _sync_dev_overrides(mgr)

    if task:
        with st.expander("📝 Task Prompt", expanded=False):
            st.markdown(f"**{task.title}** ({task.genre})")
            st.write(task.participant_prompt)

    # Active ad mode badge
    from core.config import AD_MODE_LABELS
    st.caption(f"**Ad mode:** {AD_MODE_LABELS.get(ad_mode, ad_mode)}")

    if st.session_state.dev_trial_complete:
        st.divider()
        st.success("🎉 This conversation is complete.")
        if st.button("🔄 Start New Trial"):
            st.session_state.dev_manager = None
            st.session_state.dev_trial_complete = False
            st.rerun()
        return

    show_side = ad_mode in AD_SIDE_PANEL_MODES
    if show_side:
        col_main, col_side = st.columns([3, 1])
    else:
        col_main = st.container()
        col_side = None

    with col_main:
        for msg in mgr.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Render manually-injected ad from sidebar button
        manual_ad_result = st.session_state.pop("dev_manual_ad", None)
        if manual_ad_result and manual_ad_result.display_payload:
            _render_ad_card(col_main, manual_ad_result.display_payload)

    if show_side and mgr.should_inject_ad and col_side:
        last_user = next(
            (m["content"] for m in reversed(mgr.messages) if m["role"] == "user"),
            "",
        )
        ad = get_ad(query=last_user, context=mgr.messages)
        injector = get_injector(ad_mode)
        result = injector.inject(ad, mgr.messages)
        if result.display_payload:
            _render_ad_card(col_side, result.display_payload)

    # Sponsored suggestion chips
    if ad_mode == "sponsored_conversational" and mgr.should_inject_ad:
        last_user = next(
            (m["content"] for m in reversed(mgr.messages) if m["role"] == "user"),
            "",
        )
        ad = get_ad(query=last_user, context=mgr.messages)
        injector = get_injector(ad_mode)
        result = injector.inject(ad, mgr.messages)
        if result.suggestions:
            st.markdown("### 🔍 Sponsored Suggestions")
            for suggestion in result.suggestions:
                if st.button(suggestion, key=f"dev_sug_{suggestion[:20]}"):
                    _sync_dev_overrides(mgr)
                    _call_llm_with_spinner(mgr, suggestion)
                    st.rerun()

    if mgr.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        st.session_state.dev_trial_complete = True
        st.rerun()
        return

    if user_input := st.chat_input("Send a message..."):
        if not user_input.strip():
            st.warning("Please enter a message before sending.")
        else:
            _sync_dev_overrides(mgr)
            _call_llm_with_spinner(mgr, user_input.strip())
            log.info(
                "Dev turn {} | ad_mode={} | exp={}",
                mgr.turn_count, ad_mode, st.session_state.logger.experiment_id,
            )
            st.rerun()
