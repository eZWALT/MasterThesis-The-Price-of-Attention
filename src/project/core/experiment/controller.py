"""
Experiment Controller.

Manages the progression of an experimental session as a linear screen
state machine:

  consent → demographics → ocean → baseline → practice
  → [trial_intro → trial_chat → post_trial_survey] × N
  → final_survey → done

Paper reference: Section 6.3 — Experiment Controller.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.config import (
    TRIALS_PER_SESSION,
    AD_MODES,
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
from core.experiment.tasks import TaskDefinition, TASK_CATALOG


# ── Ordered list of screens (non-trial portion) ──────────────
_PRE_TRIAL_SCREENS: list[str] = [
    SCREEN_CONSENT,
    SCREEN_DEMOGRAPHICS,
    SCREEN_OCEAN,
    SCREEN_BASELINE,
    SCREEN_PRACTICE,
]

_TRIAL_SCREENS: list[str] = [
    SCREEN_TRIAL_INTRO,
    SCREEN_TRIAL_CHAT,
    SCREEN_POST_TRIAL_SURVEY,
]

_POST_TRIAL_SCREENS: list[str] = [
    SCREEN_FINAL_SURVEY,
    SCREEN_DONE,
]


class ExperimentController:
    """
    Orchestrates a full experimental session for one participant.

    The controller is a *pure state machine*: it knows which screen
    the participant should see, what trial they are on, and stores
    every datum collected along the way.  It has **no Streamlit
    dependency** — the UI calls ``advance()`` and reads
    ``current_screen`` to decide what to render.
    """

    def __init__(
        self,
        participant_id: str,
        n_trials: int = TRIALS_PER_SESSION,
    ):
        self.participant_id = participant_id
        self.n_trials = n_trials

        # ── Screen state ──────────────────────────────────────
        self.current_screen: str = SCREEN_CONSENT
        self.current_trial_index: int = 0        # 0-based
        self._trial_sub_index: int = 0           # index within _TRIAL_SCREENS

        # ── Trial plan ────────────────────────────────────────
        self.trial_plan: List[dict] = []

        # ── Collected data ────────────────────────────────────
        self.demographics: Dict[str, Any] = {}
        self.ocean_raw: List[int] = []
        self.ocean_scores: Dict[str, float] = {}
        self.trial_results: List[Dict[str, Any]] = []   # one dict per trial
        self.post_trial_surveys: List[Dict[str, int]] = []
        self.final_survey: Dict[str, Any] = {}

    # ── Counterbalancing ──────────────────────────────────────

    def build_trial_plan(
        self,
        tasks: Optional[List[TaskDefinition]] = None,
        ad_modes: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Generate a counterbalanced assignment of tasks × ad conditions.

        TODO: Implement Latin-square rotation keyed on participant_id.
        """
        tasks = tasks or TASK_CATALOG[: self.n_trials]
        ad_modes = ad_modes or AD_MODES[: self.n_trials]
        self.trial_plan = [
            {"task": t, "ad_mode": m}
            for t, m in zip(tasks, ad_modes)
        ]
        return self.trial_plan

    # ── Navigation ────────────────────────────────────────────

    def advance(self) -> str:
        """
        Move to the next screen in the protocol.

        Returns the new ``current_screen`` value.
        """
        scr = self.current_screen

        # Pre-trial sequence
        if scr in _PRE_TRIAL_SCREENS:
            idx = _PRE_TRIAL_SCREENS.index(scr)
            if idx + 1 < len(_PRE_TRIAL_SCREENS):
                self.current_screen = _PRE_TRIAL_SCREENS[idx + 1]
            else:
                # Finished pre-trial → enter first trial block
                self.current_trial_index = 0
                self._trial_sub_index = 0
                self.current_screen = _TRIAL_SCREENS[0]
            return self.current_screen

        # Trial screens (repeating block)
        if scr in _TRIAL_SCREENS:
            self._trial_sub_index += 1
            if self._trial_sub_index < len(_TRIAL_SCREENS):
                self.current_screen = _TRIAL_SCREENS[self._trial_sub_index]
            else:
                # Finished one trial block → next trial or post-trial
                self.current_trial_index += 1
                if self.current_trial_index < self.n_trials:
                    self._trial_sub_index = 0
                    self.current_screen = _TRIAL_SCREENS[0]
                else:
                    self.current_screen = _POST_TRIAL_SCREENS[0]
            return self.current_screen

        # Post-trial sequence
        if scr in _POST_TRIAL_SCREENS:
            idx = _POST_TRIAL_SCREENS.index(scr)
            if idx + 1 < len(_POST_TRIAL_SCREENS):
                self.current_screen = _POST_TRIAL_SCREENS[idx + 1]
            # Already at DONE → stay
            return self.current_screen

        return self.current_screen

    # ── Trial helpers ─────────────────────────────────────────

    @property
    def current_trial_config(self) -> Optional[dict]:
        """Return ``{task, ad_mode}`` for the active trial, or None."""
        if 0 <= self.current_trial_index < len(self.trial_plan):
            return self.trial_plan[self.current_trial_index]
        return None

    @property
    def trial_number(self) -> int:
        """1-based trial number for display."""
        return self.current_trial_index + 1

    @property
    def is_session_complete(self) -> bool:
        return self.current_screen == SCREEN_DONE
