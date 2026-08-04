# EEG pipeline state and stage gates

Date: 3 August 2026

## Purpose

This entry records the current state of the laboratory EEG pipeline after XDF
organization, marker recovery, MNE conversion, initial signal QC, and window
contract development. It separates completed recording/timing work from signal
processing that still requires validation.

The processing order is:

`Ingestion / Landing → Bronze → Silver → Gold → Analysis`

In plain language:

- Ingestion collects the EEG recording and experiment log, then links the files
  to a participant.
- Bronze preserves the raw files, verifies their integrity, links each XDF to
  its log, and audits the raw marker streams without changing them.
- Silver aligns log and EEG clocks, creates one canonical event timeline,
  estimates explicitly governed missing times, converts XDF to MNE, and applies
  validated signal cleaning.
- Gold creates condition/ad windows and analysis-ready EEG feature tables.
- Analysis compares conditions and produces statistical results and figures.

All executable preprocessing code, manifests, policies, and validation tools are
centralized under `analysis/eeg/preprocessing/`. The pipeline diagram follows
the project convention at `src/project/docs/eeg_pipeline/`. Participant data
remains under `src/project/logs/xdf/`.

The code layout mirrors the stage gates:

- `ingestion/`: landing and safe organization;
- `bronze/manifests/`: immutable inventory and recording-map evidence;
- `silver/markers/`: canonical timing and reconstruction validation;
- `silver/signal/`: XDF-to-MNE conversion, cleaning, and signal QC;
- `gold/windows/`: condition and advertisement timing contracts;
- `gold/features/`: fixed-epoch spectral features and validation evidence.

Raw marker-stream auditing is shown in Bronze because it describes source
evidence. Event matching, canonicalization, and recovery remain in Silver
because they create derived data and must never alter Bronze.

Analysis is outside the data lake. `cognitive-mllm` remains a reference for
reusable metric formulas; the study-specific ingestion boundary is the native
XDF-to-MNE implementation in this repository.

## Cohort decision

- There are 19 current XDF recordings.
- Subject 4 ran the crowd protocol and has no laboratory baseline. Its raw file
  remains in Bronze, but it is excluded from the laboratory EEG cohort.
- Subjects 1–3 and 5–19 form the 18-recording candidate laboratory cohort.
- All 18 have usable recording identity, JSONL/XDF synchronization, canonical
  analysis events, one baseline, and five condition windows.
- `eeg_recording_manifest.csv` is an annotation-free generated summary.
  Reproducible evidence and explicit pipeline rules govern the mapping and
  protocol decision.

This means recording identity and marker timing are resolved for the 18
laboratory recordings. It does not guarantee that every participant will pass
final cleaned-epoch signal criteria.

## Ingestion / Landing

### Implemented

- Incoming XDF discovery and safe organization.
- Atomic movement into immutable Bronze folders without modifying XDF content.
- SHA-256 hashing by default.
- Retention of 19 current recordings and two superseded `_old1` files.

### Stage status

Operationally complete for the current cohort. Explicit current/superseded
labels in the inventory would improve presentation but are not an analysis
blocker because the current-recording and evidence manifests already make the
distinction.

## Bronze

### Implemented

- Byte-preserved XDF recordings.
- Cryptographic inventory and stream evidence.
- Recording-to-log matching independent of folder names.
- Corrected subject 1 and subject 2 recordings.
- Corrected subject 11/12 payload swap.
- Explicit subject 4 wrong-protocol classification.
- Preservation of superseded recordings without using them downstream.

### Stage status

Complete for the current cohort. Bronze files must not be edited or replaced.
Subject 4 is retained only for provenance and possible non-primary sensitivity
work.

## Silver

### Implemented

- Duplicate and extra-marker audit.
- Canonical marker timelines with provenance.
- Participant-specific affine JSONL-to-XDF synchronization.
- Leakage-resistant leave-one-marker-out validation.
- Subject 19 `experiment_end` retained as metadata-only outside the EEG span.
- XDF-to-MNE conversion for all 19 current recordings.
- Microvolt-to-volt scaling and actual-sample marker placement.
- Complete `standard_1020` montage for all 32 recorded channels.
- Condition-blind signal QC using twelve distributed 30-second windows per
  recording.
- Deterministic cleaning: 50 Hz notch, 0.5–40 Hz band-pass, average
  reference, bad-channel marking, and spherical-spline interpolation.
- Condition-blind evidence interpolates subject 8 `F10`. Full-window evidence
  additionally interpolates subject 1 `P4`, subject 9 `P4`, and subject 10
  `C4`.
- Primary `frozen_v3` gross-artifact rule: reject above 1,050 µV
  peak-to-peak or for a near-flat channel; require at least 80% and five
  retained epochs per window. Preserve 1,000 µV `frozen_v1` and 1,500 µV
  `frozen_v2` as stricter and permissive sensitivity policies.
- Visual validation pack for representative filtering and all four repaired
  channels. Objective notch, rereference, amplitude, and spatial-correlation
  checks pass.
- ICA disabled for the first feature version. The laboratory now requests a
  99%-PCA-variance ICA branch using `Fp1/Fp2` as ocular proxies, with explicit
  visual component validation and no-ICA retained as sensitivity.

### Known signal findings

- No near-flat or flatline channels were found.
- No recording is currently automatically excluded by signal QC.
- Four localized channel failures are interpolated; no participant is excluded
  by signal quality.
- Low `Fp1/Fp2` correlation is treated as expected ocular activity and retained
  for ocular-component assessment.
- Strong cohort-wide 50 Hz contamination requires notch filtering but is not a
  bad-channel criterion.

### Mandatory work remaining

- Obtain human signoff on the generated filtering and interpolation figures.
- Human-review the implemented ICA component packs, freeze or revise candidate
  removals, and inspect the generated comparison of all primary conclusions
  against the current no-ICA branch.
- Change `cleaning_policy.json` from `requires_visual_validation` to `frozen`.

Laboratory feedback identifies `Cz` as the online reference and `Fpz` as
ground. Average rereferencing remains the offline policy. `Cz` is also exported
as a dynamic XDF channel, so the acquisition workspace remains useful for
verifying amplifier/export handling but is no longer a blocker.

## Gold

### Implemented

- Baseline and sustained condition-window manifests.
- Five condition windows for every recording.
- Subject 4 windows explicitly marked ineligible.
- Advertisement visibility table with observed and derived provenance.
- 72 eligible laboratory ad events.
- Leave-one-out p95 visual-onset error of 0.226 seconds for missing explicit
  block events and 0.433 seconds for missing inline events.
- Native 4-second epoch feature extraction using Welch spectral estimates.
- Delta, theta, alpha, beta, and gamma absolute and relative power.
- Regional Fz theta and posterior alpha over `O1/Oz/O2/P3/Pz/P4`.
- Standard log FAA, `ln(alpha F4) - ln(alpha F3)`.
- Three exploratory engagement measures: global and frontocentral
  `beta / (alpha + theta)`, plus the Kislov central 16–24 Hz beta / 8–12 Hz
  alpha advertising ratio.
- Participant-window medians, IQRs, and within-participant baseline
  differences.
- Cohort validation with 18 participants, 108 windows, and 9,468 complete
  epochs.
- Frozen primary condition policy retains 9,438 epochs (99.68%); every one of
  108 windows passes retention, with a minimum window retention of 85.7%.
- No duplicate keys, non-finite spectral values, or ineligible condition cells.
- Frozen four-second ad windows around validated visual onset and matched no-ad
  `assistant_reply` events at turns 2 and 4.
- Ad response dataset with 216 pre/post epochs and 108 pairs: 72 advertisement
  exposures and 36 matched no-ad replies.
- All 216 ad epochs and 108 response pairs are retained; all ad and no-ad
  conditions retain 18 participants.
- Maximum combined ad-onset timing uncertainty is 0.433 seconds.

These uncertainties support multi-second spectral windows, not ERP claims.

The recorded baseline is used as the primary operational pre-task comparison,
as requested, but its eye state was not controlled and was only recalled as
mostly eyes open. Every baseline row is labelled
`uncontrolled_mostly_open`. Confirmatory analyses must include a sensitivity
model that excludes baseline-derived contrasts.

The epoch table preserves all complete epochs and marks each as retained or
rejected. Condition summaries use retained epochs only. Full-window evidence
identified localized failures at subject 1 `P4`, subject 9 `P4`, and subject 10
`C4`; interpolation reduced the condition p95 peak-to-peak amplitude to 428 µV
before the frozen 1,050 µV primary gross-artifact rule was applied.

### Mandatory work remaining

- Treat all three engagement measures as exploratory unless an exact formula,
  channel set, and band definition are preregistered.
- Report the complete 1,000 µV `frozen_v1` and 1,500 µV `frozen_v2`
  sensitivities beside the selected 1,050 µV `frozen_v3` primary analysis.
- Preserve the 0.433-second inline-onset uncertainty in all interpretation.

Gold now contains analysis-ready condition and ad response datasets.
Publication readiness still requires human signoff on filtering/interpolation
and the prescribed baseline/no-ICA sensitivity analyses.

## Analysis outside Gold

The condition and advertisement tables now support:

- fit baseline, no-ad, format, timing, and pre/post-ad EEG contrasts;
- join EEG summaries to behavioural and personality tables;
- run sensitivity analyses based on retained signal quality;
- produce publication figures, model summaries, and multimodal ablations.

## Issue disposition

- Subject 4: not fixable as a laboratory EEG participant because the wrong
  protocol was run; exclude from primary laboratory inference.
- Subjects 1 `P4`, 8 `F10`, 9 `P4`, and 10 `C4`: localized failures repaired by
  policy-governed interpolation; all participants and condition cells pass
  retained-epoch QC.
- Subject 19 missing `experiment_end`: resolved as metadata-only and irrelevant
  to analysis windows.
- Duplicate markers: resolved by canonical selection while preserving raw
  evidence.
- Missing `ad_displayed` events: not recoverable exactly; handled by validated
  estimators with explicit uncertainty.
- Acquisition reference: not recoverable from XDF metadata; preserve as unknown
  unless externally confirmed.

## Immediate left-to-right gate

The condition and advertisement paths are executable from Bronze through
analysis-ready Gold datasets and initial participant-level contrast tables.
The remaining left-to-right gate is human review of the cleaning validation
figures before changing the Silver policy status to `frozen`.
