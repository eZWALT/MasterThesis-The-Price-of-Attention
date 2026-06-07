"""
Unit tests for dev=flow participant helpers — ad overrides and manager wiring.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from core.experiment.tasks import TASK_BY_ID


def _fake_session_state(**kwargs):
    """Dict that supports both attribute and key access like Streamlit."""

    class SessionState(dict):
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError as exc:
                raise AttributeError(key) from exc

        def __setattr__(self, key, value):
            self[key] = value

    return SessionState(kwargs)


@pytest.mark.unit
class TestResolveDevAdSettings:
    def _session(self, monkeypatch, **kwargs):
        session = _fake_session_state(**kwargs)
        monkeypatch.setattr("streamlit.session_state", session)
        return session

    def test_reads_force_ad_and_rag_from_session(self, monkeypatch):
        from core.ui.participant import _resolve_dev_ad_settings

        self._session(monkeypatch, dev_force_ad=False, dev_rag_mode="mock", dev_ad_mode_override="explicit_ad_block")
        params = SimpleNamespace(force_ad=True, use_rag=True)
        force_ad, use_rag, mode = _resolve_dev_ad_settings(params)
        assert force_ad is False
        assert use_rag is False
        assert mode == "explicit_ad_block"

    def test_falls_back_to_params_when_session_keys_missing(self, monkeypatch):
        from core.ui.participant import _resolve_dev_ad_settings

        self._session(monkeypatch)
        params = SimpleNamespace(force_ad=True, use_rag=None)
        force_ad, use_rag, mode = _resolve_dev_ad_settings(params)
        assert force_ad is True
        assert use_rag is None
        assert mode == ""


@pytest.mark.unit
class TestSyncDevOverrides:
    def test_sync_updates_manager_private_fields(self, monkeypatch):
        from core.ui.participant import _sync_dev_overrides

        monkeypatch.setattr(
            "streamlit.session_state",
            _fake_session_state(
                dev_force_ad=True,
                dev_rag_mode="mock",
                dev_ad_mode_override="sponsored_conversational",
            ),
        )
        mgr = MagicMock()
        mgr._force_ad = False
        mgr._ad_backend = None
        mgr.ad_mode = "inline_persuasive"

        _sync_dev_overrides(mgr)

        assert mgr._force_ad is True
        assert mgr._ad_backend == "mock"


@pytest.mark.unit
class TestGetOrCreateTrialManager:
    def test_keeps_manager_and_clears_ads_when_mode_changes_in_flow(self, monkeypatch):
        from core.ui.participant import _get_or_create_trial_manager

        task = TASK_BY_ID["swt_dev_role_setup"]
        logger = MagicMock()
        ctrl = MagicMock()
        ctrl.model = "test"
        ctrl.turns_min = 1
        ctrl.turns_max = 5
        ctrl.ad_turns = [1]

        old_mgr = MagicMock()
        old_mgr.task.id = task.id
        old_mgr.ad_mode = "inline_persuasive"
        old_mgr.messages = [{"role": "user", "content": "fishing"}]

        monkeypatch.setattr(
            "streamlit.session_state",
            _fake_session_state(
                trial_manager=old_mgr,
                controller=ctrl,
                logger=logger,
                dev_force_ad=True,
                dev_rag_mode="mock",
                dev_ad_mode_override="explicit_ad_block",
            ),
        )

        params = SimpleNamespace(force_ad=True, use_rag=False)
        with patch("core.ui.participant.ConversationManager") as MockCM:
            mgr = _get_or_create_trial_manager(task, "inline_persuasive", params, flow_test=True)
            MockCM.assert_not_called()
            old_mgr.apply_ad_mode.assert_called_once_with("explicit_ad_block")
            assert mgr is old_mgr
            assert mgr.messages == [{"role": "user", "content": "fishing"}]
