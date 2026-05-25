"""
Build the text used for dense retrieval / BM25 / reranking from query + chat context.
"""

from __future__ import annotations

from typing import Dict, List


def build_retrieval_query(
    query: str,
    context: List[Dict[str, str]],
    *,
    max_chars: int = 1200,
) -> str:
    """
    Combine the latest user message with recent user turns.

    The pipeline historically embedded only ``query`` (last message), so
    multi-turn chats retrieved ads for the wrong topic when the last line was short.
    """
    query = (query or "").strip()
    seen: set[str] = set()
    parts: List[str] = []

    for msg in context:
        if msg.get("role") != "user":
            continue
        text = (msg.get("content") or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        parts.append(text)

    if query and query not in seen:
        parts.append(query)
    elif query and not parts:
        parts.append(query)

    if not parts:
        return query

    # Weight the latest user message: repeat once at the end for emphasis.
    if query and parts[-1] != query:
        parts.append(query)

    combined = " ".join(parts[-4:])
    if len(combined) > max_chars:
        combined = combined[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return combined
