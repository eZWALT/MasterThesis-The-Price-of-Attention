"""
HuggingFace SentenceTransformer embedding backend.

This is the default embedding model used in the retrieval pipeline.
It wraps sentence-transformers, which supports any HuggingFace model
that produces sentence embeddings (BERT, MiniLM, E5, Qwen-Embedding…).

Swap config.embedding_model_name in RetrievalConfig to change the model
with no other code changes.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from core.retrieval.embeddings.base import EmbeddingModel

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


class HuggingFaceEmbedding(EmbeddingModel):
    """
    SentenceTransformer-backed embedding model.

    Parameters
    ----------
    model_name : any HuggingFace model id compatible with SentenceTransformer.
                 Example: "sentence-transformers/all-MiniLM-L6-v2"
                          "Qwen/Qwen3-Embedding-0.6B"
    device     : "cpu", "cuda:0", "cuda:1", etc.
    batch_size : how many texts to encode per forward pass.
    dtype      : "bfloat16", "float16", or "float32". Half precision halves VRAM.
    """

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
        batch_size: int = 32,
        dtype: Optional[str] = None,
    ) -> None:
        model_kwargs = {}
        if dtype and dtype in _DTYPE_MAP:
            model_kwargs["dtype"] = _DTYPE_MAP[dtype]
            _log.info("[Embedding] Loading %s on %s with dtype=%s", model_name, device, dtype)
        else:
            _log.info("[Embedding] Loading %s on %s with default dtype (FP32)", model_name, device)

        self._model = SentenceTransformer(
            model_name,
            device=device,
            model_kwargs=model_kwargs,
        )
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
