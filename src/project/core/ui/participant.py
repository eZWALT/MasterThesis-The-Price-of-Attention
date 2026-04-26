"""
Participant flow: session state management, screen dispatcher,
progress sidebar, and dev-flow skip helpers.
"""

from __future__ import annotations

import uuid
import streamlit as st

from core.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    TRIALS_PER_SESSION,
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
from core.experiment import ExperimentController, TaskDefinition, TASK_CATALOG, score_ocean
from core.ui.screens import (
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
)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════

def init_session_state():
    """Ensure every expected key exists in st.session_state."""
    if "logger" not in st.session_state:
        st.session_state.logger = ExperimentLogger()

    if "controller" not in st.session_state:
        pid = str(uuid.uuid4())[:8]
        ctrl = ExperimentController(participant_id=pid, n_trials=TRIALS_PER_SESSION)
        ctrl.build_trial_plan()
        st.session_state.controller = ctrl

    if "practice_manager" not in st.session_state:
        st.session_state.practice_manager = None
    if "trial_manager" not in st.session_state:
        st.session_state.trial_manager = None

    # Dev mode state
    if "dev_manager" not in st.session_state:
        st.session_state.dev_manager = None
    if "dev_trial_complete" not in st.session_state:
        st.session_state.dev_trial_complete = False


# ═══════════════════════════════════════════════════════════════
# MANAGER FACTORIES
# ═══════════════════════════════════════════════════════════════

def _get_or_create_practice_manager() -> ConversationManager:
    mgr = st.session_state.practice_manager
    if mgr is None:
        practice_task = TaskDefinition(
            id="practice",
            title="Practice",
            genre="Practice",
            participant_prompt="Practice chatting with the assistant.",
            system_prompt_extension=PRACTICE_SYSTEM_PROMPT_EXT,
        )
        mgr = ConversationManager(
            ad_mode="1_classical_ui",
            model=DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=practice_task,
            logger=st.session_state.logger,
        )
        st.session_state.practice_manager = mgr
    return mgr


def _get_or_create_trial_manager(task: TaskDefinition, ad_mode: str) -> ConversationManager:
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


# ═══════════════════════════════════════════════════════════════
# DATA EXPORT
# ═══════════════════════════════════════════════════════════════

def export_session_data(ctrl: ExperimentController):
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


# ═══════════════════════════════════════════════════════════════
# DEV-FLOW SKIP HELPERS
# ═══════════════════════════════════════════════════════════════

def dev_inject_stub_data(ctrl: ExperimentController):
    """Inject minimal stub data so the controller doesn't break on skip."""
    scr = ctrl.current_screen
    if scr == SCREEN_DEMOGRAPHICS and not ctrl.demographics:
        ctrl.demographics = {"age": 0, "gender": "skip", "education": "skip"}
    elif scr == SCREEN_OCEAN and not ctrl.ocean_raw:
        ctrl.ocean_raw = {str(i): 4 for i in range(10)}
        ctrl.ocean_scores = score_ocean(ctrl.ocean_raw)
    elif scr == SCREEN_POST_TRIAL_SURVEY:
        ctrl.post_trial_surveys.append({"skipped": True})
    elif scr == SCREEN_FINAL_SURVEY:
        ctrl.final_survey = {"skipped": True}
        export_session_data(ctrl)
    elif scr == SCREEN_TRIAL_CHAT:
        ctrl.trial_results.append({
            "trial": ctrl.trial_number,
            "task_id": "skip",
            "ad_mode": "skip",
            "turns": 0,
            "messages": [],
        })
        st.session_state.trial_manager = None
    elif scr == SCREEN_PRACTICE:
        st.session_state.practice_manager = None


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_progress_sidebar(ctrl: ExperimentController, flow_test: bool = False):
    with st.sidebar:
        if flow_test:
            st.caption(f"pid: `{ctrl.participant_id}`")
            st.divider()
            st.caption("🛠 Dev mode — flow test")
            if st.button("⏭ Skip screen", use_container_width=True):
                dev_inject_stub_data(ctrl)
                ctrl.advance()
                st.rerun()
            st.divider()

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
        st.caption(f"📍 {labels.get(ctrl.current_screen, ctrl.current_screen)}")


# ═══════════════════════════════════════════════════════════════
# PARTICIPANT SCREEN DISPATCHER
# ═══════════════════════════════════════════════════════════════

def run_participant_mode(flow_test: bool = False):
    """Drive the participant through the full experiment protocol."""
    ctrl: ExperimentController = st.session_state.controller
    scr = ctrl.current_screen

    render_progress_sidebar(ctrl, flow_test=flow_test)

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
            st.session_state.practice_manager = None
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_TRIAL_INTRO:
        trial_cfg = ctrl.current_trial_config
        if trial_cfg:
            task: TaskDefinition = trial_cfg["task"]
            if render_trial_intro(ctrl.trial_number, ctrl.n_trials, task.participant_prompt):
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
            export_session_data(ctrl)
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DONE:
        render_done()

    else:
        st.error(f"Unknown screen: {scr}")
