"""
Ad Retrieval Pipeline.

Composes the 5 stages in sequence.  This file reads like pseudocode:
  state → intent → dense → hybrid → rerank → format → Ad

Callers never instantiate stages directly; they use the pipeline.
The pipeline is built once (at module load or on first call) and reused
across all ad injection events.
"""

from __future__ import annotations

from typing import Dict, List, Optional

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

        for stage in self._stages:
            state = stage.run(state)
            if state.candidates:
                logger.debug(
                    "After {}: {} candidates",
                    stage.__class__.__name__,
                    len(state.candidates),
                )
            if state.ranked:
                logger.debug(
                    "After {}: {} ranked",
                    stage.__class__.__name__,
                    len(state.ranked),
                )

        self.last_state = state
        if not state.top_ads:
            return None
        return AdRetrievalResult(ads=list(state.top_ads))
