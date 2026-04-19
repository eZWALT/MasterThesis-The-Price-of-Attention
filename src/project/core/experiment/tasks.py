"""
TARA — Task definitions for experimental trials.

Each task induces a specific intent genre (Informational, Transactional,
Social) and provides both a participant-facing prompt and a system-prompt
extension so the LLM receives task-aware context.

Paper reference: Section 5.2.2 — Task Design.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskDefinition:
    """A single experimental task prompt with its metadata."""
    id: str
    title: str
    genre: str                          # Informational | Transactional | Social
    participant_prompt: str             # What the participant sees
    system_prompt_extension: str        # Appended to BASE_SYSTEM_PROMPT
    description: str = ""               # Internal researcher note


# ── Task catalog ──────────────────────────────────────────────

TASK_CATALOG: list[TaskDefinition] = [
    # ── Informational ────────────────────────────────────────
    TaskDefinition(
        id="info_optimize_routine",
        title="Optimize your daily routine",
        genre="Informational",
        participant_prompt=(
            "Think about your daily routine — what part of your day feels "
            "most inefficient or draining? Chat with the assistant to come "
            "up with concrete ideas to improve it."
        ),
        system_prompt_extension=(
            "The user wants to optimize part of their daily routine. "
            "Help them reflect on their habits and suggest practical, "
            "actionable improvements. Ask follow-up questions to understand "
            "their specific situation."
        ),
        description="Informational task targeting workflow/habit optimization.",
    ),
    # ── Transactional ────────────────────────────────────────
    TaskDefinition(
        id="trans_plan_trip",
        title="Plan a trip",
        genre="Transactional",
        participant_prompt=(
            "You want to plan a realistic trip this year — pick a destination "
            "you're curious about and work with the assistant to build a plan "
            "covering budget, activities, and logistics."
        ),
        system_prompt_extension=(
            "The user is planning a trip. Help them choose a destination, "
            "estimate costs, suggest activities, and work out logistics. "
            "Ask clarifying questions about their preferences, budget, "
            "and constraints."
        ),
        description="Transactional task involving purchase/planning decisions.",
    ),
    TaskDefinition(
        id="trans_find_product",
        title="Find the right product",
        genre="Transactional",
        participant_prompt=(
            "Think of a product you currently need or have been considering "
            "buying (e.g., headphones, a bag, a laptop, a gift). Chat with "
            "the assistant to narrow down the best option for you."
        ),
        system_prompt_extension=(
            "The user is looking for a product recommendation. Help them "
            "define their requirements, compare options, and arrive at a "
            "decision. Ask about budget, use case, and preferences."
        ),
        description="Transactional task focusing on product recommendation.",
    ),
    # ── Social / Reflective ──────────────────────────────────
    TaskDefinition(
        id="social_new_hobby",
        title="Discover a new hobby",
        genre="Social",
        participant_prompt=(
            "You want to find a new hobby that fits your personality and "
            "lifestyle. Chat with the assistant to explore options — think "
            "about what excites you, what you've tried before, and what "
            "you'd like to get out of a hobby."
        ),
        system_prompt_extension=(
            "The user wants to discover a new hobby. Engage them in a "
            "reflective conversation about their interests, lifestyle, "
            "and personality. Suggest creative options and help them "
            "narrow down what fits best."
        ),
        description="Social/reflective task exploring personal interests.",
    ),
]

TASK_BY_ID: dict[str, TaskDefinition] = {t.id: t for t in TASK_CATALOG}
