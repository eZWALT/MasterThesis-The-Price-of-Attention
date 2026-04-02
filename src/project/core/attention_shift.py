"""
TARA — Attention Shift Module.

Implements the formal metric for measuring how ad interventions
shift the semantic trajectory of a conversation.

Theory
------
Let Z be a latent space of intents / topics / semantic concepts.
Given a conversation C_≤t = (u_1, ..., u_t), define:

    A_t = P(Z | C_≤t)

as the attention state — a distribution of conversational focus
over latent concepts.

Attention Shift (non-causal):

    Δ_attn = D( P(Z | C_post) ‖ P(Z | C_pre) )

where D is a divergence measure (KL, cosine, Jensen-Shannon, etc.).

This module provides pluggable estimators for P(Z|C) and divergence
functions, so different backends can be swapped in as the research
evolves.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any

import numpy as np


# ── Data types ────────────────────────────────────────────────


@dataclass
class AttentionState:
    """Distribution over latent concepts Z given a conversation."""
    distribution: np.ndarray            # P(Z | C), shape (|Z|,)
    labels: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttentionShiftResult:
    """Result of computing Δ_attn between pre/post states."""
    divergence: float
    method: str
    pre_state: AttentionState
    post_state: AttentionState
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Divergence functions ──────────────────────────────────────

def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
    """KL(P ‖ Q) with smoothing."""
    p = np.clip(p, epsilon, None)
    q = np.clip(q, epsilon, None)
    return float(np.sum(p * np.log(p / q)))


def cosine_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """1 − cosine_similarity(p, q)."""
    dot = np.dot(p, q)
    norm = np.linalg.norm(p) * np.linalg.norm(q)
    if norm == 0:
        return 1.0
    return float(1.0 - dot / norm)


def jensen_shannon_divergence(p: np.ndarray, q: np.ndarray) -> float:
    """Symmetric Jensen-Shannon divergence."""
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)


DIVERGENCE_REGISTRY = {
    "kl": kl_divergence,
    "cosine": cosine_divergence,
    "jsd": jensen_shannon_divergence,
}


# ── Attention estimators ──────────────────────────────────────

class AttentionEstimator(ABC):
    """
    Base class for estimating P(Z | C).

    Subclass this to implement different backends:
    - Embedding-based (e.g. sentence-transformers → topic clusters)
    - LLM-logprob-based
    - Knowledge-graph-based
    """

    @abstractmethod
    def estimate(self, conversation: List[Dict[str, str]]) -> AttentionState:
        """Compute P(Z | C) for a conversation history."""
        ...


class DummyEstimator(AttentionEstimator):
    """
    Placeholder estimator returning a uniform distribution.
    Replace with a real implementation (e.g. embedding + topic model).
    """

    def __init__(self, n_concepts: int = 16):
        self.n_concepts = n_concepts

    def estimate(self, conversation: List[Dict[str, str]]) -> AttentionState:
        uniform = np.ones(self.n_concepts) / self.n_concepts
        return AttentionState(
            distribution=uniform,
            labels=[f"z_{i}" for i in range(self.n_concepts)],
            metadata={"estimator": "dummy", "n_turns": len(conversation)},
        )


# TODO: EmbeddingEstimator — encode conversation with sentence-transformers,
#       project into topic clusters, normalize as P(Z|C).

# TODO: LogprobEstimator — extract token-level logprobs from the LLM,
#       aggregate over predefined concept probes.


# ── Main API ──────────────────────────────────────────────────

def compute_attention_shift(
    C_pre: List[Dict[str, str]],
    C_post: List[Dict[str, str]],
    estimator: AttentionEstimator | None = None,
    divergence: str = "jsd",
) -> AttentionShiftResult:
    """
    Compute Attention Shift Δ_attn between pre-ad and post-ad
    conversation states.

    Parameters
    ----------
    C_pre : conversation before ad exposure.
    C_post : conversation after ad exposure.
    estimator : how to estimate P(Z|C). Defaults to DummyEstimator.
    divergence : divergence name from DIVERGENCE_REGISTRY.

    Returns
    -------
    AttentionShiftResult with the computed divergence value.
    """
    if estimator is None:
        estimator = DummyEstimator()

    pre_state = estimator.estimate(C_pre)
    post_state = estimator.estimate(C_post)

    div_fn = DIVERGENCE_REGISTRY.get(divergence)
    if div_fn is None:
        raise ValueError(
            f"Unknown divergence '{divergence}'. "
            f"Available: {list(DIVERGENCE_REGISTRY.keys())}"
        )

    shift = div_fn(post_state.distribution, pre_state.distribution)

    return AttentionShiftResult(
        divergence=shift,
        method=divergence,
        pre_state=pre_state,
        post_state=post_state,
        metadata={"n_pre_turns": len(C_pre), "n_post_turns": len(C_post)},
    )
