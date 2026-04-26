"""
Developer UI: sidebar controls and free-form chat mode (?dev=true).
"""

from __future__ import annotations

import streamlit as st

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
from core.ui.screens import _render_ad_card


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
        if mgr:
            st.markdown(f"**Turn:** {mgr.turn_count} / {MAX_TURNS_PER_TRIAL}")
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
        if st.button("💾 Export Logs (JSON)"):
            path = st.session_state.logger.export_json()
            st.success(f"Exported to {path}")
    return model, temperature, max_tokens, ad_mode, task


def run_dev_mode():
    """Free-form chat with full developer controls."""
    model, temperature, max_tokens, ad_mode, task = render_dev_sidebar()

    mgr = st.session_state.dev_manager
    needs_new = (
        mgr is None
        or mgr.ad_mode != ad_mode
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
        )
        st.session_state.dev_manager = mgr

    if task:
        with st.expander("📝 Task Prompt", expanded=False):
            st.markdown(f"**{task.title}** ({task.genre})")
            st.write(task.participant_prompt)

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

    if show_side and mgr.should_inject_ad and col_side:
        ad = get_ad()
        injector = get_injector(ad_mode)
        result = injector.inject(ad, mgr.messages)
        if result.display_payload:
            _render_ad_card(col_side, result.display_payload)

    if mgr.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        st.session_state.dev_trial_complete = True
        st.rerun()
        return

    if user_input := st.chat_input("Send a message..."):
        mgr.process_user_message(user_input)
        st.rerun()
