"""
HuggingFace CrossEncoder reranker backend.

Wraps sentence-transformers CrossEncoder, which supports any HuggingFace
cross-encoder model (ms-marco, Qwen3-Reranker, bge-reranker…).

Swap config.reranker_model_name in RetrievalConfig to change the model
with no other code changes.
"""

from __future__ import annotations

from typing import List

from sentence_transformers import CrossEncoder

from core.retrieval.rerankers.base import RerankerModel
from core.retrieval.stages.state import CatalogItem, RankedCandidate


class CrossEncoderReranker(RerankerModel):
    """
    CrossEncoder-backed reranker.

    Parameters
    ----------
    model_name : any HuggingFace cross-encoder model id.
                 Example: "cross-encoder/ms-marco-MiniLM-L-6-v2"
                          "Qwen/Qwen3-Reranker-8B"
    device     : "cpu", "cuda:0", "cuda:1", etc.

    Notes
    -----
    CrossEncoder scores (query, passage) pairs jointly, giving much higher
    precision than bi-encoder dot-product similarity but at higher cost.
    Applied only to the top reranker_top_k candidates from Stage 2/3.
    """

    def __init__(self, model_name: str, device: str = "cpu") -> None:
        self._model = CrossEncoder(model_name, device=device)

    def rerank(self, query: str, candidates: List[CatalogItem]) -> List[RankedCandidate]:
        """
        Returns
        -------
        List[RankedCandidate] sorted descending by cross-encoder score.
        """
        if not candidates:
            return []

        pairs = [(query, item.text) for item in candidates]
        scores = self._model.predict(pairs)   # shape (N,)

        ranked = sorted(
            zip(candidates, scores),
            key=lambda x: float(x[1]),
            reverse=True,
        )
        return [
            RankedCandidate(item=item, score=float(score))
            for item, score in ranked
        ]
