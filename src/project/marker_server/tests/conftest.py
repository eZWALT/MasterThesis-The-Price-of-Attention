from __future__ import annotations

import pytest

from lib.config import MarkerServerConfig


@pytest.fixture
def cfg() -> MarkerServerConfig:
    return MarkerServerConfig()
