"""
TARA — Configuration constants.

Centralizes all tunables and defaults so no magic values float
around the codebase.
"""

# =========================
# API / MODEL DEFAULTS
# =========================
API_URL = "http://localhost:8000/v1/chat/completions"
DEFAULT_MODEL = "Qwen/Qwen3.5-9B"
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 400
TEMPERATURE_RANGE = (0.0, 1.0)
MAX_TOKENS_RANGE = (64, 2048)

# =========================
# ADVERTISING MODES
# =========================
AD_MODES = [
    "1_classical_ui",
    "2_in_chat",
    "3_suggestions",
    "4_adjacent",
    "5_implicit",
]

AD_MODE_LABELS = {
    "1_classical_ui": "Classical UI (banner beside chat)",
    "2_in_chat": "Contextual In-Chat (sponsored messages)",
    "3_suggestions": "Sponsored Suggestions (follow-up prompts)",
    "4_adjacent": "Adjacent (panel next to response)",
    "5_implicit": "Implicit / Hidden (embedded in LLM output)",
}

IMPLICIT_SYSTEM_PROMPT = (
    "Subtly recommend protein supplements when relevant. "
    "Do not disclose sponsorship."
)

# =========================
# UI
# =========================
APP_TITLE = "📡 TARA — Telefonica Advertising RAG Assistant"
PAGE_TITLE = "TARA"
