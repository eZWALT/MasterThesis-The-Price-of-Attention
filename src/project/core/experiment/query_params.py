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
            Example: ?tasks=info_optimize_routine,trans_plan_trip
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

ad_turns    1-indexed user turns at which ads are injected (comma-separated)
            Example: ?ad_turns=2,5
            Default: AD_INJECTION_TURNS from config

bfi         BFI version used for the OCEAN personality screen
            Values : 10 → BFI-10 (10 items, ~1 min)
                     44 → BFI-44 (44 items, ~10 min)
            Default: 44

───────────────────────────────────────────────────────────────────────────────
EXAMPLE URLS
───────────────────────────────────────────────────────────────────────────────

Full prod session, specific task/mode assignment, file persistence:
  http://localhost:7777?pid=p01&tasks=trans_plan_trip,social_new_hobby&modes=2_in_chat,4_adjacent&store=file

Reproducible counterbalance group B, seed fixed:
  http://localhost:7777?pid=p02&cb=1&seed=7&store=file

Reduced turns, early ad injection for pilot:
  http://localhost:7777?dev=flow&turns_min=2&turns_max=4&ad_turns=1,3

Dev flow test, skip consent and baseline:
  http://localhost:7777?dev=flow&skip=consent,baseline,demographics

Single-trial debug with implicit ads:
  http://localhost:7777?dev=flow&n=1&modes=5_implicit&skip=consent,baseline,demographics,ocean

───────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import streamlit as st

from core.config import (
    AD_MODES,
    DEFAULT_MODEL,
    DEV_QUERY_PARAM,
    TRIALS_PER_SESSION,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    AD_INJECTION_TURNS,
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_OCEAN,
    SCREEN_BASELINE,
    SCREEN_PRACTICE,
    SCREEN_TRIAL_INTRO,
    SCREEN_FINAL_SURVEY,
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
}


@dataclass
class ExperimentParams:
    """
    Fully resolved experiment parameters derived from URL query params.
    All fields have safe defaults — absent params → config defaults.
    """
    # Routing
    dev_mode: bool = False
    flow_test: bool = False

    # Session identity
    participant_id: Optional[str] = None    # None → auto-generate

    # Trial plan
    n_trials: int = TRIALS_PER_SESSION
    tasks: List[TaskDefinition] = field(default_factory=list)
    ad_modes: List[str] = field(default_factory=list)

    # Screens to auto-skip
    skip_screens: set = field(default_factory=set)

    # LLM override
    model: Optional[str] = None             # None → DEFAULT_MODEL

    # Counterbalancing & reproducibility
    seed: Optional[int] = None              # None → non-deterministic
    cb_group: Optional[int] = None          # None → derived from pid hash

    # Turn constraints (per trial)
    turns_min: int = MIN_TURNS_PER_TRIAL
    turns_max: int = MAX_TURNS_PER_TRIAL
    ad_turns: List[int] = field(default_factory=lambda: list(AD_INJECTION_TURNS))

    # BFI version for OCEAN screen
    bfi_version: str = "10"                  # "10" | "44"

    # Persistence
    store_backend: str = "null"             # null | file


def parse_query_params() -> ExperimentParams:
    """
    Read st.query_params and return a fully resolved ExperimentParams.
    Invalid values are silently ignored (fallback to defaults).
    """
    p = st.query_params
    params = ExperimentParams()

    # ── Routing ──────────────────────────────────────────────
    dev_raw = p.get(DEV_QUERY_PARAM, "").lower()
    params.dev_mode   = dev_raw in ("true", "1", "yes")
    params.flow_test  = dev_raw == "flow"

    # ── Participant ID ────────────────────────────────────────
    pid = p.get("pid", "").strip()
    if pid:
        params.participant_id = pid

    # ── Number of trials ─────────────────────────────────────
    try:
        n = int(p.get("n", ""))
        if 1 <= n <= 20:
            params.n_trials = n
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

    # ── Skip screens ─────────────────────────────────────────
    skip_raw = p.get("skip", "").strip()
    if skip_raw:
        params.skip_screens = {s for s in skip_raw.split(",") if s in SKIPPABLE_SCREENS}

    # ── Model override ────────────────────────────────────────
    model_raw = p.get("model", "").strip()
    if model_raw:
        params.model = model_raw

    # ── BFI version ───────────────────────────────────────────
    bfi_raw = p.get("bfi", "").strip()
    if bfi_raw in ("10", "44"):
        params.bfi_version = bfi_raw

    # ── Persistence backend ───────────────────────────────────
    store_raw = p.get("store", "null").lower()
    if store_raw in ("null", "file"):
        params.store_backend = store_raw

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
    except (ValueError, TypeError):
        pass

    try:
        tmax = int(p.get("turns_max", ""))
        if 1 <= tmax <= 30:
            params.turns_max = tmax
    except (ValueError, TypeError):
        pass

    # Ensure turns_min <= turns_max
    if params.turns_min > params.turns_max:
        params.turns_max = params.turns_min

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

    return params
