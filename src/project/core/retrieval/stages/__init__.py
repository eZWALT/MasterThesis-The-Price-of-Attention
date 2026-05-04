"""stages package — re-export shared types used across the pipeline."""
from core.retrieval.stages.state import PipelineState, CatalogItem, RankedCandidate
from core.retrieval.stages.base import PipelineStage

__all__ = ["PipelineState", "CatalogItem", "RankedCandidate", "PipelineStage"]
