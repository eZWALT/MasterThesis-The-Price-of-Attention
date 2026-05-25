"""Unit tests for HyDE / query expansion preprocessor stage."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.retrieval.stages.query_preprocessor import QueryExpansionStage
from core.retrieval.stages.state import PipelineState


@pytest.mark.unit
class TestQueryExpansionStage:
    def test_none_mode_is_noop(self):
        state = PipelineState(query="running shoes", context=[])
        out = QueryExpansionStage(mode="none").run(state)
        assert out.expanded_query == ""

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_hyde_sets_expanded_query(self, mock_llm):
        mock_llm.return_value = "Trail shoes.\n---\nHiking boots."
        state = PipelineState(query="shoes for hiking", context=[])
        out = QueryExpansionStage(mode="hyde").run(state)
        assert len(out.hyde_documents) == 2
        assert out.expanded_query == "Trail shoes."
        mock_llm.assert_called_once()

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_hyde_failure_leaves_empty_expanded_query(self, mock_llm):
        mock_llm.side_effect = RuntimeError("LLM down")
        state = PipelineState(query="shoes", context=[])
        out = QueryExpansionStage(mode="hyde").run(state)
        assert out.expanded_query == ""

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_expand_mode_uses_expand_tokens(self, mock_llm):
        mock_llm.return_value = "waterproof hiking boots insulated"
        state = PipelineState(query="boots", context=[], context_summary="winter trip")
        QueryExpansionStage(mode="expand").run(state)
        _, kwargs = mock_llm.call_args
        assert kwargs["max_tokens"] > 0
