"""
Attention Shift — semantic trajectory analysis (Δ_attn).

Cross-cutting metric module used by the Conversation Engine to
measure how ad interventions shift conversational focus.

Paper reference: Section 2.3 — Metrics (Semantic Shift).
"""

from core.attention_shift.shift import compute_attention_shift, AttentionShiftResult, AttentionState
from core.attention_shift.estimators import AttentionEstimator, DummyEstimator
from core.attention_shift.divergence import kl_divergence, cosine_divergence, jensen_shannon_divergence

__all__ = [
    "compute_attention_shift",
    "AttentionShiftResult",
    "AttentionState",
    "AttentionEstimator",
    "DummyEstimator",
    "kl_divergence",
    "cosine_divergence",
    "jensen_shannon_divergence",
]
