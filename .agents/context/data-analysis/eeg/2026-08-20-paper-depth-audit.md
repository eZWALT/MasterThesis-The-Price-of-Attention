# Paper-depth EEG audit

Date: 20 August 2026
Runner: `analysis/eeg/analysis/run_paper_depth_audit.py`
Outputs: `analysis/eeg/analysis/outputs/paper_depth/`
Canvas: `paper-eeg-depth-audit.canvas.tsx`

This is the honesty layer on top of the confirmatory lock. It does
**not** change primary (4 s · median · ICA · \(n=18\)). It does not
rebuild Gold. It does not overwrite ICA.

## Guarantee

I independently recomputed every confirmatory paired \(t\) from the
person-level score CSVs. All 14 means and raw \(p\) values match the
frozen tables. Path A Holm hits are 0/6 on the two confirmatory
features and **0/48** across all 16 features. Path B confirmatory Holm
hits are 0/8.

What I still cannot do: Goal 1 scoring, C1, personality, genre. Those
are blocked on behavioural Gold, not on more EEG science.

## New numbers the paper can use

### Path A is compatible with a 0.3 dB bound

All six confirmatory Path A 95% \(t\) intervals lie inside \(\pm 0.3\)
dB. That bound is also the approximate 80% Holm MDE for Fz theta
any-ad (MDE \(=0.25\) dB). A post-hoc TOST at \(\delta=0.3\) dB
rejects for every Path A confirmatory cell (largest TOST \(p=0.018\),
any-ad posterior alpha). Label the bound as **illustration**, not a
pre-registered equivalence margin.

Observed Path A effects are 7–11 people one way, 7–12 the other. LOO
sign stability is 94–100%. Subject 14 is the max influencer on any-ad
alpha (shift 0.049 dB); dropping them does not flip a confirmatory
sign.

### Path B cannot rule out a 1 dB shift

No confirmatory Path B 95% interval lies inside \(\pm 1\) dB. Holm-80%
MDEs are 1.7–3.7 dB. To have 80% Holm power for a 1 dB event-level
effect you would need ~50–200 people at the observed SDs; for 0.5 dB,
hundreds. Observed power at the estimated \(d_z\) is 3–26%. That is
why “not significant” is not “no ad-locked effect.”

### Bootstrap vs \(t\) — do not promote

Percentile bootstrap CIs exclude zero for two Path B cells whose \(t\)
CIs include zero:

| Cell | \(t\) 95% CI | Bootstrap 95% CI |
|---|---|---|
| implicit late · Fz theta | \([-2.80, +0.04]\) | \([-2.63, -0.09]\) |
| explicit late · posterior alpha | \([-2.70, +0.12]\) | \([-2.63, -0.06]\) |

Primary remains paired \(t\) + Holm. Wilcoxon Holm is 0.24 and 0.47.
LOO sign stays negative. Subject 10 is the max influencer on both
leaning late cells. Still Holm-null. Still not a Results star.

Path A early−late Fz theta is non-normal (Shapiro \(p=0.00035\));
Wilcoxon Holm \(=0.50\). Keep the \(t\) interval; mention Wilcoxon.

### Exploratory ICA-only lock (do not abstract)

Exactly six Path B Holm hits exist at 4 s outside the confirmatory
features. All six are ICA-only (no-ICA Holm \(\ge 0.07\)). Five are
the same cell: **explicit early** spectral tilt (more global theta /
delta / relative delta; less relative alpha / beta). The sixth is
implicit-late relative gamma. Engagement ratios (Pope, Kislov, FAA)
are Holm-null. These stay exploratory. They are why ICA was not
chosen from \(p\).

## What this adds to the figure / prose lock

- Methods / Statistical Analysis: person is \(n\); Holm per feature;
  MDE Path A \(\approx 0.25\) dB vs Path B \(\approx 1.7\)–\(3.7\) dB.
- Results Path A: CIs inside \(\pm 0.3\) dB. Optional appendix TOST
  illustration.
- Results Path B: imprecise; bootstrap disagreement in one sentence
  if a reviewer asks about the late leans.
- Appendix: the six ICA-only hits as a table, labelled ICA-only.
- Still no C1 figure.

Stale “read-vs-write not implemented” lines in
`analysis/eeg/analysis/README.md` and
`outputs/reports/initial_results_summary.md` were corrected.

## Related

- Figure cut: `2026-08-20-paper-figures-and-narrative.md`
- CIs: `2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`
- Stop line: `2026-08-19-eeg-only-analyses-complete.md`
