"""
TARA — Survey scoring utilities.

Computes derived scores from raw Likert responses.
All item definitions and scale bounds live in config.py.
"""

from __future__ import annotations

from typing import Dict, List

from core.config import OCEAN_ITEMS, OCEAN_SCALE_MAX


def score_ocean(raw_responses: List[int]) -> Dict[str, float]:
    """
    Compute Big Five trait scores from BFI-10 raw responses.

    Parameters
    ----------
    raw_responses : list of 10 ints (1–7 Likert), one per OCEAN_ITEMS.

    Returns
    -------
    Dict with keys O, C, E, A, N → float (1.0–7.0 each).
    """
    if len(raw_responses) != len(OCEAN_ITEMS):
        raise ValueError(
            f"Expected {len(OCEAN_ITEMS)} responses, got {len(raw_responses)}"
        )

    trait_sums: Dict[str, float] = {}
    trait_counts: Dict[str, int] = {}

    for raw, (_, trait, reversed_) in zip(raw_responses, OCEAN_ITEMS):
        score = (OCEAN_SCALE_MAX + 1) - raw if reversed_ else raw
        trait_sums[trait] = trait_sums.get(trait, 0.0) + score
        trait_counts[trait] = trait_counts.get(trait, 0) + 1

    return {
        trait: trait_sums[trait] / trait_counts[trait]
        for trait in trait_sums
    }
