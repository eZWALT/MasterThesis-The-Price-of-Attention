"""
core.retrieval — public API.

The only symbol callers (provider.py) need to import:

    from core.retrieval import retrieve_ad

Everything else (pipeline, catalog, stages, config) is an internal
implementation detail.

The pipeline and catalog are built lazily on the first call to
retrieve_ad() and cached for the lifetime of the process.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from core.ad_injection.models import Ad
from core.log import logger

# Module-level singletons — built once on first call.
_pipeline = None


def retrieve_ad(query: str, context: List[Dict[str, str]]) -> Ad:
    """
    Run the full 5-stage retrieval pipeline and return the selected Ad.

    Falls back to the mock ad if the pipeline returns nothing
    (empty catalog, index error, etc.) so the experiment never blocks.

    Parameters
    ----------
    query   : user's latest message.
    context : full conversation history as list of {role, content} dicts.
    """
    global _pipeline
    if _pipeline is None:
        _pipeline = _build_pipeline()


    result: Optional[Ad] = _pipeline.run(query, context)

    if result is None:
        from core.log import logger
        logger.warning(f"[DEBUG] No ad retrieved for query: {query}")
        return None

    # Log candidate titles if possible (after result assignment)
    try:
        state = getattr(_pipeline, 'last_state', None)
        if state and hasattr(state, 'candidates'):
            from core.log import logger
            titles = [getattr(c, 'title', None) for c in state.candidates]
            logger.info(f"[DEBUG] Retrieved candidate titles: {titles}")
    except Exception as e:
        from core.log import logger
        logger.warning(f"[DEBUG] Could not log candidate titles: {e}")

    return result


def _build_pipeline():
    """Lazy construction: loads models + index on first call.

    The embedding model is built once and shared between AdCatalog
    (index building) and DenseRetriever (query encoding) so the model
    is not loaded into memory twice.
    """
    from core.config import EMBEDDING_MODEL_NAME, EMBEDDING_DEVICE, CATALOG_PATH, FAISS_INDEX_PATH
    from core.retrieval.catalog import AdCatalog
    from core.retrieval.pipeline import AdRetrievalPipeline
    from core.retrieval.embeddings import build_embedding_model
    from core.retrieval.adapters import build_adapter

    logger.info("Building retrieval pipeline (first call)...")

    # Build embedding model first — needed to construct / load FAISS index.
    embed = build_embedding_model(
        model_name=EMBEDDING_MODEL_NAME,
        device=EMBEDDING_DEVICE,
    )
    adapter = build_adapter()  # reads CATALOG_ADAPTER env var / config
    catalog = AdCatalog.load(
        catalog_path=CATALOG_PATH,
        index_path=FAISS_INDEX_PATH
    )
    # Pass the already-loaded model so DenseRetriever reuses it (no double load).
    pipeline = AdRetrievalPipeline(catalog=catalog, embedding_model=embed)
    logger.info(
        "Retrieval pipeline ready — catalog: {} items, adapter: {}",
        len(catalog),
        adapter.__class__.__name__,
    )
    return pipeline


def _fallback_ad() -> Ad:
    """Return a safe mock ad when the pipeline produces nothing."""
    from core.config import MOCK_AD_TITLE, MOCK_AD_TEXT, MOCK_AD_CTA, MOCK_AD_QUESTION
    return Ad(
        title=MOCK_AD_TITLE,
        text=MOCK_AD_TEXT,
        cta=MOCK_AD_CTA,
        question=MOCK_AD_QUESTION,
        source_item_id="fallback",
        relevance_score=0.0,
    )


__all__ = ["retrieve_ad"]
