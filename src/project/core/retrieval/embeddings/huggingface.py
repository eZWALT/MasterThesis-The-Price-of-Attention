"""
HuggingFace SentenceTransformer embedding backend.

This is the default embedding model used in the retrieval pipeline.
It wraps sentence-transformers, which supports any HuggingFace model
that produces sentence embeddings (BERT, MiniLM, E5, Qwen-Embedding…).

Swap config.embedding_model_name in RetrievalConfig to change the model
with no other code changes.
"""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from core.retrieval.embeddings.base import EmbeddingModel


class HuggingFaceEmbedding(EmbeddingModel):
    """
    SentenceTransformer-backed embedding model.

    Parameters
    ----------
    model_name : any HuggingFace model id compatible with SentenceTransformer.
                 Example: "sentence-transformers/all-MiniLM-L6-v2"
                          "Qwen/Qwen3-Embedding-8B"
    device     : "cpu", "cuda:0", "cuda:1", etc.
    batch_size : how many texts to encode per forward pass.
    """

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        batch_size: int = 32,
    ) -> None:
        self._model = SentenceTransformer(model_name, device=device)
        self._batch_size = batch_size

    def encode(self, texts: list[str]) -> np.ndarray:
        """
        Returns
        -------
        np.ndarray shape (N, D), dtype float32, L2-normalised.
        """
        vectors = self._model.encode(
            texts,
            batch_size=self._batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,   # cosine via dot-product
            show_progress_bar=False,
        )
        return vectors.astype(np.float32)
