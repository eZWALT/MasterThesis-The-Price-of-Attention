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
# POST-CONDITION SURVEY — Section 1: LLM Performance Evaluation
# (adapted from "Ads That Talk Back" paper)
# 15 items, 7-pt Likert, flat list in fixed presentation order
# ═══════════════════════════════════════════════════════════════
POST_CONDITION_SCALE_MIN: int = 1
POST_CONDITION_SCALE_MAX: int = 7

POST_CONDITION_LLM_ITEMS: list[dict[str, str]] = [
    {"id": "llm_reliable",       "text": "The chatbot provided reliable responses."},
    {"id": "llm_helpful",        "text": "The chatbot gave helpful responses."},
    {"id": "llm_made_up",        "text": "The chatbot made up information that was not real."},
    {"id": "llm_changed_mind",   "text": "The chatbot\u2019s responses changed my mind."},
    {"id": "llm_not_useful",     "text": "The chatbot gave responses that were not useful."},
    {"id": "llm_neutral",        "text": "The chatbot gave neutral (fair) responses."},
    {"id": "llm_false",          "text": "The chatbot provided false information."},
    {"id": "llm_addressed",      "text": "The chatbot adequately addressed my request."},
    {"id": "llm_impartial",      "text": "The chatbot gave impartial and unbiased responses."},
    {"id": "llm_suggestions",    "text": "The chatbot\u2019s suggestions addressed my questions."},
    {"id": "llm_opinionated",    "text": "The chatbot provided opinionated responses."},
    {"id": "llm_not_aid",        "text": "The chatbot gave a response that did not aid me."},
    {"id": "llm_skeptical",      "text": "I was skeptical of the chatbot\u2019s responses."},
    {"id": "llm_relevant",       "text": "The chatbot gave relevant responses."},
    {"id": "llm_convincing",     "text": "The chatbot provided convincing responses."},
]

# ═══════════════════════════════════════════════════════════════
# POST-CONDITION SURVEY — Section 2: Chatbot Personality
# First 3 items are 7-pt Likert with open-text elaboration.
# Last 2 are open-ended only.
# ═══════════════════════════════════════════════════════════════

POST_CONDITION_PERSONALITY_LIKERT: list[dict[str, str]] = [
    {"id": "personality_trust",        "text": "Do you trust the chatbot?",                          "elaboration": "Briefly, why or why not? (Optional)"},
    {"id": "personality_influence",    "text": "Did the chatbot influence your approach to handling tasks?", "elaboration": "If so, give an example. (Optional)"},
    {"id": "personality_changed_mind", "text": "Did the chatbot change your mind about anything?",          "elaboration": "If so, give an example. (Optional)"},
]

POST_CONDITION_PERSONALITY_OPEN: list[dict[str, str]] = [
    {"id": "personality_brands",    "text": "Did the chatbot mention any products/brands in its responses? If yes, how did you feel about the product/brand suggestions?"},
    {"id": "personality_sponsored", "text": "Did you notice or click on any \u201csponsored\u201d buttons? If yes, what did you think of the generated profile?"},
]

# ═══════════════════════════════════════════════════════════════
# POST-CONDITION SURVEY — Section 3: LLM Behaviours
# 2 items, 7-pt Likert
# ═══════════════════════════════════════════════════════════════

POST_CONDITION_BEHAVIOUR_ITEMS: list[dict[str, str]] = [
    {"id": "behaviour_pushing",    "text": "I felt like the chatbot was pushing or marketing content to me."},
    {"id": "behaviour_manipulate", "text": "I felt like the chatbot was trying to manipulate me through its response."},
]

# Keep legacy definitions for reference
POST_CONDITION_ITEMS_LEGACY: list[dict[str, str]] = [
    {"id": "usefulness_effective",   "text": "The assistant helped me complete the task effectively."},
    {"id": "usefulness_decision",    "text": "The assistant improved the quality of my decision making."},
    {"id": "usefulness_informative", "text": "The assistant provided helpful information for my task."},
    {"id": "trust_reliable",  "text": "I felt confident that the information provided by the assistant was reliable."},
    {"id": "trust_overall",   "text": "I trusted the assistant during the interaction."},
    {"id": "trust_rely",      "text": "I would rely on the assistant\u2019s suggestions for making decisions."},
    {"id": "intrusiveness_influence",  "text": "I felt the assistant was trying to influence my decisions."},
    {"id": "intrusiveness_interrupt",  "text": "The assistant interrupted my workflow with content that was not directly relevant to the task."},
    {"id": "intrusiveness_steer",      "text": "The assistant led and steered the conversation in a direction I did not fully control."},
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
# GLOBAL EVALUATION  (end of session — Workflow B)
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

# ═══════════════════════════════════════════════════════════════
# ADS AWARENESS  (post-experiment, Section 1)
# ═══════════════════════════════════════════════════════════════
ADS_AWARENESS_SCALE_MIN: int = 1
ADS_AWARENESS_SCALE_MAX: int = 7

ADS_AWARENESS_CATEGORICAL: list[dict] = [
    {"id": "aware_noticed",     "text": "Did you notice any additional content that was not directly related to the task?",                "options": ["Yes", "No"]},
    {"id": "aware_confidence",  "text": "How confident are you in your answer above?",                                                    "options": ["Low", "Medium", "High"]},
    {"id": "aware_which_tasks", "text": "In which tasks (if any) did you notice this?",                                                   "options": ["Task 1", "Task 2", "Task 3", "Task 4", "Task 5", "Not sure / cannot recall"]},
    {"id": "aware_when",        "text": "When did you notice this?",                                                                      "options": ["Early in the interaction", "Later in the interaction", "Throughout the interaction", "Not sure"]},
    {"id": "aware_where",       "text": "Where did you notice this?",                                                                     "options": ["Within the assistant\u2019s responses", "In separate UI elements or sections", "Both", "Not sure"]},
    {"id": "aware_brands",      "text": "Did the chatbot mention any brands, products, or external references during the interaction?",   "options": ["Yes", "No", "Not sure"]},
]

ADS_AWARENESS_OPEN_ENDED: list[dict] = [
    {"id": "aware_description",       "text": "What did you notice? Please describe briefly.",                                        "optional": True},
    {"id": "aware_brands_description","text": "If yes, please briefly describe what you remember.",                                   "optional": True},
]

# ═══════════════════════════════════════════════════════════════
# ADS RECALL  (post-experiment, 4-step — one per ad condition)
# Trust / credibility upgrade: 7 Likert + 1 open-ended.
# Separates ad-level credibility from system-level trust shift.
# ═══════════════════════════════════════════════════════════════
RECALL_SCALE_MIN: int = 1
RECALL_SCALE_MAX: int = 7

RECALL_ITEMS: list[dict[str, str]] = [
    {"id": "recall_noticeability",  "text": "How noticeable was this content in the conversation?"},
    {"id": "recall_memory",         "text": "How well do you remember this content?"},
    {"id": "recall_relevance",      "text": "How relevant was this content to your task?"},
    {"id": "recall_influence",      "text": "How much did this content influence your decisions or thinking?"},
    {"id": "recall_intrusiveness",  "text": "How intrusive was this content in the conversation?"},
    {"id": "recall_credibility",    "text": "How trustworthy did this content feel?"},
    {"id": "recall_trust_shift",    "text": "After seeing this content, how much do you trust the AI system overall?"},
]

RECALL_OPEN_ENDED: list[dict[str, str]] = [
    {"id": "recall_reaction", "text": "Please describe your reaction to this content. What stood out to you, and how did it fit (or not fit) within the conversation? Feel free to share anything you liked, disliked, found useful, found distracting, or found unusual, as well as what you think the purpose of this content was."},
]

# ═══════════════════════════════════════════════════════════════
# ADS PERCEPTION  (post-experiment, Section 3)
# ═══════════════════════════════════════════════════════════════
ADS_PERCEPTION_SCALE_MIN: int = 1
ADS_PERCEPTION_SCALE_MAX: int = 7

ADS_PERCEPTION_LIKERT: list[dict] = [
    {"id": "perception_advertising", "text": "I felt like the chatbot was advertising or marketing content to me."},
    {"id": "perception_manipulate",  "text": "I felt like the chatbot was trying to influence or manipulate me through its responses."},
    {"id": "perception_companies",   "text": "I think that technology companies will start integrating advertising into their chatbots (e.g., ChatGPT, Claude, Grok, Gemini, Bing Chat, etc.)."},
]

ADS_PERCEPTION_OPEN_ENDED: list[dict] = [
    {"id": "perception_benefits_drawbacks", "text": "Briefly, what do you see as the benefits or drawbacks of advertising through chatbots?", "optional": False},
    {"id": "perception_detect",             "text": "Do you think you could tell whether a chatbot was instructed to advertise content to you? If yes, how do you think you could tell?", "optional": False},
    {"id": "perception_interesting",        "text": "Was there a response from the chatbot you found interesting or problematic that you would like to highlight?", "optional": True},
]

# ═══════════════════════════════════════════════════════════════
# LLM PERFORMANCE EVALUATION  (post-experiment, Section 4)
# 5 constructs × 3 items = 15 items, 7-pt Likert
# ═══════════════════════════════════════════════════════════════
LLM_EVAL_SCALE_MIN: int = 1
LLM_EVAL_SCALE_MAX: int = 7

LLM_EVAL_CATEGORIES: dict[str, list[dict]] = {
    "Credibility": [
        {"id": "credibility_reliable",  "text": "The chatbot provided reliable responses."},
        {"id": "credibility_false",     "text": "The chatbot provided false information."},
        {"id": "credibility_made_up",   "text": "The chatbot made up information that was not real."},
    ],
    "Helpfulness": [
        {"id": "helpfulness_helpful",    "text": "The chatbot gave helpful responses."},
        {"id": "helpfulness_addressed",  "text": "The chatbot adequately addressed my request."},
        {"id": "helpfulness_not_aid",    "text": "The chatbot gave a response that did not aid me."},
    ],
    "Convincingness": [
        {"id": "convincingness_convincing",    "text": "The chatbot provided convincing responses."},
        {"id": "convincingness_changed_mind",  "text": "The chatbot\u2019s responses changed my mind."},
        {"id": "convincingness_skeptical",     "text": "I was skeptical of the chatbot\u2019s responses."},
    ],
    "Relevance": [
        {"id": "relevance_relevant",    "text": "The chatbot gave relevant responses."},
        {"id": "relevance_addressed",   "text": "The chatbot\u2019s suggestions addressed my questions."},
        {"id": "relevance_not_useful",  "text": "The chatbot gave responses that were not useful."},
    ],
    "Neutrality": [
        {"id": "neutrality_neutral",      "text": "The chatbot gave neutral (fair) responses."},
        {"id": "neutrality_impartial",    "text": "The chatbot gave impartial and unbiased responses."},
        {"id": "neutrality_opinionated",  "text": "The chatbot provided opinionated responses."},
    ],
}

def flatten_llm_eval_items() -> list[dict]:
    items: list[dict] = []
    for _cat, cat_items in LLM_EVAL_CATEGORIES.items():
        items.extend(cat_items)
    return items

# ═══════════════════════════════════════════════════════════════
# GODSPEED (simplified)  (post-experiment, Section 5)
# 7 semantic differentials + 2 re-ask Likerts
# ═══════════════════════════════════════════════════════════════
GODSPEED_SCALE_MIN: int = 1
GODSPEED_SCALE_MAX: int = 7

GODSPEED_SEMANTIC: list[dict] = [
    {"id": "godspeed_positive",     "text": "Positive \u2013 Negative",          "left": "Positive",     "right": "Negative"},
    {"id": "godspeed_friendly",     "text": "Friendly \u2013 Unfriendly",       "left": "Friendly",     "right": "Unfriendly"},
    {"id": "godspeed_competent",    "text": "Competent \u2013 Incompetent",      "left": "Competent",    "right": "Incompetent"},
    {"id": "godspeed_sensible",     "text": "Sensible \u2013 Foolish",           "left": "Sensible",     "right": "Foolish"},
    {"id": "godspeed_responsible",  "text": "Responsible \u2013 Irresponsible",  "left": "Responsible",  "right": "Irresponsible"},
    {"id": "godspeed_knowledgeable","text": "Knowledgeable \u2013 Ignorant",     "left": "Knowledgeable","right": "Ignorant"},
    {"id": "godspeed_pleasant",     "text": "Pleasant \u2013 Unpleasant",        "left": "Pleasant",     "right": "Unpleasant"},
]

GODSPEED_REASK_LIKERT: list[dict] = [
    {"id": "reuse_assistant", "text": "Based on your experience, would you use this assistant again?"},
    {"id": "reuse_system",    "text": "How likely are you to use a system like this in the future?"},
]

# ═══════════════════════════════════════════════════════════════
# DEMOGRAPHICS  (post-experiment, extended)
# ═══════════════════════════════════════════════════════════════

DEMOGRAPHICS_TEXT: list[dict] = [
    {"id": "demo_age",       "text": "Age (Optional)"},
    {"id": "demo_occupation","text": "Please type your occupation below or leave it blank if you prefer not to say. (Optional)"},
]

DEMOGRAPHICS_SELECT: list[dict] = [
    {"id": "demo_sex",       "text": "Sex",                    "options": ["Female", "Male", "Non-binary", "Prefer not to say"]},
    {"id": "demo_education", "text": "Highest achieved level of education", "options": ["High School", "Bachelor's Degree", "Master's Degree", "PhD", "Other"]},
    {"id": "demo_familiarity", "text": "Please indicate your level of familiarity with chatbots. (E.g., ChatGPT, Gemini, etc.)", "options": ["Unfamiliar", "Somewhat Unfamiliar", "Somewhat Familiar", "Familiar"]},
    {"id": "demo_frequency", "text": "How frequently do you use chatbots?", "options": ["Fewer than 5 times ever", "1\u20135 times per month", "1\u20135 times per week", "1\u20135 times per day", "Greater than 5 times per day"]},
]


# ═══════════════════════════════════════════════════════════════
# DECEPTION DISCLOSURE TEXT
# ═══════════════════════════════════════════════════════════════
DECEPTION_DISCLOSURE_TEXT: str = (
    "In this study, we utilized deception to avoid biasing the study responses. "
    "In actuality, we are not only studying the viability of creating personalities for AI. "
    "The primary focus of our study is related to using chatbots for advertising purposes. "
    "We are interested in studying the potential risks and ethical concerns of having chatbots serve advertisements. "
    "We needed to use deception to avoid biasing your behavior. In particular, we did not want you to focus on or "
    "actively look for advertisements and sponsored content within the chatbot\u2019s responses. "
    "We also did not want you to view the chatbot in a negative or adversarial light due to preconceived feelings towards advertising. "
    "Please note that any advertisements which may have been served to you were not actual advertisements, just simulated ones. "
    "We are not affiliated, sponsored by, or associated with any of the brands that may have been mentioned by the chatbot. "
    "These products and brands were selected randomly, and there were no sponsorships or connections between us or our research study "
    "and these products/brands. We understand if you feel troubled as a result of this deception. "
    "At this point, you have the option to withdraw your participation and data from this study and retain 100% of the original "
    "agreed-upon compensation. If you would like to continue participating in the remainder of this study, you may click ahead to the next page. "
    "For full transparency and disclosure, here is what we instructed ChatGPT to do during your interactions with it: "
    "To mention the product/brand in a positive light when the timing or topic is relevant, and to personalize its response "
    "to the user when promoting the product/brand. By typing \u201cWithdraw\u201d into the entry below: I am indicating that I wish to "
    "withdraw my participation and data from this study. If you wish to continue in the study, simply click to the next page "
    "without typing into the field below. Type \u201cWithdraw\u201d below if you would like to withdraw from this study. "
    "Otherwise, leave this blank and continue."
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
