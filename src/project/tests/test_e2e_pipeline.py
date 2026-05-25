"""
End-to-end tests for the retrieval pipeline.

These load real models and hit the FAISS index — slow, require GPU (or CPU
fallback). Run with:

    pytest -m e2e -v

Skip in CI by default unless GPU is available.
"""

from __future__ import annotations

import time

import pytest


def _gpu_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


skip_no_gpu = pytest.mark.skipif(
    not _gpu_available(),
    reason="No CUDA GPU available — skipping E2E tests",
)


@pytest.mark.e2e
@skip_no_gpu
class TestPipelineE2E:
    """Full pipeline integration tests — loads models, queries catalog."""

    @pytest.fixture(autouse=True)
    def _setup_pipeline(self):
        """Build pipeline once for the class."""
        from core.retrieval import retrieve_ad

        # Trigger lazy init
        retrieve_ad("warmup", [])
        self.retrieve_ad = retrieve_ad

    @pytest.mark.parametrize("query", [
        "I need wireless headphones for music",
        "running shoes for marathon training",
        "kitchen blender for smoothies",
        "laptop for programming",
        "birthday gift for my mom",
    ])
    def test_query_returns_real_ad(self, query):
        """Various queries return real ads (not fallback)."""
        result = self.retrieve_ad(query, [])
        assert result is not None
        ad = result.primary
        assert ad is not None
        assert ad.title
        assert ad.text
        assert ad.source_item_id != "fallback"
        assert isinstance(ad.relevance_score, float)
        assert len(result.ads) >= 1

    def test_different_queries_get_different_results(self):
        """Semantically different queries should return different ads."""
        r1 = self.retrieve_ad("running shoes for marathon training", [])
        r2 = self.retrieve_ad("kitchen blender for smoothies", [])
        ad1, ad2 = r1.primary, r2.primary
        assert ad1 and ad2
        assert ad1.source_item_id != ad2.source_item_id or ad1.title != ad2.title

    @pytest.mark.parametrize("query", [
        "",
        "   ",
        "a",
        "?!@#$%",
    ], ids=["empty", "whitespace", "single_char", "special_chars"])
    def test_edge_case_queries_do_not_crash(self, query):
        """Degenerate inputs should return something without raising."""
        result = self.retrieve_ad(query, [])
        assert result is not None and result.primary is not None
        assert result.primary.title

    def test_long_query_does_not_crash(self):
        """Very long input should be truncated gracefully."""
        long_query = "I want " * 500 + "a nice pair of shoes"
        result = self.retrieve_ad(long_query, [])
        assert result is not None and result.primary is not None
        assert result.primary.title

    @pytest.mark.parametrize("query", [
        "bluetooth speaker",
        "coffee maker",
        "yoga mat",
    ])
    def test_query_latency_under_threshold(self, query):
        """After warmup, queries should complete in <5s."""
        t0 = time.time()
        self.retrieve_ad(query, [])
        elapsed = time.time() - t0
        assert elapsed < 5.0, f"Query '{query}' took {elapsed:.2f}s — too slow"

    @pytest.mark.parametrize("context", [
        [],
        [{"role": "user", "content": "I need headphones"}],
        [
            {"role": "user", "content": "I'm looking for headphones"},
            {"role": "assistant", "content": "What's your budget?"},
            {"role": "user", "content": "Under 100 dollars, wireless"},
        ],
    ], ids=["no_context", "single_turn", "multi_turn"])
    def test_context_variations(self, context):
        """Pipeline handles various context lengths."""
        result = self.retrieve_ad("something good for commuting", context)
        assert result is not None and result.primary is not None
        assert result.primary.title

    def test_multiple_sequential_queries_no_state_leak(self):
        """Pipeline handles multiple queries without state leaking."""
        queries = ["gaming mouse", "yoga mat", "sci-fi novel", "espresso machine", "birthday card"]
        results = [self.retrieve_ad(q, []) for q in queries]

        for q, result in zip(queries, results):
            ad = result.primary if result else None
            assert ad and ad.title, f"Empty title for query: {q}"
            assert ad.text, f"Empty text for query: {q}"

        unique_ids = {r.primary.source_item_id for r in results if r and r.primary}
        assert len(unique_ids) >= 2, "All queries returned the same item"


@pytest.mark.e2e
@skip_no_gpu
class TestGPUMemoryE2E:
    """Verify GPU memory usage stays within bounds after loading."""

    def test_vram_within_bounds(self):
        """After loading, GPU usage shouldn't exceed estimates by too much."""
        import torch

        # Trigger pipeline load
        from core.retrieval import retrieve_ad
        retrieve_ad("test", [])

        import core.config as cfg
        from core.device import VRAM_ESTIMATES

        # Check the device where embedding lives
        if cfg.EMBEDDING_DEVICE.startswith("cuda"):
            idx = int(cfg.EMBEDDING_DEVICE.split(":")[1])
            free, total = torch.cuda.mem_get_info(idx)
            used_gb = (total - free) / 1024**3

            # We expect embedding + reranker ≈ 20 GB (at BF16)
            # Allow up to 28 GB to account for other processes + fragmentation
            max_expected_gb = 28.0
            assert used_gb < max_expected_gb, (
                f"GPU {idx} using {used_gb:.1f} GB — exceeds {max_expected_gb} GB limit"
            )
