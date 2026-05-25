"""
Ad Injection data models.

Pure dataclasses — no business logic.
Shared by injectors, the conversation manager, and the UI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from core.config import DEFAULT_AD_CTA, SPONSORED_LABEL


@dataclass
class AdRetrievalResult:
    """
    Ranked product candidates returned by the retrieval pipeline.

    ads[0] is the top-ranked item (used for UI panels and logging).
    All ads are passed to inline_persuasive so the LLM can pick at most one.
    """
    ads: List[Ad] = field(default_factory=list)

    @property
    def primary(self) -> Optional[Ad]:
        return self.ads[0] if self.ads else None

    @property
    def has_ads(self) -> bool:
        return bool(self.ads)


def compact_display_payload(ad: "Ad", header: str | None = None) -> Dict[str, str]:
    """UI banner fields: label, title, CTA only (no catalog description)."""
    return {
        "header": header or SPONSORED_LABEL,
        "title": ad.title,
        "cta": ad.cta or DEFAULT_AD_CTA,
    }


def format_products_block(ads: List["Ad"]) -> str:
    """Compact candidate list for the LLM (title + optional CTA, no body text)."""
    blocks: List[str] = []
    for i, ad in enumerate(ads, start=1):
        line = f"{i}. **{ad.title}**"
        if ad.cta:
            line += f" — {ad.cta}"
        blocks.append(line)
    return "\n\n".join(blocks)


def format_sponsored_chat_content(ad: "Ad", label: str | None = None) -> str:
    """In-chat sponsored line: title and CTA only."""
    headline = f"**{label or SPONSORED_LABEL}** — {ad.title}"
    if ad.cta:
        return f"{headline}\n\n*{ad.cta}*"
    return headline


@dataclass
class Ad:
    """
    Represents a single advertisement unit.

    Fields
    ------
    title          : display headline.
    text           : body copy shown to the user or injected into the LLM.
    cta            : call-to-action label (e.g. "Learn more").
    question       : follow-up suggestion text (used by SponsoredConversational).
    source_item_id : catalog item id from which this ad was retrieved.
    relevance_score: retrieval / reranking score (0.0 for mock ads).
    metadata       : arbitrary key-value pairs from the catalog item.
    """
    title: str
    text: str
    cta: str = ""
    question: str = ""
    source_item_id: str = "mock"
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjectionResult:
    """
    Describes what the injector wants the conversation manager / UI to do.

    Fields
    ------
    messages_to_append : chat messages inserted after the LLM reply.
    system_overrides   : system messages prepended before the LLM call.
    display_payload    : consumed by the UI to render ad panels / banners.
    suggestions        : follow-up prompt buttons shown to the participant.
    """
    messages_to_append: List[Dict[str, str]] = field(default_factory=list)
    system_overrides: List[Dict[str, str]] = field(default_factory=list)
    display_payload: Optional[Dict[str, Any]] = None
    suggestions: List[str] = field(default_factory=list)
