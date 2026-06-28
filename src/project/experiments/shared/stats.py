"""
Shared statistics utilities for experiment analysis.

No imports from project code — safe to use standalone.
"""

from __future__ import annotations

import statistics
from typing import Dict, List


def percentile(data: List[float], p: float) -> float:
    """Linear interpolation percentile (0.0–1.0)."""
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * p
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def compute_stats(values: List[float]) -> Dict:
    """Mean / std / min / max / p50 / p95 for a list of numbers."""
    if not values:
        return {"n": 0, "mean": 0, "std": 0, "min": 0, "max": 0, "p50": 0, "p95": 0}
    return {
        "n": len(values),
        "mean": round(statistics.mean(values), 1),
        "std": round(statistics.stdev(values), 1) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "p50": round(percentile(values, 0.50), 1),
        "p95": round(percentile(values, 0.95), 1),
    }


def format_table(headers: List[str], rows: List[List[str]], col_widths: List[int] | None = None) -> str:
    """
    ASCII table formatter for summary reports.
    Auto-sizes columns if col_widths not provided.
    """
    if col_widths is None:
        col_widths = [max(len(h), *(len(r[i]) for r in rows)) + 2 for i, h in enumerate(headers)]
    sep = "-" * (sum(col_widths) + len(headers) - 1)
    lines = [sep, " ".join(h.ljust(w) for h, w in zip(headers, col_widths)), sep]
    for row in rows:
        lines.append(" ".join(str(c).ljust(w) for c, w in zip(row, col_widths)))
    lines.append(sep)
    return "\n".join(lines)
