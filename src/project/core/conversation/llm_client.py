"""
LLM Client.

Supports two backends:
  ollama — native Ollama /api/chat endpoint.  Supports `think: false` to
           disable Qwen3 chain-of-thought, giving fast conversational replies.
  openai — OpenAI-compatible /v1/chat/completions endpoint (vLLM, OpenAI, …).

Backend is selected via LLM_BACKEND config / env var.
All other model parameters come from config — nothing is hardcoded here.
"""

from __future__ import annotations

import requests
from typing import List, Dict

from core.config import (
    API_URL,
    OLLAMA_API_BASE,
    LLM_TIMEOUT_SECONDS,
    LLM_BACKEND,
    LLM_THINK,
    OLLAMA_NUM_CTX,
    OLLAMA_KEEP_ALIVE,
)


class LLMClient:
    """
    Stateless HTTP client for LLM inference.

    Parameters
    ----------
    api_url : OpenAI-compat endpoint URL (used when LLM_BACKEND="openai").
    ollama_api_base : Ollama base URL (used when LLM_BACKEND="ollama").
    timeout : request timeout in seconds.
    """

    def __init__(
        self,
        api_url: str = API_URL,
        ollama_api_base: str = OLLAMA_API_BASE,
        timeout: int = LLM_TIMEOUT_SECONDS,
    ):
        self.api_url = api_url
        self.ollama_api_base = ollama_api_base
        self.timeout = timeout

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Send a chat completion request and return the assistant's reply text.

        Raises
        ------
        RuntimeError on any network or API error.
        """
        if LLM_BACKEND == "ollama":
            return self._chat_ollama(messages, model, temperature, max_tokens)
        return self._chat_openai(messages, model, temperature, max_tokens)

    # ── private ──────────────────────────────────────────────────────────

    def _chat_ollama(self, messages, model, temperature, max_tokens) -> str:
        """
        Native Ollama /api/chat — supports think:false for Qwen3 models.
        Response format: {"message": {"role": "assistant", "content": "..."}}
        """
        url = f"{self.ollama_api_base.rstrip('/')}/api/chat"
        # keep_alive: Ollama accepts an integer (seconds/-1) or a duration string
        # ("5m", "1h"). Try to coerce the config string to int where possible so
        # the API receives the correct JSON type (e.g. -1 not "-1").
        try:
            keep_alive: int | str = int(OLLAMA_KEEP_ALIVE)
        except (ValueError, TypeError):
            keep_alive = OLLAMA_KEEP_ALIVE  # leave as string for durations like "30m"
        payload = {
            "model": model,
            "messages": messages,
            "think": LLM_THINK,
            "stream": False,
            "keep_alive": keep_alive,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": OLLAMA_NUM_CTX,
            },
        }
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            content = data["message"].get("content") or ""
            return content.strip()
        except Exception as e:
            raise RuntimeError(f"Ollama request failed: {e}") from e

    def _chat_openai(self, messages, model, temperature, max_tokens) -> str:
        """
        OpenAI-compatible /v1/chat/completions — used for vLLM and hosted models.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            response = requests.post(
                self.api_url, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            msg = response.json()["choices"][0]["message"]
            content = msg.get("content") or ""
            return content.strip()
        except Exception as e:
            raise RuntimeError(f"OpenAI-compat request failed: {e}") from e
