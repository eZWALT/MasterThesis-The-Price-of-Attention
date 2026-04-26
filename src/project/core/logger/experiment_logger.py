"""
Experiment Logger.

Structured logging for every event in the experimental pipeline.
Keeps an in-memory log buffer that can be:
  - Displayed in the UI (debug panel)
  - Exported to JSON / CSV for offline analysis

Every log entry captures: timestamp, conversation_id, ad_mode,
event type, and free-form data payload.

Paper reference: Section 6.5 — Multimodal Logging System.
"""

from __future__ import annotations

import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from pathlib import Path

from core.config import DEFAULT_LOG_EXPORT_FILENAME


@dataclass
class LogEntry:
    """Single experiment event."""
    timestamp: str
    conversation_id: str
    ad_mode: str
    event: str
    data: Any


class ExperimentLogger:
    """
    Accumulates LogEntry objects and provides export utilities.

    Parameters
    ----------
    export_dir : optional directory for auto-saving logs.
    """

    def __init__(self, export_dir: Optional[str] = None):
        self.entries: List[LogEntry] = []
        self.export_dir = Path(export_dir) if export_dir else None

    # ── Core ──────────────────────────────────────────────────

    def log(
        self,
        event: str,
        data: Any,
        ad_mode: str,
        conversation_id: str,
    ) -> LogEntry:
        """Record an event and return the entry."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            conversation_id=conversation_id,
            ad_mode=ad_mode,
            event=event,
            data=data,
        )
        self.entries.append(entry)
        return entry

    def clear(self):
        """Reset the log buffer."""
        self.entries = []

    # ── Serialization ─────────────────────────────────────────

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Return all entries as plain dicts (JSON-friendly)."""
        return [asdict(e) for e in self.entries]

    def to_json(self, indent: int = 2) -> str:
        """Serialize the full log to a JSON string."""
        return json.dumps(self.to_dicts(), indent=indent, default=str)

    def export_json(
        self,
        filename: str = DEFAULT_LOG_EXPORT_FILENAME,
    ) -> Path:
        """Write logs to a JSON file."""
        out_dir = self.export_dir or Path(".")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / filename
        path.write_text(self.to_json())
        return path

    # TODO: export_csv() for easy import into pandas / R
    # TODO: export_to_wandb() for experiment tracking dashboards
    # TODO: export_to_hf_dataset() for HuggingFace Datasets integration
