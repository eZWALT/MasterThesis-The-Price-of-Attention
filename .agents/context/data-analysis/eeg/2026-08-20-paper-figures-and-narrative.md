# Paper figures and EEG narrative (statistician lock)

Date: 20 August 2026
Branch note: this lock uses **golden visual-onset** 4 s numbers. The
`eeg-path-b-after-reply` sensitivity was tried and rejected
(`2026-08-20-path-b-after-reply-lock.md`). Do not overwrite golden Gold.

This file consolidates the EEG-only stop line, the 4 s / sensitivity
CIs, the figure suite, the Monday agenda, and the Goal-1 blocker into
one writing contract. Interactive cut:
`~/.cursor/projects/home-wtroi-MasterThesis-RAG-RecSys/canvases/paper-eeg-figures-narrative.canvas.tsx`

## What “2/3 covered, 1/3 blocked” means

The EEG paper package has three scientific points. Two are frozen. The
third waits on Katerina’s behavioural ETL.

| Point | Estimand | Status |
|---|---|---|
| 1. Dataset A | Person-level condition medians. Three \(D\): any-ad − no-ads, implicit − explicit, early − late. Features: Fz theta, posterior alpha. | **Locked.** Holm-null. Tight CIs. |
| 2. Dataset B | Person-level (ad post−pre) − (matched no-ad post−pre). Four cells. Same two features. Visual-onset \(t=0\), 4 s. | **Locked.** Confirmatory Holm-null. Sensitivity: mention both off-width cells or neither. |
| 3. C1 | Same three Dataset A \(D\) correlated with Goal 1 \(D\) on trust / credibility / manipulation. Lab \(n=18\). Exploratory. | **Blocked.** No frozen scoring, no join builder. |

Do not invert the study. Paper Results order is still Goal 1
(behavioural) → Goal 2 (personality) → Goal 3 (this EEG package) → C1.
EEG figures can be locked now. Behavioural figures cannot.

## Confirmatory contract (do not reopen)

- Inferential unit = **participant**, never epoch.
- Primary: **4 s · median · ICA · \(n=18\)**.
- Holm is **per feature** across the 3 (Dataset A) or 4 (Dataset B) primary
  contrasts. Not across widths, cleanings, or the 16-feature dump.
- Paper names: **implicit** / **explicit**. Log keys stay `inline_*` /
  `block_*`.
- Dataset B \(t=0\) = when the ad becomes visible, not “they noticed it”
  and not “message finished.”
- After-reply lock: dead sensitivity. Do not promote.
- Read vs write: one sentence. Not an ad result. Not a figure.
- No ERP. No epoch-as-\(n\). No entropy / PLV. No Subject 4.

Full CIs: `2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`.
Depth audit (MDE, compatibility, exploratory lock):
`2026-08-20-paper-depth-audit.md`.

## What the numbers allow

**Dataset A is a precise null.** Person-difference SD is ~0.30 dB. Any-ad
Fz theta \(M=-0.08\) dB, 95% CI \([-0.23, 0.06]\). That interval is
incompatible with a moderate *sustained* band-power shift. It is not a
TOST equivalence test (no pre-specified bound). It is not “EEG cannot
see anything.”

**Dataset B is an imprecise null.** One ad per cell. Person-difference SD
is ~2–3 dB. CIs span 2–4 dB. We cannot reject, and we also cannot rule
out effects of the size the 2 s / 8 s sensitivity cells later show.
Implicit-late Fz theta (CI upper 0.04) and explicit-late posterior
alpha (CI \([-2.70, 0.12]\), Holm 0.284) lean; do not harvest them.

**The pipeline is alive.** Writing − reading Fz theta \(M=+0.60\) dB,
95% CI \([0.22, 0.97]\), \(d_z=0.80\), Holm \(p=0.007\). Posterior
alpha does not separate those states (Holm 0.75). So the two
confirmatory features are not interchangeable positive controls.

**Sensitivity is two different stories, not a new primary.** The whole
confirmatory Dataset B × {2,4,8,16,32} s × ICA/no-ICA grid has exactly
three Holm hits: 2 s explicit-early Fz theta (ICA only) and 8 s
explicit-late posterior alpha (both cleanings). Mention both or
neither. Do not put either in the abstract.

## Recommended figure cut

PNG/PDF live in `analysis/eeg/analysis/outputs/figures/`.
Pipeline v2: `src/project/docs/eeg_pipeline/eeg_pipeline_v2.{png,pdf,svg}`.

### Paper main text

| Slot | Artefact | Why |
|---|---|---|
| Methods | `eeg_pipeline_v2` | Preprocessing. Not `figure_01_data_flow`. Header is 19 recorded · 32 ch · 500 Hz; Gold is \(n=18\). |
| Results (the money plot) | `suite/figure_08_confirmatory_forests` | Dataset A + Dataset B, 4 s, both features, 95% t CIs. Shows the precision contrast. |
| Results (optional 2nd) | `suite/figure_07_condition_rainclouds` | Person overlap. Between-person spread exceeds condition gaps. Skip if space is tight; 08 already carries the test. |

Do **not** also print `figure_02` or `figure_03` if 08 is in.

### Paper appendix (only if the sensitivity sentence is in)

| Artefact | Why |
|---|---|
| `suite/figure_10b_epoch_grid_heatmap_ica_noica` | The honest grid. Shows both off-width cells and that 4 s is grey. Prefer this over `figure_10`. |
| `suite/figure_17_epoch_timeline` | What 2 / 4 / 8 s actually cut. Methods or appendix, not Results. |
| `suite/figure_13_ica_vs_noica` | ICA is primary; no-ICA is mandatory sensitivity. |
| `figure_06_threshold_sensitivity` | 1000 / 1050 / 1500 µV. Short if space. |

If 10b is in, you do not also need `figure_11` traces in the paper.

### Thesis may add (not the paper)

`figure_09` Dataset B slopes, `figure_11` traces, `figure_12` band
profiles, `figure_14`/`figure_15` read-vs-write (Methods sanity),
`figure_16` session order, descriptive duration / order-balance plots.

### Out of both manuscripts

`figure_01_data_flow`, `figure_02`, `figure_03`, after-reply heatmap
boards, promoting 2 s or 8 s to a Results figure of their own.

## Paper sentences (EEG Results)

Primary confirmatory EEG used 4 s epochs, person-level medians, and ICA
(\(n=18\)). Condition-level and ad-locked contrasts on Fz theta and
posterior alpha were Holm-null. Dataset A intervals sit near zero (any-ad
Fz theta \(M=-0.08\) dB, 95% CI \([-0.23, 0.06]\)). Dataset B intervals
are wide because each cell is one event. The same chain distinguished
writing from reading on Fz theta (\(M=+0.60\) dB, 95% CI
\([0.22, 0.97]\), \(d_z=0.80\), Holm \(p=0.007\)); that is a pipeline
check, not an ad finding.

A pre-specified epoch-length sensitivity (2 / 8 / 16 / 32 s; 4 s
reused) left Dataset A Holm-null at every width. Two Dataset B confirmatory
cells crossed Holm only off the frozen 4 s width: (i) 2 s after
explicit-early ads, Fz theta, ICA only (\(M=+3.30\) dB, 95% CI
\([1.12, 5.49]\), Holm \(p=0.021\)); (ii) 8 s after explicit-late ads,
posterior alpha, ICA and no-ICA (ICA \(M=-1.22\) dB, 95% CI
\([-2.04, -0.41]\), Holm \(p=0.023\)). Neither cell is Holm-significant
at 4 s. If one is mentioned, mention both. Neither belongs in the
abstract.

## Captions (draft)

**Figure 8 (paper).** Confirmatory within-person EEG contrasts at the
pre-specified 4 s width, ICA, person-level medians (Dataset A) or
post−pre versus matched no-ad (Dataset B). Navy = Fz theta; teal =
posterior alpha. Bars are 95% paired-\(t\) intervals. Holm is within
feature. \(n=18\). No interval excludes zero.

**Figure 7 (optional).** Dataset A condition medians by participant for
the two confirmatory features. Each point is one person. Between-person
spread exceeds the condition gaps that Figure 8 tests.

**Figure 10b (appendix).** Dataset B confirmatory Holm \(p\) across epoch
widths and cleaning branches. Orange = Holm \(<0.05\) within feature at
that width, not across the grid. Navy boxes mark 4 s (primary) and 8 s.

**Figure 17 (appendix / Methods).** Dataset B lock is visual ad onset.
The 2 / 4 / 8 s post windows do not reach the next user message or the
conclusion screen.

**Pipeline v2 (Methods).** Laboratory preprocessing. Recorded set is 19;
Subject 4 is out of Gold (\(n=18\)). Silver applies ICA; Gold measures
4 s epochs and 16 spectral features. Paths A and B are parallel.

## Do not claim

- Ads have no EEG effect (Dataset B is underpowered; sensitivity cells exist).
- Implicit is subliminal / covert / Heineking.
- EEG measures trust, UX, or persuasion.
- 2 s or 8 s is the analysis because a cell crossed 0.05.
- After-reply is the primary lock.
- Read/write is an advertising result.
- Epochs are \(n\).
- C1 numbers before Goal 1 is frozen.

## Related

- Numbers: `2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`
- Stop line: `2026-08-19-eeg-only-analyses-complete.md`
- Tickets / C1: `2026-08-19-eeg-analysis-menu-and-tickets.md`
- Onset: `2026-08-20-what-path-b-onset-is.md`
- Pipeline figure: `2026-08-20-eeg-pipeline-figure-v2.md`
- Names: `../2026-08-20-implicit-explicit-names.md`
- Monday ask: `../../writing/2026-08-20-monday-katerina-sebastian-agenda.md`
- Priority: `../2026-08-18-analysis-priority-order.md`
