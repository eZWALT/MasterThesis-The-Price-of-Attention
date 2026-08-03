# Independent XDF recording audit

Date: 3 August 2026

## Purpose and scope

This is the durable context summary of the first independent audit of the
production XDF recordings. It records what was established before marker
reconstruction or EEG preprocessing begins.

The audit combines:

- production lab JSONL event logs;
- all XDF files under `src/project/logs/xdf/`;
- XDF stream metadata, EEG sample spans, and marker streams;
- participant-specific matching of common JSONL and XDF marker labels.

Folder and filename participant numbers are treated as hypotheses rather than
ground truth. Matching uses the temporal pattern of same-labelled events and a
duplicate-tolerant affine clock fit.

## Reproducible artifacts

- Generator: `analysis/eeg/manifests/build_recording_manifest.py`
- Human review sheet:
  `analysis/eeg/manifests/eeg_recording_manifest.csv`
- Full machine evidence:
  `analysis/eeg/manifests/eeg_recording_evidence.csv`
- Review instructions: `analysis/eeg/manifests/README.md`

The human sheet contains 19 current XDF recordings. The evidence table contains
21 rows because it also retains superseded `_old` XDF files.

## Current objective summary

| Initial classification | Current recordings |
|---|---:|
| Healthy complete match | 8 |
| Healthy after marker deduplication | 9 |
| Outstanding folder/log mapping mismatch | 0 |
| Partial but reconstructable markers | 1 |
| Wrong protocol | 1 |

These are initial machine classifications, not final inclusion decisions.
Artifact quality, channel quality, and preprocessing retention have not yet been
assessed.

## Recording-level findings requiring action

### `lab_subject_1`

- The corrected full recording contains about 93.1 minutes of EEG.
- It matches all 68 expected log markers with negligible fitted residual.
- Current status: `healthy`.

### `lab_subject_2`

- The recovered recording contains about 36.7 minutes of EEG.
- It matches all 68 expected log markers with negligible fitted residual.
- Current status: `healthy`.

### `lab_subject_4`

- The XDF strongly matches `lab_subject_4_crowdfail`, which ran the crowd
  protocol and has no laboratory baseline.
- Initial status: `wrong_protocol`.
- Action: confirm exclusion from the laboratory EEG cohort.

### `lab_subject_11` and `lab_subject_12`

- The original temporal marker audit identified a cross-folder swap.
- On 3 August 2026, the two XDF payloads were exchanged while preserving the
  stable `lab_subject_11` and `lab_subject_12` folder and filename conventions.
- Production JSONL logs were not renamed or modified.
- The regenerated audit now maps each recording to its same-number log with all
  72 expected markers and negligible fitted residual.
- Current status: `healthy_with_duplicate_markers` for both recordings.

### `lab_subject_19`

- The recording matches its production log, but 71 of 72 expected markers are
  directly matched.
- Initial status: `partial_reconstructable`.
- Action: identify the missing event and reconstruct it from the
  participant-specific clock fit, preserving an observed/derived provenance
  flag.

### Duplicate-marker recordings

Nine current recordings contain all expected canonical events plus duplicated
XDF marker emissions:

- `lab_subject_5`
- `lab_subject_9`
- `lab_subject_10`
- `lab_subject_11`
- `lab_subject_12`
- `lab_subject_14`
- `lab_subject_15`
- `lab_subject_16`
- `lab_subject_18`

These are not evidence of duplicate experimental trials. The canonical marker
sequence must be selected before epoching, and discarded duplicates must remain
documented in the marker manifest.

## What the audit establishes

1. Filename numbering alone was unsafe: the audit detected and corrected the
   11/12 swap before EEG was assigned to behavioural records.
2. Most current recordings have a complete recoverable marker pattern, but nine
   require deterministic deduplication.
3. `lab_subject_19` supplies participant-specific synchronization anchors, so its
   missing marker is reconstructable without borrowing another participant's
   clock offset.
4. The corrected recordings for `lab_subject_1` and `lab_subject_2` are now
   present and pass the marker-timing audit.
5. The machine audit supports recording and marker triage only. It does not yet
   establish EEG signal quality or final analysis eligibility.

## Important caveats

- A near-zero marker-fit residual proves a strong clock/mapping correspondence;
  it does not prove clean EEG channels or artifact-free epochs.
- JSONL session duration and EEG duration need not be identical because logs can
  include setup, pauses, questionnaires, or time outside the acquisition span.
  Required analysis events must be checked against the EEG sample span directly.
- The 11/12 correction is retained in this audit as provenance; regenerated
  marker timing confirms that the corrected same-number mappings are consistent.
- `ad_injected` is generation onset, not visual exposure. This recording audit
  does not resolve exposure-onset reconstruction.
- All statuses remain provisional until the rightmost review columns in
  `eeg_recording_manifest.csv` are completed.

## Immediate next gate

Complete the short recording manifest manually. After mapping and recording
health are frozen:

1. build the canonical observed-marker table;
2. deduplicate the nine affected recordings;
3. reconstruct the single missing event for `lab_subject_19`;
4. implement the XDF-to-MNE adapter;
5. run signal-quality and preprocessing audits before deciding final sustained
   and event-locked inclusion.
