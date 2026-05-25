"""
Ad Injection data models.

Pure dataclasses — no business logic.
Shared by injectors, the conversation manager, and the UI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from core.config import DEFAULT_AD_CTA, PARTICIPANT_AD_TITLE_MAX_LEN, SPONSORED_LABEL


@dataclass
class AdRetrievalResult:
    """
    Ranked product candidates returned by the retrieval pipeline.

    ads[0] is the top-ranked item (used for UI panels and logging).
    All ads are passed to inline_persuasive so the LLM can pick at most one.
    """
    ads: List[Ad] = field(default_factory=list)
    # Optional timing / HyDE diagnostics from the retrieval pipeline (for logs & export).
    diag: Dict[str, Any] = field(default_factory=dict)

    @property
    def primary(self) -> Optional[Ad]:
        return self.ads[0] if self.ads else None

    @property
    def has_ads(self) -> bool:
        return bool(self.ads)


def participant_display_title(
    ad: "Ad",
    max_len: int = PARTICIPANT_AD_TITLE_MAX_LEN,
) -> str:
    """Short headline for UI/chat — never uses catalog body text."""
    title = " ".join((ad.title or "").split())
    if len(title) <= max_len:
        return title
    return title[: max_len - 1].rstrip() + "…"


def compact_display_payload(ad: "Ad", header: str | None = None) -> Dict[str, str]:
    """UI banner fields: label, title, CTA only (no catalog description)."""
    return {
        "header": header or SPONSORED_LABEL,
        "title": participant_display_title(ad),
        "cta": ad.cta or DEFAULT_AD_CTA,
    }


def format_products_block(ads: List["Ad"]) -> str:
    """Compact candidate list for the LLM (title + optional CTA, no body text)."""
    blocks: List[str] = []
    for i, ad in enumerate(ads, start=1):
        line = f"{i}. **{participant_display_title(ad)}**"
        if ad.cta:
            line += f" — {ad.cta}"
        blocks.append(line)
    return "\n\n".join(blocks)


def format_sponsored_chat_content(ad: "Ad", label: str | None = None) -> str:
    """In-chat sponsored line: title and CTA only (never ad.text)."""
    headline = f"**{label or SPONSORED_LABEL}** — {participant_display_title(ad)}"
    cta = (ad.cta or DEFAULT_AD_CTA).strip()
    if cta:
        return f"{headline}\n\n*{cta}*"
    return headline


def is_sponsored_chat_message(content: str) -> bool:
    """True if message content is a labelled sponsored ad (any format generation)."""
    return content.strip().startswith(f"**{SPONSORED_LABEL}**")


def sponsored_message_to_payload(content: str) -> Dict[str, str] | None:
    """
    Parse a sponsored chat line into a compact banner payload.

    Drops legacy middle paragraphs (old format appended ad.text between title and CTA).
    """
    if not is_sponsored_chat_message(content):
        return None

    headline, *rest = [p.strip() for p in content.split("\n\n") if p.strip()]
    prefix = f"**{SPONSORED_LABEL}** — "
    if not headline.startswith(prefix):
        return None

    title = headline[len(prefix) :].strip()
    cta = DEFAULT_AD_CTA
    for part in reversed(rest):
        if part.startswith("*") and part.endswith("*"):
            cta = part.strip("*").strip() or cta
            break

    if len(title) > PARTICIPANT_AD_TITLE_MAX_LEN:
        title = participant_display_title(Ad(title=title, text=""))

    return {
        "header": SPONSORED_LABEL,
        "title": title,
        "cta": cta,
    }


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
