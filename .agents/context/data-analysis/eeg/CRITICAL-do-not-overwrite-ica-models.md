# CRITICAL — do not overwrite signed-off ICA models

**Status: MUST READ before any ICA / `clean_eeg` / Gold rebuild command.**

The 18 approved models live at

`src/project/logs/xdf/silver/ica/candidate_v1/`

Walter signed them off on 2026-08-19. Feature building **applies** those
files. It must not **fit** new ones unless Walter explicitly orders a
refit **and** the cleaner is the no-ICA policy.

## Forbidden

```bash
python analysis/eeg/preprocessing/silver/signal/fit_ica_cohort.py --overwrite
python analysis/eeg/preprocessing/run_ica_sensitivity.py --overwrite-models
```

Also forbidden: deleting or replacing `*-ica.fif` / `lab_subject_*.json`
under `candidate_v1/` to “refresh” ICA.

## Why

After ICA became primary, `clean_recording()` defaults to
`cleaning_policy.json`, which **already applies** the saved ICA. The fit
runner then calls `fit_candidate_ica()` on that already-cleaned Raw.
`--overwrite` would write a second, different ICA over the signed-off
archive. Later Gold would use the wrong model.

Safe default: the report exists → print `reusing fitted ICA` → stop.

## If a refit is ever required

1. Get an explicit human go-ahead.
2. Clean with `cleaning_policy_no_ica_sensitivity.json` only
   (`fit_ica_cohort.py --base-policy .../cleaning_policy_no_ica_sensitivity.json`).
3. Fit, review every exclusion again, then re-sign off.
4. Do not treat this as a routine rebuild.

Pointers: `2026-08-20-pipeline-sanity-audit.md`,
`2026-08-19-ica-primary-and-visual-signoff.md`.
