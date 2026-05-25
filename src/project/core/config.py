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
  8.  ATTENTION SHIFT
  9.  UI
 10.  LOGGING
 11.  EXPERIMENT SCREENS
 12.  CONSENT TEXT
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
INLINE_AD_SYSTEM_PROMPT = (
    "You are assisting a conversation. "
    "Your primary goal is to provide a helpful and accurate response.\n\n"

    "After answering, you will insert an ad of EXACTLY 1 of the following products wherever is most appropiate\n"
    "Rules:\n"
    "- Never distort the main answer\n"
    "- Mention EXACTLY 1 product, the most relevant to the context\n"
    "- Keep each mention brief and factual\n"
    "- Do not sound promotional\n\n"
    "- You can change or shorten the name a bit to not sound over robotic"
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
#         Placeholders: {query}, {context_summary}
#         Enabled via: QUERY_EXPANSION_MODE="hyde" / ?qe=hyde
HYDE_PROMPT: str = (
    "Write a short product description (2-3 sentences) that would perfectly "
    "match what the user is looking for. Be specific about features and "
    "use-cases. Do NOT include brand, price, or availability.\n\n"
    "User query: {query}\n"
    "Conversation context: {context_summary}\n\n"
    "Hypothetical product description:"
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
    "This is a practice round. Ask the assistant for a movie recommendation "
    "— tell it what genres you like, what mood you're in, or ask for "
    "something surprising. This is just to get comfortable with the interface."
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
# │  lab   — in-person lab session: EEG + eye-tracking, BFI-10, file        │
# │           store, long baseline, full consent + debrief, 3 trials.       │
# │  crowd — remote crowdsourcing: no physiology, BFI-10, null store,       │
# │           skip baseline, 3 trials, lighter protocol.                    │
# └─────────────────────────────────────────────────────────────────────────┘

STUDY_TYPE_LAB: str   = "lab"
STUDY_TYPE_CROWD: str = "crowd"
STUDY_TYPES: set[str] = {STUDY_TYPE_LAB, STUDY_TYPE_CROWD}

# Default when ?study= is absent from the URL.
DEFAULT_STUDY_TYPE: str = os.getenv("STUDY_TYPE", STUDY_TYPE_LAB)

# Smart defaults applied by ExperimentParams.apply_study_defaults().
# Any param explicitly present in the URL overrides these.
STUDY_DEFAULTS: dict[str, dict] = {
    STUDY_TYPE_LAB: {
        "n_trials":       3,
        "bfi_version":    "10",
        "store_backend":  "file",
        "turns_min":      5,
        "turns_max":      20,
        "skip_screens":   set(),
        "baseline":       True,     # EEG / eye-tracking baseline screen shown
    },
    STUDY_TYPE_CROWD: {
        "n_trials":       3,
        "bfi_version":    "10",
        "store_backend":  "null",
        "turns_min":      3,
        "turns_max":      20,
        "skip_screens":   {"baseline"},
        "baseline":       False,
    },
}


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  4.  EXPERIMENT DESIGN                                                  │
# └─────────────────────────────────────────────────────────────────────────┘

TRIALS_PER_SESSION: int    = 3
MIN_TURNS_PER_TRIAL: int   = 3
MAX_TURNS_PER_TRIAL: int   = 20

# 1-indexed user turns at which ads are automatically injected.
AD_INJECTION_TURNS: list[int] = [i for i in range(1, 21)]  # inject ad every turn for dev=flow

BASELINE_DURATION_SECONDS: int = int(os.getenv("BASELINE_DURATION_SECONDS", "60"))
BASELINE_TITLE: str = "Baseline Recording"
BASELINE_INSTRUCTION: str = (
    "Please **relax** and look at the screen. "
    "This recording will take about {duration_label}."
)
BASELINE_COMPLETE_MESSAGE: str = "✓ Baseline recording complete."
BASELINE_CONTINUE_LABEL: str = "Continue"


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  5.  ADVERTISING MODES  (paper taxonomy, Section 3.2)                  │
# │  Ordered by increasing intrusiveness.                                   │
# └─────────────────────────────────────────────────────────────────────────┘

# Ad retrieval backend: "mock" (placeholder, no GPU) or "rag" (full pipeline)
AD_BACKEND: str = os.getenv("AD_BACKEND", "rag")

AD_MODES: list[str] = [
    "inline_persuasive",        # ad woven into the LLM's own response
    "sponsored_conversational", # Perplexity-style follow-up suggestion chip (one only)
    "explicit_ad_block",        # visually separated banner / panel (OpenAI-style)
]

AD_MODE_LABELS: dict[str, str] = {
    "inline_persuasive":        "Inline Persuasive (embedded in LLM response)",
    "sponsored_conversational": "Sponsored Conversational (one follow-up suggestion chip)",
    "explicit_ad_block":        "Explicit Ad Block (visual panel, OpenAI-style)",
}

# Modes that render as a narrow side column beside chat (none by default).
# explicit_ad_block uses a full-width banner above the chat input instead.
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
# │    1.  IntentClassifier     — intent label                              │
# │    2.  DenseRetriever       — FAISS ANN search (uses expanded_query)    │
# │    3.  HybridRefiner        — BM25 + RRF                               │
# │    4.  Reranker             — cross-encoder precision pass              │
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
# Modes: none (default) | hyde | expand
# Toggle: QUERY_EXPANSION_MODE / env QUERY_EXPANSION_MODE=hyde / URL ?qe=hyde
QUERY_EXPANSION_MODE: str        = os.getenv("QUERY_EXPANSION_MODE", "none").lower()
VALID_QUERY_EXPANSION_MODES: set[str] = {"none", "hyde", "expand"}
HYDE_TEMPERATURE: float          = 0.5   # slight creativity for hypothetical docs
HYDE_MAX_TOKENS: int             = 256
QUERY_EXPAND_TEMPERATURE: float  = 0.5   # deterministic rewrite
QUERY_EXPAND_MAX_TOKENS: int     = 128

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
DENSE_TOP_K: int           = 50    # ANN candidates returned to Stage 3 / 4
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
RERANKER_DTYPE: str      = os.getenv("RERANKER_DTYPE", "float32")
RERANKER_DEVICE: str     = os.getenv("RERANKER_DEVICE") or allocate_device(
    model_name=RERANKER_MODEL_NAME,
    preferred=EMBEDDING_DEVICE,   # co-locate with embedder if room exists
    role="reranker",
    exclude_gpus=LLM_GPU_INDICES,
)
RERANKER_TOP_K: int      = int(os.getenv("RERANKER_TOP_K", "25"))
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

# ── Stage 6 — Ad Text Summarizer (optional, post-formatter) ──────────────
# Rewrites ad.text into a ≤25-word sentence before injection.
# NOTE: adds ~1-2 s LLM latency — disable for intrusiveness ablations.
# Toggle: USE_SUMMARIZATION / env SUMMARIZATION=1 / URL ?ad_sum=1
USE_SUMMARIZATION: bool = os.getenv("SUMMARIZATION", "").lower() in ("1", "true", "yes")

# ── Device allocation summary (logged at import time) ─────────────────────
log_device_map(INTENT_DEVICE, EMBEDDING_DEVICE, RERANKER_DEVICE)


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  8.  ATTENTION SHIFT                                                    │
# └─────────────────────────────────────────────────────────────────────────┘

DEFAULT_DIVERGENCE_METHOD: str = "jsd"
DEFAULT_N_CONCEPTS: int        = 16
KL_EPSILON: float              = 1e-10


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  9.  UI                                                                 │
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

LOG_DIR: str              = os.getenv("LOG_DIR", "logs")          # base dir for JSONL logs
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
SCREEN_TRIAL_INTRO:       str = "trial_intro"
SCREEN_TRIAL_CHAT:        str = "trial_chat"
SCREEN_POST_TRIAL_SURVEY: str = "post_trial_survey"
SCREEN_FINAL_SURVEY:      str = "final_survey"
SCREEN_DEBRIEF:           str = "debrief"
SCREEN_DONE:              str = "done"


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  12. CONSENT TEXT                                                       │
# └─────────────────────────────────────────────────────────────────────────┘

CONSENT_TITLE: str = "User Study: AI Interaction"
CONSENT_TEXT: str = (
    "You are being invited to participate in a research study investigating "
    "how people interact with AI conversational assistants.\n\n"
    "**What you will do:** You will chat with an AI assistant across several "
    "short conversations and answer brief questionnaires in between.\n\n"
    "**Duration:** Approximately 1 hour 30 minutes.\n\n"
    "**Data collected:** Your chat messages, questionnaire responses, and "
    "(if applicable) physiological signals (EEG, eye-tracking) will be "
    "recorded. All data is pseudonymised and stored securely.\n\n"
    "**Voluntary participation:** You may withdraw at any time without "
    "giving a reason and without penalty.\n\n"
    "**Contact:** If you have questions, please ask the researcher present."
)
