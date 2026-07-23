"""
EEG integration — Lab Stream Layer (LSL) markers for time-locking.

Marker protocol
---------------
All markers are plain strings pushed as a single-channel sample.
Naming convention:  `domain:value[:sub_value]`

  session:start
  session:end

  screen:{screen_name}             — entering a screen

  condition:{id}:start
  condition:{id}:end
  condition:{id}:ad_mode:{mode}

  baseline:start
  baseline:end

  turn:{n}                         — after assistant reply at turn n
  ad_injected:{n}                  — ad injection at turn n

  survey:{type}:submitted

Usage from participant.py:
    from core.modalities.eeg import marker

    marker("screen:consent")
    marker("condition:inline_early:start")
    marker("survey:ocean:submitted")

Requires: pylsl (pip install pylsl).  If pylsl is unavailable all
calls are silently ignored — safe to call unconditionally.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from core.log import logger


# ── LSL Outlet (lazy singleton) ──────────────────────────────────────────────

_outlet = None
_enabled = False


def enable() -> None:
    """Enable LSL markers for lab sessions.  No-op in crowd mode."""
    global _enabled
    _enabled = True


def disable() -> None:
    """Disable LSL markers (default)."""
    global _enabled
    _enabled = False


def _get_outlet():
    """Lazy-init LSL outlet. Returns None if pylsl unavailable."""
    global _outlet
    if _outlet is not None:
        return _outlet
    try:
        from pylsl import StreamInfo, StreamOutlet
        info = StreamInfo(
            name="ExperimentMarkers",
            type="Markers",
            channel_count=1,
            nominal_srate=0,  # irregular rate
            source_id="rag-recsys-experiment",
        )
        _outlet = StreamOutlet(info)
        logger.info("[EEG] LSL marker outlet created: ExperimentMarkers")
    except ImportError:
        logger.warning("[EEG] pylsl not installed — markers disabled")
        _outlet = None
    except Exception as e:
        logger.warning("[EEG] LSL outlet creation failed: {}", e)
        _outlet = None
    return _outlet


# ── Core marker emission ─────────────────────────────────────────────────────

def marker(label: str) -> None:
    """Push a single string marker to LSL.

    Idempotent, non-blocking, best-effort.  Safe to call even when
    pylsl is not installed — returns silently.
    """
    if not _enabled:
        return
    outlet = _get_outlet()
    if outlet:
        outlet.push_sample([label])


# ── Convenience helpers ──────────────────────────────────────────────────────

def screen_marker(screen_name: str) -> None:
    """Send a screen-entry marker (e.g. 'screen:consent')."""
    marker(f"screen:{screen_name}")


def condition_marker(condition_id: str, action: str, ad_mode: str = "") -> None:
    """Send a condition lifecycle marker.

    action: "start" | "end"
    """
    marker(f"condition:{condition_id}:{action}")
    if ad_mode:
        marker(f"condition:{condition_id}:ad_mode:{ad_mode}")


def survey_marker(survey_type: str) -> None:
    """Send a survey-submission marker (e.g. 'survey:ocean:submitted')."""
    marker(f"survey:{survey_type}:submitted")


def session_marker(action: str) -> None:
    """Send a session lifecycle marker.

    action: "start" | "end"
    """
    marker(f"session:{action}")


def baseline_marker(action: str) -> None:
    """Send a baseline lifecycle marker.

    action: "start" | "end"
    """
    marker(f"baseline:{action}")


# ── Modality hook (registered with ConversationManager) ─────────────────────

def eeg_turn_hook(turn: int, ad_injected: bool, ad: Any) -> None:
    """
    Called in thread pool after each LLM turn.

    Emits LSL markers that EEG recording software (BrainVision, OpenBCI,
    etc.) can time-lock to neural data for epoch extraction.
    """
    marker(f"turn:{turn}")
    if ad_injected:
        marker(f"ad_injected:{turn}")
