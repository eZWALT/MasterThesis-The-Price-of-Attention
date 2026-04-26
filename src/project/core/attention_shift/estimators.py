"""
Attention estimators.

An AttentionEstimator maps a conversation history C to a distribution
P(Z | C) over a latent concept space Z.

Current implementations:
  - DummyEstimator : uniform placeholder.

Planned:
  - EmbeddingEstimator : sentence-transformers → topic clusters.
  - LogprobEstimator   : LLM logprobs over concept probes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict

import numpy as np

from core.config import DEFAULT_N_CONCEPTS
from core.attention_shift.shift import AttentionState


class AttentionEstimator(ABC):
    """
    Base class for estimating P(Z | C).

    Subclass this to plug in different backends as the research
    evolves.
    """

    @abstractmethod
    def estimate(self, conversation: List[Dict[str, str]]) -> AttentionState:
        """Compute P(Z | C) for a conversation history."""
        ...


class DummyEstimator(AttentionEstimator):
    """
    Placeholder estimator returning a uniform distribution.
    Replace with a real implementation.
    """

    def __init__(self, n_concepts: int = DEFAULT_N_CONCEPTS):
        self.n_concepts = n_concepts

    def estimate(self, conversation: List[Dict[str, str]]) -> AttentionState:
        uniform = np.ones(self.n_concepts) / self.n_concepts
        return AttentionState(
            distribution=uniform,
            labels=[f"z_{i}" for i in range(self.n_concepts)],
            metadata={"estimator": "dummy", "n_turns": len(conversation)},
        )
