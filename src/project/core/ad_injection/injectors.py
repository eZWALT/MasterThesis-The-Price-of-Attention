"""
Ad injection strategies.

One class per ad type in the paper's taxonomy (Section 3.2).
Each injector knows *only* how to package the ad into an InjectionResult.
Orchestration (when to inject, which ad to use) lives in the conversation
manager, not here.

Paper taxonomy:
  1. InlinePersuasive          — ad woven into the LLM's own response
  2. ExplicitAdBlock           — visually separated banner / panel (OpenAI-style)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict

from core.config import (
    INLINE_INJECTION_PROMPT,
    EXPLICIT_AD_LABEL,
)
from core.ad_injection.models import (
    AdRetrievalResult,
    compact_display_payload,
    format_products_block,
    InjectionResult,
)
from core.ad_injection.ad_links import enrich_display_payload


# ── Base ──────────────────────────────────────────────────────

class AdInjector(ABC):
    """
    Contract for all ad injection strategies.

    inject() receives ranked retrieval results and the current conversation
    history, and returns an InjectionResult that tells the conversation
    manager and UI layer what to do — without knowing anything about either.
    """

    @abstractmethod
    def inject(
        self,
        retrieval: AdRetrievalResult,
        conversation: List[Dict[str, str]],
    ) -> InjectionResult:
        ...


# ── Concrete strategies (paper taxonomy) ─────────────────────

class InlinePersuasiveInjector(AdInjector):
    """
    Ad Type 1 — Inline Persuasive Suggestion.

    Promotional content is subtly woven into the LLM's natural response
    via a system-prompt override.  The ad is never visually labelled;
    the LLM references it organically.

    All retrieved candidates are shown to the LLM; it may mention at most one.

    Intrusiveness: lowest (fully implicit).
    """

    def inject(
        self,
        retrieval: AdRetrievalResult,
        conversation: List[Dict[str, str]],
    ) -> InjectionResult:
        products_block = format_products_block(retrieval.ads)
        system_instruction = INLINE_INJECTION_PROMPT.format(
            products_block=products_block,
        )
        return InjectionResult(
            system_overrides=[{"role": "system", "content": system_instruction}]
        )


class ExplicitAdBlockInjector(AdInjector):
    """
    Ad Type 3 — Explicit Ad Block (OpenAI-style).

    A highly salient, visually separated panel is rendered beside the
    conversation with a clear call-to-action.  The LLM is told what product
    is being shown so it can sincerely discuss it if asked.

    Intrusiveness: highest (fully disclosed, unavoidable).
    """

    def inject(
        self,
        retrieval: AdRetrievalResult,
        conversation: List[Dict[str, str]],
    ) -> InjectionResult:
        from core.config import EXPLICIT_AD_LABEL

        ad = retrieval.primary
        if ad is None:
            return InjectionResult()

        # No system override at injection time — the ad is purely visual.
        # Awareness for subsequent turns is handled by the conversation
        # manager via _ad_awareness_override.
        return InjectionResult(
            display_payload=enrich_display_payload(
                ad, compact_display_payload(ad, header=EXPLICIT_AD_LABEL)
            ),
        )
