"""
retrieval.rerankers — factory function.

To add a new reranker backend: create a new file in this package,
subclass RerankerModel, and add it to the registry below.
"""

from __future__ import annotations

from core.retrieval.rerankers.base import RerankerModel
from core.retrieval.rerankers.cross_encoder import CrossEncoderReranker

# Registry: backend_name → class
_REGISTRY = {
    "cross_encoder": CrossEncoderReranker,
}


def build_reranker(
    model_name: str,
    device: str = "cpu",
    backend: str = "cross_encoder",
) -> RerankerModel:
    """
    Instantiate and return a RerankerModel.

    Parameters
    ----------
    model_name : HuggingFace model id passed to the backend constructor.
    device     : target device string (e.g. "cuda:1").
    backend    : key in _REGISTRY (default "cross_encoder").
    """
    cls = _REGISTRY.get(backend)
    if cls is None:
        raise ValueError(f"Unknown reranker backend '{backend}'. "
                         f"Available: {list(_REGISTRY)}")
    return cls(model_name=model_name, device=device)


__all__ = ["RerankerModel", "CrossEncoderReranker", "build_reranker"]
