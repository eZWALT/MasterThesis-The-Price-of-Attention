"""
Unit tests for core.device — GPU/CPU allocation logic.

These run fully mocked (no real GPU needed) and test the decision logic.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from core.device import allocate_device, estimate_vram, VRAM_ESTIMATES


# ─── estimate_vram ────────────────────────────────────────────────────────────

class TestEstimateVram:
    @pytest.mark.unit
    @pytest.mark.parametrize("model,expected", [
        ("Qwen/Qwen3-Embedding-4B", 10.0),
        ("Qwen/Qwen3-Embedding-0.6B", 2.0),
        ("Qwen/Qwen3-Reranker-4B", 10.0),
        ("Qwen/Qwen3-Reranker-0.6B", 2.0),
        ("intent-bert", 0.5),
    ])
    def test_known_model(self, model, expected):
        assert estimate_vram(model) == expected

    @pytest.mark.unit
    @pytest.mark.parametrize("model", [
        "some/unknown-model-999B",
        "facebook/opt-125m",
        "",
    ])
    def test_unknown_model_returns_default(self, model):
        assert estimate_vram(model) == 4.0  # _DEFAULT_VRAM_ESTIMATE_GB

    @pytest.mark.unit
    @pytest.mark.parametrize("model,vram", list(VRAM_ESTIMATES.items()))
    def test_all_known_models_have_positive_values(self, model, vram):
        assert vram > 0, f"{model} has non-positive VRAM estimate"


# ─── allocate_device — CPU fallback paths ─────────────────────────────────────

class TestAllocateDeviceCPUFallback:
    @pytest.mark.unit
    def test_force_cpu_env(self, reset_reservations):
        """FORCE_CPU=1 → always returns cpu."""
        with patch("core.device.FORCE_CPU", True):
            result = allocate_device("Qwen/Qwen3-Embedding-4B", role="test")
            assert result == "cpu"

    @pytest.mark.unit
    @pytest.mark.parametrize("model_name", [
        "intent-bert",
        "Qwen/Qwen3-Embedding-4B",
        "any-model",
    ])
    def test_preferred_cpu_respected(self, reset_reservations, model_name):
        """When preferred='cpu', skip GPU even if available."""
        result = allocate_device(model_name, preferred="cpu", role="test")
        assert result == "cpu"

    @pytest.mark.unit
    def test_no_torch_falls_back(self, reset_reservations):
        """If torch is not importable, fall back to CPU."""
        with patch("core.device.FORCE_CPU", False), \
             patch.dict("sys.modules", {"torch": None}):
            import builtins
            real_import = builtins.__import__

            def mock_import(name, *args, **kwargs):
                if name == "torch":
                    raise ImportError("mocked")
                return real_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                result = allocate_device("Qwen/Qwen3-Embedding-4B", role="test")
                assert result == "cpu"

    @pytest.mark.unit
    def test_no_gpus_available(self, reset_reservations):
        """Empty free_map → CPU."""
        with patch("core.device.FORCE_CPU", False), \
             patch("core.device.get_free_vram", return_value={}):
            result = allocate_device("Qwen/Qwen3-Embedding-4B", role="test")
            assert result == "cpu"


# ─── allocate_device — GPU selection logic ────────────────────────────────────

class TestAllocateDeviceGPU:
    @pytest.mark.unit
    @pytest.mark.parametrize("preferred,free_map,expected", [
        # Preferred GPU has enough → use it
        ("cuda:1", {0: 30, 1: 35}, "cuda:1"),
        ("cuda:0", {0: 30, 1: 35}, "cuda:0"),
        # Preferred doesn't have enough → fall to best alternative
        ("cuda:1", {0: 20, 1: 8}, "cuda:0"),
        # Only one GPU with enough
        ("cuda:0", {0: 5, 1: 20}, "cuda:1"),
    ], ids=["preferred_ok", "preferred_other_ok", "preferred_too_small", "only_gpu1_fits"])
    def test_gpu_selection(self, reset_reservations, preferred, free_map, expected):
        fake = {k: int(v * 1024**3) for k, v in free_map.items()}
        with patch("core.device.FORCE_CPU", False), \
             patch("core.device.get_free_vram", return_value=fake):
            result = allocate_device(
                "Qwen/Qwen3-Embedding-4B",  # needs 10 GB + 10% margin
                preferred=preferred,
                role="test",
            )
            assert result == expected

    @pytest.mark.unit
    @pytest.mark.parametrize("exclude,expected", [
        ({1}, "cuda:0"),
        ({0}, "cuda:1"),
        ({0, 1}, "cpu"),
    ], ids=["exclude_1", "exclude_0", "exclude_all"])
    def test_exclude_gpus(self, reset_reservations, exclude, expected):
        fake = {0: int(30 * 1024**3), 1: int(35 * 1024**3)}
        with patch("core.device.FORCE_CPU", False), \
             patch("core.device.get_free_vram", return_value=fake):
            result = allocate_device(
                "Qwen/Qwen3-Embedding-4B",
                preferred="cuda:1",
                role="test",
                exclude_gpus=exclude,
            )
            assert result == expected

    @pytest.mark.unit
    @pytest.mark.parametrize("free_gb", [5, 8, 10])
    def test_insufficient_vram_falls_to_cpu(self, reset_reservations, free_gb):
        """10 GB model + 10% margin = 11 GB needed; anything less → CPU."""
        fake = {0: int(free_gb * 1024**3)}
        with patch("core.device.FORCE_CPU", False), \
             patch("core.device.get_free_vram", return_value=fake):
            result = allocate_device("Qwen/Qwen3-Embedding-4B", preferred="cuda:0", role="test")
            assert result == "cpu"


# ─── Reservation tracking ────────────────────────────────────────────────────

class TestReservationTracking:
    @pytest.mark.unit
    @pytest.mark.parametrize("total_gb,n_models,expected_last", [
        (25, 2, "cuda:1"),   # 25 GB fits two 10 GB models (10+10 < 25 with margin)
        (25, 3, "cpu"),      # third doesn't fit
        (40, 3, "cuda:1"),   # 40 GB fits three
    ], ids=["two_fit", "three_overflow", "three_fit_40gb"])
    def test_sequential_reservations(self, reset_reservations, total_gb, n_models, expected_last):
        import core.device
        result = None
        for i in range(n_models):
            reserved = core.device._gpu_reservations.get(1, 0)
            fake = {1: int(total_gb * 1024**3) - reserved}
            with patch("core.device.FORCE_CPU", False), \
                 patch("core.device.get_free_vram", return_value=fake):
                result = allocate_device(
                    "Qwen/Qwen3-Embedding-4B", preferred="cuda:1", role=f"model_{i}"
                )
        assert result == expected_last


# ─── Override via required_vram_gb ────────────────────────────────────────────

class TestVramOverride:
    @pytest.mark.unit
    @pytest.mark.parametrize("override_gb,free_gb,expected", [
        (2.0, 5.0, "cuda:0"),   # override fits
        (2.0, 1.0, "cpu"),      # override still too big
        (0.5, 1.0, "cuda:0"),   # tiny model fits
    ], ids=["override_fits", "override_too_big", "tiny_fits"])
    def test_explicit_vram_overrides_table(self, reset_reservations, override_gb, free_gb, expected):
        fake = {0: int(free_gb * 1024**3)}
        with patch("core.device.FORCE_CPU", False), \
             patch("core.device.get_free_vram", return_value=fake):
            result = allocate_device(
                "Qwen/Qwen3-Embedding-4B",
                preferred="cuda:0",
                role="test",
                required_vram_gb=override_gb,
            )
            assert result == expected
