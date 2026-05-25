"""
Retrieval logging and stage timing.

[LATENCY] is only used for measured pipeline stages (ms).
Lifecycle/config lines use the ``retrieval |`` prefix instead.
"""

from __future__ import annotations

import time
from typing import Iterable, List, Optional

from core.log import logger
from core.retrieval.stages.state import PipelineState

STAGE_SHORT: dict[str, str] = {
    "ContextSummaryStage": "ctx",
    "QueryExpansionStage": "hyde",
    "IntentClassifier": "intent",
    "DenseRetriever": "dense",
    "HybridRefiner": "hybrid",
    "Reranker": "rerank",
    "AdFormatter": "format",
}

WARMUP_QUERY = "warmup"

_config_logged: Optional[str] = None


def short_stage_chain(stage_names: Iterable[str]) -> str:
    return ">".join(STAGE_SHORT.get(n, n.lower()) for n in stage_names)


def is_warmup_query(query: str) -> bool:
    return (query or "").strip().lower() == WARMUP_QUERY


def elapsed_ms(t0: float) -> float:
    return (time.perf_counter() - t0) * 1000.0


def _hyde_knobs_suffix(state: PipelineState) -> str:
    from core.config import HYDE_MAX_TOKENS, HYDE_TOKENS_PER_DOC
    from core.retrieval.hyde import effective_hyde_num_docs

    n_cfg = effective_hyde_num_docs()
    n_out = len(state.hyde_documents)
    docs = f"hyde×{n_out}" if n_out else f"hyde×{n_cfg}?"
    return f"{docs} n={n_cfg} max={HYDE_MAX_TOKENS} doc={HYDE_TOKENS_PER_DOC}"


def _latency_suffix(stage_name: str, state: PipelineState) -> str:
    if stage_name == "QueryExpansionStage":
        if state.hyde_documents or state.expanded_query:
            return _hyde_knobs_suffix(state)
        return ""
    if stage_name == "ContextSummaryStage" and state.context_summary:
        return f"{len(state.context)} turns"
    if stage_name == "DenseRetriever":
        if state.hyde_documents:
            return f"embed=hyde×{len(state.hyde_documents)}"
        if state.expanded_query:
            return "embed=hyde×1"
        return "embed=raw"
    if stage_name == "AdFormatter" and state.top_ads:
        return f"{len(state.top_ads)} ads"
    return ""


def log_stage_latency(
    stage_name: str,
    ms: float,
    state: PipelineState,
    *,
    query: str,
) -> None:
    """
    Per-stage timing only::

        [LATENCY] QueryExpansionStage: 3781.9 ms hyde×4 n=4 max=512 doc=100
        [LATENCY] DenseRetriever: 783.8 ms embed=hyde×4
    """
    if is_warmup_query(query):
        logger.debug("[LATENCY] {}: {:.1f} ms (warmup)", stage_name, ms)
        return

    suffix = _latency_suffix(stage_name, state)
    if suffix and suffix.endswith(" ads"):
        logger.info("[LATENCY] {}: {:.1f} ms ({})", stage_name, ms, suffix)
    elif suffix:
        logger.info("[LATENCY] {}: {:.1f} ms {}", stage_name, ms, suffix)
    else:
        logger.info("[LATENCY] {}: {:.1f} ms", stage_name, ms)


def log_retrieval(message: str, *args) -> None:
    """Lifecycle / config — not a latency measurement."""
    logger.info("retrieval | " + message, *args)


def log_pipeline_building() -> None:
    log_retrieval("building pipeline (first load)…")


def log_pipeline_ready(*, n_items: int, stage_names: List[str]) -> None:
    log_retrieval(
        "pipeline ready — {} items | {}",
        n_items,
        short_stage_chain(stage_names),
    )


def log_config_once(
    *,
    mode: str,
    hyde_docs: int = 0,
    max_tokens: int = 0,
    tokens_per_doc: int = 0,
) -> None:
    global _config_logged
    key = f"{mode}:{hyde_docs}:{max_tokens}:{tokens_per_doc}"
    if _config_logged == key:
        return
    _config_logged = key
    if mode == "hyde":
        log_retrieval(
            "hyde enabled n={} max={} doc={} (?qe=none to disable)",
            hyde_docs,
            max_tokens,
            tokens_per_doc,
        )
    elif mode != "none":
        log_retrieval("query expansion mode={}", mode)


def reset_config_log_for_tests() -> None:
    global _config_logged
    _config_logged = None


def log_run_total(*, wall_ms: float, query: str) -> None:
    if is_warmup_query(query):
        logger.debug("retrieval | warmup {:.1f} ms", wall_ms)
    else:
        logger.debug("retrieval | run total {:.1f} ms", wall_ms)
