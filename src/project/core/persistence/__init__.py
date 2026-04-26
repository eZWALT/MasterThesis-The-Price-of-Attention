"""
Persistence layer.

Solves: Streamlit session_state is in-memory only — a page refresh
wipes all participant data mid-experiment.

Architecture:
  SessionStore (abstract)
    ├── NullSessionStore      — no-op, current behaviour
    ├── FileSessionStore      — JSON on disk, keyed by participant_id
    └── RedisSessionStore     — stub for future networked deployment

The active store is injected at startup via init_session_state().
"""
from core.persistence.store import SessionStore, NullSessionStore, FileSessionStore

__all__ = ["SessionStore", "NullSessionStore", "FileSessionStore"]
