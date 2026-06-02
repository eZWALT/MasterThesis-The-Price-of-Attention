"""
Participant flow: session state management, screen dispatcher,
progress sidebar, and dev-flow skip helpers.
"""

from __future__ import annotations

import uuid
import streamlit as st
from loguru import logger as log

from core.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    TRIALS_PER_SESSION,
    PRACTICE_SYSTEM_PROMPT_EXT,
    STUDY_TYPE_LABELS,
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
    clear_baseline_session_state,
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
        from core.config import LOG_DIR, LOG_FLUSH_EVERY_N, LOG_FLUSH_EVERY_S
        st.session_state.logger = ExperimentLogger(
            log_dir=LOG_DIR,
            flush_every_n=LOG_FLUSH_EVERY_N,
            flush_every_s=LOG_FLUSH_EVERY_S,
        )

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
        st.session_state.experiment_params = params
        log.info(
            "Session init | pid={} | study={} | skip={} | exp={} | run={} | trials={}",
            pid,
            params.study_type,
            sorted(params.skip_screens),
            st.session_state.logger.experiment_id,
            st.session_state.logger.run_id,
            ctrl.n_trials,
        )
        st.session_state.logger.log(
            "session_started",
            {
                "participant_id": pid,
                "study_type": params.study_type,
                "skip_screens": sorted(params.skip_screens),
                "n_trials": params.n_trials,
                "turns_min": params.turns_min,
                "turns_max": params.turns_max,
            },
            ad_mode="session",
            conversation_id=pid,
            source="system",
        )

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
        st.session_state.dev_force_ad = params.force_ad
    if "dev_rag_mode" not in st.session_state:
        # Always default to 'rag' in dev/flow mode unless explicitly set to 'mock' in URL
        use_rag = getattr(params, "use_rag", None)
        if use_rag is False:
            st.session_state.dev_rag_mode = "mock"
        else:
            st.session_state.dev_rag_mode = "rag"


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


def _resolve_dev_ad_settings(params) -> tuple[bool, bool | None, str]:
    """Map dev/flow session overrides to ConversationManager constructor args."""
    force_ad = st.session_state.get("dev_force_ad", params.force_ad)
    rag_mode = st.session_state.get("dev_rag_mode")
    if rag_mode == "rag":
        use_rag: bool | None = True
    elif rag_mode == "mock":
        use_rag = False
    else:
        use_rag = params.use_rag
    effective_mode = st.session_state.get("dev_ad_mode_override") or ""
    return force_ad, use_rag, effective_mode


def _get_or_create_trial_manager(
    task: TaskDefinition,
    ad_mode: str,
    params,
    flow_test: bool = False,
) -> ConversationManager:
    mgr = st.session_state.trial_manager
    ctrl: ExperimentController = st.session_state.controller

    force_ad = params.force_ad
    use_rag = params.use_rag
    if flow_test:
        force_ad, use_rag, mode_override = _resolve_dev_ad_settings(params)
        if mode_override:
            ad_mode = mode_override

    if mgr is None or mgr.task.id != task.id:
        st.session_state.logger.set_trial_index(ctrl.current_trial_index)
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
    elif flow_test and mgr.ad_mode != ad_mode:
        # Keep chat history; drop stale banner/chip from the previous mode.
        mgr.apply_ad_mode(ad_mode)
        _sync_dev_overrides(mgr)
    elif flow_test:
        _sync_dev_overrides(mgr)
    return mgr


# ═══════════════════════════════════════════════════════════════
# DATA EXPORT
# ═══════════════════════════════════════════════════════════════

def _trial_summary_for_log(trial_result: dict) -> dict:
    """Metadata only — per-turn detail lives in JSONL events."""
    return {
        k: trial_result[k]
        for k in (
            "trial",
            "task_id",
            "ad_mode",
            "conversation_id",
            "initial_intent",
            "turns",
            "ad_turns_actual",
            "trial_start_ts",
            "trial_end_ts",
        )
        if k in trial_result
    }


def export_session_data(ctrl: ExperimentController):
    """Persist session-level aggregates; turn-level data is already in JSONL."""
    logger: ExperimentLogger = st.session_state.logger
    logger.log(
        "session_complete",
        {
            "participant_id": ctrl.participant_id,
            "demographics": ctrl.demographics,
            "ocean_raw": ctrl.ocean_raw,
            "ocean_scores": ctrl.ocean_scores,
            "trial_summaries": [_trial_summary_for_log(tr) for tr in ctrl.trial_results],
            "post_trial_surveys": ctrl.post_trial_surveys,
            "final_survey": ctrl.final_survey,
        },
        ad_mode="session",
        conversation_id=ctrl.participant_id,
    )
    logger.export_jsonl()


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
    from core.config import AD_BACKEND
    rag_options = ["mock", "rag"]
    rag_labels  = {"mock": "🧸 Mock (fast, no GPU)", "rag": "🔍 RAG pipeline"}
    stored = st.session_state.get("dev_rag_mode", AD_BACKEND)
    current_idx = rag_options.index(stored) if stored in rag_options else 0
    chosen = st.radio(
        "Ad backend",
        rag_options,
        index=current_idx,
        format_func=lambda k: rag_labels[k],
        horizontal=True,
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
        mgr.last_retrieval = ad
        mgr.last_retrieval_ad_mode = mgr.ad_mode if ad and ad.has_ads else None
        injector = get_injector(mgr.ad_mode)
        result = injector.inject(ad, mgr.messages)
        # Store result in session state so run_dev_mode can render it in the main area
        st.session_state["dev_manual_ad"] = result
        primary = ad.primary
        st.caption(f"📦 {primary.title if primary else 'No ad'}")


def _sync_dev_overrides(mgr) -> None:
    """Push dev force-ad / backend overrides onto the live ConversationManager."""
    mgr._force_ad = st.session_state.get("dev_force_ad", False)
    mgr._ad_backend = st.session_state.get("dev_rag_mode")  # "mock" or "rag"


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_progress_sidebar(ctrl: ExperimentController, flow_test: bool = False, bfi_version: str = "10", study_type: str | None = None):
    with st.sidebar:
        if study_type:
            st.caption(f"Study: {STUDY_TYPE_LABELS.get(study_type, study_type)}")
        if flow_test:
            st.caption(f"pid: `{ctrl.participant_id}`")
            st.divider()
            st.caption("🛠 Dev mode — flow test")
            if st.button("⏭ Skip screen", use_container_width=True):
                dev_inject_stub_data(ctrl, bfi_version=bfi_version)
                ctrl.advance()
                st.rerun()

            # Ad mode override — lets dev switch injection style mid-session
            from core.config import AD_MODES, AD_MODE_LABELS
            trial_cfg = ctrl.current_trial_config
            default_mode = trial_cfg["ad_mode"] if trial_cfg else AD_MODES[0]
            default_idx = AD_MODES.index(default_mode) if default_mode in AD_MODES else 0
            selected_mode = st.selectbox(
                "📊 Ad Mode",
                AD_MODES,
                index=default_idx,
                format_func=lambda k: AD_MODE_LABELS.get(k, k),
                key="dev_flow_ad_mode",
            )
            st.session_state.dev_ad_mode_override = selected_mode

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

    render_progress_sidebar(
        ctrl,
        flow_test=params.flow_test,
        bfi_version=params.bfi_version,
        study_type=params.study_type,
    )

    # Handle skip logic for screens
    if scr in params.skip_screens:
        if scr == SCREEN_BASELINE:
            clear_baseline_session_state()
        dev_inject_stub_data(ctrl, bfi_version=params.bfi_version)
        st.session_state.logger.log(
            "screen_skipped",
            {"screen": scr, "study_type": params.study_type},
            ad_mode="session",
            conversation_id=ctrl.participant_id,
            source="system",
        )
        ctrl.advance()
        st.rerun()
        return

    if scr == SCREEN_CONSENT:
        if render_consent():
            st.session_state.logger.log(
                "consent_granted", {},
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DEMOGRAPHICS:
        result = render_demographics()
        if result is not None:
            ctrl.demographics = result
            st.session_state.logger.log(
                "demographics_submitted", result,
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_OCEAN:
        result = render_ocean(params.bfi_version)
        if result is not None:
            ctrl.ocean_raw = result
            items = get_ocean_items(params.bfi_version)
            ctrl.ocean_scores = score_ocean(result, items=items)
            st.session_state.logger.log(
                "ocean_submitted",
                {"bfi_version": params.bfi_version, "raw": result, "scores": ctrl.ocean_scores},
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_BASELINE:
        if render_baseline():
            st.session_state.logger.log(
                "baseline_complete", {},
                ad_mode="session", conversation_id=ctrl.participant_id, source="system",
            )
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
                log.info(
                    "Trial {}/{} starting | pid={} | task={} | ad_mode={} | exp={}",
                    ctrl.trial_number, ctrl.n_trials,
                    ctrl.participant_id, task.id, trial_cfg["ad_mode"],
                    st.session_state.logger.experiment_id,
                )
                st.session_state.trial_manager = None
                ctrl.advance()
                st.rerun()

    elif scr == SCREEN_TRIAL_CHAT:
        trial_cfg = ctrl.current_trial_config
        if trial_cfg:
            task = trial_cfg["task"]
            ad_mode = trial_cfg["ad_mode"]
            mgr = _get_or_create_trial_manager(
                task,
                ad_mode,
                params,
                flow_test=params.flow_test,
            )
            if render_trial_chat(mgr, mgr.ad_mode, flow_test=params.flow_test):
                from dataclasses import asdict
                from datetime import datetime

                # Determine end reason for continuation tracking
                end_reason = "max_turns" if mgr.must_end else "user_ended"
                continuation_summary = mgr.finalize_trial(reason=end_reason)

                trial_end_ts = datetime.now().isoformat()
                trial_record = {
                    "trial": ctrl.trial_number,
                    "task_id": task.id,
                    "ad_mode": ad_mode,
                    "conversation_id": mgr.conversation_id,
                    "initial_intent": mgr.initial_intent,
                    "intent_history": list(mgr.intent_history),
                    "turns": mgr.turn_count,
                    "ad_turns_actual": list(mgr.ad_turns_actual),
                    "trial_start_ts": mgr.trial_start_ts,
                    "trial_end_ts": trial_end_ts,
                    "turn_metrics": [asdict(m) for m in mgr.turn_metrics],
                    "continuation": continuation_summary,
                    "messages": list(mgr.messages),
                }
                ctrl.trial_results.append(trial_record)
                st.session_state.logger.log(
                    "trial_complete",
                    _trial_summary_for_log(trial_record),
                    ad_mode=ad_mode,
                    conversation_id=mgr.conversation_id,
                    source="system",
                    turn=mgr.turn_count,
                )
                log.info(
                    "Trial {}/{} complete | pid={} | turns={} | ads_injected={} | continued_after_ad={}",
                    ctrl.trial_number, ctrl.n_trials,
                    ctrl.participant_id, mgr.turn_count, len(mgr.ad_turns_actual),
                    continuation_summary.get("n_continued_after_ad", "?"),
                )
                st.session_state.trial_manager = None
                ctrl.advance()
                st.rerun()

    elif scr == SCREEN_POST_TRIAL_SURVEY:
        result = render_post_trial_survey(ctrl.trial_number)
        if result is not None:
            ctrl.post_trial_surveys.append(result)
            st.session_state.logger.log(
                "post_trial_survey_submitted",
                {"trial": ctrl.trial_number, "responses": result},
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_FINAL_SURVEY:
        result = render_final_survey()
        if result is not None:
            ctrl.final_survey = result
            export_session_data(ctrl)
            log.info(
                "Session complete | pid={} | exp={} | trials_completed={}",
                ctrl.participant_id,
                st.session_state.logger.experiment_id,
                len(ctrl.trial_results),
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DONE:
        render_done()

    else:
        st.error(f"Unknown screen: {scr}")
