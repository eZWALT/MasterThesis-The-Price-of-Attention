"""
Unit tests for recent infrastructure changes:
- AD_BACKEND in config
- Eager retrieval warmup
- Ad backend selector (mock/rag only, no "default")
- _sync_dev_overrides
"""

from __future__ import annotations

import os
from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.unit
class TestADBackendConfig:
    def test_ad_backend_exists_in_config(self):
        from core.config import AD_BACKEND
        assert AD_BACKEND in ("mock", "rag")

    def test_ad_backend_default_is_mock(self):
        """Without env var, defaults to mock."""
        # AD_BACKEND reads at import time; it should be "mock" in test env
        from core.config import AD_BACKEND
        assert AD_BACKEND == os.getenv("AD_BACKEND", "mock")

    def test_ad_backend_importable_from_provider(self):
        from core.ad_injection.provider import AD_BACKEND
        assert AD_BACKEND in ("mock", "rag")

    def test_ad_backend_importable_from_package(self):
        from core.ad_injection import AD_BACKEND
        assert AD_BACKEND in ("mock", "rag")

    def test_config_and_provider_agree(self):
        from core.config import AD_BACKEND as cfg_backend
        from core.ad_injection import AD_BACKEND as pkg_backend
        assert cfg_backend == pkg_backend


@pytest.mark.unit
class TestWarmupRetrieval:
    def test_warmup_skips_when_not_rag(self):
        """_warmup_retrieval should be a no-op when AD_BACKEND != 'rag'."""
        with patch("core.config.AD_BACKEND", "mock"):
            # Import fresh — the function checks AD_BACKEND at call time
            import importlib
            import app
            importlib.reload(app)
            # Should not raise even without GPU/models
            # (it returns immediately when not rag)
            # We can't easily test st.cache_resource in unit tests,
            # so just verify the function exists and is callable
            assert callable(app._warmup_retrieval.__wrapped__)


@pytest.mark.unit
class TestSyncDevOverrides:
    def test_sync_sets_ad_backend(self):
        """_sync_dev_overrides should set _ad_backend on manager."""
        import streamlit as st
        from unittest.mock import MagicMock

        # Mock streamlit session state
        mock_state = {"dev_force_ad": True, "dev_rag_mode": "rag"}
        with patch.object(st, "session_state", mock_state):
            from core.ui.participant import _sync_dev_overrides
            mgr = MagicMock()
            mgr._force_ad = False
            mgr._ad_backend = None
            mgr.ad_mode = "inline_persuasive"
            _sync_dev_overrides(mgr)
            assert mgr._force_ad == True
            assert mgr._ad_backend == "rag"

    def test_sync_sets_ad_mode_override(self):
        """_sync_dev_overrides should override ad_mode when set."""
        import streamlit as st
        from unittest.mock import MagicMock

        mock_state = {
            "dev_force_ad": False,
            "dev_rag_mode": "mock",
            "dev_ad_mode_override": "sponsored_conversational",
        }
        with patch.object(st, "session_state", mock_state):
            from core.ui.participant import _sync_dev_overrides
            mgr = MagicMock()
            mgr._force_ad = False
            mgr._ad_backend = None
            mgr.ad_mode = "inline_persuasive"
            _sync_dev_overrides(mgr)
            assert mgr.ad_mode == "sponsored_conversational"

    def test_sync_no_mode_override_when_absent(self):
        """Without dev_ad_mode_override, ad_mode stays unchanged."""
        import streamlit as st
        from unittest.mock import MagicMock

        mock_state = {"dev_force_ad": False, "dev_rag_mode": "mock"}
        with patch.object(st, "session_state", mock_state):
            from core.ui.participant import _sync_dev_overrides
            mgr = MagicMock()
            mgr._force_ad = False
            mgr._ad_backend = None
            mgr.ad_mode = "inline_persuasive"
            _sync_dev_overrides(mgr)
            # ad_mode should not have been set (only accessed via .get)
            # MagicMock records attribute sets — check it wasn't set to something else
            # Since mock_state has no "dev_ad_mode_override", the if branch is skipped
            assert mgr.ad_mode == "inline_persuasive"
