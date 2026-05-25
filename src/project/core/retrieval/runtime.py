"""
Per-session retrieval overrides (from URL query params).

Applied once at app startup before the pipeline singleton is built.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class RetrievalRuntimeConfig:
    use_context_summary: Optional[bool] = None
    query_expansion_mode: Optional[str] = None  # none | hyde | expand


_runtime = RetrievalRuntimeConfig()


def configure_from_experiment_params(params) -> None:
    """Map ExperimentParams RAG fields onto runtime overrides."""
    if getattr(params, "ctx_sum", None) is not None:
        _runtime.use_context_summary = params.ctx_sum
    if getattr(params, "query_expansion", None) is not None:
        _runtime.query_expansion_mode = params.query_expansion


def get_use_context_summary(default: bool) -> bool:
    if _runtime.use_context_summary is not None:
        return _runtime.use_context_summary
    return default


def get_query_expansion_mode(default: str) -> str:
    if _runtime.query_expansion_mode is not None:
        return _runtime.query_expansion_mode
    return default


def reset_for_tests() -> None:
    global _runtime
    _runtime = RetrievalRuntimeConfig()
