"""
Retrieval pipeline — shared state object.

PipelineState is the single data envelope that flows through every stage.
Stages read what they need and write what they produce.  Nothing else is
passed between stages.

CatalogItem is the raw representation of a product in the corpus.
RankedCandidate wraps a CatalogItem with a retrieval / reranking score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ── Catalog ───────────────────────────────────────────────────────────────

@dataclass
class CatalogItem:
    """
    A single product / ad unit from the corpus.

    Fields
    ------
    item_id  : unique identifier (used for logging and deduplication).
    title    : short display headline.
    text     : full-text description used for embedding and reranking.
    category : optional product category for metadata filtering.
    price    : optional price for metadata filtering.
    metadata : arbitrary extra fields from the catalog JSON.
    """
    item_id: str
    title: str
    text: str
    category: str = ""
    price: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# ── Ranking ───────────────────────────────────────────────────────────────

@dataclass
class RankedCandidate:
    """A CatalogItem paired with its retrieval or reranking score."""
    item: CatalogItem
    score: float


# ── Pipeline state ────────────────────────────────────────────────────────

@dataclass
class PipelineState:
    """
    The shared envelope passed through every stage of the pipeline.

    Populated incrementally:
      Stage 0 (input)  : query, context
      Stage 1 (intent) : intent
      Stage 2 (dense)  : candidates
      Stage 3 (hybrid) : candidates (refined / re-scored)
      Stage 4 (rerank) : ranked
      Stage 5 (format) : top_ad
    """
    # ── Input ─────────────────────────────────────────
    query: str
    context: List[Dict[str, str]] = field(default_factory=list)

    # ── Stage 1 output ────────────────────────────────
    intent: str = ""

    # ── Stage 2 / 3 output ────────────────────────────
    candidates: List[CatalogItem] = field(default_factory=list)

    # ── Stage 4 output ────────────────────────────────
    ranked: List[RankedCandidate] = field(default_factory=list)

    # ── Stage 5 output ────────────────────────────────
    # Imported lazily to avoid a circular reference at module load time.
    top_ad: Optional[Any] = None   # type: Ad (core.ad_injection.models)
