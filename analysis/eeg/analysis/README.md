# EEG publication analysis

This folder is the analysis sibling of `analysis/eeg/preprocessing/`.
Preprocessing creates immutable Silver and Gold datasets; this folder reads
those outputs and produces interpretation-facing tables, figures, diagnostics,
and notebooks.

## Scientific goals

The initial analysis answers two distinct questions:

1. **Sustained condition effects:** Does EEG activity differ between any-ad and
   no-ad conversations, inline and labelled-block formats, or early and late
   ad timing?
2. **Ad-locked responses:** Does the four-second post-onset change differ from
   the timing-matched no-ad response for each format and timing cell?

The participant is always the replication unit.

## Analysis hierarchy

- **Primary features:** Fz theta and posterior alpha.
- **Primary condition contrasts:** any ad minus no ads, inline minus labelled
  block, and early minus late.
- **Primary ad contrasts:** each of four ad cells minus its timing-matched
  no-ad response.
- **Secondary:** global theta/alpha/beta, FAA, and factorial interactions.
- **Exploratory:** three engagement ratios, delta/gamma, and relative powers.

Holm correction is performed separately for each EEG feature across its
prespecified primary contrast family. A stricter sensitivity column also
corrects all primary-feature tests together within each analysis. Secondary and
exploratory results are clearly labelled and must not be promoted after
inspection.

## Run

From the repository root:

```bash
python analysis/eeg/analysis/run_publication_analysis.py
```

The runner verifies twenty quality gates and then writes:

- `outputs/tables/`: QC, primary results, exploratory engagement,
  assumption/influence diagnostics, Subject 14 influence, onset provenance,
  and threshold sensitivity;
- `outputs/figures/`: six figures in PNG and vector PDF;
- `outputs/reports/analysis_manifest.json`: input hashes, analysis contract,
  output inventory, and gates;
- `outputs/reports/initial_results_summary.md`: concise initial interpretation.

## Notebook

Open `notebooks/01_eeg_publication_analysis.ipynb`. It is designed as the
human-facing workspace:

1. verify repository paths and regenerate outputs;
2. inspect Gold condition and ad-response tables;
3. review cohort retention and the analysis hierarchy;
4. inspect primary results with effect sizes and confidence intervals;
5. examine participant-level profiles and distributions;
6. review assumption and leave-one-participant-out diagnostics;
7. compare 1,000, 1,050, and 1,500 µV policies;
8. explore FAA and engagement without changing their inferential tier;
9. define the future behavioral–EEG integration contract.

The notebook delegates production output generation to
`run_publication_analysis.py`; interactive cells may be edited freely without
silently changing the publication contract.

## Twenty quality passes

The executable gates cover:

1. aggregate preprocessing soundness;
2. condition validation;
3. ad validation;
4. engagement validation;
5. cohort size;
6. complete condition cells;
7. complete ad/no-ad cells;
8. unique condition keys;
9. unique ad keys;
10. frozen primary policy;
11. explicit no-ICA policy;
12. complete primary estimates;
13. complete participant scores;
14. bounded Holm-adjusted probabilities;
15. confidence-interval consistency;
16. threshold comparison status;
17. confirmatory direction stability;
18. no uncontrolled-baseline dependency in confirmatory tests;
19. unique epoch keys;
20. complete non-empty publication artifacts.

Passing these gates demonstrates internal consistency and reproducibility. It
does not replace the remaining human signoff on cleaning figures, acquisition
reference, ICA policy, or scientific interpretation.

This workspace currently renders the frozen no-ICA primary branch. The
implemented ICA sensitivity is generated separately with
`analysis/eeg/preprocessing/run_ica_sensitivity.py`. Its first comparison
preserved all corrected condition conclusions but produced six ICA-only
corrected ad-response findings. Do not merge those findings into the
publication notebook until component-level human review chooses the final
cleaning branch.

The era-aware read-versus-write positive control described in the analysis plan
is not yet implemented. It requires additional marker-derived windows and is an
interpretation gate, not one of the twenty checks of currently generated
artifacts. Until it is implemented, null condition results cannot be used as
evidence that the pipeline was sensitive to every plausible state difference.

## Method basis

The runner operationalizes the literature decisions documented in
`.agents/context/data-analysis/eeg/2026-08-03-eeg-analysis-ready-datasets-and-open-decisions.md`:

- COBIDAS-style transparent cohort, acquisition, preprocessing, and exclusion
  reporting;
- participant-level inference rather than treating epochs as independent;
- Welch-derived regional spectral features;
- Allen-style caution for FAA interpretation;
- Pope-family and advertising-specific engagement ratios kept exploratory;
- confidence intervals, standardized within-participant effects, nonparametric
  sensitivity, multiplicity correction, threshold sensitivity, and
  leave-one-participant-out influence review.

## Current interpretation boundary

This is a publication-oriented initial analysis, not a final manuscript result.
The cohort has 18 participants. Lead with confidence intervals,
participant-level plots, and sensitivity analyses. Never interpret
non-significance as proof of no effect. Behavioral covariates should be joined
only after the behavioral data contract and subject mapping are frozen.
