"""
Experiment Logger — production-grade structured event logging.

Design: mini event-sourcing system.
  - Append-only JSONL on disk (one line per event, crash-safe)
  - Buffered writes (flush every N events OR T seconds)
  - Hierarchical IDs: experiment_id > run_id > participant_id > conversation_id
  - Every event carries full context for independent queryability

Output: one JSONL file per experiment run at:
    logs/{experiment_id}/{run_id}.jsonl

Paper reference: Section 6.5 — Multimodal Logging System.
"""

from __future__ import annotations

import atexit
import csv
import json
import queue
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.logger.identity import make_experiment_id, make_run_id

# Sentinel to signal the writer thread to stop
_STOP = object()


# ── Schema ────────────────────────────────────────────────────────────────────

@dataclass
class LogEntry:
    """
    Single experiment event — self-contained and independently queryable.

    Every field needed to locate this event in the experiment hierarchy
    is included directly (no joins required).
    """
    # Identity
    experiment_id: str
    run_id: str
    participant_id: str
    conversation_id: str

    # Event
    timestamp: str           # ISO-8601 UTC
    event: str               # user_message | assistant_reply | retrieval | ad_injected | ...
    source: str              # "user" | "model" | "system" | "retrieval"
    step_index: int          # global monotonic counter within this run

    # Context
    ad_mode: str             # experimental condition
    trial_index: int         # which trial (0-based)
    turn: int                # turn within trial

    # Payload
    data: Any                # free-form event-specific data


# ── Logger ────────────────────────────────────────────────────────────────────

class ExperimentLogger:
    """
    Production experiment logger with buffered JSONL persistence.

    Parameters
    ----------
    experiment_id  : stable ID for this experiment configuration.
    run_id         : unique per app launch.
    participant_id : human subject ID (set later via set_participant).
    log_dir        : base directory for log files.
    flush_every_n  : flush buffer to disk every N events.
    flush_every_s  : flush buffer to disk every N seconds (timer-based).
    """

    def __init__(
        self,
        experiment_id: Optional[str] = None,
        run_id: Optional[str] = None,
        participant_id: str = "unknown",
        log_dir: str = "logs",
        flush_every_n: int = 25,
        flush_every_s: float = 60.0,
    ) -> None:
        self.experiment_id = experiment_id or make_experiment_id()
        self.run_id = run_id or make_run_id()
        self.participant_id = participant_id
        self.flush_every_n = flush_every_n
        self.flush_every_s = flush_every_s

        # State
        self._entries: List[LogEntry] = []
        self._step_counter: int = 0
        self._trial_index: int = 0
        self._lock = threading.Lock()  # protects _entries + _step_counter

        # Non-blocking write queue — log() never blocks on disk I/O.
        # A dedicated daemon thread drains the queue and writes to JSONL.
        self._write_queue: queue.Queue = queue.Queue()
        self._pending_count: int = 0   # events since last flush (approx)

        # File path
        self._log_dir = Path(log_dir) / self.experiment_id
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = self._log_dir / f"{self.run_id}.jsonl"

        # Background writer thread (daemon — dies with main)
        self._writer_thread = threading.Thread(
            target=self._writer_loop, name="log-writer", daemon=True
        )
        self._writer_thread.start()

        # Periodic flush timer (fires every flush_every_s)
        self._timer: Optional[threading.Timer] = None
        self._start_flush_timer()

        # Flush on exit (best-effort)
        atexit.register(self.stop)

    # ── Public API ────────────────────────────────────────────────────────

    def log(
        self,
        event: str,
        data: Any,
        ad_mode: str = "",
        conversation_id: str = "",
        source: str = "system",
        turn: int = 0,
    ) -> LogEntry:
        """
        Record a structured event.

        Parameters
        ----------
        event           : event type key (e.g. "user_message", "retrieval")
        data            : free-form payload dict
        ad_mode         : current experimental condition
        conversation_id : conversation UUID
        source          : who produced this event (user/model/system/retrieval)
        turn            : turn number within current trial

        Returns
        -------
        The created LogEntry.
        """
        with self._lock:
            self._step_counter += 1
            entry = LogEntry(
                experiment_id=self.experiment_id,
                run_id=self.run_id,
                participant_id=self.participant_id,
                conversation_id=conversation_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                event=event,
                source=source,
                step_index=self._step_counter,
                ad_mode=ad_mode,
                trial_index=self._trial_index,
                turn=turn,
                data=data,
            )
            self._entries.append(entry)

        # Enqueue for async disk write (never blocks caller)
        line = json.dumps(asdict(entry), default=str)
        self._write_queue.put_nowait(line)
        self._pending_count += 1

        # Trigger flush if buffer threshold reached
        if self._pending_count >= self.flush_every_n:
            self._write_queue.put_nowait(None)  # flush signal
            self._pending_count = 0

        return entry

    def set_participant(self, participant_id: str) -> None:
        """Update participant ID (set after consent/demographics)."""
        self.participant_id = participant_id

    def set_trial_index(self, index: int) -> None:
        """Update current trial index (called by ExperimentController)."""
        self._trial_index = index

    def flush(self) -> None:
        """Signal the writer thread to flush now (non-blocking)."""
        self._write_queue.put_nowait(None)  # flush signal
        self._pending_count = 0

    def flush_sync(self) -> None:
        """Blocking flush — waits until all queued writes are on disk."""
        event = threading.Event()
        self._write_queue.put_nowait(event)
        event.wait(timeout=5.0)

    def clear(self) -> None:
        """Reset in-memory entries (disk log is never cleared)."""
        with self._lock:
            self._entries = []

    @property
    def entries(self) -> List[LogEntry]:
        """Read-only access to in-memory entries."""
        return list(self._entries)

    @property
    def log_path(self) -> Path:
        """Path to the current JSONL log file."""
        return self._log_path

    # ── Export utilities ───────────────────────────────────────────────────

    def to_dicts(self) -> List[Dict[str, Any]]:
        """Return all in-memory entries as plain dicts."""
        return [asdict(e) for e in self._entries]

    def to_json(self, indent: int = 2) -> str:
        """Serialize in-memory entries as JSON array (for debug/UI)."""
        return json.dumps(self.to_dicts(), indent=indent, default=str)

    def export_csv(self, path: Optional[str] = None) -> Path:
        """
        Export a flattened CSV — one row per event, ready for pandas/R.

        Flattens the `data` dict into top-level columns prefixed with `d_`.
        """
        out_path = Path(path) if path else (self._log_dir / f"{self.run_id}.csv")

        # Collect all data keys across entries for consistent columns
        all_data_keys: set = set()
        for entry in self._entries:
            if isinstance(entry.data, dict):
                all_data_keys.update(entry.data.keys())
        sorted_data_keys = sorted(all_data_keys)

        base_fields = [
            "experiment_id", "run_id", "participant_id", "conversation_id",
            "timestamp", "event", "source", "step_index",
            "ad_mode", "trial_index", "turn",
        ]
        fieldnames = base_fields + [f"d_{k}" for k in sorted_data_keys]

        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for entry in self._entries:
                row = {
                    "experiment_id": entry.experiment_id,
                    "run_id": entry.run_id,
                    "participant_id": entry.participant_id,
                    "conversation_id": entry.conversation_id,
                    "timestamp": entry.timestamp,
                    "event": entry.event,
                    "source": entry.source,
                    "step_index": entry.step_index,
                    "ad_mode": entry.ad_mode,
                    "trial_index": entry.trial_index,
                    "turn": entry.turn,
                }
                if isinstance(entry.data, dict):
                    for k in sorted_data_keys:
                        row[f"d_{k}"] = entry.data.get(k, "")
                writer.writerow(row)

        return out_path

    def export_jsonl(self, path: Optional[str] = None) -> Path:
        """
        Export the full in-memory log as a clean JSONL file.

        Unlike the live append file (which may have partial writes from
        crashes), this produces a validated export.
        """
        out_path = Path(path) if path else (self._log_dir / f"{self.run_id}_export.jsonl")
        with open(out_path, "w", encoding="utf-8") as f:
            for entry in self._entries:
                f.write(json.dumps(asdict(entry), default=str) + "\n")
        return out_path

    # ── Private — background writer ────────────────────────────────────────

    def _writer_loop(self) -> None:
        """
        Background writer thread.  Drains the queue and batch-writes to disk.

        Queue protocol:
          str          → a JSONL line to buffer
          None         → flush signal (write buffer to disk now)
          Event        → flush + set event (for flush_sync)
          _STOP        → exit the loop

        Flush also triggers on 1-second idle timeout so data never sits
        in memory indefinitely.
        """
        buffer: List[str] = []

        while True:
            try:
                item = self._write_queue.get(timeout=1.0)
            except queue.Empty:
                # Idle timeout — flush whatever is buffered so far
                if buffer:
                    self._write_lines(buffer)
                    buffer = []
                continue

            if item is _STOP:
                # Final flush before exit
                if buffer:
                    self._write_lines(buffer)
                    buffer = []
                break
            elif item is None:
                # Flush signal
                if buffer:
                    self._write_lines(buffer)
                    buffer = []
            elif isinstance(item, threading.Event):
                # Sync flush — write + signal caller
                if buffer:
                    self._write_lines(buffer)
                    buffer = []
                item.set()
            else:
                # Regular JSONL line
                buffer.append(item)

    def _write_lines(self, lines: List[str]) -> None:
        """Atomic batch write to the JSONL file."""
        with open(self._log_path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    def _start_flush_timer(self) -> None:
        """Periodic timer — sends flush signal every flush_every_s."""
        def _tick():
            self.flush()
            self._start_flush_timer()

        self._timer = threading.Timer(self.flush_every_s, _tick)
        self._timer.daemon = True
        self._timer.start()

    def stop(self) -> None:
        """Stop timer, drain queue, and do a final blocking flush."""
        if self._timer:
            self._timer.cancel()
            self._timer = None
        # Signal writer to exit
        self._write_queue.put_nowait(_STOP)
        self._writer_thread.join(timeout=5.0)

