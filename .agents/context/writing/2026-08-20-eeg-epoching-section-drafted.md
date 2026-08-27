# EEG Epoching drafted in publication Method

Date: 20 August 2026

Visible prose lives under `\subsection{EEG Epoching}` (Method 5.7).
Tightened 20 August after 5.6 Preprocessing was rewritten: no Gold
rebuild, no ``p-value search''. Epoching is induced-vs-ERP, Dataset B
\(t=0\), why 4~s, and the width grid. 5.6 was not edited.

Pulled first (`b3a6869`, Walter's sample-figure caption + `\raggedbottom`).
Pushed as `cf48a14` on 20 August after he asked. Cite keys
`smulders2018log`, `pernet2020cobidas`, `allen2004asymmetry`,
`holm1979simple` went up with it (`kislov2023central` was already in
the bib). Revert on Overleaf if the prose is wrong.

## What the subsection now states

- Induced 4~s spectra, not ERP (onset LOO p95 0.23~s explicit / 0.43~s
  implicit).
- Dataset A: non-overlapping 4~s tiles; leftover dropped; 1{,}050 µV /
  near-flat; ≥5 epochs and ≥80\% retained; median of epoch dB →
  \(Y_A\in\mathbb{R}^{18\times 5\times 16}\). 9{,}468 / 9{,}449
  retained under ICA.
- Dataset B: visual-onset \(t=0\); pre \([t-4,t)\), post \([t,t+4)\);
  window = epoch; 216/216 retained →
  \(Y_B\in\mathbb{R}^{18\times 6\times 16}\). Reconstruction lags and
  30/36 implicit derived onsets are in the prose.
- 4~s frozen before the grid (Welch, leftover vs condition, chat
  timeline ~53/~79~s, Kislov width not Kislov estimand).
- Sensitivity 2/8/16/32~s: Dataset A null everywhere; both Dataset B cells
  with CIs; Holm not across the grid; neither cell unfreezes 4~s.
- Mean-of-epoch-dB 0/48; median stays primary.

## Still TO-START in Method

EEG Measures (ERP list). Statistical Analysis (XXXXX). EEG
Preprocessing still says ICA was not applied.

## Related

- Numbers: `../data-analysis/eeg/2026-08-20-paper-4s-primary-and-epoch-sensitivity.md`
- Onset: `../data-analysis/eeg/2026-08-20-what-path-b-onset-is.md`
- Writing rule: pull → show → apply → push only when asked.
