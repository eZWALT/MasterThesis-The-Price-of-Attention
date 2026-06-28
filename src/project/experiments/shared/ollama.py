"""
Shared Ollama utilities for experiments.

All experiment runners call this — no direct requests.post in experiment code.
"""

from __future__ import annotations

import requests
from typing import Dict, List


def ollama_is_up(ollama_url: str) -> bool:
    try:
        r = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=5)
        return r.ok
    except Exception:
        return False


def call_ollama(
    messages: List[Dict[str, str]],
    model: str,
    ollama_url: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    num_ctx: int = 16384,
    timeout: int = 300,
) -> Dict:
    """
    Non-streaming Ollama /api/chat call.

    Returns dict with:
      content             — assistant reply text
      eval_count          — exact generation token count (from Ollama)
      prompt_eval_count   — input tokens (from Ollama)
      eval_duration_ns   — Ollama's own generation timing
      done_reason         — why generation stopped ("stop" | "length" | ...)
    """
    url = f"{ollama_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "think": False,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx": num_ctx,
        },
    }
    resp = requests.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    content = data.get("message", {}).get("content", "")
    return {
        "content": content.strip(),
        "eval_count": data.get("eval_count", 0),
        "prompt_eval_count": data.get("prompt_eval_count", 0),
        "eval_duration_ns": data.get("eval_duration", 0),
        "done_reason": data.get("done_reason", ""),
    }
