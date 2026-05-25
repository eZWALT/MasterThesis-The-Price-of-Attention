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
        import time
        from core.log import logger
        t0 = time.time()
        from core.ad_injection.models import Ad
        # Prefer ranked, fallback to candidates, else None
        best = None
        if state.ranked and len(state.ranked) > 0:
            best = state.ranked[0]
            logger.debug(f"AdFormatter: Using top ranked candidate: {best.item.title}")
        elif state.candidates and len(state.candidates) > 0:
            # Fallback: wrap candidate as RankedCandidate with score 0.0
            from core.retrieval.stages.state import RankedCandidate
            best = RankedCandidate(item=state.candidates[0], score=0.0)
            logger.debug(f"AdFormatter: Using fallback candidate: {best.item.title}")
        else:
            logger.warning("AdFormatter: No candidates or ranked ads available.")
            state.top_ad = None
            return state

        state.top_ad = Ad(
            title=best.item.title,
            text=best.item.text,
            cta=best.item.metadata.get("cta", DEFAULT_AD_CTA),
            question=best.item.metadata.get("question", ""),
            source_item_id=best.item.item_id,
            relevance_score=best.score,
            metadata=best.item.metadata,
        )
        elapsed = (time.time() - t0) * 1000
        logger.info(f"[LATENCY] AdFormatter: {elapsed:.1f} ms")
        return state
