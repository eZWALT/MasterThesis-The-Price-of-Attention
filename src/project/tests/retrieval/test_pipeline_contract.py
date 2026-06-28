"""
Unit tests for retrieval pipeline contracts — empty results, stage wiring.
"""

from __future__ import annotations

import pytest

from core.retrieval.pipeline import AdRetrievalPipeline
from core.retrieval.stages.formatter import AdFormatter
from core.retrieval.stages.state import PipelineState


@pytest.mark.unit
class TestPipelineEmptyResults:
    def test_returns_none_when_formatter_has_no_candidates(self):
        pipeline = AdRetrievalPipeline(catalog=None, stages=[AdFormatter()])
        result = pipeline.run("query", [])
        assert result is None
        assert pipeline.last_state is not None
        assert pipeline.last_state.top_ads == []

    def test_formatter_empty_ranked_and_candidates(self):
        formatter = AdFormatter()
        state = PipelineState(query="q")
        out = formatter.run(state)
        assert out.top_ad is None
        assert out.top_ads == []


@pytest.mark.unit
class TestRetrieveAdModule:
    def test_retrieve_ad_returns_none_when_pipeline_empty(self):
        from unittest.mock import MagicMock, patch

        import core.retrieval as retrieval_mod

        fake_pipeline = MagicMock()
        fake_pipeline.run.return_value = None
        with patch.object(retrieval_mod, "_pipeline", fake_pipeline):
            result = retrieval_mod.retrieve_ad("q", [])
        assert result is None
