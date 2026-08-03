# EEG recording manifests

Two files are generated from production lab JSONL logs and immutable XDF files
under `src/project/logs/xdf/bronze/`:

- `eeg_recording_manifest.csv` is the concise recording summary. It has one row
  per current recording or missing participant and omits superseded `_old` files.
- `eeg_recording_evidence.csv` is the dense machine-audit table. Use it only
  when the short evidence summary is insufficient.

Regenerate it from the repository root:

```bash
python analysis/eeg/preprocessing/bronze/manifests/build_recording_manifest.py
```

The manifest has no human-annotation columns. Do not edit either generated CSV
by hand; correct its derivation in the generator or encode downstream protocol
and signal eligibility in the corresponding Silver/Gold manifests.

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
cover all required events. Final event and signal eligibility is governed by the
Silver canonical marker, acquisition, and quality-control outputs.

Folder and filename subject numbers are treated as guesses, never ground truth.
