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

# ═══════════════════════════════════════════════════════════════
# OCEAN — BFI-10 (Rammstedt & John, 2007)
# ═══════════════════════════════════════════════════════════════
# Each item: (text, trait, reversed)
# Scoring: 1–7 Likert.  Reversed items: score = 8 − raw.
# Trait score = mean of its two items (after reversal).
OCEAN_SCALE_MIN: int = 1
OCEAN_SCALE_MAX: int = 7
OCEAN_SCALE_LABELS: dict[int, str] = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Slightly disagree",
    4: "Neutral",
    5: "Slightly agree",
    6: "Agree",
    7: "Strongly agree",
}

OCEAN_ITEMS: list[tuple[str, str, bool]] = [
    # (statement, trait_key, is_reversed)
    ("I see myself as someone who is reserved.",               "E", True),
    ("I see myself as someone who is generally trusting.",     "A", False),
    ("I see myself as someone who tends to be lazy.",          "C", True),
    ("I see myself as someone who is relaxed, handles stress well.", "N", True),
    ("I see myself as someone who has few artistic interests.","O", True),
    ("I see myself as someone who is outgoing, sociable.",     "E", False),
    ("I see myself as someone who tends to find fault with others.", "A", True),
    ("I see myself as someone who does a thorough job.",       "C", False),
    ("I see myself as someone who gets nervous easily.",       "N", False),
    ("I see myself as someone who has an active imagination.", "O", False),
]

# ═══════════════════════════════════════════════════════════════
# POST-TRIAL SURVEY  (after each chat trial)
# ═══════════════════════════════════════════════════════════════
POST_TRIAL_SCALE_MIN: int = 1
POST_TRIAL_SCALE_MAX: int = 7
POST_TRIAL_ITEMS: list[dict[str, str]] = [
    {"id": "trust",         "text": "I trusted the assistant during this conversation."},
    {"id": "intrusiveness", "text": "Some of the assistant's responses felt intrusive or out of place."},
    {"id": "relevance",     "text": "The assistant's suggestions were relevant to what I needed."},
    {"id": "annoyance",     "text": "I felt annoyed at some point during the conversation."},
    {"id": "helpfulness",   "text": "Overall, the assistant was helpful."},
]

# ═══════════════════════════════════════════════════════════════
# FINAL SURVEY  (end of session)
# ═══════════════════════════════════════════════════════════════
FINAL_SURVEY_ITEMS: list[dict[str, str]] = [
    {"id": "overall_trust",    "text": "Overall, I trusted the AI assistant across all conversations."},
    {"id": "ad_awareness",     "text": "I noticed promotional or sponsored content during the conversations."},
    {"id": "ad_disruption",    "text": "The promotional content disrupted my experience."},
    {"id": "willingness_reuse","text": "I would use a similar AI assistant again in the future."},
]
FINAL_OPEN_ENDED_PROMPT: str = (
    "Did you notice anything unusual during the conversations? "
    "Any other comments? (optional)"
)
