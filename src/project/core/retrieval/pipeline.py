"""
Ad Retrieval Pipeline.

Composes the 5 stages in sequence.  This file reads like pseudocode:
  state → intent → dense → hybrid → rerank → format → Ad

Callers never instantiate stages directly; they use the pipeline.
The pipeline is built once (at module load or on first call) and reused
across all ad injection events.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from core.retrieval.catalog import AdCatalog
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState
from core.retrieval.stages.intent import IntentClassifier
from core.retrieval.stages.dense import DenseRetriever
from core.retrieval.stages.hybrid import HybridRefiner
from core.retrieval.stages.reranker import Reranker
from core.retrieval.stages.formatter import AdFormatter
from core.ad_injection.models import AdRetrievalResult


def build_default_stages(catalog, embedding_model=None) -> list:
    """Compose pipeline stages from config + per-session runtime overrides."""
    from core.config import QUERY_EXPANSION_MODE, USE_CONTEXT_SUMMARY, USE_RERANKER
    from core.retrieval.runtime import get_query_expansion_mode, get_use_context_summary
    from core.retrieval.stages.query_preprocessor import (
        ContextSummaryStage,
        QueryExpansionStage,
    )

    stages: list = []

    if get_use_context_summary(USE_CONTEXT_SUMMARY):
        stages.append(ContextSummaryStage())

    qe_mode = get_query_expansion_mode(QUERY_EXPANSION_MODE)
    if qe_mode != "none":
        stages.append(QueryExpansionStage(mode=qe_mode))

    stages.extend([
        IntentClassifier(),
        DenseRetriever(catalog, embedding_model=embedding_model),
        HybridRefiner(),
    ])
    if USE_RERANKER:
        stages.append(Reranker())
    stages.append(AdFormatter())
    return stages


def _build_retrieval_diag(state: PipelineState) -> Dict[str, Any]:
    """Compact diagnostics for experiment logs (no full HyDE text)."""
    from core.config import QUERY_EXPANSION_MODE
    from core.retrieval.runtime import get_query_expansion_mode

    qe_mode = get_query_expansion_mode(QUERY_EXPANSION_MODE)
    hyde_ms = state.stage_ms.get("QueryExpansionStage", 0.0)
    ctx_ms = state.stage_ms.get("ContextSummaryStage", 0.0)
    total_ms = sum(state.stage_ms.values())
    return {
        "query_expansion_mode": qe_mode,
        "query_expansion_ms": round(hyde_ms, 1) if hyde_ms else None,
        "context_summary_ms": round(ctx_ms, 1) if ctx_ms else None,
        "hyde_used": bool(state.hyde_documents or state.expanded_query),
        "hyde_doc_count": len(state.hyde_documents),
        "hyde_documents": list(state.hyde_documents),
        "retrieval_query": state.query,
        "query_chars": len(state.query),
        "hyde_chars": len(state.expanded_query) if state.expanded_query else 0,
        "retrieval_stage_ms": {k: round(v, 1) for k, v in state.stage_ms.items()},
        "retrieval_total_ms": round(total_ms, 1),
    }


class AdRetrievalPipeline:
    """
    Ad retrieval pipeline.

    Stages (default)
    ----------------
    0a. ContextSummaryStage  — optional; compress history → context_summary
    0b. QueryExpansionStage  — optional; HyDE / expand query → expanded_query
    1.  IntentClassifier     — infers conversational intent (CPU, BERT)
    2.  DenseRetriever       — ANN search over FAISS index (GPU 1)
    3.  HybridRefiner        — BM25 + metadata filter + RRF (CPU, optional)
    4.  Reranker             — cross-encoder precision pass (GPU 1)
    5.  AdFormatter          — top-N candidates → Ad dataclasses
    6.  SummarizationStage   — optional; rewrite ad text → concise sentence
    """

    def __init__(
        self,
        catalog: AdCatalog,
        embedding_model=None,
        stages: Optional[List[PipelineStage]] = None,
    ) -> None:
        if stages is not None:
            self._stages = stages
        else:
            self._stages = build_default_stages(catalog, embedding_model)
        self.last_state: Optional[PipelineState] = None

    def run(self, query: str, context: List[Dict[str, str]]) -> AdRetrievalResult | None:
        """
        Execute all stages in order and return ranked ads.

        Returns None if the pipeline produces no candidates
        (caller should fall back to mock ad).
        """
        from core.log import logger
        from core.retrieval.query_text import build_retrieval_query

        state = PipelineState(query=query, context=context)
        effective_query = build_retrieval_query(query, context)
        if effective_query != query:
            logger.debug(
                "Retrieval query expanded from {} chars → {} chars (context-aware)",
                len(query),
                len(effective_query),
            )
        state.query = effective_query

        from core.retrieval.log_util import (
            elapsed_ms,
            log_hyde_documents,
            log_run_total,
            log_stage_latency,
        )

        run_t0 = time.perf_counter()
        for stage in self._stages:
            name = stage.__class__.__name__
            t0 = time.perf_counter()
            state = stage.run(state)
            ms = elapsed_ms(t0)
            state.stage_ms[name] = ms
            log_stage_latency(name, ms, state, query=query)
            if state.candidates:
                logger.debug(
                    "After {}: {} candidates",
                    name,
                    len(state.candidates),
                )
            if state.ranked:
                logger.debug(
                    "After {}: {} ranked",
                    name,
                    len(state.ranked),
                )

        wall_ms = elapsed_ms(run_t0)
        self.last_state = state
        log_hyde_documents(state, query=query)
        log_run_total(wall_ms=wall_ms, query=query)

        if not state.top_ads:
            return None
        return AdRetrievalResult(
            ads=list(state.top_ads),
            diag=_build_retrieval_diag(state),
        )
