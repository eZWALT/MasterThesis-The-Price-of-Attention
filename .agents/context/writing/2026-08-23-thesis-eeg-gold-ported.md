# Thesis EEG Gold (preprocessing + Dataset A/B) ported from the paper

Date: 23 August 2026. Overleaf `docs/overleaf/thesis/`, local only.

Pulled thesis first (`67be29e`; remote only touched `models.tex`).
Filled `\subsection{EEG Data}` in `chapters/dataset.tex` by reusing
publication Method 5.6 (`EEG Preprocessing`), not 6.3 Results.

## What was written

- Four-zone mandate, Dataset A vs Dataset B questions, figure caption from
  the paper.
- `\subsubsection{Preprocessing}`: Bronze, Silver events, Silver
  signals (notch, 0.5–40 Hz, average ref, spline, FastICA), shared
  4 s Welch measurement, 1{,}050 µV disclosure.
- `\subsubsection{Condition Level}`: Dataset A, \(Y_A\in\mathbb{R}^{18\times 5\times 16}\),
  median, 9{,}449 / 9{,}468.
- `\subsubsection{Advertisement Level}`: Dataset B, visibility \(t=0\),
  \(Y_B\in\mathbb{R}^{18\times 6\times 16}\), 30/36 implicit onsets
  derived, 216/216 retained.

Left for Methods: the full 5.7 4 s justification, \(D_i\) contrasts,
Holm. No Results numbers in Dataset.

Copied `smulders2018log` and `pernet2020cobidas` into
`thesis/references.bib` (`lopezcardona2026vlfeedbackeeg` was already
there).

Do **not** push until Walter approves.
