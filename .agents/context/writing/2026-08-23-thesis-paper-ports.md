# Thesis: paper low-hanging ports

Date: 23 August 2026. Overleaf `docs/overleaf/thesis/`.

Pulled first (thesis `67be29e`, paper `3efb3e2`). Placement: EEG
construction in Dataset; design/workflow/stats in Methods; theory as
its own chapter after Related Work.

Pushed to Overleaf after Walter asked (23 Aug evening).

## Where it went

| Paper | Thesis |
|---|---|
| Theoretical Foundations (Defs 1–6, taxonomy, \(\Pi/\pi\)) | **Chapter** `chapters/theory.tex` (`chp:theory`; alias `sec:theoretical-foundations`). \(f_{\mathrm{genre}}\) kept. |
| EEG Acquisition + montage | Dataset, `\subsubsection{Acquisition}` |
| EEG 5.7 induced / onset jitter / why 4 s / 2 s vs 8 s | Dataset, `\subsubsection{Epoching}` (moved out of Methods 23 Aug) |
| Lab/crowd design, IVs, DVs, flow + UI figures | Methods, Study Design |
| Statistical Analysis (EEG \(D_i\), Holm, families) | Methods, Statistical Framework |
| Sample 6.1 + EEG Results 6.3 | Results (numbers only; no 7.3) |
| EEG appendix (QC, 16 measures, confirmatory tables) | Appendix D |
| Future Work | Conclusion |

Not ported: Discussion 7.3, behavioural results, trajectory Results
numbers, paper Introduction, remaining RQs (1–11). Insertion-policy
model dropped 24 August (not a port target).

Figures: `figures/ui/` and `figures/results/`. Bib:
`rainie2025llmusers`, `holm1979simple`, `gramfort2013mne`,
`allen2004asymmetry`.
