"""Shared LLM helper for retrieval preprocessor stages (context summary, HyDE)."""

from __future__ import annotations

from core.config import DEFAULT_MODEL
from core.conversation.llm_client import LLMClient

# Reuse a single client instance — avoids re-instantiating per retrieval call.
_client: LLMClient | None = None


def _get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient()
    return _client


def preprocess_llm_chat(
    prompt: str,
    *,
    temperature: float,
    max_tokens: int,
) -> str:
    """Single-turn chat used by ContextSummaryStage and QueryExpansionStage."""
    return _get_client().chat(
        [{"role": "user", "content": prompt}],
        model=DEFAULT_MODEL,
        temperature=temperature,
        max_tokens=max_tokens,
    )
