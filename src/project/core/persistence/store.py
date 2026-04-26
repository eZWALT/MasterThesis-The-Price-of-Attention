"""
Session store implementations.

Responsibility: persist and restore the ExperimentController state
across page refreshes so a participant doesn't lose progress.

Wire up in core/ui/participant.py::init_session_state():

    store = FileSessionStore(base_dir="./sessions")
    if "controller" not in st.session_state:
        pid = ...
        state = store.load(pid)         # returns None on first visit
        if state:
            ctrl = ExperimentController.from_dict(state)
        else:
            ctrl = ExperimentController(pid, ...)
            ctrl.build_trial_plan()
        st.session_state.controller = ctrl
        st.session_state.store = store

    # After every ctrl.advance():
    st.session_state.store.save(ctrl.participant_id, ctrl.to_dict())
"""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class SessionStore(ABC):
    """Abstract key-value store for experiment session snapshots."""

    @abstractmethod
    def save(self, participant_id: str, state: Dict[str, Any]) -> None:
        """Persist the controller state dict for this participant."""

    @abstractmethod
    def load(self, participant_id: str) -> Optional[Dict[str, Any]]:
        """
        Return the last saved state dict, or None if no snapshot exists.
        """

    @abstractmethod
    def delete(self, participant_id: str) -> None:
        """Remove the snapshot (e.g. after session export)."""


class NullSessionStore(SessionStore):
    """
    No-op store — current behaviour.
    Page refresh will restart the experiment from the beginning.
    """

    def save(self, participant_id: str, state: Dict[str, Any]) -> None:
        pass

    def load(self, participant_id: str) -> Optional[Dict[str, Any]]:
        return None

    def delete(self, participant_id: str) -> None:
        pass


class FileSessionStore(SessionStore):
    """
    JSON file store. One file per participant under base_dir/.

    Suitable for single-machine experiments. Safe for concurrent
    single-participant sessions; not safe for multi-machine setups.
    """

    def __init__(self, base_dir: str = "./sessions"):
        self._dir = Path(base_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _path(self, participant_id: str) -> Path:
        return self._dir / f"{participant_id}.json"

    def save(self, participant_id: str, state: Dict[str, Any]) -> None:
        tmp = self._path(participant_id).with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, default=str))
        tmp.replace(self._path(participant_id))  # atomic on POSIX

    def load(self, participant_id: str) -> Optional[Dict[str, Any]]:
        p = self._path(participant_id)
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def delete(self, participant_id: str) -> None:
        p = self._path(participant_id)
        if p.exists():
            p.unlink()


class RedisSessionStore(SessionStore):
    """
    Redis-backed store for networked / multi-machine deployments.

    Requirements:
      redis>=5.0.0  (add to requirements.txt when needed)
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl: int = 86400):
        try:
            import redis  # type: ignore
            self._r = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self._ttl = ttl
        except ImportError:
            raise RuntimeError("redis-py not installed. Add redis>=5.0.0 to requirements.txt.")

    def _key(self, participant_id: str) -> str:
        return f"session:{participant_id}"

    def save(self, participant_id: str, state: Dict[str, Any]) -> None:
        self._r.set(self._key(participant_id), json.dumps(state, default=str), ex=self._ttl)

    def load(self, participant_id: str) -> Optional[Dict[str, Any]]:
        raw = self._r.get(self._key(participant_id))
        return json.loads(raw) if raw else None

    def delete(self, participant_id: str) -> None:
        self._r.delete(self._key(participant_id))
