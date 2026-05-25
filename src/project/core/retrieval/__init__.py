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

from core.ad_injection.models import AdRetrievalResult
from core.log import logger

# Module-level singletons — built once on first call.
_pipeline = None


def retrieve_ad(query: str, context: List[Dict[str, str]]) -> Optional[AdRetrievalResult]:
    """
    Run the full 5-stage retrieval pipeline and return ranked ads.

    Returns None if the pipeline produces no candidates (caller falls
    back to mock ads via get_ad).

    Parameters
    ----------
    query   : user's latest message.
    context : full conversation history as list of {role, content} dicts.
    """
    global _pipeline
    if _pipeline is None:
        _pipeline = _build_pipeline()

    result = _pipeline.run(query, context)
    from core.retrieval.log_util import is_warmup_query

    if result is None or not result.has_ads:
        if not is_warmup_query(query):
            logger.warning("retrieval no ads query={!r}", query[:80])
        return None

    logger.debug(
        "Retrieved {} ad(s): {}",
        len(result.ads),
        [ad.title for ad in result.ads],
    )
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

    from core.retrieval.log_util import log_pipeline_building, log_pipeline_ready

    log_pipeline_building()

    embed = build_embedding_model(
        model_name=EMBEDDING_MODEL_NAME,
        device=EMBEDDING_DEVICE,
    )
    adapter = build_adapter()
    catalog = AdCatalog.load(
        catalog_path=CATALOG_PATH,
        index_path=FAISS_INDEX_PATH
    )
    from core.retrieval.pipeline import build_default_stages

    stage_names = [s.__class__.__name__ for s in build_default_stages(catalog, embed)]
    pipeline = AdRetrievalPipeline(catalog=catalog, embedding_model=embed)
    log_pipeline_ready(n_items=len(catalog), stage_names=stage_names)
    logger.debug("retrieval adapter={}", adapter.__class__.__name__)
    return pipeline


__all__ = ["retrieve_ad"]
