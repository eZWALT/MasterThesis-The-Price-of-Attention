"""
Stage 5 — Ad Formatter.

Reads  : state.ranked, state.intent
Writes : state.top_ad  (Ad dataclass)

This is the only stage that knows about the Ad model.
It converts the top-ranked CatalogItem into the Ad dataclass consumed
by the injectors, preserving the retrieval score for logging.

No model inference happens here — pure data transformation.
"""

from __future__ import annotations

from core.config import RETRIEVAL_FINAL_TOP_N, DEFAULT_AD_CTA
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState


class AdFormatter(PipelineStage):
    """
    Converts the top-ranked CatalogItem into an Ad dataclass.

    Config keys (core.config)
    -------------------------
    RETRIEVAL_FINAL_TOP_N

    Output
    ------
    state.top_ad : Ad instance ready for injection, or None if
                   state.ranked is empty (pipeline will fall back to mock).
    """

    def __init__(self) -> None:
        self._top_n = RETRIEVAL_FINAL_TOP_N

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if not state.ranked:
            state.top_ad = None
            return state

        best = state.ranked[0]  # highest reranking score

        from core.ad_injection.models import Ad
        state.top_ad = Ad(
            title=best.item.title,
            text=best.item.text,
            cta=best.item.metadata.get("cta", DEFAULT_AD_CTA),
            question=best.item.metadata.get("question", ""),
            source_item_id=best.item.item_id,
            relevance_score=best.score,
            metadata=best.item.metadata,
        )
        return state
