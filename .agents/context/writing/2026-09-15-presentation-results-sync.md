# Presentation Results sync (15 September 2026)

Walter asked to update the defence deck from the current thesis
PDF (`docs/overleaf/thesis/_build/dissertation.pdf`, compiled
15 Sep 08:47) and the live Results chapter. The August deck still
had Goal 1 / combos as WIP.

Presentation Overleaf:
`https://git.overleaf.com/69b05745e534a779b65aae63`.

## What landed

- **Rehearsal cut applied.** Theoretical Work (2) is appendix
  (comments kept). Retrieval pipeline sits immediately before
  the system-architecture slide.
- **Behavioural Results** (thesis §7.2–7.3): planned forests,
  notice percentages, personality board. Numbers from
  `tab:beh-planned` and the 15 Sep PDF.
- **EEG figures** pointed at the current thesis PDFs. On-slide
  line: early−late posterior \(\alpha\) \(-0.22\) dB, Holm
  \(p=.0496\). Do not say Dataset A is all-null.
- **Combos:** `combos_trust_alpha.pdf`, \(\rho=.80\), Holm
  \(p=.0004\), \(n=18\).
- **Discussion:** effects matrix + four-beat read. Trajectories
  sentence is still his. Do not say the slow tilt is processing
  before the text.
- **Takeaways** filled from the abstract / `tab:rq-answers`.
  His `%` comments were not rewritten.

## Evening pass: landscape figures, RQ-mirrored skeleton

His note: the two-panel figures stacked vertically look wrong on a
4:3 slide; the skeleton after section 2 may change for flow.

- **Landscape deck variants.** The thesis draws page-width portrait
  figures; the deck now uses
  `images/results/beh_confirmatory_forests_wide.pdf` (composites left,
  cued recall top-right, Holm legend bottom-right) and
  `images/results/effects_matrix_wide.pdf` (matrix transposed: outcomes
  as columns, seven contrasts as rows). Both come from
  `images/results/make_deck_figures.py`, which imports the thesis
  plotting code (`make_thesis_figures._forest`,
  `make_effects_matrix.build_cells`) and reads the same frozen CSVs.
  Thesis figures untouched. Re-run the script, not the thesis one.
- **Results skeleton** mirrors the RQ summary slide, numbered 1–4:
  Experience (planned, who notices) → User → Unconscious (two markers,
  onset by format) → **1 + 3 Trust meets the scalp** (combos, moved up
  because it reuses the posterior \(\alpha\) just shown) → Trajectory
  (genre, transitions, descriptives, \(\tilde\delta\)). Trajectory
  closes on “the classifier sees conversational depth, not the
  advertisement”, which hands off to the Discussion claim.
- **Discussion:** “Every estimated effect on one grid” (wide matrix)
  then “What moved, what did not” in RQ order, with a one-line User
  beat added. His `%` spoken notes kept in place.
- Frame titles shortened to one line in the UniPD bar
  (“3 - Unconscious: the two markers”, not “The Unconscious: …”).
- Build recipe for the deck: copy the folder to `/tmp/deck_src`, then
  `docker run --rm -v /tmp/deck_src:/work -v /tmp/deck_build:/out -w
  /work texlive/texlive:latest bash -lc 'latexmk -f -pdf
  -interaction=nonstopmode -output-directory=/out main.tex'`.
  72 pages full; changed slides are 23–35.

## Do not

- Invent extra Likert cells or reopen Gold.
- Write “Wilcoxon Holm” or “approached significance”.
- Put Defs 1–6 back on the main path.
- Treat Katerina’s `analysis/behavioural/` as a source.
