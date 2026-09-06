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

## Still open for impeccable Ch 7

Goal 1 freeze (7.2), then combos (7.5). Collapse empty subsections
until there is content. Personality moderation is not estimated;
Discussion must not read it as if it were. Do not rewrite `%` slides.
