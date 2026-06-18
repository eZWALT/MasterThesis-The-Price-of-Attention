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

import json
import requests
from typing import List, Dict, Generator

import logging

from core.config import (
    API_URL,
    OLLAMA_API_BASE,
    LLM_TIMEOUT_SECONDS,
    LLM_BACKEND,
    LLM_THINK,
    OLLAMA_NUM_CTX,
    OLLAMA_KEEP_ALIVE,
)

log = logging.getLogger(__name__)


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
        mock: bool = False,
    ):
        self.api_url = api_url
        self.ollama_api_base = ollama_api_base
        self.timeout = timeout
        self.mock = mock

    def warmup(self, model: str) -> None:
        """
        Send a minimal 1-token request to force Ollama to load the model into
        GPU memory.  Call this once at application startup so the first real
        generation does not pay the cold-start penalty (~15 s).

        No-ops silently when the backend is not Ollama or if the request fails
        (warmup errors should never block startup).
        """
        if LLM_BACKEND != "ollama":
            return
        log.info("Warming up Ollama model '%s' …", model)
        try:
            url = f"{self.ollama_api_base.rstrip('/')}/api/chat"
            try:
                keep_alive: int | str = int(OLLAMA_KEEP_ALIVE)
            except (ValueError, TypeError):
                keep_alive = OLLAMA_KEEP_ALIVE
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": "hi"}],
                "think": False,
                "stream": False,
                "keep_alive": keep_alive,
                "options": {
                    "num_predict": 1,
                    "num_ctx": OLLAMA_NUM_CTX,
                },
            }
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            log.info("Ollama warmup complete.")
        except Exception as exc:  # noqa: BLE001
            log.warning("Ollama warmup failed (non-fatal): %s", exc)

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
        if self.mock:
            return self._mock_chat()
        if LLM_BACKEND == "ollama":
            return self._chat_ollama(messages, model, temperature, max_tokens)
        return self._chat_openai(messages, model, temperature, max_tokens)

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> Generator[str, None, None]:
        """
        Stream tokens from the LLM. Yields content strings as they arrive.

        Raises
        ------
        RuntimeError on any network or API error (emitted as the first
        yielded token so the UI can display it).
        """
        if self.mock:
            yield from self._mock_chat_stream()
            return
        if LLM_BACKEND == "ollama":
            yield from self._chat_ollama_stream(messages, model, temperature, max_tokens)
        else:
            yield from self._chat_openai_stream(messages, model, temperature, max_tokens)

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

    def _chat_ollama_stream(self, messages, model, temperature, max_tokens) -> Generator[str, None, None]:
        """Streaming variant of _chat_ollama."""
        url = f"{self.ollama_api_base.rstrip('/')}/api/chat"
        try:
            keep_alive: int | str = int(OLLAMA_KEEP_ALIVE)
        except (ValueError, TypeError):
            keep_alive = OLLAMA_KEEP_ALIVE
        payload = {
            "model": model,
            "messages": messages,
            "think": LLM_THINK,
            "stream": True,
            "keep_alive": keep_alive,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": OLLAMA_NUM_CTX,
            },
        }
        try:
            response = requests.post(url, json=payload, stream=True, timeout=self.timeout)
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if data.get("done", False):
                        break
        except Exception as e:
            yield f"⚠️ {e}"

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

    def _chat_openai_stream(self, messages, model, temperature, max_tokens) -> Generator[str, None, None]:
        """Streaming variant of _chat_openai."""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        try:
            response = requests.post(
                self.api_url, json=payload, stream=True, timeout=self.timeout
            )
            response.raise_for_status()
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
        except Exception as e:
            yield f"⚠️ {e}"

    # ── mock (dry-run mode, no HTTP calls) ─────────────────────

    _MOCK_RESPONSE: str = (
        "That's a great question! Based on what you've told me, "
        "I'd recommend looking into a few different options. "
        "For example, MyProtein Creatine is a popular choice for "
        "boosting recovery and muscle growth. "
        "Consider factors like your budget, lifestyle, and specific needs. "
        "Would you like me to help you compare some choices?"
    )

    def _mock_chat(self) -> str:
        return self._MOCK_RESPONSE

    def _mock_chat_stream(self) -> Generator[str, None, None]:
        import time
        for token in self._MOCK_RESPONSE.split():
            yield token + " "
            time.sleep(0.02)
