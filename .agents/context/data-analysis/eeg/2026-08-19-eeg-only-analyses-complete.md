# EEG-only analyses are complete

Date: 19 August 2026

This is the stop line for EEG science that does not need the behavioural
ETL. Remaining EEG work is **writing** (Results / Statistical Analysis)
and **C1** (EEG × trust/credibility/manipulation) after Goal 1 freezes.

## What now exists

Confirmatory primary (unchanged): 4 s, median, ICA, person as \(n\).

| Analysis | Result | Artefact |
|---|---|---|
| Path A, 4 s | Holm-null on all 16×3 tests | `eeg_condition_contrasts.csv`; figures 02, 07, 08, 12 |
| Path B, 4 s | Confirmatory Holm-null; 6 ICA-only exploratory hits | `eeg_ad_response_contrasts.csv`; figures 03, 08, 09 |
| Mean vs median | Still 0/48 Holm | `sensitivity/mean_of_epoch_db/` |
| Epoch grid 2–32 s | Path A null at every width; 3 confirmatory Path B cells that do not hold at 4 s | `epoch_length_grid_comparison.csv`; figures 10, 11 |
| ICA vs no-ICA | ICA primary; effects agree in sign more than size | figure 13 |
| Read vs write | **Fz theta writing−reading +0.60 dB, Holm 0.007, \(d_z=0.80\), n=18**. Posterior alpha null (Holm 0.75) | `outputs/task_state/`; figures 14, 15 |
| Session order | Last−first condition null (theta p=0.47, alpha p=0.20) | `eeg_session_order_contrasts.csv`; figure 16 |

## Positive control (the important new number)

268 eligible turn pairs (13–15 per person). Writing is the last complete
4 s before `user_message`; reading is the first complete 4 s after
`assistant_reply`. Same cleaner, same 4 s, same 16 features.

The chain **can** recover a state difference: more Fz theta while
composing than while reading. Therefore the Q1/Q2 nulls are not evidence
that the pipeline is dead. Posterior alpha does not separate the two
states here.

What that does and does not prove:
`2026-08-19-read-vs-write-what-it-proved.md`.

## Paper sentences

Primary 4 s ICA analyses show no Holm-significant Fz-theta or
posterior-alpha condition or ad-locked contrast (\(n=18\)). Mention in
one sentence that the same chain distinguished writing from reading on
Fz theta (Holm \(p=0.007\), \(d_z=0.80\)); do not build a Results
subsection around it. An 8 s labelled-block late window showed lower
posterior alpha versus matched no-ad under both ICA and no-ICA; that
cell was not Holm-significant at the pre-specified 4 s width.

## Figures (PNG + PDF)

`analysis/eeg/analysis/outputs/figures/suite/`

- 07 condition rainclouds
- 08 confirmatory forests
- 09 ad paired slopes
- 10 epoch-grid Holm heatmap
- 11 epoch-grid traces
- 12 band profiles
- 13 ICA vs no-ICA
- 14 task-state differences
- 15 task-state read/write slopes
- 16 session-order slopes

Regenerate:

```bash
python analysis/eeg/analysis/plot_eeg_publication_suite.py
python analysis/eeg/preprocessing/run_task_state_positive_control.py --skip-extract
```

## Do not build next

- Mixed models (B2): paired \(D\) already answers the planned contrasts
- ERP, epoch-as-\(n\), entropy/PLV, Subject 4
- More epoch lengths or onset games
- EEG × survey until Goal 1 scoring is frozen
- Promoting 2 s or 8 s to primary
