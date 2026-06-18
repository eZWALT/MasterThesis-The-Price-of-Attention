"""
Helpers to keep JSONL event payloads small and non-redundant.

Envelope fields (turn, ad_mode, conversation_id, trial_index, …) are set once
on LogEntry; data should not repeat them unless needed for nested exports.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

# retrieval_query duplicates the top-level "query" on retrieval events.
_LOG_DIAG_OMIT_KEYS = frozenset({"retrieval_query"})


def compact_event_data(data: Any, *, turn: Optional[int] = None) -> Any:
    """Drop payload keys that duplicate the LogEntry envelope."""
    if not isinstance(data, dict):
        return data
    out = dict(data)
    if turn is not None and out.get("turn") == turn:
        out.pop("turn", None)
    if out.get("conversation_id"):
        out.pop("conversation_id", None)
    return out


def compact_retrieval_diag(diag: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge pipeline diag into JSONL; keeps hyde_documents for traceability."""
    if not diag:
        return {}
    return {k: v for k, v in diag.items() if k not in _LOG_DIAG_OMIT_KEYS and v is not None}


def build_retrieval_log_data(
    *,
    query: str,
    turn: int,
    retrieval: Any,
    intent_label: str,
    retrieval_latency_ms: float,
    retrieval_backend: str,
) -> Dict[str, Any]:
    """Structured retrieval row for JSONL (HyDE passages logged once per retrieval)."""
    ad = retrieval.primary
    ad_metadata = ad.metadata or {}
    payload: Dict[str, Any] = {
        "query": query,
        "ad_title": ad.title,
        "ad_item_id": ad.source_item_id,
        "ad_source": ad_metadata.get("source", "amazon"),
        "ad_category": ad_metadata.get("category", ""),
        "ad_relevance_score": ad.relevance_score,
        "ad_cta": ad.cta,
        "candidate_count": len(retrieval.ads),
        "candidate_titles": [a.title for a in retrieval.ads],
        "retrieval_latency_ms": round(retrieval_latency_ms, 1),
        "retrieval_backend": retrieval_backend,
        "intent_label": intent_label,
    }
    payload.update(compact_retrieval_diag(getattr(retrieval, "diag", None)))
    return compact_event_data(payload, turn=turn)
