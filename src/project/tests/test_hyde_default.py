"""Verify HyDE is on by default and feeds the dense retriever."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.retrieval.pipeline import AdRetrievalPipeline, build_default_stages
from core.retrieval.stages.query_preprocessor import QueryExpansionStage
from core.retrieval.stages.state import PipelineState


@pytest.mark.unit
class TestHydeDefault:
    def test_config_default_is_hyde(self):
        import core.config as cfg

        assert cfg.QUERY_EXPANSION_MODE == "hyde"

    def test_build_default_stages_includes_query_expansion(self):
        names = [s.__class__.__name__ for s in build_default_stages(catalog=None)]
        assert "QueryExpansionStage" in names

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_pipeline_passes_hyde_text_to_downstream(self, mock_llm):
        mock_llm.return_value = (
            "Trail running shoes with breathable mesh.\n"
            "---\n"
            "Waterproof hiking boots with ankle support.\n"
            "---\n"
            "Lightweight approach shoes for rocky terrain."
        )

        captured: dict = {}

        class CaptureEmbed:
            def run(self, state: PipelineState) -> PipelineState:
                captured["hyde_docs"] = list(state.hyde_documents)
                captured["hyde_used"] = bool(state.hyde_documents)
                return state

        pipeline = AdRetrievalPipeline(
            catalog=None,
            stages=[QueryExpansionStage(mode="hyde"), CaptureEmbed()],
        )
        pipeline.run("boots for hiking", [])

        assert captured["hyde_used"] is True
        assert len(captured["hyde_docs"]) == 3
        mock_llm.assert_called_once()
