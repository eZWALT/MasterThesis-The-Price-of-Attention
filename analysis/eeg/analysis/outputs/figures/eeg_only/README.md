# EEG-only figure hub

One place to find EEG pictures. Do not hunt in `suite/` and the parent
folder. Primary science stays **4 s + median + ICA**.

Regenerate heatmaps:

```bash
python analysis/eeg/analysis/plot_eeg_only_heatmaps.py
```

## Heatmaps you asked for

`heatmaps/` — Holm *p*, ICA, all 16 features. Rows 1–2 (Fz theta,
posterior alpha) are confirmatory. Orange = Holm < 0.05. Holm is within
feature at that width, not across 2/4/8 s.

| File | What |
|---|---|
| `board_dataset_a_b_2_4_8s` | Dataset A (top) and Dataset B (bottom) at 2 / 4 / 8 s |
| `dataset_a_2s` | Dataset A only, 2 s |
| `dataset_a_4s` | Dataset A only, 4 s (primary) |
| `dataset_a_8s` | Dataset A only, 8 s |
| `dataset_b_2s` | Dataset B only, 2 s |
| `dataset_b_4s` | Dataset B only, 4 s (primary) |
| `dataset_b_8s` | Dataset B only, 8 s |

Dataset A columns: any-ad, implicit−explicit, early−late.
Dataset B columns: implicit/explicit × early/late vs matched no-ad.
Log keys remain `inline_*` / `block_*`.

## Where the other pictures live

Paper / talk (4 s):

- `../suite/figure_08_confirmatory_forests` — main
- `../suite/figure_07_condition_rainclouds` — optional main
- `../eeg_pipeline` is Overleaf; not `../figure_01_data_flow`

Appendix / robustness:

- `../suite/figure_10_epoch_grid_heatmap` — Dataset B confirmatory across 2–32 s
- `../suite/figure_10b_epoch_grid_heatmap_ica_noica` — same, ICA + no-ICA
- `../suite/figure_11_epoch_grid_traces`
- `../suite/figure_13_ica_vs_noica`
- `../figure_06_threshold_sensitivity`
- `../suite/figure_17_epoch_timeline` — what 2/4/8 s cut on a turn

Not for the paper:

- `../suite/figure_14_*` / `figure_15_*` — read vs write sanity check
- `../suite/figure_16_session_order`

Older duplicates of 08 (do not also use if 08 is in):

- `../figure_02_condition_primary_forest`
- `../figure_03_ad_primary_forest`
