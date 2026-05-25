"""
Unit tests for core.logger — ExperimentLogger, identity generation,
async flush, and export utilities.
"""

from __future__ import annotations

import json
import time
import threading
from pathlib import Path

import pytest

from core.logger import ExperimentLogger, make_experiment_id, make_run_id
from core.logger.identity import make_experiment_id as _make_exp_id
from core.logger.payload import compact_event_data, compact_retrieval_diag


@pytest.fixture
def tmp_log_dir(tmp_path):
    """Provide a temporary log directory."""
    return str(tmp_path / "logs")


@pytest.fixture
def logger(tmp_log_dir):
    """Create a logger that flushes immediately for testing."""
    lg = ExperimentLogger(
        participant_id="test_participant",
        log_dir=tmp_log_dir,
        flush_every_n=1,
        flush_every_s=300.0,  # disable timer-based flush for predictability
    )
    yield lg
    lg.stop()


# ── Identity generation ────────────────────────────────────────────────────


@pytest.mark.unit
class TestIdentity:
    def test_experiment_id_format(self):
        eid = make_experiment_id()
        assert eid.startswith("exp_")
        parts = eid.split("_")
        assert len(parts) == 3  # exp, timestamp, hash
        assert len(parts[2]) == 8  # 8-char config hash

    def test_experiment_id_deterministic(self):
        """Same config → same experiment ID (within same second)."""
        id1 = _make_exp_id()
        id2 = _make_exp_id()
        # Hash portion should be the same (config hasn't changed)
        assert id1.split("_")[2] == id2.split("_")[2]

    def test_run_id_unique(self):
        id1 = make_run_id()
        id2 = make_run_id()
        assert id1 != id2
        assert id1.startswith("run_")
        assert id2.startswith("run_")


# ── Logger basics ──────────────────────────────────────────────────────────


@pytest.mark.unit
class TestExperimentLogger:
    def test_log_creates_entry(self, logger):
        entry = logger.log("test_event", {"key": "value"}, "mock", "conv1", source="user", turn=1)
        assert entry.event == "test_event"
        assert entry.data == {"key": "value"}
        assert entry.participant_id == "test_participant"
        assert entry.source == "user"
        assert entry.turn == 1

    def test_step_counter_increments(self, logger):
        logger.log("e1", {}, "m", "c")
        logger.log("e2", {}, "m", "c")
        logger.log("e3", {}, "m", "c")
        assert logger.entries[-1].step_index == 3

    def test_set_participant(self, logger):
        logger.set_participant("P042")
        entry = logger.log("test", {}, "m", "c")
        assert entry.participant_id == "P042"

    def test_set_trial_index(self, logger):
        logger.set_trial_index(2)
        entry = logger.log("test", {}, "m", "c")
        assert entry.trial_index == 2

    def test_clear_resets_memory_not_disk(self, logger):
        logger.log("e1", {}, "m", "c")
        time.sleep(0.1)  # let writer flush
        logger.flush_sync()
        assert logger.log_path.exists()
        logger.clear()
        assert len(logger.entries) == 0
        # Disk file still exists
        assert logger.log_path.exists()

    def test_entries_returns_copy(self, logger):
        logger.log("e1", {}, "m", "c")
        entries = logger.entries
        entries.clear()
        assert len(logger.entries) == 1  # original not affected


# ── Flush behaviour ────────────────────────────────────────────────────────


@pytest.mark.unit
class TestFlushBehaviour:
    def test_flush_writes_to_disk(self, logger):
        logger.log("event", {"data": "test"}, "mock", "conv1")
        logger.flush_sync()
        assert logger.log_path.exists()
        with open(logger.log_path) as f:
            lines = f.readlines()
        assert len(lines) == 1
        obj = json.loads(lines[0])
        assert obj["event"] == "event"

    def test_idle_timeout_flushes(self, tmp_log_dir):
        """Writer flushes buffer after 1s idle even if threshold not reached."""
        lg = ExperimentLogger(
            participant_id="idle_test",
            log_dir=tmp_log_dir,
            flush_every_n=1000,  # won't trigger threshold
            flush_every_s=300.0,  # won't trigger timer
        )
        lg.log("idle_event", {"x": 1}, "m", "c")
        assert not lg.log_path.exists()
        time.sleep(2.0)  # wait for 1s idle timeout in writer loop
        assert lg.log_path.exists()
        with open(lg.log_path) as f:
            lines = f.readlines()
        assert len(lines) == 1
        lg.stop()

    def test_flush_sync_blocks(self, logger):
        """flush_sync returns only after data is on disk."""
        for i in range(5):
            logger.log("event", {"i": i}, "m", "c")
        logger.flush_sync()
        with open(logger.log_path) as f:
            lines = f.readlines()
        assert len(lines) == 5

    def test_stop_flushes_remaining(self, tmp_log_dir):
        """stop() ensures all buffered data reaches disk."""
        lg = ExperimentLogger(
            participant_id="stop_test",
            log_dir=tmp_log_dir,
            flush_every_n=1000,
            flush_every_s=300.0,
        )
        for i in range(10):
            lg.log("event", {"i": i}, "m", "c")
        lg.stop()
        with open(lg.log_path) as f:
            lines = f.readlines()
        assert len(lines) == 10


# ── Export utilities ───────────────────────────────────────────────────────


@pytest.mark.unit
class TestExport:
    def test_export_csv(self, logger):
        logger.log("user_message", {"content": "hello", "turn": 1}, "mock", "c1", source="user", turn=1)
        logger.log("retrieval", {"query": "hello", "score": 0.9}, "mock", "c1", source="retrieval", turn=1)
        logger.flush_sync()
        csv_path = logger.export_csv()
        assert csv_path.exists()
        with open(csv_path) as f:
            content = f.read()
        assert "user_message" in content
        assert "retrieval" in content

    def test_export_jsonl(self, logger):
        logger.log("e1", {"a": 1}, "mock", "c1")
        logger.log("e2", {"b": 2}, "mock", "c1")
        path = logger.export_jsonl()
        assert path.exists()
        with open(path) as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["event"] == "e1"
        assert json.loads(lines[1])["event"] == "e2"

    def test_to_dicts(self, logger):
        logger.log("e1", {"x": 1}, "mock", "c1")
        dicts = logger.to_dicts()
        assert len(dicts) == 1
        assert dicts[0]["event"] == "e1"
        assert dicts[0]["data"] == {"x": 1}


# ── Non-blocking performance ──────────────────────────────────────────────


@pytest.mark.unit
class TestPayloadCompaction:
    def test_compact_event_data_drops_duplicate_turn(self):
        assert compact_event_data({"turn": 3, "x": 1}, turn=3) == {"x": 1}

    def test_compact_retrieval_diag_strips_hyde_documents(self):
        diag = {
            "hyde_doc_count": 2,
            "hyde_documents": ["long passage"] * 2,
            "retrieval_query": "rewritten query text",
            "retrieval_total_ms": 120.0,
        }
        slim = compact_retrieval_diag(diag)
        assert "hyde_documents" not in slim
        assert "retrieval_query" not in slim
        assert slim["hyde_doc_count"] == 2


@pytest.mark.unit
class TestPerformance:
    def test_logging_is_nonblocking(self, logger):
        """50 log calls should complete in under 50ms (no disk I/O in caller)."""
        t0 = time.perf_counter()
        for i in range(50):
            logger.log("perf_test", {"i": i}, "m", f"c{i}", source="user", turn=i)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        assert elapsed_ms < 50, f"Logging took {elapsed_ms:.1f}ms — should be <50ms"
