# Defence save (31 August 2026)

Pokemon save. Live deck: Overleaf `docs/overleaf/presentation/`
(`https://git.overleaf.com/69b05745e534a779b65aae63`). Thesis due
17 September. Paper optional if it fights the thesis.

Prior deck notes: title page `2026-08-29-presentation-title-page.md`;
flow pass / rollback `d5d42ab` `2026-08-29-presentation-flow-pass.md`.
Do not rewrite Walter's `%` spoken comments. He is drafting the
Results EEG script himself (Overleaf `d931f86`): body copy on
`2 - EEG: confirmatory markers` and `2 - EEG: the format-specific
onset` is now comments; the Holm board is wider (`1.15\linewidth`).

Trajectory Results (31 August). Eight spoken frames, thesis
Results order, no “because of the ad” read (that stays
Discussion). (1) examples + \(\hat g_k,\delta_k\);
(2) descriptives table (\(N_{\mathrm{shift}}=2.45\), KW, fallback);
(3) heatmap, bare vs contextual;
(4) shift by position;
(5) crossing forest, \(D^{\delta}\), McNemar / GEE;
(6) depth versus ad;
(7) Def.\ 6 permutation (`s24_permutation.png`, copied in);
(8) late \(N_{\mathrm{shift}}\) (`s24_negative_control.png`).
His `%` comments stay on (1). 81% is the bare shift rate
0.817, not a published F1.

Results EEG slides stay **image-first**. No prose on the figures.
Forests: one line, the two thesis estimands only
(\(D^{A}_{i}\), \(D^{B}_{i}\)). Do **not** unpack \(\mathbf{w}\) or
\(c\) on the slide. Holm board: test names under the figure —
one-sample \(t\), Wilcoxon signed-rank, Holm within measure.

## What landed this save

Appendix **EEG recording** now opens on the five bands, then the
sixteen measures, then formulas/tiers, then the preprocessing figure.

- Trump-card image: `images/misc/waves.jpg` (already in the deck
  tree; was unused). Not `images/misc/eeg.png` (clinical
  spike-and-wave; wrong message). Size it with
  `width=\linewidth` inside `columns[onlytextwidth]`. Do not use
  `height=0.70\textheight`: the art is wider than tall and then
  overflows the left column onto the bullets.
- Analysis cuts, not the art's printed Hz:
  \(\delta\) 0.5–4, \(\theta\) 4–8, \(\alpha\) 8–13, \(\beta\) 13–30,
  \(\gamma\) 30–40 (`build_condition_features.py` `BANDS`; thesis
  appendix D). The figure is schematic; its labels run gamma to
  100 Hz and shift a few edges. The 40 Hz top is the band-pass.
- Interpretations match appendix D: awake \(\delta\) carries ocular
  activity; Fz \(\theta\) confirmatory; posterior \(\alpha\) down
  when gaze is on the display; \(\beta\) is the Pope/Kislov
  numerator; scalp \(\gamma\) overlaps EMG.

Do not put this slide in confirmatory Results. Do not promote a
band from the figure.

## How EEG statistical power is computed

Not an a-priori sample-size calc. It is a **post-hoc minimum
detectable effect** and **observed power** on the frozen
person-level difference scores \(D_i\), \(n=18\).

Runner: `analysis/eeg/analysis/run_paper_depth_audit.py`.
Outputs: `analysis/eeg/analysis/outputs/paper_depth/`
(`confirmatory_depth.csv`, `summary.json`).
Lock: `../data-analysis/eeg/2026-08-20-paper-depth-audit.md`.
Never write “approached significance”; use the MDE
(`2026-08-28-eeg-three-tier-framing.md`).

Paired \(t\), two-sided. Holm is approximated by the **first-step**
threshold \(\alpha=0.05/m\) (not the sequential remainder):

- Dataset A: \(m=3\) planned contrasts per measure \(\Rightarrow\alpha=0.0167\)
- Dataset B: \(m=4\) \(\Rightarrow\alpha=0.0125\)
- Uncorrected companion: \(\alpha=0.05\)

Cohen's \(d_z=\bar{D}/s_D\). The 80% MDE in \(d_z\) units is

\[
\mathrm{MDE}_{d_z}
=
\bigl(t_{1-\alpha/2,\,n-1}+t_{1-\beta,\,n-1}\bigr)/\sqrt{n},
\qquad \beta=0.20.
\]

In decibels: \(\mathrm{MDE}_{\mathrm{dB}}=\mathrm{MDE}_{d_z}\times s_D\).
Observed power is the two-sided noncentral-\(t\) tail at the
**estimated** \(d_z\) (nct noncentrality \(|d_z|\sqrt{n}\)).
\(n\) for 80% at a target \(\delta\) (0.5 or 1.0 dB) walks
\(n=4\ldots 400\) until \(\mathrm{MDE}_{d_z}(n)\times s_D\le\delta\).

At \(n=18\):

| Correction | \(\mathrm{MDE}_{d_z}\) (80%) |
|---|---|
| uncorrected | 0.70 |
| Holm within 3 (Dataset A) | 0.83 |
| Holm within 4 (Dataset B) | 0.86 |

## How much power the EEG arm actually has

**Dataset A** (equal-n \(k=37\) neighbourhood of onset). Dispersion
is still small. Holm-80% MDE is **0.22–0.44 dB** (Fz \(\theta\)
any-ad **0.24 dB**). Any-ad and format stay Holm-null. Early vs late
posterior \(\alpha\) is \(M=-0.22\) dB, Holm \(p=.050\) (Wilcoxon
Holm \(p=.062\)). Observed Holm power on the six confirmatory cells
is **3–52%**. The limits slide uses this range, not 0.20–0.35.

**Dataset B** (ad-locked post−pre). Dispersion is an order
larger (\(s_D\approx 2\)–\(4\) dB). Holm-80% MDE is
**1.7–3.7 dB**. No confirmatory 95% interval lies inside
\(\pm 1\) dB. Observed Holm power at the estimated \(d_z\) is
**1–26%**. Best confirmatory cell: implicit-late Fz \(\theta\),
\(d_z=-0.48\), observed Holm power **26%** (raw 49%). To have
80% Holm power for a 1 dB event-level effect at the observed
SDs you would need ~50–200 people; for 0.5 dB, hundreds
(several cells hit the walker cap of 400).

“Not significant” on Dataset B is not “no ad-locked effect.”
It is “we were not powered for a 1 dB shift after Holm.”
Dataset A *is* powered to rule out that size of sustained
condition shift.

The six explicit-early exploratory cells sit at
\(|d_z|=0.69\)–\(0.93\), i.e. at the Holm-within-4 bound
(\(\approx 0.87\)). That is the effect size this \(n\) can
see. Still exploratory; ICA-only; do not abstract as
confirmatory.

## Locks that still apply

- Confirmatory: 4 s + median + ICA, Fz \(\theta\) + posterior \(\alpha\).
- Holm within a measure, never across the sixteen.
- Channel-sets / exhaustive ad-local \(k\) / post-hoc pairwise:
  exploratory or sensitivity. Equal-n \(k=37\) is confirmatory
  Dataset A (shortest chat), not a \(k\) picked by \(p\).
- Do not overwrite `src/project/logs/xdf/silver/ica/candidate_v1/`.
- Results ≠ Discussion. Trajectories stay in this talk (thesis-only
  in the paper). Implicit ≠ subliminal. Dataset A/B.
- Do not invent Goal 1 Likert numbers.
