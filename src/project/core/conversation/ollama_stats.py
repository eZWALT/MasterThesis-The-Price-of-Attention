"""
Ollama stats helper — ETA estimation for LLM responses.

Probes the Ollama native API (/api/ps) to detect whether the target
model is warm in VRAM, then combines that with a rolling tokens-per-second
estimate derived from previous responses to compute an ETA.

Usage
-----
    from core.conversation.ollama_stats import estimate_eta, record_timing

    # Before LLM call
    eta_seconds = estimate_eta(max_tokens=400, model=model, base_url=OLLAMA_API_BASE)

    # After LLM call
    record_timing(elapsed=elapsed, reply=reply_text)
"""

from __future__ import annotations

import time
import requests
from typing import Optional


# Module-level rolling average of tokens/s across all calls this session.
_last_tps: Optional[float] = None
_alpha: float = 0.3          # EMA smoothing factor


def probe_model_status(base_url: str, model: str | None = None) -> dict:
    """
    Query Ollama /api/ps and return status dict.

    Returns
    -------
    dict with keys:
        loaded : bool    — is any model currently loaded?
        matched : bool   — is the requested model specifically loaded?
        vram_bytes : int — VRAM used by matched model (0 if unknown)
        size_bytes : int — total parameter size of matched model (0 if unknown)
    """
    result = {"loaded": False, "matched": False, "vram_bytes": 0, "size_bytes": 0}
    try:
        resp = requests.get(f"{base_url}/api/ps", timeout=2)
        resp.raise_for_status()
        models = resp.json().get("models", [])
        if models:
            result["loaded"] = True
        for m in models:
            name = m.get("model", m.get("name", ""))
            if model and not name.startswith(model.split(":")[0]):
                continue
            result["matched"] = True
            result["vram_bytes"] = m.get("size_vram", 0)
            result["size_bytes"] = m.get("size", 0)
            break
    except Exception:
        pass
    return result


def _tps_from_vram(size_bytes: int) -> float:
    """
    Rough heuristic: estimate tokens/s from VRAM usage.
    Based on typical Ollama/CUDA throughput for quantised models.
    """
    gb = size_bytes / 1e9
    if gb <= 5:      return 60.0   # ~3-7B
    elif gb <= 12:   return 35.0   # ~13B
    elif gb <= 24:   return 18.0   # ~32B
    elif gb <= 48:   return 10.0   # ~70B
    else:            return 4.0    # >70B


def estimate_eta(
    max_tokens: int,
    model: Optional[str] = None,
    base_url: str = "http://localhost:11434",
) -> Optional[float]:
    """
    Return an estimated seconds-to-completion for a response of *max_tokens*.

    Steps
    -----
    1.  If we have a measured tokens/s from previous calls, use that.
    2.  Otherwise probe /api/ps — if model is warm, estimate from VRAM size.
    3.  If nothing is available, return None (caller shows indeterminate spinner).
    """
    global _last_tps

    if _last_tps and _last_tps > 0:
        return max_tokens / _last_tps

    status = probe_model_status(base_url, model)
    if status["matched"] and status["vram_bytes"] > 0:
        return max_tokens / _tps_from_vram(status["vram_bytes"])
    if status["loaded"] and status["size_bytes"] > 0:
        return max_tokens / _tps_from_vram(status["size_bytes"])

    return None   # cold start or Ollama unreachable


def record_timing(elapsed: float, reply: str) -> None:
    """
    Update the rolling tokens/s estimate from a completed response.
    Approximates token count via word count × 1.35 (typical EN ratio).
    """
    global _last_tps
    if elapsed <= 0:
        return
    approx_tokens = max(1, len(reply.split()) * 1.35)
    measured_tps = approx_tokens / elapsed
    if _last_tps is None:
        _last_tps = measured_tps
    else:
        _last_tps = _alpha * measured_tps + (1 - _alpha) * _last_tps
