# Thesis: EEG MDE in Methods / Results / Discussion (31 August 2026)

**Superseded 6 September.** Walter withdrew MDE from the thesis,
paper, and deck. Do not restore `eq:mde` or the Results MDE
paragraph. Historical numbers below only.

Walter asked to land the paper-depth MDE computation in the thesis
(Results as numbers; Discussion as the read). Runner:
`analysis/eeg/analysis/run_paper_depth_audit.py`. Lock:
`../data-analysis/eeg/2026-08-20-paper-depth-audit.md`.

## Split (do not invert)

- **Methods** `sec:methods:statistical-framework`: equation
  `\eqref{eq:mde}`. First-step Holm \(\alpha=0.05/m\). Observed
  power = two-sided nct tail. Not an a-priori calc.
- **Results** `sec:results-eeg`, paragraph *Minimum detectable
  effects*: the numbers only. No “precise null”, no “not absence”.
- **Discussion** `sec:disc-eeg` and Limitations: those two reads,
  now citing the dB MDEs and the \(n_{80}\) for 1 dB / 0.5 dB.

Never write “approached significance”.

## Numbers of record (\(n=18\))

| Family | \(m\) | \(\mathrm{MDE}_{d_z}\) | Holm-80% MDE (dB) | obs. Holm power |
|---|---|---|---|---|
| uncorrected | 1 | 0.70 | — | — |
| Dataset A confirmatory | 3 | 0.83 | 0.20–0.35 (Fz \(\theta\) any-ad 0.25) | 2–19% |
| Dataset B confirmatory | 4 | 0.86 | 1.7–3.7 | 1–26% |
| Dataset A 10 pairs | 10 | 0.97 | — | — |

Best B cell: implicit-late Fz \(\theta\), \(d_z=-0.48\), 26% Holm
(49% raw). \(n_{80}\) for 1 dB at observed B SDs: ~50–200; for
0.5 dB: hundreds. Global delta explicit-early \(d_z=0.88\) sits
on the Holm-within-4 bound.

The previous Results line used 0.87 for Holm-within-4 (same
quantity, rounded up). The runner is 0.8617; the thesis now
says 0.86 so `\eqref{eq:mde}` and the prose agree. Discussion
and Limitations were updated with it.

TOST at \(\delta=0.3\) dB stays an illustration, not a
pre-registered equivalence margin. Do not promote it into
this paragraph.
