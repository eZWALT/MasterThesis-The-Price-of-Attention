"""
TARA — Streamlit entrypoint.

Sequential experiment flow controlled by ExperimentController.

Screens (participant mode):
  consent → demographics → OCEAN → baseline → practice
  → [trial_intro → trial_chat → post_trial_survey] × N
  → final_survey → done

Developer mode (?dev=true) bypasses the flow and opens a free-form
chat with full parameter controls.
"""

import streamlit as st
import uuid

from core.config import (
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
    TRIALS_PER_SESSION,
    DEV_QUERY_PARAM,
    PRACTICE_SYSTEM_PROMPT_EXT,
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_OCEAN,
    SCREEN_BASELINE,
    SCREEN_PRACTICE,
    SCREEN_TRIAL_INTRO,
    SCREEN_TRIAL_CHAT,
    SCREEN_POST_TRIAL_SURVEY,
    SCREEN_FINAL_SURVEY,
    SCREEN_DONE,
)
from core.conversation import ConversationManager
from core.logger import ExperimentLogger
from core.experiment import (
    ExperimentController,
    TaskDefinition,
    TASK_CATALOG,
    TASK_BY_ID,
    score_ocean,
)
from core.ad_injection import get_ad, get_injector
from core.ui import (
    render_consent,
    render_demographics,
    render_ocean,
    render_baseline,
    render_practice,
    render_trial_intro,
    render_trial_chat,
    render_post_trial_survey,
    render_final_survey,
    render_done,
    _render_ad_card,
)


# =============================================================
# HELPERS
# =============================================================

def is_dev_mode() -> bool:
    return st.query_params.get(DEV_QUERY_PARAM, "").lower() in ("true", "1", "yes")


# =============================================================
# SESSION STATE
# =============================================================

def init_session_state():
    """Ensure every expected key exists in session_state."""
    if "logger" not in st.session_state:
        st.session_state.logger = ExperimentLogger()

    if "controller" not in st.session_state:
        pid = str(uuid.uuid4())[:8]
        ctrl = ExperimentController(participant_id=pid, n_trials=TRIALS_PER_SESSION)
        ctrl.build_trial_plan()
        st.session_state.controller = ctrl

    # ConversationManager instances — keyed by purpose
    if "practice_manager" not in st.session_state:
        st.session_state.practice_manager = None

    if "trial_manager" not in st.session_state:
        st.session_state.trial_manager = None

    # Dev mode state
    if "dev_manager" not in st.session_state:
        st.session_state.dev_manager = None
    if "dev_trial_complete" not in st.session_state:
        st.session_state.dev_trial_complete = False


def _get_or_create_practice_manager() -> ConversationManager:
    """Return a ConversationManager configured for the practice round."""
    mgr = st.session_state.practice_manager
    if mgr is None:
        # Practice: no ads, default model, custom system prompt extension
        practice_task = TaskDefinition(
            id="practice",
            title="Practice",
            genre="Practice",
            participant_prompt="Practice chatting with the assistant.",
            system_prompt_extension=PRACTICE_SYSTEM_PROMPT_EXT,
        )
        mgr = ConversationManager(
            ad_mode="1_classical_ui",  # irrelevant — ads won't trigger
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=practice_task,
            logger=st.session_state.logger,
        )
        st.session_state.practice_manager = mgr
    return mgr


def _get_or_create_trial_manager(task: TaskDefinition, ad_mode: str) -> ConversationManager:
    """Return a ConversationManager for the current trial, creating on demand."""
    mgr = st.session_state.trial_manager
    if mgr is None or mgr.task.id != task.id:
        mgr = ConversationManager(
            ad_mode=ad_mode,
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=task,
            logger=st.session_state.logger,
        )
        st.session_state.trial_manager = mgr
    return mgr


# =============================================================
# DEV MODE — full controls (unchanged from original)
# =============================================================

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

    # Get or create manager
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

    # Chat
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


# =============================================================
# PARTICIPANT MODE — sequential screen flow
# =============================================================

def run_participant_mode():
    """Drive the participant through the full experiment protocol."""
    ctrl: ExperimentController = st.session_state.controller
    scr = ctrl.current_screen

    # ── Progress indicator in sidebar ─────────────────────────
    _render_progress_sidebar(ctrl)

    # ── Screen dispatcher ─────────────────────────────────────
    if scr == SCREEN_CONSENT:
        if render_consent():
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DEMOGRAPHICS:
        result = render_demographics()
        if result is not None:
            ctrl.demographics = result
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_OCEAN:
        result = render_ocean()
        if result is not None:
            ctrl.ocean_raw = result
            ctrl.ocean_scores = score_ocean(result)
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_BASELINE:
        if render_baseline():
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_PRACTICE:
        mgr = _get_or_create_practice_manager()
        if render_practice(mgr):
            # Clean up practice manager
            st.session_state.practice_manager = None
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_TRIAL_INTRO:
        trial_cfg = ctrl.current_trial_config
        if trial_cfg:
            task: TaskDefinition = trial_cfg["task"]
            done = render_trial_intro(ctrl.trial_number, ctrl.n_trials, task.participant_prompt)
            if done:
                # Prepare trial manager
                st.session_state.trial_manager = None
                ctrl.advance()
                st.rerun()

    elif scr == SCREEN_TRIAL_CHAT:
        trial_cfg = ctrl.current_trial_config
        if trial_cfg:
            task = trial_cfg["task"]
            ad_mode = trial_cfg["ad_mode"]
            mgr = _get_or_create_trial_manager(task, ad_mode)
            if render_trial_chat(mgr, ad_mode):
                # Store trial data
                ctrl.trial_results.append({
                    "trial": ctrl.trial_number,
                    "task_id": task.id,
                    "ad_mode": ad_mode,
                    "turns": mgr.turn_count,
                    "messages": list(mgr.messages),
                })
                st.session_state.trial_manager = None
                ctrl.advance()
                st.rerun()

    elif scr == SCREEN_POST_TRIAL_SURVEY:
        result = render_post_trial_survey(ctrl.trial_number)
        if result is not None:
            ctrl.post_trial_surveys.append(result)
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_FINAL_SURVEY:
        result = render_final_survey()
        if result is not None:
            ctrl.final_survey = result
            # Export all collected data
            _export_session_data(ctrl)
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DONE:
        render_done()

    else:
        st.error(f"Unknown screen: {scr}")


def _render_progress_sidebar(ctrl: ExperimentController):
    """Minimal sidebar showing experiment progress."""
    with st.sidebar:
        st.markdown(f"**Participant:** `{ctrl.participant_id}`")
        scr = ctrl.current_screen
        # Map screen to friendly name
        labels = {
            SCREEN_CONSENT: "Consent",
            SCREEN_DEMOGRAPHICS: "Demographics",
            SCREEN_OCEAN: "Personality",
            SCREEN_BASELINE: "Baseline",
            SCREEN_PRACTICE: "Practice",
            SCREEN_TRIAL_INTRO: f"Trial {ctrl.trial_number}/{ctrl.n_trials} — Intro",
            SCREEN_TRIAL_CHAT: f"Trial {ctrl.trial_number}/{ctrl.n_trials} — Chat",
            SCREEN_POST_TRIAL_SURVEY: f"Trial {ctrl.trial_number}/{ctrl.n_trials} — Survey",
            SCREEN_FINAL_SURVEY: "Final Survey",
            SCREEN_DONE: "Done ✓",
        }
        st.caption(f"📍 {labels.get(scr, scr)}")


def _export_session_data(ctrl: ExperimentController):
    """Persist all collected data via the experiment logger."""
    logger: ExperimentLogger = st.session_state.logger
    logger.log("session_complete", {
        "participant_id": ctrl.participant_id,
        "demographics": ctrl.demographics,
        "ocean_raw": ctrl.ocean_raw,
        "ocean_scores": ctrl.ocean_scores,
        "trial_results": [
            {k: v for k, v in tr.items() if k != "messages"}
            for tr in ctrl.trial_results
        ],
        "post_trial_surveys": ctrl.post_trial_surveys,
        "final_survey": ctrl.final_survey,
    })
    logger.export_json()


# =============================================================
# MAIN
# =============================================================

def main():
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    st.title(APP_TITLE)
    init_session_state()

    if is_dev_mode():
        run_dev_mode()
    else:
        run_participant_mode()


if __name__ == "__main__":
    main()
