"""
HyDE helpers — parse multi-document LLM output and fuse dense search lists.
"""

from __future__ import annotations

import re
from typing import List

from core.config import HYDE_MAX_TOKENS, HYDE_NUM_DOCS, HYDE_TOKENS_PER_DOC, RRF_K


_SEPARATOR_RE = re.compile(r"\n\s*---\s*\n", re.MULTILINE)


def effective_hyde_num_docs() -> int:
    """Cap doc count so num_docs × per-doc budget fits HYDE_MAX_TOKENS."""
    per_doc = max(1, HYDE_TOKENS_PER_DOC)
    cap = max(1, HYDE_MAX_TOKENS // per_doc)
    return max(1, min(HYDE_NUM_DOCS, cap))


def parse_hyde_documents(text: str, *, max_docs: int | None = None) -> List[str]:
    if max_docs is None:
        max_docs = effective_hyde_num_docs()
    """
    Split one LLM response into up to ``max_docs`` hypothetical product passages.

    Expected format (prompt-enforced): passages separated by a line containing only ---.
    Falls back to a single passage if the model did not use separators.
    """
    raw = (text or "").strip()
    if not raw:
        return []

    parts = [p.strip() for p in _SEPARATOR_RE.split(raw) if p.strip()]
    if len(parts) >= 2:
        return parts[:max_docs]

    # Numbered list fallback: "1. ... 2. ..."
    numbered = re.split(r"\n\s*(?=\d+[\.\)]\s)", raw)
    numbered = [re.sub(r"^\d+[\.\)]\s*", "", p).strip() for p in numbered if p.strip()]
    if len(numbered) >= 2:
        return numbered[:max_docs]

    return [raw]


def rrf_merge_item_ids(lists: List[List[str]], *, k: int = RRF_K) -> List[str]:
    """Reciprocal rank fusion across multiple FAISS hit lists (one per HyDE doc)."""
    scores: dict[str, float] = {}
    for hits in lists:
        for rank, item_id in enumerate(hits):
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.keys(), key=lambda i: scores[i], reverse=True)
