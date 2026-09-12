# WP-B report — drop in-plot legends, high-contrast palette, Holm mark

12 Sep 2026. Plotting-code only. No `.tex` edits. No Gold/ICA/stats mains. No commit.

Holm marker unchanged: orange `#C45C26`, bold `*`, forests at `xmax + 0.06·span`, boards inside the cell. No text legend for it.

Palette locked: red `#D32F2F`, blue `#1565C0`, yellow `#F9A825`, purple `#6A1B9A`. White/grey for neutrals. Sequential boards: `YlOrRd` / `YlOrRd_r`. Signed maps: `RdBu_r`.

`pdfimages -list` after copy: **0 rasters** on every row below.

## Figure table

| Figure | Generator | Legend removed? (what it said) | Caption fragment | Colours (from → to) | 0 rasters | Copied |
|---|---|---|---|---|---|---|
| `beh_localisation_forest` | `make_thesis_figures.localisation_forest` | yes — "Holm p < .05" | none | navy/teal point+CI → blue `#1565C0` | yes | yes |
| `beh_holm_board` | `make_thesis_figures.holm_board` | yes — "Holm p < .05 / .05–.10 / .10–.50 / >.50" | Fill: Holm *p* (red <.05, yellow .05–.10, grey .10–.50, white >.50). | clay/peach/mist/grey → red/yellow/grey/white; orange `*` added in cell | yes | yes |
| `beh_condition_profiles` | `make_thesis_figures.condition_profiles` | none | none | navy box edge → ink; clay median → red | yes | yes |
| `beh_likert_distributions` | `make_thesis_figures.likert_distributions` | yes — "Response (1 = strongly disagree, 7 = strongly agree)" 1–7 | Stacked bars are Likert 1 (yellow) to 7 (red); 1 = strongly disagree, 7 = strongly agree. | clay–navy house cmap → `YlOrRd` | yes | yes |
| `beh_estimator_concordance` | `make_thesis_figures.estimator_concordance` | yes — "Paired t, Holm (primary)"; "Random-intercept LMM, Holm (adjusted check)"; "Wilcoxon, raw (sensitivity)" | Circles: paired *t* Holm; squares: LMM Holm; triangles: Wilcoxon raw. Dashed line: *p* = .05. | navy/teal/slate → red/blue/yellow | yes | yes |
| `beh_personality_board` | `make_thesis_figures.personality_board` | yes — same four Holm-*p* bands | Fill: Holm *p* (red <.05, yellow .05–.10, grey .10–.50, white >.50). | clay/peach/mist/grey → red/yellow/grey/white; orange `*` added in cell | yes | yes |
| `beh_item_forest` | `run_item_sensitivity.item_forest` (frozen `item_level_contrasts.csv`) | yes — "Holm p < .05" | none | navy/teal → blue | yes | yes |
| `beh_notice_percentages` | `run_notice_percentages.make_figure` | yes — "Noticed"; "Did not notice"; "Wilson 95% on noticed" | Red: noticed (sponsored-button rating ≥ 5); blue: did not; whiskers: Wilson 95% on noticed. | navy + light clay → red + blue; clay whiskers → ink | yes | yes |
| `beh_demographics_board` | `run_demographic_moderation.board` via `--plot-only` / `plot_from_frozen` | yes — same four Holm-*p* bands plus a footer on cell contents | Fill: Holm *p* (red <.05, yellow .05–.10, grey .10–.50, white >.50). Cell: spread of the mean within-person contrast across factor levels (Likert points) and Holm *p* of the joint contrast × factor Wald test. | clay/peach/mist/grey → red/yellow/grey/white; `*` kept `#C45C26` | yes | yes |
| `eeg_confirmatory_forests` | `plot_eeg_publication_suite.plot_confirmatory_forests` | yes — "Holm p < .05" | Red: Fz θ; blue: posterior α. | navy vs teal (Fz θ vs posterior α) → red vs blue | yes | yes |
| `eeg_holm_board_4s` | `plot_eeg_only_heatmaps.plot_board_4s` | none (colorbar kept as the *p* scale) | Colour is Holm *p* (`YlOrRd_r`; red low). | clay–grey pastel → `YlOrRd_r`; orange `*` added in cell | yes | yes |
| `posthoc_pairwise_thesis` | `plot_posthoc_pairwise.draw_thesis_appendix` | none | Column codes: N no ads, IE/IL implicit early/late, EE/EL explicit early/late. | clay–grey pastel → `YlOrRd_r`; orange `*` added in cell | yes | yes |
| `combos_declared_forests` | `run_thesis_families.plot_from_frozen` | yes — "Dataset A, condition aggregation"; "Dataset B, onset-locked"; "behaviour × trajectory, N = 54"; "trajectory × EEG (Dataset A), n = 18"; "Holm p < .05" | (a) Filled circles: Dataset A (condition aggregation); hollow squares: Dataset B (onset-locked). (b) Yellow circles: behaviour × trajectory (*N*=54); purple diamonds: trajectory × EEG Dataset A (*n*=18). | grey/dark-red/blue → red/blue/yellow/purple | yes | yes |
| `combos_trust_alpha` | same | yes — "Dataset B, onset-locked"; "Dataset A, condition aggregation"; "Holm p < .05" | Squares: Dataset B (onset-locked); hollow circles: Dataset A (condition aggregation). | dark-red/grey → blue (B) / red (A) | yes | yes |
| `effects_matrix` | `make_effects_matrix.draw` | yes — "Holm *p*<.05"; "Holm *p*≥.05"; "estimate below zero"; "not estimated" plus a four-line decode note | Filled orange triangles: Holm *p*<.05; hollow otherwise; direction is the sign of the estimate; 1/2/3 triangles are \|*d<sub>z</sub>*\| bands (<.2 / .2–.5 / >.5) or \|ρ\| bands (<.3 / .3–.6 / >.6); dot = not estimated; 0 = estimate exactly zero. | navy group labels → ink; Holm fill stays `#C45C26` | yes | yes |
| `s24_depth_versus_ad` | `run_stages_2_4.figure_depth_versus_ad` | yes — "Holm p < .05" | Filled markers: content genres; hollow: residual fallback classes. | navy → blue (content); slate kept for fallback | yes | yes |
| `traj_shift_by_position` | `describe_trajectories.plot_shift_by_position` | none | Red: transition that crosses the advertisement; blue: other positions. | clay/navy → red/blue | yes | yes |
| `traj_example_trajectories` | `eda_stage1.figure_examples` | none | Red box: genre changed at that turn; yellow line: advertisement. | navy change-box → red; clay ad mark → yellow | yes | yes |
| `traj_heatmap_both` | `run_direction_pass.plot_overall_both` | none (colorbar kept) | none | navy sequential → `YlOrRd` | yes | yes |
| `sample_demographics` | `sample_descriptives.draw_demographics` | yes — "Lab *n*=18"; "Crowd *n*=36" | Red: laboratory (*n*=18); blue: crowd (*n*=36). | muted teal/mauve → red/blue | yes | yes |

## Not regenerated

- `beh_confirmatory_forests` — not on the WP-B list (WP2: not in Ch 7). Shared `_forest` no longer draws a Holm legend; not re-saved.
- `s24_crossing_forest` — left as-is (WP2; not on this list).
- `beh_d_rainclouds`, `bfi10_boxplots` — sit in `figures/results/` but were not on the WP-B generator list.
- Stats mains not run: `run_thesis_families.py` main, `run_item_sensitivity.py` main, `run_stages_2_4.py` main, `eda_stage1.py` main, `plot_eeg_publication_suite.py` main, `run_demographic_moderation.py` main, `sample_descriptives.main()` (that last one writes `analysis/behavioural/`).
- Added `run_demographic_moderation.plot_from_frozen()` / `--plot-only` (reads `outputs/exploratory/demographic_moderation_lmm.csv`).
- `make_effects_matrix` still prints a pre-existing rounding note (`credibility` IL *d<sub>z</sub>* 0.005 vs table 0.01). Numbers not changed.

## Commands

```
python3 /tmp/wp_b_regen.py
```

That script only imported plot functions and called them on frozen CSVs, then copied each PDF to `docs/overleaf/thesis/figures/results/<same name>.pdf`. Entry points:

- `make_thesis_figures.{condition_profiles,localisation_forest,likert_distributions,estimator_concordance,holm_board,personality_board}`
- `run_item_sensitivity.item_forest` ← `outputs/sensitivity/item_level_contrasts.csv`
- `run_notice_percentages.make_figure` ← Gold `condition_features.csv` (sponsored item only)
- `run_demographic_moderation.plot_from_frozen`
- `plot_eeg_publication_suite.plot_confirmatory_forests` ← `eeg_condition_contrasts.csv`, `eeg_ad_response_contrasts.csv`
- `plot_eeg_only_heatmaps.plot_board_4s`
- `plot_posthoc_pairwise.draw_thesis_appendix`
- `run_thesis_families.plot_from_frozen`
- `make_effects_matrix.main` (reads frozen confirmatory CSVs; no model fit)
- `run_stages_2_4.figure_depth_versus_ad` ← `utterances.csv` + `t1_crossing_hard.csv`
- `describe_trajectories.plot_shift_by_position` ← `transitions.csv`
- `eda_stage1.figure_examples` ← `conversations.csv`
- `run_direction_pass.plot_overall_both` ← `transitions.csv`
- `sample_descriptives.draw_demographics` → `src/project/docs/sample_descriptives/sample_demographics.pdf` (did not write `analysis/behavioural/`)

Raster check:

```
THESIS=docs/overleaf/thesis/figures/results
for f in beh_condition_profiles beh_localisation_forest beh_likert_distributions \
  beh_estimator_concordance beh_holm_board beh_personality_board \
  beh_item_forest beh_notice_percentages beh_demographics_board \
  eeg_confirmatory_forests eeg_holm_board_4s posthoc_pairwise_thesis \
  combos_declared_forests combos_trust_alpha effects_matrix \
  s24_depth_versus_ad traj_shift_by_position traj_example_trajectories \
  traj_heatmap_both sample_demographics
do pdfimages -list "$THESIS/$f.pdf"; done
```

Every list was header-only (0 images).
