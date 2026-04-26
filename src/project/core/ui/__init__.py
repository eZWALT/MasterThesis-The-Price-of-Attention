"""
TARA UI — Screen renderers for the Streamlit experiment flow.

Each render_*() function draws one screen and returns a value
(True or a data dict) when the user completes it, allowing the
ExperimentController to advance.
"""

from core.ui.screens import (             # noqa: F401
    render_consent,
    render_demographics,
    render_ocean,
    render_baseline,
    render_practice,
    render_trial_intro,
    render_trial_chat,
    render_post_trial_survey,
    render_final_survey,
    render_done,
    _render_ad_card,
)
