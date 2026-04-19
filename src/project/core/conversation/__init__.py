"""
Conversation Engine — UI-facing chat orchestration and LLM client.

Paper reference: Section 6.1 — Conversation Engine.
"""

from core.conversation.llm_client import LLMClient
from core.conversation.manager import ConversationManager, TurnResult

__all__ = ["LLMClient", "ConversationManager", "TurnResult"]
