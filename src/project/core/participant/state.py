"""
Participant State.

Maintains all session-specific information for one participant:
  - Participant ID and metadata
  - OCEAN personality scores
  - Assigned experimental conditions
  - Current trial and turn index

Paper reference: Section 6.4 — Participant State Manager.

STATUS: stub — to be wired into the Experiment Controller and UI.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional, List


@dataclass
class OceanScores:
    """Big Five personality trait scores (0-1 normalised)."""
    openness: float = 0.0
    conscientiousness: float = 0.0
    extraversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {
            "O": self.openness,
            "C": self.conscientiousness,
            "E": self.extraversion,
            "A": self.agreeableness,
            "N": self.neuroticism,
        }


@dataclass
class ParticipantState:
    """
    Persisted state for a single experimental participant.

    Attributes
    ----------
    participant_id : unique identifier (auto-generated if not provided).
    ocean : OCEAN personality scores (filled after personality assessment).
    assigned_conditions : list of {task_id, ad_mode} dicts from the controller.
    current_trial_index : 0-based index into assigned_conditions.
    metadata : free-form metadata (e.g., demographics, consent timestamp).
    """
    participant_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ocean: Optional[OceanScores] = None
    assigned_conditions: List[Dict[str, str]] = field(default_factory=list)
    current_trial_index: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)

    # ── Convenience ───────────────────────────────────────────

    @property
    def current_condition(self) -> Optional[Dict[str, str]]:
        """Return the current trial's condition dict, or None if done."""
        if self.current_trial_index >= len(self.assigned_conditions):
            return None
        return self.assigned_conditions[self.current_trial_index]

    def advance_trial(self) -> None:
        """Move to the next trial."""
        self.current_trial_index += 1

    def to_dict(self) -> Dict:
        return {
            "participant_id": self.participant_id,
            "ocean": self.ocean.to_dict() if self.ocean else None,
            "assigned_conditions": self.assigned_conditions,
            "current_trial_index": self.current_trial_index,
            "metadata": self.metadata,
        }
