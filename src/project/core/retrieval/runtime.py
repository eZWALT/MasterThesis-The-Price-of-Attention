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
    from core.config import (
        HYDE_MAX_TOKENS,
        HYDE_TOKENS_PER_DOC,
        QUERY_EXPANSION_MODE,
    )
    from core.retrieval.hyde import effective_hyde_num_docs

    if getattr(params, "ctx_sum", None) is not None:
        _runtime.use_context_summary = params.ctx_sum
    if getattr(params, "query_expansion", None) is not None:
        _runtime.query_expansion_mode = params.query_expansion

    from core.retrieval.log_util import log_config_once

    mode = get_query_expansion_mode(QUERY_EXPANSION_MODE)
    log_config_once(
        mode=mode,
        hyde_docs=effective_hyde_num_docs() if mode == "hyde" else 0,
        max_tokens=HYDE_MAX_TOKENS,
        tokens_per_doc=HYDE_TOKENS_PER_DOC,
    )


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
