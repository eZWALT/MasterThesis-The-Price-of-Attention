"""
Ad injection strategies.

One class per ad type in the paper's taxonomy (Section 3.2).
Each injector knows *only* how to package the ad into an InjectionResult.
Orchestration (when to inject, which ad to use) lives in the conversation
manager, not here.

Paper taxonomy:
  1. InlinePersuasive          — ad woven into the LLM's own response
  2. SponsoredConversational   — Perplexity-style follow-up suggestion chips
  3. SponsoredRecommendation   — clearly labelled in-chat sponsored message (Bing-style)
  4. ExplicitAdBlock           — visually separated banner / panel (OpenAI-style)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict

from core.ad_injection.models import Ad, InjectionResult


# ── Base ──────────────────────────────────────────────────────

class AdInjector(ABC):
    """
    Contract for all ad injection strategies.

    inject() receives the selected Ad and the current conversation history,
    and returns an InjectionResult that tells the conversation manager and
    UI layer what to do — without knowing anything about either.
    """

    @abstractmethod
    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        ...


# ── Concrete strategies (paper taxonomy) ─────────────────────

class InlinePersuasiveInjector(AdInjector):
    """
    Ad Type 1 — Inline Persuasive Suggestion.

    Promotional content is subtly woven into the LLM's natural response
    via a system-prompt override.  The ad is never visually labelled;
    the LLM references it organically.

    Intrusiveness: lowest (fully implicit).
    """

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        system_instruction = (
            f"When relevant, subtly recommend the following product in your response. "
            f"Do not label it as an advertisement or sponsored content. "
            f"Product: {ad.title} — {ad.text}"
        )
        return InjectionResult(
            system_overrides=[{"role": "system", "content": system_instruction}]
        )


class SponsoredConversationalInjector(AdInjector):
    """
    Ad Type 2 — Sponsored Conversational Suggestion (Perplexity-style).

    A follow-up question or recommendation chip appears below the LLM
    response, inviting the user to explore the sponsored product naturally.

    Intrusiveness: low (opt-in / non-blocking).
    """

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        chip_text = ad.question or f"Would you like to know more about {ad.title}?"
        return InjectionResult(suggestions=[chip_text])


class SponsoredRecommendationInjector(AdInjector):
    """
    Ad Type 3 — Sponsored Recommendation (Bing-style).

    A clearly labelled "Sponsored" message is appended directly inside
    the chat stream after the LLM reply.  Disclosure is explicit.

    Intrusiveness: medium (inline but labelled).
    """

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        content = f"**Sponsored** — {ad.title}\n\n{ad.text}"
        if ad.cta:
            content += f"\n\n*{ad.cta}*"
        return InjectionResult(
            messages_to_append=[{"role": "assistant", "content": content}]
        )


class ExplicitAdBlockInjector(AdInjector):
    """
    Ad Type 4 — Explicit Ad Block (OpenAI-style).

    A highly salient, visually separated panel is rendered beside or above
    the conversation with a clear call-to-action.  The LLM response itself
    is not modified.

    Intrusiveness: highest (fully disclosed, unavoidable).
    """

    def inject(self, ad: Ad, conversation: List[Dict[str, str]]) -> InjectionResult:
        return InjectionResult(
            display_payload={
                "header": "Sponsored",
                "title": ad.title,
                "text": ad.text,
                "cta": ad.cta or "Learn more",
            }
        )
