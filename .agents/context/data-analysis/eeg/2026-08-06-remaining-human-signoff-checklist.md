# Remaining human signoff checklist

Date: 6 August 2026
Updated: 19 August 2026

## Purpose

This entry separates decisions that genuinely require a person from work the
pipeline can complete automatically. Machine checks, synthetic metric tests,
and dataset validators establish implementation consistency; they do not decide
whether an ICA component is physiologically appropriate to remove or which
analysis branch should support the manuscript.

## Inputs already resolved

No further human action is currently needed for:

- online acquisition reference: `Cz`;
- acquisition ground: `Fpz`;
- offline rereference: common average;
- baseline state: uncontrolled and mixed, but mostly eyes open;
- primary gross-artifact threshold: `1050 µV` peak-to-peak;
- retained engagement family: global Pope, frontocentral Pope, and central
  Kislov beta/alpha;
- protocol cohort: Subjects 1–3 and 5–19, with Subject 4 excluded because it
  used the crowd protocol rather than because of missing baseline or bad EEG;
- filtering and interpolation figures: approved 2026-08-19;
- ICA automatic exclusions: approved 2026-08-19 (all 18, including Subject
  14's three components);
- primary cleaning branch: ICA (`frozen_v5_ica_primary`); no-ICA remains the
  mandatory sensitivity under `cleaning_policy_no_ica_sensitivity.json`.

## Remaining human / scientific inputs

### 1. Positive-control interpretation — decided 2026-08-06, not implemented

The read-versus-write analysis is a pipeline sanity check, not Q1/Q2. It asks
whether the same 4 s / 16-feature chain can tell reading from typing. If it
cannot, a null ad-condition result is hard to interpret.

Do **not** time-lock to `user_starts_typing`, `turn_N_write`, or `turn_N_read`.
In the deployed lab app those events often share the message-submission
timestamp, so they do not mark true reading onset or typing onset.

Static contract (first implementation, if/when coded):

- baseline: reuse retained non-overlapping four-second baseline epochs;
- reading: first complete four-second interval after an `assistant_reply`;
- writing: final complete four-second interval before the following
  `user_message`;
- include only intervals bounded by `condition_start` and
  `condition_conclusion_submitted`;
- exclude warmup, questionnaires, and post-task periods;
- reject pairs whose reading and writing intervals overlap or fall outside the
  parent condition.

Dynamic-duration epochs (reply length, message length, `time_to_reply_ms`) are
a later sensitivity, not the first implementation.

### 2. Behavioral handoff

Before EEG and behavior are joined, Person A must freeze:

- participant mapping;
- outcome names and scale directions;
- condition and ad identifiers;
- missingness and exclusion rules;
- whether recall, trust, helpfulness, convincingness, preference, or another
  measure is the target for engagement validation.

The join should use participant-by-condition or participant-by-ad-response
rows, never EEG epochs as independent observations.

## Optional human evidence

If the original BrainVision/actiCHamp acquisition workspace or recorder setup
file becomes available, it can verify how `Cz` was exported despite being the
reported online reference. This is useful provenance, not a blocker.

## Work that does not require additional human input

After the signoffs above, the pipeline can automatically:

- regenerate Gold outputs under the approved ICA primary policy;
- rerun ICA/no-ICA and threshold sensitivities;
- rebuild Path A summaries with `--from-epochs` (mean vs median);
- retile Path A/B at other epoch lengths (2/8/16/32 s) as robustness,
  without promoting a width that happens to yield p < 0.05;
- implement the static baseline/reading/writing positive-control windows;
- export total PSD and mean absolute amplitude;
- add entropy or connectivity only after their estimator contracts are frozen;
- regenerate publication tables, figures, and the notebook.

## Machine-test status

`analysis/eeg/preprocessing/test_eeg_metrics.py` contains one self-contained
suite covering synthetic spectral formulas, FAA, Pope and Kislov engagement,
artifact rejection, ad-response arithmetic, median vs mean window
aggregation, complete-epoch tiling, condition-contrast feature suffixes,
policy separation, primary and ICA Gold validators, and ICA evidence
completeness. Passing that suite reduces implementation risk but does not
replace the human signoffs above.
