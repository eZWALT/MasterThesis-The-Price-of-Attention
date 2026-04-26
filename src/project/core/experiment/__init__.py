"""
Experiment Controller — session flow, task definitions, counterbalancing, surveys.

Paper reference: Section 6.3 — Experiment Controller.
"""

from core.experiment.tasks import TaskDefinition, TASK_CATALOG, TASK_BY_ID
from core.experiment.controller import ExperimentController
from core.experiment.surveys import score_ocean

__all__ = [
    "TaskDefinition",
    "TASK_CATALOG",
    "TASK_BY_ID",
    "ExperimentController",
    "score_ocean",
]
