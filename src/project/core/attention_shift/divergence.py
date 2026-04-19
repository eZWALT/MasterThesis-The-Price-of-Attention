"""
TARA — Divergence functions for attention shift computation.

All magic constants (epsilon, etc.) are imported from config.
"""

from __future__ import annotations

import numpy as np

from core.config import KL_EPSILON


def kl_divergence(
    p: np.ndarray,
    q: np.ndarray,
    epsilon: float = KL_EPSILON,
) -> float:
    """KL(P ‖ Q) with additive smoothing."""
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
    """Symmetric Jensen–Shannon divergence."""
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m) + 0.5 * kl_divergence(q, m)


DIVERGENCE_REGISTRY: dict[str, callable] = {
    "kl": kl_divergence,
    "cosine": cosine_divergence,
    "jsd": jensen_shannon_divergence,
}
