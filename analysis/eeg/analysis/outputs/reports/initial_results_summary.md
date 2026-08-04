# Initial publication analysis summary

## Scope

This report summarizes the frozen `frozen_v3` EEG datasets for 18 laboratory
participants. It is an initial analysis scaffold, not a final claim of
neurophysiological or causal evidence.

## Confirmatory results

No primary sustained-condition or ad-response contrast survives its
feature-specific Holm family at α=0.05.

The smallest corrected sustained-condition result is
`early_vs_late` for `posterior_alpha_power_db_uv2`
(`mean=-0.089`,
`95% CI [-0.201, 0.023]`,
`dz=-0.395`,
`p_Holm=0.337`,
`p_global_Holm=0.674`).

The smallest corrected ad-response result is
`inline_late_vs_no_ad_late` for `fz_theta_power_db_uv2`
(`mean=-1.992`,
`95% CI [-3.942, -0.042]`,
`dz=-0.508`,
`p_Holm=0.183`,
`p_global_Holm=0.366`).

## Robustness

The 1,000 and 1,500 µV sensitivity branches preserve all confirmatory effect
directions and corrected conclusions relative to the 1,050 µV primary policy.
The minimum leave-one-participant-out sign stability across primary-feature
diagnostics is 55.6%.

## Interpretation boundaries

- The sample is small (`n=18`), so confidence intervals and participant-level
  distributions should lead interpretation.
- Laboratory feedback identifies `Cz` as the online reference and `Fpz` as
  ground; the XDF does not encode those physical roles directly.
- Current feature tables are no-ICA. An ICA branch retaining 99% PCA variance
  and using `Fp1/Fp2` as ocular proxies must be visually validated before the
  final primary policy is chosen.
- Baseline eye state was uncontrolled and is excluded from confirmatory tests.
- Engagement ratios, FAA, global bands, and uncorrected interactions are
  secondary or exploratory.
- The era-aware read-versus-write positive control is not yet implemented;
  null condition results therefore do not establish universal pipeline
  sensitivity.
- A non-significant result is not evidence of absence; report compatible effect
  ranges and study power limitations.

## Automated quality review

20 of 20 analysis gates pass.
