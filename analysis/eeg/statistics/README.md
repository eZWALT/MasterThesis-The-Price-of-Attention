# Statistical analysis

Condition comparisons, multimodal models, sensitivity analyses, and publication
outputs. Statistical inference is intentionally outside the Gold data layer.

## Initial condition contrasts

```bash
python analysis/eeg/statistics/build_condition_contrasts.py
python analysis/eeg/statistics/build_ad_contrasts.py
```

The script treats participants, not epochs, as the replication unit. It emits
condition descriptives, participant-level contrast scores, paired t-tests,
Wilcoxon sensitivity tests, confidence intervals, effect sizes, and Holm
correction across the three primary contrasts per EEG feature.

Primary regional features are Fz theta and posterior alpha. FAA, global band
power, relative power, and the three engagement ratios remain secondary or
exploratory. Baseline-referenced descriptives are emitted separately, but
condition-to-condition tests use condition medians because subtracting the same
participant baseline cancels algebraically from every paired contrast.

Outputs are written to `analysis/eeg/statistics/outputs/`.

The ad-response script compares `post − pre` spectral changes against the
timing-matched no-ad reply for each ad condition. Four primary ad-versus-control
tests are Holm-corrected per feature. Factorial summaries are retained as
secondary, uncorrected contrasts.

The primary outputs use the 1,050 µV `frozen_v3` artifact policy. Run the
complete 1,000 µV `frozen_v1` and 1,500 µV `frozen_v2` feature and statistics
sensitivity branches with:

```bash
python analysis/eeg/preprocessing/run_threshold_sensitivity.py
```

The runner also writes
`analysis/eeg/statistics/outputs/threshold_sensitivity_comparison.json`, which
checks confirmatory effect directions and corrected conclusions across policy
versions.
