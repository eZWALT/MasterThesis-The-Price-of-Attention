"""
Ad provider and injector factory.

Public API
----------
get_ad(query, context)  — returns the Ad to inject at the current turn.
                           Routes to mock backend or the full RAG pipeline
                           depending on AD_BACKEND (env var or module flag).
get_injector(ad_mode)   — returns the AdInjector strategy for a given mode key.

Switching backends
------------------
Set the environment variable:
    AD_BACKEND=mock    (default) — instant, no GPU, static placeholder ad
    AD_BACKEND=rag               — full 5-stage retrieval pipeline

Or change the module-level AD_BACKEND constant below for dev convenience.
"""

from __future__ import annotations

import os
from typing import Dict, List

from core.config import (
    MOCK_AD_TITLE,
    MOCK_AD_TEXT,
    MOCK_AD_CTA,
    MOCK_AD_QUESTION,
)
from core.ad_injection.models import Ad
from core.ad_injection.injectors import (
    AdInjector,
    InlinePersuasiveInjector,
    SponsoredConversationalInjector,
    SponsoredRecommendationInjector,
    ExplicitAdBlockInjector,
)

# ── Backend selector ──────────────────────────────────────────
# Override with env var AD_BACKEND=rag to activate the retrieval pipeline.
AD_BACKEND: str = os.getenv("AD_BACKEND", "mock")


# ── Ad provider ───────────────────────────────────────────────

def get_ad(query: str = "", context: List[Dict] | None = None) -> Ad:
    """
    Return the Ad to inject at the current conversation turn.

    Parameters
    ----------
    query   : the user's latest message (used by the RAG backend).
    context : full conversation history (used by the RAG backend).

    Returns
    -------
    Ad dataclass populated either from the mock catalog or the
    retrieval pipeline, depending on AD_BACKEND.
    """
    if AD_BACKEND == "rag":
        return _rag_ad(query, context or [])
    return _mock_ad()


def _mock_ad() -> Ad:
    """Static placeholder ad — zero latency, no model required."""
    return Ad(
        title=MOCK_AD_TITLE,
        text=MOCK_AD_TEXT,
        cta=MOCK_AD_CTA,
        question=MOCK_AD_QUESTION,
        source_item_id="mock",
        relevance_score=0.0,
    )


def _rag_ad(query: str, context: List[Dict]) -> Ad:
    """Full 5-stage retrieval pipeline (lazy import to keep startup fast)."""
    from core.retrieval import retrieve_ad
    return retrieve_ad(query, context)


# ── Injector registry & factory ───────────────────────────────

INJECTOR_REGISTRY: Dict[str, AdInjector] = {
    "inline_persuasive":        InlinePersuasiveInjector(),
    "sponsored_conversational": SponsoredConversationalInjector(),
    "sponsored_recommendation": SponsoredRecommendationInjector(),
    "explicit_ad_block":        ExplicitAdBlockInjector(),
}


def get_injector(ad_mode: str) -> AdInjector:
    """Return the AdInjector strategy for a given ad mode key."""
    injector = INJECTOR_REGISTRY.get(ad_mode)
    if injector is None:
        raise ValueError(
            f"Unknown ad mode '{ad_mode}'. "
            f"Valid modes: {list(INJECTOR_REGISTRY)}"
        )
    return injector
