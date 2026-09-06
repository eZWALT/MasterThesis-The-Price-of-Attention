# Condition aggregation + `fig:traj-position` (6 September)

Superseded for the live layout/Holm lock by
`2026-09-06-results-readability.md` (pushed later the same day).
Kept for the naming and position-bar audit trail.

## Dataset A display name

Call the confirmatory Dataset A cell **condition aggregation**.
Do not write “equal-n neighbourhood of onset” or “condition state”.

The estimator did not change: median of the 37 retained 4 s tiles
whose midpoints lie nearest that condition’s visual onset
(\(k=37\) is the shortest chat, not a \(k\) picked by \(p\)).
Gold `condition_features.csv` still stores the whole-window median.
Dataset B is unchanged.

Applied in thesis Methods / Results / Discussion, paper Methods /
Results / Discussion, and the analysis-family tables. Presentation
`%` spoken comments were left alone.

## `fig:traj-position`

Plot code: `analysis/trajectories/describe_trajectories.py`
`plot_shift_by_position`. Groups Gold `transitions.csv` by
`position` on `delta`.

| bar | `position` | what it is | rate | \(n\) |
| --- | --- | --- | ---: | ---: |
| navy | `no_ad` | \(\delta_1,\delta_2,\delta_3\) in \(a^{\emptyset}\) | 0.827 | 162 |
| navy | `pre_ad` | every step before an ad (early \(k=1\) + all late \(k\)) | 0.794 | 432 |
| orange | `crosses_ad` | \(\delta^{(a)}_2\) only (early ads) | 0.824 | 108 |
| navy | `post_ad` | \(\delta_3\) after a turn-2 ad | 0.889 | 108 |

The caption was already right. The Results sentence was not: it
treated 0.827 as \(\Pr(\delta_2=1)\) in \(a^{\emptyset}\). That
same-step rate is **0.778** (\(n=54\); 42/54). Early-pooled
\(\delta^{(a)}_2\) minus that control is \(+0.046\), which is the
confirmatory contrast later in the same section.

The figure was not rebuilt. The sentence now reports both
estimands. Caption left as written.

## Results readability pass (same day, later)

Local only. Three-row \(\tilde{\delta}^{(a)}\) table; writing-versus-reading
table; width-sensitivity table; turn-length/fallback table.
BFI boxplots dropped; table stays. `fig:traj-position` navy bar is
\(\delta_2\) in \(a^{\emptyset}\) (\(0.778\), \(n=54\)). Dataset A
display name is condition aggregation; Gold table no longer says
Path A/B. \(N_{ic}(37)\) is defined as that set of 37 epochs.

## Wilcoxon vs Holm (same day)

Holm is the paired \(t\) family only. Wilcoxon is a raw
sensitivity check on the same \(D_i\). Never write
“Wilcoxon Holm \(p\)”. Timing posterior alpha is Holm
\(p=.050\) (\(t\)) and Wilcoxon \(p=.021\) (uncorrected).
Appendix \(p_W\) columns are now the raw Wilcoxon values.
Results layout: slim roadmap at the chapter head; EEG
opener cut; forests and Holm board sit under the claim;
body does not restate every CI. Local only.
