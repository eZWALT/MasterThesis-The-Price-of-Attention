# 7 September (evening): Ch 7.2 / 8.1 behavioural — what is ready, one decision

> **Superseded 8 September.** Applied and pushed (thesis `15cf438`); the
> estimator decision went to option 2 (paired \(t\) primary) and the
> family to 16 tests. Read `2026-09-08-behavioural-ch7-ch8-applied.md`.

Not applied to Overleaf. Nothing pushed. Personality / demographic
moderation (`sec:disc-personality`, `tab:analysis-families` row 2)
stays unestimated and is left for later. Free text is discarded.

## Inventory against the current LaTeX

`results.tex` §7.2 (`sec:results-behaviour`) is a stub with two
subsections (`-composites`, `-notice`) and a comment naming the
estimator "linear mixed model, participant random intercept".
`discussion.tex` §8.1 has two WIP paragraphs (Notice; Presentation,
timing, and \(a^{\emptyset}\)). `tab:results-summary` and
`tab:results-checks` need the behavioural rows filled.

Everything §7.2 needs exists, frozen, under
`analysis/walter/behavioural/outputs/`:

| Thesis object | Source | Status |
|---|---|---|
| Fig `beh_condition_profiles` (descriptive, 4 panels, both arms) | `figures/thesis/` | built |
| Fig `beh_confirmatory_forests` (12 + 4 planned cells) | `figures/thesis/` | built |
| Fig `beh_localisation_forest` (each ad − no ads, post hoc) | `figures/thesis/` | built |
| Fig `beh_likert_distributions` (8 items × 5 conditions) — appendix | `figures/thesis/` | built |
| Fig `beh_estimator_concordance` (t / LMM / Wilcoxon) — appendix | `figures/thesis/` | built |
| `tab:beh-planned` (16 rows: \(\overline D\), CI, \(d_z\), Holm, Wilcoxon, LMM Holm) | `figures/thesis/tab_beh_planned.tex` | built |
| `tab:beh-localisation` (16 rows) | `figures/thesis/tab_beh_localisation.tex` | built |
| `tab:beh-descriptives` (M (SD) × condition, 8 + 2 outcomes) | `figures/thesis/tab_beh_descriptives.tex` | built |
| Figure environments + captions | `figures/thesis/fig_beh_environments.tex` | built |
| Assumptions (Shapiro / QQ / bootstrap / engines) — appendix | `outputs/assumptions/` | built |
| Process variables (36 planned tests, 0 raw hits) — one sentence | `outputs/eda/process_planned_D_forest.png`, `process_by_condition.csv` | built |

Rebuild: `python analysis/walter/behavioural/figures/make_thesis_figures.py`
(reads `gold/`, `confirmatory/confirmatory_planned_D.csv`,
`confirmatory/lmm_declared.csv`, `confirmatory/posthoc_vs_control.csv`).
Style = `analysis/eeg/analysis/plot_eeg_publication_suite.py` (NAVY dots,
TEAL bars, CLAY asterisk = Holm < .05). PDFs must be copied to
`docs/overleaf/thesis/figures/results/` when the text is applied.

## The one decision: which estimator is primary in the table

`tab:analysis-families` declares **linear mixed model on \(Y_{ic}\),
participant random intercept** for the behavioural battery, while the
Methods prose (`eq:person-contrast`) and the Results intro ("Holm \(p\)
always means the Holm-adjusted paired \(t\)") build everything on the
paired \(t\) on \(D_i\). Both were run (`stats/run_lmm_declared.py`,
`confirmatory/lmm_declared.csv`, `planned_t_vs_lmm.csv`):

- Point estimates are **identical** (balanced complete data).
- Holm verdicts agree in 15/16 cells.
- The exception is **trust early − late**: \(\overline D=-0.44\)
  \([-0.81,-0.08]\), LMM Holm .048, paired \(t\) Holm .063, Wilcoxon
  raw .026. (Also the one engine-sensitive cell in the assumption
  check.) Under the declared LMM, 7/12 survey cells survive; under the
  paired \(t\), 6/12.

Options, either is defensible if stated once in Methods:

1. **Keep the table row as declared (LMM primary).** Report the LMM Holm
   in the main column, paired \(t\) + Wilcoxon as the shared-framework
   sensitivity. Trust early − late is then a Holm survivor. Results
   intro sentence about Holm needs a clause for §7.2.
2. **Amend the row to paired \(t\) on \(D_i\) with Wilcoxon sensitivity,
   LMM as covariate-adjusted check** (mirrors the trajectories GEE row
   and the EEG rows). Trust early − late is then reported as
   \(t\) Holm .063 with the LMM .048 and Wilcoxon .026 beside it. The
   built table and forest are laid out for this option (dagger on the
   LMM-only cell).

Walter to choose. Do not pick by which reads better for trust; the
argument is consistency with `eq:person-contrast` (option 2) versus
fidelity to the declared row (option 1). Whichever is chosen, the
other column stays in `tab:beh-planned`.

## Results 7.2 sentences (numbers only)

Follow `results-figure-first.mdc`: claim, artefact, one cell.

- Composites: `fig:beh-profiles`, then `fig:beh-forests` +
  `tab:beh-planned`. Sentences: perceived manipulation and notice move
  with any ad (\(+1.27\), \(+2.07\) points; \(d_z\) 0.66, 1.01);
  explicit raises both more than implicit (\(-0.62\), \(-1.15\) for
  implicit − explicit); early raises manipulation (\(+0.58\)) and lowers
  credibility (\(-0.33\)); trust is Holm-null on the planned \(t\) with
  the early − late cell engine-sensitive (name the three \(p\)).
- Localisation (post hoc): `fig:beh-localisation` /
  `tab:beh-localisation`. Notice and manipulation survive in all four
  conditions; explicit early is the largest (\(d_z\) 1.18, 0.97); trust
  moves only under explicit early (\(-0.69\) \([-1.17,-0.20]\), Holm
  .031); credibility in none.
- Cued recall: explicit is remembered better (\(-1.45\) for implicit −
  explicit, \(d_z=-0.93\)); early advertisements shift trust on
  re-exposure downward relative to late (\(-0.49\), Holm .047).
- Process: one sentence, 36 planned tests, 0 below raw .05, max
  \(|d_z|=0.24\). Clicks: none observed (already in Methods).
- Fill `tab:results-summary` rows: behavioural battery 16 tests,
  8 Holm (or 9 under option 1); personality "not estimated"; free text
  "not analysed". `tab:results-checks`: localisation 16 / 9 Holm;
  assumptions (bootstrap CI ratio 0.97–1.01; 14/16 engines agree);
  exploratory sweep 1,755 tests; process 36 / 0.

## Discussion 8.1 claims (first sentence of each paragraph)

Interpret only what §7.2 estimates. No design implications from
unestimated rows; no "depends on how and when".

- **Notice.** Participants noticed the advertisements, and noticed the
  explicit banner more; brand mention alone is not detection (Methods
  already says so), so notice is a manipulation check that passed, not
  a finding about attention.
- **Perceived manipulation is the cost the battery detects.** It rises
  with any ad, more for explicit than implicit, more for early than
  late; the implicit − explicit and early − late cells are where format
  and timing separate.
- **Credibility and trust barely move.** Credibility is a within-person
  third of a point for early vs late; trust is a marginal any-ad drop
  concentrated in explicit early (post hoc) and one engine-sensitive
  early − late cell. Say the estimator sensitivity, do not say "approached
  significance".
- **Timing vs format.** Format drives notice and memory (explicit is
  seen and remembered); timing drives felt pressure (early raises
  manipulation, lowers credibility, and in the post hoc grid carries
  the trust drop). Keep to the estimated contrasts.
- **Memory without trust cost on re-exposure.** Explicit is remembered
  better with no implicit − explicit difference in trust shift; early
  vs late shifts trust down on re-exposure.
- **Limits proper to this family.** Single-item trust; Likert ceilings
  on credibility (mean 6); no clicks; both arms pooled with arm profiles
  parallel in `fig:beh-profiles`; composites planned but Cronbach
  \(\alpha\) belongs in Methods/appendix if quoted.

`sec:disc-personality` stays WIP.
