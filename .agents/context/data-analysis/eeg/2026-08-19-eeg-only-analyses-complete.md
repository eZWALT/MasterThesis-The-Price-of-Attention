# EEG-only analyses are complete

Date: 19 August 2026

This is the stop line for EEG science that does not need the behavioural
ETL. Remaining EEG work is **writing** (Results / Statistical Analysis)
and **C1** (EEG × trust/credibility/manipulation) after Goal 1 freezes.

## What now exists

Confirmatory primary (unchanged): 4 s, median, ICA, person as \(n\).

| Analysis | Result | Artefact |
|---|---|---|
| Dataset A, 4 s | Holm-null on all 16×3 tests | `eeg_condition_contrasts.csv`; figures 02, 07, 08, 12 |
| Dataset B, 4 s | Confirmatory Holm-null; 6 ICA-only exploratory hits | `eeg_ad_response_contrasts.csv`; figures 03, 08, 09 |
| Mean vs median | Still 0/48 Holm | `sensitivity/mean_of_epoch_db/` |
| Epoch grid 2–32 s | Dataset A null at every width; 3 confirmatory Dataset B cells that do not hold at 4 s | `epoch_length_grid_comparison.csv`; figures 10, 11 |
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
Fz theta (\(M=+0.60\) dB, 95% CI \([0.22, 0.97]\), Holm \(p=0.007\),
\(d_z=0.80\)); do not build a Results subsection around it.

Sensitivity, mention **both** or neither (full table:
`2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`): 2 s
explicit-early Fz theta, ICA only (\(M=+3.30\) dB, 95% CI
\([1.12, 5.49]\), Holm \(p=0.021\)); 8 s explicit-late posterior alpha
under ICA (\(M=-1.22\) dB, 95% CI \([-2.04, -0.41]\), Holm \(p=0.023\))
and no-ICA (Holm \(p=0.012\)). Neither cell is Holm-significant at 4 s.

A 20 August after-reply lock (finished message + 0.49 s for every
cell) stayed 4 s Holm-null and removed the 2 s explicit-early theta
hit. **Keep the golden visual-onset lock.** See
`2026-08-20-what-path-b-onset-is.md`.

Figure cut and Results sentences (20 August lock):
`2026-08-20-paper-figures-and-narrative.md`.

## Paper figures

Main text, at most two EEG figures, both at **4 s**:

- `suite/figure_08_confirmatory_forests` — Dataset A + Dataset B money plot
- `suite/figure_07_condition_rainclouds` — person-level overlap (optional
  second figure; skip if space is tight)

Do **not** also use `figure_02` / `figure_03` if 08 is in. Pipeline
figure stays the existing Overleaf flow (`eeg_pipeline`), not
`figure_01`.

Appendix only, if mentioned: 09 (Dataset B slopes), 06 (threshold), 10 or
11 (epoch grid; show both 2 s and 8 s cells, do not re-freeze either),
13 (ICA vs no-ICA).

Not for the paper: 14, 15 (sanity check), 16 (session order).

Primary epoch width for the paper is **4 s**. 2 s and 8 s are a
sensitivity footnote (both cells), not the reported analysis.

Organised EEG-only hub (heatmaps at 2 / 4 / 8 s, Dataset A and Dataset B):

`analysis/eeg/analysis/outputs/figures/eeg_only/`

```bash
python analysis/eeg/analysis/plot_eeg_only_heatmaps.py
```

Organised EEG-only hub (heatmaps at 2 / 4 / 8 s, Dataset A and Dataset B):

`analysis/eeg/analysis/outputs/figures/eeg_only/`

```bash
python analysis/eeg/analysis/plot_eeg_only_heatmaps.py
```

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
