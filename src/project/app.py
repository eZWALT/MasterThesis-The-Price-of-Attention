"""
TARA — Streamlit entrypoint.

This is the main chat page. Additional pages live in pages/.
All business logic is delegated to the `core` package.

Two UI modes:
  - Participant mode (default): minimal chat + task prompt + turn counter.
  - Developer mode (?dev=true): exposes model params, ad mode selector,
    debug logs, and attention shift history.
"""

import streamlit as st
import uuid

from core import (
    AD_MODES,
    AD_MODE_LABELS,
    AD_SIDE_PANEL_MODES,
    APP_TITLE,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    MAX_TOKENS_RANGE,
    PAGE_TITLE,
    TEMPERATURE_RANGE,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    TASK_CATALOG,
    TASK_BY_ID,
    DEV_QUERY_PARAM,
    get_ad,
    get_injector,
    ConversationManager,
    ExperimentLogger,
    TaskDefinition,
)


# =============================================================
# HELPERS
# =============================================================

def is_dev_mode() -> bool:
    """Check whether the developer mode query param is set."""
    return st.query_params.get(DEV_QUERY_PARAM, "").lower() in ("true", "1", "yes")


# =============================================================
# SESSION STATE
# =============================================================

def init_session_state():
    """Initialize Streamlit session defaults."""
    if "logger" not in st.session_state:
        st.session_state.logger = ExperimentLogger()
    if "conv_manager" not in st.session_state:
        st.session_state.conv_manager = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    if "selected_task" not in st.session_state:
        st.session_state.selected_task = None
    if "trial_complete" not in st.session_state:
        st.session_state.trial_complete = False


def get_or_create_manager(
    ad_mode: str,
    model: str,
    temperature: float,
    max_tokens: int,
    task: TaskDefinition | None = None,
) -> ConversationManager:
    """Return existing ConversationManager or create a new one when settings change."""
    mgr = st.session_state.conv_manager
    task_id = task.id if task else None
    current_task_id = mgr.task.id if mgr and mgr.task else None

    needs_new = (
        mgr is None
        or mgr.ad_mode != ad_mode
        or mgr.model != model
        or mgr.temperature != temperature
        or mgr.max_tokens != max_tokens
        or task_id != current_task_id
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
        # Preserve conversation history if only model params changed (not task)
        if (
            st.session_state.conv_manager is not None
            and task_id == current_task_id
        ):
            mgr.messages = st.session_state.conv_manager.messages
            mgr.conversation_id = st.session_state.conv_manager.conversation_id
        st.session_state.conv_manager = mgr
    return mgr


def clear_session():
    """Reset conversation and logs."""
    st.session_state.logger.clear()
    if st.session_state.conv_manager:
        st.session_state.conv_manager.reset()
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.selected_task = None
    st.session_state.trial_complete = False
    st.rerun()


def start_new_trial():
    """Reset conversation state for a new trial, keeping logs."""
    if st.session_state.conv_manager:
        st.session_state.conv_manager.reset()
    st.session_state.conversation_id = str(uuid.uuid4())
    st.session_state.selected_task = None
    st.session_state.trial_complete = False
    st.rerun()


# =============================================================
# SIDEBAR — developer-only controls
# =============================================================

def render_dev_sidebar():
    """Full sidebar with model params, ad mode, debug — only in dev mode."""
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
            clear_session()

        st.divider()

        # Show turn info
        mgr = st.session_state.conv_manager
        if mgr:
            st.markdown(f"**Turn:** {mgr.turn_count} / {MAX_TURNS_PER_TRIAL}")
            st.markdown(f"**Can end:** {mgr.can_end}")
            st.markdown(f"**System prompt:**")
            st.code(mgr.system_prompt, language="text")

        st.divider()

        with st.expander("🧪 Debug / Logs"):
            st.json(st.session_state.logger.to_dicts())

        with st.expander("📐 Attention Shift History"):
            shifts = [
                e for e in st.session_state.logger.entries
                if e.event == "attention_shift"
            ]
            if shifts:
                for s in shifts:
                    st.write(f"Δ = {s.data['divergence']:.6f}  ({s.data['method']})")
            else:
                st.caption("No attention shifts recorded yet.")

        if st.button("💾 Export Logs (JSON)"):
            path = st.session_state.logger.export_json()
            st.success(f"Exported to {path}")

    return model, temperature, max_tokens, ad_mode, task


def render_participant_sidebar():
    """Minimal sidebar for participants — only turn progress and end-trial."""
    with st.sidebar:
        st.markdown("## 💬 Conversation")

        mgr = st.session_state.conv_manager
        if mgr:
            progress = min(mgr.turn_count / MAX_TURNS_PER_TRIAL, 1.0)
            st.progress(progress, text=f"Turn {mgr.turn_count} / {MAX_TURNS_PER_TRIAL}")

            if mgr.can_end and not st.session_state.trial_complete:
                st.success(f"✓ You've reached the minimum of {MIN_TURNS_PER_TRIAL} turns. "
                           "You can continue chatting or end this conversation.")
                if st.button("✅ End Conversation"):
                    st.session_state.trial_complete = True
                    st.session_state.logger.log(
                        "trial_ended_by_user",
                        {"turn": mgr.turn_count, "task": mgr.task.id if mgr.task else None},
                        mgr.ad_mode,
                        mgr.conversation_id,
                    )
                    st.rerun()
        else:
            st.caption("Select a task to begin.")


# =============================================================
# TASK SELECTION (Participant Mode)
# =============================================================

def render_task_selection():
    """Show task cards for the participant to pick from."""
    st.markdown("### 📝 Choose your conversation task")
    st.caption("Pick one of the tasks below and start chatting with the assistant.")

    cols = st.columns(2)
    for i, task in enumerate(TASK_CATALOG):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{task.title}**")
                st.markdown(f"*{task.genre}*")
                st.write(task.participant_prompt)
                if st.button("Start", key=f"task_{task.id}"):
                    st.session_state.selected_task = task
                    st.rerun()


# =============================================================
# AD PANEL
# =============================================================

def render_ad_panel(container, display_payload):
    """Render a styled ad card inside a given Streamlit container."""
    if not display_payload:
        return
    with container:
        st.markdown(
            f"""
            <div style="background-color: #2a1f0e; border-left: 4px solid #ff9800;
                        padding: 12px; border-radius: 8px; margin-top: 8px;">
                <h4 style="margin: 0 0 6px 0; color: #e0e0e0;">{display_payload['header']}</h4>
                <p style="font-weight: bold; margin: 0 0 4px 0; color: #f5f5f5;">{display_payload['title']}</p>
                <p style="margin: 0; color: #bbb;">{display_payload['text']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================
# SUGGESTION ADS
# =============================================================

def render_suggestion_ads(ad_mode, manager: ConversationManager):
    """Render sponsored suggestion buttons (only on ad turns)."""
    if ad_mode != "3_suggestions":
        return
    if not manager.should_inject_ad:
        return
    ad = get_ad()
    injector = get_injector(ad_mode)
    result = injector.inject(ad, manager.messages)
    if result.suggestions:
        st.markdown("### 🔍 Sponsored Suggestions")
        for suggestion in result.suggestions:
            if st.button(suggestion):
                manager.logger.log(
                    "suggestion_clicked",
                    {"suggestion": suggestion, "turn": manager.turn_count},
                    ad_mode,
                    manager.conversation_id,
                )
                manager.process_user_message(suggestion)
                st.rerun()


# =============================================================
# CHAT DISPLAY
# =============================================================

def render_chat(ad_mode, manager: ConversationManager):
    """Render chat messages and optional ad side panel."""
    show_side = ad_mode in AD_SIDE_PANEL_MODES

    if show_side:
        col_main, col_side = st.columns([3, 1])
    else:
        col_main, col_side = st.columns([1, 0.01])

    with col_main:
        for msg in manager.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Side-panel ads only on ad injection turns
    if show_side and manager.should_inject_ad:
        ad = get_ad()
        injector = get_injector(ad_mode)
        result = injector.inject(ad, manager.messages)
        render_ad_panel(col_side, result.display_payload)


# =============================================================
# TRIAL COMPLETE
# =============================================================

def render_trial_complete(manager: ConversationManager):
    """Show trial completion message and next-trial button."""
    st.divider()
    st.success("🎉 This conversation is complete. Thank you!")
    st.info(f"Turns completed: {manager.turn_count}")

    if is_dev_mode():
        if st.button("🔄 Start New Trial"):
            start_new_trial()
    else:
        st.caption("The researcher will guide you to the next step.")
        if st.button("Next"):
            start_new_trial()


# =============================================================
# CHAT INPUT
# =============================================================

def handle_chat_input(manager: ConversationManager):
    """Process user input through the ConversationManager pipeline."""
    if manager.must_end:
        st.caption(f"Maximum turns ({MAX_TURNS_PER_TRIAL}) reached.")
        if not st.session_state.trial_complete:
            st.session_state.trial_complete = True
            manager.logger.log(
                "trial_ended_max_turns",
                {"turn": manager.turn_count, "task": manager.task.id if manager.task else None},
                manager.ad_mode,
                manager.conversation_id,
            )
            st.rerun()
        return

    if user_input := st.chat_input("Send a message..."):
        manager.process_user_message(user_input)
        st.rerun()


# =============================================================
# MAIN
# =============================================================

def main():
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    st.title(APP_TITLE)

    init_session_state()

    dev = is_dev_mode()

    # ── Developer mode: full controls ─────────────────────────
    if dev:
        model, temperature, max_tokens, ad_mode, task = render_dev_sidebar()
        manager = get_or_create_manager(ad_mode, model, temperature, max_tokens, task)

        # Show task prompt if set
        if task:
            with st.expander("📝 Task Prompt", expanded=False):
                st.markdown(f"**{task.title}** ({task.genre})")
                st.write(task.participant_prompt)

        if st.session_state.trial_complete:
            render_trial_complete(manager)
        else:
            render_chat(ad_mode, manager)
            render_suggestion_ads(ad_mode, manager)
            handle_chat_input(manager)

    # ── Participant mode: minimal UI ──────────────────────────
    else:
        render_participant_sidebar()
        task = st.session_state.selected_task

        # No task selected yet → show task picker
        if task is None:
            render_task_selection()
            return

        # Use defaults for participant mode — ad_mode is assigned by
        # the Experiment Controller (hardcoded for now, will be
        # parameterized when the Controller module is implemented).
        ad_mode = st.session_state.get("assigned_ad_mode", AD_MODES[1])
        manager = get_or_create_manager(
            ad_mode, DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, task
        )

        # Task banner
        st.info(f"**Task:** {task.participant_prompt}")

        if st.session_state.trial_complete:
            render_trial_complete(manager)
        else:
            render_chat(ad_mode, manager)
            render_suggestion_ads(ad_mode, manager)
            handle_chat_input(manager)


if __name__ == "__main__":
    main()
