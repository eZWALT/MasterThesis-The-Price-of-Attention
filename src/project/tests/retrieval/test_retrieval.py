"""
Unit tests for retrieval components — embeddings, rerankers, factories.

These test the factory wiring and constructor logic (no real model loading
unless explicitly running with GPU).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# ─── Embedding factory ────────────────────────────────────────────────────────

@pytest.mark.unit
class TestEmbeddingFactory:
    def test_build_embedding_model_returns_instance(self):
        """Factory returns a HuggingFaceEmbedding (mocked instantiation)."""
        with patch("core.retrieval.embeddings.huggingface.SentenceTransformer") as mock_st:
            mock_st.return_value = MagicMock()
            from core.retrieval.embeddings import build_embedding_model
            model = build_embedding_model(
                model_name="test-model",
                device="cpu",
                batch_size=16,
                dtype="bfloat16",
            )
            assert model is not None
            mock_st.assert_called_once()
            # Verify dtype was passed
            _, kwargs = mock_st.call_args
            assert "model_kwargs" in kwargs
            import torch
            assert kwargs["model_kwargs"]["dtype"] == torch.bfloat16

    def test_build_embedding_unknown_backend_raises(self):
        from core.retrieval.embeddings import build_embedding_model
        with pytest.raises(ValueError, match="Unknown embedding backend"):
            build_embedding_model(
                model_name="test", device="cpu", backend="nonexistent"
            )

    def test_build_embedding_default_dtype_from_config(self):
        """When dtype=None, factory reads EMBEDDING_DTYPE from config."""
        with patch("core.retrieval.embeddings.huggingface.SentenceTransformer") as mock_st:
            mock_st.return_value = MagicMock()
            from core.retrieval.embeddings import build_embedding_model
            model = build_embedding_model(
                model_name="test-model",
                device="cpu",
            )
            # Should still pass dtype from config (bfloat16)
            _, kwargs = mock_st.call_args
            assert "model_kwargs" in kwargs
            assert "dtype" in kwargs["model_kwargs"]


# ─── Reranker factory ─────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRerankerFactory:
    def test_build_reranker_returns_instance(self):
        """Factory returns a CrossEncoderReranker (mocked instantiation)."""
        with patch("core.retrieval.rerankers.cross_encoder.CrossEncoder") as mock_ce:
            mock_ce.return_value = MagicMock()
            from core.retrieval.rerankers import build_reranker
            model = build_reranker(
                model_name="test-reranker",
                device="cpu",
                dtype="float16",
            )
            assert model is not None
            mock_ce.assert_called_once()
            _, kwargs = mock_ce.call_args
            assert "model_kwargs" in kwargs
            import torch
            assert kwargs["model_kwargs"]["dtype"] == torch.float16

    def test_build_reranker_unknown_backend_raises(self):
        from core.retrieval.rerankers import build_reranker
        with pytest.raises(ValueError, match="Unknown reranker backend"):
            build_reranker(model_name="test", device="cpu", backend="fake")

    def test_reranker_no_dtype_uses_fp32(self):
        """When dtype is explicitly 'float32', no special kwarg needed."""
        with patch("core.retrieval.rerankers.cross_encoder.CrossEncoder") as mock_ce:
            mock_ce.return_value = MagicMock()
            from core.retrieval.rerankers import build_reranker
            build_reranker(model_name="test", device="cpu", dtype="float32")
            _, kwargs = mock_ce.call_args
            import torch
            assert kwargs["model_kwargs"]["dtype"] == torch.float32


# ─── Embedding encode contract ────────────────────────────────────────────────

@pytest.mark.unit
class TestEmbeddingContract:
    def test_encode_returns_ndarray(self):
        """HuggingFaceEmbedding.encode() returns float32 numpy array."""
        import numpy as np

        with patch("core.retrieval.embeddings.huggingface.SentenceTransformer") as mock_st:
            fake_vectors = np.random.randn(3, 128).astype(np.float32)
            mock_instance = MagicMock()
            mock_instance.encode.return_value = fake_vectors
            mock_st.return_value = mock_instance

            from core.retrieval.embeddings.huggingface import HuggingFaceEmbedding
            emb = HuggingFaceEmbedding("test", device="cpu")
            result = emb.encode(["a", "b", "c"])

            assert isinstance(result, np.ndarray)
            assert result.shape == (3, 128)
            assert result.dtype == np.float32


# ─── Reranker rerank contract ────────────────────────────────────────────────

@pytest.mark.unit
class TestRerankerContract:
    def test_rerank_empty_candidates(self):
        """Reranking empty list returns empty list."""
        with patch("core.retrieval.rerankers.cross_encoder.CrossEncoder") as mock_ce:
            mock_ce.return_value = MagicMock()
            from core.retrieval.rerankers.cross_encoder import CrossEncoderReranker
            reranker = CrossEncoderReranker("test", device="cpu")
            result = reranker.rerank("query", [])
            assert result == []

    def test_rerank_orders_by_score_desc(self):
        """Results are returned in descending score order."""
        import numpy as np
        from core.retrieval.stages.state import CatalogItem

        with patch("core.retrieval.rerankers.cross_encoder.CrossEncoder") as mock_ce:
            mock_instance = MagicMock()
            # Scores: item_a=0.1, item_b=0.9, item_c=0.5
            mock_instance.predict.return_value = np.array([0.1, 0.9, 0.5])
            mock_ce.return_value = mock_instance

            from core.retrieval.rerankers.cross_encoder import CrossEncoderReranker
            reranker = CrossEncoderReranker("test", device="cpu")

            items = [
                CatalogItem(item_id="a", title="A", text="text a"),
                CatalogItem(item_id="b", title="B", text="text b"),
                CatalogItem(item_id="c", title="C", text="text c"),
            ]
            ranked = reranker.rerank("query", items)

            assert len(ranked) == 3
            assert ranked[0].item.item_id == "b"  # highest score
            assert ranked[1].item.item_id == "c"
            assert ranked[2].item.item_id == "a"  # lowest score
