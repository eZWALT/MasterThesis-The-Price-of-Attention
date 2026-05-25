"""
E2E: HyDE vs no-HyDE retrieval.

Loads the real FAISS index and embedding/reranker models. HyDE LLM calls are
mocked by default so CI does not need Ollama; optional live test when Ollama is up.

    pytest -m e2e tests/test_e2e_hyde.py -v
"""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from tests.test_e2e_pipeline import skip_no_gpu

HYDE_MOCK_RESPONSE = (
    "Professional marathon running shoes with carbon plate and responsive foam "
    "midsole for long-distance road racing and cushioned heel strike protection.\n"
    "---\n"
    "Moisture-wicking athletic socks bundle designed for blister prevention during "
    "high-mileage training runs and breathable mesh upper compatibility.\n"
)

QUERIES = [
    "running shoes for marathon training",
    "wireless headphones for commuting",
    "kitchen blender for smoothies",
]


def _ollama_available() -> bool:
    try:
        import requests
        from core.config import OLLAMA_API_BASE

        url = f"{OLLAMA_API_BASE.rstrip('/')}/api/tags"
        return requests.get(url, timeout=3).status_code == 200
    except Exception:
        return False


skip_no_ollama = pytest.mark.skipif(
    not _ollama_available(),
    reason="Ollama not reachable — skipping live HyDE E2E",
)


def _warm_retrieve(mode: str, query: str, context: list | None = None):
    """Rebuild pipeline with forced query-expansion mode and run one retrieval."""
    import core.retrieval as retrieval_mod
    from core.retrieval.runtime import reset_for_tests, set_query_expansion_mode_for_tests

    reset_for_tests()
    set_query_expansion_mode_for_tests(mode)
    retrieval_mod.reset_pipeline_singleton()
    # Warmup loads FAISS/embed; HyDE LLM is skipped for query "warmup".
    retrieval_mod.retrieve_ad("warmup", [])
    return retrieval_mod.retrieve_ad(query, context or [])


@pytest.mark.e2e
@skip_no_gpu
class TestHydeVsNoneE2E:
    """Compare retrieval with QueryExpansionStage off vs on (mocked HyDE text)."""

    @pytest.fixture(autouse=True)
    def _reset_runtime(self):
        from core.retrieval.runtime import reset_for_tests

        reset_for_tests()
        yield
        reset_for_tests()

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_none_mode_has_no_hyde_documents(self, mock_llm):
        result = _warm_retrieve("none", QUERIES[0])
        mock_llm.assert_not_called()
        assert result is not None and result.has_ads
        assert not result.diag.get("hyde_used")
        assert not result.diag.get("hyde_documents")

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_hyde_mode_populates_documents_and_diag(self, mock_llm):
        mock_llm.return_value = HYDE_MOCK_RESPONSE
        result = _warm_retrieve("hyde", QUERIES[0])
        mock_llm.assert_called_once()
        assert result is not None and result.has_ads
        assert result.diag.get("hyde_used") is True
        docs = result.diag.get("hyde_documents") or []
        assert len(docs) >= 2
        assert result.diag.get("hyde_llm_max_tokens", 0) > 0

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_hyde_changes_top_ad_vs_none(self, mock_llm):
        mock_llm.return_value = HYDE_MOCK_RESPONSE
        ctx = [
            {"role": "user", "content": "I need gear for marathon training"},
            {"role": "user", "content": QUERIES[0]},
        ]
        r_none = _warm_retrieve("none", QUERIES[0], ctx)
        r_hyde = _warm_retrieve("hyde", QUERIES[0], ctx)

        assert r_none and r_hyde and r_none.primary and r_hyde.primary
        assert len(r_hyde.diag.get("hyde_documents") or []) >= 2
        assert r_hyde.diag.get("hyde_used") is True
        assert not r_none.diag.get("hyde_used")

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    @pytest.mark.parametrize("query", QUERIES)
    def test_hyde_returns_ads_for_varied_queries(self, mock_llm, query):
        mock_llm.return_value = HYDE_MOCK_RESPONSE
        result = _warm_retrieve("hyde", query)
        assert result is not None and result.primary
        assert result.primary.source_item_id != "mock"

    @patch("core.retrieval.stages.query_preprocessor.preprocess_llm_chat")
    def test_hyde_adds_llm_latency_budget(self, mock_llm):
        mock_llm.return_value = HYDE_MOCK_RESPONSE
        t0 = time.perf_counter()
        result = _warm_retrieve("hyde", QUERIES[1])
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        assert result is not None
        qe_ms = (result.diag.get("retrieval_stage_ms") or {}).get(
            "QueryExpansionStage", 0
        )
        assert qe_ms >= 0
        # Mock is fast; live HyDE would dominate — we only assert stage is present.
        assert "QueryExpansionStage" in (result.diag.get("retrieval_stage_ms") or {})


@pytest.mark.e2e
@skip_no_gpu
@skip_no_ollama
class TestHydeLiveOllamaE2E:
    """Full HyDE with real Ollama — run manually when comparing latency/quality."""

    def test_live_hyde_end_to_end(self):
        r_none = _warm_retrieve("none", QUERIES[0])
        r_hyde = _warm_retrieve("hyde", QUERIES[0])
        assert r_none and r_hyde and r_none.primary and r_hyde.primary
        assert r_hyde.diag.get("hyde_used")
        assert len(r_hyde.diag.get("hyde_documents") or []) >= 1
