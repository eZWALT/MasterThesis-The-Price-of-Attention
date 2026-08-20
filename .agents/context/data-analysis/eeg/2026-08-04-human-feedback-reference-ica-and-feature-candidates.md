# Human feedback: acquisition, ICA, and feature candidates

## Status

Human laboratory feedback received on 2026-08-04 resolves part of the
acquisition contract and changes the ICA work from optional discussion to a
required implementation and validation branch.

## Acquisition reference and ground

Laboratory report:

- `Fpz` was ground and had no displayed values;
- `Cz` was the online acquisition reference;
- common-average rereferencing was recommended offline.

The offline average reference remains the pipeline policy. Online reference and
offline rereferencing are different operations: average rereferencing does not
change the historical acquisition reference, but reduces downstream dependence
on that single reference.

Machine evidence adds one caveat. `Fpz` is absent from all XDF data streams, as
expected for ground. `Cz` is present among the 32 XDF channels and has dynamic
values. This can reflect amplifier or export handling, but is not the simple
zero-valued trace expected from a reference-only channel. Treat `Cz`/`Fpz` as
human-confirmed roles while recording that the BrainVision/actiCHamp workspace
would provide the strongest technical verification if it becomes available.

## ICA decision

`Fp1` and `Fp2` are frontal scalp EEG electrodes that are strongly sensitive to
blinks and eye movements. They can serve as ocular proxies, but they are not
dedicated bipolar EOG channels and also contain neural signal.

Laboratory practice:

- fit PCA/ICA while retaining 99% explained variance;
- this commonly yields approximately 10–20 components for these recordings.

The 99% rule determines decomposition dimensionality. It does not determine
which components should be removed. Component rejection must use convergent
evidence:

1. correlation with `Fp1/Fp2`;
2. frontal component topography;
3. blink-like time course;
4. low-frequency ocular spectrum;
5. visual review, with automated labels used only as supporting evidence.

Implementation contract:

- fit ICA on a separate processing branch; never overwrite Bronze or current
  no-ICA outputs;
- use `n_components=0.99`;
- record fitted, excluded, and retained component counts per participant;
- save component maps, spectra, proxy correlations, and exclusion reasons;
- regenerate every Gold feature and participant-level contrast under ICA;
- keep the current no-ICA result as a mandatory sensitivity;
- choose the final primary branch only after visual validation and
  ICA/no-ICA conclusion comparison.

Current datasets remain valid as the no-ICA branch. They are no longer the
automatically accepted final cleaning choice.

### Implemented candidate branch

Implemented on 2026-08-04:

- policy:
  `analysis/eeg/preprocessing/silver/signal/cleaning_policy_ica_candidate_v1.json`;
- cohort fitter:
  `analysis/eeg/preprocessing/silver/signal/fit_ica_cohort.py`;
- ICA implementation:
  `analysis/eeg/preprocessing/silver/signal/ica_cleaning.py`;
- full sensitivity runner:
  `analysis/eeg/preprocessing/run_ica_sensitivity.py`;
- conclusion comparison:
  `analysis/eeg/statistics/compare_ica_sensitivity.py`.

The implementation fits FastICA at 1–40 Hz with a fixed random seed after the
same channel repair and average rereference used by the no-ICA branch. It uses
`n_components=0.99`, fits on every fifth sample for computational efficiency,
and applies the fitted decomposition to the 0.5–40 Hz cleaned data.

Candidate exclusion is intentionally conservative and auditable. A component
must satisfy both:

1. maximum absolute source correlation with `Fp1` or `Fp2` of at least `0.35`;
2. mean absolute frontal topography weight at least `1.5` times the all-channel
   mean.

At most three qualifying components are removed. The thresholds are engineering
candidate rules, not literature-derived universal constants. They must not be
retuned after examining preferred statistical outcomes.

All 18 eligible recordings fit successfully. The 99% rule yielded 6–25
components, median 19.5. The automatic rule selected 27 components across 17
recordings; Subject 19 selected none. Per-recording JSON reports, component
maps, selection plots, spectra, and source/proxy traces are written under
`src/project/logs/xdf/silver/ica/candidate_v1/`.

Initial machine and agent visual checks show strongly frontal maps and
Fp1/Fp2-aligned source traces for the selected examples. This is evidence that
the branch executes as intended, but it is not final human signoff. In
particular, three-component removals in Subjects 11, 14, and 15 and the
six-component decomposition in Subject 17 deserve focused review. Subject 19's
no-removal decision should also be checked because frontal-looking components
did not pass the joint correlation/topography rule.

### First ICA versus no-ICA comparison

The full ICA branch completed for all 18 participants without changing primary
files. Machine validation passed for condition features, ad-response features,
and all three engagement indices.

Retention remained stable:

- condition epochs: `0.9968` no ICA versus `0.9980` ICA;
- ad epochs: `1.0000` in both branches;
- eligible ad-response pairs: `1.0000` in both branches.

Condition-level conclusions were comparatively stable:

- contrast mean-difference correlation: `0.906`;
- effect-direction agreement: `0.891`;
- corrected significance agreement: `1.000`;
- no corrected condition test changed significance status.

Ad-response conclusions were more sensitive:

- contrast mean-difference correlation: `0.716`;
- effect-direction agreement: `0.828`;
- corrected significance agreement: `0.906`;
- six corrected tests changed from non-significant without ICA to significant
  with ICA.

Five of those six changes concern the early explicit-ad versus matched early
no-ad contrast: alpha relative power, beta relative power, delta absolute and
relative power, and theta absolute power. The sixth concerns gamma relative
power for late implicit ads versus matched late no-ad replies. Low-frequency
delta/theta shifts are substantial in several ad contrasts.

This is not evidence that the new significant findings are automatically more
correct. Ocular activity is concentrated at low frequencies, so a real
ICA/no-ICA difference is expected; overly broad component removal can produce
the same pattern. Do not promote the ICA-only findings until component review,
especially Subjects 11, 14, and 15, is complete. The machine-readable details
are in
`analysis/eeg/statistics/outputs/ica_sensitivity_comparison.json`.

## Engagement decision

Human feedback supports retaining engagement as an important metric. Keep all
three implemented measures:

- global `beta / (alpha + theta)`;
- frontocentral `beta / (alpha + theta)`;
- central advertising-specific `beta16–24 / alpha8–12`.

They remain exploratory until linked to behavioral engagement, trust, recall,
or related ratings. “Keep the metric” does not by itself make one formula a
confirmatory endpoint.

## Candidate features from the supplied VLFEEDBACK-EEG appendix

The supplied appendix proposes the following feature family. These are
candidate additions, not yet frozen outputs.

### Ready or nearly ready

**Band power**

Already implemented with the same canonical edges:

- delta `0.5–4 Hz`;
- theta `4–8 Hz`;
- alpha `8–13 Hz`;
- beta `13–30 Hz`;
- gamma `30–40 Hz`.

**Total PSD**

The pipeline already integrates `0.5–40 Hz` power internally as the denominator
for relative power, but does not currently export total PSD as its own feature.
It can be exported with no new estimator decision.

**Mean absolute amplitude**

For samples \(x_i\):

\[
\mathrm{MAA}=\frac{1}{N}\sum_{i=1}^{N}|x_i|.
\]

This is easy to implement but highly sensitive to reference, ocular activity,
and residual artifacts. Use it first as a QC or exploratory magnitude feature,
not a direct neural-engagement measure.

### Requires an estimator contract

**Shannon entropy**

\[
H(X)=-\sum_i p(x_i)\log p(x_i).
\]

EEG amplitude is continuous, so `p(x_i)` cannot be interpreted as the
probability of every exact sample value. Freeze binning, symbolization, or a
differential-entropy estimator; log base and normalization must also be fixed.

**Conditional entropy**

\[
H(Y|X)=-\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)}.
\]

Define what `X` and `Y` mean before implementation. For temporal dependence, a
reasonable candidate is `X=x_t`, `Y=x_{t+lag}`, with prespecified lag,
discretization, and channel aggregation. Without these choices the formula is
not a reproducible EEG feature.

**Phase-locking value**

\[
\mathrm{PLV}_{ij}(f)=\left|\frac{1}{T}\sum_t
e^{j(\phi_i(t,f)-\phi_j(t,f))}\right|.
\]

Freeze the time-frequency transform, edge trimming, channel-pair set,
band aggregation, and minimum epoch duration. All-pair mean PLV is strongly
affected by volume conduction and common reference. Treat PLV as exploratory
and report a reference/ICA sensitivity; consider a lag-sensitive connectivity
measure such as wPLI as a robustness alternative.

### Alpha-asymmetry definition conflict

The supplied appendix defines:

\[
AA=P_\alpha(F3)-P_\alpha(F4).
\]

The current pipeline implements:

\[
\mathrm{FAA}=\ln P_\alpha(F4)-\ln P_\alpha(F3).
\]

These have opposite orientation and different scaling. Do not silently rename
one as the other. Preserve the current log-ratio FAA for continuity and, if the
appendix definition is needed, add a separately named exploratory feature such
as `alpha_asymmetry_raw_f3_minus_f4`.

## Recommended implementation order

1. Human-review the implemented ICA component packs and freeze or revise the
   candidate component choices.
2. Review the generated ICA/no-ICA spectral, FAA, engagement, and conclusion
   comparison.
3. Export total PSD and mean absolute amplitude.
4. Freeze entropy estimators before adding entropy features.
5. Add PLV only with explicit pair, transform, and volume-conduction controls.
6. Compare every new feature across ICA/no-ICA and 1,000/1,050/1,500 µV
   artifact policies before inferential promotion.
