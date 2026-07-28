"""Build version stamped into every session log.

Resolution order: the APP_VERSION environment variable, then the nearest
VERSION file above this module. Docker images do not include the repository
root, so containerised runs rely on APP_VERSION — launch.sh exports it.
"""

from __future__ import annotations

import os
from pathlib import Path


def get_version() -> str:
    env_version = os.getenv("APP_VERSION", "").strip()
    if env_version:
        return env_version

    for parent in Path(__file__).resolve().parents:
        candidate = parent / "VERSION"
        if candidate.is_file():
            try:
                version = candidate.read_text().strip()
            except OSError:
                return "unknown"
            if version:
                return version

    return "unknown"
