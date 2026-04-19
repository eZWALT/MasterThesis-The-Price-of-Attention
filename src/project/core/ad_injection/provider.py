"""
TARA — Ad provider & injector factory.

`get_ad()`       — returns the current ad unit (mock for now; will be
                   replaced by a RAG pipeline).
`get_injector()` — returns the AdInjector for a given ad mode key.
"""

from __future__ import annotations

from typing import Dict

from core.config import (
    MOCK_AD_TITLE,
    MOCK_AD_TEXT,
    MOCK_AD_CTA,
    MOCK_AD_QUESTION,
)
from core.ad_injection.models import Ad
from core.ad_injection.injectors import (
    AdInjector,
    ClassicalUIInjector,
    InChatInjector,
    SuggestionInjector,
    AdjacentInjector,
    ImplicitInjector,
)


# ── Mock ad provider ──────────────────────────────────────────

def get_ad() -> Ad:
    """
    Return the current advertisement unit.

    TODO: Replace with RAG-based contextual ad retrieval.
    """
    return Ad(
        title=MOCK_AD_TITLE,
        text=MOCK_AD_TEXT,
        cta=MOCK_AD_CTA,
        question=MOCK_AD_QUESTION,
    )


# ── Injector registry & factory ───────────────────────────────

INJECTOR_REGISTRY: Dict[str, AdInjector] = {
    "1_classical_ui": ClassicalUIInjector(),
    "2_in_chat": InChatInjector(),
    "3_suggestions": SuggestionInjector(),
    "4_adjacent": AdjacentInjector(),
    "5_implicit": ImplicitInjector(),
}


def get_injector(ad_mode: str) -> AdInjector:
    """Return the injector for a given ad mode key."""
    injector = INJECTOR_REGISTRY.get(ad_mode)
    if injector is None:
        raise ValueError(f"Unknown ad mode '{ad_mode}'")
    return injector
