"""
Stage 3 — Hybrid Refiner  (optional).

Reads  : state.query, state.candidates
Writes : state.candidates  (re-scored and filtered list)

Logic  :
  1. Score each candidate with BM25 (lexical).
  2. Combine BM25 score with the FAISS cosine score via Reciprocal Rank
     Fusion (RRF), or a configurable weighted sum.
  3. Apply optional metadata filters (category, price ceiling, etc.).

Disabled automatically when RetrievalConfig.use_hybrid = False,
in which case this stage is a no-op pass-through.

Dependencies : rank-bm25 (CPU-only, lightweight).
"""

from __future__ import annotations

from typing import List

from core.config import USE_HYBRID, BM25_WEIGHT, DENSE_WEIGHT
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState, CatalogItem


class HybridRefiner(PipelineStage):
    """
    Optional BM25 + FAISS score fusion with metadata pre-filtering.

    Config keys (core.config)
    -------------------------
    USE_HYBRID, BM25_WEIGHT, DENSE_WEIGHT

    Parameters
    ----------
    metadata_filters : optional dict of {field: value} applied before
                       RRF fusion (e.g. {"category": "electronics"}).

    Output
    ------
    state.candidates : same list, possibly trimmed by metadata filters
                       and re-ordered by fused score.
                       If USE_HYBRID=False, state is returned unchanged.
    """

    def __init__(self, metadata_filters: dict | None = None) -> None:
        self._enabled = USE_HYBRID
        self._bm25_w = BM25_WEIGHT
        self._dense_w = DENSE_WEIGHT
        self._filters = metadata_filters or {}

    # ── private ─────────────────────────────────────────────────────────

    def _apply_metadata_filters(self, items: List[CatalogItem]) -> List[CatalogItem]:
        """Remove items that fail any active metadata filter."""
        if not self._filters:
            return items
        filtered = []
        for item in items:
            if "category" in self._filters:
                if item.category != self._filters["category"]:
                    continue
            if "max_price" in self._filters:
                if item.price > self._filters["max_price"]:
                    continue
            filtered.append(item)
        return filtered

    def _bm25_rescore(
        self, query: str, items: List[CatalogItem]
    ) -> List[CatalogItem]:
        """Re-rank candidates with BM25 + RRF and return sorted list."""
        from rank_bm25 import BM25Okapi

        tokenised_corpus = [item.text.lower().split() for item in items]
        bm25 = BM25Okapi(tokenised_corpus)
        bm25_scores = bm25.get_scores(query.lower().split())

        # For each item at dense rank i, look up its rank in BM25-score order.
        bm25_rank_of: dict[int, int] = {
            dense_idx: bm25_rank
            for bm25_rank, dense_idx in enumerate(
                sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
            )
        }

        # Reciprocal Rank Fusion (k=60 is a standard default).
        k = 60
        rrf_scores = [
            self._dense_w * (1.0 / (k + dense_rank + 1))
            + self._bm25_w * (1.0 / (k + bm25_rank_of[dense_rank] + 1))
            for dense_rank in range(len(items))
        ]
        return [item for _, item in sorted(zip(rrf_scores, items), key=lambda x: x[0], reverse=True)]

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if not self._enabled or not state.candidates:
            return state

        state.candidates = self._apply_metadata_filters(state.candidates)
        if state.candidates:
            state.candidates = self._bm25_rescore(state.query, state.candidates)
        return state
