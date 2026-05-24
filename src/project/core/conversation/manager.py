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

import time
import uuid
from concurrent.futures import ThreadPoolExecutor, Future
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field

from core.config import (
    BASE_SYSTEM_PROMPT,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    AD_INJECTION_TURNS,
    INTENT_MAX_SEQ_LENGTH,
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
from core.retrieval.stages.intent import classify_intent, truncate_to_tokens


# ── Turn result (returned to the UI) ─────────────────────────

@dataclass
class TurnMetrics:
    """Per-turn behavioural metrics logged for offline analysis."""
    turn: int
    user_msg_len: int                        # chars in user message
    assistant_msg_len: int                    # chars in assistant reply
    llm_latency_ms: float                    # LLM call wall-clock time in ms
    ad_injected: bool                        # was an ad injected this turn?
    ad_title: Optional[str] = None           # ad title if injected
    ad_relevance_score: Optional[float] = None  # retrieval relevance score
    attention_divergence: Optional[float] = None  # attention shift KL
    time_to_reply_ms: Optional[float] = None  # user delay since last assistant msg (set by UI)
    intent_label: str = ""                   # ThradBERT intent classification for this turn


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


# ── Shared thread pool for CPU-bound post-turn work ───────────
# Used for BERT intent classification, attention shift, and future
# modality processing (EEG markers, eye-tracking AOI, etc.).
# Daemon threads — die with main. Max 4 workers for CPU tasks.
_CPU_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="turn-cpu")


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
        min_turns: int = MIN_TURNS_PER_TRIAL,
        max_turns: int = MAX_TURNS_PER_TRIAL,
        ad_turns: Optional[List[int]] = None,
        force_ad: bool = False,
        use_rag: Optional[bool] = None,
    ):
        self.ad_mode = ad_mode
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.task = task
        self.llm = llm_client or LLMClient()
        self.logger = logger or ExperimentLogger()
        self.attention_estimator = attention_estimator
        self.min_turns = min_turns
        self.max_turns = max_turns
        self.ad_turns: List[int] = ad_turns if ad_turns is not None else list(AD_INJECTION_TURNS)
        # Dev overrides — None means "respect module-level defaults"
        self._force_ad: bool = force_ad
        self._ad_backend: str | None = (
            "rag" if use_rag is True else "mock" if use_rag is False else None
        )

        self.conversation_id: str = str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []
        self._system_prompt = self._build_system_prompt()

        # ── Per-turn metrics (paper DVs) ──────────────────────
        self.turn_metrics: List[TurnMetrics] = []
        self.ad_turns_actual: List[int] = []          # turns where ads were actually injected
        self.trial_start_ts: str = datetime.now().isoformat()
        self._last_assistant_ts: Optional[float] = None  # perf_counter of last assistant reply
        # ── Intent tracking (ThradBERT, paper §RQ3) ──────────
        # initial_intent: classified from task prompt at conversation start
        # per-turn intent: classified each turn from compact context
        self.initial_intent: str = self._classify_initial_intent()
        self.intent_history: List[str] = []           # one label per user turn

        # ── Modality hooks (EEG, eye-tracking, etc.) ──────────
        # Each hook is called with (turn: int, ad_injected: bool, ad: Ad|None)
        # in the thread pool after LLM reply — non-blocking.
        self._modality_hooks: List[Callable[[int, bool, Any], None]] = []

    # ── Modality Registration ─────────────────────────────────

    def register_modality_hook(self, hook: Callable[[int, bool, Any], None]) -> None:
        """
        Register a callback for parallel post-turn processing.

        Hooks run in the CPU thread pool AFTER the LLM reply is ready,
        in parallel with attention shift and intent classification.

        Signature: hook(turn: int, ad_injected: bool, ad: Ad | None)

        Use cases:
          - EEG marker emission (LSL push)
          - Eye-tracking AOI fixation logging
          - Physiological signal snapshotting
        """
        self._modality_hooks.append(hook)

    # ── Intent Classification ─────────────────────────────────

    def _classify_initial_intent(self) -> str:
        """Classify the task prompt to get the initial (s₀) intent label."""
        if self.task and self.task.participant_prompt:
            return classify_intent(self.task.participant_prompt)
        return ""

    def _classify_turn_intent(self, user_input: str) -> str:
        """
        Classify the current conversation intent (sₜ) for this turn.

        Token budget allocation (510 tokens total, 2 reserved for [CLS]/[SEP]):
          - Current user message: 50% (255 tokens) — strongest signal
          - Recent history:       35% (178 tokens) — conversation drift
          - Task/system prompt:   15% (77 tokens)  — initial anchor

        Truncation is done at the WordPiece token level using the
        ThradBERT tokenizer, so we never exceed the model's 512 context.
        """
        MAX_TOKENS = 510  # 512 - 2 special tokens ([CLS] + [SEP])
        CURRENT_BUDGET = int(MAX_TOKENS * 0.50)   # 255
        HISTORY_BUDGET = int(MAX_TOKENS * 0.35)   # 178
        TASK_BUDGET    = MAX_TOKENS - CURRENT_BUDGET - HISTORY_BUDGET  # 77

        # 1. Current user message (highest priority)
        current = truncate_to_tokens(user_input, CURRENT_BUDGET)

        # 2. Task prompt (context anchor)
        task_text = ""
        if self.task and self.task.participant_prompt:
            task_text = truncate_to_tokens(self.task.participant_prompt, TASK_BUDGET)

        # 3. Recent history — last N user messages before current turn
        #    Split budget evenly among last 2-3 messages
        prev_user_msgs = [
            m["content"] for m in self.messages if m["role"] == "user"
        ][:-1]  # exclude current (already appended before this call)
        recent = prev_user_msgs[-3:]  # last 3 for richer context
        history_parts: List[str] = []
        if recent:
            per_msg = HISTORY_BUDGET // len(recent)
            for msg in recent:
                history_parts.append(truncate_to_tokens(msg, per_msg))

        # Assemble: task | history | current
        parts: List[str] = []
        if task_text:
            parts.append(task_text)
        for hp in history_parts:
            parts.append(hp)
        parts.append(current)

        return classify_intent(" ".join(parts))

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
        return self.turn_count >= self.min_turns

    @property
    def must_end(self) -> bool:
        """Whether the trial has reached the maximum number of turns."""
        return self.turn_count >= self.max_turns

    @property
    def is_ad_turn(self) -> bool:
        """Whether the *next* user turn triggers an ad."""
        return (self.turn_count + 1) in self.ad_turns

    @property
    def should_inject_ad(self) -> bool:
        """Whether the current turn (just completed) is an ad injection turn.

        When force_ad=True (dev mode ?force_ad=1), every turn injects an ad.
        """
        if self._force_ad:
            return True
        return self.turn_count in self.ad_turns

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

        # ── Compute user reply delay (time since last assistant message)
        time_to_reply_ms: Optional[float] = None
        if self._last_assistant_ts is not None:
            time_to_reply_ms = (time.perf_counter() - self._last_assistant_ts) * 1000.0

        # 2 — user message
        self.messages.append({"role": "user", "content": user_input})
        current_turn = self.turn_count
        self.logger.log(
            "user_message",
            {"content": user_input, "turn": current_turn,
             "msg_len": len(user_input),
             "time_to_reply_ms": time_to_reply_ms},
            self.ad_mode,
            self.conversation_id,
            source="user",
            turn=current_turn,
        )

        # 3 — pre-ad snapshot
        C_pre = list(self.messages)

        # 4 — ad injection decision (timed for logging)
        inject_ad = self.should_inject_ad
        ad = None
        if inject_ad:
            retrieval_t0 = time.perf_counter()
            ad = get_ad(query=user_input, context=self.messages, backend=self._ad_backend)
            retrieval_latency_ms = (time.perf_counter() - retrieval_t0) * 1000.0

            # Log retrieval event with full ad metadata
            self.logger.log(
                "retrieval",
                {
                    "query": user_input,
                    "turn": current_turn,
                    "ad_title": ad.title,
                    "ad_item_id": ad.source_item_id,
                    "ad_source": ad.metadata.get("source", "amazon"),
                    "ad_category": ad.metadata.get("category", ""),
                    "ad_relevance_score": ad.relevance_score,
                    "ad_cta": ad.cta,
                    "retrieval_latency_ms": round(retrieval_latency_ms, 1),
                    "retrieval_backend": self._ad_backend or "default",
                },
                self.ad_mode,
                self.conversation_id,
                source="retrieval",
                turn=current_turn,
            )

        injector = get_injector(self.ad_mode) if inject_ad else None
        injection = (
            injector.inject(ad, self.messages)
            if injector and ad
            else InjectionResult()
        )

        # 5 — LLM call (timed)
        llm_t0 = time.perf_counter()
        assistant_reply = self._call_llm(injection.system_overrides)
        llm_latency_ms = (time.perf_counter() - llm_t0) * 1000.0

        # 6 — record assistant reply
        self.messages.append({"role": "assistant", "content": assistant_reply})
        self._last_assistant_ts = time.perf_counter()
        self.logger.log(
            "assistant_reply",
            {"content": assistant_reply, "turn": current_turn,
             "msg_len": len(assistant_reply),
             "llm_latency_ms": round(llm_latency_ms, 1)},
            self.ad_mode,
            self.conversation_id,
            source="model",
            turn=current_turn,
        )

        # 7 — post-response injection
        if inject_ad:
            self.ad_turns_actual.append(current_turn)
            for msg in injection.messages_to_append:
                self.messages.append(msg)
                self.logger.log(
                    "ad_injected",
                    {
                        "content": msg["content"],
                        "turn": current_turn,
                        "ad_mode": self.ad_mode,
                        "ad_title": ad.title if ad else None,
                        "ad_item_id": ad.source_item_id if ad else None,
                        "ad_source": ad.metadata.get("source", "amazon") if ad else None,
                        "ad_relevance_score": ad.relevance_score if ad else None,
                    },
                    self.ad_mode,
                    self.conversation_id,
                    source="system",
                    turn=current_turn,
                )

        # 8 — post-ad snapshot
        C_post = list(self.messages)

        # 9+10 — PARALLEL: attention shift + intent classification
        # These are CPU-bound (numpy divergence + BERT forward pass) and
        # independent of each other. Run in thread pool to avoid blocking
        # the main thread (Streamlit / UI / future modality streams).
        shift_future: Future = _CPU_POOL.submit(
            compute_attention_shift, C_pre, C_post, self.attention_estimator
        )
        intent_future: Future = _CPU_POOL.submit(
            self._classify_turn_intent, user_input
        )

        # Fire modality hooks in parallel (non-blocking, best-effort)
        for hook in self._modality_hooks:
            _CPU_POOL.submit(hook, current_turn, inject_ad, ad)

        # Collect parallel results
        shift = shift_future.result()
        turn_intent = intent_future.result()
        self.intent_history.append(turn_intent)

        # Log attention shift (after result is ready)
        self.logger.log(
            "attention_shift",
            {
                "divergence": shift.divergence,
                "method": shift.method,
                "turn": current_turn,
            },
            self.ad_mode,
            self.conversation_id,
            source="system",
            turn=current_turn,
        )

        # 11 — record per-turn metrics for offline analysis
        metrics = TurnMetrics(
            turn=current_turn,
            user_msg_len=len(user_input),
            assistant_msg_len=len(assistant_reply),
            llm_latency_ms=round(llm_latency_ms, 1),
            ad_injected=inject_ad,
            ad_title=ad.title if (inject_ad and ad) else None,
            ad_relevance_score=ad.relevance_score if (inject_ad and ad) else None,
            attention_divergence=shift.divergence if shift else None,
            time_to_reply_ms=round(time_to_reply_ms, 1) if time_to_reply_ms is not None else None,
            intent_label=turn_intent,
        )
        self.turn_metrics.append(metrics)

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
