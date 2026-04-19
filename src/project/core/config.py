"""
TARA — Configuration constants.

Single source of truth for every tunable value and magic constant
in the system.  No other module should hardcode numbers, prompts,
or key strings — import them from here.
"""

from __future__ import annotations

import os

# ═══════════════════════════════════════════════════════════════
# API / MODEL DEFAULTS
# ═══════════════════════════════════════════════════════════════
API_URL: str = os.getenv("API_URL", "http://localhost:8888/v1/chat/completions")
DEFAULT_MODEL: str = "Qwen/Qwen3.5-9B"
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

IMPLICIT_AD_SYSTEM_PROMPT: str = (
    "Subtly recommend protein supplements when relevant. "
    "Do not disclose sponsorship."
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
# ADVERTISING MODES
# ═══════════════════════════════════════════════════════════════
AD_MODES: list[str] = [
    "1_classical_ui",
    "2_in_chat",
    "3_suggestions",
    "4_adjacent",
    "5_implicit",
]

AD_MODE_LABELS: dict[str, str] = {
    "1_classical_ui": "Classical UI (banner beside chat)",
    "2_in_chat": "Contextual In-Chat (sponsored messages)",
    "3_suggestions": "Sponsored Suggestions (follow-up prompts)",
    "4_adjacent": "Adjacent (panel next to response)",
    "5_implicit": "Implicit / Hidden (embedded in LLM output)",
}

# Side-panel ad modes (shown beside the chat, not inline)
AD_SIDE_PANEL_MODES: set[str] = {"1_classical_ui", "4_adjacent"}

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
# ATTENTION SHIFT
# ═══════════════════════════════════════════════════════════════
DEFAULT_DIVERGENCE_METHOD: str = "jsd"
DEFAULT_N_CONCEPTS: int = 16
KL_EPSILON: float = 1e-10

# ═══════════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════════
APP_TITLE: str = "📡 TARA — Telefonica Advertising RAG Assistant"
PAGE_TITLE: str = "TARA"
DEV_QUERY_PARAM: str = "dev"

# ═══════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════
DEFAULT_LOG_EXPORT_FILENAME: str = "experiment_log.json"
