"""
Centralised loguru configuration.

Every module in the project should import the logger from here so that
format tweaks and sink additions propagate everywhere automatically.

Usage
-----
    from core.log import logger

    logger.info("catalog loaded: {} items", n_items)
    logger.warning("model '{}' not found — using fallback", name)
    logger.debug("query_vec shape: {}", query_vec.shape)
    logger.opt(exception=True).error("unexpected error during inference")

Environment variables
---------------------
LOG_LEVEL  : verbosity level (default "INFO").
             Set "DEBUG" to see detailed per-stage traces.
LOG_FILE   : path to a rotating log file (optional).
             Example: LOG_FILE=logs/experiment.log
"""

from __future__ import annotations

import os
import sys

from loguru import logger

# ── Remove the default stderr sink added by loguru on import ──────────────
logger.remove()

_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>"
)

logger.add(sys.stderr, level=_LEVEL, format=_FORMAT, colorize=True)

# ── Optional file sink (rotating, 7-day retention) ────────────────────────
_LOG_FILE = os.getenv("LOG_FILE")
if _LOG_FILE:
    logger.add(
        _LOG_FILE,
        level=_LEVEL,
        format=_FORMAT,
        rotation="10 MB",
        retention="7 days",
        colorize=False,
    )

__all__ = ["logger"]
