"""Unit tests for context-aware retrieval query building."""

from __future__ import annotations

import pytest

from core.retrieval.query_text import build_retrieval_query


@pytest.mark.unit
class TestBuildRetrievalQuery:
    def test_uses_recent_user_turns(self):
        ctx = [
            {"role": "user", "content": "Why do Peruvians eat pigeons?"},
            {"role": "assistant", "content": "Long answer about cuy."},
            {"role": "user", "content": "What about ceviche?"},
        ]
        q = build_retrieval_query("What about ceviche?", ctx)
        assert "Peruvians" in q or "pigeons" in q
        assert "ceviche" in q

    def test_single_message_unchanged(self):
        q = build_retrieval_query("running shoes", [])
        assert q == "running shoes"
