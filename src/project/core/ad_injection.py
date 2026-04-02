"""
TARA — Ad Injection Module.

Centralizes all ad content retrieval and injection logic,
independent of the presentation layer (UI).

Each advertising mode has a dedicated injector that knows *how*
to modify the conversation or produce display payloads.
Replace `get_ad()` with a RAG pipeline when ready.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from .config import IMPLICIT_SYSTEM_PROMPT


# ── Ad data ───────────────────────────────────────────────────

@dataclass
class Ad:
    """Represents a single advertisement unit."""
    title: str
    text: str
    cta: str = ""
    question: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def get_ad() -> Ad:
    """
    Mock ad provider — replace with RAG retrieval later.

    TODO: Integrate knowledge-graph-based ad retrieval so ads are
          contextually relevant to the conversation.
    """
    return Ad(
        title="MyProtein Creatine",
        text="Boost recovery with high-quality creatine designed for muscle & neural growth.",
        cta="Learn more",
        question="Do you want a creatine recommendation for your goals?",
    )


# ── Injection results ─────────────────────────────────────────

@dataclass
class InjectionResult:
    """What the injector wants the UI / conversation manager to do."""
    messages_to_append: List[Dict[str, str]] = field(default_factory=list)
    system_overrides: List[Dict[str, str]] = field(default_factory=list)
    display_payload: Optional[Dict[str, Any]] = None
    suggestions: List[str] = field(default_factory=list)


# ── Base injector ─────────────────────────────────────────────

class AdInjector(ABC):
    """Base class for mode-specific ad injection strategies."""

    @abstractmethod
    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        ...


# ── Mode-specific injectors ──────────────────────────────────

class ClassicalUIInjector(AdInjector):
    """Ads displayed outside the conversation (banner / side panel)."""

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        return InjectionResult(
            display_payload={
                "header": "💰 Sponsored",
                "title": ad.title,
                "text": ad.text,
                "cta": ad.cta,
            }
        )


class InChatInjector(AdInjector):
    """Ads inserted as clearly-labelled sponsored messages."""

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        return InjectionResult(
            messages_to_append=[{
                "role": "assistant",
                "content": f"💡 **Sponsored**: {ad.text}",
            }]
        )


class SuggestionInjector(AdInjector):
    """Ads appear as suggested follow-up questions."""

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        return InjectionResult(suggestions=[ad.question])


class AdjacentInjector(AdInjector):
    """Ads shown in a panel beside the LLM response."""

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        return InjectionResult(
            display_payload={
                "header": "💡 Sponsored",
                "title": ad.title,
                "text": ad.text,
                "cta": ad.cta,
            }
        )


class ImplicitInjector(AdInjector):
    """Ads embedded into the LLM's response via system prompt manipulation."""

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        return InjectionResult(
            system_overrides=[{
                "role": "system",
                "content": IMPLICIT_SYSTEM_PROMPT,
            }]
        )


# ── Factory ───────────────────────────────────────────────────

INJECTOR_REGISTRY: Dict[str, AdInjector] = {
    "1_classical_ui": ClassicalUIInjector(),
    "2_in_chat": InChatInjector(),
    "3_suggestions": SuggestionInjector(),
    "4_adjacent": AdjacentInjector(),
    "5_implicit": ImplicitInjector(),
}


def get_injector(ad_mode: str) -> AdInjector:
    """Return the injector for a given ad mode."""
    injector = INJECTOR_REGISTRY.get(ad_mode)
    if injector is None:
        raise ValueError(f"Unknown ad mode '{ad_mode}'")
    return injector
