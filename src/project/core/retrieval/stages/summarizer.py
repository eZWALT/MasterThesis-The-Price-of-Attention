"""
Stage 6 (optional) — LLM-based Ad Summarizer.

Reads  : state.top_ad (Ad dataclass)
Writes : state.top_ad.text (replaces the raw catalog text with a
         concise, injection-ready sentence)

This stage is a no-op when USE_SUMMARIZATION is False (the default).
Enable it by setting the env var SUMMARIZATION=1 or USE_SUMMARIZATION=True
in core/config.py.

Why optional?
-------------
Summarization adds ~1–2 s of LLM latency per ad injection turn.  For
experiments that compare ad intrusiveness, that latency is confounding;
disable it in those conditions.  For naturalness-focused ablations it
can be switched on without touching the pipeline.

Adding this stage to the pipeline:
-----------------------------------
    from core.retrieval.stages.summarizer import SummarizationStage

    pipeline = AdRetrievalPipeline(
        catalog=catalog,
        stages=[
            IntentClassifier(),
            DenseRetriever(catalog, embedding_model=embed),
            HybridRefiner(catalog),
            Reranker(),
            AdFormatter(),
            SummarizationStage(),    # <- append after formatter
        ],
    )
"""

from __future__ import annotations

from typing import Any, Dict, List

from core.config import SUMMARIZATION_PROMPT, USE_SUMMARIZATION
from core.log import logger
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.state import PipelineState


class SummarizationStage(PipelineStage):
    """
    Rewrites the top ad's text field with a concise LLM-generated sentence.

    Config keys (core.config)
    -------------------------
    USE_SUMMARIZATION  : bool — if False, stage is a transparent pass-through.
    SUMMARIZATION_PROMPT : str template with {title}, {category}, {text}.

    The LLM call is made via the same API_URL / DEFAULT_MODEL as the
    conversation engine (OpenAI-compatible endpoint).
    """

    def __init__(self, enabled: bool | None = None) -> None:
        """
        Parameters
        ----------
        enabled : override for USE_SUMMARIZATION config flag.
                  Pass True/False to force-enable/disable in tests.
        """
        self._enabled: bool = USE_SUMMARIZATION if enabled is None else enabled

    # ── PipelineStage interface ───────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if not self._enabled:
            return state  # transparent pass-through

        if state.top_ad is None:
            return state  # nothing to summarize

        ad = state.top_ad
        prompt = SUMMARIZATION_PROMPT.format(
            title=ad.title or "",
            category=ad.metadata.get("category", ""),
            text=ad.text or "",
        )

        try:
            summary = self._call_llm(prompt)
            # Replace ad.text in-place (dataclass is mutable)
            state.top_ad = ad.__class__(
                title=ad.title,
                text=summary,
                cta=ad.cta,
                question=ad.question,
                source_item_id=ad.source_item_id,
                relevance_score=ad.relevance_score,
                metadata=ad.metadata,
            )
            if state.top_ads:
                state.top_ads[0] = state.top_ad
            logger.debug("SummarizationStage: rewrote ad text to: {}", summary[:80])
        except Exception as exc:
            logger.opt(exception=True).warning(
                "SummarizationStage: LLM call failed, keeping original text — {}", exc
            )

        return state

    # ── private ──────────────────────────────────────────────────────────

    def _call_llm(self, user_message: str) -> str:
        """Fire a single-turn LLM call and return the assistant reply."""
        import httpx

        from core.config import API_URL, DEFAULT_MAX_TOKENS, DEFAULT_MODEL, LLM_TIMEOUT_SECONDS

        payload: Dict[str, Any] = {
            "model": DEFAULT_MODEL,
            "messages": [{"role": "user", "content": user_message}],
            "max_tokens": 64,      # summaries are short — cap tight
            "temperature": 0.0,    # deterministic summaries
        }
        resp = httpx.post(API_URL, json=payload, timeout=LLM_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
