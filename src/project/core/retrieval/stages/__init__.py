"""stages package — re-export shared types used across the pipeline."""
from core.retrieval.stages.state import PipelineState, CatalogItem, RankedCandidate
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.query_preprocessor import ContextSummaryStage, QueryExpansionStage

__all__ = [
    "PipelineState",
    "CatalogItem",
    "RankedCandidate",
    "PipelineStage",
    "ContextSummaryStage",
    "QueryExpansionStage",
]
