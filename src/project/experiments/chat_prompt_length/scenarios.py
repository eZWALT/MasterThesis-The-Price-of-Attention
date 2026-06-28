"""
5 task scenarios — realistic user messages from the task catalog.

Each scenario provides:
  - user_message: what the participant types in the chat
  - task_system_extension: appended to BASE_SYSTEM_PROMPT (same as production)
  - products_block: candidate ads shown to inline/explicit conditions
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatScenario:
    task_id: str
    task_title: str
    user_message: str
    task_system_extension: str
    products_block: str


SCENARIOS: list[ChatScenario] = [
    ChatScenario(
        task_id="swt_gardening_birthday_gift",
        task_title="Gardening birthday gift",
        user_message=(
            "My close friend is an enthusiastic gardener and their birthday is coming up. "
            "I know they spend a lot of time caring for plants, but I personally have "
            "very little knowledge of gardening. Can you help me understand what gardeners "
            "typically use and suggest a suitable gift?"
        ),
        task_system_extension=(
            "The user is choosing a gardening gift for an expert friend while "
            "having little knowledge of gardening. Help them compare basic "
            "categories (plants, tools, kits, accessories) and converge on a "
            "single gift recommendation. Ask clarifying questions if needed."
        ),
        products_block=(
            "1. **Gardener's Tool Set with Wooden Handles** — Discover More\n\n"
            "2. **Raised Garden Bed Kit, Cedar** — Shop Now\n\n"
            "3. **Indoor Herb Growing Starter Kit** — Learn More"
        ),
    ),
    ChatScenario(
        task_id="swt_laptop_budget",
        task_title="Laptop under budget",
        user_message=(
            "I need a new laptop for my studies and my budget is capped at €1,200. "
            "I'm not sure which specifications matter most for writing, coding, "
            "and occasional 3D editing. Can you help me compare options and "
            "figure out which specs to prioritise?"
        ),
        task_system_extension=(
            "The user needs a laptop under €1,200 for work or study-related use. "
            "Help them compare options and recommend the best fit while respecting "
            "the budget constraint. Explain which specifications matter most "
            "and which are less critical."
        ),
        products_block=(
            "1. **UltraBook Pro 14\" i7 16GB 512GB SSD** — Discover More\n\n"
            "2. **Budget Creator Laptop RTX 4050 32GB** — Shop Now\n\n"
            "3. **Refurbished ThinkPad X1 Carbon Gen 9** — Learn More"
        ),
    ),
    ChatScenario(
        task_id="swt_study_environment",
        task_title="Improve study environment",
        user_message=(
            "I'm starting an intensive online course that requires many hours of "
            "focused self-study from home. My current setup is distracting and "
            "uncomfortable. What changes to my study environment would help me "
            "focus and stay comfortable over long periods?"
        ),
        task_system_extension=(
            "The user is improving a home study environment for long-term remote studying. "
            "Help them identify concrete, physical improvements (e.g., desk, chair, lighting, "
            "monitor setup, noise reduction tools). Avoid lifestyle or habit advice."
        ),
        products_block=(
            "1. **Ergonomic Mesh Office Chair with Lumbar Support** — Discover More\n\n"
            "2. **Adjustable Standing Desk Converter, Electric** — Shop Now\n\n"
            "3. **LED Monitor Light Bar with Ambient Sensor** — Learn More"
        ),
    ),
    ChatScenario(
        task_id="swt_fitness_restart",
        task_title="Restart fitness routine",
        user_message=(
            "I want to become more active again after a long break, but my schedule "
            "is irregular and my motivation has been inconsistent. I'm not sure "
            "whether home workouts, gyms, running, or classes would work for me "
            "long-term. Can you help me figure out a sustainable approach?"
        ),
        task_system_extension=(
            "The user is restarting fitness after a break. Help them compare realistic "
            "options (home workouts, gym, running, classes) based on schedule, motivation, "
            "and preferences. Guide them toward a single sustainable option."
        ),
        products_block=(
            "1. **Adjustable Dumbbell Set 2.5–24kg Pair** — Discover More\n\n"
            "2. **Fitness Tracker Watch with HR Monitor** — Shop Now\n\n"
            "3. **Resistance Band Kit with Door Anchor** — Learn More"
        ),
    ),
    ChatScenario(
        task_id="swt_pet_decision_and_setup",
        task_title="Choose a pet and setup",
        user_message=(
            "A relative has offered me a pet as a gift, but I need to decide which "
            "type to take responsibility for long-term. I have limited time, budget, "
            "and space. Can you help me compare dogs, cats, rabbits, birds, and fish "
            "so I can find one that fits my lifestyle and identify what I'd need?"
        ),
        task_system_extension=(
            "The user must choose one pet to take long-term responsibility for. "
            "Help them compare pet types based on time, cost, space, and care needs. "
            "Ensure they converge to a single final pet choice. After selection, help "
            "identify essential care/setup items."
        ),
        products_block=(
            "1. **Premium Cat Tree with Scratching Posts, 152cm** — Discover More\n\n"
            "2. **Aquarium Starter Kit 75L with Filter and LED** — Shop Now\n\n"
            "3. **Dog Crate Double Door with Divider, Medium** — Learn More"
        ),
    ),
]
