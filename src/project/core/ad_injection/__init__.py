"""
Advertisement Injection Engine — ad content, injection strategies, and factory.

Paper reference: Section 6.2 — Advertisement Injection Engine.
"""

from core.ad_injection.models import (
    Ad,
    AdRetrievalResult,
    InjectionResult,
    compact_display_payload,
    format_products_block,
    format_sponsored_chat_content,
    is_sponsored_chat_message,
    participant_display_title,
    sponsored_message_to_payload,
)
from core.ad_injection.injectors import AdInjector
from core.ad_injection.provider import get_ad, get_injector, AD_BACKEND

__all__ = [
    "Ad",
    "AdRetrievalResult",
    "InjectionResult",
    "compact_display_payload",
    "format_products_block",
    "format_sponsored_chat_content",
    "is_sponsored_chat_message",
    "participant_display_title",
    "sponsored_message_to_payload",
    "AdInjector",
    "get_ad",
    "get_injector",
]
