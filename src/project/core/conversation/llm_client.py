"""
LLM Client.

Thin wrapper around the vLLM-compatible OpenAI chat completions API.
Responsible only for sending messages and returning the assistant reply.

All model parameters are passed in from config — nothing is hardcoded here.
"""

from __future__ import annotations

import requests
from typing import List, Dict

from core.config import API_URL, LLM_TIMEOUT_SECONDS


class LLMClient:
    """
    Stateless HTTP client for an OpenAI-compatible chat completions endpoint.

    Parameters
    ----------
    api_url : endpoint URL (default from config).
    timeout : request timeout in seconds (default from config).
    """

    def __init__(
        self,
        api_url: str = API_URL,
        timeout: int = LLM_TIMEOUT_SECONDS,
    ):
        self.api_url = api_url
        self.timeout = timeout

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        """
        Send a chat completion request and return the assistant's text.

        Raises
        ------
        RuntimeError on any network or API error.
        """
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"LLM request failed: {e}") from e
