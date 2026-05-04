"""
EmbeddingModel — abstract base.

All embedding backends must implement encode().
Swap the concrete class in retrieval/embeddings/__init__.py
to change the backbone with no other code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np


class EmbeddingModel(ABC):
    """
    Contract for all embedding backends.

    encode() must return an L2-normalised (unit-norm) float32 array
    of shape (N, D) where N = len(texts) and D = embedding dimension.
    Normalised vectors allow dot-product to equal cosine similarity,
    which is what FAISS IndexFlatIP expects.
    """

    @abstractmethod
    def encode(self, texts: list[str]) -> np.ndarray:
        """
        Parameters
        ----------
        texts : list of N strings to embed.

        Returns
        -------
        np.ndarray of shape (N, D), dtype float32, L2-normalised.
        """
        ...
