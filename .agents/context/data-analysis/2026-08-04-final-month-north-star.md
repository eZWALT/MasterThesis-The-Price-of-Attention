# Final-month north star

Recorded 4 August 2026 from Walter's final-month team plan.

## Deadlines

- Hard thesis deadline: **17 September 2026**.
- Publication submission around **27 September 2026** is a soft target and may
  move. It must not endanger the thesis deadline.
- August is the implementation and first complete-analysis month.
- September is reserved primarily for systematic revision, thesis completion,
  presentation preparation, and publication review.
- Walter is on vacation from **8 through 15 August 2026**. Planning must not
  assign Walter-dependent implementation or review to that interval.
- The rest of the team expects at least two weeks of vacation after the first
  August workweek. Until exact return dates are confirmed, planning assumes no
  dependable team input from **8 through 23 August**.

## Availability-adjusted schedule

### Before vacation — 4–7 August

- obtain a transferable behavioural handoff from Katerina: current ETL code,
  source inventory, schema, scoring directions, identifier mapping, exclusions,
  known failures, and exact commands;
- freeze every behavioural decision that would otherwise block Walter while
  Katerina is unavailable;
- obtain Angela's acquisition-reference and ground answer if possible;
- package the EEG notebook, figures, open gates, and reproducible commands;
- agree concrete team return and review dates for late August and September;
- begin thesis Methods structure and insert already-frozen EEG pipeline facts.

The goal is to remove team dependencies. A verbal status update is not a
sufficient handoff; Walter must be able to run and inspect the behavioural work
without its original author.

### Shared vacation overlap — 8–15 August

- no planned Walter deliverables;
- no assumed deliverables or review from the rest of the team.

### Walter-only work — 16–23 August

- implement the read-versus-write EEG positive control and complete every EEG
  task that does not require team judgment
  (done 2026-08-19; see `eeg/2026-08-19-read-vs-write-what-it-proved.md`);
- freeze Action 4 EEG tables, figures, and provisional interpretation;
- run or repair behavioural ETL only if the pre-vacation handoff is complete;
- write thesis Introduction, Methods, EEG Results, and reproducibility sections;
- collect blocked decisions for one team review after return.

Do not assume behavioural dataset approval, acquisition-reference confirmation,
or scientific signoff during this interval.

### Team return and critical-path recovery — 24–31 August

- freeze the first validated behavioural dataset immediately;
- complete Action 1 behavioural condition analysis;
- close EEG human gates and approve Action 4 interpretation;
- execute Action 5 attention-shift analysis if its metric contract is ready;
- write behavioural Methods and primary Results in parallel.

### Full draft — 1–7 September

- execute a bounded Action 2 moderation analysis;
- implement a simple baseline version of Action 3 only if Actions 1, 4, and 5
  are already stable; otherwise defer Action 3 until after thesis submission;
- restrict exploratory analysis to questions that directly support the paper;
- finish the complete thesis draft and presentation skeleton;
- freeze all main tables and figures.

### Review and submission — 8–17 September

- 8–11 September: team and supervisor review;
- 12–14 September: statistical, narrative, citation, and formatting fixes;
- 15–16 September: final build and submission checks only;
- 17 September: thesis submission.

### Publication revision — after thesis submission

- incorporate thesis-review feedback into the paper;
- obtain Ioannis' final review;
- submit when the paper is scientifically and administratively ready; the
  original 27 September target may be postponed.

## Workstreams in priority order

### 0. Behavioural data

Lead: Katerina. Walter supports refinement, attention-shift work, and modeling.

Required sequence:

1. preprocess production and survey data into the first validated behavioural
   dataset;
2. execute Action 1, condition-level behavioural analysis;
3. execute Action 2, demographic and personality moderation analysis;
4. perform bounded exploratory data analysis for correlations or patterns
   beyond the research questions;
5. Walter reviews and refines the first behavioural implementation;
6. execute Action 5, attention-shift metric analysis;
7. execute Action 3, multi-output prediction and feature importance.

### 1. EEG data

Lead: Walter. Katerina, Angela, and Sebastian provide domain and review support.

Required sequence:

1. complete the reproducible preprocessing-to-dataset pipeline;
2. verify preprocessing validity and document all human gates;
3. retain Subject 4 only as a separately labelled wrong-protocol sensitivity
   if scientifically useful; never add Subject 4 to the primary laboratory
   cohort;
4. freeze the EEG feature hierarchy;
5. execute Action 4, participant-level EEG feature analysis;
6. integrate EEG with behavioural outcomes only after both data contracts are
   frozen.

### 2. Publication

- Walter, Katerina, and Sebastian write and review.
- Ioannis performs final review and leads publication submission.
- Initial analysis outputs must be converted into manuscript tables, figures,
  methods, limitations, and reproducibility statements.

### 3. Thesis and presentation

- Walter owns the thesis and presentation.
- September review support from the team is desirable but not assumed.
- Thesis completion takes precedence over optional exploratory analyses if the
  schedule becomes constrained.

## Five data-analysis action items

These identifiers are the stable project-wide meaning of “the five goals.”

### Action 1 — Behavioural condition analysis

Estimate within-participant differences among:

- any advertising versus no advertising;
- inline versus labelled-block advertising;
- early versus late placement;
- format-by-timing interaction as secondary.

Primary behavioural families remain credibility/trust, perceived
manipulation, and recognition. Report uncertainty, effect sizes, and
multiplicity-adjusted tests.

### Action 2 — Demographic and personality moderation

Evaluate whether demographic variables, familiarity, study arm, and continuous
BFI-10 traits explain heterogeneity in condition effects.

Use shrinkage or parsimonious interaction models. Do not create personality
clusters at the available sample size, and do not replace within-participant
condition evidence with between-person comparisons.

Participant age is currently an unresolved data-availability question. Ioannis
should confirm whether ages can be retrieved lawfully and whether participant
recontact or broadcast email is permitted under the study consent and data
governance process.

### Action 3 — Multi-output prediction and feature importance

Build a bounded multi-output classifier/regressor only after the behavioural
dataset and outcomes are frozen.

Requirements:

- participant-grouped validation;
- leakage-safe preprocessing inside folds;
- simple baselines before complex models;
- uncertainty and out-of-sample metrics;
- permutation or similarly defensible feature importance;
- explicit separation between prediction and causal explanation.

This is lower priority than Actions 1, 2, and 4 and is the first action to
reduce or defer if deadlines are threatened.

### Action 4 — EEG feature analysis

Use the frozen participant-level EEG datasets to analyse:

- primary Fz theta and posterior alpha;
- sustained condition contrasts;
- ad-locked post-minus-pre contrasts against matched no-ad events;
- secondary global bands and FAA;
- exploratory engagement ratios;
- 1,000/1,050/1,500 µV threshold sensitivity;
- participant-level influence and onset-provenance diagnostics.

Do not treat epochs as independent observations. Subject 4 remains excluded
from primary EEG inference because the recording used the wrong protocol.

### Action 5 — Attention-shift metric analysis

Operationalize attention shift from observable conversational or semantic
change rather than claiming direct latent attention measurement.

Requirements:

- define the metric before testing associations;
- validate it against behavioural outcomes as convergent evidence;
- analyse direction, magnitude, uncertainty, and correlation structure;
- use early-ad and matched no-ad turn-2 comparisons where post-exposure text
  exists;
- acknowledge that turn-4 ads lack a subsequent user message;
- treat EEG relationships as exploratory cross-modal evidence.

## Extra analysis — bounded exploratory data analysis

Inspect distributions, missingness, reliability, condition heterogeneity,
within-person correlations, demographic imbalances, and unexpected behavioral
or EEG relationships.

Exploration must remain clearly labelled. Any newly discovered hypothesis is a
future or sensitivity analysis, not a retroactive confirmatory result.

## Current implementation state on 4 August

EEG:

- primary cohort and preprocessing pipeline are implemented for 18 laboratory
  participants;
- condition and ad-response Gold datasets are analysis-ready;
- the 1,050 µV primary and 1,000/1,500 µV sensitivities are generated;
- a publication-analysis runner, tables, six figures, and an executable
  notebook exist under `analysis/eeg/analysis/`;
- current primary EEG contrasts do not survive Holm correction;
- machine checks pass; visual signoff, ICA-as-primary, and the
  read-versus-write positive control closed 2026-08-19
  (`eeg/2026-08-19-read-vs-write-what-it-proved.md`).

Behavioural:

- remains the critical path;
- the first validated behavioural dataset and frozen scoring contract must be
  completed before Actions 1, 2, 3, 5, or multimodal integration can be
  considered publication-ready.

## Scope-control rule

The minimum viable thesis package is:

1. validated behavioural dataset;
2. Action 1 complete;
3. defensible and documented EEG pipeline;
4. Action 4 complete;
5. integrated methods/results/limitations in the thesis;
6. reviewed thesis and presentation.

If schedule pressure rises, reduce work in this order:

1. complex multi-output models;
2. broad exploratory analysis;
3. high-dimensional demographic/personality interactions;
4. optional EEG branches such as ICA or whole-scalp discovery.

Do not sacrifice dataset validation, primary condition analyses, EEG
reproducibility, or thesis writing to preserve optional modeling.

Publication polishing, journal formatting, and submission logistics are outside
the hard-deadline critical path. Before 17 September, paper work should be done
only when it directly reuses and improves thesis Methods, Results, figures, or
limitations.
