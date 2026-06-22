"""
Ad provider and injector factory.

Public API
----------
get_ad(query, context)  — returns ranked ads to inject at the current turn.
                           Routes to mock backend or the full RAG pipeline
                           depending on AD_BACKEND (env var or module flag).
get_injector(ad_mode)   — returns the AdInjector strategy for a given mode key.

Switching backends
------------------
Set the environment variable:
    AD_BACKEND=mock    — instant, no GPU, static placeholder ad
    AD_BACKEND=rag     — full 5-stage retrieval pipeline (default)

Or change AD_BACKEND in core/config.py for dev convenience.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Dict, List, Optional

from core.config import (
    AD_BACKEND,
    MOCK_AD_TITLE,
    MOCK_AD_TEXT,
    MOCK_AD_CTA,
    MOCK_AD_QUESTION,
    MOCK_AD_IMAGE_PATH,
)
from core.ad_injection.models import Ad, AdRetrievalResult
from core.ad_injection.injectors import (
    AdInjector,
    InlinePersuasiveInjector,
    ExplicitAdBlockInjector,
)


def _load_mock_image_data_uri() -> str | None:
    """Read mock ad image from resources/ and return as base64 data URI."""
    path = Path(__file__).resolve().parent.parent / MOCK_AD_IMAGE_PATH
    if not path.exists():
        return None
    ext = path.suffix.lstrip(".").lower()
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{data}"


def get_ad(
    query: str = "",
    context: List[Dict] | None = None,
    backend: str | None = None,
    categories: Optional[List[str]] = None,
    task_prompt: str = "",
) -> AdRetrievalResult:
    """
    Return ranked ads to inject at the current conversation turn.

    Parameters
    ----------
    query       : the user's latest message (used by the RAG backend).
    context     : full conversation history (used by the RAG backend).
    backend     : optional per-call override — "mock" | "rag".
                  Defaults to the module-level AD_BACKEND setting.
    categories  : optional list of allowed meta-category strings for retrieval filtering.
    task_prompt : participant-facing task scenario for HyDE context.

    Returns
    -------
    AdRetrievalResult with up to RETRIEVAL_FINAL_TOP_N ranked ads.
    Falls back to the mock ad when the pipeline returns nothing.
    """
    effective = backend if backend in ("mock", "rag") else AD_BACKEND
    if effective == "rag":
        return _rag_ad(query, context or [], categories=categories, task_prompt=task_prompt)
    return _mock_ad()


def _mock_ad() -> AdRetrievalResult:
    """Static placeholder ad — zero latency, no model required."""
    image_uri = _load_mock_image_data_uri()
    metadata: dict = {"image": image_uri} if image_uri else {}
    ad = Ad(
        title=MOCK_AD_TITLE,
        text=MOCK_AD_TEXT,
        cta=MOCK_AD_CTA,
        question=MOCK_AD_QUESTION,
        source_item_id="mock",
        relevance_score=0.0,
        metadata=metadata,
    )
    return AdRetrievalResult(ads=[ad])


def _rag_ad(
    query: str,
    context: List[Dict],
    categories: Optional[List[str]] = None,
    task_prompt: str = "",
) -> AdRetrievalResult:
    """Full 5-stage retrieval pipeline (lazy import to keep startup fast)."""
    from core.retrieval import retrieve_ad

    result = retrieve_ad(query, context, categories=categories, task_prompt=task_prompt)
    if result is None or not result.has_ads:
        return _mock_ad()
    return result


# ── Injector registry & factory ───────────────────────────────

INJECTOR_REGISTRY: Dict[str, AdInjector] = {
    "inline_persuasive":        InlinePersuasiveInjector(),
    "explicit_ad_block":        ExplicitAdBlockInjector(),
}


def get_injector(ad_mode: str) -> AdInjector:
    """Return the AdInjector strategy for a given ad mode key."""
    injector = INJECTOR_REGISTRY.get(ad_mode)
    if injector is None:
        raise ValueError(
            f"Unknown ad mode '{ad_mode}'. "
            f"Valid modes: {list(INJECTOR_REGISTRY)}"
        )
    return injector
