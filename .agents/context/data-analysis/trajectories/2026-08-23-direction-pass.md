# Direction pass (EDA + stages 2–4)

Date: 23 Aug 2026. Owner: Walter. Status: SUPERSEDED for inference
by `2026-08-23-stages-2-4.md` and `run_stages_2_4.py`. The ΔP heatmaps
here remain useful as a labelling comparison; do not quote the first-pass
GEE OR 0.99. Jensen–Shannon is retired (hard labels only). Stage 5 still blocked.
Recovery of what belongs in the paper is **not** decided; this note records
what was computed.

Script: `analysis/trajectories/run_direction_pass.py`. Report:
`analysis/trajectories/outputs/direction_pass.md`. Figures:
`analysis/trajectories/outputs/figures/direction/`.

Direction lock remains `2026-08-23-analysis-direction.md`. Numbers below
use the bare utterance as primary unless named.

## What was run

1. Full EDA for both labellings: genre shares, shift / diversity /
   entropy / persistence by condition, turn profiles, position rates.
2. Full 13×13 heatmaps: overall (both sources side by side), advertised
   vs no-ad + ΔP, and crossing 2→3 vs no-ad 2→3 + ΔP.
3. Stage 2 tests on the crossing estimand (paired mean, exact McNemar,
   Jensen-Shannon) plus destination shares among shifts.
4. Stage 3 stacked same / unrelated / aligned, conditional q, permutation
   null, split by ad type.
5. Stage 4: implicit vs explicit on the crossing estimand; late vs no-ad
   as negative control only.

## How to read the heatmaps

The useful comparison is `heatmap_overall_both.png`. Bare is a 13-state
diffuse chain with a weak diagonal (self-transition 0.12–0.28) and
guidance as an attractor. Contextual is a 3-state sticky chain
(guidance / academic / relationships; self-transition 0.72–0.93). That
is the labelling difference, not an advertisement effect.

ΔP boards (`heatmap_ad_vs_none_*`, `heatmap_crossing_*`) must not be
read cellwise on rare rows. Under the primary labels, no-ad
`writing_and_editing` as a source is **1 transition**; several crossing
rows are n=1 and therefore print as ±1.00. Live rows are guidance,
relationships, academic (and, barely, the junk classes). Contextual
crossing is only those three sources (81 / 23 / 4).

## First-pass numbers, unchanged

Crossing hard shift, early pooled vs no-ad: +0.046, Holm p = 0.94.
Implicit vs explicit on that estimand: +0.093, Holm p = 0.91.
Late N_shift vs no-ad: −0.074, Holm p = 1.00.
`delta`-tilde: 9 of 108 vs 10.5 chance, permutation p = 0.80.
Conditional q = P(aligned | shifted) = 9/89 = 0.101.
Already in the ad genre at turn 2: 25 of 108.

## Not decided

Which of these boards and tables belong in the paper or appendix. Walter
will recover after looking.