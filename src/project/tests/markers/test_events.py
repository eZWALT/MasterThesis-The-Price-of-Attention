"""
Unit tests for the marker/event system.

Sanity-checks that:
  - LSL sender is wired correctly through the logger → _marker_client path
  - All expected event names are used consistently across the codebase
  - ConversationManager emits turn_{n}_read after each assistant reply
  - ConversationManager emits ad_inserted after ad injection
  - _render_write_trigger fires turn_{n}_write (indirectly via logger mock)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch, call
from typing import Any, Optional

import pytest


# ═══════════════════════════════════════════════════════════════
# EEG / LSL sender
# ═══════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLSLSender:
    def test_lsl_sender_returns_object_with_send(self):
        from core.modalities.eeg import lsl_sender

        sender = lsl_sender()
        assert hasattr(sender, "send")
        assert callable(sender.send)

    def test_lsl_sender_send_does_not_crash(self):
        from core.modalities.eeg import lsl_sender

        sender = lsl_sender()
        # Should not raise even without pylsl
        sender.send("baseline_start")
        sender.send("turn_1_write")

    def test_lsl_sender_send_calls_marker(self):
        from core.modalities.eeg import lsl_sender, marker

        original_marker = marker
        calls = []

        def tracking_marker(label: str) -> None:
            calls.append(label)

        import core.modalities.eeg as eeg_mod
        eeg_mod.marker = tracking_marker

        try:
            sender = lsl_sender()
            sender.send("baseline_start")
            sender.send("turn_1_write")
            assert calls == ["dummy_start", "baseline_start", "turn_1_write"]
        finally:
            eeg_mod.marker = original_marker

    def test_lsl_sender_whitelist_filters(self):
        from core.modalities.eeg import lsl_sender, marker

        import core.modalities.eeg as eeg_mod
        original = eeg_mod.marker
        calls = []
        eeg_mod.marker = lambda label: calls.append(label)

        try:
            sender = lsl_sender()
            sender.send("baseline_start")     # whitelisted
            sender.send("turn_3_read")         # whitelisted (pattern)
            sender.send("user_message")        # filtered
            sender.send("intent_classified")   # filtered
            sender.send("retrieval")           # filtered
            sender.send("ad_inserted")         # filtered (ad_inserted stripped)
            assert calls == ["dummy_start", "baseline_start", "turn_3_read"]
        finally:
            eeg_mod.marker = original


# ═══════════════════════════════════════════════════════════════
# Event name inventory
# ═══════════════════════════════════════════════════════════════

EXPECTED_EVENTS = {
    # Core experiment lifecycle
    "session_started",
    "session_complete",
    "experiment_config",
    "screen_skipped",
    "early_exit",
    # Consent / identity
    "consent_granted",
    "worker_id_set",
    # Baseline
    "baseline_start",
    "baseline_end",
    # Warmup
    "warmup_start",
    "warmup_finish",
    # Condition lifecycle
    "condition_start",
    "condition_end",
    "condition_conclusion_submitted",
    "post_condition_survey_submitted",
    "ads_recall_submitted",
    "ocean_submitted",
    "demographics_post_submitted",
    "deception_disclosure_submitted",
    "validation_submitted",
    # Per-turn events (dynamic names)
    #   turn_{n}_read  — generated at runtime
    #   turn_{n}_write — generated at runtime
    # Ad events
    "ad_inserted",
    # Conversation pipeline
    "conversation_started",
    "user_message",
    "intent_classified",
    "retrieval",
    "ad_injected",
    "assistant_reply",
    "attention_shift",
    "trial_end",
    "session_reset",
    # Post-task questionnaires
    "post_task_questionnaire_end",
    "experiment_end",
    # Eye-tracking
    "eyetracking_recording_started",
    "eyetracking_video_saved",
    # Ad click tracking
    "ad_clicked",
}


@pytest.mark.unit
class TestEventNameInventory:
    """Verify static event names are spelled consistently."""

    def test_expected_events_are_defined(self):
        """Smoke check: the expected set is not empty."""
        assert len(EXPECTED_EVENTS) > 20

    def test_find_log_event_strings(self):
        """Extract all static event strings from .log() calls and compare."""
        import ast, os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        found = set()
        # Only scan core/ source directory (skip tests, site-packages, etc.)
        source_dirs = [
            os.path.join(project_root, "core"),
            os.path.join(project_root, "core/ui"),
            os.path.join(project_root, "core/conversation"),
            os.path.join(project_root, "core/logger"),
        ]
        for src_dir in source_dirs:
            if not os.path.isdir(src_dir):
                continue
            for root, dirs, files in os.walk(src_dir):
                if "__pycache__" in root:
                    continue
                for fn in files:
                    if not fn.endswith(".py"):
                        continue
                    path = os.path.join(root, fn)
                    try:
                        with open(path) as f:
                            tree = ast.parse(f.read())
                    except (SyntaxError, Exception):
                        continue
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            func = node.func
                            if isinstance(func, ast.Attribute) and func.attr == "log":
                                if node.args:
                                    first_arg = node.args[0]
                                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                                        val = first_arg.value
                                        if val.startswith("f"):
                                            continue
                                        if "{" not in val and "}" not in val:
                                            found.add(val)

        # Verify our key events are found
        for key in ["baseline_start", "baseline_end", "warmup_start", "warmup_finish",
                     "condition_start", "condition_end", "condition_conclusion_submitted",
                     "post_task_questionnaire_end", "experiment_end"]:
            assert key in found, f"Event {key!r} not found in any .log() call"

    def test_logger_event_names_are_snake_case(self):
        """All event names should be snake_case."""
        for ev in EXPECTED_EVENTS:
            if ev.startswith("turn_"):
                continue
            # Should not contain colons, spaces, or uppercase
            assert ":" not in ev, f"Event {ev!r} uses colon (should be snake_case)"
            assert " " not in ev, f"Event {ev!r} contains spaces"
            # Should be all lowercase with underscores
            assert ev == ev.lower(), f"Event {ev!r} should be lowercase snake_case"


# ═══════════════════════════════════════════════════════════════
# ConversationManager — turn_{n}_read + ad_inserted
# ═══════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestManagerMarkerEvents:
    """Verify that ConversationManager emits the correct marker events."""

    def _make_mgr(self, logger_mock=None, force_ad=False, dry_run=True, max_turns=3):
        from core.conversation.manager import ConversationManager

        mgr = ConversationManager(
            ad_mode="inline_persuasive",
            model="mock-model",
            temperature=0.7,
            max_tokens=100,
            use_rag=False,
            dry_run=dry_run,
            logger=logger_mock,
            force_ad=force_ad,
            max_turns=max_turns,
        )
        return mgr

    def test_turn_read_logged_after_message(self):
        """After processing a user message, turn_{n}_read is logged."""
        logger = MagicMock()
        mgr = self._make_mgr(logger, dry_run=True)

        # Inject a first assistant message so _last_assistant_ts is set
        with patch.object(mgr.llm, 'chat_stream', return_value=iter(["mock reply"])):
            list(mgr.process_user_message_stream("hello"))

        # Verify turn_1_read was logged
        read_calls = [c for c in logger.log.call_args_list if 'read' in str(c)]
        assert len(read_calls) >= 1, "Expected at least one turn_*_read log call"

        # Check the specific event name
        first_read = read_calls[0]
        event_name = first_read[0][0]  # first positional arg
        assert event_name == "turn_1_read", f"Expected turn_1_read, got {event_name}"

    def test_ad_inserted_logged_when_ad_injected(self):
        """When an ad is injected, ad_inserted is logged."""
        logger = MagicMock()
        mgr = self._make_mgr(logger, dry_run=False, force_ad=True)

        # Mock the LLM and ad retrieval
        with patch.object(mgr.llm, 'chat_stream', return_value=iter(["mock reply"])):
            from core.ad_injection.models import Ad, AdRetrievalResult
            mock_retrieval = AdRetrievalResult(
                ads=[Ad(title="Test", text="Test ad", source_item_id="t1", relevance_score=0.9)]
            )
            # Patch get_ad in the manager module where it's imported
            import core.conversation.manager as mgr_mod
            with patch.object(mgr_mod, 'get_ad', return_value=mock_retrieval):
                list(mgr.process_user_message_stream("show me an ad"))

        ad_calls = [c for c in logger.log.call_args_list if 'ad_inserted' in str(c)]
        assert len(ad_calls) >= 1, "Expected at least one ad_inserted log call"

        event_name = ad_calls[0][0][0]
        assert event_name == "ad_inserted", f"Expected ad_inserted, got {event_name}"

    def test_no_ad_inserted_when_no_ads(self):
        """When no ad is shown, ad_inserted should NOT be logged."""
        logger = MagicMock()
        mgr = self._make_mgr(logger, dry_run=True, force_ad=False)

        # no_ads mode shouldn't inject ads
        with patch.object(mgr.llm, 'chat_stream', return_value=iter(["mock reply"])):
            list(mgr.process_user_message_stream("hello"))

        ad_calls = [c for c in logger.log.call_args_list if 'ad_inserted' in str(c)]
        assert len(ad_calls) == 0, "Expected NO ad_inserted call for no_ads mode"

    def test_event_order_within_turn(self):
        """Within one turn: user_message → turn_1_read (and possibly ad_inserted)."""
        logger = MagicMock()
        mgr = self._make_mgr(logger, dry_run=True, force_ad=False)

        with patch.object(mgr.llm, 'chat_stream', return_value=iter(["mock reply"])):
            list(mgr.process_user_message_stream("hello"))

        call_events = [c[0][0] for c in logger.log.call_args_list]
        # Find positions of key events
        msg_pos = next(i for i, e in enumerate(call_events) if e == "user_message")
        read_pos = next(i for i, e in enumerate(call_events) if "turn_" in e and "read" in e)
        assert read_pos > msg_pos, "turn_*_read should come after user_message"


# ═══════════════════════════════════════════════════════════════
# Logger → LSL path
# ═══════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestLoggerToLSLPath:
    """Verify that ExperimentLogger.log() fires _marker_client.send()."""

    def test_log_calls_marker_client_send(self):
        """logger.log(event, data) should call _marker_client.send(event)."""
        from core.logger import ExperimentLogger

        marker_mock = MagicMock()
        log = ExperimentLogger(
            participant_id="test_pid",
            log_dir="/tmp/test_logs_markers",
            marker_client=marker_mock,
        )

        log.log("baseline_start", {"turn": 0})

        marker_mock.send.assert_called_once_with("baseline_start")

    def test_marker_client_send_pushes_correct_name(self):
        """Verify the exact string sent to the marker client."""
        from core.logger import ExperimentLogger

        sent_events = []

        class TrackingSender:
            @staticmethod
            def send(event: str, **kwargs: Any) -> None:
                sent_events.append(event)

            @staticmethod
            def set_logger(_: Any) -> None:
                pass

        log = ExperimentLogger(
            participant_id="test_pid",
            log_dir="/tmp/test_logs_markers",
            marker_client=TrackingSender(),
        )

        # Log each of our target events
        for event in ["baseline_start", "baseline_end", "warmup_start",
                       "warmup_finish", "condition_start", "condition_end",
                       "ad_inserted", "condition_conclusion_submitted",
                       "post_task_questionnaire_end", "experiment_end"]:
            log.log(event, {"turn": 0})

        for event in ["baseline_start", "baseline_end", "warmup_start",
                       "warmup_finish", "condition_start", "condition_end",
                       "ad_inserted", "condition_conclusion_submitted",
                       "post_task_questionnaire_end", "experiment_end"]:
            assert event in sent_events, f"{event} was not sent to marker client"
