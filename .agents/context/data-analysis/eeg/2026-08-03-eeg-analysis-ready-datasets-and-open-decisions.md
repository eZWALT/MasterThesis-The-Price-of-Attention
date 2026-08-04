# EEG analysis-ready datasets and open decisions

Date: 3 August 2026

## Purpose

This entry preserves the implementation state, validation evidence, scientific
decisions, and unresolved inputs after completing the first condition-level and
ad-response EEG datasets. It should be read together with
`2026-08-03-eeg-pipeline-state-and-stage-gates.md`.

## Executable pipeline

The top-level entry point is:

```bash
python analysis/eeg/preprocessing/run_pipeline.py
```

It executes:

1. Bronze recording inventory;
2. Silver marker reconstruction and invariants;
3. XDF-to-MNE conversion and signal audit;
4. condition, visual-ad, and matched no-ad window construction;
5. condition and ad spectral feature extraction and validation;
6. initial participant-level statistical contrast tables.

The visual cleaning pack is intentionally separate:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --stage silver-visual
```

Run both archived threshold sensitivity branches with:

```bash
python analysis/eeg/preprocessing/run_threshold_sensitivity.py
```

After the visual pack and sensitivity branch exist, aggregate machine evidence
with:

```bash
python analysis/eeg/preprocessing/run_pipeline.py --stage validation
```

The executable preprocessing code is under
`analysis/eeg/preprocessing/`. Statistical inference remains outside Gold under
`analysis/eeg/statistics/`.

## Cohort

- 19 XDF recordings are preserved.
- Subject 4 used the crowd protocol and is excluded from laboratory inference.
- Subjects 1–3 and 5–19 form the 18-participant EEG cohort.
- No laboratory participant is excluded globally because of signal quality.

## Silver cleaning contract

Current policy: `analysis/eeg/preprocessing/silver/signal/cleaning_policy.json`.

- 50 Hz notch filter;
- 0.5–40 Hz band-pass filter;
- average rereference;
- spherical-spline interpolation of governed bad channels;
- current Gold features use no ICA;
- a separate ICA branch retaining 99% PCA variance is now required;
- `Fp1/Fp2` are ocular-sensitive scalp EEG proxies, not dedicated EOG
  channels, and remain present until component rejection is validated.

Recording-specific repaired channels:

- subject 1 `P4`;
- subject 8 `F10`;
- subject 9 `P4`;
- subject 10 `C4`.

These repairs were derived from channel and full-window evidence, not manual
manifest annotations.

## Artifact policy

Primary policy `frozen_v3`:

- reject a four-second epoch when any EEG channel exceeds 1,050 µV
  peak-to-peak;
- reject an epoch containing a near-flat channel;
- sustained windows require at least 80% and at least five retained epochs;
- aggregate sustained windows using retained-epoch medians.

The 1,000 µV `frozen_v1` and 1,500 µV `frozen_v2` rules are preserved as
stricter and permissive sensitivities. The 1,050 µV decision was selected
specifically after observing Subject 14's 1,042.56 µV epoch. It is therefore a
versioned, post-review, participant-retention-driven policy and must never be
described as preregistered or literature-derived. Publication results must show
whether conclusions change under both archived policies.

Policy files:

- primary: `silver/signal/cleaning_policy.json`;
- archived sensitivities:
  `silver/signal/cleaning_policy_frozen_v1.json` and
  `silver/signal/cleaning_policy_frozen_v2.json`.

All paths are relative to `analysis/eeg/preprocessing/`.

The word `frozen` means the numerical decisions are versioned and must not be
changed after examining statistical outcomes simply to preserve participants or
produce preferred results. It does not mean the code cannot be improved. A
policy change requires a new version, an evidence-based rationale, full dataset
regeneration, and a sensitivity comparison against the superseded version.

## Visual cleaning validation

Generated evidence:

- `src/project/logs/xdf/silver/validation/cleaning_visual/filtering_validation.png`;
- `src/project/logs/xdf/silver/validation/cleaning_visual/interpolation_validation.png`;
- `src/project/logs/xdf/silver/validation/cleaning_visual/cleaning_visual_validation.json`.

Objective checks pass:

- representative 50 Hz peaks collapse after filtering;
- average-reference residual is effectively zero;
- all four repaired channels remain below 1,000 µV in their worst inspected
  segment after interpolation;
- repaired-channel correlation with neighboring signals ranges from 0.688 to
  0.991.

Human visual signoff remains pending. Until signoff, the overall policy status
remains `requires_visual_validation`, although the numerical epoch rule is
already `frozen_v3`.

## Condition dataset

Generated outputs:

- `src/project/logs/xdf/gold/features/condition_epoch_features.csv`;
- `src/project/logs/xdf/gold/features/condition_features.csv`;
- `src/project/logs/xdf/gold/features/condition_feature_validation.json`.

Validation:

- status `analysis_ready_condition_v1`;
- 18 participants;
- 108 windows: 18 baseline and 90 condition windows;
- 9,468 complete four-second epochs;
- 9,438 retained epochs (99.68%);
- all 108 windows pass retention;
- no duplicate keys or non-finite spectral values.

The baseline eye state was not controlled and was recalled as mostly eyes open.
Baseline rows are labelled `uncontrolled_mostly_open`. Baseline-derived
descriptives require a sensitivity analysis using condition medians without
baseline subtraction.

## Ad and matched no-ad dataset

Advertisement exposure is locked to participant-visible onset, not
`ad_injected`:

- observed `ad_displayed` when available;
- validated block estimate from assistant reply plus calibrated lag;
- validated inline estimate from injection plus calibrated lag.

Inline derived onset has a maximum combined uncertainty of approximately 0.433
seconds. This supports four-second spectral windows, not ERP claims.

Matched no-ad controls use clock-projected `assistant_reply` events:

- turn 2 for early controls;
- turn 4 for late controls.

`turn_N_read` is a user-submission marker and must never be used as visual
onset.

Generated outputs:

- `src/project/logs/xdf/gold/windows/ad_analysis_windows.csv`;
- `src/project/logs/xdf/gold/features/ad_epoch_features.csv`;
- `src/project/logs/xdf/gold/features/ad_response_features.csv`;
- `src/project/logs/xdf/gold/features/ad_feature_validation.json`.

Validation:

- status `analysis_ready_ad_v1`;
- 216 four-second epochs;
- 72 advertisement events and 36 matched no-ad reference events;
- 216 of 216 epochs retained;
- 108 of 108 pre/post pairs retained;
- all four advertisement conditions retain 18 participants;
- matched no-ad controls retain 36 of 36 pairs.

## Subject 14 decision

Subject 14 is not excluded.

Under `frozen_v3`, the early matched no-ad response is retained:

- pre epoch retained at 298.27 µV peak-to-peak;
- post epoch reached 1,042.56 µV peak-to-peak at `F4`;
- the post epoch is 7.44 µV below the 1,050 µV primary threshold;
- the pre/post pair is therefore eligible.

Consequences:

- all subject 14 sustained-condition data remain usable;
- all four real advertisement responses remain usable;
- all planned ad-versus-no-ad contrasts retain 18 participants.

This retention was decided with knowledge of the observation. It is therefore
not evidence that 1,050 µV is scientifically optimal. It is a second policy
revision made after statistical outputs existed, and must be disclosed as
such. The mandatory robustness contract is:

- use 1,050 µV as the explicitly selected `frozen_v3` primary policy;
- report both 1,000 µV `frozen_v1` and 1,500 µV `frozen_v2` sensitivities;
- compare effect direction, magnitude, confidence intervals, corrected
  significance, and the Subject 14 influence;
- do not tune the threshold again after comparing these three fixed policies.

## Spectral features

Each condition or pre/post epoch contains:

- global delta, theta, alpha, beta, and gamma absolute log power;
- relative power for each band;
- Fz theta power;
- posterior alpha over `O1/Oz/O2/P3/Pz/P4`;
- FAA as `ln(alpha F4) - ln(alpha F3)`;
- global Pope-family engagement as `beta / (alpha + theta)`;
- frontocentral Pope-family engagement over
  `F3/F4/Fz/FC1/FC2/C3/C4/Cz`;
- advertising-specific Kislov engagement as central 16–24 Hz beta divided by
  central 8–12 Hz alpha over `Cz/Pz/P3/P4`;
- amplitude, bad-channel, retention, timing, and provenance fields.

Fz theta and posterior alpha are the initial primary regional features. FAA is
secondary. Engagement and broad global/relative powers remain exploratory
unless explicitly preregistered otherwise.

`validate_engagement_features.py` verifies that all retained condition and ad
values are finite and positive, summarizes each implementation, and records
pairwise Spearman correlations. Its report is
`src/project/logs/xdf/gold/features/engagement_feature_validation.json`.

## Literature-grounded soundness audit

### What the literature supports strongly

**Reproducible reporting.** COBIDAS MEEG requires the original reference and
ground, sensor layout, filter design, artifact criteria, interpolation,
rereferencing, and ICA details to be reported. It also emphasizes that
preprocessing order can change results [1]. This repository records the order
and parameters in executable code and `cleaning_policy.json`. The acquisition
reference remains an explicit unresolved field rather than an inferred fact.

**Filter specification and validation.** Widmann, Schröger, and Maess warn that
filter choices can distort electrophysiological data and recommend reporting
filter type, cutoffs, transition behavior, causality, and response [2]. The
pipeline fixes 50 Hz notch and 0.5–40 Hz band-pass operations in code. The
validation pack measures line-noise reduction on four representative
recordings rather than assuming filtering worked. The report currently shows
more than 99.9998% reduction of its defined 50 Hz line-noise ratio and an
average-reference mean residual near numerical zero.

**Bad-channel handling before group features.** PREP demonstrates that noisy
channels contaminate ordinary average references and motivates robust bad
channel identification followed by interpolation [3]. MNE implements EEG
interpolation with spherical splines [4, 5]. This pipeline excludes governed
bad channels from the average, interpolates them with MNE, and validates the
four repaired channels against amplitude and neighboring-channel correlation.

**Welch spectral estimation.** Welch's method averages modified periodograms to
reduce variance in spectral estimates [6]. MNE-Python provides the
well-documented, reproducible EEG processing environment used here [7]. The
pipeline uses 4-second analysis epochs, 2-second Welch segments, 50% overlap,
and explicit frequency bands. Epochs remain nested within participants;
statistical scripts never treat epochs as independent people.

**FAA construction.** The implemented `ln(alpha F4) - ln(alpha F3)` follows the
common right-minus-left log-alpha construction discussed by Allen, Coan, and
Nazarian [8]. Ohme and colleagues applied frontal EEG asymmetry directly to
advertising responses [9]. FAA remains secondary because reference choice,
ocular artifacts, epoch duration, and the inverse relation between alpha and
cortical activation complicate interpretation [8].

**Engagement formulas.** Pope, Bogart, and Bartolome found
`beta / (alpha + theta)` to be the best of their tested operator-engagement
indices [10]. The current implementation retains a global Pope-family measure
and adds a frontocentral variant. Kislov and colleagues used a 4-second
post-advertisement FFT and found that central `beta / alpha` over
`Cz/Pz/P3/P4` predicted population-wide banner efficiency [11]. The new Kislov
feature matches their channels and 16–24 Hz beta / 8–12 Hz alpha bands.

### What is supported, but not settled

**Engagement is task-dependent.** The Pope ratio is not a universal direct
readout of psychological engagement. Kamzanova and colleagues found that lower
alpha and a task-load index were more consistently sensitive than the
engagement index in a vigilance task [12]. A recent advertising study found
both `beta / alpha` and `beta / (alpha + theta)` associated with self-reported
ad ratings, particularly at frontal and central sites [13]. Therefore all
three engagement variables remain exploratory and should be interpreted
against behavioral ratings, not alone.

**Artifact thresholds are dataset-specific.** Autoreject was developed because
a useful peak-to-peak cutoff is data-specific and manual trial-and-error adds
researcher degrees of freedom [14]. COBIDAS gives examples of much smaller
ERP-style thresholds but does not prescribe one universal value [1].
Consequently, 1,050 µV is not a literature-standard neural purity threshold.
It is a participant-retention-driven gross-artifact boundary placed just above
one known observation. Its only defensible use is transparent versioning and
mandatory comparison with both the stricter 1,000 µV and permissive 1,500 µV
policies.

**Preprocessing choices affect downstream spectra.** Robbins and colleagues
found broadly similar structure but meaningful low-frequency and blink
residual differences across ICA and ASR pipelines [15]. This directly supports
reporting no-ICA and ICA-cleaned sensitivity results rather than claiming one
pipeline is uniquely correct.

### ICA decision and evidence

ICA can separate ocular and muscle sources without a dedicated clean reference
channel [16]. ICLabel provides probabilistic component classes trained on a
large common-average-referenced corpus [17]. Klug and Gramann show that
decomposition quality depends on channel count, movement, data quantity, and
high-pass filtering; 0.5 Hz was acceptable in their standard stationary
64-channel setting, while other settings benefited from higher cutoffs [18].

However, optimized ocular ICA work also shows that ordinary ICA settings can
leave residual eye artifacts and distort neural activity; validation against
eye tracking was needed to quantify both undercorrection and overcorrection
[19]. This study has 32 EEG channels but no EOG and no eye tracking.
`Fp1/Fp2` can act as ocular proxies, but they also contain neural signal.

Human laboratory feedback now prioritizes ICA with 99% PCA explained variance.
The defensible implementation policy is therefore:

1. preserve the current no-ICA branch as a mandatory sensitivity;
2. fit ICA on a separate copy prepared for decomposition, never overwrite
   Bronze or the no-ICA Silver path;
3. use `n_components=0.99` and report the algorithm, seed, filter used for
   fitting, rank, fitted component count, and rejected components per
   participant;
4. use `Fp1/Fp2`, component topographies, spectra, time courses, and ICLabel
   probabilities together rather than one automatic label;
5. visually inspect every proposed ocular component;
6. compare primary features and statistical conclusions with and without ICA;
7. select the final primary branch only if component selection is reproducible
   without removing plausible frontal neural activity.

HAPPE [20] and Automagic [21] demonstrate that standardized automated
pipelines can pair artifact correction with quantitative quality reports. They
support building a documented sensitivity branch, not assuming that their
population-specific defaults transfer unchanged to this experiment.

### Acquisition reference audit

Brain Products documentation confirms that actiCAP systems use physically
separate reference and ground electrodes, and that their locations are defined
by the cap/workspace configuration [22]. Laboratory feedback received on
2026-08-04 identifies `Cz` as online reference and `Fpz` as ground. `Fpz` is
absent from the 32 streamed EEG labels; `Cz` is present as a dynamic channel.
The latter makes the exact amplifier/export handling worth checking, but does
not justify replacing the laboratory report with the earlier `FCz` hypothesis.
Re-referencing offline changes the representation but not the historical
acquisition setup [1].

Required evidence, in descending order:

1. BrainVision Recorder workspace or exported channel configuration;
2. cap montage identifier and setup sheet;
3. contemporaneous lab protocol or photograph;
4. written confirmation from the operator or laboratory.

Current manuscript wording: “Laboratory records identify Cz as the online
reference and Fpz as ground. Data were rereferenced to the common average
offline. These physical roles were not encoded directly in the preserved XDF
metadata.” Do not claim `FCz` as fact.

### Pipeline-specific proof chain

The pipeline now checks evidence at multiple independent levels:

1. Bronze source files have SHA-256 identities and are never overwritten.
2. All analysis-required events are available for 18 laboratory recordings.
   Seventeen timelines are fully inside EEG; Subject 19's late
   `experiment_end` remains metadata-only and is not fabricated at the final
   EEG sample.
3. Leakage-resistant leave-one-marker-out validation hides each observed
   marker and prevents rematching it during reconstruction.
4. Marker fit residuals and ad-onset uncertainty are stored in generated data.
5. XDF values are converted from microvolts to MNE volts explicitly.
6. Channel names and montage requirements are checked before regional
   features.
7. Objective filtering, average-reference, and interpolation checks pass.
8. Rejected epochs remain in the epoch tables with explicit reasons.
9. Condition and ad validators check cohort size, key uniqueness, finite
   features, retention, and policy identity.
10. Engagement validation checks all three formulas independently.
11. Participant-level contrasts avoid epoch pseudoreplication.
12. `validate_preprocessing_soundness.py` aggregates these invariants into
    `src/project/logs/xdf/gold/validation/preprocessing_soundness.json`.

Current aggregate report status:
`machine_checks_passed_human_gates_pending`. All 20 machine checks pass.
Leave-one-marker-out validation covers 1,265 observed events with median
absolute error 0.000013 seconds, p95 0.000043 seconds, and maximum 0.000153
seconds. These values validate the participant clock projection for observed
markers; they do not replace the separately measured uncertainty of derived
visual ad onsets.

Passing these checks means the implementation is internally consistent and
reproducible. It does not prove that every retained sample is neural, that the
unknown online reference is irrelevant, or that an engagement ratio uniquely
measures engagement. Those remain interpretation and sensitivity constraints.

### Reuse audit of the earlier motor-imagery paper

The earlier work under `docs/overleaf/example-eeg/FinalReport_Template/` targets
supervised motor-imagery time-series classification, not condition-level
inference. Its preprocessing must not be copied wholesale.

Reusable material:

- `model.tex` defines EEG as a channels-by-samples multivariate time series,
  explains voltage relative to a reference, and emphasizes event
  synchronization.
- Its PREP motivation reinforces standardized preprocessing and explicit
  reporting [3].
- Its train-only fitting of data augmentation and CSP is a useful leakage
  principle for any future predictive EEG model: learned transforms must be
  estimated inside training folds, never on the complete cohort.
- Its discussion of frequency bands and temporal resolution is useful
  background for explaining why sampling rate, filter cutoffs, and epoch
  duration are linked.
- The orphan `water.tex` file, which is not included by `template.tex`,
  identifies low SNR, non-stationarity, and volume conduction as interpretation
  limits that also apply here.
- Its hardware and replication section is a useful structural precedent for
  documenting software versions and compute environments.

Material that must not transfer into the current primary pipeline:

- 1 Hz high-pass filtering, because that choice served motor-imagery decoding
  and differs from the frozen 0.5 Hz inferential filter.
- Laplacian rereferencing, because changing from common average would alter
  sensor-level FAA, regional power, and comparability with current validation.
- high-frequency data augmentation, train/test splitting, normalization,
  FB-CSP, CSP, overlapping classification windows, and model architectures;
  these optimize prediction and are not valid inferential preprocessing.
- dataset-specific channel, window, and class assumptions from the Kaya motor
  imagery dataset.

The source does not actually state or cite the Nyquist theorem. That concept
should be sourced from Shannon's sampling-theorem treatment [23] and COBIDAS
guidance rather than attributed to the old paper. The current recordings are
sampled at 500 Hz, so their Nyquist frequency is 250 Hz. The 40 Hz low-pass is
therefore 6.25 times below Nyquist. `validate_preprocessing_soundness.py` now
checks the actual sampling rates in generated epochs and fails if the low-pass
reaches Nyquist.

The old `biblio.bib` is useful as a discovery index, but several entries omit
DOIs, issue numbers, or complete page metadata. Citations must be verified
against publisher records before entering the thesis bibliography. PREP is
already represented by the verified reference [3]; EEGNet, Shallow ConvNet,
FBCSP, and Conformer references belong only in a future predictive-modeling
section.

### References

1. Pernet, C. R., et al. (2020). Issues and recommendations from the OHBM
   COBIDAS MEEG committee for reproducible EEG and MEG research. *Nature
   Neuroscience, 23*, 1473–1483.
   https://doi.org/10.1038/s41593-020-00709-0
2. Widmann, A., Schröger, E., & Maess, B. (2015). Digital filter design for
   electrophysiological data: A practical approach. *Journal of Neuroscience
   Methods, 250*, 34–46.
   https://doi.org/10.1016/j.jneumeth.2014.08.002
3. Bigdely-Shamlo, N., Mullen, T., Kothe, C., Su, K.-M., & Robbins, K. A.
   (2015). The PREP pipeline: standardized preprocessing for large-scale EEG
   analysis. *Frontiers in Neuroinformatics, 9*, 16.
   https://doi.org/10.3389/fninf.2015.00016
4. Gramfort, A., et al. (2013). MEG and EEG data analysis with MNE-Python.
   *Frontiers in Neuroscience, 7*, 267.
   https://doi.org/10.3389/fnins.2013.00267
5. Perrin, F., Pernier, J., Bertrand, O., & Echallier, J. F. (1989). Spherical
   splines for scalp potential and current density mapping.
   *Electroencephalography and Clinical Neurophysiology, 72*, 184–187.
   https://doi.org/10.1016/0013-4694(89)90180-6
6. Welch, P. D. (1967). The use of fast Fourier transform for the estimation
   of power spectra. *IEEE Transactions on Audio and Electroacoustics, 15*,
   70–73. https://doi.org/10.1109/TAU.1967.1161901
7. Gramfort, A., et al. (2014). MNE software for processing MEG and EEG data.
   *NeuroImage, 86*, 446–460.
   https://doi.org/10.1016/j.neuroimage.2013.10.027
8. Allen, J. J. B., Coan, J. A., & Nazarian, M. (2004). Issues and assumptions
   on the road from raw signals to metrics of frontal EEG asymmetry in emotion.
   *Biological Psychology, 67*, 183–218.
   https://doi.org/10.1016/j.biopsycho.2004.03.007
9. Ohme, R., Reykowska, D., Wiener, D., & Choromanska, A. (2010). Application
   of frontal EEG asymmetry to advertising research. *Journal of Economic
   Psychology, 31*, 785–793.
   https://doi.org/10.1016/j.joep.2010.03.008
10. Pope, A. T., Bogart, E. H., & Bartolome, D. S. (1995). Biocybernetic
    system evaluates indices of operator engagement in automated task.
    *Biological Psychology, 40*, 187–195.
    https://doi.org/10.1016/0301-0511(95)05116-3
11. Kislov, A., et al. (2023). Central EEG Beta/Alpha Ratio Predicts the
    Population-Wide Efficiency of Advertisements. *Brain Sciences, 13*, 57.
    https://doi.org/10.3390/brainsci13010057
12. Kamzanova, A. T., Matthews, G., Kustubayeva, A. M., & Jakupov, S. M.
    (2011). EEG indices to time-on-task effects and to a workload manipulation.
    https://doi.org/10.5281/zenodo.1071802
13. Mashrur, F. R., et al. (2025). Machine learning-based viewers’ preference
    prediction on social awareness advertisements using EEG. *Frontiers in
    Human Neuroscience, 19*, 1542574.
    https://doi.org/10.3389/fnhum.2025.1542574
14. Jas, M., et al. (2017). Autoreject: Automated artifact rejection for MEG
    and EEG data. *NeuroImage, 159*, 417–429.
    https://doi.org/10.1016/j.neuroimage.2017.06.030
15. Robbins, K. A., Touryan, J., Mullen, T., Kothe, C., &
    Bigdely-Shamlo, N. (2020). How sensitive are EEG results to preprocessing
    methods: A benchmarking study. *IEEE Transactions on Neural Systems and
    Rehabilitation Engineering, 28*, 1081–1090.
    https://doi.org/10.1109/TNSRE.2020.2980223
16. Jung, T.-P., et al. (2000). Removing electroencephalographic artifacts by
    blind source separation. *Psychophysiology, 37*, 163–178.
    https://doi.org/10.1111/1469-8986.3720163
17. Pion-Tonachini, L., Kreutz-Delgado, K., & Makeig, S. (2019). ICLabel: An
    automated electroencephalographic independent component classifier,
    dataset, and website. *NeuroImage, 198*, 181–197.
    https://doi.org/10.1016/j.neuroimage.2019.05.026
18. Klug, M., & Gramann, K. (2021). Identifying key factors for improving
    ICA-based decomposition of EEG data in mobile and stationary experiments.
    *European Journal of Neuroscience, 54*, 8406–8420.
    https://doi.org/10.1111/ejn.14992
19. Dimigen, O. (2020). Optimizing the ICA-based removal of ocular EEG
    artifacts from free viewing experiments. *NeuroImage, 207*, 116117.
    https://doi.org/10.1016/j.neuroimage.2019.116117
20. Gabard-Durnam, L. J., Mendez Leal, A. S., Wilkinson, C. L., & Levin,
    A. R. (2018). The Harvard Automated Processing Pipeline for
    Electroencephalography. *Frontiers in Neuroscience, 12*, 97.
    https://doi.org/10.3389/fnins.2018.00097
21. Pedroni, A., Bahreini, A., & Langer, N. (2019). Automagic: Standardized
    preprocessing of big EEG data. *NeuroImage, 200*, 460–473.
    https://doi.org/10.1016/j.neuroimage.2019.06.046
22. Brain Products GmbH. actiCAP operating instructions and cap montage
    resources. https://www.brainproducts.com/downloads/cap-montages/
23. Shannon, C. E. (1949). Communication in the presence of noise.
    *Proceedings of the IRE, 37*(1), 10–21.
    https://doi.org/10.1109/JRPROC.1949.232969

## Initial statistics

Scripts:

- `analysis/eeg/statistics/build_condition_contrasts.py`;
- `analysis/eeg/statistics/build_ad_contrasts.py`.

Outputs are under `analysis/eeg/statistics/outputs/`.

Inference uses participant-level condition or pre/post differences; epochs are
never treated as independent participants. Tables include paired t-tests,
Wilcoxon sensitivity tests, confidence intervals, Cohen's dz, and Holm
correction within each primary EEG-feature family.

The initial smoke analysis found no Holm-corrected primary effect for Fz theta
or posterior alpha. One inline-late Fz-theta ad response had raw `p≈0.046`, but
the Holm-adjusted value was `p≈0.183`; it is not corrected evidence of an
effect.

The added engagement measures also produce no Holm-corrected exploratory
effect. The smallest corrected condition value is global Pope-family
engagement for inline versus block (`p_Holm≈0.299`, `dz≈0.410`). The smallest
corrected ad-response value is frontocentral Pope-family engagement for block
early versus matched no-ad early (`p_Holm≈0.509`, `dz≈-0.378`). These are smoke
analysis results, not evidence that engagement is absent.

## Threshold sensitivity result

Both archived branches have been regenerated under versioned
`sensitivity/frozen_v1/` and `sensitivity/frozen_v2/` directories in:

- `src/project/logs/xdf/gold/features/`;
- `analysis/eeg/statistics/outputs/`.

The machine comparison is
`analysis/eeg/statistics/outputs/threshold_sensitivity_comparison.json` and
reports `status=pass`:

- no confirmatory Fz-theta or posterior-alpha direction changes;
- no confirmatory Holm-corrected conclusion changes;
- no condition-feature direction changes under either sensitivity;
- 1,000 µV retains 9,435/9,468 condition epochs and 107/108 ad pairs;
- 1,050 µV retains 9,438/9,468 condition epochs and 108/108 ad pairs;
- 1,500 µV retains 9,451/9,468 condition epochs and 108/108 ad pairs;
- three engagement measures keep the same direction in every comparison;
- the 1,500 µV ad dataset and all ad statistics are identical to 1,050 µV;
- relative to 1,000 µV, four early ad-control effects change direction:
  absolute beta and gamma for block early and inline early versus matched no-ad;
- those four features are secondary or exploratory, and none is
  Holm-corrected evidence under any policy.

The 1,050 µV policy differs from 1,000 µV by three retained sustained-condition
epochs and Subject 14's no-ad epoch. It differs from 1,500 µV by thirteen
condition epochs but no ad epochs. Subject 14's recovered early no-ad pair
matters for high-frequency exploratory summaries. It does not alter the initial
confirmatory conclusion, but the direction flips must be disclosed if beta or
gamma results are discussed.

## Remaining human inputs

1. Review and approve or reject the filtering and interpolation validation
   figures.
2. Implement and visually validate the 99%-variance ICA branch, then compare it
   against the current no-ICA sensitivity.
3. Keep all three engagement metrics; confirm only whether they remain
   exploratory for inferential claims.
4. Optionally verify the reported `Cz` online reference and `Fpz` ground against
   the acquisition workspace because `Cz` is exported as a dynamic channel.
5. Preserve and report the 1,000 µV `frozen_v1` and 1,500 µV `frozen_v2`
   sensitivities beside the selected 1,050 µV `frozen_v3` primary analysis.

## Diagram

The maintained pipeline diagram is:

`src/project/docs/eeg_pipeline/eeg_pipeline.png`

Its Gold stage now shows condition windows, ad and matched no-ad windows,
four-second feature extraction, and dataset validation. Analysis remains outside
Gold and contains separate condition and ad-response contrasts.
