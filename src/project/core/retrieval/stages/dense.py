"""
Stage 2 — Dense Retriever.

Reads  : state.query
Writes : state.candidates  (top-k CatalogItems from ANN search)

Model  : HuggingFace embedding model (GPU 1).
Index  : FAISS HNSW / IVF, loaded from disk into RAM on first call.
         Swap embedding_model_name in RetrievalConfig to change the
         encoder with no other code changes.

Design note (thesis):
  We intentionally avoid learned ranking models to prevent confounding
  effects from ranking policies.  Dense retrieval maximises recall;
  precision is handled by the reranker in Stage 4.
"""

from __future__ import annotations

import numpy as np

from core.config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE, DENSE_TOP_K
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState, CatalogItem


class DenseRetriever(PipelineStage):
    """
    Encodes the query and performs ANN search over the FAISS index.

    Config keys (core.config)
    -------------------------
    EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE, DENSE_TOP_K

    Parameters
    ----------
    catalog : AdCatalog instance (passed in by the pipeline so it is
              shared and not reloaded per stage).

    Output
    ------
    state.candidates : list of CatalogItem, length <= DENSE_TOP_K.
    """

    def __init__(self, catalog, embedding_model=None) -> None:
        if embedding_model is not None:
            self._embed = embedding_model
        else:
            from core.retrieval.embeddings import build_embedding_model
            self._embed = build_embedding_model(
                model_name=EMBEDDING_MODEL_NAME,
                device=EMBEDDING_DEVICE,
            )
        self._catalog = catalog
        self._top_k = DENSE_TOP_K

    # ── PipelineStage interface ──────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        import time
        from core.log import logger
        t0 = time.time()
        embed_text = state.expanded_query or state.query
        query_vec: np.ndarray = self._embed.encode([embed_text])    # (1, D)
        item_ids = self._catalog.search(query_vec, top_k=self._top_k)
        state.candidates = [self._catalog.get(item_id) for item_id in item_ids]
        elapsed = (time.time() - t0) * 1000
        logger.info(f"[LATENCY] DenseRetriever: {elapsed:.1f} ms")
        return state
