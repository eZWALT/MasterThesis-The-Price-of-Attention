"""
TARA — Experiment Controller.

Manages the progression of an experimental session:
  consent → baseline → trials (with counterbalancing) → surveys → debrief.

Paper reference: Section 6.3 — Experiment Controller.

STATUS: stub — to be implemented when the full session pipeline is built.
"""

from __future__ import annotations

from typing import List, Optional

from core.config import TRIALS_PER_SESSION, AD_MODES
from core.experiment.tasks import TaskDefinition, TASK_CATALOG


class ExperimentController:
    """
    Orchestrates the experimental session for one participant.

    Responsibilities:
      - Assign task order and ad conditions (Latin square counterbalancing).
      - Track trial boundaries and turn indices.
      - Trigger ad injection events at the correct turns.
      - Gate transitions between session phases.

    TODO: Implement Latin-square assignment for task × ad_mode.
    TODO: Implement session phase gating (consent → baseline → trials → survey).
    """

    def __init__(
        self,
        participant_id: str,
        n_trials: int = TRIALS_PER_SESSION,
    ):
        self.participant_id = participant_id
        self.n_trials = n_trials
        self.current_trial: int = 0

        # Will be populated by counterbalancing logic
        self.trial_plan: List[dict] = []  # [{task: TaskDefinition, ad_mode: str}, ...]

    # ── Counterbalancing ──────────────────────────────────────

    def build_trial_plan(
        self,
        tasks: Optional[List[TaskDefinition]] = None,
        ad_modes: Optional[List[str]] = None,
    ) -> List[dict]:
        """
        Generate a counterbalanced assignment of tasks and ad conditions.

        TODO: Implement Latin-square rotation keyed on participant_id.
        """
        tasks = tasks or TASK_CATALOG[: self.n_trials]
        ad_modes = ad_modes or AD_MODES[: self.n_trials]
        self.trial_plan = [
            {"task": t, "ad_mode": m}
            for t, m in zip(tasks, ad_modes)
        ]
        return self.trial_plan

    # ── Trial progression ─────────────────────────────────────

    def next_trial(self) -> Optional[dict]:
        """Advance to the next trial and return its config, or None if done."""
        if self.current_trial >= len(self.trial_plan):
            return None
        trial = self.trial_plan[self.current_trial]
        self.current_trial += 1
        return trial

    @property
    def is_session_complete(self) -> bool:
        return self.current_trial >= len(self.trial_plan)
