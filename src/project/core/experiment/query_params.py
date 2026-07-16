"""
Query parameter management for experiment control.

This is the primary lever for configuring sessions from the URL.
The researcher crafts a URL per participant — no code changes needed.

───────────────────────────────────────────────────────────────────────────────
SUPPORTED PARAMETERS
───────────────────────────────────────────────────────────────────────────────

dev         Mode flag
            Values : true | 1 | yes → dev free-chat
                     flow           → participant flow + skip buttons
            Default: (absent) → production participant mode

pid         Force a specific participant ID (for re-running or debugging)
            Example: ?pid=abc123

tasks       Ordered comma-separated task IDs for this session
            Example: ?tasks=swt_dev_role_setup,swt_birthday_surprise
            Default: first N tasks from TASK_CATALOG

modes       Ordered comma-separated advertising mode keys
            Example: ?modes=1_classical_ui,5_implicit
            Default: first N modes from AD_MODES
            Must have same length as tasks (or tasks is auto-padded)

n           Number of trials (overrides TRIALS_PER_SESSION)
            Example: ?n=2
            Default: TRIALS_PER_SESSION

skip        Comma-separated screens to silently auto-advance past
            Useful for: ?skip=consent,baseline,demographics
            Values: consent | demographics | ocean | baseline |
                    practice | trial_intro | final_survey
            Default: (none)

model       Override the LLM model for this session
            Example: ?model=qwen2.5:32b-instruct-q4_K_M
            Default: DEFAULT_MODEL from config / env

store       Persistence backend
            Values: null (default, in-memory only) | file
            Default: null

seed        Integer seed for reproducible task/mode shuffling
            Example: ?seed=42
            Default: (absent) → non-deterministic

cb          Counterbalance group for Latin-square assignment (0-based row)
            Example: ?cb=0  ?cb=1  ?cb=2
            Default: derived from participant_id hash when absent

turns_min   Minimum user turns before the "Done" button appears
            Example: ?turns_min=4
            Default: MIN_TURNS_PER_TRIAL from config

turns_max   Maximum user turns before the chat is auto-closed
            Example: ?turns_max=8
            Default: MAX_TURNS_PER_TRIAL from config

finish_from Turn from which the "I've finished" button becomes visible
            Example: ?finish_from=5
            Default: FINISH_BUTTON_VISIBLE_FROM_TURN from config (= turns_min)

ad_turns    1-indexed user turns at which ads are injected (comma-separated)
            Example: ?ad_turns=2,5
            Default: AD_INJECTION_TURNS from config

bfi         BFI version used for the OCEAN personality screen
            Values : 10 → BFI-10 (10 items, ~1 min)
                     44 → BFI-44 (44 items, ~10 min)
            Default: 10

study       Study protocol type — sets smart defaults for the session.
            Values : lab   → BFI-10, 3 trials, baseline, full consent
                     crowd → BFI-10, 3 trials, skip baseline
            Default: lab (or env var STUDY_TYPE)
            Note: any other param explicitly in the URL overrides the
                  corresponding study default.

qe          Query expansion mode for the retrieval pipeline (Stage 0b).
            Values : none   → pass raw query to dense retriever (default)
                     hyde   → generate hypothetical product doc and embed that
                     expand → LLM rewrites query into a richer keyword form
            Default: none (or env var QUERY_EXPANSION_MODE)
            Example: ?qe=hyde

ctx_sum     Enable conversation context summarizer before retrieval (Stage 0a).
            Values : 1 / true / yes → enabled
                     0 / false / no  → disabled
            Default: off (or env var CONTEXT_SUMMARY=1)
            Example: ?ctx_sum=1

ad_sum      Enable ad text summarizer after formatter (Stage 6).
            Rewrites raw catalog description into a ≤25-word sentence.
            Values : 1 / true / yes → enabled
                     0 / false / no  → disabled
            Default: off (or env var SUMMARIZATION=1)
            Example: ?ad_sum=1

force_ad    ⚠ DEV MODE ONLY (requires dev=true or dev=flow)
            Inject an ad on every turn, ignoring the ad_turns schedule.
            Useful for rapidly testing all UI renderers without waiting N turns.
            Values : 1 / true / yes → force inject every turn
            Default: off
            Example: ?dev=flow&force_ad=1

rag         ⚠ DEV MODE ONLY (requires dev=true or dev=flow)
            Override the AD_BACKEND for this session.
            Values : 0 → force mock backend (instant, no GPU, placeholder ad)
                     1 → force RAG backend (full retrieval pipeline)
            Default: (absent) → use AD_BACKEND env var / module default
            Example: ?dev=flow&rag=0   (iterate UI without GPU)
                     ?dev=flow&rag=1   (end-to-end pipeline check)

───────────────────────────────────────────────────────────────────────────────
EXAMPLE URLS
───────────────────────────────────────────────────────────────────────────────

Lab session — full protocol, specific task/mode assignment:
  http://localhost:7777?study=lab&pid=p01&tasks=swt_dev_role_setup,swt_birthday_surprise&modes=inline_persuasive,explicit_ad_block

Crowdsourcing session — lightweight, 2 trials, BFI-10, skip baseline:
  http://localhost:7777?study=crowd&pid=p42

Crowdsourcing with HyDE query expansion + context summarizer:
  http://localhost:7777?study=crowd&pid=p42&qe=hyde&ctx_sum=1

Reproducible counterbalance group B, seed fixed:
  http://localhost:7777?study=lab&pid=p02&cb=1&seed=7

Dev — force mock ads (no pipeline), inject on every turn, skip all setup screens:
  http://localhost:7777?dev=flow&rag=0&force_ad=1&skip=consent,baseline,demographics,ocean

Dev — force RAG pipeline + HyDE, check end-to-end ad injection:
  http://localhost:7777?dev=flow&rag=1&qe=hyde&force_ad=1&skip=consent,baseline,demographics,ocean

Dev — single trial, specific mode, reduced turns:
  http://localhost:7777?dev=flow&n=1&modes=explicit_ad_block&turns_min=2&turns_max=4&skip=consent,baseline,demographics,ocean

───────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import streamlit as st

from core.config import (
    LSL_MARKER_OUTLET,
    AD_MODES,
    DEFAULT_MODEL,
    DEFAULT_STUDY_TYPE,
    DEV_QUERY_PARAM,
    STUDY_DEFAULTS,
    STUDY_TYPES,
    TRIALS_PER_SESSION,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    FINISH_BUTTON_VISIBLE_FROM_TURN,
    AD_INJECTION_TURNS,
    VALID_QUERY_EXPANSION_MODES,
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_OCEAN,
    SCREEN_BASELINE,
    SCREEN_PRACTICE,
    SCREEN_TRIAL_INTRO,
    SCREEN_FINAL_SURVEY,
    SCREEN_PROLIFIC_ID,
    SCREEN_VALIDATION,
    study_skip_screens,
)
from core.experiment.tasks import TASK_CATALOG, TASK_BY_ID, TaskDefinition


# ── Valid skippable screens ───────────────────────────────────────────────────

SKIPPABLE_SCREENS = {
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_OCEAN,
    SCREEN_BASELINE,
    SCREEN_PRACTICE,
    SCREEN_TRIAL_INTRO,
    SCREEN_FINAL_SURVEY,
    SCREEN_PROLIFIC_ID,
    SCREEN_VALIDATION
}


@dataclass
class ExperimentParams:
    """
    Fully resolved experiment parameters derived from URL query params.
    All fields have safe defaults — absent params → study type defaults.
    """
    # ── Routing ──────────────────────────────────────
    dev_mode: bool = False
    flow_test: bool = False

    # ── Study type ───────────────────────────────────
    # lab   → BFI-10, file store, 3 trials, baseline, full protocol
    # crowd → BFI-10, null store, 3 trials, skip baseline, lighter protocol
    study_type: str = DEFAULT_STUDY_TYPE

    # ── Session identity ─────────────────────────────
    participant_id: Optional[str] = None    # None → auto-generate

    # ── Trial plan ───────────────────────────────────
    n_trials: int = TRIALS_PER_SESSION
    tasks: List[TaskDefinition] = field(default_factory=list)
    ad_modes: List[str] = field(default_factory=list)

    # ── Screens to auto-skip ─────────────────────────
    skip_screens: set = field(default_factory=set)

    # ── LLM override ─────────────────────────────────
    model: Optional[str] = None             # None → DEFAULT_MODEL

    # ── Counterbalancing & reproducibility ───────────
    seed: Optional[int] = None              # None → non-deterministic
    cb_group: Optional[int] = None          # None → derived from pid hash

    # ── Turn constraints (per trial) ─────────────────
    turns_min: int = MIN_TURNS_PER_TRIAL
    turns_max: int = MAX_TURNS_PER_TRIAL
    finish_from: Optional[int] = None   # None → FINISH_BUTTON_VISIBLE_FROM_TURN
    ad_turns: List[int] = field(default_factory=lambda: list(AD_INJECTION_TURNS))

    # ── BFI version for OCEAN screen ─────────────────
    bfi_version: str = "10"                 # "10" | "44"

    # ── RAG pipeline overrides (per-session via URL) ─
    # None = "use whatever config.py / env var says"
    ctx_sum: Optional[bool] = None          # ?ctx_sum=1  → ContextSummaryStage
    query_expansion: Optional[str] = None   # ?qe=hyde|expand|none
    ad_summarize: Optional[bool] = None     # ?ad_sum=1  → SummarizationStage

    # ── Dev-only overrides ────────────────────────────
    # Available only when dev=true|flow; silently ignored in production.
    force_ad: bool = False                  # ?force_ad=1 → inject ad on every turn
    use_rag: Optional[bool] = None          # ?rag=0 → force mock  |  ?rag=1 → force RAG
    dry_run: bool = False                   # ?dry_run=1 → mock LLM + mock ads, zero cost
    webcam_enabled: bool = False
    lsl_outlet_name: str = ""            # LSL outlet name (e.g. "experiment_lab_pilot") for EEG markers

    def apply_study_defaults(self, explicitly_set: set) -> None:
        """
        Fill in per-study smart defaults for any param NOT explicitly set
        in the URL.  Called by parse_query_params() after all URL params
        have been parsed.
        """
        defaults = STUDY_DEFAULTS.get(self.study_type, {})
        for key, value in defaults.items():
            if key not in explicitly_set:
                setattr(self, key, value)


def parse_query_params() -> ExperimentParams:
    """
    Read st.query_params and return a fully resolved ExperimentParams.
    Invalid values are silently ignored (fallback to defaults).

    New parameters
    --------------
    study     : lab | crowd — dispatches protocol + smart defaults
    qe        : none | hyde | expand — query expansion mode (Stage 0b)
    ctx_sum   : 1 | 0 — enable/disable conversation context summarizer (Stage 0a)
    ad_sum    : 1 | 0 — enable/disable ad text summarizer (Stage 6)
    force_ad  : 1 (DEV ONLY) — inject an ad on every turn, ignoring ad_turns schedule
    rag       : 0 | 1 (DEV ONLY) — force mock (0) or RAG (1) backend for this session
    """
    p = st.query_params
    params = ExperimentParams()

    # Track which params were explicitly set in the URL so that
    # apply_study_defaults() does not overwrite them.
    explicitly_set: set = set()

    # ── Routing ──────────────────────────────────────────────
    dev_raw = p.get(DEV_QUERY_PARAM, "").lower()
    params.dev_mode   = dev_raw in ("true", "1", "yes")
    params.flow_test  = dev_raw == "flow"

    # ── Study type ───────────────────────────────────────────
    # Sets protocol-wide smart defaults (BFI version, store, n_trials, …).
    # Any param that is also explicitly in the URL overrides the default.
    study_raw = p.get("study", "").lower()
    if study_raw in STUDY_TYPES:
        params.study_type = study_raw
        explicitly_set.add("study_type")

    # ── Participant ID ────────────────────────────────────────
    pid = p.get("pid", "").strip()
    if pid:
        params.participant_id = pid
        explicitly_set.add("participant_id")

    # ── Number of trials ─────────────────────────────────────
    try:
        n = int(p.get("n", ""))
        if 1 <= n <= 20:
            params.n_trials = n
            explicitly_set.add("n_trials")
    except (ValueError, TypeError):
        pass

    # ── Tasks ────────────────────────────────────────────────
    tasks_raw = p.get("tasks", "").strip()
    if tasks_raw:
        resolved = [TASK_BY_ID[t] for t in tasks_raw.split(",") if t in TASK_BY_ID]
        if resolved:
            params.tasks = resolved

    # ── Ad modes ─────────────────────────────────────────────
    modes_raw = p.get("modes", "").strip()
    if modes_raw:
        resolved_modes = [m for m in modes_raw.split(",") if m in AD_MODES]
        if resolved_modes:
            params.ad_modes = resolved_modes

    # ── Align tasks & modes to n_trials ──────────────────────
    # Fallback to catalog/config defaults if not specified
    default_tasks  = TASK_CATALOG[: params.n_trials]
    default_modes  = AD_MODES[: params.n_trials]
    params.tasks    = (params.tasks    or default_tasks)[: params.n_trials]
    params.ad_modes = (params.ad_modes or default_modes)[: params.n_trials]
    # Pad if shorter than n_trials
    while len(params.tasks)    < params.n_trials:
        params.tasks.append(default_tasks[len(params.tasks) % len(default_tasks)])
    while len(params.ad_modes) < params.n_trials:
        params.ad_modes.append(default_modes[len(params.ad_modes) % len(default_modes)])

    # ── Skip screens (URL extras merged with study protocol skips) ─
    skip_raw = p.get("skip", "").strip()
    url_skip_screens: set[str] = set()
    if skip_raw:
        url_skip_screens = {s for s in skip_raw.split(",") if s in SKIPPABLE_SCREENS}

    # ── Model override ────────────────────────────────────────
    model_raw = p.get("model", "").strip()
    if model_raw:
        params.model = model_raw

    # ── BFI version ───────────────────────────────────────────
    bfi_raw = p.get("bfi", "").strip()
    if bfi_raw in ("10", "44"):
        params.bfi_version = bfi_raw
        explicitly_set.add("bfi_version")

    # ── Seed ─────────────────────────────────────────────────
    try:
        params.seed = int(p.get("seed", ""))
    except (ValueError, TypeError):
        pass

    # ── Counterbalance group ──────────────────────────────────
    try:
        cb = int(p.get("cb", ""))
        if cb >= 0:
            params.cb_group = cb
    except (ValueError, TypeError):
        pass

    # ── Turn constraints ──────────────────────────────────────
    try:
        tmin = int(p.get("turns_min", ""))
        if 1 <= tmin <= 30:
            params.turns_min = tmin
            explicitly_set.add("turns_min")
    except (ValueError, TypeError):
        pass

    try:
        tmax = int(p.get("turns_max", ""))
        if 1 <= tmax <= 30:
            params.turns_max = tmax
            explicitly_set.add("turns_max")
    except (ValueError, TypeError):
        pass

    # Ensure turns_min <= turns_max
    if params.turns_min > params.turns_max:
        params.turns_max = params.turns_min

    # ── Finish button visible from turn ────────────────────────
    try:
        ff = int(p.get("finish_from", ""))
        if 1 <= ff <= 30:
            params.finish_from = ff
    except (ValueError, TypeError):
        pass

    # ── Ad injection turns ────────────────────────────────────
    ad_turns_raw = p.get("ad_turns", "").strip()
    if ad_turns_raw:
        parsed = []
        for t in ad_turns_raw.split(","):
            try:
                v = int(t.strip())
                if v >= 1:
                    parsed.append(v)
            except ValueError:
                pass
        if parsed:
            params.ad_turns = sorted(set(parsed))
            explicitly_set.add("ad_turns")

    # ── RAG pipeline overrides ────────────────────────────────
    # ?qe=none | hyde | expand  — query expansion mode for Stage 0b
    qe_raw = p.get("qe", "").lower()
    if qe_raw in VALID_QUERY_EXPANSION_MODES:
        params.query_expansion = qe_raw

    # ?ctx_sum=1 | 0  — enable/disable conversation context summarizer (Stage 0a)
    ctx_raw = p.get("ctx_sum", "").strip()
    if ctx_raw in ("1", "true", "yes"):
        params.ctx_sum = True
    elif ctx_raw in ("0", "false", "no"):
        params.ctx_sum = False

    # ?ad_sum=1 | 0  — enable/disable ad text summarizer (Stage 6)
    ad_sum_raw = p.get("ad_sum", "").strip()
    if ad_sum_raw in ("1", "true", "yes"):
        params.ad_summarize = True
    elif ad_sum_raw in ("0", "false", "no"):
        params.ad_summarize = False

    # ?dry_run=1  — mock everything (LLM + ads), zero cost, no GPU
    dry_raw = p.get("dry_run", "").strip().lower()
    if dry_raw in ("1", "true", "yes"):
        params.dry_run = True
        params.use_rag = False

    # ?webcam=1  — enable session-wide webcam recording (lab study or dev)
    webcam_raw = p.get("webcam", "").strip().lower()
    if webcam_raw in ("1", "true", "yes"):
        params.webcam_enabled = True

    # ── LSL marker outlet ─────────────────────────────────────
    lsl_raw = p.get("lsl", "").strip()
    if lsl_raw:
        params.lsl_outlet_name = lsl_raw
    else:
        params.lsl_outlet_name = LSL_MARKER_OUTLET

    # ── Dev-only overrides (silently ignored outside dev mode) ────────────
    if params.dev_mode or params.flow_test:
        # ?force_ad=1  — inject an ad on every turn regardless of ad_turns schedule
        force_raw = p.get("force_ad", "").strip().lower()
        if force_raw in ("1", "true", "yes"):
            params.force_ad = True
        elif force_raw in ("0", "false", "no"):
            params.force_ad = False

        # ?rag=0  — force mock backend (skip retrieval pipeline, instant response)
        # ?rag=1  — force RAG backend regardless of AD_BACKEND env var
        rag_raw = p.get("rag", "").strip()
        if rag_raw == "0":
            params.use_rag = False
        elif rag_raw == "1":
            params.use_rag = True

    # ── Apply study-type smart defaults for unset params ──────
    params.apply_study_defaults(explicitly_set)

    # Protocol skips (e.g. crowd → baseline) plus any ?skip= extras
    params.skip_screens = study_skip_screens(params.study_type) | url_skip_screens

    return params
