# George vs Wang channel-set heatmaps

Date: 25 August 2026. Sensitivity only. Not EEG 6.3.

Rebuilt Dataset A/B at 4 s · median · ICA · n=18 for `literature_roi_v0`
(George nine-site) and `wang2022_v0` (Wang zone geography). One clean
per subject. Validators passed. Derived measures (Fz theta, posterior
alpha, FAA, Pope, Pope FC, Kislov) match primary Holm to 0.0.

Dataset A stays Holm-null on all 16 features in all three branches.
Wang global theta is the closest (any-ad Holm 0.15; implicit−explicit
0.13) and still above 0.05.

Dataset B exploratory cells move a little:

- George keeps explicit-early theta / delta / rel. delta / rel. beta.
  Rel. alpha explicit-early and rel. gamma implicit-late leave Holm
  0.05 (0.026→0.057 and 0.037→0.063).
- Wang drops explicit-early theta (0.023→0.75) because θ is now left
  C/P/T only. It keeps delta / rel. delta / rel. beta, keeps rel.
  gamma implicit-late, and adds rel. beta explicit-late (0.052→0.030).

`teaching_atlas_v0` added 25 August (AES region words mapped onto
this cap). Dataset A still Holm-null. Dataset B keeps explicit-early
delta / rel. delta / rel. beta and rel. gamma implicit-late;
explicit-early theta does not survive. Derived Holm still matches
primary to 0.0.

Figures: `analysis/eeg/analysis/outputs/figures/channel_sets/`
(four columns: primary, George, Wang, AES).
Table: `analysis/eeg/statistics/outputs/sensitivity/channel_sets/comparison/channel_set_contrast_comparison.csv`.
