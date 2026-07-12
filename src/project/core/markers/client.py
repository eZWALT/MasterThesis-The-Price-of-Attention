"""
Marker sender — fires HTTP POST to the receiver via a single worker thread.

Disabled by default (url="").  When enabled, sends markers asynchronously
through a queue-based daemon thread so the experiment flow is never blocked.
"""

from __future__ import annotations

import json
import logging
import queue
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.request import Request, urlopen

log = logging.getLogger("markers.client")


MARKER_EVENT_CODES: dict[str, int] = {
    "session_started": 1,
    "consent_granted": 2,
    "condition_started": 3,
    "condition_complete": 4,
    "post_condition_survey_submitted": 5,
    "condition_conclusion_submitted": 6,
    "ads_recall_submitted": 7,
    "ocean_submitted": 8,
    "demographics_post_submitted": 9,
    "worker_id_set": 10,
    "validation_submitted": 11,
    "session_complete": 12,
    "early_exit": 13,
    "screen_skipped": 14,
    "experiment_config": 15,
}


@dataclass
class MarkerConfig:
    url: str = ""
    timeout_s: float = 2.0


class MarkerClient:
    """Fire-and-forget HTTP marker sender (single worker thread)."""

    def __init__(self, config: MarkerConfig) -> None:
        self._url = config.url.rstrip("/")
        self._timeout = config.timeout_s
        self._enabled = bool(self._url)
        self._experiment_logger: Any = None
        self._queue: queue.Queue = queue.Queue()

        if self._enabled:
            self._worker = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker.start()
            log.info("marker client enabled -> %s", self._url)

    def set_logger(self, logger: Any) -> None:
        self._experiment_logger = logger

    def send(
        self,
        event: str,
        *,
        marker_name: str = "",
        event_type: str = "",
        marker_index: Optional[int] = None,
    ) -> None:
        if not self._enabled or event not in MARKER_EVENT_CODES:
            return
        index = marker_index if marker_index is not None else MARKER_EVENT_CODES[event]
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "marker_name": marker_name or event,
            "event_type": event_type or event,
            "timestamp": now.isoformat(),
            "unix_ts": now.timestamp(),
            "index": index,
        }
        self._queue.put((event, payload))

    def _worker_loop(self) -> None:
        while True:
            event, payload = self._queue.get()
            self._post(payload)
            self._log_sent(event, payload)

    def _post(self, payload: dict) -> None:
        try:
            data = json.dumps(payload, default=str).encode()
            req = Request(
                f"{self._url}/marker",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urlopen(req, timeout=self._timeout):
                pass
        except Exception as exc:
            log.debug("marker send failed: %s", exc)

    def _log_sent(self, event: str, payload: dict) -> None:
        if self._experiment_logger is None:
            return
        try:
            self._experiment_logger._log_internal(
                "marker_sent",
                {
                    "marker_event": event,
                    "marker_name": payload["marker_name"],
                    "marker_index": payload["index"],
                    "target_url": self._url,
                },
            )
        except Exception as exc:
            log.debug("marker self-log failed: %s", exc)
