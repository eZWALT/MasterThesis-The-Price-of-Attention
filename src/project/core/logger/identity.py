"""
Experiment Identity — deterministic, unique, queryable IDs.

Generates hierarchical identifiers for experiments:

    experiment_id   — one per config/session (stable across restarts)
    run_id          — one per app launch (distinguishes restarts)
    participant_id  — one per human subject (assigned externally)
    conversation_id — one per trial conversation (UUID, created in manager)

Format: exp_{ISO_UTC}_{config_hash8}
    Example: exp_20260524T154233Z_a83f2c1d

The config hash is derived from the experiment-relevant settings
(model, ad modes, retrieval config) so that the same configuration
always produces the same hash suffix — useful for deduplication and
grouping.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any, Dict, Optional


def make_experiment_id(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Generate a stable experiment ID from config + timestamp.

    Parameters
    ----------
    config : dict of experiment-relevant keys.
             If None, uses a snapshot of core.config values.

    Returns
    -------
    str like "exp_20260524T154233Z_a83f2c1d"
    """
    if config is None:
        config = _default_config_snapshot()

    raw = str(sorted(config.items()))
    h = hashlib.sha1(raw.encode()).hexdigest()[:8]
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    return f"exp_{ts}_{h}"


def make_run_id() -> str:
    """
    Generate a unique run ID for this app launch.

    Format: run_{short_uuid}
    """
    return f"run_{uuid.uuid4().hex[:12]}"


def _default_config_snapshot() -> Dict[str, Any]:
    """
    Capture experiment-relevant config values for hashing.

    Only includes settings that affect experimental results —
    NOT display/UI settings.
    """
    from core.config import (
        DEFAULT_MODEL,
        LLM_BACKEND,
        EMBEDDING_MODEL_NAME,
        RERANKER_MODEL_NAME,
        AD_MODES,
        TRIALS_PER_SESSION,
        MIN_TURNS_PER_TRIAL,
        MAX_TURNS_PER_TRIAL,
        AD_INJECTION_TURNS,
        DENSE_TOP_K,
        RERANKER_TOP_K,
        USE_HYBRID,
        BM25_WEIGHT,
        DENSE_WEIGHT,
        CATALOG_DIR,
    )

    return {
        "model": DEFAULT_MODEL,
        "llm_backend": LLM_BACKEND,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "reranker_model": RERANKER_MODEL_NAME,
        "ad_modes": str(AD_MODES),
        "trials_per_session": TRIALS_PER_SESSION,
        "min_turns": MIN_TURNS_PER_TRIAL,
        "max_turns": MAX_TURNS_PER_TRIAL,
        "ad_injection_turns": str(AD_INJECTION_TURNS),
        "dense_top_k": DENSE_TOP_K,
        "reranker_top_k": RERANKER_TOP_K,
        "use_hybrid": USE_HYBRID,
        "bm25_weight": BM25_WEIGHT,
        "dense_weight": DENSE_WEIGHT,
        "catalog_dir": CATALOG_DIR,
    }
