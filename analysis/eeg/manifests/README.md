# EEG recording manifest review

Two files are generated from production lab JSONL logs and the XDF files under
`src/project/logs/xdf/`:

- `eeg_recording_manifest.csv` is the short human-review sheet. It has one row
  per current recording or missing participant and omits superseded `_old` files.
- `eeg_recording_evidence.csv` is the dense machine-audit table. Use it only
  when the short evidence summary is insufficient.

Regenerate it from the repository root:

```bash
python analysis/eeg/manifests/build_recording_manifest.py
```

The generator recalculates evidence and initial guesses while preserving entries
in the seven review columns of the short manifest.

## Columns to fill manually

- `mapping_correct`: `yes`, `no`, or `uncertain`.
- `corrected_mapping`: fill only when the proposed mapping is wrong.
- `health_correct`: `yes`, `no`, or `uncertain`.
- `corrected_health`: fill only when the initial status is wrong.
- `include_sustained_eeg`: `yes`, `no`, or `pending`.
- `include_event_locked_eeg`: `yes`, `no`, or `pending`.
- `reviewer_notes`: correction evidence or relevant lab notes.

Normally, review only `eeg_recording_manifest.csv`. Do not edit
`eeg_recording_evidence.csv` by hand; correct its derivation in the generator.

## Initial health labels

- `healthy`: complete marker-timing match without substantial extras.
- `healthy_with_duplicate_markers`: complete match plus duplicate XDF markers;
  canonicalization is required before epoching.
- `partial_reconstructable`: a strong mapping exists but expected markers are
  missing.
- `folder_mismatch`: marker timing strongly matches a different production log
  than the XDF folder name.
- `marker_mismatch`: insufficient evidence for a clean marker/log mapping.
- `partial_recording`: EEG is shorter than five minutes.
- `wrong_protocol`: the numbered log ran the crowd rather than lab protocol.
- `missing_xdf`: a production lab log has no corresponding XDF file.

## Important interpretation

The marker matching compares the complete pattern of same-labelled JSONL and XDF
events using a duplicate-tolerant participant-specific clock fit. A tiny residual
is strong mapping evidence, but it does not by itself prove that all EEG samples
cover all required events. Use the EEG-span columns and manual lab notes before
approving a recording.

Folder and filename subject numbers are treated as guesses, never ground truth.
