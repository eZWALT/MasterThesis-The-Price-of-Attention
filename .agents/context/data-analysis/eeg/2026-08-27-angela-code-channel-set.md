# Angela code channel set (`angela_code_v0`)

Date: 27 August 2026. Sensitivity only. Not EEG 6.3. Not confirmatory.

This closes the backlog item “retry / close the Angela list”
(`../2026-08-27-backlog-and-timeline.md` item 1).

## Source

The lists are the `BAND_CHANNELS` dict in
`scripts/cognitive-mllm/eeg_preprocessing/eeg_analysis.py`
(same dict in `eeg_analysis_testing_Sebastian.py`). They are **not**
cited to a paper. Angela’s manuscript cites Zheng 2015 and Cochran
1967 for band *names*, Newson 2019 for Hz edges, and Smith 2017 for
F3–F4 FAA. It does not publish these electrode tuples.

As written:

| Band | Her list |
|---|---|
| δ | Fz, F3, F4, Cz |
| θ | Fz, FCz, Cz, F3, F4 |
| α | O1, Oz, O2, P3, Pz, P4 |
| β | C3, Cz, C4, CP3, CPz, CP4 |
| γ | O1, Oz, O2, P7, P8, PO7, PO8 |

## What this cap can actually use

Recorded 32 sites:
`acquisition_contract.md`. **FCz is not a recorded data channel.**
CP3, CPz, CP4, PO7, and PO8 are also absent.

Used lists (`channel_sets.ANGELA_CODE_BAND_CHANNELS`; JSON must match):

| Band | Used here | Dropped |
|---|---|---|
| δ | Fz, F3, F4, Cz | — |
| θ | Fz, F3, F4, Cz | FCz |
| α | O1, Oz, O2, P3, Pz, P4 | — |
| β | C3, Cz, C4 | CP3, CPz, CP4 |
| γ | O1, Oz, O2, P7, P8 | PO7, PO8 |

Missing sites were **dropped, not replaced**. Do not invent
nearest-neighbour fillers. Alpha on this list is the same six sites as
confirmatory posterior alpha.

Hz edges stay 0.5–4 / 4–8 / 8–13 / 13–30 / 30–40. Derived measures
stay `current_v1`. Cleaning stays the full montage.

## Role

`angela_code_v0` is a fifth channel-set sensitivity, next to primary
32-ch, George nine-site, Wang zones, and AES regions. Appendix only
(`sec:app-eeg-channel-sets`). Do not write it into primary Gold or
the abstract.

```bash
python analysis/eeg/preprocessing/run_channel_set_sensitivity.py \
  --channel-set-policy \
  analysis/eeg/preprocessing/gold/features/channel_set_policy_angela_code.json
python analysis/eeg/analysis/plot_channel_set_heatmaps.py
```

## 27 August rebuild

4 s · median · ICA · n=18. Validators passed. Derived Holm and
mean differences match primary to 0.0. Primary Gold not written.

Dataset A stays Holm-null (closest: global θ early−late, Holm 0.19).

Dataset B exploratory cells, vs primary’s six Holm < 0.05:

| Cell | Primary | Angela | |
|---|---|---|---|
| δ explicit-early | 0.0069 | 0.0225 | keep |
| rel. δ explicit-early | 0.0043 | 0.0062 | keep |
| θ explicit-early | 0.0229 | 0.2339 | drop |
| rel. α explicit-early | 0.0263 | 0.5395 | drop |
| rel. β explicit-early | 0.0180 | 0.0889 | drop |
| rel. γ implicit-late | 0.0374 | 0.2637 | drop |

No new Holm cell appears. Across the five boards, only δ / rel. δ
explicit-early survive every montage.

Figures: `analysis/eeg/analysis/outputs/figures/channel_sets/`
(`board_holm_dataset_a_b.png` is the five-column board).
Table: `analysis/eeg/statistics/outputs/sensitivity/channel_sets/comparison/channel_set_contrast_comparison.csv`.
