# WP6 — Effects matrix figure (11 Sep 2026)

Closes `discussion.tex:174` (Walter: "visual matrix with marginals … arrow up
or down and number of arrows 1-3"). No `.tex` edited. Insertion of
`fig:effects-matrix` and the one reading paragraph belong to WP5b.

## What was produced

| Artefact | Path |
|---|---|
| Script (standalone, read-only on frozen CSVs) | `analysis/walter/combos/make_effects_matrix.py` |
| Figure (vector PDF, no rasters, 16 cm × 19.5 cm; scales to `\linewidth`) | `analysis/walter/combos/outputs/thesis/effects_matrix.pdf` |
| Thesis copy | `docs/overleaf/thesis/figures/results/effects_matrix.pdf` |
| Cell provenance (121 rows: 105 drawn + 16 companion rows) | `analysis/walter/combos/outputs/thesis/effects_matrix_cells.csv` |

Rerun: `python analysis/walter/combos/make_effects_matrix.py`. The script
cross-checks 44 cells against the printed thesis tables and prints any
disagreement.

## Encoding (as drawn in the legend)

- Triangle direction = sign of the estimate in the row's own units
  (higher trust ▲, higher manipulation ▲; association rows ▲ = positive ρ).
- Count 1 / 2 / 3 = |d_z| < .2 / .2–.5 / > .5; association rows |ρ| < .3 / .3–.6 / > .6.
- Filled CLAY orange (`#C45C26`, the unified Holm colour) = Holm p < .05;
  hollow slate = Holm p ≥ .05; "·" = not estimated in the thesis; "0" =
  estimate exactly zero.
- Columns keep the **thesis coding**: any ad − no ad · implicit − explicit ·
  early − late, then the four condition − a∅ marginals.
- Row groups with thin separators and left gutter labels: Behavioural
  (N=54) · EEG, condition aggregation (n=18) · EEG, onset-locked (n=18) ·
  Trajectories (N=54) · Association (n=18). †marks the exploratory row.

## Proposed caption and label (2 lines)

```latex
\begin{figure}[!htb]
\centering
\includegraphics[width=\linewidth]{figures/results/effects_matrix.pdf}
\caption{Every estimated effect in one grid. Triangles give direction and \(|d_z|\) band (\(|\rho|\) for associations); filled orange is Holm \(p<.05\); a dot is not estimated.}
\label{fig:effects-matrix}
\end{figure}
```

## Cell table (● Holm p < .05, ○ not; estimate, effect size, Holm p)

| Row | Any ad − no ad | Implicit − explicit | Early − late | Implicit early | Implicit late | Explicit early | Explicit late |
|---|---|---|---|---|---|---|---|
| Notice | ▲▲▲● +2.07, dz 1.01, <.001 | ▼▼▼● −1.15, dz −0.55, <.001 | ▲○ +0.26, dz 0.16, .234 | ▲▲▲● +1.60, dz 0.59, <.001 | ▲▲▲● +1.40, dz 0.52, <.001 | ▲▲▲● +2.81, dz 1.18, <.001 | ▲▲▲● +2.49, dz 0.99, <.001 |
| Perceived manipulation | ▲▲▲● +1.27, dz 0.66, <.001 | ▼▼● −0.62, dz −0.32, .022 | ▲▲● +0.58, dz 0.41, .007 | ▲▲● +1.20, dz 0.42, .006 | ▲▲● +0.72, dz 0.29, .039 | ▲▲▲● +1.92, dz 0.97, <.001 | ▲▲▲● +1.24, dz 0.53, <.001 |
| Credibility | ▼○ −0.14, dz −0.13, .673 | ▼○ −0.06, dz −0.10, .673 | ▼▼● −0.33, dz −0.39, .016 | ▼▼○ −0.35, dz −0.23, .411 | ▲○ +0.01, dz 0.00, 1.000 | ▼▼○ −0.26, dz −0.21, .411 | ▲○ +0.04, dz 0.04, 1.000 |
| Trust | ▼▼○ −0.34, dz −0.25, .153 | ▲○ +0.15, dz 0.11, .405 | ▼▼○ −0.44, dz −0.32, .063 | ▼▼○ −0.44, dz −0.24, .250 | ▼○ −0.09, dz −0.05, 1.000 | ▼▼● −0.69, dz −0.38, .031 | ▼○ −0.15, dz −0.08, 1.000 |
| Cued memory | · | ▼▼▼● −1.45, dz −0.93, <.001 | ▲○ +0.19, dz 0.10, .473 | · | · | · | · |
| Trust on re-exposure | · | ▲○ +0.12, dz 0.09, .525 | ▼▼● −0.49, dz −0.32, .047 | · | · | · | · |
| Fz θ (cond. aggr.) | ▼○ −0.04, dz −0.13, .598 | ▼▼○ −0.08, dz −0.30, .430 | ▼▼▼○ −0.20, dz −0.52, .121 | ▼▼○ −0.17, dz −0.47, .577 | ▲○ +0.02, dz 0.04, 1.000 | ▼▼○ −0.10, dz −0.21, 1.000 | ▲▲○ +0.11, dz 0.35, .921 |
| Posterior α (cond. aggr.) | ▲○ +0.09, dz 0.17, .974 | ▲○ +0.06, dz 0.11, .974 | ▼▼▼● −0.22, dz −0.63, .0496 | ▲○ +0.02, dz 0.03, 1.000 | ▲▲○ +0.22, dz 0.29, 1.000 | ▼○ −0.06, dz −0.08, 1.000 | ▲▲○ +0.18, dz 0.28, 1.000 |
| Fz θ (onset-locked) | · | · | · | ▲▲○ +0.61, dz 0.21, .791 | ▼▼○ −1.38, dz −0.48, .223 | ▲▲○ +0.74, dz 0.36, .421 | ▼○ −0.13, dz −0.05, .820 |
| Posterior α (onset-locked) | · | · | · | ▲○ +0.44, dz 0.11, 1.000 | ▼▼○ −1.11, dz −0.31, .598 | ▲○ +0.64, dz 0.15, 1.000 | ▼▼○ −1.29, dz −0.45, .284 |
| Slow-power tilt, abs. δ (expl.)† | · | · | · | ▲○ +0.97, dz 0.18, .898 | ▲○ +1.43, dz 0.18, .898 | ▲▲▲● +4.60, dz 0.88, .007 | ▲▲○ +2.13, dz 0.28, .736 |
| δ₂⁽ᵃ⁾ | ▲○ +0.046, dz 0.10, .94 (early pooled) | ▲○ +0.093, dz 0.16, .91 (implicit − explicit early) | · | ▲○ +0.093, dz 0.17, .91 | · | 0 (0.000, dz 0.00, 1.00) | · |
| Late N_shift | ▼○ −0.074, dz −0.07, 1.00 (late pooled) | · | · | · | ▼○ −0.019, dz −0.02, 1.00 | · | ▼○ −0.130, dz −0.11, 1.00 |
| Trust × posterior α (cond. aggr.) | ▲○ ρ .24, 1.00 | ▲○ ρ .29, 1.00 (sens.) | ▲○ ρ .02, 1.00 (sens.) | · | · | · | · |
| Trust × posterior α (onset-locked) | ▲▲▲● ρ .80, .0004 | ▲○ ρ .18, 1.00 (sens.) | ▲○ ρ .15, 1.00 (sens.) | · | · | · | · |

Companion rows in the CSV (not drawn; `in_figure=False`) for the tilt cell,
onset-locked explicit early − matched a∅: relative δ +0.19 (dz 0.93, Holm
.004), relative α −0.039 (dz −0.73, Holm .026), relative β −0.088 (dz −0.77,
Holm .018), global θ +1.68 (dz 0.74, Holm .023). These are the "five of six
exploratory orange cells on explicit early" of `sec:results-eeg`.

## Sources per block (all frozen; nothing rebuilt)

| Block | File | Columns |
|---|---|---|
| Behavioural planned | `analysis/walter/behavioural/outputs/confirmatory/confirmatory_planned_D.csv` | `mean, dz, p_holm` |
| Behavioural marginals | `analysis/walter/behavioural/outputs/confirmatory/posthoc_vs_control.csv` | `mean, dz, p_holm` |
| EEG cond. aggr. planned | `analysis/eeg/statistics/outputs/eeg_condition_contrasts.csv` (`contrast_tier=primary`) | `mean_difference, cohen_dz, p_t_holm` |
| EEG cond. aggr. marginals | `analysis/eeg/statistics/outputs/posthoc/eeg_posthoc_pairwise_dataset_a.csv` (`comparison_type=ad_vs_no_ad`) | same |
| EEG onset-locked cells | `analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv` (`contrast_tier=primary`) | same |
| Trajectories | `analysis/trajectories/outputs/stages_2_4/tables/t1_crossing_hard.csv`, `t4_negative_control.csv` | `mean, dz, p_holm` |
| Associations | `analysis/walter/combos/outputs/thesis/declared_families.csv` (`beh_eeg` declared; `beh_eeg_sens` for the two other contrasts) | `rho, p_holm` |

## Cells that were inferred, decided, or disagree (read this, WP5b / WP11)

**Decisions (not in any thesis table as a single number):**

1. **Onset-locked planned columns are "·".** The CSV carries
   `any_ad_vs_matched_no_ad`, `inline_vs_block`, `early_vs_late` as
   `secondary_uncorrected` (no Holm p) and the thesis reports Dataset B as
   "four cells" only. For the record: any ad − matched a∅ Fz θ −0.04 dB
   (dz −.03), posterior α −0.33 dB (dz −.12); early − late posterior α
   +1.23 dB (dz .59, raw p .023). If WP4 ever puts the secondary rows into
   Results, flip these cells on (`in_figure`) rather than redraw by hand.
2. **Condition-aggregation marginals come from the post hoc pairwise sweep**
   (Holm within measure across ten pairs, `sec:app-eeg-posthoc`). All eight
   are hollow. They are flagged `exploratory=True` in the CSV. If Walter
   prefers strictly confirmatory EEG, replace these eight with "·" (one flag
   in the script).
3. **Slow-power tilt row is drawn from absolute δ** (the measure the
   Discussion lock names first); relative δ, α, β and global θ are companion
   rows in the CSV and named in the figure footnote (Holm .026, .018).
4. **δ₂⁽ᵃ⁾ explicit early − a∅ is exactly 0.000** (`t1_crossing_hard.csv`);
   sign undefined, drawn as "0".
5. **Trajectory "any ad − no ad" cells are pooled-timing contrasts** (early
   pooled for δ₂, late pooled for N_shift), as declared in
   `tab:traj-crossing` / `tab:traj-late`; the footnote says so.
6. **Association implicit − explicit / early − late cells** are the
   `beh_eeg_sens` pairs (`tab:results-checks`: 24 tests, 0 Holm), drawn
   hollow and flagged `exploratory=True`. Remove if WP5b wants only the
   declared six.
7. **Posterior α early − late (cond. aggr.) Holm p = .0496** is drawn filled.
   It is the borderline cell; the thesis prints .0496 everywhere.

**CSV vs thesis-table disagreements (all rounding; none changes a triangle or a fill):**

- `tab:beh-localisation` credibility implicit late: d_z printed **+0.01**,
  CSV 0.00498 → rounds to **0.00**. Cosmetic.
- `tab:beh-planned` credibility early − late: Holm printed **.017**, CSV
  .016497 → **.016** at three decimals. Cosmetic.
- `tab:beh-localisation` manipulation implicit late: Holm printed **.040**,
  CSV .03946 → **.039**. Cosmetic.
- All other 41 checked cells agree at printed precision (estimate, d_z,
  Holm p), including every bold row of `tab:beh-planned`, the whole
  localisation grid, `tab:traj-crossing`, `tab:traj-late`, ρ = .24 / .80.

**Prose that the matrix contradicts (for WP5b, `sec:disc-implications`
and Walter's own gloss in the 174 comment):**

- "Implicit decreases notice and recall" is true **relative to explicit**
  only. Against a∅, implicit raises notice at both timings (▲▲▲● +1.60,
  +1.40) and raises manipulation at both timings (▲▲● +1.20, +0.72). The
  matrix row reads: implicit is noticed less than explicit, but noticed.
- "Late increases credibility" is not estimated as such. Late − a∅
  credibility is +0.01 / +0.04, hollow; only early − late (−0.33, Holm
  .017) is significant. The direction in words is "early lowers
  credibility relative to late", not "late raises it".
- Cued memory and trust on re-exposure have no a∅ cell; any "any ad"
  claim about memory cannot be sourced.
- Trust: the only filled trust cell is explicit early − a∅ (−0.69, Holm
  .031, post hoc). The three planned trust contrasts are hollow, matching
  8.1 and `tab:rq-answers`.

## Open questions for Walter

- Keep the eight post hoc condition-aggregation EEG marginals (hollow,
  labelled as post hoc in the footnote), or blank them to "·"?
- Keep the four sensitivity association cells, or show only the declared
  any-ad pair?
- One row for the tilt (absolute δ) is what the checklist asked for; a
  second row "relative α, β (expl.)" would show the fast-band fall visually.
  Say the word and it is one list entry in `GROUPS`.
