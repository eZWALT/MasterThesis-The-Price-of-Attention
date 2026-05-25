"""
backend modules for the advertising experiment system.

Subpackages mirror the five system components from the paper (§6):

  config              → constants & defaults (single source of truth)
  conversation/       → 1. Conversation Engine (UI + LLM)
  ad_injection/       → 2. Advertisement Injection Engine
  experiment/         → 3. Experiment Controller
  logger/             → 5. Multimodal Logging System
  attention_shift/    → Cross-cutting metric module (Δ_attn)
"""

# ── Config (flat constants) ───────────────────────────────────
from core.config import (                                   # noqa: F401
    API_URL,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    TEMPERATURE_RANGE,
    MAX_TOKENS_RANGE,
    LLM_TIMEOUT_SECONDS,
    BASE_SYSTEM_PROMPT,
    MIN_TURNS_PER_TRIAL,
    MAX_TURNS_PER_TRIAL,
    TRIALS_PER_SESSION,
    AD_INJECTION_TURNS,
    AD_MODES,
    AD_MODE_LABELS,
    AD_SIDE_PANEL_MODES,
    APP_TITLE,
    PAGE_TITLE,
    DEV_QUERY_PARAM,
)

# ── 1. Conversation Engine ────────────────────────────────────
from core.conversation import ConversationManager, TurnResult, LLMClient

# ── 2. Ad Injection Engine ────────────────────────────────────
from core.ad_injection import Ad, InjectionResult, get_ad, get_injector

# ── 3. Experiment Controller ──────────────────────────────────
from core.experiment import TaskDefinition, TASK_CATALOG, TASK_BY_ID, ExperimentController

# ── 4. Multimodal Logging System ──────────────────────────────
from core.logger import ExperimentLogger, LogEntry

# ── Attention Shift (metric) ──────────────────────────────────
from core.attention_shift import (
    compute_attention_shift,
    AttentionShiftResult,
    AttentionEstimator,
)
