"""
Ad Injection data models.

Pure dataclasses — no business logic.
Shared by injectors, the conversation manager, and the UI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


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
