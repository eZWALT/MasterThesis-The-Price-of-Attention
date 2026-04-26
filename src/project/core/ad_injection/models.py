"""
Ad Injection data models.

Pure dataclasses with no business logic — shared by injectors,
the conversation manager, and the UI layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class Ad:
    """Represents a single advertisement unit."""
    title: str
    text: str
    cta: str = ""
    question: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjectionResult:
    """
    What the injector wants the conversation manager / UI to do.

    Fields
    ------
    messages_to_append : chat messages to insert after the assistant reply.
    system_overrides   : extra system messages prepended before the LLM call.
    display_payload    : dict consumed by the UI for rendering ad panels.
    suggestions        : follow-up prompt buttons shown to the participant.
    """
    messages_to_append: List[Dict[str, str]] = field(default_factory=list)
    system_overrides: List[Dict[str, str]] = field(default_factory=list)
    display_payload: Optional[Dict[str, Any]] = None
    suggestions: List[str] = field(default_factory=list)
