"""
Ad injection strategies.

Each advertising mode has a dedicated AdInjector subclass that
knows *how* to modify the conversation or produce display payloads.

The injector hierarchy mirrors the paper's integration-mode taxonomy
(Section 3.2 — Ads Taxonomy).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict

from core.config import IMPLICIT_AD_SYSTEM_PROMPT
from core.ad_injection.models import Ad, InjectionResult


# ── Base ──────────────────────────────────────────────────────

class AdInjector(ABC):
    """Base class for mode-specific ad injection strategies."""

    @abstractmethod
    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        ...


# ── Concrete strategies ──────────────────────────────────────

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
                "content": IMPLICIT_AD_SYSTEM_PROMPT,
            }]
        )
