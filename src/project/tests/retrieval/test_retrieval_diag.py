"""Unit tests for retrieval pipeline diagnostics."""

from __future__ import annotations

import pytest

from core.retrieval.pipeline import AdRetrievalPipeline, _build_retrieval_diag
from core.retrieval.stages.state import PipelineState


@pytest.mark.unit
class TestRetrievalDiag:
    def test_build_diag_includes_hyde_fields(self):
        hyde_text = "A traditional citrus-marinated seafood dish from Peru."
        state = PipelineState(
            query="Peruvian food ceviche",
            expanded_query=hyde_text,
            hyde_documents=[hyde_text],
        )
        state.stage_ms = {
            "QueryExpansionStage": 1200.5,
            "DenseRetriever": 40.2,
        }
        diag = _build_retrieval_diag(state)
        assert diag["hyde_used"] is True
        assert diag["query_expansion_ms"] == 1200.5
        assert diag["hyde_chars"] > 0
        assert len(diag["hyde_documents"]) == 1
        assert "Peru" in diag["hyde_documents"][0]
        assert "DenseRetriever" in diag["retrieval_stage_ms"]

    def test_pipeline_attaches_diag_on_result(self):
        class FakeFormatter:
            def run(self, state: PipelineState) -> PipelineState:
                from core.ad_injection.models import Ad

                state.top_ads = [
                    Ad(
                        title="Test Product",
                        text="",
                        cta="Shop",
                        question="More?",
                        source_item_id="1",
                    )
                ]
                return state

        pipeline = AdRetrievalPipeline(catalog=None, stages=[FakeFormatter()])
        result = pipeline.run("query", [])
        assert result is not None
        assert "retrieval_total_ms" in result.diag
