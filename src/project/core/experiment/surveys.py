"""
Survey definitions and scoring utilities.

All item definitions, scale bounds, and scoring logic live here.
"""

from __future__ import annotations

from typing import Dict, List, Literal

# ─────────────────────────────────────────────────────────────
# Supported BFI versions
# ─────────────────────────────────────────────────────────────
BFI_VERSION = Literal["10", "44"]
BFI_VERSIONS = {"10", "44"}

# ═══════════════════════════════════════════════════════════════
# OCEAN — BFI-44 (John & Srivastava, 1999)
# Source: John, O. P., & Srivastava, S. (1999). The Big Five trait
# taxonomy: History, measurement, and theoretical perspectives.
# In L. A. Pervin & O. P. John (Eds.), Handbook of personality:
# Theory and research (Vol. 2, pp. 102-138). Guilford Press.
# Items & scoring key sourced from:
# https://github.com/coppermare/ai-like-humans (MIT licence)
# ═══════════════════════════════════════════════════════════════
# Each item: (text, trait, reversed)
# Scoring: 1–5 Likert.  Reversed items: score = 6 − raw.
# Trait score = mean of domain items (after reversal).
# Domain sizes: E=8, A=9, C=9, N=8, O=10  (total 44)
OCEAN_SCALE_MIN: int = 1
OCEAN_SCALE_MAX: int = 5
OCEAN_SCALE_LABELS: dict[int, str] = {
    1: "Disagree strongly",
    2: "Disagree a little",
    3: "Neither agree nor disagree",
    4: "Agree a little",
    5: "Agree strongly",
}

# Instruction prefix shown once above the item list
OCEAN_INSTRUCTIONS: str = (
    "Describe yourself as you generally are now, not as you wish to be in the "
    "future. Describe yourself as you honestly see yourself, in relation to "
    "other people you know of the same sex as you are, and roughly your same "
    "age. Rate how much each statement applies to you."
)

OCEAN_ITEMS: list[tuple[str, str, bool]] = [
    # (statement, trait_key, is_reversed)
    # --- Extraversion (E): items 1, 6R, 11, 16, 21R, 26, 31R, 36
    ("I see myself as someone who is talkative.",                           "E", False),  #  1
    ("I see myself as someone who tends to find fault with others.",        "A", True),   #  2
    ("I see myself as someone who does a thorough job.",                    "C", False),  #  3
    ("I see myself as someone who is depressed, blue.",                     "N", False),  #  4
    ("I see myself as someone who is original, comes up with new ideas.",   "O", False),  #  5
    ("I see myself as someone who is reserved.",                            "E", True),   #  6R
    ("I see myself as someone who is helpful and unselfish with others.",   "A", False),  #  7
    ("I see myself as someone who can be somewhat careless.",               "C", True),   #  8R
    ("I see myself as someone who is relaxed, handles stress well.",        "N", True),   #  9R
    ("I see myself as someone who is curious about many different things.", "O", False),  # 10
    ("I see myself as someone who is full of energy.",                      "E", False),  # 11
    ("I see myself as someone who starts quarrels with others.",            "A", True),   # 12R
    ("I see myself as someone who is a reliable worker.",                   "C", False),  # 13
    ("I see myself as someone who can be tense.",                           "N", False),  # 14
    ("I see myself as someone who is ingenious, a deep thinker.",           "O", False),  # 15
    ("I see myself as someone who generates a lot of enthusiasm.",          "E", False),  # 16
    ("I see myself as someone who has a forgiving nature.",                 "A", False),  # 17
    ("I see myself as someone who tends to be disorganized.",               "C", True),   # 18R
    ("I see myself as someone who worries a lot.",                          "N", False),  # 19
    ("I see myself as someone who has an active imagination.",              "O", False),  # 20
    ("I see myself as someone who tends to be quiet.",                      "E", True),   # 21R
    ("I see myself as someone who is generally trusting.",                  "A", False),  # 22
    ("I see myself as someone who tends to be lazy.",                       "C", True),   # 23R
    ("I see myself as someone who is emotionally stable, not easily upset.","N", True),   # 24R
    ("I see myself as someone who is inventive.",                           "O", False),  # 25
    ("I see myself as someone who has an assertive personality.",           "E", False),  # 26
    ("I see myself as someone who can be cold and aloof.",                  "A", True),   # 27R
    ("I see myself as someone who perseveres until the task is finished.",  "C", False),  # 28
    ("I see myself as someone who can be moody.",                           "N", False),  # 29
    ("I see myself as someone who values artistic, aesthetic experiences.", "O", False),  # 30
    ("I see myself as someone who is sometimes shy, inhibited.",            "E", True),   # 31R
    ("I see myself as someone who is considerate and kind to almost everyone.", "A", False),  # 32
    ("I see myself as someone who does things efficiently.",                "C", False),  # 33
    ("I see myself as someone who remains calm in tense situations.",       "N", True),   # 34R
    ("I see myself as someone who prefers work that is routine.",           "O", True),   # 35R
    ("I see myself as someone who is outgoing, sociable.",                  "E", False),  # 36
    ("I see myself as someone who is sometimes rude to others.",            "A", True),   # 37R
    ("I see myself as someone who makes plans and follows through with them.", "C", False),  # 38
    ("I see myself as someone who gets nervous easily.",                    "N", False),  # 39
    ("I see myself as someone who likes to reflect, play with ideas.",      "O", False),  # 40
    ("I see myself as someone who has few artistic interests.",             "O", True),   # 41R
    ("I see myself as someone who likes to cooperate with others.",         "A", False),  # 42
    ("I see myself as someone who is easily distracted.",                   "C", True),   # 43R
    ("I see myself as someone who is sophisticated in art, music, or literature.", "O", False),  # 44
]

# ═══════════════════════════════════════════════════════════════
# OCEAN — BFI-10 (Rammstedt & John, 2007)
# Source: Rammstedt, B., & John, O. P. (2007). Measuring personality
# in one minute or less: A 10-item short version of the Big Five
# Inventory in English and German. Journal of Research in Personality,
# 41(1), 203-212. https://doi.org/10.1016/j.jrp.2006.02.001
# ═══════════════════════════════════════════════════════════════
# Each item: (text, trait, reversed)
# Scoring: 1–5 Likert.  Reversed items: score = 6 − raw.
# Trait score = mean of 2 domain items (after reversal).
# Domain sizes: E=2, A=2, C=2, N=2, O=2  (total 10)
BFI10_ITEMS: list[tuple[str, str, bool]] = [
    # (statement, trait_key, is_reversed)
    ("I see myself as someone who is reserved.",                              "E", True),   #  1R
    ("I see myself as someone who is generally trusting.",                    "A", False),  #  2
    ("I see myself as someone who tends to be lazy.",                         "C", True),   #  3R
    ("I see myself as someone who is relaxed, handles stress well.",          "N", True),   #  4R
    ("I see myself as someone who has few artistic interests.",               "O", True),   #  5R
    ("I see myself as someone who is outgoing, sociable.",                    "E", False),  #  6
    ("I see myself as someone who tends to find fault with others.",          "A", True),   #  7R
    ("I see myself as someone who does a thorough job.",                      "C", False),  #  8
    ("I see myself as someone who gets nervous easily.",                      "N", False),  #  9
    ("I see myself as someone who has an active imagination.",                "O", False),  # 10
]


def get_ocean_items(version: str = "10") -> list[tuple[str, str, bool]]:
    """Return the BFI item list for the requested version ("10" or "44")."""
    if version == "10":
        return BFI10_ITEMS
    return OCEAN_ITEMS


# ═══════════════════════════════════════════════════════════════
# POST-CONDITION SURVEY  (after each condition chat — Workflow A*)
# ═══════════════════════════════════════════════════════════════
POST_CONDITION_SCALE_MIN: int = 1
POST_CONDITION_SCALE_MAX: int = 7
POST_CONDITION_ITEMS: list[dict[str, str]] = [
    # ── Perceived Usefulness ──
    {"id": "usefulness_effective",   "text": "The assistant helped me complete the task effectively."},
    {"id": "usefulness_decision",    "text": "The assistant improved the quality of my decision making."},
    {"id": "usefulness_informative", "text": "The assistant provided helpful information for my task."},
    # ── Trust in the System ──
    {"id": "trust_reliable",  "text": "I felt confident that the information provided by the assistant was reliable."},
    {"id": "trust_overall",   "text": "I trusted the assistant during the interaction."},
    {"id": "trust_rely",      "text": "I would rely on the assistant\u2019s suggestions for making decisions."},
    # ── Perceived Intrusiveness and Manipulative Influence ──
    {"id": "intrusiveness_influence",  "text": "I felt the assistant was trying to influence my decisions."},
    {"id": "intrusiveness_interrupt",  "text": "The assistant interrupted my workflow with content that was not directly relevant to the task."},
    {"id": "intrusiveness_steer",      "text": "The assistant led and steered the conversation in a direction I did not fully control."},
    # ── Satisfaction with the Experience ──
    {"id": "satisfaction_overall",      "text": "I am satisfied with the experience of using this assistant."},
    {"id": "satisfaction_expectations", "text": "The assistant met my expectations."},
    {"id": "satisfaction_positive",     "text": "I had a positive experience interacting with this assistant."},
]

# ═══════════════════════════════════════════════════════════════
# POST-TRIAL SURVEY  (after each chat trial — legacy, kept for compat)
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
# GLOBAL EVALUATION  (end of session — Workflow A*)
# ═══════════════════════════════════════════════════════════════
GLOBAL_EVAL_SCALE_MIN: int = 1
GLOBAL_EVAL_SCALE_MAX: int = 7
GLOBAL_EVAL_ITEMS: list[dict[str, str]] = [
    {"id": "overall_trust",     "text": "Overall, I trusted the AI assistant across all conversations."},
    {"id": "overall_usefulness","text": "Overall, the assistant was useful for my shopping tasks."},
    {"id": "ad_awareness",      "text": "I noticed promotional content during the conversations."},
    {"id": "ad_disruption",     "text": "The promotional content disrupted my experience."},
    {"id": "willingness_reuse", "text": "I would use a similar AI assistant again in the future."},
]

GLOBAL_OPEN_ENDED_PROMPT: str = (
    "Did you notice anything unusual during the conversations? "
    "Any other comments? (optional)"
)

# ═══════════════════════════════════════════════════════════════
# FINAL SURVEY  (end of session — legacy)
# ═══════════════════════════════════════════════════════════════
FINAL_SURVEY_ITEMS: list[dict[str, str]] = [
    {"id": "overall_trust",    "text": "Overall, I trusted the AI assistant across all conversations."},
    {"id": "ad_awareness",     "text": "I noticed promotional content during the conversations."},
    {"id": "ad_disruption",    "text": "The promotional content disrupted my experience."},
    {"id": "willingness_reuse","text": "I would use a similar AI assistant again in the future."},
]
FINAL_OPEN_ENDED_PROMPT: str = (
    "Did you notice anything unusual during the conversations? "
    "Any other comments? (optional)"
)


def score_ocean(
    raw_responses: List[int],
    items: list[tuple[str, str, bool]] | None = None,
) -> Dict[str, float]:
    """
    Compute Big Five trait scores from raw BFI responses.

    Parameters
    ----------
    raw_responses : list of ints (1–5 Likert), one per item in *items*.
    items : item list to score against.  Defaults to BFI10_ITEMS (BFI-10).
            Pass ``get_ocean_items("44")`` for BFI-44.

    Returns
    -------
    Dict with keys O, C, E, A, N → float (1.0–5.0 each).
    """
    if items is None:
        items = BFI10_ITEMS
    if len(raw_responses) != len(items):
        raise ValueError(
            f"Expected {len(items)} responses, got {len(raw_responses)}"
        )

    for i, (raw, (text, _trait, _rev)) in enumerate(zip(raw_responses, items)):
        if not (OCEAN_SCALE_MIN <= raw <= OCEAN_SCALE_MAX):
            raise ValueError(
                f"Response {i + 1} is out of range: got {raw!r}, "
                f"expected {OCEAN_SCALE_MIN}–{OCEAN_SCALE_MAX} "
                f"(item: '{text[:40]}')"
            )

    trait_sums: Dict[str, float] = {}
    trait_counts: Dict[str, int] = {}

    for raw, (_, trait, reversed_) in zip(raw_responses, items):
        score = (OCEAN_SCALE_MAX + 1) - raw if reversed_ else raw
        trait_sums[trait] = trait_sums.get(trait, 0.0) + score
        trait_counts[trait] = trait_counts.get(trait, 0) + 1

    return {
        trait: trait_sums[trait] / trait_counts[trait]
        for trait in trait_sums
    }
