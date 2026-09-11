# Behavioural Gold (Walter)

```bash
python analysis/walter/behavioural/build_gold.py
python analysis/walter/behavioural/run_eda.py
```

Notebooks:

- `Behavioural_EDA.ipynb` — descriptives, interactions, correlations
- `01_behavioural_confirmatory.ipynb` — planned freeze (`stats/run_confirmatory.py`,
  `outputs/confirmatory/`). Results 7.2 is written from this. §2b is the
  localisation stream (`posthoc_vs_control.csv`, each ad condition − no ad,
  Holm across 4; post-hoc).
- `02_behavioural_sweep.ipynb` — exploratory search over every outcome ×
  planned \(D\) / Friedman / 10 pairwise / BFI (`stats/run_sweep.py`,
  `outputs/exploratory/`). Three corrections side by side. Quote the
  test count with anything you take from it.
- `stats/run_ordinal.py` → `outputs/ordinal/`: ordinal GEE (items) and
  random-intercept LMM (composites), adjusted for arm / position / task;
  `primary_four_engines.csv` is paired \(t\) vs Wilcoxon vs GEE vs LMM.
  Shown in notebook 01 §5.
- `stats/run_bayes_ordinal.py` → `outputs/ordinal/bayes_ordinal_random_intercept.csv`:
  subject-specific ordered logit (PyMC, random intercept per person)
  for trust and the `behaviour_pushing` positive control. Shown in
  notebook 01 §5b. Rebuilds in ~15 s.
- `stats/trust_deepdive.py` → `outputs/exploratory/trust/`.
- `stats/run_lmm_declared.py` → `outputs/confirmatory/lmm_declared.csv`,
  `planned_t_vs_lmm.csv`: the estimator `tab:analysis-families` declares
  (bare random-intercept LMM, Wald planned contrasts, Holm within
  composite). Same estimates as the paired \(t\); 15/16 verdicts agree.
- `stats/run_personality_declared.py` → `outputs/confirmatory/personality_lmm.csv`:
  Goal 2 as Methods declares it (trait \(\times\) the three planned
  contrast codes, demographics as covariates, Holm-15 within composite).
  0/60 Holm. OLS check and a demo-factor screen sit beside it.
- `figures/make_thesis_figures.py` → `outputs/figures/thesis/`: PNG + PDF
  in the EEG-suite style (profiles, confirmatory forests, localisation,
  Likert stacks, estimator concordance) and `.tex` tables + figure
  environments for Results 7.2.
- `stats/run_omnibus_pairwise.py` → `outputs/confirmatory/omnibus_friedman.csv`,
  `omnibus_pairwise.csv`, `cronbach_alpha.csv`: Katerina's design on Gold
  (\(N=54\), correct roster) — Friedman over five conditions + ten pairs,
  paired \(t\) and Wilcoxon, Holm-10 and BH-10 within outcome, eight
  composites; plus Cronbach α (items reversed once) with arm splits.
  Post hoc; thesis Appendix F (`tab:beh-friedman`, `tab:beh-pairwise`,
  `tab:beh-alpha`).
- `stats/run_item_sensitivity.py` → `outputs/sensitivity/`: item
  diagnostics (raw vs reversed inter-item ρ, item–rest ρ, α-if-deleted),
  leave-one-item-out planned contrasts for the five 3-item composites,
  item-level planned contrasts, `beh_item_forest`, and the two appendix
  tables `tab_beh_item_diag` / `tab_beh_item_loo`. Sensitivity only; the
  pre-specified composites stay primary.
- `stats/run_assumptions.py` → `outputs/assumptions/`: Shapiro / skew /
  kurtosis / QQ on every planned \(D_i\); paired \(t\) vs Wilcoxon vs sign
  vs bootstrap CI on the same cells; Katerina's 10-pair design on Gold with
  both statistics (`pairwise_t_vs_wilcoxon.csv`). Notebook 01 §2c.
- `stats/run_giant_corr.py` → `outputs/eda/giant_corr_*` (person-mean
  Spearman matrices, N = 54 / lab n = 18 with EEG / any-ad \(D_i\)) and
  `outputs/eda/process_by_condition.csv`. Shown at the end of
  `Behavioural_EDA.ipynb`.

Figures come from `../viz.py`; stats from `../statkit.py`.

Combos are in `../combos/`.

**Three grains:** message (2,160) → chat (270) → person (54).
Condition vs ad, and the contrast table, are views. Catalog:
`.agents/context/data-analysis/2026-09-07-gold-catalog-and-lineage.md`.
Map: `src/project/docs/behavioural_pipeline/behavioural_grains.png`.

## Gold (`outputs/gold/`)

| Grain | View | File | Rows |
|---|---|---|---|
| Message | turns | `messages.csv` | 2,160 |
| Chat | ratings (5 cond.) | `condition_features.csv` (+ `conclusions.csv`) | 270 |
| Chat | recall (4 ads) | `advertisement_features.csv` | 216 |
| Person | BFI + demo | `person_features.csv` (+ `id_map.csv`) | 54 |
| Person | contrasts | `contrast_scores.csv` | 54 |
| Join | joined chat | `combo_threeway.csv` | 270 |
| Join | joined chat, lab | `combo_threeway_lab.csv` | 90 |
| Join | joined contrasts | `combo_threeway_D.csv` | 54 |
| Join | joined contrasts, lab | `combo_threeway_lab_D.csv` | 18 |
| Older names | `combo_condition_*.csv` | copies of the join tables |

Composites are the planned formulas. `manipulation` sits next to
`behaviour_pushing` and `behaviour_manipulate`. `notice` sits next to
`notice_brands` and `notice_sponsored`. Every raw `llm_*` item is kept.

`n_ad_clicked` is 0 in this cohort. `demo_age` is empty in the JSONL.

## EDA (`outputs/eda/`)

Person is the unit. Holm is the Holm-adjusted paired \(t\) within
outcome. Wilcoxon \(p\) is raw. Combo Spearman is association, lab
\(n=18\), not mediation.
