"""Unit tests for multi-document HyDE parsing and RRF merge."""

from __future__ import annotations

import pytest

from core.retrieval.hyde import effective_hyde_num_docs, parse_hyde_documents, rrf_merge_item_ids


@pytest.mark.unit
class TestParseHydeDocuments:
    def test_splits_on_separator(self):
        text = "First product doc about boots.\n---\nSecond doc about waterproofing.\n---\nThird angle."
        docs = parse_hyde_documents(text, max_docs=4)
        assert len(docs) == 3
        assert "boots" in docs[0]

    def test_single_block_fallback(self):
        text = "One long hypothetical product description only."
        docs = parse_hyde_documents(text, max_docs=4)
        assert docs == [text]


@pytest.mark.unit
class TestEffectiveHydeNumDocs:
    def test_caps_by_token_budget(self, monkeypatch):
        monkeypatch.setenv("HYDE_MAX_TOKENS", "512")
        monkeypatch.setenv("HYDE_TOKENS_PER_DOC", "100")
        monkeypatch.setenv("HYDE_NUM_DOCS", "4")
        import importlib
        import core.config as cfg
        import core.retrieval.hyde as hyde_mod

        importlib.reload(cfg)
        importlib.reload(hyde_mod)
        assert hyde_mod.effective_hyde_num_docs() == 4


@pytest.mark.unit
class TestRrfMerge:
    def test_merges_overlapping_lists(self):
        merged = rrf_merge_item_ids([["a", "b", "c"], ["b", "d", "e"]])
        assert merged[0] == "b"
