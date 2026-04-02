"""
TARA — Streamlit entrypoint.

This is the main chat page. Additional pages live in pages/.
All business logic is delegated to the `core` package.
"""

import streamlit as st
import uuid

from core import (
    AD_MODES,
    AD_MODE_LABELS,
    APP_TITLE,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    MAX_TOKENS_RANGE,
    PAGE_TITLE,
    TEMPERATURE_RANGE,
    get_ad,
    get_injector,
    ConversationManager,
    ExperimentLogger,
)


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


def get_or_create_manager(ad_mode, model, temperature, max_tokens) -> ConversationManager:
    """Return existing ConversationManager or create a new one when settings change."""
    mgr = st.session_state.conv_manager
    needs_new = (
        mgr is None
        or mgr.ad_mode != ad_mode
        or mgr.model != model
        or mgr.temperature != temperature
        or mgr.max_tokens != max_tokens
    )
    if needs_new:
        mgr = ConversationManager(
            ad_mode=ad_mode,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            logger=st.session_state.logger,
        )
        if st.session_state.conv_manager is not None:
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
    st.rerun()


# =============================================================
# SIDEBAR — developer-only controls
# =============================================================

def render_sidebar():
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

        if st.button("🧹 Clear Chat"):
            clear_session()

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

    return model, temperature, max_tokens, ad_mode


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
            <div style="background-color: #fff3e0; border-left: 4px solid #ff9800;
                        padding: 12px; border-radius: 8px; margin-top: 8px;">
                <h4 style="margin: 0 0 6px 0; color: #333;">{display_payload['header']}</h4>
                <p style="font-weight: bold; margin: 0 0 4px 0; color: #222;">{display_payload['title']}</p>
                <p style="margin: 0; color: #444;">{display_payload['text']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =============================================================
# SUGGESTION ADS
# =============================================================

def render_suggestion_ads(ad_mode, manager: ConversationManager):
    """Render sponsored suggestion buttons."""
    if ad_mode != "3_suggestions":
        return
    ad = get_ad()
    injector = get_injector(ad_mode)
    result = injector.inject(ad, manager.messages)
    if result.suggestions:
        st.markdown("### 🔍 Sponsored Suggestions")
        for suggestion in result.suggestions:
            if st.button(suggestion):
                manager.logger.log(
                    "suggestion_clicked", suggestion, ad_mode, manager.conversation_id
                )
                manager.process_user_message(suggestion)
                st.rerun()


# =============================================================
# CHAT DISPLAY
# =============================================================

def render_chat(ad_mode, manager: ConversationManager):
    """Render chat messages and optional ad side panel."""
    show_side = ad_mode in ("1_classical_ui", "4_adjacent")

    if show_side:
        col_main, col_side = st.columns([3, 1])
    else:
        col_main, col_side = st.columns([1, 0.01])

    with col_main:
        for msg in manager.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if show_side:
        ad = get_ad()
        injector = get_injector(ad_mode)
        result = injector.inject(ad, manager.messages)
        render_ad_panel(col_side, result.display_payload)


# =============================================================
# CHAT INPUT
# =============================================================

def handle_chat_input(manager: ConversationManager):
    """Process user input through the ConversationManager pipeline."""
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

    model, temperature, max_tokens, ad_mode = render_sidebar()
    manager = get_or_create_manager(ad_mode, model, temperature, max_tokens)

    render_chat(ad_mode, manager)
    render_suggestion_ads(ad_mode, manager)
    handle_chat_input(manager)


if __name__ == "__main__":
    main()
