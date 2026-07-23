"""
LSL marker emitter — log-adherent, single-outlet.

Pushes a whitelisted subset of marker events from ExperimentLogger.log() to LSL.
Outlet name: experiment_lab_pilot (hardcoded).

Usage:
    logger._marker_client = lsl_sender()         # hooks into logger.log()

Requires: pylsl (pip install pylsl).  If pylsl is unavailable all
calls are silently ignored — safe to call unconditionally.
"""

from __future__ import annotations

import os
import re

from core.log import logger as log


_LSL_EVENTS: frozenset[str] = frozenset({
    "baseline_start",
    "baseline_end",
    "warmup_start",
    "warmup_finish",
    "ad_injected",
    "condition_conclusion_submitted",
    "post_task_questionnaire_end",
    "experiment_end",
    "condition_start",
    "ad_displayed",
})

_TURN_READ_RE = re.compile(r"^turn_\d+_read$")
_TURN_WRITE_RE = re.compile(r"^turn_\d+_write$")


def _allow_lsl(event: str) -> bool:
    if event in _LSL_EVENTS:
        return True
    if _TURN_READ_RE.match(event) or _TURN_WRITE_RE.match(event):
        return True
    return False


_outlet = None


def _get_outlet():
    global _outlet
    if _outlet is not None:
        return _outlet
    name = "experiment_lab_pilot"
    try:
        from pylsl import StreamInfo, StreamOutlet
        info = StreamInfo(
            name=name,
            type="Markers",
            channel_count=1,
            nominal_srate=0,
            channel_format="string",
            source_id="rag-recsys-experiment-lab",
        )
        _outlet = StreamOutlet(info)
        log.info("[LSL] outlet created: {}", name)
    except ImportError:
        log.warning("[LSL] pylsl not installed — markers disabled")
        _outlet = None
    except Exception as e:
        log.warning("[LSL] outlet creation failed: {}", e)
        _outlet = None
    return _outlet


def marker(label: str) -> None:
    outlet = _get_outlet()
    if outlet:
        outlet.push_sample([label])


def screen_marker(screen_name: str) -> None:
    marker(f"screen:{screen_name}")


def condition_marker(condition_id: str, action: str, ad_mode: str = "") -> None:
    marker(f"condition:{condition_id}:{action}")
    if ad_mode:
        marker(f"condition:{condition_id}:ad_mode:{ad_mode}")


def survey_marker(survey_type: str) -> None:
    marker(f"survey:{survey_type}:submitted")


def session_marker(action: str) -> None:
    marker(f"session:{action}")


def baseline_marker(action: str) -> None:
    marker(f"baseline:{action}")


def lsl_sender() -> object:
    _get_outlet()
    marker("dummy_start")

    class _Sender:
        @staticmethod
        def send(event: str, **kwargs) -> None:
            if _allow_lsl(event):
                marker(event)

    return _Sender()
