"""
EEG integration — Lab Stream Layer (LSL) markers and stream reading.

This module provides:
  1. Marker emission — push event markers to LSL for time-locking EEG epochs
  2. Stream reader  — (future) read raw EEG for real-time features

Markers are sent via the modality hook system in ConversationManager.
They run in the CPU thread pool — non-blocking to the main thread.

Integration:
    from core.modalities.eeg import eeg_turn_hook
    conversation_manager.register_modality_hook(eeg_turn_hook)

LSL marker protocol:
    "turn_{N}"           — user turn N started
    "ad_injected_{N}"    — ad was injected at turn N
    "ad_mode_{mode}"     — which ad condition is active

Requires: pylsl (pip install pylsl) — only imported at runtime.
"""

from __future__ import annotations

import time
from typing import Any, Optional

from core.log import logger


# ── LSL Outlet (lazy singleton) ──────────────────────────────────────────────

_outlet = None


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


# ── Marker emission ──────────────────────────────────────────────────────────

def send_marker(label: str) -> None:
    """Push a single string marker to LSL (non-blocking, best-effort)."""
    outlet = _get_outlet()
    if outlet:
        outlet.push_sample([label])


# ── Modality hook (register with ConversationManager) ────────────────────────

def eeg_turn_hook(turn: int, ad_injected: bool, ad: Any) -> None:
    """
    Called in thread pool after each LLM turn.

    Emits LSL markers that EEG recording software (BrainVision, OpenBCI,
    etc.) can time-lock to neural data for epoch extraction.
    """
    send_marker(f"turn_{turn}")
    if ad_injected:
        send_marker(f"ad_injected_{turn}")
        if ad and hasattr(ad, "metadata"):
            source = ad.metadata.get("source", "unknown")
            send_marker(f"ad_source_{source}")
