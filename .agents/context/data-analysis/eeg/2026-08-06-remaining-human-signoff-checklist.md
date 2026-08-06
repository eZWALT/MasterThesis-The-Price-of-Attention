# Remaining human signoff checklist

Date: 6 August 2026

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
  used the crowd protocol rather than because of missing baseline or bad EEG.

## Required human inputs

### 1. ICA component review

Open:

`src/project/logs/xdf/silver/ica/candidate_v1/ica_review.html`

For each participant, inspect:

1. selection evidence;
2. component topography;
3. source versus `Fp1/Fp2` time course;
4. component spectrum.

The minimum usable response is either:

- `approve all candidate ICA removals`; or
- a list of exceptions such as
  `Subject 14: keep IC0, remove IC2 and IC5`.

Focused review is especially important for:

- Subjects 11, 14, and 15, where three components were selected;
- Subject 17, where the 99% rule yielded only six components;
- Subject 19, where no component passed the joint automatic rule.

Do not choose components based on whether their removal creates statistically
significant ad effects. Ocular topography, time course, spectrum, and proxy
correlation must drive the decision.

### 2. Final ICA versus no-ICA branch

After component signoff and any required rerun, select:

- ICA as primary and no ICA as sensitivity; or
- no ICA as primary and ICA as sensitivity.

This decision matters because condition conclusions were stable, but six
corrected ad-response tests became significant only under ICA. The branch
cannot be chosen by preferring those results.

### 3. Filtering and interpolation visual signoff

The generated filtering and bad-channel repair figures still need an explicit
human disposition:

- approve;
- reject with a concrete concern; or
- request review by an EEG-experienced laboratory colleague.

The existing figures support technical plausibility, but prior discussion did
not constitute explicit final approval.

### 4. Positive-control interpretation — resolved

Human decision received on 2026-08-06:

- estimate reading and writing epochs from the available event timing;
- begin with static, fixed-duration epochs rather than dynamic-duration
  estimates;
- restrict this analysis to baseline and condition periods.

Candidate static contract:

- baseline: reuse retained non-overlapping four-second baseline epochs;
- reading: first complete four-second interval after an `assistant_reply`;
- writing: final complete four-second interval before the following
  `user_message`;
- include only intervals bounded by `condition_start` and
  `condition_conclusion_submitted`;
- exclude warmup, questionnaires, and post-task periods;
- reject pairs whose reading and writing intervals overlap or fall outside the
  parent condition.

This contract is necessary because `user_starts_typing`, `turn_N_write`, and
`turn_N_read` can share the submission timestamp in the logs and therefore do
not independently measure true typing onset. Dynamic epochs can be added later
as a sensitivity using reply length, message length, and total
`time_to_reply_ms`; they are not the first implementation.

### 5. Behavioral handoff

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

- apply any ICA component overrides and regenerate Gold outputs;
- rerun ICA/no-ICA and threshold sensitivities;
- implement the static baseline/reading/writing positive-control windows;
- export total PSD and mean absolute amplitude;
- add entropy or connectivity only after their estimator contracts are frozen;
- regenerate publication tables, figures, and the notebook.

## Machine-test status

`analysis/eeg/preprocessing/test_eeg_metrics.py` contains one self-contained
suite covering synthetic spectral formulas, FAA, Pope and Kislov engagement,
artifact rejection, ad-response arithmetic, policy separation, primary and ICA
Gold validators, and ICA evidence completeness. The current local run passes
all 12 tests. This reduces implementation risk but does not replace the human
signoffs above.
