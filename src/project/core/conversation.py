"""
TARA — Conversation Manager.

Owns the multi-turn conversation state and orchestrates:
  1. User message intake
  2. LLM backend call (with optional system overrides from ad injection)
  3. Post-response ad injection
  4. Attention shift computation
  5. Event logging

The UI layer should call `process_user_message()` and render
whatever comes back — it should never talk to the LLM directly.
"""

from __future__ import annotations

import uuid
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .config import API_URL
from .ad_injection import Ad, get_ad, get_injector, InjectionResult
from .attention_shift import (
    compute_attention_shift,
    AttentionShiftResult,
    AttentionEstimator,
)
from .experiment_logger import ExperimentLogger


# ── Turn result (what the UI receives) ────────────────────────

@dataclass
class TurnResult:
    """Everything the UI needs after one conversational turn."""
    assistant_reply: str
    injection: InjectionResult
    attention_shift: Optional[AttentionShiftResult] = None
    error: Optional[str] = None


# ── Conversation Manager ──────────────────────────────────────

class ConversationManager:
    """
    Stateful manager for a single conversation session.

    Parameters
    ----------
    ad_mode : current advertising paradigm key.
    model : HF model id served by vLLM.
    temperature : sampling temperature.
    max_tokens : max new tokens per response.
    api_url : vLLM-compatible chat completions endpoint.
    logger : experiment logger instance.
    attention_estimator : optional custom estimator for P(Z|C).
    """

    def __init__(
        self,
        ad_mode: str,
        model: str,
        temperature: float,
        max_tokens: int,
        api_url: str = API_URL,
        logger: ExperimentLogger | None = None,
        attention_estimator: AttentionEstimator | None = None,
    ):
        self.ad_mode = ad_mode
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = api_url
        self.logger = logger or ExperimentLogger()
        self.attention_estimator = attention_estimator

        self.conversation_id: str = str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []

    # ── Public API ────────────────────────────────────────────

    def process_user_message(self, user_input: str) -> TurnResult:
        """
        Full pipeline for one user turn:
        1. Record user message
        2. Snapshot C_pre
        3. Build LLM payload (with any system overrides)
        4. Call LLM
        5. Record assistant message
        6. Run post-response ad injection
        7. Snapshot C_post
        8. Compute attention shift
        """
        # 1. User message
        self.messages.append({"role": "user", "content": user_input})
        self.logger.log("user_message", user_input, self.ad_mode, self.conversation_id)

        # 2. Pre-ad snapshot
        C_pre = list(self.messages)

        # 3. Ad injection (pre-call: system overrides)
        ad = get_ad()
        injector = get_injector(self.ad_mode)
        injection = injector.inject(ad, self.messages)

        # 4. LLM call
        assistant_reply = self._call_llm(injection.system_overrides)

        # 5. Record assistant reply
        self.messages.append({"role": "assistant", "content": assistant_reply})
        self.logger.log("assistant_reply", assistant_reply, self.ad_mode, self.conversation_id)

        # 6. Post-response injection (in-chat ads)
        for msg in injection.messages_to_append:
            self.messages.append(msg)
            self.logger.log("ad_injected", msg["content"], self.ad_mode, self.conversation_id)

        # 7. Post-ad snapshot
        C_post = list(self.messages)

        # 8. Attention shift
        shift = compute_attention_shift(
            C_pre, C_post, estimator=self.attention_estimator
        )
        self.logger.log(
            "attention_shift",
            {"divergence": shift.divergence, "method": shift.method},
            self.ad_mode,
            self.conversation_id,
        )

        return TurnResult(
            assistant_reply=assistant_reply,
            injection=injection,
            attention_shift=shift,
        )

    def reset(self):
        """Clear conversation for a new session."""
        self.messages = []
        self.conversation_id = str(uuid.uuid4())
        self.logger.log("session_reset", {}, self.ad_mode, self.conversation_id)

    # ── Private ───────────────────────────────────────────────

    def _call_llm(self, system_overrides: List[Dict[str, str]]) -> str:
        """Send messages + any system overrides to the vLLM backend."""
        msgs = list(self.messages)
        msgs.extend(system_overrides)

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model,
                    "messages": msgs,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"⚠️ LLM Error: {e}"
