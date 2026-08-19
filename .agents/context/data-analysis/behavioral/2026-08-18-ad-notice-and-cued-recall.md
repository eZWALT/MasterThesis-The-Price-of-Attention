# Advertisement notice and cued recall (18 August 2026)

Descriptive plots only. Participants are the inferential units.
The first notice/recall dump used n = 45 and a bad glob
(``*_export.jsonl`` + string condition keys only). That missed crowd
1–5 and also dropped ``unfocused`` / ``crowdfail`` by folder name.

**Current finished rule** (no beta, unfinished, synthetic, crowdfail;
unfocused stays if complete): **54** in `tracked/` (18 lab + 36 crowd,
including 42–44 copied from production on 18 August 2026).
See `2026-08-18-behavioural-roster-and-log-schemes.md`.

Scripts:

- `analysis/behavioural/plot_ad_notice_rates.py`
- `analysis/behavioural/plot_ad_recall.py`

## Instruments

Immediate notice is the two post-condition Likert items
(`personality_brands`, `personality_sponsored`). A trial is dichotomised
as noticed if either rating is ≥ 5; the boxplots of the raw 1–7 scores
are the primary figures.

Cued recall is the end-of-session task (`ads_recall_submitted`). The
advertisement is shown again. There is no no-ad recall step. Items:

- `recall_memory`: “I feel I remember this content well.”
- `recall_trust_shift`: “After seeing this content, I felt I could trust
  the chatbot overall.”

Do not call `recall_memory` objective recognition. It is cued
self-report.

## Palette

Implicit = blue (early darker, late lighter). Explicit = orange (same
early/late split). No advertisement = gray. Used on both notice and
recall figures.

## What the ratings show

Sponsored-button notice tracks presentation: implicit median 2
(IQR 1–6), explicit median 7 (IQR 5–7), no-ad median 1 (IQR 1–2).
Brand mention is high in every ad condition and still median 5 under
no-ad (false alarm / organic mention).

Cued memory tracks the same presentation contrast: implicit median 5
(IQR 2–6), explicit median 7 (IQR 5–7). Timing is weak next to format
(implicit early/late both median 5; explicit early 7, late 6).

Trust after the cue does not follow presentation (both formats median
4). Explicit early is slightly lower (median 3). Memory and trust are
not interchangeable here.

Immediate notice and later cued memory are only modestly associated
(Spearman ρ ≈ 0.30 for both notice items, 180 ad trials). The
sponsored-button item still predicts memory better under explicit
(ρ = 0.32) than implicit (ρ = 0.14).

Within person, most participants rate explicit cued memory higher than
implicit cued memory (mean of early + late).
