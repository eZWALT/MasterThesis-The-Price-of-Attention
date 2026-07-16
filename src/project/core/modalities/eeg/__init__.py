"""
LSL marker emitter — log-adherent, single-outlet.

Pushes every marker event from ExperimentLogger.log() to LSL.
Outlet name comes from env LSL_MARKER_OUTLET (default: experiment_lab_pilot).

Usage:
    logger._marker_client = lsl_sender()         # hooks into logger.log()

Requires: pylsl (pip install pylsl).  If pylsl is unavailable all
calls are silently ignored — safe to call unconditionally.
"""

from __future__ import annotations

import os

from core.log import logger as log


# ── LSL Outlet (lazy singleton) ──────────────────────────────────────────────

_outlet = None


def _get_outlet():
    global _outlet
    if _outlet is not None:
        return _outlet
    name = os.environ.get("LSL_MARKER_OUTLET", "experiment_lab_pilot").strip()
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


# ── Core marker emission ─────────────────────────────────────────────────────

def marker(label: str) -> None:
    """Push a string marker to LSL."""
    outlet = _get_outlet()
    if outlet:
        outlet.push_sample([label])


def lsl_sender() -> object:
    """Return a duck-typed sender compatible with ExperimentLogger._marker_client.

    Usage:
        logger._marker_client = lsl_sender()
        # now every logger.log(event, ...) also pushes to LSL
    """
    _get_outlet()  # eager init — stream visible on network now

    class _Sender:
        @staticmethod
        def send(event: str, **kwargs) -> None:
            marker(event)

    return _Sender()
