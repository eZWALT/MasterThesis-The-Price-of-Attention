"""
Dummy marker sender — fires HTTP POST to the marker receiver.

Disabled by default (MARKER_SERVER_URL="").  When enabled, sends
markers asynchronously so the experiment flow is never blocked.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
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
    "deception_disclosure_submitted": 10,
    "worker_id_set": 11,
    "validation_submitted": 12,
    "session_complete": 13,
    "early_exit": 14,
    "screen_skipped": 15,
    "experiment_config": 16,
}


@dataclass
class MarkerConfig:
    url: str = ""
    timeout_s: float = 2.0


class MarkerClient:
    """Fire-and-forget HTTP marker sender."""

    def __init__(self, config: MarkerConfig) -> None:
        self._url = config.url.rstrip("/")
        self._timeout = config.timeout_s
        self._enabled = bool(self._url)
        if self._enabled:
            log.info("marker client enabled -> %s", self._url)

    def send(
        self,
        event: str,
        *,
        marker_name: str = "",
        event_type: str = "",
        marker_index: Optional[int] = None,
        **extra,
    ) -> None:
        if not self._enabled:
            return
        marker_name = marker_name or event
        event_type = event_type or event
        index = (
            marker_index
            if marker_index is not None
            else MARKER_EVENT_CODES.get(event)
        )
        now = datetime.now(timezone.utc)
        payload = {
            "marker_name": marker_name,
            "event_type": event_type,
            "timestamp": now.isoformat(),
            "unix_ts": now.timestamp(),
            "index": index,
        }
        payload.update(extra)
        threading.Thread(
            target=self._post,
            args=(payload,),
            daemon=True,
        ).start()

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
