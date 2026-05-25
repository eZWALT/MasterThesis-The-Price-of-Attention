"""
Unit tests for baseline screen helpers and config alignment.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.config import (
    BASELINE_COMPLETE_MESSAGE,
    BASELINE_CONTINUE_LABEL,
    BASELINE_DURATION_SECONDS,
    BASELINE_INSTRUCTION,
    BASELINE_TITLE,
)
from core.ui.screens import (
    _BASELINE_SESSION_KEYS,
    _format_duration_label,
    clear_baseline_session_state,
)


@pytest.mark.unit
class TestFormatDurationLabel:
    @pytest.mark.parametrize(
        "seconds, expected_fragment",
        [
            (1, "1 second"),
            (2, "2 seconds"),
            (45, "45 seconds"),
            (60, "1 minute"),
            (120, "2 minutes"),
            (90, "1 minute and 30 seconds"),
            (61, "1 minute and 1 second"),
        ],
    )
    def test_human_readable_durations(self, seconds, expected_fragment):
        label = _format_duration_label(seconds)
        assert expected_fragment in label

    def test_instruction_uses_config_duration_not_hardcoded_two_minutes(self):
        label = _format_duration_label(BASELINE_DURATION_SECONDS)
        text = BASELINE_INSTRUCTION.format(duration_label=label)
        assert "2 minutes" not in text or BASELINE_DURATION_SECONDS == 120
        assert label in text


@pytest.mark.unit
class TestBaselineConfig:
    def test_baseline_constants_are_non_empty(self):
        assert BASELINE_TITLE
        assert "{duration_label}" in BASELINE_INSTRUCTION
        assert BASELINE_COMPLETE_MESSAGE
        assert BASELINE_CONTINUE_LABEL
        assert BASELINE_DURATION_SECONDS > 0


@pytest.mark.unit
class TestClearBaselineSessionState:
    def test_clears_all_baseline_keys(self, monkeypatch):
        fake_state = {
            "baseline_start": 123.0,
            "_baseline_screen_active": True,
            "_baseline_user_confirmed": True,
            "unrelated": "keep",
        }

        class SessionState(dict):
            def pop(self, key, default=None):
                return super().pop(key, default)

        session = SessionState(fake_state)
        monkeypatch.setattr("streamlit.session_state", session)

        clear_baseline_session_state()

        for key in _BASELINE_SESSION_KEYS:
            assert key not in session
        assert session["unrelated"] == "keep"

    def test_render_baseline_returns_true_after_confirmation_flag(self, monkeypatch):
        """After user confirms, next call short-circuits without Streamlit UI."""
        session = {"_baseline_user_confirmed": True}
        monkeypatch.setattr("streamlit.session_state", session)
        monkeypatch.setattr("streamlit.header", MagicMock())
        monkeypatch.setattr("streamlit.markdown", MagicMock())
        monkeypatch.setattr("streamlit.fragment", lambda **kwargs: (lambda fn: fn))

        from core.ui.screens import render_baseline

        assert render_baseline() is True
        assert "_baseline_user_confirmed" not in session
