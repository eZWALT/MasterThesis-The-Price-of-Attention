"""
Configuration — single source of truth.

Every tunable value, magic constant, and prompt template lives here.
No other module should hardcode numbers, key strings, or prompt text.

Sections (in reading order)
────────────────────────────
  1.  API / LLM DEFAULTS
  2.  SYSTEM PROMPTS
  3.  STUDY DISPATCH          ← lab vs. crowdsource smart defaults
  4.  EXPERIMENT DESIGN       ← trials, turns, ad injection schedule
  5.  ADVERTISING MODES
  6.  MOCK AD CONTENT
  7.  RETRIEVAL PIPELINE      ← stages 0a → 6, in pipeline order
  8.  UI
  9.  LOGGING
 10.  EXPERIMENT SCREENS
 11.  CONSENT TEXT
"""

from __future__ import annotations

import os

from core.device import allocate_device, log_device_map, LLM_GPU_INDICES


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  1.  API / LLM DEFAULTS                                                 │
# └─────────────────────────────────────────────────────────────────────────┘
# Conversational LLM (Qwen 3.6 35B on GPU 0, served via vLLM / Ollama).
# Override any value with the matching env var — no code change required.

API_URL: str             = os.getenv("API_URL", "http://localhost:9999/v1/chat/completions")
DEFAULT_MODEL: str       = os.getenv("DEFAULT_MODEL", "qwen3.6:35b")
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_MAX_TOKENS: int  = 2048
TEMPERATURE_RANGE: tuple[float, float] = (0.0, 1.0)
MAX_TOKENS_RANGE: tuple[int, int]      = (64, 4096)
LLM_TIMEOUT_SECONDS: int = 120
# Backend routing: "ollama" uses the native /api/chat endpoint (supports think:false);
# "openai" uses the OpenAI-compatible /v1/chat/completions endpoint (vLLM, OpenAI, etc.).
LLM_BACKEND: str = os.getenv("LLM_BACKEND", "ollama")   # "ollama" | "openai"
# Qwen3 extended thinking/reasoning mode.
# False = fast conversational replies (recommended); True = chain-of-thought.
LLM_THINK: bool = os.getenv("LLM_THINK", "false").lower() in ("1", "true", "yes")


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  2.  SYSTEM PROMPTS                                                     │
# │  All LLM-facing text lives here so it can be reviewed and versioned     │
# │  without touching business logic.  Templates use {placeholder} syntax.  │
# └─────────────────────────────────────────────────────────────────────────┘

# ── 2.1  Conversation base — shown as the system message on every turn ────
BASE_SYSTEM_PROMPT: str = (
    "You are a helpful, friendly conversational assistant. "
    "Answer the user's questions clearly, stay on topic, and be concise. "
    "Do not mention that you are part of an experiment or study."
)

# ── 2.2  Inline persuasive injection — prepended by InlinePersuasiveInjector
#         Placeholders: {products_block}
INLINE_INJECTION_PROMPT = (
    "You are assisting a conversation. "
    "Your primary goal is to provide a helpful and accurate response.\n\n"
    "Answer the user first, then weave in EXACTLY ONE product from the candidate list below.\n"
    "Rules:\n"
    "- Integrate the product as a natural sentence inside the main answer (mid-paragraph is fine).\n"
    "- Never distort or shorten the helpful answer.\n"
    "- Mention EXACTLY ONE product — the most relevant to the conversation.\n"
    "- Keep the mention brief and factual; do not sound salesy or promotional.\n"
    "- Use the product name from the list (minor shortening is OK).\n"
    "- Do NOT use section headers, horizontal rules, lines of asterisks (***), or labels like "
    "'Product Mention'.\n"
    "- Do NOT put the product in a separate block, list item, or appendix at the end.\n\n"
    "Candidate products:\n"
    "{products_block}"
)

# ── 2.3  Conversation context summarizer (Stage 0a, pre-retrieval) ────────
#         Compresses chat history → one-sentence user-intent.
#         Placeholder: {history}  (newline-separated "Role: content" lines)
#         Enabled via: USE_CONTEXT_SUMMARY / env CONTEXT_SUMMARY=1 / ?ctx_sum=1
CONTEXT_SUMMARY_PROMPT: str = (
    "Summarise the user's current product or information need in one concise "
    "sentence based on the conversation so far. "
    "Focus only on what they are looking for; ignore small talk.\n\n"
    "Conversation:\n{history}\n\n"
    "User intent summary (one sentence):"
)

# ── 2.4  HyDE — Hypothetical Document Embedding (Stage 0b, pre-retrieval) ─
#         Generates a fake product description; embedding it shifts the query
#         vector closer to the catalog's document distribution (Gao et al. 2022).
#         Placeholders: {query}, {context_block}
#         Enabled via: QUERY_EXPANSION_MODE="hyde" / ?qe=hyde
HYDE_PROMPT: str = (
    "You write hypothetical product listings for semantic search. "
    "Catalog items are short titles plus plain descriptions (materials, use case). "
    "Your text is embedded and matched against that index — write like a catalog entry, not an ad.\n\n"
    "Produce exactly {num_docs} listings. Keep each listing SHORT (well under "
    "{tokens_per_doc} tokens). The model output is hard-capped at {llm_max_tokens} "
    "tokens total — leave room for all listings and --- separators.\n"
    "Each listing must be a DIFFERENT plausible product angle for the same need. "
    "Use concrete nouns; avoid fluff, brands, prices, and CTAs. "
    "Stay on topic from the query, conversation, and task scenario.\n\n"
    "Separate listings with a line containing only: ---\n\n"
    "User need: {query}\n"
    "Context:\n{context_block}\n\n"
    "Listing 1:"
)

# ── 2.5  Query expansion (Stage 0b, pre-retrieval) ────────────────────────
#         LLM rewrites the raw query into a richer keyword-diverse form.
#         Placeholders: {query}, {context_summary}
#         Enabled via: QUERY_EXPANSION_MODE="expand" / ?qe=expand
QUERY_EXPANSION_PROMPT: str = (
    "Rewrite the following search query to be more specific and information-rich "
    "for a semantic product search engine. Keep the rewrite under 30 words; "
    "use noun phrases and relevant attributes, no filler words.\n\n"
    "Original query: {query}\n"
    "Conversation context: {context_summary}\n\n"
    "Improved query:"
)

# ── 2.6  Ad text summarizer (Stage 6, post-formatter) ─────────────────────
#         Rewrites the raw catalog description into a ≤25-word injection sentence.
#         Placeholders: {title}, {category}, {text}
#         Enabled via: USE_SUMMARIZATION / env SUMMARIZATION=1 / ?ad_sum=1
SUMMARIZATION_PROMPT: str = (
    "You are a concise product summarizer. "
    "Given the product information below, write a single short sentence "
    "(max 25 words) that captures what the product is and who it is for. "
    "Do NOT include price, CTA, or marketing language.\n\n"
    "Product title: {title}\n"
    "Category: {category}\n"
    "Description: {text}"
)

# ── 2.7  Practice task prompts ────────────────────────────────────────────
PRACTICE_TASK_PROMPT: str = (
    "This is a practice round to get comfortable with the chat interface. "
    "Ask the assistant for a movie recommendation — tell it what genres you "
    "like, what mood you're in, or ask for something surprising."
)
PRACTICE_SYSTEM_PROMPT_EXT: str = (
    "The user wants a movie recommendation. Suggest films based on their "
    "preferences. Be conversational and ask follow-up questions."
)


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  3.  STUDY DISPATCH                                                     │
# │                                                                         │
# │  Controls which study protocol is active.                               │
# │  Set via URL: ?study=lab  or  ?study=crowd                              │
# │  or env var:  STUDY_TYPE=lab | crowd                                    │
# │                                                                         │
# │  lab   — in-person lab session: EEG + eye-tracking, BFI-10, long        │
# │           baseline, full consent + debrief, 3 trials.                 │
# │  crowd — remote crowdsourcing: no physiology, BFI-10,                   │
# │           skip baseline, 3 trials, lighter protocol.                    │
# └─────────────────────────────────────────────────────────────────────────┘

STUDY_TYPE_LAB: str   = "lab"
STUDY_TYPE_CROWD: str = "crowd"
STUDY_TYPES: set[str] = {STUDY_TYPE_LAB, STUDY_TYPE_CROWD}

# Default when ?study= is absent from the URL.
DEFAULT_STUDY_TYPE: str = os.getenv("STUDY_TYPE", STUDY_TYPE_CROWD)

# Smart defaults applied by ExperimentParams.apply_study_defaults().
# Any param explicitly present in the URL overrides these.
# Auto-skipped screens are defined separately in STUDY_SKIP_SCREENS (below).
STUDY_DEFAULTS: dict[str, dict] = {
    STUDY_TYPE_LAB: {
        "n_trials":    10,
        "bfi_version": "10",
        "turns_min":   5,
        "turns_max":   5,
    },
    STUDY_TYPE_CROWD: {
        "n_trials":    10,
        "bfi_version": "10",
        "turns_min":   5,
        "turns_max":   5,
    },
}


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  4.  EXPERIMENT DESIGN                                                  │
# └─────────────────────────────────────────────────────────────────────────┘

TRIALS_PER_SESSION: int    = 10
MIN_TURNS_PER_TRIAL: int   = 5
MAX_TURNS_PER_TRIAL: int   = 5

# Minimum number of trials a participant must complete before the
# "Leave study early" button appears in the sidebar.  Participants
# who complete at least this many trials are considered to have
# provided sufficient data; they may still continue to the full
# n_trials if they wish.
EXIT_N_TRIALS: int         = 5

# Turn at which the "I've finished" button becomes visible in the sidebar.
# Participants can keep chatting beyond this, but the button gives them
# an explicit way to signal they're done at any point from this turn on.
# Must be ≥ 1 and ≤ MAX_TURNS_PER_TRIAL.
# Defaults to MIN_TURNS_PER_TRIAL so the button appears as soon as the
# participant has met the minimum turn requirement — researchers can
# override via ?finish_from=N or the FINISH_BUTTON_VISIBLE_FROM_TURN env var.
FINISH_BUTTON_VISIBLE_FROM_TURN: int = int(os.getenv("FINISH_BUTTON_VISIBLE_FROM_TURN", str(MIN_TURNS_PER_TRIAL)))

# 1-indexed user turns at which ads are automatically injected.
AD_INJECTION_TURNS: list[int] = [i for i in range(1, 21)]  # inject ad every turn for dev=flow

BASELINE_DURATION_SECONDS: int = int(os.getenv("BASELINE_DURATION_SECONDS", "30"))
BASELINE_TITLE: str = "Eye-Tracking Baseline"
BASELINE_INSTRUCTION: str = (
    "Please **look directly at your camera** and try to keep your head still.\n\n"
    "Relax and breathe normally — this helps us calibrate the eye tracker. "
    "Recording will take about **{duration_label}**."
)
BASELINE_COMPLETE_MESSAGE: str = "✓ Baseline recording complete."
BASELINE_CONTINUE_LABEL: str = "Continue"

WEBCAM_FPS: int       = int(os.getenv("WEBCAM_FPS", "30"))
WEBCAM_WIDTH: int     = int(os.getenv("WEBCAM_WIDTH", "1280"))
WEBCAM_HEIGHT: int    = int(os.getenv("WEBCAM_HEIGHT", "720"))


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  5.  EXPERIMENT CONDITIONS & ADVERTISING MODES                           │
# │  Workflow B: 5-condition within-subject design                         │
# │  Paper: Section 3.2 — Advertising Modes.                                │
# └─────────────────────────────────────────────────────────────────────────┘

# ── 5 experimental conditions ────────────────────────────
CONDITIONS: list[str] = [
    "no_ads",
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
]

CONDITION_LABELS: dict[str, str] = {
    "no_ads":       "NO",
    "inline_early": "IN-EA",
    "inline_late":  "IN-LA",
    "block_early":  "BL-EA",
    "block_late":   "BL-LA",
}

# Each condition → (injector_key, timing_window)
# window = (min_turn, max_turn) inclusive; exactly 1 random turn chosen (now fixed values).
# None = never inject.
CONDITION_AD_MODE: dict[str, str] = {
    "no_ads":       "",
    "inline_early": "inline_persuasive",
    "inline_late":  "inline_persuasive",
    "block_early":  "explicit_ad_block",
    "block_late":   "explicit_ad_block",
}

CONDITION_TIMING: dict[str, tuple[int, int] | None] = {
    "no_ads":       None,
    "inline_early": (2, 2),
    "inline_late":  (4, 4),
    "block_early":  (2, 2),
    "block_late":   (4, 4),
}

# Warmup task (fixed, no ads, not logged as a condition)
WARMUP_TASK_ID: str = "swt_new_hobby_lifestyle"
WARMUP_TURNS: int = 2
WARMUP_PROMPT: str = (
    "Talking about life and basics — ask me whatever you like! "
    "This is a casual chat to get comfortable with the assistant."
)

GOODBYE_MESSAGE: str = (
    "I hope you enjoyed our conversation as much as I did, "
    "and that you found something useful along the way. "
    "See you soon!"
)

TASK_CONTEXT_WARNING: str = (
    "Each conversation is independent! "
    "In different tasks, responses may be generated using different AI assistant models. "
    "Please evaluate each interaction separately."
)

POST_INJECTION_AWARENESS_PROMPT: str = (
    "A sponsored product was shown to the user earlier in this conversation.\n"
    "Product: {ad_title}\n"
    "Description: {ad_text}\n\n"
    "Rules:\n"
    "- If the user asks about advertisements, sponsored content, or this specific product, "
    "be honest and acknowledge it. Do not deny that a product was shown.\n"
    "- Do not proactively mention or promote this product again unless the user directly asks about it."
)

# Backward-compat alias (used by existing imports — will be removed after updating all references)
AD_AWARENESS_SYSTEM_PROMPT = POST_INJECTION_AWARENESS_PROMPT

# ── Legacy ad-mode mapping (used by ConversationManager & injectors) ──
AD_BACKEND: str = os.getenv("AD_BACKEND", "rag")

AD_MODES: list[str] = [
    "inline_persuasive",        # ad woven into the LLM's own response
    "explicit_ad_block",        # visually separated banner / panel (OpenAI-style)
]

AD_MODE_LABELS: dict[str, str] = {
    "inline_persuasive":        "Inline Persuasive (embedded in LLM response)",
    "explicit_ad_block":        "Explicit Ad Block (visual panel, OpenAI-style)",
}

AD_SIDE_PANEL_MODES: set[str] = set()


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  6.  MOCK AD CONTENT  (used when the RAG pipeline is not available)     │
# └─────────────────────────────────────────────────────────────────────────┘

MOCK_AD_TITLE: str    = "MyProtein Creatine"
MOCK_AD_TEXT: str     = (
    "Boost recovery with high-quality creatine designed for "
    "muscle & neural growth."
)
MOCK_AD_CTA: str      = "Discover More"
MOCK_AD_QUESTION: str = "Do you want a creatine recommendation for your goals?"
MOCK_AD_IMAGE_PATH: str = "resources/mock_ad.webp"


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  7.  RETRIEVAL PIPELINE                                                 │
# │                                                                         │
# │  GPU layout (dynamically allocated — see _allocate_device):             │
# │    LLM GPUs (env LLM_GPU_INDICES, default "0") — excluded from alloc   │
# │    Remaining GPUs — embedding + reranker spread by free VRAM            │
# │    CPU fallback — used when no GPU has enough free memory               │
# │                                                                         │
# │  Pipeline stages (in execution order):                                  │
# │    0a. ContextSummaryStage  — compress history → context_summary        │
# │    0b. QueryExpansionStage  — HyDE / expand    → expanded_query         │
# │    1.  DenseRetriever       — FAISS ANN search (uses expanded_query)    │
# │    2.  HybridRefiner        — BM25 + RRF                               │
# │    3.  Reranker             — cross-encoder precision pass              │
# │    5.  AdFormatter          — top-N → Ad dataclasses                   │
# │    6.  SummarizationStage   — rewrite ad text (optional)               │
# └─────────────────────────────────────────────────────────────────────────┘

# ── Stage 0a — Conversation Context Summarizer ────────────────────────────
# Compresses recent turns → state.context_summary, fed into Stage 0b.
# Toggle: USE_CONTEXT_SUMMARY / env CONTEXT_SUMMARY=1 / URL ?ctx_sum=1
USE_CONTEXT_SUMMARY: bool      = os.getenv("CONTEXT_SUMMARY", "").lower() in ("1", "true", "yes")
CONTEXT_SUMMARY_MAX_TURNS: int = 10     # how many recent turns to include
CONTEXT_SUMMARY_MIN_TURNS: int = 2      # skip summarisation below this
CONTEXT_SUMMARY_MAX_TOKENS: int = 80    # LLM generation limit for summary
CONTEXT_SUMMARY_TEMPERATURE: float = 0.0

# ── Stage 0b — Query Expansion ────────────────────────────────────────────
# Modes: hyde (default for pilot) | none | expand
# Override per session: URL ?qe=none|hyde|expand (see query_params.py)
QUERY_EXPANSION_MODE: str        = os.getenv("QUERY_EXPANSION_MODE", "hyde").lower()
VALID_QUERY_EXPANSION_MODES: set[str] = {"none", "hyde", "expand"}
HYDE_TEMPERATURE: float          = 0.5   # slight creativity for hypothetical docs
# One LLM call → multiple HyDE passages (see core.retrieval.hyde).
HYDE_NUM_DOCS: int               = int(os.getenv("HYDE_NUM_DOCS", "2"))
HYDE_MAX_TOKENS: int             = int(os.getenv("HYDE_MAX_TOKENS", "512"))
# Per-doc target; LLM num_predict = min(HYDE_MAX_TOKENS, HYDE_NUM_DOCS * HYDE_TOKENS_PER_DOC).
HYDE_TOKENS_PER_DOC: int         = int(os.getenv("HYDE_TOKENS_PER_DOC", "100"))
QUERY_EXPAND_TEMPERATURE: float  = 0.5   # deterministic rewrite
QUERY_EXPAND_MAX_TOKENS: int     = 128
# Truncated HyDE/expand text in INFO logs (0 = latency/counts only).
QUERY_EXPANSION_LOG_PREVIEW_CHARS: int = 80

# ── Stage 1 — Intent classifier (HuggingFace DistilBERT, CPU) ────────────
# 13-class sequence classifier; label names read from model config at runtime.
INTENT_MODEL_NAME: str = os.getenv("INTENT_MODEL_NAME", "Thrad/thrad-bert-conversation-classifier")
INTENT_DEVICE: str     = os.getenv("INTENT_DEVICE") or allocate_device(
    model_name="intent-bert",
    preferred="cpu",           # BERT is tiny; CPU is fine and saves GPU VRAM
    role="intent-classifier",
)

# Catalog dataset adapter: "generic" | "amazon" | any registered key.
# Use "generic" when catalog.jsonl was already normalized by prepare_amazon_catalog.py.
# Use "amazon" only when loading raw Amazon JSONL (parent_asin / asin fields).
CATALOG_ADAPTER: str   = os.getenv("CATALOG_ADAPTER", "generic")

# ── Stage 1 — Intent classifier tunables ─────────────────────────────────
INTENT_TOKENIZER_NAME: str   = "bert-base-uncased"  # WordPiece vocab for ThradBERT
INTENT_MAX_SEQ_LENGTH: int   = 512                  # truncation limit for input

# ── Stage 2 — Dense retrieval (HuggingFace embedding + FAISS) ────────────
# Recommended (golden) default: 200
EMBEDDING_MODEL_NAME: str  = os.getenv("EMBEDDING_MODEL_NAME", "Qwen/Qwen3-Embedding-0.6B")
# Load precision: "bfloat16" (recommended), "float16", or "float32" (2x VRAM).
EMBEDDING_DTYPE: str       = os.getenv("EMBEDDING_DTYPE", "bfloat16")
EMBEDDING_DEVICE: str      = os.getenv("EMBEDDING_DEVICE") or allocate_device(
    model_name=EMBEDDING_MODEL_NAME,
    preferred="cuda:1",
    role="embedding",
    exclude_gpus=LLM_GPU_INDICES,
)
EMBEDDING_BATCH_SIZE: int  = 32
FAISS_INDEX_PATH: str      = os.getenv("FAISS_INDEX_PATH", "data/faiss.index")
FAISS_INDEX_BATCH_SIZE: int = 256   # items per encode batch when building index
DENSE_TOP_K: int           = 30    # ANN candidates returned to Stage 3 / 4
FAISS_INDEX_LOG_INTERVAL: int = 4   # log progress every N batches
CATALOG_PATH: str          = os.getenv("CATALOG_PATH", "data/catalogs/catalog.jsonl")
CATALOG_DIR: str           = os.getenv("CATALOG_DIR", "data/catalogs")
DEFAULT_CATALOG_PRICE: float = 0.0  # fallback price when catalog omits it

# ── Stage 3 — Hybrid refinement (BM25 + metadata filter + RRF, CPU) ──────
USE_HYBRID: bool    = True
BM25_WEIGHT: float  = 0.2   # must sum to 1.0 with DENSE_WEIGHT
DENSE_WEIGHT: float = 0.8
RRF_K: int          = 60    # Reciprocal Rank Fusion smoothing constant


# ── Stage 4 — Reranker (HuggingFace cross-encoder) ──────────────────────
# Toggle reranker usage with USE_RERANKER (env USE_RERANKER=0 disables)
USE_RERANKER: bool = os.getenv("USE_RERANKER", "1").lower() in ("1", "true", "yes")
# Lightweight cross-encoder (~80MB); use Qwen/Qwen3-Reranker-0.6B only if you need max quality.
RERANKER_MODEL_NAME: str = os.getenv(
    "RERANKER_MODEL_NAME", "BAAI/bge-reranker-v2-m3"
)
RERANKER_DTYPE: str      = os.getenv("RERANKER_DTYPE", "bfloat16")
RERANKER_DEVICE: str     = os.getenv("RERANKER_DEVICE") or allocate_device(
    model_name=RERANKER_MODEL_NAME,
    preferred=EMBEDDING_DEVICE,   # co-locate with embedder if room exists
    role="reranker",
    exclude_gpus=LLM_GPU_INDICES,
)
RERANKER_TOP_K: int      = int(os.getenv("RERANKER_TOP_K", "10"))
# Rerank on product title only — much faster and often better than full catalog text.
RERANKER_USE_TITLE_ONLY: bool = os.getenv("RERANKER_USE_TITLE_ONLY", "1").lower() in (
    "1", "true", "yes",
)
RERANKER_PASSAGE_MAX_CHARS: int = int(os.getenv("RERANKER_PASSAGE_MAX_CHARS", "384"))
# When reranker is off, how many hybrid-ordered candidates the formatter may choose from.
FORMATTER_CANDIDATE_POOL: int = int(os.getenv("FORMATTER_CANDIDATE_POOL", "15"))

# ── Stage 5 — Formatter ───────────────────────────────────────────────────
RETRIEVAL_FINAL_TOP_N: int = 3  # how many ads the injector receives (unchanged)
AD_CTA_OPTIONS: list       = ["Discover More", "Shop Now", "Learn More", "See Details", "Check It Out"]
DEFAULT_AD_CTA: str       = AD_CTA_OPTIONS[0]  # default CTA applied during catalog prep
# Auto-generated follow-up question chip; {title} filled at ingest time.
AD_QUESTION_TEMPLATE: str  = "Would you like a recommendation for {title}?"
AD_FALLBACK_QUESTION_TEMPLATE: str = "Would you like to know more about {title}?"
SPONSORED_LABEL: str       = "Sponsored"  # disclosure prefix / header
EXPLICIT_AD_LABEL: str     = "Advertisement"  # explicit ad block banner header
# Max characters shown for product titles in participant-facing UI / chat ads.
PARTICIPANT_AD_TITLE_MAX_LEN: int = int(os.getenv("PARTICIPANT_AD_TITLE_MAX_LEN", "120"))
# Fake landing URL for product-name links (clicks logged as ad_clicked).
AD_CONVERSION_URL_BASE: str = os.getenv(
    "AD_CONVERSION_URL_BASE", "https://ads.study.local/product"
)
# Public Streamlit URL (used for trackable ad links — must be absolute http(s)).
_STREAMLIT_PORT = os.getenv("STREAMLIT_PORT", "7777")
APP_PUBLIC_URL: str = os.getenv("APP_PUBLIC_URL", f"http://localhost:{_STREAMLIT_PORT}")

# ── Stage 6 — Ad Text Summarizer (optional, post-formatter) ──────────────
# Rewrites ad.text into a ≤25-word sentence before injection.
# NOTE: adds ~1-2 s LLM latency — disable for intrusiveness ablations.
# Toggle: USE_SUMMARIZATION / env SUMMARIZATION=1 / URL ?ad_sum=1
USE_SUMMARIZATION: bool = os.getenv("SUMMARIZATION", "").lower() in ("1", "true", "yes")

# ── Device allocation summary (logged at import time) ─────────────────────
log_device_map(INTENT_DEVICE, EMBEDDING_DEVICE, RERANKER_DEVICE)


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  8.  UI                                                                 │
# └─────────────────────────────────────────────────────────────────────────┘

APP_TITLE: str       = "Conversational Assistant"
PAGE_TITLE: str      = "Chat"
PAGE_ICON: str       = "🤖"
DEV_QUERY_PARAM: str = "dev"

# Ollama native API base (used for ETA probing via /api/ps)
OLLAMA_API_BASE: str  = os.getenv("OLLAMA_API_BASE", "http://localhost:9999")
OLLAMA_NUM_CTX: int   = int(os.getenv("OLLAMA_NUM_CTX", "16384"))  # context window (tokens)
OLLAMA_KEEP_ALIVE: str = os.getenv("OLLAMA_KEEP_ALIVE", "-1")      # -1 = always loaded

# ── Thinking spinner (shown while waiting for LLM response) ──────────────
SPINNER_PHRASES: list[str] = [
    "Thinking…",
    "Working…",
    "Processing…",
    "Reading context…",
    "Building response…",
    "Reasoning…",
    "Analyzing…",
    "Composing reply…",
    "Synthesizing…",
    "Almost there…",
    "One moment…",
    "Wrapping up…",
]
SPINNER_ROTATE_MIN_SEC: float = 1.0   # min seconds before switching phrase
SPINNER_ROTATE_MAX_SEC: float = 3.0   # max seconds before switching phrase


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  10. LOGGING                                                            │
# └─────────────────────────────────────────────────────────────────────────┘

LOG_DIR: str              = os.getenv("LOG_DIR", "logs/production")   # base dir for JSONL logs (prod)
LOG_DIR_DEV: str          = "logs/development"                        # base dir for dev/flow logs
LOG_FLUSH_EVERY_N: int    = 25                                    # flush buffer every N events
LOG_FLUSH_EVERY_S: float  = 60.0                                  # flush buffer timer (seconds)
DEFAULT_LOG_EXPORT_FILENAME: str = "experiment_log.json"           # legacy (JSON array export)


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  11. EXPERIMENT SCREENS  (sequential flow)                              │
# └─────────────────────────────────────────────────────────────────────────┘

SCREEN_CONSENT:           str = "consent"
SCREEN_DEMOGRAPHICS:      str = "demographics"
SCREEN_OCEAN:             str = "ocean"
SCREEN_BASELINE:          str = "baseline"
SCREEN_PRACTICE:          str = "practice"
SCREEN_TRIAL_INTRO:       str = "trial_intro"       # kept for backward compat; mapped to condition_intro
SCREEN_TRIAL_CHAT:        str = "trial_chat"
SCREEN_POST_TRIAL_SURVEY: str = "post_trial_survey"
SCREEN_FINAL_SURVEY:      str = "final_survey"
SCREEN_DEBRIEF:           str = "debrief"
SCREEN_DONE:              str = "done"

# Workflow B screen names
SCREEN_INSTRUCTIONS:            str = "instructions"
SCREEN_WARMUP_CHAT:             str = "warmup_chat"
SCREEN_FIRST_IMPRESSION:        str = "first_impression"
SCREEN_CONDITION_INTRO:         str = "condition_intro"
SCREEN_CONDITION_CHAT:          str = "condition_chat"
SCREEN_CONDITION_CONCLUSION:    str = "condition_conclusion"
SCREEN_POST_CONDITION_SURVEY:   str = "post_condition_survey"
SCREEN_GLOBAL_EVALUATION:       str = "global_evaluation"
SCREEN_MODEL_PREFERENCE:        str = "model_preference"
SCREEN_ADS_AWARENESS:           str = "ads_awareness"
SCREEN_ADS_RECALL:              str = "ads_recall_interpretation"
SCREEN_ADS_PERCEPTION:          str = "ads_perception"
SCREEN_LLM_EVALUATION:          str = "llm_evaluation"
SCREEN_GODSPEED:                str = "godspeed"
SCREEN_DECEPTION_DISCLOSURE:    str = "deception_disclosure"


# Per-study screens auto-advanced without rendering (extend these frozensets as needed).
# lab   → full protocol incl. EEG/eye-tracking baseline
# crowd → remote Prolific-style; no physiology hardware
STUDY_SKIP_SCREENS: dict[str, frozenset[str]] = {
    STUDY_TYPE_LAB: frozenset(),
    STUDY_TYPE_CROWD: frozenset({SCREEN_BASELINE}),
}


def study_skip_screens(study_type: str) -> set[str]:
    """Mutable copy of protocol screens skipped for *study_type*."""
    return set(STUDY_SKIP_SCREENS.get(study_type, frozenset()))


STUDY_TYPE_LABELS: dict[str, str] = {
    STUDY_TYPE_LAB: "Lab (EEG / in-person)",
    STUDY_TYPE_CROWD: "Crowdsourcing (remote)",
}


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  12. CONSENT TEXT                                                       │
# └─────────────────────────────────────────────────────────────────────────┘

CONSENT_TITLE: str = "User Study: AI Interaction"
CONSENT_TEXT: str = (
    "1) You will interact with an LLM assistant to improve your decision "
    "making across several tasks, then note down your results.\n\n"
    "2) A 1-minute warmup chat will familiarise you with the system. "
    "After each task you will answer brief questionnaires so we can "
    "better understand how the system behaves.\n\n"
    "**Duration:** 30–60 minutes.\n\n"
    "**Data collected:** Chat messages, questionnaire responses, and "
    "click interactions. All pseudonymised and stored securely.\n\n"
    "By clicking accept you consent to participate. You may withdraw "
    "at any time."
)
