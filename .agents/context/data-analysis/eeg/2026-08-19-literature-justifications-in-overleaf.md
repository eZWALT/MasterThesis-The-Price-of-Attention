# EEG literature justifications parked in Overleaf

Date: 19 August 2026

## What happened

A methodology check against advertising EEG, oscillation-scaling papers, and
COBIDAS concluded that the current Gold collapse (log each 4 s epoch, then
median) and person-level Holm tests are valid. They are a robust variant of
Smulders, not a defect relative to Kislov’s mean-of-linear-power.

Walter asked to park the reusable justifications as **comments** in the
publication Overleaf, with a short bibliography, not a citation soup, and
without rewriting the visible Method yet.

**Update 20 August:** the visible `EEG Epoching` subsection is now
drafted in the local publication mirror (Dataset A tiles, Dataset B locked
windows, 4~s rationale, both sensitivity cells). Comments under that
heading were replaced. Preprocessing / Measures / Stats comments remain.
Overleaf was **not** committed or pushed.

## Where it lives

Publication mirror (pull before further edits):

- comments under `EEG Preprocessing`, `EEG Epoching`, `EEG Measures`, and
  `Statistical Analysis` in `docs/overleaf/publication/main.tex`
- four new bib keys in `docs/overleaf/publication/bibliography.bib`, after
  `kislov2023central`

## Cite set (keep it small)

Already in the bib, now pointed from comments:

- `kislov2023central` — 4 s window and central β/α formula; **different**
  estimand (market forecast, mean of linear power)
- `ohme2010application` — FAA used on advertisements

Added:

- `smulders2018log` — log each epoch before collapsing
- `allen2004asymmetry` — FAA = \(\ln\alpha_{F4}-\ln\alpha_{F3}\)
- `pernet2020cobidas` — participant as \(n\); induced vs evoked
- `holm1979simple` — Holm family on the planned \(D_p\)

Do not add Donoghue, Pope, Kamzanova, Welch 1967, Keil, or Melman to the
paper unless a sentence truly needs them. They remain in the 3 August EEG
audit and the 19 August literature canvas if an appendix wants them.

## Inferential objects the comments now state

- \(Y_A\): 18 × 5 × 16 medians of epoch dB (baseline row dropped for tests)
- \(Y_B\): 18 × 6 × 16 post−pre
- \(D\): planned contrasts of those rows, not one vector per condition
- Dataset A primary \(D\): any-ad, implicit vs explicit, early vs late
- Dataset B primary \(D\): each ad minus the timing-matched \(a^{\emptyset}\) reply
- \(H_0:\mathbb{E}[D]=0\) on 18 people; \(t\) + Wilcoxon; Holm inside that family

IQR and baseline-delta are stored extras, not a third tensor axis.

## Other flags in those comments

- ICA is primary as of 2026-08-19; the visible preprocessing prose still
  says ICA was not applied and must be rewritten.
- Delete the leftover ERP epoching / P1–P3 template.
- Engagement and Kislov stay exploratory.
- Optional later code (not requested): mean-of-epoch-dB sensitivity from
  the existing epoch CSV. Do not replace the median.

## Related

- Gold pedagogy: `2026-08-19-gold-paths-shapes-and-ica.md`
- ICA primary: `2026-08-19-ica-primary-and-visual-signoff.md`
- Earlier methods audit: `2026-08-03-eeg-analysis-ready-datasets-and-open-decisions.md`
- Scan-able comparison: `~/.cursor/projects/home-wtroi-MasterThesis-RAG-RecSys/canvases/eeg-literature-sanity-check.canvas.tsx`
