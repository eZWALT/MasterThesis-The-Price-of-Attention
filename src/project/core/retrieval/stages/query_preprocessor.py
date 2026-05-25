"""
Stage 0-pre A — Conversation Context Summarizer
Stage 0-pre B — Query Expansion (HyDE / expand / none)

These two stages run BEFORE DenseRetriever (Stage 2) to enrich the query
signal fed into the vector index.

Data flow
---------
  state.context  ──► ContextSummaryStage  ──► state.context_summary
                                                      │
  state.query ────────────────────────────────────────┤
                                                      ▼
                              QueryExpansionStage (mode: hyde | expand | none)
                                                      │
                                                      ▼
                                          state.expanded_query
                                                      │
                                                      ▼
                              DenseRetriever  (embeds expanded_query or query)


ContextSummaryStage
-------------------
  Reads  : state.context (conversation history as list of {role, content} dicts)
  Writes : state.context_summary (one-sentence intent string)
  Config : USE_CONTEXT_SUMMARY (env: CONTEXT_SUMMARY=1)
  Prompt : CONTEXT_SUMMARY_PROMPT

  Only fires when the conversation has ≥ 2 turns (one user, one assistant).
  On single-turn conversations the raw query carries enough signal on its own.

QueryExpansionStage
-------------------
  Reads  : state.query, state.context_summary
  Writes : state.expanded_query
  Config : QUERY_EXPANSION_MODE (env: QUERY_EXPANSION_MODE=hyde|expand|none)
  Prompts: HYDE_PROMPT (mode="hyde"), QUERY_EXPANSION_PROMPT (mode="expand")

  Modes:
    none   — pass-through; state.expanded_query stays empty so DenseRetriever
             falls back to state.query.
    hyde   — generates a hypothetical product description and embeds that
             instead of the raw query; shifts the query vector closer to the
             catalog's document distribution (Gao et al., 2022).
    expand — LLM rewrites the query into a richer keyword-diverse form;
             useful when the user turn is short or ambiguous.

Adding both stages to the pipeline
-----------------------------------
    from core.retrieval.stages.query_preprocessor import (
        ContextSummaryStage,
        QueryExpansionStage,
    )

    pipeline = AdRetrievalPipeline(
        catalog=catalog,
        stages=[
            ContextSummaryStage(),    # <- stage 0a (optional, before intent)
            QueryExpansionStage(),    # <- stage 0b (optional, before dense)
            IntentClassifier(),
            DenseRetriever(catalog, embedding_model=embed),
            HybridRefiner(),
            Reranker(),
            AdFormatter(),
            SummarizationStage(),     # <- existing stage 6
        ],
    )
"""

from __future__ import annotations

from typing import Dict, List

from core.config import (
    CONTEXT_SUMMARY_PROMPT,
    CONTEXT_SUMMARY_MIN_TURNS,
    CONTEXT_SUMMARY_MAX_TOKENS,
    CONTEXT_SUMMARY_TEMPERATURE,
    HYDE_PROMPT,
    HYDE_MAX_TOKENS,
    HYDE_TEMPERATURE,
    HYDE_TOKENS_PER_DOC,
    QUERY_EXPANSION_PROMPT,
    QUERY_EXPANSION_MODE,
    QUERY_EXPANSION_LOG_PREVIEW_CHARS,
    QUERY_EXPAND_MAX_TOKENS,
    QUERY_EXPAND_TEMPERATURE,
    USE_CONTEXT_SUMMARY,
)
from core.retrieval.hyde import (
    effective_hyde_num_docs,
    hyde_generation_max_tokens,
    parse_hyde_documents,
)
from core.log import logger
from core.retrieval.stages.base import PipelineStage
from core.retrieval.stages.preprocess_llm import preprocess_llm_chat
from core.retrieval.stages.state import PipelineState


def _preview(text: str, max_chars: int) -> str:
    one_line = " ".join((text or "").split())
    if max_chars <= 0 or len(one_line) <= max_chars:
        return one_line
    return one_line[: max_chars - 1] + "…"


def _context_block_for_hyde(state: PipelineState) -> str:
    """Conversation text for HyDE — one LLM call, no separate summary pass."""
    if state.context_summary:
        return state.context_summary
    if not state.context:
        return "(none)"
    lines = []
    for msg in state.context[-6:]:
        role = msg.get("role", "user").capitalize()
        content = (msg.get("content") or "").strip()
        if content:
            lines.append(f"{role}: {content}")
    return "\n".join(lines) if lines else "(none)"


# ══════════════════════════════════════════════════════════════════════════════
# Stage 0-pre A — Conversation Context Summarizer
# ══════════════════════════════════════════════════════════════════════════════

class ContextSummaryStage(PipelineStage):
    """
    Compresses the conversation history into a single intent sentence.

    The summary is stored in ``state.context_summary`` and is consumed by
    ``QueryExpansionStage`` in the same pipeline pass.  It is *not* used as
    the embedding target directly — that is the job of QueryExpansionStage.

    Config keys (core.config)
    -------------------------
    USE_CONTEXT_SUMMARY : bool — if False, stage is a transparent pass-through.
    CONTEXT_SUMMARY_PROMPT : str template with {history}.

    Parameters
    ----------
    enabled : override for USE_CONTEXT_SUMMARY at construction time.
              Pass True/False to force-enable/disable in unit tests.
    """

    def __init__(self, enabled: bool | None = None) -> None:
        self._enabled: bool = (
            USE_CONTEXT_SUMMARY if enabled is None else enabled
        )

    # ── PipelineStage interface ───────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if not self._enabled:
            return state

        if len(state.context) < CONTEXT_SUMMARY_MIN_TURNS:
            logger.debug(
                "ContextSummaryStage: skipped — only {} turns in context",
                len(state.context),
            )
            return state

        history = self._format_history(state.context)
        prompt = CONTEXT_SUMMARY_PROMPT.format(history=history)

        try:
            summary = preprocess_llm_chat(
                prompt,
                temperature=CONTEXT_SUMMARY_TEMPERATURE,
                max_tokens=CONTEXT_SUMMARY_MAX_TOKENS,
            )
            state.context_summary = summary
        except Exception as exc:
            logger.opt(exception=True).warning(
                "ContextSummaryStage: LLM call failed, context_summary left empty — {}",
                exc,
            )

        return state

    # ── private ──────────────────────────────────────────────────────────

    @staticmethod
    def _format_history(context: List[Dict[str, str]]) -> str:
        """Converts message list to a plain-text dialogue string."""
        lines = []
        for msg in context:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "").strip()
            lines.append(f"{role}: {content}")
        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Stage 0-pre B — Query Expansion
# ══════════════════════════════════════════════════════════════════════════════

class QueryExpansionStage(PipelineStage):
    """
    Transforms ``state.query`` into a richer ``state.expanded_query``.

    The expansion mode is controlled by ``QUERY_EXPANSION_MODE`` (config /
    env var) or overridden at construction time.

    Modes
    -----
    none   — no-op; DenseRetriever falls back to state.query unchanged.
    hyde   — generates a *hypothetical product description* and sets that
             as expanded_query; embedding a document (rather than a short
             query) shifts the vector closer to the catalog distribution.
    expand — LLM rewrites the query into a longer, keyword-diverse form
             suitable for semantic search.

    Config keys (core.config)
    -------------------------
    QUERY_EXPANSION_MODE : str — "none" | "hyde" | "expand"
    HYDE_PROMPT          : str template with {query}, {context_summary}
    QUERY_EXPANSION_PROMPT : str template with {query}, {context_summary}

    Parameters
    ----------
    mode : override for QUERY_EXPANSION_MODE at construction time.
           Pass "hyde", "expand", or "none" to force a mode in tests.
    """

    _VALID_MODES = frozenset({"none", "hyde", "expand"})

    def __init__(self, mode: str | None = None) -> None:
        raw = (QUERY_EXPANSION_MODE if mode is None else mode).lower()
        if raw not in self._VALID_MODES:
            logger.warning(
                "QueryExpansionStage: unknown mode '{}', defaulting to 'none'", raw
            )
            raw = "none"
        self._mode: str = raw

    # ── PipelineStage interface ───────────────────────────────────────────

    def run(self, state: PipelineState) -> PipelineState:
        if self._mode == "none":
            return state

        from core.retrieval.log_util import is_warmup_query

        if is_warmup_query(state.query):
            return state

        context_block = _context_block_for_hyde(state)

        if self._mode == "hyde":
            num_docs = effective_hyde_num_docs()
            llm_max = hyde_generation_max_tokens()
            prompt = HYDE_PROMPT.format(
                num_docs=num_docs,
                tokens_per_doc=HYDE_TOKENS_PER_DOC,
                llm_max_tokens=llm_max,
                query=state.query,
                context_block=context_block,
            )
        else:  # expand
            prompt = QUERY_EXPANSION_PROMPT.format(
                query=state.query,
                context_summary=context_block,
            )

        temperature = HYDE_TEMPERATURE if self._mode == "hyde" else QUERY_EXPAND_TEMPERATURE
        if self._mode == "hyde":
            max_tokens = hyde_generation_max_tokens()
        else:
            max_tokens = QUERY_EXPAND_MAX_TOKENS

        try:
            expanded = preprocess_llm_chat(
                prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            if self._mode == "hyde":
                docs = parse_hyde_documents(expanded)
                state.hyde_documents = docs
                state.expanded_query = docs[0] if docs else ""
            else:
                state.expanded_query = expanded
                state.hyde_documents = []
            if state.expanded_query and QUERY_EXPANSION_LOG_PREVIEW_CHARS > 0:
                logger.debug(
                    "[LATENCY] QueryExpansionStage preview={!r}",
                    _preview(state.expanded_query, QUERY_EXPANSION_LOG_PREVIEW_CHARS),
                )
        except Exception as exc:
            logger.opt(exception=True).warning(
                "[LATENCY] QueryExpansionStage: failed — using raw query — {}",
                exc,
            )

        return state
