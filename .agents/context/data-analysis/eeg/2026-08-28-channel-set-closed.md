# Channel-set closed (28 August 2026 save)

Session checkpoint. EEG sensor retry (backlog item 1) is **done**.
Primary Gold stays confirmatory. Do not reopen EEG 6.3. ICA archive
untouched. No Overleaf push in this session.

Earlier notes still stand: `2026-08-24-channel-set-policy.md`,
`2026-08-24-literature-roi-from-angela.md`,
`2026-08-25-wang-zone-sensitivity.md`,
`2026-08-25-teaching-atlas-band-regions.md`,
`2026-08-25-george-wang-heatmap-run.md`,
`2026-08-27-angela-code-channel-set.md`,
`../../writing/2026-08-24-channel-set-sensitivity-not-confirmatory.md`.

## Decision (Walter, 28 August)

**Use `current_v1` (all 32 channels) for confirmatory globals.**

Not because it keeps more Holm cells. Those orange Dataset B cells
are **exploratory global band powers**. Confirmatory EEG is still
4 s · median · ICA · Fz theta + posterior alpha (`2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`).
Those two rows do not change across the five boards and stay
Holm-null. Do **not** pick a width or electrode set by \(p\)
(`../2026-08-27-backlog-and-timeline.md`).

The other four maps are appendix robustness
(`sec:app-eeg-channel-sets`). Do not write them into primary Gold,
EEG 6.3, or the abstract.

## What was checked this session

Angela’s `BAND_CHANNELS` is **code, not a paper**. Her manuscript
cites Zheng 2015 + Cochran 1967 for band *names*, Newson 2019 for
Hz, Smith 2017 for F3–F4 FAA. Zheng Fig. 10 is lateral-temporal
SEED sites (FT7/FT8/T7/T8…), not her ROI dict. Scholar did not
return one paper with all five of her tuples.

This cap cannot record FCz, CP3, CPz, CP4, PO7, PO8. Used lists
are the intersection; missing sites were dropped, not replaced.
Lock: `2026-08-27-angela-code-channel-set.md`.

Rebuilt Dataset A/B at 4 s · median · ICA · n=18 as
`angela_code_v0` only. Validators passed. Derived Holm and
mean differences match primary to 0.0.

Five-column Holm board (primary / George / Wang / AES / Angela):
`analysis/eeg/analysis/outputs/figures/channel_sets/board_holm_dataset_a_b.png`.
Comparison table:
`analysis/eeg/statistics/outputs/sensitivity/channel_sets/comparison/channel_set_contrast_comparison.csv`.

## What the boards say (do not over-read)

- Dataset A: Holm-null on all five montages.
- Dataset B: primary has six exploratory Holm < 0.05 cells. Angela
  keeps **two** (δ and rel. δ, explicit-early). θ / rel. α / rel. β /
  rel. γ leave 0.05.
- Across all five maps, only **δ / rel. δ at explicit-early** survive.
  That is a reason not to promote those globals, not a reason to
  leave primary.

## Still open after this save

Backlog items 2–5 (post-hoc EEG restructure, Goal 1 battery,
free text, joined dataset). Thesis Ch 5–6 polish. Paper optional.
Presentation. Appendix LaTeX may still list only George/Wang;
adding Angela/AES is a later Overleaf pass, not this save.
