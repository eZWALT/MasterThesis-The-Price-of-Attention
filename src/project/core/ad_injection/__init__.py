"""
Advertisement Injection Engine — ad content, injection strategies, and factory.

Paper reference: Section 6.2 — Advertisement Injection Engine.
"""

from core.ad_injection.models import Ad, InjectionResult
from core.ad_injection.injectors import AdInjector
from core.ad_injection.provider import get_ad, get_injector, AD_BACKEND

__all__ = [
    "Ad",
    "InjectionResult",
    "AdInjector",
    "get_ad",
    "get_injector",
]
