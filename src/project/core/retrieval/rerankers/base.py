"""
Reranker — abstract base.

All reranker backends must implement rerank().
Swap the concrete class in retrieval/rerankers/__init__.py
to change the backbone with no other code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from core.retrieval.stages.state import CatalogItem, RankedCandidate


class RerankerModel(ABC):
    """
    Contract for all reranker backends.

    rerank() takes a query and a list of candidates and returns the
    same candidates sorted by relevance score (descending).
    """

    @abstractmethod
    def rerank(self, query: str, candidates: List[CatalogItem]) -> List[RankedCandidate]:
        """
        Parameters
        ----------
        query      : the user's current query string.
        candidates : list of CatalogItem returned by Stage 2/3.

        Returns
        -------
        List of RankedCandidate, sorted descending by score.
        """
        ...
