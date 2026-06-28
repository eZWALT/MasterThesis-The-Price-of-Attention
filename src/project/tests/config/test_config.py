"""
Unit tests for core.config — validates config loads without error and
has sane defaults.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestConfigLoads:
    def test_import_succeeds(self):
        """Config module imports without error."""
        import core.config  # noqa: F401

    def test_embedding_model_is_set(self):
        import core.config as cfg
        assert cfg.EMBEDDING_MODEL_NAME
        assert "Embedding" in cfg.EMBEDDING_MODEL_NAME or "embedding" in cfg.EMBEDDING_MODEL_NAME.lower()

    def test_reranker_model_is_set(self):
        import core.config as cfg
        assert cfg.RERANKER_MODEL_NAME
        name = cfg.RERANKER_MODEL_NAME.lower()
        assert "reranker" in name or "cross-encoder" in name or "ms-marco" in name

    def test_dtype_is_valid(self):
        import core.config as cfg
        valid = {"float32", "fp32", "float16", "fp16", "bfloat16", "bf16"}
        assert cfg.EMBEDDING_DTYPE in valid
        assert cfg.RERANKER_DTYPE in valid

    def test_device_strings_are_valid(self):
        import core.config as cfg
        for device in [cfg.INTENT_DEVICE, cfg.EMBEDDING_DEVICE, cfg.RERANKER_DEVICE]:
            assert device == "cpu" or device.startswith("cuda:")

    def test_catalog_path_exists(self):
        import core.config as cfg
        # Relative path resolved from project root
        proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(proj, cfg.CATALOG_PATH)
        assert os.path.exists(path), f"Catalog not found at {path}"

    def test_faiss_index_path_exists(self):
        import core.config as cfg
        proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(proj, cfg.FAISS_INDEX_PATH)
        assert os.path.exists(path), f"FAISS index not found at {path}"


@pytest.mark.unit
class TestConfigEnvOverrides:
    def test_force_cpu_propagates(self):
        """FORCE_CPU=1 makes all devices cpu."""
        # We can't easily re-import config, so test device module directly.
        with patch.dict(os.environ, {"FORCE_CPU": "1"}):
            # Re-evaluate
            import core.device
            import importlib
            importlib.reload(core.device)
            assert core.device.FORCE_CPU is True
            # Restore
            importlib.reload(core.device)

    def test_llm_gpu_indices_parsed(self):
        with patch.dict(os.environ, {"LLM_GPU_INDICES": "0,2"}):
            import core.device
            import importlib
            importlib.reload(core.device)
            assert core.device.LLM_GPU_INDICES == {0, 2}
            # Restore
            importlib.reload(core.device)


@pytest.mark.unit
class TestConfigConstants:
    def test_ad_modes_non_empty(self):
        import core.config as cfg
        assert len(cfg.AD_MODES) >= 2

    def test_dense_top_k_positive(self):
        import core.config as cfg
        assert cfg.DENSE_TOP_K > 0

    def test_reranker_top_k_less_than_dense(self):
        import core.config as cfg
        assert cfg.RERANKER_TOP_K <= cfg.DENSE_TOP_K

    def test_temperature_range(self):
        import core.config as cfg
        assert 0.0 <= cfg.DEFAULT_TEMPERATURE <= 1.0

    def test_retrieval_final_top_n_positive(self):
        import core.config as cfg
        assert cfg.RETRIEVAL_FINAL_TOP_N >= 1

    def test_baseline_duration_positive(self):
        import core.config as cfg
        assert cfg.BASELINE_DURATION_SECONDS > 0
        assert "{duration_label}" in cfg.BASELINE_INSTRUCTION
