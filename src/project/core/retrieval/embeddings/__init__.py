"""
retrieval.embeddings — factory function.

Importing from here is the only thing stages/dense.py needs to do.
To add a new embedding backend: create a new file in this package,
subclass EmbeddingModel, and add it to the registry below.
"""

from __future__ import annotations

from core.retrieval.embeddings.base import EmbeddingModel
from core.retrieval.embeddings.huggingface import HuggingFaceEmbedding

# Registry: backend_name → class
_REGISTRY = {
    "huggingface": HuggingFaceEmbedding,
}


def build_embedding_model(
    model_name: str,
    device: str = "cpu",
    batch_size: int | None = None,
    dtype: str | None = None,
    backend: str = "huggingface",
) -> EmbeddingModel:
    """
    Instantiate and return an EmbeddingModel.

    Parameters
    ----------
    model_name : HuggingFace model id passed to the backend constructor.
    device     : target device string (e.g. "cuda:1").
    batch_size : forward-pass batch size; defaults to config.EMBEDDING_BATCH_SIZE.
    dtype      : "bfloat16", "float16", or "float32"; defaults to config.EMBEDDING_DTYPE.
    backend    : key in _REGISTRY (default "huggingface").
    """
    from core.config import EMBEDDING_BATCH_SIZE, EMBEDDING_DTYPE

    cls = _REGISTRY.get(backend)
    if cls is None:
        raise ValueError(f"Unknown embedding backend '{backend}'. "
                         f"Available: {list(_REGISTRY)}")
    return cls(
        model_name=model_name,
        device=device,
        batch_size=batch_size if batch_size is not None else EMBEDDING_BATCH_SIZE,
        dtype=dtype if dtype is not None else EMBEDDING_DTYPE,
    )


__all__ = ["EmbeddingModel", "HuggingFaceEmbedding", "build_embedding_model"]
