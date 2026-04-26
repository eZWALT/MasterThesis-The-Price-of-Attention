"""
Conversation Manager.

Owns the multi-turn conversation state and orchestrates the
per-turn pipeline:

    user message → system prompt → (ad overrides) → LLM call
    → assistant reply → post-response ad injection → attention shift

Design principles (from paper §6.1):
  - A *fixed* base system prompt ensures cross-participant consistency.
  - Task-specific context is appended via the system prompt extension.
  - Turn tracking enforces the trial structure (min / max turns).

The UI layer calls `process_user_message()` and renders the result.
It should never talk to the LLM directly.
"""

from __future__ import annotations

import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass

from core.config import (
    BASE_SYSTEM_PROMPT,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    AD_INJECTION_TURNS,
)
from core.ad_injection import Ad, InjectionResult, get_ad, get_injector
from core.attention_shift import (
    compute_attention_shift,
    AttentionShiftResult,
    AttentionEstimator,
)
from core.logger import ExperimentLogger
from core.experiment.tasks import TaskDefinition
from core.conversation.llm_client import LLMClient


# ── Turn result (returned to the UI) ─────────────────────────

@dataclass
class TurnResult:
    """Everything the UI needs after one conversational turn."""
    assistant_reply: str
    injection: InjectionResult
    turn_number: int = 0
    can_end: bool = False
    must_end: bool = False
    attention_shift: Optional[AttentionShiftResult] = None
    error: Optional[str] = None


# ── Conversation Manager ──────────────────────────────────────

class ConversationManager:
    """
    Stateful manager for a single conversation trial.

    Parameters
    ----------
    ad_mode : advertising paradigm key (e.g. ``"2_in_chat"``).
    model : HuggingFace model id served by vLLM.
    temperature : sampling temperature.
    max_tokens : max new tokens per response.
    task : optional task definition for this trial.
    llm_client : LLM backend client instance.
    logger : experiment logger instance.
    attention_estimator : optional custom estimator for P(Z|C).
    """

    def __init__(
        self,
        ad_mode: str,
        model: str,
        temperature: float,
        max_tokens: int,
        task: Optional[TaskDefinition] = None,
        llm_client: LLMClient | None = None,
        logger: ExperimentLogger | None = None,
        attention_estimator: AttentionEstimator | None = None,
    ):
        self.ad_mode = ad_mode
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.task = task
        self.llm = llm_client or LLMClient()
        self.logger = logger or ExperimentLogger()
        self.attention_estimator = attention_estimator

        self.conversation_id: str = str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []
        self._system_prompt = self._build_system_prompt()

    # ── System Prompt ─────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        """
        Construct the full system prompt.

        Always starts with BASE_SYSTEM_PROMPT for cross-participant
        consistency.  If a task is assigned, its context-specific
        extension is appended.
        """
        parts = [BASE_SYSTEM_PROMPT]
        if self.task and self.task.system_prompt_extension:
            parts.append(self.task.system_prompt_extension)
        return " ".join(parts)

    @property
    def system_prompt(self) -> str:
        return self._system_prompt

    # ── Turn Tracking ─────────────────────────────────────────

    @property
    def turn_count(self) -> int:
        """Number of completed user turns (user messages sent)."""
        return sum(1 for m in self.messages if m["role"] == "user")

    @property
    def can_end(self) -> bool:
        """Whether the trial has reached the minimum number of turns."""
        return self.turn_count >= MIN_TURNS_PER_TRIAL

    @property
    def must_end(self) -> bool:
        """Whether the trial has reached the maximum number of turns."""
        return self.turn_count >= MAX_TURNS_PER_TRIAL

    @property
    def is_ad_turn(self) -> bool:
        """Whether the *next* user turn triggers an ad."""
        return (self.turn_count + 1) in AD_INJECTION_TURNS

    @property
    def should_inject_ad(self) -> bool:
        """Whether the current turn (just completed) is an ad injection turn."""
        return self.turn_count in AD_INJECTION_TURNS

    # ── Public API ────────────────────────────────────────────

    def process_user_message(self, user_input: str) -> TurnResult:
        """
        Full pipeline for one user turn.

        Steps:
          1. Enforce turn limit
          2. Record user message
          3. Snapshot C_pre
          4. Determine ad injection
          5. Call LLM (system prompt + ad overrides + conversation)
          6. Record assistant reply
          7. Post-response injection (in-chat ads)
          8. Snapshot C_post
          9. Compute attention shift
        """
        # 1 — enforce limit
        if self.must_end:
            return TurnResult(
                assistant_reply="",
                injection=InjectionResult(),
                turn_number=self.turn_count,
                can_end=True,
                must_end=True,
                error="Trial has reached the maximum number of turns.",
            )

        # 2 — user message
        self.messages.append({"role": "user", "content": user_input})
        current_turn = self.turn_count
        self.logger.log(
            "user_message",
            {"content": user_input, "turn": current_turn},
            self.ad_mode,
            self.conversation_id,
        )

        # 3 — pre-ad snapshot
        C_pre = list(self.messages)

        # 4 — ad injection decision
        inject_ad = self.should_inject_ad
        ad = get_ad() if inject_ad else None
        injector = get_injector(self.ad_mode) if inject_ad else None
        injection = (
            injector.inject(ad, self.messages)
            if injector and ad
            else InjectionResult()
        )

        # 5 — LLM call
        assistant_reply = self._call_llm(injection.system_overrides)

        # 6 — record assistant reply
        self.messages.append({"role": "assistant", "content": assistant_reply})
        self.logger.log(
            "assistant_reply",
            {"content": assistant_reply, "turn": current_turn},
            self.ad_mode,
            self.conversation_id,
        )

        # 7 — post-response injection
        if inject_ad:
            for msg in injection.messages_to_append:
                self.messages.append(msg)
                self.logger.log(
                    "ad_injected",
                    {
                        "content": msg["content"],
                        "turn": current_turn,
                        "ad_mode": self.ad_mode,
                    },
                    self.ad_mode,
                    self.conversation_id,
                )

        # 8 — post-ad snapshot
        C_post = list(self.messages)

        # 9 — attention shift
        shift = compute_attention_shift(
            C_pre, C_post, estimator=self.attention_estimator,
        )
        self.logger.log(
            "attention_shift",
            {
                "divergence": shift.divergence,
                "method": shift.method,
                "turn": current_turn,
            },
            self.ad_mode,
            self.conversation_id,
        )

        return TurnResult(
            assistant_reply=assistant_reply,
            injection=injection,
            turn_number=current_turn,
            can_end=self.can_end,
            must_end=self.must_end,
            attention_shift=shift,
        )

    def reset(self):
        """Clear conversation for a new trial."""
        self.messages = []
        self.conversation_id = str(uuid.uuid4())
        self.logger.log("session_reset", {}, self.ad_mode, self.conversation_id)

    # ── Private ───────────────────────────────────────────────

    def _call_llm(self, system_overrides: List[Dict[str, str]]) -> str:
        """
        Build the full message list and call the LLM.

        Order: system prompt → ad overrides → conversation history.
        """
        system_msg = {"role": "system", "content": self._system_prompt}
        msgs = [system_msg] + system_overrides + list(self.messages)
        try:
            return self.llm.chat(msgs, self.model, self.temperature, self.max_tokens)
        except RuntimeError as e:
            return f"⚠️ {e}"
