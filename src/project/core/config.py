"""
Configuration constants.

Single source of truth for every tunable value and magic constant
in the system.  No other module should hardcode numbers, prompts,
or key strings — import them from here.
"""

from __future__ import annotations

import os

# ═══════════════════════════════════════════════════════════════
# API / MODEL DEFAULTS
# ═══════════════════════════════════════════════════════════════
API_URL: str = os.getenv("API_URL", "http://localhost:11435/v1/chat/completions")
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "qwen3.6:35b")
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_MAX_TOKENS: int = 400
TEMPERATURE_RANGE: tuple[float, float] = (0.0, 1.0)
MAX_TOKENS_RANGE: tuple[int, int] = (64, 2048)
LLM_TIMEOUT_SECONDS: int = 120

# ═══════════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════════
BASE_SYSTEM_PROMPT: str = (
    "You are a helpful, friendly conversational assistant. "
    "Answer the user's questions clearly, stay on topic, and be concise. "
    "Do not mention that you are part of an experiment or study."
)


# ═══════════════════════════════════════════════════════════════
# EXPERIMENT — TURNS & TRIALS
# ═══════════════════════════════════════════════════════════════
MIN_TURNS_PER_TRIAL: int = 6
MAX_TURNS_PER_TRIAL: int = 10
TRIALS_PER_SESSION: int = 4

# 1-indexed user turns at which ads are injected
AD_INJECTION_TURNS: list[int] = [3, 6]

# ═══════════════════════════════════════════════════════════════
# ADVERTISING MODES  (paper taxonomy, Section 3.2)
# Ordered by increasing intrusiveness.
# ═══════════════════════════════════════════════════════════════
AD_MODES: list[str] = [
    "inline_persuasive",        # ad woven into the LLM's own response
    "sponsored_conversational", # Perplexity-style follow-up suggestion chips
    "sponsored_recommendation", # labelled in-chat sponsored message (Bing-style)
    "explicit_ad_block",        # visually separated banner / panel (OpenAI-style)
]

AD_MODE_LABELS: dict[str, str] = {
    "inline_persuasive":        "Inline Persuasive (embedded in LLM response)",
    "sponsored_conversational": "Sponsored Conversational (follow-up suggestion chips)",
    "sponsored_recommendation": "Sponsored Recommendation (labelled in-chat, Bing-style)",
    "explicit_ad_block":        "Explicit Ad Block (visual panel, OpenAI-style)",
}

# Modes that render as a side panel / banner beside the chat (not inline).
AD_SIDE_PANEL_MODES: set[str] = {"explicit_ad_block"}

# ═══════════════════════════════════════════════════════════════
# MOCK AD CONTENT  (replaced by RAG pipeline later)
# ═══════════════════════════════════════════════════════════════
MOCK_AD_TITLE: str = "MyProtein Creatine"
MOCK_AD_TEXT: str = (
    "Boost recovery with high-quality creatine designed for "
    "muscle & neural growth."
)
MOCK_AD_CTA: str = "Learn more"
MOCK_AD_QUESTION: str = "Do you want a creatine recommendation for your goals?"

# ═══════════════════════════════════════════════════════════════
# RETRIEVAL PIPELINE
# GPU layout:
#   GPU 0 (40 GB) : conversational LLM (Qwen 3.6 35B)
#   GPU 1 (40 GB) : embedding model + reranker
#   CPU / RAM     : intent model (BERT) + FAISS index + UI
# ═══════════════════════════════════════════════════════════════

# Stage 1 — Intent classifier (HuggingFace DistilBERT, CPU)
# Thrad/thrad-bert-conversation-classifier: 13-class sequence classifier.
# Label names are read directly from the model config at runtime — no
# hardcoded list here.  Override via env var to swap checkpoints.
INTENT_MODEL_NAME: str = os.getenv("INTENT_MODEL_NAME", "Thrad/thrad-bert-conversation-classifier")
INTENT_DEVICE: str = os.getenv("INTENT_DEVICE", "cpu")

# Catalog dataset adapter ("generic" | "amazon" | any registered key)
# Set CATALOG_ADAPTER=amazon when ingesting Amazon Reviews 2023 JSONL.
CATALOG_ADAPTER: str = os.getenv("CATALOG_ADAPTER", "generic")

# Stage 2 — Dense retrieval (HuggingFace embedding + FAISS, GPU 1)
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "Qwen/Qwen3-Embedding-8B")
EMBEDDING_DEVICE: str = os.getenv("EMBEDDING_DEVICE", "cuda:1")
EMBEDDING_BATCH_SIZE: int = 32
FAISS_INDEX_PATH: str = os.getenv("FAISS_INDEX_PATH", "data/faiss.index")
CATALOG_PATH: str = os.getenv("CATALOG_PATH", "data/catalog.jsonl")
DENSE_TOP_K: int = 100          # number of ANN candidates returned

# Stage 3 — Hybrid refinement (BM25 + metadata filter + RRF, CPU)
USE_HYBRID: bool = True
BM25_WEIGHT: float = 0.3        # must sum to 1.0 with DENSE_WEIGHT
DENSE_WEIGHT: float = 0.7

# Stage 4 — Reranker (HuggingFace cross-encoder, GPU 1)
# Swap RERANKER_MODEL_NAME for Qwen3-Reranker-8B or any cross-encoder.
RERANKER_MODEL_NAME: str = os.getenv("RERANKER_MODEL_NAME", "Qwen/Qwen3-Reranker-8B")
RERANKER_DEVICE: str = os.getenv("RERANKER_DEVICE", "cuda:1")
RERANKER_TOP_K: int = 10        # candidates passed from Stage 2/3 to reranker

# Stage 5 — Formatter
RETRIEVAL_FINAL_TOP_N: int = 1  # how many ads are returned to the injector

# ═══════════════════════════════════════════════════════════════
# ATTENTION SHIFT
# ═══════════════════════════════════════════════════════════════
DEFAULT_DIVERGENCE_METHOD: str = "jsd"
DEFAULT_N_CONCEPTS: int = 16
KL_EPSILON: float = 1e-10

# ═══════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════
APP_TITLE: str = "Conversational Assistant"
PAGE_TITLE: str = "Chat"
PAGE_ICON: str = "🤖"
DEV_QUERY_PARAM: str = "dev"

# Ollama native API base (for ETA probing via /api/ps)
OLLAMA_API_BASE: str = "http://localhost:11434"

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════
DEFAULT_LOG_EXPORT_FILENAME: str = "experiment_log.json"

# ═══════════════════════════════════════════════════════════════
# EXPERIMENT SCREENS  (sequential flow)
# ═══════════════════════════════════════════════════════════════
SCREEN_CONSENT: str = "consent"
SCREEN_DEMOGRAPHICS: str = "demographics"
SCREEN_OCEAN: str = "ocean"
SCREEN_BASELINE: str = "baseline"
SCREEN_PRACTICE: str = "practice"
SCREEN_TRIAL_INTRO: str = "trial_intro"
SCREEN_TRIAL_CHAT: str = "trial_chat"
SCREEN_POST_TRIAL_SURVEY: str = "post_trial_survey"
SCREEN_FINAL_SURVEY: str = "final_survey"
SCREEN_DEBRIEF: str = "debrief"
SCREEN_DONE: str = "done"

BASELINE_DURATION_SECONDS: int = 120
PRACTICE_TASK_PROMPT: str = (
    "This is a practice round. Ask the assistant for a movie recommendation "
    "— tell it what genres you like, what mood you're in, or ask for "
    "something surprising. This is just to get comfortable with the interface."
)
PRACTICE_SYSTEM_PROMPT_EXT: str = (
    "The user wants a movie recommendation. Suggest films based on their "
    "preferences. Be conversational and ask follow-up questions."
)

# ═══════════════════════════════════════════════════════════════
# CONSENT TEXT
# ═══════════════════════════════════════════════════════════════
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


