"""
Stage 4 — Reranker.

Reads  : state.query, state.candidates
Writes : state.ranked  (list of RankedCandidate, sorted by score desc)

Model  : HuggingFace cross-encoder (GPU 1).
         Swap reranker_model_name in RetrievalConfig to use any
         cross-encoder or Qwen reranker checkpoint.

This stage provides semantic precision over recall:
  Stage 2 (dense) maximises recall  → top-100 broad candidates
  Stage 4 (rerank) maximises precision → top-10 semantically relevant

Only the top reranker_top_k candidates from Stage 2/3 are scored here
to keep latency manageable.
"""

from __future__ import annotations

from core.config import RERANKER_MODEL_NAME, RERANKER_DEVICE, RERANKER_TOP_K
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState, RankedCandidate


class Reranker(PipelineStage):
    """
    Cross-encoder reranker over the dense / hybrid candidate list.

    Config keys (core.config)
    -------------------------
    RERANKER_MODEL_NAME, RERANKER_DEVICE, RERANKER_TOP_K

    Output
    ------
    state.ranked : list of RankedCandidate sorted descending by score,
                   length <= RERANKER_TOP_K.
    """

    def __init__(self) -> None:
        from core.retrieval.rerankers import build_reranker
        self._reranker = build_reranker(
            model_name=RERANKER_MODEL_NAME,
            device=RERANKER_DEVICE,
        )
        self._top_k = RERANKER_TOP_K

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        candidates = state.candidates[: self._top_k]
        state.ranked = self._reranker.rerank(state.query, candidates)
        return state
