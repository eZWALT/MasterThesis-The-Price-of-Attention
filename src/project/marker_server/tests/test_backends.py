"""
Unit tests for marker backends.
"""

from __future__ import annotations

import json

from lib.backends import (
    LoggingBackend,
    LSLBackend,
    PsychopyBackend,
    resolve_backend,
)


class TestResolve:
    def test_log_backend(self, cfg):
        b = resolve_backend("log", cfg)
        assert isinstance(b, LoggingBackend)

    def test_lsl_backend(self, cfg):
        b = resolve_backend("lsl", cfg)
        assert isinstance(b, LSLBackend)

    def test_psychopy_backend(self, cfg):
        b = resolve_backend("psychopy", cfg)
        assert isinstance(b, PsychopyBackend)

    def test_unknown_falls_back_to_log(self, cfg):
        b = resolve_backend("nonsense", cfg)
        assert isinstance(b, LoggingBackend)


class TestLoggingBackend:
    def test_send_does_not_crash(self, cfg):
        b = LoggingBackend(cfg)
        b.send({
            "marker_name": "test",
            "event_type": "test",
            "timestamp": "2026-01-01T00:00:00Z",
            "unix_ts": 1767225600.0,
            "index": 1,
        })
        b.close()

    def test_send_with_file(self, tmp_path, cfg):
        cfg.log_file = str(tmp_path / "markers.log")
        b = LoggingBackend(cfg)
        b.send({"marker_name": "x", "event_type": "y", "timestamp": "z", "unix_ts": 0.0, "index": 0})
        b.close()
        lines = (tmp_path / "markers.log").read_text().strip().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["marker_name"] == "x"

    def test_multiple_events(self, tmp_path, cfg):
        cfg.log_file = str(tmp_path / "multi.log")
        b = LoggingBackend(cfg)
        for i in range(5):
            b.send({"marker_name": f"e{i}", "event_type": "t", "timestamp": "", "unix_ts": float(i), "index": i})
        b.close()
        lines = (tmp_path / "multi.log").read_text().strip().splitlines()
        assert len(lines) == 5
        assert json.loads(lines[-1])["marker_name"] == "e4"

    def test_close_idempotent(self, cfg):
        b = LoggingBackend(cfg)
        b.close()
        b.close()


class TestLSLBackend:
    def test_instantiation_does_not_crash(self, cfg):
        b = LSLBackend(cfg)
        assert isinstance(b, LSLBackend)
        b.close()

    def test_send_without_pylsl_does_not_crash(self, cfg):
        b = LSLBackend(cfg)
        b.send({"marker_name": "x", "event_type": "y", "timestamp": "", "unix_ts": 0.0, "index": 0})
        b.close()


class TestPsychopyBackend:
    def test_instantiation_does_not_crash(self, cfg):
        b = PsychopyBackend(cfg)
        assert isinstance(b, PsychopyBackend)
        b.close()

    def test_send_without_psychopy_does_not_crash(self, cfg):
        b = PsychopyBackend(cfg)
        b.send({"marker_name": "x", "event_type": "y", "timestamp": "", "unix_ts": 0.0, "index": 0})
        b.close()
