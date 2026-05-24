"""
Device allocation — smart GPU/CPU assignment for ML models.

Spreads models across available GPUs and falls back to CPU when VRAM is
insufficient.  Each call "reserves" the estimated memory so subsequent
calls pick a different device where possible.

Environment overrides
─────────────────────
  FORCE_CPU=1            → all models on CPU regardless of GPU availability
  CUDA_VISIBLE_DEVICES   → standard NVIDIA variable; limits visible GPUs
  LLM_GPU_INDICES=0      → comma-separated GPU indices reserved for the LLM
  <MODEL>_DEVICE         → per-model override (e.g. EMBEDDING_DEVICE=cuda:0)
"""

from __future__ import annotations

import logging
import os
from typing import Optional

_log = logging.getLogger(__name__)

# ─── Global state ─────────────────────────────────────────────────────────────

FORCE_CPU: bool = os.getenv("FORCE_CPU", "").lower() in ("1", "true", "yes")

# GPUs reserved for the external LLM server (Ollama / vLLM).
# Excluded from automatic allocation unless overridden per-model.
LLM_GPU_INDICES: set[int] = {
    int(x) for x in os.getenv("LLM_GPU_INDICES", "0").split(",") if x.strip().isdigit()
}

# Track VRAM already claimed by earlier allocations in this process.
# Key = GPU index, value = bytes "reserved" (not yet loaded, just planned).
_gpu_reservations: dict[int, int] = {}


# ─── Estimated VRAM per model (GB, BF16 weights + activation overhead) ────────

VRAM_ESTIMATES: dict[str, float] = {
    "Qwen/Qwen3-Embedding-0.6B": 2.0,
    "Qwen/Qwen3-Embedding-4B":   10.0,
    "Qwen/Qwen3-Reranker-0.6B":  2.0,
    "Qwen/Qwen3-Reranker-4B":    10.0,
    "intent-bert":                0.5,
}

# Fallback estimate when model is not in the table above.
_DEFAULT_VRAM_ESTIMATE_GB: float = 4.0


# ─── Public API ───────────────────────────────────────────────────────────────

def estimate_vram(model_name: str) -> float:
    """Return estimated VRAM (GB) for a model, falling back to a safe default."""
    return VRAM_ESTIMATES.get(model_name, _DEFAULT_VRAM_ESTIMATE_GB)


def get_free_vram() -> dict[int, int]:
    """
    Return {gpu_index: free_bytes} for every visible CUDA device.
    Accounts for reservations already made by this process.
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return {}
        result: dict[int, int] = {}
        for i in range(torch.cuda.device_count()):
            free, _ = torch.cuda.mem_get_info(i)
            reserved = _gpu_reservations.get(i, 0)
            result[i] = max(free - reserved, 0)
        return result
    except Exception:
        return {}


def allocate_device(
    model_name: str,
    preferred: str = "cuda:1",
    role: str = "model",
    exclude_gpus: Optional[set[int]] = None,
    required_vram_gb: Optional[float] = None,
) -> str:
    """
    Intelligent device allocator.

    Parameters
    ----------
    model_name       : HuggingFace model id — used to look up VRAM estimate.
    preferred        : device string to try first (e.g. "cuda:1", "cpu").
    role             : human-readable name for logging (e.g. "embedding").
    exclude_gpus     : GPU indices to avoid (e.g. the one running the LLM).
    required_vram_gb : override the VRAM estimate from the table.

    Returns
    -------
    Device string: "cuda:X" or "cpu".
    """
    if FORCE_CPU:
        _log.info("[DeviceAlloc] FORCE_CPU=1 → %s assigned to cpu", role)
        return "cpu"

    # If cpu is explicitly preferred, honour it (e.g. small models).
    if preferred == "cpu":
        _log.info("[DeviceAlloc] %s → cpu (preferred)", role)
        return "cpu"

    try:
        import torch  # noqa: F401
    except ImportError:
        _log.warning("[DeviceAlloc] torch not installed → %s on cpu", role)
        return "cpu"

    free_map = get_free_vram()
    if not free_map:
        _log.info("[DeviceAlloc] No CUDA devices available → %s on cpu", role)
        return "cpu"

    exclude = exclude_gpus or set()
    vram_gb = required_vram_gb if required_vram_gb is not None else estimate_vram(model_name)
    required_bytes = int(vram_gb * 1024**3)
    # Add 10% headroom to avoid borderline OOM
    required_with_margin = int(required_bytes * 1.10)

    # 1) Try the preferred device first
    try:
        pref_idx = int(preferred.split(":")[-1]) if "cuda" in preferred else -1
    except (ValueError, IndexError):
        pref_idx = -1

    if pref_idx >= 0 and pref_idx in free_map and pref_idx not in exclude:
        if free_map[pref_idx] >= required_with_margin:
            _gpu_reservations[pref_idx] = _gpu_reservations.get(pref_idx, 0) + required_bytes
            _log.info(
                "[DeviceAlloc] %s → cuda:%d (preferred, %.1f GB free, %.1f GB needed)",
                role, pref_idx, free_map[pref_idx] / 1024**3, vram_gb,
            )
            return f"cuda:{pref_idx}"

    # 2) Find the GPU with the most free VRAM that has enough room
    candidates = [
        (idx, free)
        for idx, free in free_map.items()
        if idx not in exclude and free >= required_with_margin
    ]
    candidates.sort(key=lambda x: x[1], reverse=True)  # most free first

    if candidates:
        best_idx, best_free = candidates[0]
        _gpu_reservations[best_idx] = _gpu_reservations.get(best_idx, 0) + required_bytes
        _log.info(
            "[DeviceAlloc] %s → cuda:%d (%.1f GB free, %.1f GB needed)",
            role, best_idx, best_free / 1024**3, vram_gb,
        )
        return f"cuda:{best_idx}"

    # 3) No GPU has enough room → fall back to CPU
    _log.warning(
        "[DeviceAlloc] %s → cpu (no GPU with %.1f GB free; available: %s)",
        role, vram_gb,
        {k: f"{v / 1024**3:.1f}GB" for k, v in free_map.items() if k not in exclude},
    )
    return "cpu"


def log_device_map(intent: str, embedding: str, reranker: str) -> None:
    """Log the final device assignments at startup."""
    _log.info(
        "[DeviceAlloc] Final map: intent=%s | embedding=%s | reranker=%s | "
        "LLM GPUs excluded=%s | FORCE_CPU=%s",
        intent, embedding, reranker, LLM_GPU_INDICES, FORCE_CPU,
    )
