"""
Stage 5 — Ad Formatter.

Reads  : state.ranked, state.intent
Writes : state.top_ads, state.top_ad  (Ad dataclasses)

This is the only stage that knows about the Ad model.
It converts the top-ranked CatalogItems into Ad dataclasses consumed
by the injectors, preserving retrieval scores for logging.

No model inference happens here — pure data transformation.
"""

from __future__ import annotations

from core.config import (
    RETRIEVAL_FINAL_TOP_N,
    DEFAULT_AD_CTA,
    FORMATTER_CANDIDATE_POOL,
    USE_RERANKER,
)
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState, RankedCandidate


class AdFormatter(PipelineStage):
    """
    Converts the top-N ranked CatalogItems into Ad dataclasses.

    Config keys (core.config)
    -------------------------
    RETRIEVAL_FINAL_TOP_N

    Output
    ------
    state.top_ads : up to RETRIEVAL_FINAL_TOP_N ads for LLM selection.
    state.top_ad  : primary ad (top_ads[0]) for UI and logging.
    """

    def __init__(self) -> None:
        self._top_n = RETRIEVAL_FINAL_TOP_N

    def _to_ad(self, candidate: RankedCandidate):
        from core.ad_injection.models import Ad

        item = candidate.item
        return Ad(
            title=item.title,
            text=item.text,
            cta=item.metadata.get("cta", DEFAULT_AD_CTA),
            question=item.metadata.get("question", ""),
            source_item_id=item.item_id,
            relevance_score=candidate.score,
            metadata=item.metadata,
        )

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        from core.log import logger

        ranked: list[RankedCandidate] = []
        if state.ranked:
            ranked = state.ranked
            logger.debug(
                "AdFormatter: Using {} ranked candidates",
                len(ranked),
            )
        elif state.candidates:
            pool = FORMATTER_CANDIDATE_POOL if not USE_RERANKER else self._top_n
            ranked = [
                RankedCandidate(item=item, score=0.0)
                for item in state.candidates[: max(pool, self._top_n)]
            ]
            logger.debug(
                "AdFormatter: Using {} fallback candidates",
                len(ranked),
            )
        else:
            logger.warning("AdFormatter: No candidates or ranked ads available.")
            state.top_ad = None
            state.top_ads = []
            return state

        state.top_ads = [self._to_ad(c) for c in ranked[: self._top_n]]
        state.top_ad = state.top_ads[0] if state.top_ads else None
        return state
