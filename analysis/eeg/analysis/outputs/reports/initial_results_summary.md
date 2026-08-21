# Initial publication analysis summary

## Scope

This report summarizes the frozen `frozen_v3` EEG datasets for 18 laboratory
participants. It is an initial analysis scaffold, not a final claim of
neurophysiological or causal evidence.

## Confirmatory results

No primary sustained-condition or ad-response contrast survives its
feature-specific Holm family at α=0.05.

The smallest corrected sustained-condition result is
`early_vs_late` for `fz_theta_power_db_uv2`
(`mean=-0.113`,
`95% CI [-0.258, 0.032]`,
`dz=-0.387`,
`p_Holm=0.358`,
`p_global_Holm=0.716`).

The smallest corrected ad-response result is
`inline_late_vs_no_ad_late` for `fz_theta_power_db_uv2`
(`mean=-1.383`,
`95% CI [-2.803, 0.037]`,
`dz=-0.484`,
`p_Holm=0.223`,
`p_global_Holm=0.445`).

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
- Current feature tables apply the approved 99%-variance ICA branch
  (`Fp1/Fp2` ocular proxies, at most three components). No-ICA remains a
  mandatory sensitivity. Artifact-threshold 1,000/1,500 µV branches were
  computed on the no-ICA 1,050 µV tables and have not been rebuilt under ICA.
- Baseline eye state was uncontrolled and is excluded from confirmatory tests.
- Engagement ratios, FAA, global bands, and uncorrected interactions are
  secondary or exploratory.
- The era-aware read-versus-write positive control is implemented:
  writing − reading Fz theta \(M=+0.60\) dB, Holm \(p=0.007\),
  \(d_z=0.80\). Pipeline check only; not an ad finding. See
  `2026-08-19-read-vs-write-what-it-proved.md` and
  `outputs/paper_depth/`.
- A non-significant result is not evidence of absence; report compatible effect
  ranges and study power limitations.

## Automated quality review

20 of 20 analysis gates pass.
