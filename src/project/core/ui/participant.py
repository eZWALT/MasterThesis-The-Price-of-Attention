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
from core.experiment import ExperimentController, TaskDefinition, TASK_CATALOG, score_ocean, get_ocean_items
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

def init_session_state(params):
    """Ensure every expected key exists in st.session_state, using ExperimentParams for config."""
    if "logger" not in st.session_state:
        st.session_state.logger = ExperimentLogger()

    if "controller" not in st.session_state:
        pid = params.participant_id or str(uuid.uuid4())[:8]
        ctrl = ExperimentController(
            participant_id=pid,
            n_trials=params.n_trials,
            tasks=params.tasks,
            ad_modes=params.ad_modes,
            model=params.model or DEFAULT_MODEL,
            seed=params.seed,
            cb_group=params.cb_group,
            turns_min=params.turns_min,
            turns_max=params.turns_max,
            ad_turns=params.ad_turns,
        )
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

    # Dev ad-control overrides (survive reruns; initialised from URL params)
    if "dev_force_ad" not in st.session_state:
        st.session_state.dev_force_ad = getattr(params, "force_ad", False)
    if "dev_rag_mode" not in st.session_state:
        # use_rag: True→"rag"  False→"mock"  None→"default"
        use_rag = getattr(params, "use_rag", None)
        st.session_state.dev_rag_mode = (
            "rag" if use_rag is True else "mock" if use_rag is False else "default"
        )


# ═══════════════════════════════════════════════════════════════
# MANAGER FACTORIES
# ═══════════════════════════════════════════════════════════════

def _get_or_create_practice_manager() -> ConversationManager:
    mgr = st.session_state.practice_manager
    if mgr is None:
        ctrl: ExperimentController = st.session_state.controller
        practice_task = TaskDefinition(
            id="practice",
            title="Practice",
            genre="Practice",
            participant_prompt="Practice chatting with the assistant.",
            system_prompt_extension=PRACTICE_SYSTEM_PROMPT_EXT,
        )
        mgr = ConversationManager(
            ad_mode="inline_persuasive",
            model=ctrl.model or DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=practice_task,
            logger=st.session_state.logger,
            min_turns=ctrl.turns_min,
            max_turns=ctrl.turns_max,
            ad_turns=ctrl.ad_turns,
        )
        st.session_state.practice_manager = mgr
    return mgr


def _get_or_create_trial_manager(
    task: TaskDefinition,
    ad_mode: str,
    force_ad: bool = False,
    use_rag: bool | None = None,
) -> ConversationManager:
    mgr = st.session_state.trial_manager
    ctrl: ExperimentController = st.session_state.controller
    if mgr is None or mgr.task.id != task.id:
        mgr = ConversationManager(
            ad_mode=ad_mode,
            model=ctrl.model or DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=task,
            logger=st.session_state.logger,
            min_turns=ctrl.turns_min,
            max_turns=ctrl.turns_max,
            ad_turns=ctrl.ad_turns,
            force_ad=force_ad,
            use_rag=use_rag,
        )
        st.session_state.trial_manager = mgr
    return mgr


# ═══════════════════════════════════════════════════════════════
# DATA EXPORT
# ═══════════════════════════════════════════════════════════════

def export_session_data(ctrl: ExperimentController):
    """Persist all collected data via the experiment logger."""
    logger: ExperimentLogger = st.session_state.logger
    logger.log(
        "session_complete",
        {
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
        },
        ad_mode="session",
        conversation_id=ctrl.participant_id,
    )
    logger.export_json()


# ═══════════════════════════════════════════════════════════════
# DEV-FLOW SKIP HELPERS
# ═══════════════════════════════════════════════════════════════

def dev_inject_stub_data(ctrl: ExperimentController, bfi_version: str = "10"):
    """Inject minimal stub data so the controller doesn't break on skip."""
    scr = ctrl.current_screen
    if scr == SCREEN_DEMOGRAPHICS and not ctrl.demographics:
        ctrl.demographics = {"age": 0, "gender": "skip", "education": "skip"}
    elif scr == SCREEN_OCEAN and not ctrl.ocean_raw:
        items = get_ocean_items(bfi_version)
        ctrl.ocean_raw = [4] * len(items)
        ctrl.ocean_scores = score_ocean(ctrl.ocean_raw, items=items)
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
# DEV AD CONTROLS
# ═══════════════════════════════════════════════════════════════

def _render_dev_ad_controls(mgr=None) -> None:
    """
    Render the dev ad-injection control panel inside the *current* sidebar context.

    Writes to st.session_state.dev_force_ad and st.session_state.dev_rag_mode.
    Optionally accepts the active ConversationManager so it can be synced live.
    """
    from core.ad_injection import get_ad, get_injector

    st.markdown("**🎯 Ad Controls**")

    # Force-ad toggle
    st.session_state.dev_force_ad = st.toggle(
        "Inject ad every turn",
        value=st.session_state.get("dev_force_ad", False),
        help="Overrides ad_turns schedule — every user turn triggers an injection.",
    )

    # Backend selector
    rag_options  = ["default", "mock", "rag"]
    rag_labels   = {"default": "⚙️ default (env)", "mock": "🧸 mock (no GPU)", "rag": "🔍 RAG pipeline"}
    current_idx  = rag_options.index(st.session_state.get("dev_rag_mode", "default"))
    chosen = st.radio(
        "Ad backend",
        rag_options,
        index=current_idx,
        format_func=lambda k: rag_labels[k],
        horizontal=True,
        help="Override AD_BACKEND for this session only.",
    )
    st.session_state.dev_rag_mode = chosen

    # Sync onto the live manager so changes take effect without page reload
    if mgr is not None:
        _sync_dev_overrides(mgr)

    # One-shot manual inject button
    if mgr is not None and st.button("💉 Inject ad NOW", use_container_width=True,
                                      help="Fire one ad immediately, regardless of turn schedule."):
        backend = None if chosen == "default" else chosen
        last_user = next(
            (m["content"] for m in reversed(mgr.messages) if m["role"] == "user"),
            "",
        )
        ad = get_ad(query=last_user, context=mgr.messages, backend=backend)
        injector = get_injector(mgr.ad_mode)
        result = injector.inject(ad, mgr.messages)
        # Store result in session state so run_dev_mode can render it in the main area
        st.session_state["dev_manual_ad"] = result
        st.caption(f"📦 {ad.title}")


def _sync_dev_overrides(mgr) -> None:
    """Push current dev session-state overrides onto a live ConversationManager."""
    mgr._force_ad = st.session_state.get("dev_force_ad", False)
    mode = st.session_state.get("dev_rag_mode", "default")
    mgr._ad_backend = None if mode == "default" else mode


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_progress_sidebar(ctrl: ExperimentController, flow_test: bool = False, bfi_version: str = "10"):
    with st.sidebar:
        if flow_test:
            st.caption(f"pid: `{ctrl.participant_id}`")
            st.divider()
            st.caption("🛠 Dev mode — flow test")
            if st.button("⏭ Skip screen", use_container_width=True):
                dev_inject_stub_data(ctrl, bfi_version=bfi_version)
                ctrl.advance()
                st.rerun()
            # Ad controls — only shown on the chat screen, manager may be None
            mgr = st.session_state.get("trial_manager")
            with st.expander("🎯 Ad overrides", expanded=bool(st.session_state.get("dev_force_ad"))):
                _render_dev_ad_controls(mgr=mgr)
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

def run_participant_mode(params):
    """Drive the participant through the full experiment protocol, using ExperimentParams for config."""
    ctrl: ExperimentController = st.session_state.controller
    scr = ctrl.current_screen

    render_progress_sidebar(ctrl, flow_test=params.flow_test, bfi_version=params.bfi_version)

    # Handle skip logic for screens
    if scr in params.skip_screens:
        dev_inject_stub_data(ctrl, bfi_version=params.bfi_version)
        ctrl.advance()
        st.rerun()
        return

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
        result = render_ocean(params.bfi_version)
        if result is not None:
            ctrl.ocean_raw = result
            items = get_ocean_items(params.bfi_version)
            ctrl.ocean_scores = score_ocean(result, items=items)
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
            mgr = _get_or_create_trial_manager(
                task, ad_mode,
                force_ad=params.force_ad,
                use_rag=params.use_rag,
            )
            # Apply any live sidebar tweaks before the next turn
            if params.flow_test:
                _sync_dev_overrides(mgr)
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
