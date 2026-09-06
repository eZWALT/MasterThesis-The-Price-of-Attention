# Results readability + Holm lock (6 September)

Pushed thesis `f6b7ecf` (rebased onto Walter's `0fb0881`) and
paper `8ef03d4` the same day. That Overleaf edit kept the 7.2
split (post-condition vs post-experiment notice) and the
Methods multiplicity rewrite. It is **not** restored: equal-n
neighbourhood, “Wilcoxon Holm”, or the long \(\tilde{\delta}\)
tail. Parent context committed with the figure/table-first rule.

## Layout rule (standing)

In Results: one-sentence claim, then the figure or table, then only
what the visual cannot say. Do not restate every bar or CI.
Cursor rule: `.cursor/rules/results-figure-first.mdc`.

## Holm vs Wilcoxon

Holm is the paired \(t\) family only. Wilcoxon is raw. Never write
“Wilcoxon Holm \(p\)”. Timing posterior alpha: Holm \(p=.050\),
Wilcoxon \(p=.021\). Appendix \(p_W\) is raw Wilcoxon.
`fig:traj-depth` left-panel Holm is now the six paired \(t\) tests
(personal writing Holm \(p=.020\); relationships \(p=.411\)).

## Dataset A

Display name is **condition aggregation**. Not equal-n neighbourhood,
not condition state, not Path A. \(N_{ic}(37)\) is that set of 37
epochs. Gold table in the Dataset chapter says Dataset A / B.

## `fig:traj-position`

Navy bar is \(\delta_2\) in \(a^{\emptyset}\) (\(0.778\), \(n=54\)).
Orange is \(\delta^{(a)}_2\) (\(0.824\), \(n=108\)). Same estimand as
the \(+0.046\) confirmatory contrast. Plot:
`analysis/trajectories/describe_trajectories.py`.

## What landed in Ch 7 this pass

Slim roadmap. EEG opener cut. Forests and Holm board under the claim.
Four small tables (task-state, width, turn length, \(\tilde{\delta}^{(a)}\)
counts). BFI boxplots dropped. 7.1 no longer restates the demo figure
or the BFI table. \(\tilde{\delta}^{(a)}\) tail is two sentences after
the count table.

## Second pass, same day: thesis `d251c31`, paper `47dd10e`

Diagnostic list of 33 flaws (categories A–E) worked through except
what Walter excluded: 7.2 and 7.5 stay WIP, points 18/19 ignored,
33 (section title "Genre trajectories and intent theory") kept.

- Numbers: timing posterior \(\alpha\) is written **Holm
  \(p=.0496\)** in the thesis (to four decimals because it sits
  at the boundary; the board prints `.050`). Paper prose still
  says `.050`; harmonise when the paper is next touched.
- Vocabulary in Ch 7: any ad minus no ad / implicit minus explicit /
  early minus late (never "any-ad", "format", "timing"). Symbols
  everywhere: Fz \(\theta\), posterior \(\alpha\); figure labels
  now Greek too. Dataset B four cells named in the opener.
- `fig:traj-position`: tick labels name the \(\tau\) steps per bar;
  caption decodes all four bars incl. \(\tau_3\) at 0.889.
- `fig:traj-depth`: single panel (the \(\delta^{(a)}_2\) dot
  duplicated `tab:traj-crossing`); hollow markers = fallback
  classes; `s24_crossing_forest` dropped from the thesis (table
  carries it). `stages_2_4.md` regenerated so its depth table is
  Holm-on-\(t\) too.
- New `tab:traj-late` (late pooled, implicit late, explicit late
  on \(N_{\mathrm{shift}}\)); 156 distinct products verified from
  `advertisements.csv`; 9/83 vs 9/108 spelled out; 169 and 0.183
  decrypted; bootstrap named as bias-corrected on the pooled diff.
- Interpretive sentences (length explains part of the fallback
  rise; contextual labelling stickier) moved to
  `sec:disc-trajectories`. Positive-control windows (first 4 s
  after reply = reading, last 4 s before send = writing) now
  defined once in Methods; Results gives the one-line version.
- Floats `[H]` → `[!htb]`; one overfull paragraph title fixed;
  Ch 7 compiles with zero overfull boxes and zero undefined refs
  (built locally with the `texlive/texlive` docker image, XeLaTeX).
- All Ch 7 figures recut without suptitles/in-figure footnotes.
  Scripts: `plot_eeg_publication_suite.py` (forests),
  `plot_eeg_only_heatmaps.py` (board, `apa_p`),
  `sample_descriptives.py` (7.2 in wide), `eda_stage1.py`
  (examples), `describe_trajectories.py` (position),
  `run_stages_2_4.py` (depth). Paper `Figures/` got the shared three.

### Reviewer attack list

Started as a `%` block at the top of `chapters/introduction.tex`.
Entry 1: Kruskal–Wallis on 270 conversation rows vs the
participant-as-unit rule. Add there, do not delete until answered.

### Next iteration (not done)

- Holm board: put an up/down arrow (sign of \(M\)) in every cell so
  direction is readable without the appendix tables.
- `Dissertate.cls` breaks on TeX Live 2026: `caption` rejects
  `justification={justified,RaggedRight}` (line 95) and quotchap
  gives "Too many }'s" at line 392. Overleaf's current image
  tolerates both; will bite on the next image bump.
- Discussion `sec:disc-eeg` still has the observed-power paragraph
  (26 % power, fifty participants) that the 6 September MDE
  withdrawal says to drop. Not touched in this pass.

## Still open for impeccable Ch 7

Goal 1 freeze (7.2), then combos (7.5). Collapse empty subsections
until there is content. Personality moderation is not estimated;
Discussion must not read it as if it were. Do not rewrite `%` slides.
