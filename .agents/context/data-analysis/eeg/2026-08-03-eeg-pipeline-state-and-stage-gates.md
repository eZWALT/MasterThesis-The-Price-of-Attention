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
- `gold/windows/`: condition and advertisement timing contracts.

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
- Candidate deterministic cleaning: 50 Hz notch, 0.5–40 Hz band-pass, average
  reference, bad-channel marking, and spherical-spline interpolation.
- Successful cleaning test for subject 8 with `F10` interpolation.

### Known signal findings

- No near-flat or flatline channels were found.
- No recording is currently automatically excluded by signal QC.
- Subject 8 `F10` is the only current non-ocular channel flag. It is a candidate
  for interpolation, not a participant exclusion.
- Low `Fp1/Fp2` correlation is treated as expected ocular activity and retained
  for ocular-component assessment.
- Strong cohort-wide 50 Hz contamination requires notch filtering but is not a
  bad-channel criterion.

### Mandatory work remaining

- Visually validate filtering, average rereferencing, and interpolation.
- Decide and validate the ocular-artifact strategy. ICA is currently disabled
  because there are no dedicated EOG channels.
- Compute artifact distributions on actual condition and ad windows.
- Freeze epoch rejection and minimum-retention thresholds.
- Run post-cleaning channel, participant, and condition-cell QC.
- Change `cleaning_policy.json` from `requires_visual_validation` to `frozen`.

The online acquisition reference remains unconfirmed; `FCz` is a hypothesis and
`Fpz` is the operator-recalled ground. This uncertainty must remain explicit,
but it does not prevent average-rereferenced sensor-level processing.

## Gold

### Implemented as provisional contracts

- Baseline and sustained condition-window manifests.
- Five condition windows for every recording.
- Subject 4 windows explicitly marked ineligible.
- Advertisement visibility table with observed and derived provenance.
- 72 eligible laboratory ad events.
- Leave-one-out p95 visual-onset error of 0.226 seconds for missing explicit
  block events and 0.433 seconds for missing inline events.

These uncertainties support multi-second spectral windows, not ERP claims.

### Mandatory work remaining

- Freeze pre-ad and post-ad spectral window definitions.
- Construct matched no-ad pseudo-onsets.
- Apply final Silver cleaning to every eligible window.
- Divide sustained data into fixed-length analysis epochs.
- Calculate retained duration and epoch counts per participant and condition.
- Produce prespecified band-power, FAA, engagement, and related feature tables.
- Freeze Gold schemas and provenance fields.

Gold currently contains timing/window metadata, not final cleaned EEG feature
tables. Its existing contracts remain provisional until the Silver cleaning
policy is frozen.

## Analysis outside Gold

After Gold feature tables are frozen:

- fit baseline, no-ad, format, timing, and pre/post-ad EEG contrasts;
- join EEG summaries to behavioural and personality tables;
- run sensitivity analyses based on retained signal quality;
- produce publication figures, model summaries, and multimodal ablations.

## Issue disposition

- Subject 4: not fixable as a laboratory EEG participant because the wrong
  protocol was run; exclude from primary laboratory inference.
- Subject 8 `F10`: likely fixable by reviewed interpolation; participant remains
  eligible pending epoch QC.
- Subject 19 missing `experiment_end`: resolved as metadata-only and irrelevant
  to analysis windows.
- Duplicate markers: resolved by canonical selection while preserving raw
  evidence.
- Missing `ad_displayed` events: not recoverable exactly; handled by validated
  estimators with explicit uncertainty.
- Acquisition reference: not recoverable from XDF metadata; preserve as unknown
  unless externally confirmed.

## Immediate left-to-right gate

Ingestion and Bronze are closed for the current cohort. Work should now remain
in Silver until visual cleaning validation, artifact rules, and epoch-retention
criteria are frozen. Only then should final Gold EEG features be generated.
