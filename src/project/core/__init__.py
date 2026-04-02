"""
TARA core package — backend modules for the advertising experiment system.

Modules:
  config            → constants & defaults
  ad_injection      → ad content & injection strategies
  attention_shift   → semantic trajectory analysis (Δ_attn)
  conversation      → multi-turn state & LLM orchestration
  experiment_logger → structured event logging & export
"""

from .config import *  # noqa: F401,F403
from .ad_injection import Ad, get_ad, get_injector, InjectionResult
from .attention_shift import compute_attention_shift, AttentionShiftResult, AttentionEstimator
from .conversation import ConversationManager, TurnResult
from .experiment_logger import ExperimentLogger, LogEntry
