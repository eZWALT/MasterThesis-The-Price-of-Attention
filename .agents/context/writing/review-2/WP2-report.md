# WP2 report — Figures: vector PDF + unified Holm asterisk + PNG audit

11 Sep 2026. Plotting-code only. No Results/Discussion prose. No Gold/ICA/preprocessing rebuild. No commit.

Holm marker locked to `beh_localisation_forest`: clay `#C45C26`, bold `*` at panel `xmax + 0.06 × span`, legend **"Holm p < .05"**. Only Holm \(p<.05\) (paired \(t\) Holm / `p_t_holm` / `sig_holm` / `p_holm_16` on the trust×16 panel). Wilcoxon never marked.

`pdfimages -list` (conda-forge poppler) after regen: **0 rasters** on every `figures/results/*.pdf`. Heatmaps that used `imshow` (boards, posthoc, traj matrix) were switched to vector `pcolormesh`; colorbars that still embedded a strip were replaced by a `pcolormesh` strip or a discrete legend.

## Analysis figures

| Figure (thesis `figures/results/`) | Generator | Vector OK | Holm unified | Copied |
|---|---|---|---|---|
| `beh_localisation_forest.pdf` | `analysis/walter/behavioural/figures/make_thesis_figures.py` → `localisation_forest` | yes | yes | yes |
| `beh_item_forest.pdf` | `analysis/walter/behavioural/stats/run_item_sensitivity.py` → `item_forest` (from frozen `item_level_contrasts.csv`) | yes | yes (was point-recolor; now `*`) | yes |
| `beh_holm_board.pdf` | `make_thesis_figures.py` → `holm_board` | yes (`pcolormesh`) | n.a. (board) | yes |
| `beh_condition_profiles.pdf` | `make_thesis_figures.py` → `condition_profiles` | yes | n.a. | yes |
| `beh_likert_distributions.pdf` | `make_thesis_figures.py` | yes | n.a. | yes |
| `beh_estimator_concordance.pdf` | `make_thesis_figures.py` | yes | n.a. | yes |
| `beh_personality_board.pdf` | `make_thesis_figures.py` → `personality_board` | yes (`pcolormesh`) | n.a. (board) | yes |
| `beh_confirmatory_forests.pdf` | `make_thesis_figures.py` (not included in Ch 7) | yes | yes | yes |
| `eeg_confirmatory_forests.pdf` | `analysis/eeg/analysis/plot_eeg_publication_suite.py` → `plot_confirmatory_forests` (`figure_08_…`) | yes | yes | yes |
| `eeg_holm_board_4s.pdf` | `plot_eeg_only_heatmaps.py` → `plot_board_4s` (`board_dataset_a_b_4s`) | yes | n.a. (board) | yes |
| `posthoc_pairwise_thesis.pdf` | `plot_posthoc_pairwise.py` → `draw_thesis_appendix` | yes | n.a. (board) | yes |
| `combos_declared_forests.pdf` | `analysis/walter/combos/run_thesis_families.py` → `plot_from_frozen` | yes | yes | yes |
| `combos_trust_alpha.pdf` | same; Holm on panel (b) only, `p_holm_16 < .05` | yes | yes | yes |
| `s24_depth_versus_ad.pdf` | `analysis/trajectories/run_stages_2_4.py` → `figure_depth_versus_ad` only | yes | yes | yes |
| `traj_shift_by_position.pdf` | `describe_trajectories.py` → `plot_shift_by_position` (`shift_by_position`) | yes | n.a. | yes |
| `traj_example_trajectories.pdf` | `eda_stage1.py` → `figure_examples` (`eda_example_trajectories`) | yes | n.a. | yes |
| `traj_heatmap_both.pdf` | `run_direction_pass.py` → `plot_overall_both` (`heatmap_overall_both`) | yes | n.a. | yes |
| `sample_demographics.pdf` | `src/project/docs/sample_descriptives/sample_descriptives.py` → `draw_demographics` only (did **not** write `analysis/behavioural/`) | yes | n.a. | yes |
| `s24_crossing_forest.pdf` | already on disk; 0 rasters | yes | no (not in WP2 Holm list) | no (unchanged) |

Holm cells marked (unchanged numbers): localisation from `posthoc_vs_control.csv`; item forest 17 Holm hits in `item_level_contrasts.csv`; EEG Dataset A posterior \(\alpha\) early−late (`p_t_holm` = .0496); combos trust × posterior \(\alpha\) Dataset B (`sig_holm` / `p_holm_16`); depth figure Holm within the turn-4−turn-1 genre family.

## PNG audit

textwidth from Dissertate `geometry` (A4, inner=outer=1.2 in) ≈ **14.90 cm**. textheight ≈ **24.62 cm**. Effective DPI = pixel width / display width in inches.

| PNG | Pixels | `\includegraphics` | Display (cm) | Eff. DPI | Vector source | Action |
|---|---|---|---|---|---|---|
| `figures/system_architecture.png` | 2308×1510 | `0.85\textwidth` | 12.67×8.29 | 463 | `src/project/docs/architecture/arch.py` + `architecture.pdf` | exported/copied PDF; swapped in `system_design.tex` |
| `figures/preprocessing/ads_data_pipeline.png` | 2646×527 | `\textwidth`, `height=0.70\textheight`, keepaspectratio | 14.90×2.97 | 451 | `catalog_pipeline.py` + `.pdf` | copied PDF; swapped in `dataset.tex` |
| `figures/preprocessing/trajectory_preprocessing.png` | 2799×792 | `\linewidth` | 14.90×4.22 | 477 | `trajectory_pipeline.py` + `.pdf` | copied PDF; swapped in `dataset.tex` |
| `figures/preprocessing/eeg_preprocessing.png` | 2094×1988 | `\linewidth`, `height=0.62\textheight`, keepaspectratio | 14.90×14.15 | 357 | `eeg_pipeline_v2.py` / `.svg` / `.pdf` | copied PDF (0 rasters); swapped in `dataset.tex` |
| `figures/preprocessing/eeg_montage.png` | 819×763 | `0.62\linewidth` | 9.24×8.61 | **225** | placeholder only (`eeg_montage_placeholder.py` says PLACEHOLDER; not this drawing) | **left PNG**; do not swap |
| `figures/models/qwen3.6.png` | 4399×4175 | `\linewidth`, `height=0.5\textheight`, keepaspectratio | 12.97×12.31 | 861 | none | left PNG |
| `figures/ui/implicit_ad.png` | 667×636 | `height=0.30\textheight` | 7.75×7.39 | 219 | screenshot | stay PNG |
| `figures/ui/explicit_ad_2.png` | 1024×1024 | `height=0.30\textheight` | 7.39×7.39 | 352 | screenshot | stay PNG |

Diagrams-library PDFs (`system_architecture`, `ads_data_pipeline`, `trajectory_preprocessing`) still embed **icon PNGs** (28 / 12 / 16 rasters). That is the official `diagrams` export; icons were not redrawn. `eeg_preprocessing.pdf` is matplotlib and fully vector.

`models.tex` only includes UI screenshots (kept PNG) and the already-PDF workflow figures.

## Not regenerated / notes

- Full `run_thesis_families.py`, `run_item_sensitivity.py`, `run_stages_2_4.py`, `eda_stage1.py`, `plot_eeg_publication_suite.py` mains were **not** run (those recompute families or write extra artefacts). Plot functions only.
- `sample_descriptives.main()` was **not** run (it writes `analysis/behavioural/ocean_corr_outputs`).
- `s24_crossing_forest` left as-is (0 rasters; not on the Holm-unify list).
- No edits to `results.tex` or `discussion.tex`.
- Open for Walter: replace `eeg_montage.png` with a signed-off vector if one exists outside this repo (the in-repo placeholder is a different figure).
