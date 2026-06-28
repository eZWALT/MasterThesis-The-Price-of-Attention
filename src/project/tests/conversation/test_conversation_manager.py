"""
Unit tests for ConversationManager — ad injection schedule, retrieval, injection state.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from core.ad_injection.models import Ad, AdRetrievalResult, InjectionResult
from core.conversation.manager import ConversationManager, TurnResult
from core.experiment.tasks import TaskDefinition


def _make_manager(**kwargs) -> ConversationManager:
    defaults = dict(
        ad_mode="inline_persuasive",
        model="test-model",
        temperature=0.7,
        max_tokens=128,
        logger=MagicMock(),
        min_turns=1,
        max_turns=5,
        ad_turns=[1, 3],
        force_ad=False,
        use_rag=False,
    )
    defaults.update(kwargs)
    with patch.object(ConversationManager, "_classify_initial_intent", return_value=""):
        return ConversationManager(**defaults)


@pytest.mark.unit
class TestShouldInjectAd:
    def test_injects_on_configured_turns(self):
        mgr = _make_manager(ad_turns=[2, 4])
        assert mgr.should_inject_ad is False
        mgr.messages.append({"role": "user", "content": "hi"})
        assert mgr.turn_count == 1
        assert mgr.should_inject_ad is False
        mgr.messages.append({"role": "assistant", "content": "hello"})
        mgr.messages.append({"role": "user", "content": "again"})
        assert mgr.turn_count == 2
        assert mgr.should_inject_ad is True

    def test_force_ad_injects_every_turn(self):
        mgr = _make_manager(ad_turns=[99], force_ad=True)
        mgr.messages.append({"role": "user", "content": "first"})
        assert mgr.should_inject_ad is True

    def test_is_ad_turn_predicts_next_turn(self):
        mgr = _make_manager(ad_turns=[1])
        assert mgr.is_ad_turn is True
        mgr.messages.append({"role": "user", "content": "x"})
        assert mgr.is_ad_turn is False


@pytest.mark.unit
class TestProcessUserMessage:
    @patch("core.conversation.manager.get_ad")
    @patch.object(ConversationManager, "_classify_turn_intent", return_value="info")
    def test_stores_last_retrieval_and_injection(
        self, _intent, mock_get_ad, sample_ad_retrieval
    ):
        mock_get_ad.return_value = sample_ad_retrieval

        mgr = _make_manager(force_ad=True, use_rag=False)
        mgr.llm = MagicMock()
        mgr.llm.chat.return_value = "Assistant reply"

        result = mgr.process_user_message("I need headphones")

        assert isinstance(result, TurnResult)
        assert result.assistant_reply == "Assistant reply"
        assert mgr.last_retrieval is sample_ad_retrieval
        assert mgr.last_injection.system_overrides
        mock_get_ad.assert_called_once()
        assert mock_get_ad.call_args.kwargs.get("backend") == "mock"

    @patch("core.conversation.manager.get_ad")
    @patch.object(ConversationManager, "_classify_turn_intent", return_value="info")
    def test_no_injection_when_not_ad_turn(self, _intent, mock_get_ad):
        mgr = _make_manager(ad_turns=[99], force_ad=False)
        mgr.llm = MagicMock()
        mgr.llm.chat.return_value = "ok"

        mgr.process_user_message("hello")

        mock_get_ad.assert_not_called()
        assert mgr.last_retrieval is None
        assert mgr.last_injection == InjectionResult()

    def test_apply_ad_mode_clears_stale_retrieval(self, sample_ad_retrieval):
        mgr = _make_manager(ad_mode="inline_persuasive")
        mgr.last_retrieval = sample_ad_retrieval
        mgr.last_retrieval_ad_mode = "inline_persuasive"

        mgr.apply_ad_mode("explicit_ad_block")

        assert mgr.ad_mode == "explicit_ad_block"
        assert mgr.last_retrieval is None
        assert mgr.last_retrieval_ad_mode is None

    def test_reset_clears_retrieval_state(self, sample_ad_retrieval):
        with patch.object(ConversationManager, "_classify_initial_intent", return_value=""):
            mgr = _make_manager()
        mgr.last_retrieval = sample_ad_retrieval
        mgr.last_injection = InjectionResult(system_overrides=[{"role": "system", "content": "x"}])
        mgr.reset()
        assert mgr.last_retrieval is None
        assert mgr.last_injection == InjectionResult()


class TestAdInfoSnapshot:
    """_injected_ad_info is snapshotted at injection turn and survives later turns."""

    def make_mgr(self, dry_run=False):
        from unittest.mock import MagicMock
        from core.conversation.manager import ConversationManager
        from core.experiment.tasks import TaskDefinition
        mgr = ConversationManager(
            ad_mode="inline_persuasive",
            model="test-model",
            temperature=0.7,
            max_tokens=512,
            task=TaskDefinition(
                id="test", title="T", genre="Transactional",
                participant_prompt="Test prompt.",
                system_prompt_extension="",
            ),
            llm_client=MagicMock(),
            logger=MagicMock(),
            max_turns=5, min_turns=2, finish_from=2,
            use_rag=False, dry_run=dry_run,
        )
        mgr.llm = MagicMock()
        mgr.llm.chat.return_value = "OK."
        return mgr

    def test_snapshot_set_at_injection(self, monkeypatch, sample_ad_retrieval):
        monkeypatch.setattr(
            "core.conversation.manager.get_ad",
            lambda *a, **kw: sample_ad_retrieval,
        )
        mgr = self.make_mgr()
        mgr.process_user_message("hello")
        info = mgr.injected_ad_info
        assert info is not None
        assert info["title"] == "Alpha"

    def test_snapshot_persists_after_later_turns(self, monkeypatch, sample_ad_retrieval):
        from core.ad_injection.models import AdRetrievalResult
        no_ad = AdRetrievalResult(ads=[])
        monkeypatch.setattr(
            "core.conversation.manager.get_ad",
            lambda *a, **kw: no_ad,
        )
        mgr = self.make_mgr()
        with monkeypatch.context() as m:
            m.setattr("core.conversation.manager.get_ad", lambda *a, **kw: sample_ad_retrieval)
            mgr.process_user_message("hello")
        mgr.process_user_message("tell me more")
        info = mgr.injected_ad_info
        assert info is not None
        assert info["title"] == "Alpha"

    def test_clear_resets_snapshot(self, monkeypatch, sample_ad_retrieval):
        monkeypatch.setattr(
            "core.conversation.manager.get_ad",
            lambda *a, **kw: sample_ad_retrieval,
        )
        mgr = self.make_mgr()
        mgr.process_user_message("hello")
        mgr.clear_ad_display_state()
        assert mgr.injected_ad_info is None

    def test_dry_run_does_not_set_snapshot(self, monkeypatch, sample_ad_retrieval):
        monkeypatch.setattr(
            "core.conversation.manager.get_ad",
            lambda *a, **kw: sample_ad_retrieval,
        )
        mgr = self.make_mgr(dry_run=True)
        mgr.process_user_message("hello")
        assert mgr.injected_ad_info is None
