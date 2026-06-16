"""
Task definitions for experimental trials.

Each task induces a specific intent genre (Informational, Transactional,
Social) and provides both a participant-facing prompt and a system-prompt
extension so the LLM receives task-aware context.

Paper reference: Section 5.2.2 — Task Design.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class TaskDefinition:
    """A single experimental task prompt with its metadata."""
    id: str
    title: str
    genre: str                          # Informational | Transactional | Social
    participant_prompt: str             # What the participant sees
    system_prompt_extension: str        # Appended to BASE_SYSTEM_PROMPT
    description: str = ""               # Internal researcher note
    gold_items: List[str] = field(default_factory=list)  # ground-truth answers for benchmark metrics


# ── Task catalog ──────────────────────────────────────────────

TASK_CATALOG: list[TaskDefinition] = [
    # ── Simulated Work Task Situations ──────────────────────
    # (Borlund 2003; Borlund & Ingwersen 1997 — realistic information-
    # -seeking scenarios designed to trigger natural search behaviour.)
    #
    # Order matters: first n_trials tasks are the default picks.

    # 1 ──────────────────────────────────────────────────────
    TaskDefinition(
        id="swt_gardening_birthday_gift",
        title="Choose a gardening birthday gift",
        genre="Social",
        participant_prompt=(
            "Your close friend is an enthusiastic gardener and their birthday is coming up. "
            "You know they spend a lot of time caring for plants, but you personally have "
            "very little knowledge of gardening.\n\n"
            "You want to choose a thoughtful and genuinely useful gardening-related gift, "
            "but you are unsure what would be appropriate or not too basic for someone experienced.\n\n"
            "Find information that would help you understand what gardeners typically use "
            "and select a single suitable gift atleast."
        ),
        system_prompt_extension=(
            "The user is choosing a gardening gift for an expert friend while "
            "having little knowledge of gardening. Help them compare basic "
            "categories (plants, tools, kits, accessories) and converge on a "
            "single gift recommendation. Ask clarifying questions if needed."
        ),
        description="Social task — selecting a gardening-related gift for a knowledgeable friend.",
    ),

    # 2 ──────────────────────────────────────────────────────
    TaskDefinition(
        id="swt_laptop_budget",
        title="Choose the best laptop within a budget",
        genre="Transactional",
        participant_prompt=(
            "You need a new laptop for your work or studies, and your "
            "budget is capped at €1,200. You are unsure which "
            "specifications matter most for tasks like writing, 3d-editing, "
            "running software, or other typical workload-related activities, "
            "and you want to avoid overspending on features you will not use.\n\n"
            "Find information that would help you compare laptop options, "
            "understand which specs to prioritise for your needs, and choose "
            "a good fit within your budget."
        ),
        system_prompt_extension=(
            "The user needs a laptop under €1,200 for work or study-related use, "
            "with possible variation in workload depending on their context.\n\n"
            "Help them compare options and recommend the best fit while respecting "
            "the budget constraint. Explain which specifications matter most "
            "(e.g., CPU, RAM, storage, GPU when relevant) and which are less critical.\n\n"
            "Compare concrete models at different price points and highlight trade-offs. "
            "If useful, ask about their intended use to better tailor recommendations, "
            "but keep the focus on helping them reach a single suitable choice."
        ),
        description="Transactional task — comparing laptops under €1,200 and learning which specs matter for the user's needs.",
    ),

    # 3 ──────────────────────────────────────────────────────
    TaskDefinition(
        id="swt_study_environment",
        title="Improve your study environment",
        genre="Transactional",
        participant_prompt=(
            "You are beginning an intensive multi-month online course that will require "
            "many hours of focused self-study from home.\n\n"
            "Your current study setup is distracting and uncomfortable, making it hard to concentrate "
            "for long periods without feeling tired or burned out.\n\n"
            "Find information that would help you decide what changes to your study environment "
            "would improve your ability to focus, stay comfortable, and study effectively over time.\n\n"
            "Focus on tangible home office setup elements such as furniture, equipment, and room setup."
        ),
        system_prompt_extension=(
            "The user is improving a home study environment for long-term remote studying.\n\n"
            "Help them identify concrete, physical improvements (e.g., desk, chair, lighting, monitor setup, "
            "noise reduction tools, organization solutions). Avoid lifestyle or habit advice.\n\n"
            "Keep the output grounded in actionable, physical changes they could implement or buy. "
            "Guide toward a small set of concrete setup improvements that improve comfort and focus."
        ),
        description="Transactional task — improving a physical home office setup for long-term study.",
    ),
    # 4 ──────────────────────────────────────────────────────
    TaskDefinition(
        id="swt_fitness_restart",
        title="Restart your fitness routine",
        genre="Social",
        participant_prompt=(
            "You want to become more active again after a long break, but your schedule is irregular "
            "and your motivation has been inconsistent in the past.\n\n"
            "You are unsure whether home workouts, gyms, running, or structured classes would be realistic "
            "for you long-term.\n\n"
            "Find information that would help you choose a sustainable fitness approach that fits your lifestyle "
            "and constraints and which sport you would like to initiate."
        ),
        system_prompt_extension=(
            "The user is restarting fitness after a break. Help them compare realistic options "
            "(home workouts, gym, running, classes, apps) based on schedule, motivation, and preferences. "
            "Guide them toward a single sustainable option."
        ),
        description="Social task — selecting a sustainable fitness approach.",
    ),

    # 5 ──────────────────────────────────────────────────────
    TaskDefinition(
        id="swt_pet_decision_and_setup",
        title="Choose a pet and prepare its basic setup",
        genre="Informational",
        participant_prompt=(
            "A relative has offered you a pet as a gift, but you must decide which type to take responsibility for long-term.\n\n"
            "You have limited time, budget, and space, and this decision will affect your daily routine for years.\n\n"
            "Different pets (dogs, cats, rabbits, birds, fish, reptiles) vary significantly in care requirements, cost, and commitment.\n\n"
            "Find information that would help you compare options and select one pet that best fits your lifestyle, "
            "then identify the basic items needed to care for it."
        ),
        system_prompt_extension=(
            "The user must choose one pet to take long-term responsibility for. "
            "Help them compare pet types (dogs, cats, rabbits, birds, fish, reptiles) based on time, cost, space, and care needs. "
            "Ensure they converge to a single final pet choice. After selection, help identify essential care/setup items."
        ),
        description="Decision task — choose a pet and identify basic care requirements.",
    ),

    # ── Remaining tasks (order not critical) ────────────────

    TaskDefinition(
        id="swt_new_hobby_lifestyle",
        title="Find a new personal activity",
        genre="Social",
        participant_prompt=(
            "You want to start a new hobby to improve your routine, "
            "wellbeing, or social life. You have limited time and budget, "
            "and you want something that fits your personality and "
            "lifestyle. Find information that would help you identify "
            "suitable hobby options and compare their practical "
            "requirements."
        ),
        system_prompt_extension=(
            "The user wants to start a new hobby to improve wellbeing, "
            "routine, or social life with limited time and budget. Help "
            "them explore options that fit their personality and lifestyle. "
            "Compare practical requirements like cost, time commitment, "
            "space, and learning curve. Ask about their current routine, "
            "interests, and what they want to get out of the hobby."
        ),
        description="Social task — finding a hobby that matches personality, time, and budget constraints.",
    ),
    TaskDefinition(
        id="swt_photography_event",
        title="Document an important event",
        genre="Informational",
        participant_prompt=(
            "You have been asked to photograph a community event for your "
            "organisation. You already have access to a basic camera, but "
            "you are unsure what additional equipment, if any, would help "
            "you capture the event properly. Find information that would "
            "help you prepare an appropriate photography kit for this "
            "situation."
        ),
        system_prompt_extension=(
            "The user is preparing to photograph a community event with a "
            "basic camera. Help them figure out what additional equipment "
            "— lenses, lighting, tripods, memory cards, etc. — would "
            "improve their results. Ask about the venue, lighting "
            "conditions, type of event, and what kind of shots they need."
        ),
        description="Informational task — preparing a photography kit for a community event.",
    ),
    TaskDefinition(
        id="swt_anniversary_surprise",
        title="Plan a 10-year anniversary surprise",
        genre="Social",
        participant_prompt=(
            "Your 10-year anniversary with your partner is coming up. You "
            "want to plan something memorable that reflects your "
            "relationship, shared experiences, and your partner's "
            "preferences, but you are unsure whether a trip, event, "
            "keepsake, or experience would feel most meaningful. Find "
            "information that would help you decide what kinds of "
            "anniversary surprises or experiences might suit this "
            "relationship."
        ),
        system_prompt_extension=(
            "The user is planning a 10-year anniversary surprise for their "
            "partner. Help them think about what would feel most meaningful "
            "— a trip, event, keepsake, or experience — based on their "
            "relationship and shared history. Suggest ideas and help them "
            "weigh the emotional impact of different options. Ask about "
            "their partner's preferences, shared memories, and what has "
            "felt special in the past."
        ),
        description="Social task — planning a meaningful anniversary surprise that reflects the relationship.",
    ),
    TaskDefinition(
        id="swt_plasticfree_living",
        title="Go plastic-free to protect your health",
        genre="Informational",
        participant_prompt=(
            "You have been reading about the health risks of microplastics "
            "and want to reduce your exposure by eliminating as much "
            "plastic from your daily life as possible. You know this is "
            "an almost impossible task, but you want to find out where "
            "plastic hides in your food, household products, clothing, "
            "and personal care items, and what realistic alternatives "
            "exist. Find information that would help you identify the "
            "biggest sources of plastic in everyday life and discover "
            "practical ways to avoid them."
        ),
        system_prompt_extension=(
            "The user wants to reduce microplastic exposure by going "
            "plastic-free. Help them discover where plastic is hidden in "
            "daily life — food packaging, kitchen utensils, clothing "
            "fibres, personal care products, household items — and what "
            "alternatives exist. Be realistic: acknowledge that complete "
            "elimination is nearly impossible, but help prioritise the "
            "changes with the biggest impact. Compare swaps by cost, "
            "convenience, and effectiveness. Ask about their diet, "
            "household routines, and which areas of life they most want "
            "to change."
        ),
        description="Informational task — discovering hidden sources of plastic in daily life and finding realistic alternatives to reduce microplastic exposure.",
    ),
    TaskDefinition(
        id="swt_dev_role_setup",
        title="Prepare for a software development role",
        genre="Informational",
        participant_prompt=(
            "You are starting a new software development project from home. "
            "You need to make sure your working setup can support coding, "
            "testing, video meetings, and occasional travel, while staying "
            "within a limited equipment allowance. Find information that "
            "would help you decide what type of computer setup would be "
            "appropriate for this work situation."
        ),
        system_prompt_extension=(
            "The user is setting up a home workstation for software "
            "development. Help them identify what hardware and peripherals "
            "they need — considering coding, testing, video calls, and "
            "portability — within a limited budget. Ask about their "
            "specific tech stack, meeting frequency, and travel needs."
        ),
        description="Informational task — researching a home dev workstation within a budget.",
    ),
    TaskDefinition(
        id="swt_remote_collab",
        title="Set up for remote collaboration",
        genre="Informational",
        participant_prompt=(
            "You have joined a distributed team and will spend several "
            "hours a day in video calls, sometimes from noisy environments. "
            "You need to avoid audio problems and fatigue during meetings. "
            "Find information that would help you identify what features "
            "matter in a suitable communication setup."
        ),
        system_prompt_extension=(
            "The user needs a communication setup for long daily video "
            "calls in noisy environments. Help them identify key features "
            "for headsets, microphones, webcams, and software that reduce "
            "audio problems and meeting fatigue. Ask about their workspace, "
            "noise level, and meeting patterns."
        ),
        description="Informational task — finding the right communication gear for remote work.",
    ),
    TaskDefinition(
        id="swt_pricing_strategy",
        title="Plan pricing for a small online service",
        genre="Informational",
        participant_prompt=(
            "You help manage a small online business that is about to "
            "launch a new product or service. You need to set prices that "
            "are competitive but still cover costs and leave a reasonable "
            "margin. Find information that would help you compare pricing "
            "strategies, competitor signals, and margin considerations."
        ),
        system_prompt_extension=(
            "The user is setting prices for a new online product or "
            "service. Help them explore pricing strategies (cost-plus, "
            "value-based, competitive), understand competitor pricing "
            "signals, and balance margin with market positioning. Ask "
            "about their cost structure, target market, and competitive "
            "landscape."
        ),
        description="Informational task — researching pricing strategies for a small online business.",
    ),
    TaskDefinition(
        id="swt_choose_destination",
        title="Choose a destination for a break",
        genre="Transactional",
        participant_prompt=(
            "You have time available for a short trip and want the "
            "destination to match your budget, interests, travel style, "
            "and tolerance for crowds or long journeys. Find information "
            "that would help you identify destinations that fit this "
            "travel situation."
        ),
        system_prompt_extension=(
            "The user is choosing a destination for a short break. Help "
            "them compare options that match their budget, interests, "
            "travel style, and tolerance for crowds or long travel times. "
            "Ask about their budget range, preferred climate, activities, "
            "and travel duration preferences."
        ),
        description="Transactional task — choosing a travel destination that fits personal constraints.",
    ),
    TaskDefinition(
        id="swt_dinner_party",
        title="Organise a small dinner party",
        genre="Transactional",
        participant_prompt=(
            "You are hosting a dinner for a few close friends with "
            "different tastes and dietary preferences. You want the evening "
            "to feel relaxed and thoughtful, but you are unsure how to plan "
            "the food, atmosphere, and small details. Find information that "
            "would help you plan a dinner experience that fits the guests, "
            "setting, and budget."
        ),
        system_prompt_extension=(
            "The user is organising a dinner party for friends with "
            "diverse dietary preferences. Help them plan a menu, "
            "atmosphere, and small details that work for everyone. Suggest "
            "recipes, table settings, and hosting tips. Ask about dietary "
            "restrictions, budget, cooking skill level, and the kind of "
            "evening they want to create."
        ),
        description="Transactional task — planning a dinner party for guests with diverse preferences.",
    ),
    TaskDefinition(
        id="swt_friend_new_job",
        title="Help a friend start a new job",
        genre="Social",
        participant_prompt=(
            "A close friend is starting their first professional role after "
            "graduation. You want to support them with something useful or "
            "encouraging, but you do not know what would actually help them "
            "in their new routine. Find information that would help you "
            "understand what kinds of support, tools, or gestures are "
            "useful for someone starting a new job."
        ),
        system_prompt_extension=(
            "The user wants to help a friend who is starting their first "
            "professional role. Help them think about practical support, "
            "useful tools or gifts, and encouraging gestures that would "
            "genuinely help someone adjusting to a new work routine. Ask "
            "about the friend's industry, work style, and what stage of "
            "preparation they are in."
        ),
        description="Social task — finding useful support or gifts for a friend starting a new job.",
    ),
    TaskDefinition(
        id="swt_friend_moving_abroad",
        title="Support a friend who is moving abroad",
        genre="Social",
        participant_prompt=(
            "A close friend is relocating to another country for work or "
            "study. You want to help them prepare emotionally and "
            "practically, but you are unsure what would be genuinely "
            "useful before they leave. Find information that would help "
            "you identify practical resources, keepsakes, or supportive "
            "gestures for someone moving abroad."
        ),
        system_prompt_extension=(
            "The user wants to support a friend who is moving abroad. Help "
            "them think about practical help, meaningful keepsakes, and "
            "supportive gestures that would be genuinely useful before the "
            "departure. Ask about the friend's destination, reason for "
            "moving, how long they'll be away, and what kind of person "
            "they are."
        ),
        description="Social task — finding practical and emotional support ideas for a friend moving abroad.",
    ),
    TaskDefinition(
        id="swt_creative_weekend",
        title="Plan a creative weekend project",
        genre="Social",
        participant_prompt=(
            "You have a free weekend and want to do something creative "
            "rather than spend the time passively. You would like the "
            "project to be enjoyable, achievable in two days, and suited "
            "to your interests and available space. Find information that "
            "would help you compare creative project ideas and decide "
            "which would be realistic and rewarding."
        ),
        system_prompt_extension=(
            "The user wants a creative weekend project that is enjoyable, "
            "achievable in two days, and suited to their interests and "
            "space. Help them compare ideas — cooking, writing, crafting, "
            "DIY, digital projects, etc. — and assess which are realistic "
            "and rewarding. Ask about their interests, available tools and "
            "materials, space constraints, and past creative experience."
        ),
        description="Social task — comparing creative weekend project ideas that are realistic and rewarding.",
    ),
]

TASK_BY_ID: dict[str, TaskDefinition] = {t.id: t for t in TASK_CATALOG}
