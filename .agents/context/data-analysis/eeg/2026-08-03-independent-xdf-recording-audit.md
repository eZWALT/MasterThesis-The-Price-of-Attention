# Independent XDF recording audit

Date: 3 August 2026

## Purpose and scope

This is the durable context summary of the first independent audit of the
production XDF recordings, followed by the resolutions established during
marker reconstruction and initial EEG preprocessing.

The audit combines:

- production lab JSONL event logs;
- all immutable XDF files under `src/project/logs/xdf/bronze/`;
- XDF stream metadata, EEG sample spans, and marker streams;
- participant-specific matching of common JSONL and XDF marker labels.

Folder and filename participant numbers are treated as hypotheses rather than
ground truth. Matching uses the temporal pattern of same-labelled events and a
duplicate-tolerant affine clock fit.

## Reproducible artifacts

- Generator:
  `analysis/eeg/preprocessing/bronze/manifests/build_recording_manifest.py`
- Concise recording summary:
  `analysis/eeg/preprocessing/bronze/manifests/eeg_recording_manifest.csv`
- Full machine evidence:
  `analysis/eeg/preprocessing/bronze/manifests/eeg_recording_evidence.csv`
- Manifest documentation:
  `analysis/eeg/preprocessing/bronze/manifests/README.md`
- Marker pipeline: `analysis/eeg/preprocessing/silver/markers/`
- Silver anomaly report:
  `src/project/logs/xdf/silver/audits/marker_anomaly_report.csv`
- Canonical marker manifest:
  `src/project/logs/xdf/silver/canonical_marker_manifest.csv`
- Reconstruction validation:
  `src/project/logs/xdf/silver/validation/reconstruction_validation_summary.csv`

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

These are marker classifications, not final inclusion decisions. A subsequent
condition-blind signal audit sampled six minutes across each recording. It found
no flat channels or automatic recording exclusions; subject 8 channel `F10` is
the only current non-ocular channel review flag.

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
- Final protocol status: `wrong_protocol`.
- Decision: retain the recording in Bronze provenance but exclude it from the
  laboratory EEG cohort and all primary laboratory contrasts.

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
- The missing event is `experiment_end`. Its participant-specific projected
  timestamp falls about 30 seconds beyond the recorded EEG span and about 581
  seconds beyond the final observed marker, so it cannot define an EEG epoch and
  does not affect earlier event windows.
- The silver canonical table preserves it as `derived` with
  `participant_affine_projection` provenance, `metadata_only` scope, and a
  conservative extrapolation-aware uncertainty.
- The initial manifest status remains `partial_reconstructable` as provenance,
  but all analysis-relevant events are available. The unresolved event is
  metadata-only and does not reduce EEG analysis eligibility.

### Extra-marker recordings

The detailed silver audit distinguishes two mechanisms that the initial
recording manifest grouped together.

- Near-simultaneous overlap across marker streams occurs in subjects 5, 7,
  9–12, 15, 16, and 19.
- Time-separated repeated emissions occur in subjects 13, 14, 18, and 19.

These are not duplicate experimental trials. One canonical marker is selected
for each expected JSONL event; every unselected raw marker remains in bronze and
is documented in `extra_marker_details.csv`.

## What the audit establishes

1. Filename numbering alone was unsafe: the audit detected and corrected the
   11/12 swap before EEG was assigned to behavioural records.
2. Every lab recording has a complete canonical event timeline inside its EEG
   span; subject 19's only derived event is the post-recording
   `experiment_end`.
3. `lab_subject_19` supplies participant-specific synchronization anchors, so its
   missing marker is reconstructable without borrowing another participant's
   clock offset.
4. The corrected recordings for `lab_subject_1` and `lab_subject_2` are now
   present and pass the marker-timing audit.
5. The marker audit supports recording and timing triage. The later signal audit
   adds channel-level evidence, but final eligibility still depends on cleaned
   epoch retention.
6. Leakage-resistant leave-one-marker-out validation over 1,265 observed markers
   has a global 95th-percentile absolute timing error of about 0.000043 seconds.
   Each held-out event and all its near-simultaneous duplicates are removed
   before correspondence and clock fitting are rerun. This validates
   JSONL-to-XDF clock projection, not visual ad-onset semantics.

## Reproducible recovery proof

Run:

```bash
python analysis/eeg/preprocessing/silver/markers/validate_marker_reconstruction.py
python analysis/eeg/preprocessing/silver/markers/verify_recovery_invariants.py
```

The 3 August rerun established for the 18 laboratory recordings:

- 18 of 18 independently select their same-participant production log;
- 18 of 18 pass the governed affine clock-fit criteria;
- 1,199 directly observed events are each predicted under marker holdout;
- 354 holdouts remove multiple near-simultaneous raw samples;
- zero held-out events rematch to another marker;
- laboratory p95 holdout error is 0.000042 seconds and the maximum is
  0.000099 seconds;
- all 18 convert to MNE, with canonical annotation placement no farther than
  0.000999 seconds from an EEG sample;
- all 18 produce one baseline and five eligible condition windows.

There are 1,200 expected laboratory events: 1,199 are observed and one is the
subject 19 metadata-only `experiment_end`; none are unavailable. These checks
prove recording identity and event-timing usability. They do not replace final
cleaned-epoch signal retention.

## Important caveats

- A near-zero marker-fit residual proves a strong clock/mapping correspondence;
  it does not prove artifact-free epochs.
- JSONL session duration and EEG duration need not be identical because logs can
  include setup, pauses, questionnaires, or time outside the acquisition span.
  Required analysis events must be checked against the EEG sample span directly.
- The 11/12 correction is retained in this audit as provenance; regenerated
  marker timing confirms that the corrected same-number mappings are consistent.
- `ad_injected` is generation onset, not visual exposure. The separate Gold
  visibility contract now prefers observed `ad_displayed` events and uses
  validated estimators where they are absent. Leave-one-out p95 errors are
  0.226 seconds for explicit blocks and 0.433 seconds for inline ads.
- `eeg_recording_manifest.csv` is an annotation-free generated summary. The
  reproducible machine evidence, canonical marker manifest, and explicit
  protocol decision for subject 4 govern downstream processing.

## Immediate next gate

Bronze organization, canonical markers, XDF-to-MNE conversion, condition-blind
channel QC, five-condition window construction, and ad-onset validation are now
implemented. All 18 laboratory-protocol recordings have a baseline and five
eligible sustained condition windows; subject 4 remains explicitly ineligible.
Next:

1. visually validate the candidate filter, rereference, interpolation, and
   ocular-component strategy;
2. freeze epoch-level artifact and retention rules;
3. extract prespecified spectral features from retained windows.
