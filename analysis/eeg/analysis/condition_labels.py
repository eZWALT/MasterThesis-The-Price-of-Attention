"""Paper display names for EEG conditions and contrasts.

Log / Gold keys stay ``inline_*`` and ``block_*``. Do not rename those
fields. Every figure and caption uses implicit / explicit.
"""

CONDITION_LABELS = {
    "no_ads": "No ads",
    "inline_early": "Implicit early",
    "inline_late": "Implicit late",
    "block_early": "Explicit early",
    "block_late": "Explicit late",
}

PATH_A_LABELS = {
    "any_ad_vs_no_ads": "Any ad − no ads",
    "inline_vs_block": "Implicit − explicit",
    "early_vs_late": "Early − late",
}

PATH_B_LABELS = {
    "inline_early_vs_no_ad_early": "Implicit early",
    "block_early_vs_no_ad_early": "Explicit early",
    "inline_late_vs_no_ad_late": "Implicit late",
    "block_late_vs_no_ad_late": "Explicit late",
}

CONDITION_CONTRAST_LABELS = {
    "any_ad_vs_no_ads": "Any ad − no ads",
    "inline_vs_block": "Implicit − explicit",
    "early_vs_late": "Early − late",
    "format_x_timing": "Format × timing",
}

AD_CONTRAST_LABELS = {
    "inline_early_vs_no_ad_early": "Implicit early − matched no-ad",
    "block_early_vs_no_ad_early": "Explicit early − matched no-ad",
    "inline_late_vs_no_ad_late": "Implicit late − matched no-ad",
    "block_late_vs_no_ad_late": "Explicit late − matched no-ad",
    "any_ad_vs_matched_no_ad": "Any ad − matched no-ad",
    "inline_vs_block": "Implicit − explicit",
    "early_vs_late": "Early − late",
    "format_x_timing": "Format × timing",
}

PATH_B_SLOPE_PANELS = (
    ("inline_early", "no_ads_early", "Implicit early"),
    ("block_early", "no_ads_early", "Explicit early"),
    ("inline_late", "no_ads_late", "Implicit late"),
    ("block_late", "no_ads_late", "Explicit late"),
)
