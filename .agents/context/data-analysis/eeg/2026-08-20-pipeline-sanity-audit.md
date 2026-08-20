# Pipeline sanity audit

Date: 20 August 2026

Walter asked whether the EEG data can actually be analyzed, given the
4 s confirmatory Holm-null and unstable epoch-length hits.

## Verdict

**Analyzable**, with the caveats already on the books. No fatal
implementation bug turned up. The null is a small, precisely estimated
Path A effect plus a noisy Path B slice, not scrambled IDs or inverted
arithmetic. The 19 August read-versus-write control already showed the
same 4 s ICA chain can recover Fz theta (writing−reading +0.60 dB,
Holm 0.007, \(d_z=0.80\)).

## Recomputed facts

- Gold subjects are lab 1–3 and 5–19. Subject 4 is only in Bronze as
  `lab_subject_4_crowdfail`.
- 108 condition summaries, 90 eligible condition rows, 9,468 / 9,449
  retained 4 s epochs, 108/108 eligible ad pairs, 216/216 retained ad
  epochs. All `ica_applied=yes`. No NaNs in the 16 spectral features.
- Path A any-ad Fz theta recomputed from Gold medians: mean −0.0847,
  matches `eeg_condition_contrasts.csv` to 1e−12. Score vectors match.
- Path B `post − pre` matches epoch rows: 0 mismatches in 1,728 cells.
- Condition windows: no overlaps, no negative starts. No person has
  five identical Fz-theta medians.
- JSONL–XDF clock RMSE 15–29 µs on eligible recordings.
- ICA reports exist for all 18; visual signoff approved. Subject 19
  has zero exclusions, so that one person is identical under ICA and
  no-ICA. That is expected, not a copy-paste of the whole cohort.
- Publication runner: 20/20 gates. Metric unit tests: 20/20.

## Why the null is not a red flag

Path A any-ad Fz theta CI is [−0.23, +0.06] dB (dz −0.28). n=18 needs
about |dz| ≈ 0.66 for 80% power. A tight CI around zero is what a
working pipeline looks like when the contrast is small.

Path B SD for a comparable Fz-theta contrast is ~2.0 dB versus ~0.30 dB
on Path A. 30 of 36 implicit onsets are derived (p95 lag error 0.43 s).
That is why 2 s / 8 s Holm cells appear and disappear. Keep 4 s primary.

## Still true, still not bugs

- Read-versus-write is implemented (`outputs/task_state/`). It is a
  chain check, not an ad result. See
  `2026-08-19-read-vs-write-what-it-proved.md`.
- Baseline ~30 s, eyes uncontrolled.
- Cz is a live exported channel (robust SD ~20–40 µV), online ref
  unverified against BrainVision workspace.
- Condition order is shuffled (16 unique permutations); no_ads is not
  parked first or last.
- Do not `--overwrite` ICA models through the current fit runner:
  `fit_ica_cohort.py` cleans with the ICA-primary policy, so a refit
  would run on already-cleaned data. Reuse the archived
  `ica_candidate_v1` models. Hard stop:
  `CRITICAL-do-not-overwrite-ica-models.md`.

## Paper

Write the confirmatory 4 s null with CIs. Do not claim absence of any
neural ad effect. Do not promote the 8 s alpha cell.
