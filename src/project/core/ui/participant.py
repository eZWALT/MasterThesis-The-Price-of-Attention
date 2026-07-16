"""
Participant flow — Workflow B: session state, screen dispatcher,
progress sidebar, and dev-flow skip helpers.
"""

from __future__ import annotations

import uuid
import random
import streamlit as st
from loguru import logger as log
from pathlib import Path

from core.config import (
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    EXIT_N_TRIALS,
    PRACTICE_SYSTEM_PROMPT_EXT,
    STUDY_TYPE_LABELS,
    CONDITION_AD_MODE,
    CONDITION_LABELS,
    CONDITION_TIMING,
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_INSTRUCTIONS,
    SCREEN_BASELINE,
    SCREEN_WARMUP_CHAT,
    SCREEN_CONDITION_INTRO,
    SCREEN_CONDITION_CHAT,
    SCREEN_CONDITION_CONCLUSION,
    SCREEN_POST_CONDITION_SURVEY,
    SCREEN_ADS_RECALL,
    SCREEN_OCEAN,
    SCREEN_DECEPTION_DISCLOSURE,
    SCREEN_PROLIFIC_ID,
    SCREEN_VALIDATION,
    SCREEN_DONE,
    WARMUP_TASK_ID,
    WARMUP_TURNS,
    LLM_BACKEND,
    LLM_THINK,
    EMBEDDING_MODEL_NAME,
    RERANKER_MODEL_NAME,
    DENSE_TOP_K,
    RERANKER_TOP_K,
    RETRIEVAL_FINAL_TOP_N,
    USE_HYBRID,
    USE_RERANKER,
    QUERY_EXPANSION_MODE,
    HYDE_NUM_DOCS,
    USE_CONTEXT_SUMMARY,
    CATALOG_PATH,
    STUDY_TYPE_CROWD,
    MOCK_AD_TITLE,
    MOCK_AD_TEXT,
    MOCK_AD_CTA,
)
from core.conversation import ConversationManager
from core.logger import ExperimentLogger
from core.experiment import ExperimentController, TaskDefinition, TASK_CATALOG, TASK_BY_ID, score_ocean, get_ocean_items
from core.ui.screens import (
    render_consent,
    render_prolific_id,
    render_baseline,
    render_demographics,
    render_ocean,
    render_instructions,
    render_warmup_chat,
    render_condition_intro,
    render_condition_chat,
    render_condition_conclusion,
    render_post_condition_survey,
    render_ads_recall,
    render_demographics_end,
    render_deception_disclosure,
    render_validation_questions,
    render_done,
    render_webcam_preview,
    finalize_webcam_recording,
)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════

def init_session_state(params):
    """Ensure every expected key exists in st.session_state."""
    if "logger" not in st.session_state:
        from core.config import LOG_DIR, LOG_DIR_DEV, LOG_FLUSH_EVERY_N, LOG_FLUSH_EVERY_S, STUDY_TYPE_LAB
        if params.dev_mode or params.flow_test:
            log_dir = LOG_DIR_DEV
        else:
            log_dir = LOG_DIR
        pid = params.participant_id or str(uuid.uuid4())[:8]
        st.session_state.logger = ExperimentLogger(
            log_dir=log_dir,
            flush_every_n=LOG_FLUSH_EVERY_N,
            flush_every_s=LOG_FLUSH_EVERY_S,
            participant_id=pid,
            marker_client=None,
        )
        from core.modalities.eeg import lsl_sender
        st.session_state.logger._marker_client = lsl_sender()
        if params.study_type == STUDY_TYPE_LAB:
            import os as _os
            if not _os.environ.get("LSL_MARKER_OUTLET", "").strip():
                st.error("Lab sessions require LSL_MARKER_OUTLET env var")
                st.stop()

    if "controller" not in st.session_state:
        ctrl = ExperimentController(
            participant_id=st.session_state.logger.participant_id,
            tasks=params.tasks,
            model=params.model or DEFAULT_MODEL,
            seed=params.seed,
            cb_group=params.cb_group,
            turns_min=params.turns_min,
            turns_max=params.turns_max,
            finish_from=params.finish_from,
        )
        ctrl.build_condition_plan()
        st.session_state.controller = ctrl
        st.session_state.experiment_params = params
        log.info(
            "Session init (B) | pid={} | study={} | skip={} | exp={}",
            pid,
            params.study_type,
            sorted(params.skip_screens),
            st.session_state.logger.experiment_id,
        )
        st.session_state.logger.log(
            "session_started",
            {
                "participant_id": pid,
            "study_type": params.study_type,
            "skip_screens": sorted(params.skip_screens),
                "protocol": "workflow_a_star",
                "conditions": ctrl.condition_plan,
            },
            ad_mode="session",
            conversation_id=pid,
            source="system",
        )

        # Log experiment config snapshot for self-describing logs
        try:
            _ver = Path(__file__).resolve().parents[4] / "VERSION"
            _version = _ver.read_text().strip() if _ver.exists() else "unknown"
        except Exception:
            _version = "unknown"

        _active_pipeline_stages = []
        if USE_CONTEXT_SUMMARY:
            _active_pipeline_stages.append("ContextSummaryStage")
        if QUERY_EXPANSION_MODE != "none":
            _active_pipeline_stages.append("QueryExpansionStage")
        _active_pipeline_stages.append("DenseRetriever")
        if USE_HYBRID:
            _active_pipeline_stages.append("HybridRefiner")
        if USE_RERANKER:
            _active_pipeline_stages.append("Reranker")
        _active_pipeline_stages.append("AdFormatter")

        st.session_state.logger.log(
            "experiment_config",
            {
                "version": _version,
                "llm": {
                    "model": params.model or DEFAULT_MODEL,
                    "temperature": DEFAULT_TEMPERATURE,
                    "max_tokens": DEFAULT_MAX_TOKENS,
                    "backend": LLM_BACKEND,
                    "think": LLM_THINK,
                },
                "retrieval": {
                    "embedding_model": EMBEDDING_MODEL_NAME,
                    "reranker_model": RERANKER_MODEL_NAME,
                    "dense_top_k": DENSE_TOP_K,
                    "reranker_top_k": RERANKER_TOP_K,
                    "final_top_n": RETRIEVAL_FINAL_TOP_N,
                    "use_hybrid": USE_HYBRID,
                    "use_reranker": USE_RERANKER,
                    "query_expansion_mode": QUERY_EXPANSION_MODE,
                    "hyde_num_docs": HYDE_NUM_DOCS,
                    "use_context_summary": USE_CONTEXT_SUMMARY,
                    "catalog_path": CATALOG_PATH,
                    "active_stages": _active_pipeline_stages,
                },
                "experiment": {
                    "study_type": params.study_type,
                    "n_trials": params.n_trials,
                    "turns_min": params.turns_min,
                    "turns_max": params.turns_max,
                },
            },
            ad_mode="session",
            conversation_id=pid,
            source="system",
        )

    if "warmup_manager" not in st.session_state:
        st.session_state.warmup_manager = None
    if "condition_manager" not in st.session_state:
        st.session_state.condition_manager = None

    # Dev mode state
    if "dev_manager" not in st.session_state:
        st.session_state.dev_manager = None

    # Dev ad-control overrides
    if "dev_force_ad" not in st.session_state:
        st.session_state.dev_force_ad = params.force_ad
    if "dev_rag_mode" not in st.session_state:
        use_rag = getattr(params, "use_rag", None)
        if use_rag is False:
            st.session_state.dev_rag_mode = "mock"
        else:
            st.session_state.dev_rag_mode = "rag"


# ═══════════════════════════════════════════════════════════════
# MANAGER FACTORIES
# ═══════════════════════════════════════════════════════════════

def _get_or_create_warmup_manager() -> ConversationManager:
    mgr = st.session_state.warmup_manager
    if mgr is None:
        ctrl: ExperimentController = st.session_state.controller
        experiment_params = st.session_state.get("experiment_params")
        warmup_task = TASK_BY_ID.get(WARMUP_TASK_ID, TASK_CATALOG[0])
        mgr = ConversationManager(
            ad_mode="",
            model=ctrl.model or DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=warmup_task,
            logger=st.session_state.logger,
            min_turns=1,
            max_turns=WARMUP_TURNS,
            finish_from=1,
            ad_turns=[],
            use_rag=True,
            dry_run=getattr(experiment_params, "dry_run", False),
        )
        st.session_state.warmup_manager = mgr
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


def _get_or_create_condition_manager(
    task: TaskDefinition,
    condition_id: str,
    params,
    flow_test: bool = False,
) -> ConversationManager:
    mgr = st.session_state.condition_manager
    ctrl: ExperimentController = st.session_state.controller

    ad_mode = CONDITION_AD_MODE.get(condition_id, "")
    window = CONDITION_TIMING.get(condition_id)

    # Determine ad_turns for this condition
    force_ad = params.force_ad
    use_rag = params.use_rag
    if flow_test:
        force_ad, use_rag, mode_override = _resolve_dev_ad_settings(params)
        if mode_override:
            ad_mode = mode_override

    # Build ad_turns list: exactly 1 random turn within window
    ad_turns: list[int] = []
    if condition_id != "no_ads" and window is not None and ad_mode:
        # Use deterministic seed if set, else random
        if ctrl.seed is not None:
            rng = random.Random(ctrl.seed + hash(condition_id) + hash(task.id))
            ad_turns = [rng.randint(window[0], window[1])]
        else:
            ad_turns = [random.randint(window[0], window[1])]

    if mgr is None or mgr.task.id != task.id:
        st.session_state.logger.set_trial_index(ctrl.current_condition_index)
        mgr = ConversationManager(
            ad_mode=ad_mode,
            model=ctrl.model or DEFAULT_MODEL,
            temperature=DEFAULT_TEMPERATURE,
            max_tokens=DEFAULT_MAX_TOKENS,
            task=task,
            logger=st.session_state.logger,
            min_turns=ctrl.turns_min,
            max_turns=ctrl.turns_max,
            finish_from=ctrl.finish_from,
            ad_turns=ad_turns,
            force_ad=force_ad,
            use_rag=use_rag,
            dry_run=params.dry_run,
        )
        st.session_state.condition_manager = mgr
    elif flow_test:
        if mgr.ad_mode != ad_mode:
            mgr.apply_ad_mode(ad_mode)
        _sync_dev_overrides(mgr)
    return mgr


# ═══════════════════════════════════════════════════════════════
# DATA EXPORT
# ═══════════════════════════════════════════════════════════════

def _condition_summary_for_log(condition_result: dict) -> dict:
    return {
        k: condition_result[k]
        for k in (
            "condition_id",
            "ad_mode",
            "task_id",
            "conversation_id",
            "initial_intent",
            "turns",
            "ad_turns_actual",
            "trial_start_ts",
            "trial_end_ts",
        )
        if k in condition_result
    }


def export_session_data(ctrl: ExperimentController):
    """Persist session-level aggregates and finalize eye-tracking video."""
    finalize_webcam_recording()
    logger: ExperimentLogger = st.session_state.logger
    logger.log(
        "session_complete",
        {
            "participant_id": ctrl.participant_id,
            "worker_id": ctrl.worker_id if ctrl.worker_id else None,
            "demographics": ctrl.demographics,
            "ocean_raw": ctrl.ocean_raw,
            "ocean_scores": ctrl.ocean_scores,
            "validation": ctrl.validation_results,
            "condition_summaries": [_condition_summary_for_log(cr) for cr in ctrl.condition_results],
            "condition_surveys": ctrl.condition_surveys,
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
    if scr == SCREEN_PROLIFIC_ID:
        ctrl.worker_id = "DEV_STUB_WORKER"
    elif scr == SCREEN_VALIDATION:
        ctrl.validation_results = {
            "correct": 5,
            "false_positives": 0,
            "false_negatives": 0,
            "mistakes": 0,
            "accuracy": 1.0,
            "validation_failed": False,
            "real_task_ids": [],
            "distractor_task_ids": [],
            "selected_task_ids": [],
        }
    elif scr == SCREEN_DEMOGRAPHICS and not ctrl.demographics:
        ctrl.demographics = {"age": 0, "gender": "skip", "education": "skip"}
    elif scr == SCREEN_OCEAN and not ctrl.ocean_raw:
        items = get_ocean_items(bfi_version)
        ctrl.ocean_raw = [4] * len(items)
        ctrl.ocean_scores = score_ocean(ctrl.ocean_raw, items=items)
    elif scr == SCREEN_ADS_RECALL:
        st.session_state.pop("recall_step", None)
        st.session_state.pop("recall_responses", None)
    elif scr == SCREEN_POST_CONDITION_SURVEY:
        stub = {k: 4 for k in [
            "llm_reliable", "llm_helpful", "llm_made_up", "llm_changed_mind",
            "llm_not_useful", "llm_neutral", "llm_false", "llm_addressed",
            "llm_impartial", "llm_suggestions", "llm_opinionated", "llm_not_aid",
            "llm_skeptical", "llm_relevant", "llm_convincing",
            "personality_trust", "personality_influence", "personality_changed_mind",
            "behaviour_pushing", "behaviour_manipulate",
        ]}
        stub.update({k: "(skip)" for k in [
            "personality_trust_text", "personality_influence_text", "personality_changed_mind_text",
            "personality_brands_text", "personality_sponsored_text",
        ]})
        ctrl.condition_surveys.append(stub)
        # Clean up sub-step state so Back starts at section 0
        cn = ctrl.condition_number
        st.session_state.pop(f"pcs_section_{cn}", None)
        st.session_state.pop(f"pcs_responses_{cn}", None)
    elif scr == SCREEN_CONDITION_CHAT:
        cfg = ctrl.current_condition_config
        cond_id = cfg["condition"] if cfg else "skip"
        task = cfg["task"] if cfg else TASK_CATALOG[0]
        ad_mode = cfg.get("ad_mode", "") if cfg else ""
        stub_result = {
            "condition_id": cond_id,
            "ad_mode": ad_mode,
            "task_id": task.id,
            "task_prompt": task.participant_prompt,
            "turns": 0,
            "messages": [],
        }
        if ad_mode:
            is_inline = ad_mode == "inline_persuasive"
            stub_result["ad_info"] = {
                "title": MOCK_AD_TITLE,
                "text": MOCK_AD_TEXT,
                "cta": MOCK_AD_CTA,
                "question": "",
                "source_item_id": "mock",
                "image_url": None,
                "product_url": f"https://example.com/product/{MOCK_AD_TITLE.lower().replace(' ', '-')}",
                "ad_mode": ad_mode,
                "ad_turn": cfg.get("ad_turn"),
            }
            if is_inline:
                stub_result["ad_info"]["inline_response"] = (
                    "That's a great question! Based on what you've told me, "
                    "I'd recommend looking into a few different options. "
                    "For example, MyProtein Creatine is a popular choice for "
                    "boosting recovery and muscle growth. "
                    "Consider factors like your budget, lifestyle, and specific needs. "
                    "Would you like me to help you compare some choices?"
                )
                stub_result["ad_info"]["inline_user_msg"] = (
                    "I need help finding a good supplement for my workout routine. "
                    "What would you recommend?"
                )
                stub_result["ad_info"]["inline_ctx_before"] = []
                stub_result["ad_info"]["inline_ctx_after"] = []
        ctrl.condition_results.append(stub_result)
        st.session_state.condition_manager = None
    elif scr == SCREEN_WARMUP_CHAT:
        st.session_state.warmup_manager = None


# ═══════════════════════════════════════════════════════════════
# DEV AD CONTROLS
# ═══════════════════════════════════════════════════════════════

def _render_dev_ad_controls(mgr=None) -> None:
    from core.ad_injection import get_ad, get_injector

    st.markdown("**🎯 Ad Controls**")

    st.session_state.dev_force_ad = st.toggle(
        "Inject ad every turn",
        value=st.session_state.get("dev_force_ad", False),
        help="Overrides ad_turns schedule — every user turn triggers an injection.",
    )

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

    if mgr is not None:
        _sync_dev_overrides(mgr)

    if mgr is not None and st.button("💉 Inject ad NOW", use_container_width=True,
                                      help="Fire one ad immediately, regardless of turn schedule."):
        backend = None if chosen == "default" else chosen
        last_user = next(
            (m["content"] for m in reversed(mgr.messages) if m["role"] == "user"),
            "",
        )
        ad = get_ad(
            query=last_user,
            context=mgr.messages,
            backend=backend,
            task_prompt=mgr.task.participant_prompt if mgr.task else "",
        )
        mgr.last_retrieval = ad
        mgr.last_retrieval_ad_mode = mgr.ad_mode if ad and ad.has_ads else None
        injector = get_injector(mgr.ad_mode)
        result = injector.inject(ad, mgr.messages)
        st.session_state["dev_manual_ad"] = result
        primary = ad.primary
        st.caption(f"📦 {primary.title if primary else 'No ad'}")


def _sync_dev_overrides(mgr) -> None:
    mgr._force_ad = st.session_state.get("dev_force_ad", False)
    mgr._ad_backend = st.session_state.get("dev_rag_mode")


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════

def render_progress_sidebar(ctrl: ExperimentController, flow_test: bool = False, bfi_version: str = "10", study_type: str | None = None, webcam_enabled: bool = False):
    with st.sidebar:
        render_webcam_preview(
            webcam_enabled=webcam_enabled,
            participant_id=ctrl.participant_id,
            log_dir=st.session_state.logger._log_dir,
            experiment_id=st.session_state.logger.experiment_id,
            current_screen=ctrl.current_screen,
        )
        if study_type or flow_test:
            st.divider()
        if study_type:
            st.caption(f"Study: {STUDY_TYPE_LABELS.get(study_type, study_type)}")
        if flow_test:
            st.caption(f"pid: `{ctrl.participant_id}`")
            st.divider()
            st.caption("🛠 Dev mode — flow test")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏪ Back", use_container_width=True):
                    scr = ctrl.current_screen
                    stepped = False
                    if scr == SCREEN_POST_CONDITION_SURVEY:
                        sk = f"pcs_section_{ctrl.condition_number}"
                        if st.session_state.get(sk, 0) > 0:
                            st.session_state[sk] -= 1
                            stepped = True
                    elif scr == SCREEN_ADS_RECALL:
                        if st.session_state.get("recall_step", 0) > 0:
                            st.session_state["recall_step"] -= 1
                            stepped = True
                    if not stepped:
                        ctrl.go_back()
                    st.rerun()
            with col2:
                if st.button("⏭ Skip", use_container_width=True):
                    dev_inject_stub_data(ctrl, bfi_version=bfi_version)
                    ctrl.advance()
                    st.rerun()

            # Condition override for dev-flow
            from core.config import CONDITIONS, CONDITION_AD_MODE
            trial_cfg = ctrl.current_condition_config
            if trial_cfg:
                default_condition = trial_cfg["condition"]
                default_idx = CONDITIONS.index(default_condition) if default_condition in CONDITIONS else 0
                selected = st.selectbox(
                    "📊 Condition",
                    CONDITIONS,
                    index=default_idx,
                    format_func=lambda k: CONDITION_LABELS.get(k, k),
                    key="dev_flow_condition",
                )
                st.session_state.dev_ad_mode_override = CONDITION_AD_MODE.get(selected, "")

            mgr = st.session_state.get("condition_manager")
            with st.expander("🎯 Ad overrides", expanded=bool(st.session_state.get("dev_force_ad"))):
                _render_dev_ad_controls(mgr=mgr)
            st.divider()

        labels = {
            SCREEN_CONSENT: "Consent",
            SCREEN_PROLIFIC_ID: "Participant ID",
            SCREEN_BASELINE: "Eye-Tracking Baseline",
            SCREEN_DEMOGRAPHICS: "Demographics",
            SCREEN_INSTRUCTIONS: "Instructions",
            SCREEN_WARMUP_CHAT: "Warm-Up",
            SCREEN_CONDITION_INTRO: f"Condition {ctrl.condition_number}/{ctrl.n_conditions}",
            SCREEN_CONDITION_CHAT: f"Condition {ctrl.condition_number}/{ctrl.n_conditions}",
            SCREEN_POST_CONDITION_SURVEY: "Post-Task Questionnaire",
            SCREEN_ADS_RECALL: "Recall",
            SCREEN_OCEAN: "About You",
            SCREEN_VALIDATION: "Validation",
            SCREEN_DECEPTION_DISCLOSURE: "Debrief",
            SCREEN_DONE: "Done ✓",
        }
        st.caption(f"📍 {labels.get(ctrl.current_screen, ctrl.current_screen)}")

        _condition_screens = {SCREEN_CONDITION_INTRO, SCREEN_CONDITION_CHAT, SCREEN_POST_CONDITION_SURVEY}
        if flow_test:
            cfg = ctrl.current_condition_config
            if cfg and ctrl.current_screen in _condition_screens:
                cond_label = CONDITION_LABELS.get(cfg["condition"], cfg["condition"])
                st.caption(f"Condition: {cond_label}")

        # Early-exit button during conditions
        if ctrl.can_exit_early and ctrl.current_screen in _condition_screens:
            st.divider()
            remaining = ctrl.n_conditions - ctrl.current_condition_index
            if st.button(
                "🚪 Leave study early",
                use_container_width=True,
                help=f"You have completed {ctrl.current_condition_index} of {ctrl.n_conditions} conditions. "
                     f"You may stop now and your data so far will be saved.",
            ):
                st.session_state.logger.log(
                    "early_exit",
                    {
                        "conditions_completed": ctrl.current_condition_index,
                        "conditions_planned": ctrl.n_conditions,
                        "current_screen": ctrl.current_screen,
                    },
                    ad_mode="session",
                    conversation_id=ctrl.participant_id,
                    source="user",
                )
                ctrl.exit_early()
                st.rerun()


# ═══════════════════════════════════════════════════════════════
# PARTICIPANT SCREEN DISPATCHER (Workflow B)
# ═══════════════════════════════════════════════════════════════

def run_participant_mode(params):
    """Drive the participant through Workflow B protocol."""
    ctrl: ExperimentController = st.session_state.controller
    scr = ctrl.current_screen

    render_progress_sidebar(
        ctrl,
        flow_test=params.flow_test,
        bfi_version=params.bfi_version,
        study_type=params.study_type,
        webcam_enabled=params.webcam_enabled,
    )

    # Handle skip logic
    if scr in params.skip_screens:
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

    elif scr == SCREEN_PROLIFIC_ID:
        result = render_prolific_id()
        if result is not None:
            ctrl.worker_id = result
            st.session_state.logger.log(
                "worker_id_set",
                {"worker_id": result},
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_BASELINE:
        if "baseline_started" not in st.session_state:
            st.session_state.baseline_started = True
            st.session_state.logger.log("baseline_start", {},
                ad_mode="session", conversation_id=ctrl.participant_id, source="system")
        if render_baseline():
            del st.session_state.baseline_started
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_INSTRUCTIONS:
        if render_instructions():
            st.session_state.logger.log("screen_instructions", {}, ad_mode="session", conversation_id=ctrl.participant_id, source="system")
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_WARMUP_CHAT:
        mgr = _get_or_create_warmup_manager()
        if "_warmup_started" not in st.session_state:
            st.session_state._warmup_started = True
            st.session_state.logger.log("warmup_start", {},
                ad_mode="session", conversation_id=ctrl.participant_id, source="system")
        if render_warmup_chat(mgr):
            st.session_state.logger.log("warmup_finish", {}, ad_mode="session", conversation_id=ctrl.participant_id, source="system")
            st.session_state.warmup_manager = None
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_CONDITION_INTRO:
        cfg = ctrl.current_condition_config
        if cfg:
            task: TaskDefinition = cfg["task"]
            if render_condition_intro(
                ctrl.condition_number,
                ctrl.n_conditions,
                cfg["condition"],
                task,
            ):
                log.info(
                    "Condition {}/{} starting | pid={} | condition={} | task={} | ad_mode={}",
                    ctrl.condition_number, ctrl.n_conditions,
                    ctrl.participant_id, cfg["condition"], task.id, cfg["ad_mode"],
                )
                from core.retrieval import count_items_by_categories
                pool_size = count_items_by_categories(task.relevant_categories)
                st.session_state.logger.log(
                    "condition_start",
                    {
                        "condition": cfg["condition"],
                        "ad_mode": cfg["ad_mode"],
                        "task_id": task.id,
                        "task_title": task.title,
                        "task_genre": task.genre,
                        "relevant_categories": task.relevant_categories,
                        "pool_size": pool_size,
                        "pool_categories": task.relevant_categories,
                    },
                    ad_mode=cfg["ad_mode"],
                    conversation_id=ctrl.participant_id,
                    source="system",
                )
                st.session_state.condition_manager = None
                ctrl.advance()
                st.rerun()

    elif scr == SCREEN_CONDITION_CHAT:
        cfg = ctrl.current_condition_config
        if cfg:
            task = cfg["task"]
            condition_id = cfg["condition"]
            mgr = _get_or_create_condition_manager(
                task,
                condition_id,
                params,
                flow_test=params.flow_test,
            )
            if render_condition_chat(mgr, condition_id, flow_test=params.flow_test):
                from dataclasses import asdict
                from datetime import datetime
                from core.ad_injection.models import ad_image_url
                from core.ad_injection.ad_links import ad_product_url

                end_reason = "max_turns" if mgr.must_end else "user_ended"
                continuation_summary = mgr.finalize_trial(reason=end_reason)

                trial_end_ts = datetime.now().isoformat()

                ad_info = None
                injected = mgr.injected_ad_info
                if injected is not None:
                    ad_info = {k: injected.get(k) for k in [
                        "title", "text", "cta", "question", "source_item_id",
                        "ad_mode", "ad_turn", "retrieval_backend",
                        "retrieval_latency_ms", "query", "intent_label",
                        "candidate_count", "candidate_titles",
                    ]}
                    # Use last_retrieval as fallback for image/product URLs
                    if mgr.last_retrieval and mgr.last_retrieval.primary:
                        ad_info["image_url"] = ad_image_url(mgr.last_retrieval.primary)
                        ad_info["product_url"] = ad_product_url(mgr.last_retrieval.primary)
                    else:
                        ad_info["image_url"] = None
                        ad_info["product_url"] = None
                    is_inline = cfg["ad_mode"] == "inline_persuasive"
                    if is_inline and cfg["ad_turn"] is not None:
                        t = cfg["ad_turn"]
                        idx = 2 * t
                        if idx < len(mgr.messages) and mgr.messages[idx].get("role") == "assistant":
                            ad_info["inline_response"] = mgr.messages[idx]["content"]
                        if idx - 1 >= 0 and mgr.messages[idx - 1].get("role") == "user":
                            ad_info["inline_user_msg"] = mgr.messages[idx - 1]["content"]
                        ctx_before = []
                        for i in range(max(0, idx - 4), idx - 1):
                            role = mgr.messages[i].get("role", "")
                            content = mgr.messages[i].get("content", "")
                            ctx_before.append({"role": role, "content": content[:500]})
                        ctx_after = []
                        for i in range(idx + 1, min(len(mgr.messages), idx + 4)):
                            role = mgr.messages[i].get("role", "")
                            content = mgr.messages[i].get("content", "")
                            ctx_after.append({"role": role, "content": content[:500]})
                        ad_info["inline_ctx_before"] = ctx_before
                        ad_info["inline_ctx_after"] = ctx_after

                condition_record = {
                    "condition_id": condition_id,
                    "ad_mode": cfg["ad_mode"],
                    "ad_turn": cfg["ad_turn"],
                    "task_id": task.id,
                    "task_prompt": task.participant_prompt,
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
                    "ad_info": ad_info,
                }
                ctrl.condition_results.append(condition_record)
                from core.retrieval import count_items_by_categories
                pool_size = count_items_by_categories(task.relevant_categories)
                st.session_state.logger.log(
                    "condition_end",
                    {
                        **_condition_summary_for_log(condition_record),
                        "relevant_categories": task.relevant_categories,
                        "pool_size": pool_size,
                    },
                    ad_mode=cfg["ad_mode"],
                    conversation_id=mgr.conversation_id,
                    source="system",
                    turn=mgr.turn_count,
                )
                st.session_state.logger.log(
                    "conversation_completed",
                    {
                        "condition": condition_id,
                        "ad_mode": cfg["ad_mode"],
                        "ad_shown": len(mgr.ad_turns_actual) > 0,
                        "ad_id": mgr.last_retrieval.primary.source_item_id
                            if mgr.last_retrieval and mgr.last_retrieval.primary else None,
                        "task_id": task.id,
                        "total_turns": mgr.turn_count,
                        "ad_turn": cfg["ad_turn"],
                        "relevant_categories": task.relevant_categories,
                        "pool_size": pool_size,
                    },
                    ad_mode=cfg["ad_mode"],
                    conversation_id=mgr.conversation_id,
                    source="system",
                    turn=mgr.turn_count,
                )
                log.info(
                    "Condition {} complete | pid={} | condition={} | turns={} | ads={}",
                    ctrl.condition_number, ctrl.participant_id,
                    condition_id, mgr.turn_count, mgr.ad_turns_actual,
                )
                st.session_state.condition_manager = None
                ctrl.advance()
                st.rerun()

    elif scr == SCREEN_CONDITION_CONCLUSION:
        cfg = ctrl.current_condition_config
        task = cfg["task"]
        result = render_condition_conclusion(
            condition_number=ctrl.condition_number,
            total_conditions=ctrl.n_conditions,
            task_title=task.title,
            task_prompt=task.participant_prompt,
        )
        if result is not None:
            from core.retrieval import count_items_by_categories
            pool_size = count_items_by_categories(task.relevant_categories)
            st.session_state.logger.log(
                "condition_conclusion_submitted",
                {
                    "task_id": task.id,
                    "task_title": task.title,
                    "conclusion": result["conclusion"],
                    "relevant_categories": task.relevant_categories,
                    "pool_size": pool_size,
                },
                ad_mode=cfg["ad_mode"],
                conversation_id=ctrl.participant_id,
                source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_POST_CONDITION_SURVEY:
        result = render_post_condition_survey(ctrl.condition_number)
        if result is not None:
            ctrl.condition_surveys.append(result)
            st.session_state.logger.log(
                "post_condition_survey_submitted",
                {"condition": ctrl.current_condition_config["condition"], "responses": result},
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_ADS_RECALL:
        result = render_ads_recall()
        if result is not None:
            st.session_state.logger.log(
                "ads_recall_submitted", result,
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

    elif scr == SCREEN_DEMOGRAPHICS:
        result = render_demographics_end()
        if result is not None:
            st.session_state.logger.log(
                "demographics_post_submitted", result,
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_VALIDATION:
        result = render_validation_questions()
        if result is not None:
            ctrl.validation_results = result
            st.session_state.logger.log(
                "validation_submitted",
                result,
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DECEPTION_DISCLOSURE:
        result = render_deception_disclosure()
        if result is not None:
            st.session_state.logger.log(
                "deception_disclosure_submitted", result,
                ad_mode="session", conversation_id=ctrl.participant_id, source="user",
            )
            if result.get("withdrew"):
                log.warning("Participant {} withdrew at deception disclosure", ctrl.participant_id)
            ctrl.advance()
            st.rerun()

    elif scr == SCREEN_DONE:
        export_session_data(ctrl)
        log.info(
            "Session complete | pid={} | exp={} | conditions={}",
            ctrl.participant_id,
            st.session_state.logger.experiment_id,
            len(ctrl.condition_results),
        )
        render_done()

    else:
        st.error(f"Unknown screen: {scr}")
