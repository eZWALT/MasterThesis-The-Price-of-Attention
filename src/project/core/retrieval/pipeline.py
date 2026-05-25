"""
Ad Retrieval Pipeline.

Composes the 5 stages in sequence.  This file reads like pseudocode:
  state → intent → dense → hybrid → rerank → format → Ad

Callers never instantiate stages directly; they use the pipeline.
The pipeline is built once (at module load or on first call) and reused
across all ad injection events.

Extensibility
-------------
Pass a custom ``stages`` list to swap / add / remove any stage without
touching this file::

    pipeline = AdRetrievalPipeline(
        catalog=catalog,
        stages=[IntentClassifier(), DenseRetriever(catalog, embed), AdFormatter()],
    )
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


class AdRetrievalPipeline:
    """
    5-stage ad retrieval pipeline.

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

    All configuration is read from core.config unless overridden via
    constructor arguments.

    Parameters
    ----------
    catalog         : pre-built AdCatalog (shared across requests).
    embedding_model : optional pre-built EmbeddingModel passed through
                      to DenseRetriever so the model is not loaded twice
                      (the same instance is used for catalog indexing).
    stages          : optional list of PipelineStage instances that
                      replaces the default 5-stage sequence.  Useful for
                      testing, ablations, or adding custom stages.
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
            from core.config import USE_RERANKER
            stages = [
                IntentClassifier(),
                DenseRetriever(catalog, embedding_model=embedding_model),
                HybridRefiner(),
            ]
            if USE_RERANKER:
                stages.append(Reranker())
            stages.append(AdFormatter())
            self._stages = stages
        self.last_state: Optional[PipelineState] = None

    def run(self, query: str, context: List[Dict[str, str]]) -> AdRetrievalResult | None:
        """
        Execute all stages in order and return ranked ads.

        Returns None if the pipeline produces no candidates
        (caller should fall back to mock ad).
        """
        from core.log import logger
        state = PipelineState(query=query, context=context)

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
