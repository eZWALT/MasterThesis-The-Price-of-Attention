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
    @patch("core.conversation.manager.compute_attention_shift")
    @patch("core.conversation.manager.get_ad")
    @patch.object(ConversationManager, "_classify_turn_intent", return_value="info")
    def test_stores_last_retrieval_and_injection(
        self, _intent, mock_get_ad, mock_shift, sample_ad_retrieval
    ):
        mock_get_ad.return_value = sample_ad_retrieval
        mock_shift.return_value = MagicMock(divergence=0.1, method="jsd")

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

    @patch("core.conversation.manager.compute_attention_shift")
    @patch("core.conversation.manager.get_ad")
    @patch.object(ConversationManager, "_classify_turn_intent", return_value="info")
    def test_sponsored_recommendation_appends_chat_message(
        self, _intent, mock_get_ad, mock_shift, sample_ad_retrieval
    ):
        mock_get_ad.return_value = sample_ad_retrieval
        mock_shift.return_value = MagicMock(divergence=0.0, method="jsd")
        mgr = _make_manager(ad_mode="sponsored_recommendation", force_ad=True, use_rag=False)
        mgr.llm = MagicMock()
        mgr.llm.chat.return_value = "Main reply"

        mgr.process_user_message("buy shoes")

        roles = [m["role"] for m in mgr.messages]
        assert roles.count("assistant") >= 2
        sponsored = [m for m in mgr.messages if m["role"] == "assistant" and "Sponsored" in m["content"]]
        assert len(sponsored) == 1

    @patch("core.conversation.manager.compute_attention_shift")
    @patch("core.conversation.manager.get_ad")
    @patch.object(ConversationManager, "_classify_turn_intent", return_value="info")
    def test_no_injection_when_not_ad_turn(self, _intent, mock_get_ad, mock_shift):
        mock_shift.return_value = MagicMock(divergence=0.0, method="jsd")
        mgr = _make_manager(ad_turns=[99], force_ad=False)
        mgr.llm = MagicMock()
        mgr.llm.chat.return_value = "ok"

        mgr.process_user_message("hello")

        mock_get_ad.assert_not_called()
        assert mgr.last_retrieval is None
        assert mgr.last_injection == InjectionResult()

    def test_reset_clears_retrieval_state(self, sample_ad_retrieval):
        with patch.object(ConversationManager, "_classify_initial_intent", return_value=""):
            mgr = _make_manager()
        mgr.last_retrieval = sample_ad_retrieval
        mgr.last_injection = InjectionResult(system_overrides=[{"role": "system", "content": "x"}])
        mgr.reset()
        assert mgr.last_retrieval is None
        assert mgr.last_injection == InjectionResult()
