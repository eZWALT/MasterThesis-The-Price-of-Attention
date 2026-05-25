"""
Test configuration and shared fixtures.

Run tests:
    cd src/project
    pytest                     # unit tests only (fast)
    pytest -m e2e              # E2E tests only (loads models, needs GPU)
    pytest -m "unit or e2e"    # everything
"""

from __future__ import annotations

import os
import sys
from unittest.mock import patch

import pytest

# Ensure project root is importable.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def force_cpu(monkeypatch):
    """Force all device allocation to CPU — useful for CI without GPU."""
    monkeypatch.setenv("FORCE_CPU", "1")


@pytest.fixture
def mock_vram():
    """
    Mock get_free_vram to simulate a 2-GPU system with known free VRAM.
    GPU 0: 24 GB free, GPU 1: 35 GB free.
    """
    fake_vram = {
        0: int(24 * 1024**3),
        1: int(35 * 1024**3),
    }
    with patch("core.device.get_free_vram", return_value=fake_vram):
        yield fake_vram


@pytest.fixture
def reset_reservations():
    """Reset the device module's internal GPU reservations between tests."""
    import core.device
    core.device._gpu_reservations.clear()
    yield
    core.device._gpu_reservations.clear()


@pytest.fixture
def fake_streamlit_session():
    """Reusable Streamlit session_state stand-in for UI unit tests."""

    class SessionState(dict):
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError as exc:
                raise AttributeError(key) from exc

        def __setattr__(self, key, value):
            self[key] = value

        def pop(self, key, default=None):
            return super().pop(key, default)

    return SessionState()


@pytest.fixture
def sample_ad_retrieval():
    from core.ad_injection.models import Ad, AdRetrievalResult

    return AdRetrievalResult(
        ads=[
            Ad(title="Alpha", text="First", source_item_id="a", relevance_score=0.9),
            Ad(title="Beta", text="Second", source_item_id="b", relevance_score=0.8),
        ]
    )
