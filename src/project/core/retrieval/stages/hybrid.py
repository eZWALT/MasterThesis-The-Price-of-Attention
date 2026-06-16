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

from typing import Dict, List

from core.config import USE_HYBRID, BM25_WEIGHT, DENSE_WEIGHT, RRF_K
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
        # Cache tokenised texts by item_id — avoids re-splitting the same
        # catalog item's text on every retrieval turn.
        self._token_cache: dict[str, List[str]] = {}

    # ── private ─────────────────────────────────────────────────────────

    def _apply_metadata_filters(
        self, items: List[CatalogItem], filters: dict | None = None
    ) -> List[CatalogItem]:
        """Remove items that fail any active metadata filter."""
        filters = filters or self._filters
        if not filters:
            return items
        filtered = []
        allowed_cats = filters.get("categories")
        max_price = filters.get("max_price")
        for item in items:
            if allowed_cats:
                item_cat = item.metadata.get("filename", "")
                if item_cat not in allowed_cats:
                    continue
            if max_price is not None:
                if item.price > max_price:
                    continue
            filtered.append(item)
        return filtered

    def _tokenise_item(self, item: CatalogItem) -> List[str]:
        """Tokenise item text with caching — avoids re-splitting across turns."""
        tok = self._token_cache.get(item.item_id)
        if tok is not None:
            return tok
        tok = item.text.lower().split()
        self._token_cache[item.item_id] = tok
        return tok

    def _bm25_rescore(
        self, query: str, items: List[CatalogItem]
    ) -> tuple[List[CatalogItem], Dict[str, float]]:
        """Re-rank candidates with BM25 + RRF and return (sorted_items, {item_id: rrf_score})."""
        from rank_bm25 import BM25Okapi

        tokenised_corpus = [self._tokenise_item(item) for item in items]
        bm25 = BM25Okapi(tokenised_corpus)
        bm25_scores = bm25.get_scores(query.lower().split())

        # For each item at dense rank i, look up its rank in BM25-score order.
        bm25_rank_of: dict[int, int] = {
            dense_idx: bm25_rank
            for bm25_rank, dense_idx in enumerate(
                sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)
            )
        }

        k = RRF_K
        rrf_scores = [
            self._dense_w * (1.0 / (k + dense_rank + 1))
            + self._bm25_w * (1.0 / (k + bm25_rank_of[dense_rank] + 1))
            for dense_rank in range(len(items))
        ]
        sorted_pairs = sorted(zip(rrf_scores, items), key=lambda x: x[0], reverse=True)
        sorted_items = [item for _, item in sorted_pairs]
        score_dict = {item.item_id: score for score, item in sorted_pairs}
        return sorted_items, score_dict

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if not self._enabled or not state.candidates:
            return state

        filters = dict(self._filters)
        if state.categories:
            filters["categories"] = list(state.categories)
        state.candidates = self._apply_metadata_filters(state.candidates, filters)
        if state.candidates:
            state.candidates, state.hybrid_scores = self._bm25_rescore(state.query, state.candidates)
        return state
