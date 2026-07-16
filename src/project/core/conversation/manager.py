"""
Conversation Manager.

Owns the multi-turn conversation state and orchestrates the
per-turn pipeline:

    user message → system prompt → (ad overrides) → LLM call
    → assistant reply → post-response ad injection → intent tracking

Design principles (from paper §6.1):
  - A *fixed* base system prompt ensures cross-participant consistency.
  - Task-specific context is appended via the system prompt extension.
  - Turn tracking enforces the trial structure (min / max turns).

The UI layer calls `process_user_message()` or
`process_user_message_stream()` and renders the result.
It should never talk to the LLM directly.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import List, Dict, Optional, Callable, Any, Generator
from dataclasses import dataclass

from core.config import (
    BASE_SYSTEM_PROMPT,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    AD_INJECTION_TURNS,
    FINISH_BUTTON_VISIBLE_FROM_TURN,
    LOG_DIR,
)
from core.ad_injection import get_ad, get_injector
from core.ad_injection.models import Ad, AdRetrievalResult, InjectionResult
from core.logger.payload import build_retrieval_log_data, compact_event_data
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
    time_to_reply_ms: Optional[float] = None  # user delay since last assistant msg (set by UI)
    intent_label: str = ""                   # ThradBERT intent classification for this turn
    continued: bool = True                   # did the user send another message after this turn?


@dataclass
class TurnResult:
    """Everything the UI needs after one conversational turn."""
    assistant_reply: str
    injection: InjectionResult
    turn_number: int = 0
    can_end: bool = False
    must_end: bool = False
    error: Optional[str] = None


# ── Shared thread pool for CPU-bound post-turn work ───────────
# Used for BERT intent classification and future modality processing
# (EEG markers, eye-tracking AOI, etc.).
# Daemon threads — die with main. Max 4 workers for CPU tasks.
_CPU_POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix="turn-cpu")


# ── Conversation Manager ──────────────────────────────────────

class ConversationManager:
    """
    Stateful manager for a single conversation trial.

    Parameters
    ----------
    ad_mode : advertising paradigm key (e.g. ``"inline_persuasive"``).
    model : HuggingFace model id served by vLLM.
    temperature : sampling temperature.
    max_tokens : max new tokens per response.
    task : optional task definition for this trial.
    llm_client : LLM backend client instance.
    logger : experiment logger instance.
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
        min_turns: int = MIN_TURNS_PER_TRIAL,
        max_turns: int = MAX_TURNS_PER_TRIAL,
        finish_from: int | None = None,
        ad_turns: Optional[List[int]] = None,
        force_ad: bool = False,
        use_rag: Optional[bool] = None,
        dry_run: bool = False,
    ):
        self.ad_mode = ad_mode
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.task = task
        self.dry_run = dry_run
        self.llm = llm_client or LLMClient(mock=dry_run)
        self.logger = logger or ExperimentLogger(log_dir=LOG_DIR)
        self.min_turns = min_turns
        self.max_turns = max_turns
        self.finish_from: int = finish_from if finish_from is not None else FINISH_BUTTON_VISIBLE_FROM_TURN
        self.ad_turns: List[int] = ad_turns if ad_turns is not None else list(AD_INJECTION_TURNS)
        # Dev overrides — None means "respect module-level defaults"
        self._force_ad: bool = force_ad
        self._ad_backend: str | None = (
            "rag" if use_rag is True else "mock" if use_rag is False else None
        )

        self.conversation_id: str = str(uuid.uuid4())
        self.messages: List[Dict[str, str]] = []
        self._system_prompt = self._build_system_prompt()
        self.system_prompt_hash: str = hashlib.sha256(self._system_prompt.encode()).hexdigest()[:16]

        # ── Per-turn metrics (paper DVs) ──────────────────────
        self.turn_metrics: List[TurnMetrics] = []
        self.ad_turns_actual: List[int] = []          # turns where ads were actually injected
        self.ads_by_turn: Dict[int, List[Ad]] = {}    # candidates shown per injection turn
        self.trial_start_ts: str = datetime.now().isoformat()
        self._last_assistant_ts: Optional[float] = None  # perf_counter of last assistant reply
        self._ad_awareness_override: List[Dict[str, str]] = []  # persistent after ad injection
        # Snapshot of injected ad + pipeline info at injection time (for ad recall survey).
        self._injected_ad_info: Optional[Dict[str, Any]] = None
        # ── Intent tracking (ThradBERT, paper §RQ3) ──────────
        # initial_intent: classified from task prompt at conversation start
        # per-turn intent: classified each turn from compact context
        self.initial_intent: str = self._classify_initial_intent()
        self.intent_history: List[str] = []           # one label per user turn
        self.logger.log(
            "conversation_started",
            {
                "initial_intent": self.initial_intent,
                "task_id": self.task.id if self.task else None,
            },
            self.ad_mode,
            self.conversation_id,
            source="system",
            turn=0,
        )

        # ── Modality hooks (EEG, eye-tracking, etc.) ──────────
        # Each hook is called with (turn: int, ad_injected: bool, ad: Ad|None)
        # in the thread pool after LLM reply — non-blocking.
        self._modality_hooks: List[Callable[[int, bool, Any], None]] = []
        self.last_retrieval: Optional[AdRetrievalResult] = None
        self.last_injection: InjectionResult = InjectionResult()
        # Ad mode active when last_retrieval was produced (guards UI after dev mode switches).
        self.last_retrieval_ad_mode: Optional[str] = None

    @property
    def ad_backend(self) -> str | None:
        """Active ad backend override (mock/rag), or None for config default."""
        return self._ad_backend

    @property
    def injected_ad_info(self) -> dict | None:
        """Snapshot of the injected ad + pipeline info (set at injection turn).

        Returns None if no ad has been injected yet.  Used by participant.py
        to build the ad_info dict for the recall survey at condition end.
        """
        return self._injected_ad_info

    # ── Modality Registration ─────────────────────────────────

    def register_modality_hook(self, hook: Callable[[int, bool, Any], None]) -> None:
        """
        Register a callback for parallel post-turn processing.

        Hooks run in the CPU thread pool AFTER the LLM reply is ready,
        in parallel with intent classification.

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
          3. Determine ad injection
          4. Call LLM (system prompt + ad overrides + conversation)
          5. Record assistant reply
          6. Post-response injection (in-chat ads)
          7. Fire modality hooks
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
            "user_starts_typing",
            {"time_to_reply_ms": time_to_reply_ms},
            turn=current_turn,
        )
        self.logger.log(
            "user_message",
            compact_event_data(
                {
                    "content": user_input,
                    "msg_len": len(user_input),
                    "time_to_reply_ms": time_to_reply_ms,
                },
                turn=current_turn,
            ),
            self.ad_mode,
            self.conversation_id,
            source="user",
            turn=current_turn,
        )

        # 3 — intent (ThradBERT) before retrieval so JSONL retrieval rows carry intent_label
        turn_intent = self._classify_turn_intent(user_input)
        self.intent_history.append(turn_intent)
        self.logger.log(
            "intent_classified",
            compact_event_data({"intent_label": turn_intent}, turn=current_turn),
            self.ad_mode,
            self.conversation_id,
            source="system",
            turn=current_turn,
        )

        # 4 — ad injection decision (timed for logging)
        inject_ad = self.should_inject_ad
        retrieval: Optional[AdRetrievalResult] = None
        if inject_ad:
            retrieval_t0 = time.perf_counter()
            retrieval = get_ad(
                query=user_input,
                context=self.messages,
                backend=self._ad_backend,
                categories=self.task.relevant_categories if self.task else None,
                task_prompt=self.task.participant_prompt if self.task else "",
            )
            self.last_retrieval = retrieval
            self.last_retrieval_ad_mode = self.ad_mode if retrieval and retrieval.has_ads else None
            retrieval_latency_ms = (time.perf_counter() - retrieval_t0) * 1000.0
            ad = retrieval.primary

            if ad is not None:
                self.logger.log(
                    "retrieval",
                    build_retrieval_log_data(
                        query=user_input,
                        turn=current_turn,
                        retrieval=retrieval,
                        intent_label=turn_intent,
                        retrieval_latency_ms=retrieval_latency_ms,
                        retrieval_backend=self._ad_backend or "default",
                    ),
                    self.ad_mode,
                    self.conversation_id,
                    source="retrieval",
                    turn=current_turn,
                )

        # 4a — inject ad into conversation (skip in dry_run — banner only)
        injector = get_injector(self.ad_mode) if inject_ad else None
        injection = (
            injector.inject(retrieval, self.messages)
            if injector and retrieval and retrieval.has_ads and not self.dry_run
            else InjectionResult()
        )
        self.last_injection = injection

        # 4a.1 — persist ad awareness for all subsequent turns
        if inject_ad and retrieval and retrieval.primary and not self.dry_run:
            from core.config import POST_INJECTION_AWARENESS_PROMPT as AD_AWARENESS_SYSTEM_PROMPT
            awareness = AD_AWARENESS_SYSTEM_PROMPT.format(
                ad_title=retrieval.primary.title,
                ad_text=retrieval.primary.text[:300],
            )
            self._ad_awareness_override = [
                {"role": "system", "content": awareness}
            ]
            # Snapshot ad content + pipeline info for ad recall survey
            self._injected_ad_info = {
                "title": retrieval.primary.title,
                "text": retrieval.primary.text,
                "cta": retrieval.primary.cta,
                "question": retrieval.primary.question,
                "source_item_id": retrieval.primary.source_item_id,
                "relevance_score": retrieval.primary.relevance_score,
                "ad_mode": self.ad_mode,
                "ad_turn": current_turn,
                "query": user_input,
                "intent_label": turn_intent,
                "retrieval_backend": self._ad_backend or "default",
                "retrieval_latency_ms": round(retrieval_latency_ms, 1),
                "candidate_count": len(retrieval.ads) if retrieval.ads else 0,
                "candidate_titles": [a.title for a in retrieval.ads] if retrieval.ads else [],
            }

        # 4b — log ad_injected event (which ad was actually shown)
        if inject_ad and retrieval and retrieval.primary and not self.dry_run:
            _position = "inline" if self.ad_mode == "inline_persuasive" else "block"
            self.logger.log(
                "ad_injected",
                compact_event_data(
                    {
                        "ad_id": retrieval.primary.source_item_id,
                        "product_id": retrieval.primary.source_item_id,
                        "ad_title": retrieval.primary.title,
                        "ad_text": retrieval.primary.text[:200],
                        "position": _position,
                        "ad_mode": self.ad_mode,
                    },
                    turn=current_turn,
                ),
                self.ad_mode,
                self.conversation_id,
                source="system",
                turn=current_turn,
            )
            self.logger.log(
                "ad_inserted",
                {"turn": current_turn},
                turn=current_turn,
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
            compact_event_data(
                {
                    "content": assistant_reply,
                    "msg_len": len(assistant_reply),
                    "llm_latency_ms": round(llm_latency_ms, 1),
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "system_prompt_hash": self.system_prompt_hash,
                },
                turn=current_turn,
            ),
            self.ad_mode,
            self.conversation_id,
            source="model",
            turn=current_turn,
        )
        self.logger.log(
            f"turn_{current_turn}_read",
            {"turn": current_turn},
            turn=current_turn,
        )

        # 7 — record ad injection turn (display handled via InjectionResult, not chat append)
        if inject_ad and retrieval and retrieval.primary:
            self.ad_turns_actual.append(current_turn)
            self.ads_by_turn[current_turn] = list(retrieval.ads)

        # 8 — fire modality hooks in parallel (non-blocking, best-effort)
        for hook in self._modality_hooks:
            _CPU_POOL.submit(hook, current_turn, inject_ad, retrieval.primary if retrieval else None)

        # 9 — record per-turn metrics for offline analysis
        metrics = TurnMetrics(
            turn=current_turn,
            user_msg_len=len(user_input),
            assistant_msg_len=len(assistant_reply),
            llm_latency_ms=round(llm_latency_ms, 1),
            ad_injected=inject_ad and bool(retrieval and retrieval.has_ads),
            ad_title=retrieval.primary.title if (inject_ad and retrieval and retrieval.primary) else None,
            ad_relevance_score=retrieval.primary.relevance_score if (inject_ad and retrieval and retrieval.primary) else None,
            time_to_reply_ms=round(time_to_reply_ms, 1) if time_to_reply_ms is not None else None,
            intent_label=turn_intent,
            continued=True,
        )
        self.turn_metrics.append(metrics)

        return TurnResult(
            assistant_reply=assistant_reply,
            injection=injection,
            turn_number=current_turn,
            can_end=self.can_end,
            must_end=self.must_end,
        )

    def process_user_message_stream(self, user_input: str) -> Generator[str, None, None]:
        """
        Streaming variant of process_user_message.

        Yields tokens as the LLM generates them.  After the generator
        exhausts, self.messages contains the new assistant reply and
        all post-processing (intent tracking, metrics, logging) has
        been completed.

        Callers must iterate the generator to drive the pipeline
        (e.g. via ``st.write_stream()``).
        """
        # 1 — enforce limit
        if self.must_end:
            yield ""
            return

        # ── Compute user reply delay
        time_to_reply_ms: Optional[float] = None
        if self._last_assistant_ts is not None:
            time_to_reply_ms = (time.perf_counter() - self._last_assistant_ts) * 1000.0

        # 2 — user message
        self.messages.append({"role": "user", "content": user_input})
        current_turn = self.turn_count
        self.logger.log(
            "user_starts_typing",
            {"time_to_reply_ms": time_to_reply_ms},
            turn=current_turn,
        )
        self.logger.log(
            "user_message",
            compact_event_data(
                {
                    "content": user_input,
                    "msg_len": len(user_input),
                    "time_to_reply_ms": time_to_reply_ms,
                },
                turn=current_turn,
            ),
            self.ad_mode,
            self.conversation_id,
            source="user",
            turn=current_turn,
        )

        # 3 — intent classification
        turn_intent = self._classify_turn_intent(user_input)
        self.intent_history.append(turn_intent)
        self.logger.log(
            "intent_classified",
            compact_event_data({"intent_label": turn_intent}, turn=current_turn),
            self.ad_mode,
            self.conversation_id,
            source="system",
            turn=current_turn,
        )

        # 4 — ad injection decision
        inject_ad = self.should_inject_ad
        retrieval: Optional[AdRetrievalResult] = None
        if inject_ad:
            retrieval_t0 = time.perf_counter()
            retrieval = get_ad(
                query=user_input,
                context=self.messages,
                backend=self._ad_backend,
                categories=self.task.relevant_categories if self.task else None,
                task_prompt=self.task.participant_prompt if self.task else "",
            )
            self.last_retrieval = retrieval
            self.last_retrieval_ad_mode = self.ad_mode if retrieval and retrieval.has_ads else None
            retrieval_latency_ms = (time.perf_counter() - retrieval_t0) * 1000.0
            ad = retrieval.primary

            if ad is not None:
                self.logger.log(
                    "retrieval",
                    build_retrieval_log_data(
                        query=user_input,
                        turn=current_turn,
                        retrieval=retrieval,
                        intent_label=turn_intent,
                        retrieval_latency_ms=retrieval_latency_ms,
                        retrieval_backend=self._ad_backend or "default",
                    ),
                    self.ad_mode,
                    self.conversation_id,
                    source="retrieval",
                    turn=current_turn,
                )

        # 4a — inject ad into conversation (skip in dry_run — banner only)
        injector = get_injector(self.ad_mode) if inject_ad else None
        injection = (
            injector.inject(retrieval, self.messages)
            if injector and retrieval and retrieval.has_ads and not self.dry_run
            else InjectionResult()
        )
        self.last_injection = injection

        # 4a.1 — persist ad awareness for all subsequent turns
        if inject_ad and retrieval and retrieval.primary and not self.dry_run:
            from core.config import POST_INJECTION_AWARENESS_PROMPT as AD_AWARENESS_SYSTEM_PROMPT
            awareness = AD_AWARENESS_SYSTEM_PROMPT.format(
                ad_title=retrieval.primary.title,
                ad_text=retrieval.primary.text[:300],
            )
            self._ad_awareness_override = [
                {"role": "system", "content": awareness}
            ]
            # Snapshot ad content + pipeline info for ad recall survey
            self._injected_ad_info = {
                "title": retrieval.primary.title,
                "text": retrieval.primary.text,
                "cta": retrieval.primary.cta,
                "question": retrieval.primary.question,
                "source_item_id": retrieval.primary.source_item_id,
                "relevance_score": retrieval.primary.relevance_score,
                "ad_mode": self.ad_mode,
                "ad_turn": current_turn,
                "query": user_input,
                "intent_label": turn_intent,
                "retrieval_backend": self._ad_backend or "default",
                "retrieval_latency_ms": round(retrieval_latency_ms, 1),
                "candidate_count": len(retrieval.ads) if retrieval.ads else 0,
                "candidate_titles": [a.title for a in retrieval.ads] if retrieval.ads else [],
            }

        # 4b — log ad_injected event (which ad was actually shown)
        if inject_ad and retrieval and retrieval.primary and not self.dry_run:
            _position = "inline" if self.ad_mode == "inline_persuasive" else "block"
            self.logger.log(
                "ad_injected",
                compact_event_data(
                    {
                        "ad_id": retrieval.primary.source_item_id,
                        "product_id": retrieval.primary.source_item_id,
                        "ad_title": retrieval.primary.title,
                        "ad_text": retrieval.primary.text[:200],
                        "position": _position,
                        "ad_mode": self.ad_mode,
                    },
                    turn=current_turn,
                ),
                self.ad_mode,
                self.conversation_id,
                source="system",
                turn=current_turn,
            )

        # 5 — LLM call (streaming)
        system_msg = {"role": "system", "content": self._system_prompt}
        all_overrides = list(injection.system_overrides) + list(self._ad_awareness_override)
        msgs = [system_msg] + all_overrides + list(self.messages)

        llm_t0 = time.perf_counter()
        assistant_reply_parts: list[str] = []
        try:
            for chunk in self.llm.chat_stream(msgs, self.model, self.temperature, self.max_tokens):
                assistant_reply_parts.append(chunk)
                yield chunk
        except RuntimeError as e:
            error_text = f"⚠️ {e}"
            assistant_reply_parts.append(error_text)
            yield error_text

        assistant_reply = "".join(assistant_reply_parts)
        llm_latency_ms = (time.perf_counter() - llm_t0) * 1000.0

        # 6 — record assistant reply
        self.messages.append({"role": "assistant", "content": assistant_reply})
        self._last_assistant_ts = time.perf_counter()
        self.logger.log(
            "assistant_reply",
            compact_event_data(
                {
                    "content": assistant_reply,
                    "msg_len": len(assistant_reply),
                    "llm_latency_ms": round(llm_latency_ms, 1),
                    "model": self.model,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "system_prompt_hash": self.system_prompt_hash,
                },
                turn=current_turn,
            ),
            self.ad_mode,
            self.conversation_id,
            source="model",
            turn=current_turn,
        )
        self.logger.log(
            f"turn_{current_turn}_read",
            {"turn": current_turn},
            turn=current_turn,
        )

        # 7 — record ad injection turn
        if inject_ad and retrieval and retrieval.primary:
            self.ad_turns_actual.append(current_turn)
            self.ads_by_turn[current_turn] = list(retrieval.ads)

        # 8 — fire modality hooks in parallel (non-blocking, best-effort)
        for hook in self._modality_hooks:
            _CPU_POOL.submit(hook, current_turn, inject_ad, retrieval.primary if retrieval else None)

        metrics = TurnMetrics(
            turn=current_turn,
            user_msg_len=len(user_input),
            assistant_msg_len=len(assistant_reply),
            llm_latency_ms=round(llm_latency_ms, 1),
            ad_injected=inject_ad and bool(retrieval and retrieval.has_ads),
            ad_title=retrieval.primary.title if (inject_ad and retrieval and retrieval.primary) else None,
            ad_relevance_score=retrieval.primary.relevance_score if (inject_ad and retrieval and retrieval.primary) else None,
            time_to_reply_ms=round(time_to_reply_ms, 1) if time_to_reply_ms is not None else None,
            intent_label=turn_intent,
            continued=True,
        )
        self.turn_metrics.append(metrics)

    def finalize_trial(self, reason: str = "user_ended") -> dict:
        """Mark the last turn as continued=False and return a trial summary dict.

        Call this when the participant ends the conversation (Done button)
        or when max turns is reached (auto-end).

        Parameters
        ----------
        reason : "user_ended" | "max_turns" — why the trial ended.

        Returns
        -------
        dict with continuation stats for logging.
        """
        # ── Set continued=False on the last turn ──────────────
        if self.turn_metrics:
            self.turn_metrics[-1].continued = False

        # ── Compute continuation summary ──────────────────────
        n_turns = len(self.turn_metrics)
        n_ad_turns = sum(1 for m in self.turn_metrics if m.ad_injected)
        n_continued_after_ad = sum(
            1 for m in self.turn_metrics
            if m.ad_injected and m.continued
        )
        n_continued_total = sum(1 for m in self.turn_metrics if m.continued)

        # ── time_to_reply_ms statistics ───────────────────────
        reply_times = [
            m.time_to_reply_ms for m in self.turn_metrics
            if m.time_to_reply_ms is not None
        ]
        avg_reply_ms = sum(reply_times) / len(reply_times) if reply_times else None
        median_reply_ms = sorted(reply_times)[len(reply_times) // 2] if reply_times else None

        summary = {
            "reason": reason,
            "n_turns": n_turns,
            "n_ad_turns": n_ad_turns,
            "n_continued_after_ad": n_continued_after_ad,
            "n_continued_total": n_continued_total,
            "continuation_rate_after_ad": round(n_continued_after_ad / n_ad_turns, 3) if n_ad_turns else None,
            "continuation_rate_overall": round(n_continued_total / n_turns, 3) if n_turns else None,
            "avg_time_to_reply_ms": round(avg_reply_ms, 1) if avg_reply_ms is not None else None,
            "median_time_to_reply_ms": round(median_reply_ms, 1) if median_reply_ms is not None else None,
            "per_turn_continued": [
                {"turn": m.turn, "ad_injected": m.ad_injected, "continued": m.continued}
                for m in self.turn_metrics
            ],
        }

        self.logger.log(
            "trial_end",
            compact_event_data(summary, turn=n_turns),
            self.ad_mode,
            self.conversation_id,
            source="system",
            turn=n_turns,
        )

        return summary

    def clear_ad_display_state(self) -> None:
        """Drop cached retrieval/injection without clearing chat history."""
        self.last_retrieval = None
        self.last_injection = InjectionResult()
        self.last_retrieval_ad_mode = None
        self._ad_awareness_override = []
        self._injected_ad_info = None

    def apply_ad_mode(self, ad_mode: str) -> None:
        """Switch injection style (dev flow); clears stale ads if the mode changed."""
        if ad_mode != self.ad_mode:
            self.ad_mode = ad_mode
            self.clear_ad_display_state()

    def reset(self):
        """Clear conversation for a new trial."""
        self.messages = []
        self.conversation_id = str(uuid.uuid4())
        self.clear_ad_display_state()
        self.logger.log("session_reset", {}, self.ad_mode, self.conversation_id)

    # ── Private ───────────────────────────────────────────────

    def _call_llm(self, system_overrides: List[Dict[str, str]]) -> str:
        """
        Build the full message list and call the LLM.

        Order: system prompt → ad overrides → persistent ad awareness → conversation history.
        """
        system_msg = {"role": "system", "content": self._system_prompt}
        all_overrides = list(system_overrides) + list(self._ad_awareness_override)
        msgs = [system_msg] + all_overrides + list(self.messages)
        try:
            return self.llm.chat(msgs, self.model, self.temperature, self.max_tokens)
        except RuntimeError as e:
            return f"⚠️ {e}"
