"""
HuggingFace CrossEncoder reranker backend.

Wraps sentence-transformers CrossEncoder, which supports any HuggingFace
cross-encoder model (ms-marco, Qwen3-Reranker, bge-reranker…).

Swap config.reranker_model_name in RetrievalConfig to change the model
with no other code changes.
"""

from __future__ import annotations

import logging
from typing import List, Optional

import torch
from sentence_transformers import CrossEncoder

from core.retrieval.rerankers.base import RerankerModel
from core.retrieval.stages.state import CatalogItem, RankedCandidate

_log = logging.getLogger(__name__)

# Map string dtype names → torch dtypes
_DTYPE_MAP = {
    "float32": torch.float32,
    "fp32": torch.float32,
    "float16": torch.float16,
    "fp16": torch.float16,
    "bfloat16": torch.bfloat16,
    "bf16": torch.bfloat16,
}


class CrossEncoderReranker(RerankerModel):
    """
    CrossEncoder-backed reranker.

    Parameters
    ----------
    model_name : any HuggingFace cross-encoder model id.
                 Example: "cross-encoder/ms-marco-MiniLM-L-6-v2"
                          "Qwen/Qwen3-Reranker-0.6B"
    device     : "cpu", "cuda:0", "cuda:1", etc.
    dtype      : "bfloat16", "float16", or "float32". Half precision halves VRAM.

    Notes
    -----
    CrossEncoder scores (query, passage) pairs jointly, giving much higher
    precision than bi-encoder dot-product similarity but at higher cost.
    Applied only to the top reranker_top_k candidates from Stage 2/3.
    """

    def __init__(self, model_name: str, device: str = "cpu", dtype: Optional[str] = None) -> None:
        model_kwargs = {}
        if dtype and dtype in _DTYPE_MAP:
            model_kwargs["dtype"] = _DTYPE_MAP[dtype]
            _log.info("[Reranker] Loading %s on %s with dtype=%s", model_name, device, dtype)
        else:
            _log.info("[Reranker] Loading %s on %s with default dtype (FP32)", model_name, device)

        self._model = CrossEncoder(model_name, device=device, model_kwargs=model_kwargs)

    def rerank(self, query: str, candidates: List[CatalogItem]) -> List[RankedCandidate]:
        """
        Returns
        -------
        List[RankedCandidate] sorted descending by cross-encoder score.
        """
        if not candidates:
            return []

        from core.config import RERANKER_PASSAGE_MAX_CHARS, RERANKER_USE_TITLE_ONLY

        pairs = []
        for item in candidates:
            if RERANKER_USE_TITLE_ONLY:
                passage = (item.title or "").strip()
            else:
                passage = f"{item.title}. {(item.text or '')[:RERANKER_PASSAGE_MAX_CHARS]}"
            pairs.append((query, passage))
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
