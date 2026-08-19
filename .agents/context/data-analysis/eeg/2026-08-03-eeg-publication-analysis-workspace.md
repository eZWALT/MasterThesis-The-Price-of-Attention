# EEG publication analysis workspace

## Purpose

`analysis/eeg/analysis/` is the interpretation-facing sibling of
`analysis/eeg/preprocessing/`. It reads immutable Gold feature tables and
versioned statistics outputs. It does not modify XDF, Silver, Gold, eligibility,
or artifact decisions.

The workspace provides:

- a reproducible analysis runner;
- a guided and executable Jupyter notebook;
- publication-oriented PNG and vector PDF figures;
- manuscript-facing result and diagnostic tables;
- source hashes and an output manifest;
- twenty executable quality gates.

## Analysis contract

Replication unit: participant (`n=18`).

Primary EEG features:

- Fz theta power;
- posterior alpha power over `O1/Oz/O2/P3/Pz/P4`.

Primary sustained-condition contrasts:

- any ad minus no ads;
- inline minus labelled block;
- early minus late.

Primary ad-response contrasts:

- inline early minus matched no-ad early;
- labelled-block early minus matched no-ad early;
- inline late minus matched no-ad late;
- labelled-block late minus matched no-ad late.

Holm correction is applied across the prespecified primary contrast family
separately for each feature. The publication tables also include a stricter
global-family Holm sensitivity across all primary-feature tests in each
analysis. Global band powers, FAA, interactions, relative powers, gamma/delta,
and all engagement ratios remain secondary or exploratory.

## Files

- configuration: `analysis/eeg/analysis/analysis_config.json`;
- runner: `analysis/eeg/analysis/run_publication_analysis.py`;
- notebook:
  `analysis/eeg/analysis/notebooks/01_eeg_publication_analysis.ipynb`;
- notebook executor: `analysis/eeg/analysis/execute_notebook.py`;
- generated artifacts: `analysis/eeg/analysis/outputs/`;
- workflow documentation: `analysis/eeg/analysis/README.md`.

Run:

```bash
python analysis/eeg/analysis/run_publication_analysis.py
python analysis/eeg/analysis/execute_notebook.py
```

## Generated outputs

Tables:

- cohort and retention summary;
- primary sustained-condition results;
- primary ad-response results;
- exploratory engagement results;
- distribution, signed-rank, bootstrap, and leave-one-participant-out
  diagnostics;
- explicit Subject 14 influence and ad-onset provenance;
- 1,000/1,050/1,500 µV sensitivity estimates.

Figures:

1. cohort and retained-observation flow;
2. primary sustained-condition forest plot;
3. primary ad-response forest plot;
4. participant-level sustained-condition profiles;
5. Fz-theta participant contrast distributions;
6. artifact-threshold sensitivity comparison.

Every figure is emitted as PNG and vector PDF. The executed notebook is saved
under `outputs/reports/`.

## Initial result boundary

No primary sustained-condition or ad-response comparison is Holm-significant at
`alpha=0.05`.

The smallest corrected sustained-condition result is early minus late
posterior alpha:

- mean difference `-0.089 dB µV²`;
- 95% CI `[-0.201, 0.023]`;
- Cohen's `dz=-0.395`;
- feature-family `p_Holm=0.337`;
- global six-test `p_Holm=0.674`.

The smallest corrected ad-response result is inline-late minus matched no-ad
late Fz theta:

- mean difference `-1.992 dB µV²`;
- 95% CI `[-3.942, -0.042]`;
- Cohen's `dz=-0.508`;
- raw `p=0.046`;
- feature-family `p_Holm=0.183`;
- global eight-test `p_Holm=0.366`.

The raw confidence interval excluding zero does not survive the prespecified
Holm family. It must not be presented as confirmatory evidence.

Both 1,000 and 1,500 µV sensitivities preserve confirmatory directions and
corrected conclusions relative to 1,050 µV. Across all primary-feature
diagnostics, the minimum leave-one-participant-out sign stability is 55.6%.
This reinforces participant-level visualization and uncertainty-first
reporting.

The explicit Subject 14 deletion changes the sign of one primary condition
estimate, inline minus labelled-block posterior alpha, from `0.006` to `-0.013
dB µV²`. Both values are effectively centered on zero and the inferential
conclusion is unchanged. Two secondary ad factorial summaries also cross zero;
none becomes corrected evidence.

## Twenty-pass review

`outputs/reports/quality_gates.json` currently reports `20/20` passing:

1. preprocessing soundness;
2. condition validation;
3. ad validation;
4. engagement validation;
5. cohort size;
6. complete condition cells;
7. complete ad/no-ad cells;
8. unique condition keys;
9. unique ad keys;
10. `frozen_v3` primary policy;
11. ICA applied as the approved primary branch;
12. complete primary estimates;
13. complete participant scores;
14. valid Holm probabilities;
15. confidence-interval consistency;
16. threshold comparison pass;
17. threshold-stable confirmatory directions;
18. no uncontrolled-baseline dependency in confirmatory tests;
19. unique epoch keys;
20. complete non-empty artifacts.

These checks prove reproducible internal consistency, not neurophysiological
validity, positive-control sensitivity, or absence of effects.

The publication workspace currently renders the approved ICA primary branch
(`frozen_v5_ica_primary`). The ICA comparison preserved every corrected
condition-test conclusion but yielded six ICA-only corrected ad-response
findings, mostly in early block-ad low-frequency features. Those findings
stay labelled ICA-dependent; they were not the reason the branch was chosen.

## Remaining work

Closed 2026-08-19: filtering/interpolation figures, ICA component review, and
ICA as primary (no-ICA remains the mandatory sensitivity).

Still open:

1. keep all three engagement metrics and decide their final inferential tier;
2. optionally verify reported `Cz` reference/`Fpz` ground handling against the
   acquisition workspace;
3. implement the era-aware read-versus-write positive control
   (done 2026-08-19; see `2026-08-19-read-vs-write-what-it-proved.md`);
4. review manuscript captions and feature/contrast hierarchy.

Multimodal gate:

Do not join behavioral variables until Person A freezes participant mapping,
scale direction, condition/ad identifiers, missingness, exclusions, and output
grain. The first combined table should be participant by condition or
participant by ad-response—not epoch-level pseudoreplication.
