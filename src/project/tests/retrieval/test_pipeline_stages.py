"""Unit tests for retrieval pipeline stage wiring."""

from __future__ import annotations

import pytest

from core.retrieval.pipeline import AdRetrievalPipeline, build_default_stages
from core.retrieval.stages.state import PipelineState


@pytest.mark.unit
class TestBuildDefaultStages:
    def test_includes_query_expansion_by_default(self):
        names = [s.__class__.__name__ for s in build_default_stages(catalog=None)]
        assert "QueryExpansionStage" in names
        assert names.index("QueryExpansionStage") < names.index("DenseRetriever")

    def test_query_expansion_omitted_when_mode_none(self, monkeypatch):
        monkeypatch.setenv("QUERY_EXPANSION_MODE", "none")
        import importlib
        import core.config as cfg

        importlib.reload(cfg)
        from core.retrieval import runtime

        runtime.reset_for_tests()

        names = [s.__class__.__name__ for s in build_default_stages(catalog=None)]
        assert "QueryExpansionStage" not in names

    def test_run_applies_context_aware_query(self):
        class CaptureQuery:
            def run(self, state: PipelineState) -> PipelineState:
                state._captured_query = state.query
                return state

        pipeline = AdRetrievalPipeline(
            catalog=None,
            stages=[CaptureQuery()],
        )
        ctx = [
            {"role": "user", "content": "Peruvian food and ceviche"},
            {"role": "user", "content": "short"},
        ]
        pipeline.run("short", ctx)
        assert "Peruvian" in pipeline.last_state._captured_query
