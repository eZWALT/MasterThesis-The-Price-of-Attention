# EEG marker pipeline

These commands turn immutable bronze XDF recordings into validated silver marker
tables. They never edit raw XDF files.

## 1. Organize the lake

Preview the move:

```bash
python analysis/eeg/preprocessing/ingestion/organize_xdf_lake.py
```

Move existing `lab_subject_*` directories into bronze and create the derivative
layers:

```bash
python analysis/eeg/preprocessing/ingestion/organize_xdf_lake.py --apply
```

The applied command calculates a SHA-256 inventory by default. Use
`--skip-hash` only for a temporary fast inventory.

## 2. Audit duplicate causes

```bash
python analysis/eeg/preprocessing/silver/markers/audit_marker_anomalies.py
```

Outputs:

- `silver/audits/marker_anomaly_report.csv`
- `silver/audits/marker_stream_inventory.csv`
- `silver/audits/near_duplicate_groups.csv`
- `silver/audits/extra_marker_details.csv`

The report separates overlapping marker streams, repeated emissions within one
stream, and unmatched extra markers.

## 3. Build canonical marker tables

```bash
python analysis/eeg/preprocessing/silver/markers/build_canonical_markers.py
```

Each expected logged LSL event receives one canonical XDF timestamp. Direct
matches are marked `observed`; missing events projected through the
participant-specific affine clock fit are marked `derived`. Raw duplicates are
reported but never deleted from bronze.

Each XDF is independently matched against all candidate production logs; folder
numbering is evidence, not the join key. Canonical rows include the bronze
SHA-256 hash.

Recordings from another study protocol can still receive a canonical timeline
for signal-quality work, but `study_protocol_eligible` and
`primary_analysis_eligible` remain `no`. This keeps subject 4 usable for
technical checks without silently admitting it to laboratory contrasts.

Subject 19's missing `experiment_end` is retained as a `metadata_only`
projection because it is outside the EEG span and far beyond the final observed
anchor. It is never EEG-timing or primary-analysis eligible.

Outputs:

- `silver/canonical_markers/lab_subject_N.csv`
- `silver/canonical_marker_manifest.csv`

## 4. Validate reconstruction

```bash
python analysis/eeg/preprocessing/silver/markers/validate_marker_reconstruction.py
```

The validator hides each observed marker and all near-simultaneous raw
duplicates, reruns correspondence selection and clock fitting, then reports
held-out timing error.

This validates JSONL-to-XDF clock projection. It does **not** validate estimated
visual ad onset; that requires a separate UI-timing validation before
before/after-ad analysis.

## 5. Verify recovery invariants

```bash
python analysis/eeg/preprocessing/silver/markers/verify_recovery_invariants.py
```

This fail-fast check requires all 18 laboratory XDFs to select the correct log,
pass clock fitting and XDF-to-MNE conversion, cover every expected event through
observed or governed provenance, pass leakage-resistant holdout accuracy, and
produce a baseline plus all five condition windows. Any failed invariant exits
with an error rather than silently reducing the cohort.

## Gold layer

Gold contains validated condition and ad-response feature datasets. Marker
timing remains provenance-aware, and estimated inline visual onsets retain their
calibrated uncertainty rather than being treated as exact ERP events.
