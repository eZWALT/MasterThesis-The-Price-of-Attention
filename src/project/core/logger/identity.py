"""
Experiment Identity — unique, sortable identifiers.

Identifiers:

    experiment_id   — per run: exp_{ISO_UTC}_{random_hex8}
    participant_id  — per participant: short UUID (auto-generated)
    conversation_id — per trial: UUID (created in manager)

Format examples:
    experiment_id:  exp_20260524T154233Z_a3f2b8c1
    participant_id: 7d1e4f0a
"""

from __future__ import annotations

import secrets
import time
import uuid


def make_experiment_id() -> str:
    """
    Generate a unique, sortable experiment ID.

    The random hex suffix ensures every run produces a different ID
    even within the same second.

    Returns
    -------
    str like "exp_20260524T154233Z_a3f2b8c1"
    """
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    h = secrets.token_hex(4)  # 8 hex chars
    return f"exp_{ts}_{h}"


def make_participant_id() -> str:
    """
    Generate a short participant ID (auto-generated UUID).

    Format: 8 hex chars from a random UUID.
    """
    return uuid.uuid4().hex[:8]
