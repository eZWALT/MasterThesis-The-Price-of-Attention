"""
Eye-tracking integration — fixation logging and AOI (Area of Interest) events.

This module provides:
  1. Turn-level event hook — logs gaze state at each turn boundary
  2. AOI tracking stubs  — (future) real-time fixation-on-ad detection

Eye-tracking events are logged through the experiment logger for
offline analysis (fixation duration on ad vs. conversation content).

Integration:
    from core.modalities.eye_tracking import eye_tracking_turn_hook
    conversation_manager.register_modality_hook(eye_tracking_turn_hook)

Supported backends (future):
  - Tobii Pro SDK (tobii_research)
  - Pupil Labs (pupil_core / neon)
  - WebGazer.js (browser-based, lower accuracy)

Requires: tobii-research or pupil-labs-realtime-api — only imported at runtime.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from core.log import logger


# ── Eye-tracker connection (lazy singleton) ───────────────────────────────────

_tracker = None
_logger_ref = None  # ExperimentLogger reference for event logging


def init_eye_tracking(experiment_logger=None) -> bool:
    """
    Attempt to connect to an eye-tracker.

    Returns True if connected, False otherwise (graceful degradation).
    """
    global _tracker, _logger_ref
    _logger_ref = experiment_logger

    try:
        import tobii_research as tr
        trackers = tr.find_all_eyetrackers()
        if trackers:
            _tracker = trackers[0]
            logger.info("[EyeTracking] Connected to: {} ({})",
                        _tracker.device_name, _tracker.serial_number)
            return True
        else:
            logger.warning("[EyeTracking] No Tobii eye-tracker found")
            return False
    except ImportError:
        logger.info("[EyeTracking] tobii_research not installed — eye-tracking disabled")
        return False
    except Exception as e:
        logger.warning("[EyeTracking] Connection failed: {}", e)
        return False


# ── Gaze snapshot ─────────────────────────────────────────────────────────────

def get_gaze_snapshot() -> Optional[dict]:
    """
    Get current gaze position (stub — returns None if no tracker).

    Future: returns {x, y, pupil_diameter_mm, timestamp_us}.
    """
    if _tracker is None:
        return None
    # TODO: implement with tobii_research.ScreenBasedCalibration
    return None


# ── Modality hook (register with ConversationManager) ────────────────────────

def eye_tracking_turn_hook(turn: int, ad_injected: bool, ad: Any) -> None:
    """
    Called in thread pool after each LLM turn.

    Logs an eye-tracking event for this turn boundary.
    Future: will capture fixation data and AOI dwell time.
    """
    gaze = get_gaze_snapshot()

    if _logger_ref and ad_injected:
        _logger_ref.log(
            "eye_tracking_ad_exposure",
            {
                "turn": turn,
                "ad_title": ad.title if ad else None,
                "gaze_snapshot": gaze,
                "timestamp_epoch_ms": int(time.time() * 1000),
            },
            source="eye_tracking",
            turn=turn,
        )
