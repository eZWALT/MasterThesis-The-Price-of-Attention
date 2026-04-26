"""
Attention shift computation.

Theory (from paper §2):
  Let Z be a latent space of intents / topics / semantic concepts.
  Given a conversation C_≤t = (u_1, …, u_t), define:

      A_t = P(Z | C_≤t)     — attention state

  Attention Shift (non-causal):

      Δ_attn = D( P(Z | C_post) ‖ P(Z | C_pre) )

  where D is a divergence measure (KL, cosine, Jensen–Shannon, …).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING

import numpy as np

from core.config import DEFAULT_DIVERGENCE_METHOD
from core.attention_shift.divergence import DIVERGENCE_REGISTRY

if TYPE_CHECKING:
    from core.attention_shift.estimators import AttentionEstimator


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


# ── Main API ──────────────────────────────────────────────────

def compute_attention_shift(
    C_pre: List[Dict[str, str]],
    C_post: List[Dict[str, str]],
    estimator: Optional["AttentionEstimator"] = None,
    divergence: str = DEFAULT_DIVERGENCE_METHOD,
) -> AttentionShiftResult:
    """
    Compute Attention Shift Δ_attn between pre-ad and post-ad
    conversation states.

    Parameters
    ----------
    C_pre : conversation before ad exposure.
    C_post : conversation after ad exposure.
    estimator : how to estimate P(Z|C). Defaults to DummyEstimator.
    divergence : key from DIVERGENCE_REGISTRY.

    Returns
    -------
    AttentionShiftResult with the computed divergence value.
    """
    if estimator is None:
        from core.attention_shift.estimators import DummyEstimator
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
