"""
Experiment Controller — Workflow B.

Implements the 5-condition within-subject protocol:

  consent → baseline (eye-tracking, 30 s) → warmup_chat
  → [condition_intro → condition_chat → condition_conclusion → post_condition_survey] × 5
  → recall (4 steps, one per ad condition)
  → ocean (BFI-10) → demographics → deception_disclosure → done

Tasks are counterbalanced with Latin-square rotation (by cb_group or pid hash).
Conditions are shuffled independently, then zipped with tasks.

Paper reference: Sections 6.3 — Experiment Controller, Workflow B.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from core.config import (
    CONDITIONS,
    CONDITION_AD_MODE,
    CONDITION_TIMING,
    EXIT_N_TRIALS,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    FINISH_BUTTON_VISIBLE_FROM_TURN,
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_WARMUP_CHAT,
    SCREEN_BASELINE,
    SCREEN_CONDITION_INTRO,
    SCREEN_CONDITION_CHAT,
    SCREEN_CONDITION_CONCLUSION,
    SCREEN_POST_CONDITION_SURVEY,
    SCREEN_ADS_RECALL,
    SCREEN_OCEAN,
    SCREEN_DECEPTION_DISCLOSURE,
    SCREEN_DONE,
    WARMUP_TASK_ID,
    WARMUP_TURNS,
)
from core.experiment.tasks import TaskDefinition, TASK_CATALOG, TASK_BY_ID


# ── Screen lists ─────────────────────────────────
_PRE_CONDITION_SCREENS: list[str] = [
    SCREEN_CONSENT,
    SCREEN_BASELINE,
    SCREEN_WARMUP_CHAT,
]

_CONDITION_SCREENS: list[str] = [
    SCREEN_CONDITION_INTRO,
    SCREEN_CONDITION_CHAT,
    SCREEN_CONDITION_CONCLUSION,
    SCREEN_POST_CONDITION_SURVEY,
]

_POST_CONDITION_SCREENS: list[str] = [
    SCREEN_ADS_RECALL,
    SCREEN_OCEAN,
    SCREEN_DEMOGRAPHICS,
    SCREEN_DECEPTION_DISCLOSURE,
    SCREEN_DONE,
]


class ExperimentController:
    """
    Workflow B state machine.

    Pure state — no Streamlit dependency.  UI calls ``advance()``
    and reads ``current_screen`` to decide what to render.
    """

    def __init__(
        self,
        participant_id: str,
        tasks: Optional[List[TaskDefinition]] = None,
        model: Optional[str] = None,
        seed: Optional[int] = None,
        cb_group: Optional[int] = None,
        turns_min: int = MIN_TURNS_PER_TRIAL,
        turns_max: int = MAX_TURNS_PER_TRIAL,
        finish_from: Optional[int] = None,
    ):
        self.participant_id = participant_id
        self.model = model
        self.seed = seed
        self.cb_group = cb_group
        self.turns_min = turns_min
        self.turns_max = turns_max
        self.finish_from: int = finish_from if finish_from is not None else FINISH_BUTTON_VISIBLE_FROM_TURN

        # Screen state
        self.current_screen: str = SCREEN_CONSENT
        self._screen_history: list[str] = []
        self.current_condition_index: int = 0   # 0-based
        self._condition_sub_index: int = 0       # index within _CONDITION_SCREENS

        # ── Trial plan ────────────────────────────────
        # List of dict: {condition, ad_mode, ad_window, task, ad_turn}
        self.condition_plan: List[dict] = []

        # ── Collected data ────────────────────────────
        self.demographics: Dict[str, Any] = {}
        self.ocean_raw: List[int] = []
        self.ocean_scores: Dict[str, float] = {}
        self.condition_results: List[Dict[str, Any]] = []   # one per condition
        self.condition_surveys: List[Dict[str, int | str]] = []    # post-condition Likert + text

    # ── Counterbalancing ─────────────────────────

    def build_condition_plan(
        self,
        tasks: Optional[List[TaskDefinition]] = None,
    ) -> List[dict]:
        """
        Build counterbalanced condition plan.

        Strategy:
          1. Pick 5 tasks (first 5 from catalog, or supplied list).
          2. Latin-square rotate tasks by cb_group / pid hash so each
             participant sees tasks in a different sequential order.
          3. Shuffle conditions independently (using seed when set).
          4. Zip the two shuffled lists together.
          5. Sample exactly 1 ad turn per condition window.
        """
        conditions = list(CONDITIONS)
        tasks = (tasks or TASK_CATALOG[:5])[:5]

        while len(tasks) < 5:
            tasks.append(TASK_CATALOG[len(tasks) % len(TASK_CATALOG)])

        # Latin-square rotation of tasks (removes order bias)
        n = len(tasks)
        row = (self.cb_group % n) if self.cb_group is not None else (hash(self.participant_id) % n)
        tasks = tasks[row:] + tasks[:row]

        # Shuffle conditions independently
        if self.seed is not None:
            rng = random.Random(self.seed)
            rng.shuffle(conditions)
        else:
            random.shuffle(conditions)

        # Build plan with per-condition ad_turn assignment
        self.condition_plan = []
        for cond, task in zip(conditions, tasks):
            ad_mode = CONDITION_AD_MODE.get(cond, "")
            window = CONDITION_TIMING.get(cond)
            ad_turn = None
            if window is not None and ad_mode:
                if self.seed is not None:
                    rng_win = random.Random(self.seed + hash(cond) + hash(task.id))
                    ad_turn = rng_win.randint(window[0], window[1])
                else:
                    ad_turn = random.randint(window[0], window[1])

            self.condition_plan.append({
                "condition": cond,
                "ad_mode": ad_mode,
                "ad_window": window,
                "ad_turn": ad_turn,
                "task": task,
            })

        return self.condition_plan

    def build_condition_plan_backward_compat(
        self,
        tasks: Optional[List[TaskDefinition]] = None,
        ad_modes: Optional[List[str]] = None,
    ) -> List[dict]:
        """Legacy stub — delegates to build_condition_plan."""
        return self.build_condition_plan(tasks=tasks)

    # ── Navigation ───────────────────────────────

    @property
    def n_conditions(self) -> int:
        return len(self.condition_plan)

    def advance(self, _skip_save: bool = False) -> str:
        scr = self.current_screen
        if not _skip_save:
            self._screen_history.append(scr)

        # Pre-condition sequence
        if scr in _PRE_CONDITION_SCREENS:
            idx = _PRE_CONDITION_SCREENS.index(scr)
            if idx + 1 < len(_PRE_CONDITION_SCREENS):
                self.current_screen = _PRE_CONDITION_SCREENS[idx + 1]
            else:
                self.current_condition_index = 0
                self._condition_sub_index = 0
                self.current_screen = _CONDITION_SCREENS[0]
            return self.current_screen

        # Condition screens (repeating block)
        if scr in _CONDITION_SCREENS:
            self._condition_sub_index += 1
            if self._condition_sub_index < len(_CONDITION_SCREENS):
                self.current_screen = _CONDITION_SCREENS[self._condition_sub_index]
            else:
                self.current_condition_index += 1
                if self.current_condition_index < self.n_conditions:
                    self._condition_sub_index = 0
                    self.current_screen = _CONDITION_SCREENS[0]
                else:
                    self.current_screen = _POST_CONDITION_SCREENS[0]
            return self.current_screen

        # Post-condition sequence
        if scr in _POST_CONDITION_SCREENS:
            idx = _POST_CONDITION_SCREENS.index(scr)
            if idx + 1 < len(_POST_CONDITION_SCREENS):
                self.current_screen = _POST_CONDITION_SCREENS[idx + 1]
            return self.current_screen

        return self.current_screen

    def go_back(self) -> str:
        """Go back to the previous screen (dev-flow only)."""
        if self._screen_history:
            self.current_screen = self._screen_history.pop()
        return self.current_screen

    # ── Condition helpers ───────────────────────

    @property
    def current_condition_config(self) -> Optional[dict]:
        if 0 <= self.current_condition_index < len(self.condition_plan):
            return self.condition_plan[self.current_condition_index]
        return None

    @property
    def condition_number(self) -> int:
        return self.current_condition_index + 1

    @property
    def is_session_complete(self) -> bool:
        return self.current_screen == SCREEN_DONE

    @property
    def can_exit_early(self) -> bool:
        return self.current_condition_index >= EXIT_N_TRIALS

    def exit_early(self) -> None:
        self.condition_plan = self.condition_plan[:self.current_condition_index]
        self._condition_sub_index = _CONDITION_SCREENS.index(SCREEN_POST_CONDITION_SURVEY)
        self.current_screen = SCREEN_POST_CONDITION_SURVEY

    __all__ = [
        "ExperimentController",
    ]
