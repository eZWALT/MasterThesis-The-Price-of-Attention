"""
HyDE helpers — parse multi-document LLM output and fuse dense search lists.

Fusion (not averaging): each hypothetical doc is embedded separately, FAISS
returns top-k per doc, then reciprocal rank fusion (RRF) merges the lists.
Items that rank well under multiple HyDE angles score higher; vectors are
never averaged.
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import List

from core.config import (
    EMBEDDING_MODEL_NAME,
    HYDE_MAX_TOKENS,
    HYDE_NUM_DOCS,
    HYDE_TOKENS_PER_DOC,
    RRF_K,
)


_SEPARATOR_RE = re.compile(r"\n\s*---\s*\n", re.MULTILINE)


def effective_hyde_num_docs() -> int:
    """Cap doc count so num_docs × per-doc budget fits HYDE_MAX_TOKENS."""
    per_doc = max(1, HYDE_TOKENS_PER_DOC)
    cap = max(1, HYDE_MAX_TOKENS // per_doc)
    return max(1, min(HYDE_NUM_DOCS, cap))


def hyde_generation_max_tokens() -> int:
    """
    Exact Ollama/OpenAI ``num_predict`` / ``max_tokens`` for the single HyDE call.

    Hard ceiling on total generated tokens (all listings in one response).
    """
    n = effective_hyde_num_docs()
    return min(HYDE_MAX_TOKENS, max(1, n * HYDE_TOKENS_PER_DOC))


@lru_cache(maxsize=1)
def _embedding_tokenizer():
    """Same vocabulary as the retrieval embedder — for exact token counts in debug."""
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(EMBEDDING_MODEL_NAME)


def count_embedding_tokens(text: str) -> int:
    """Exact token count (display/diag only — generation limit is ``hyde_generation_max_tokens``)."""
    if not (text or "").strip():
        return 0
    return len(_embedding_tokenizer().encode(text, add_special_tokens=False))


def parse_hyde_documents(text: str, *, max_docs: int | None = None) -> List[str]:
    """Split one LLM response into up to ``max_docs`` passages (--- separated)."""
    if max_docs is None:
        max_docs = effective_hyde_num_docs()
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
