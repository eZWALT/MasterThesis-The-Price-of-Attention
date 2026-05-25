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
from core.retrieval.hyde import rrf_merge_item_ids
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
        if state.hyde_documents:
            embed_texts = state.hyde_documents
            embed_src = f"hyde×{len(embed_texts)}"
        elif state.expanded_query:
            embed_texts = [state.expanded_query]
        else:
            embed_texts = [state.query]

        if len(embed_texts) == 1:
            query_vec: np.ndarray = self._embed.encode(embed_texts)
            item_ids = self._catalog.search(query_vec, top_k=self._top_k)
        else:
            query_vecs: np.ndarray = self._embed.encode(embed_texts)
            hit_lists = [
                self._catalog.search(query_vecs[i : i + 1], top_k=self._top_k)
                for i in range(len(embed_texts))
            ]
            item_ids = rrf_merge_item_ids(hit_lists)[: self._top_k]

        state.candidates = [self._catalog.get(item_id) for item_id in item_ids]
        return state
