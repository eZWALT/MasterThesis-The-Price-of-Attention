"""
Base class for all retrieval pipeline stages.

Every stage receives a PipelineState, mutates exactly the fields it is
responsible for, and returns the same state object.
Stages must not call each other — they are composed solely by the pipeline.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.retrieval.stages.state import PipelineState


class PipelineStage(ABC):
    """
    Contract for a single retrieval stage.

    Subclasses must implement run() and should:
      - read only from state fields written by earlier stages
      - write only to the state fields they own
      - raise on unrecoverable errors; gracefully degrade otherwise
    """

    @abstractmethod
    def run(self, state: PipelineState) -> PipelineState:
        """Mutate state in-place and return it."""
        ...

    def __repr__(self) -> str:
        return self.__class__.__name__
