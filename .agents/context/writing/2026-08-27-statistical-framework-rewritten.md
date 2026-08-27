# Methods Statistical Framework rewritten (27 August 2026)

Thesis `chapters/models.tex`, `sec:methods:statistical-framework`.
Pushed to the thesis Overleaf as `041e1d5`, rebased onto Walter's live
edits (`f92719c`). Offline dump `/home/wtroi/tmp/thesis-tex-2026-08-25`
synced.

Walter's brief: kill the "as above" row, the table is incomplete, and
put a brief explanation of each test type **before** the table. Then:
"leaving no room for ambiguity in this section as it's one of the most
important mathematically and will be criticized a lot".

## Structure now (preserve it)

conventions itemize -> common shape of every confirmatory test, with
`eq:null-person-level` -> **Estimators** itemize -> Walter's table
sentence -> `tab:analysis-families` -> per-family paragraphs -> families
specified but not estimated -> software.

**To add an analysis later, add a table row and a sentence.** Do not add
another paragraph block per topic. That rule predates this pass
(`2026-08-21-results-vs-discussion-and-eeg-6-3-pushed.md`) and still holds.

## Every number in the section was checked against code

Not prose from memory. If any of these change, the section is wrong.

| Claim in Methods | Source |
|---|---|
| Dataset A weights `(¼,¼,¼,¼,−1)`, `(½,½,−½,−½,0)`, `(½,−½,½,−½,0)`; interaction `(1,−1,−1,1,0)` | `eeg/statistics/build_condition_contrasts.py` (`inline`=implicit, `block`=explicit) |
| Holm over 3 primary Dataset A / 4 Dataset B tests per measure | same file, `contrast_tier == "primary"` |
| t and Wilcoxon p adjusted as separate sets | same file, `adjusted_t` / `adjusted_w` |
| Holm adjusted p = `min{1, max_{j<=k}(m−j+1)p_(j)}` | `trajectories/analyse_trajectories.py:holm` |
| McNemar = exact **two-sided binomial** on b of b+c discordant | same file, `binomtest(only_treatment, discordant, 0.5)` |
| Permutation is **one-sided**, 20,000 draws, seed 11, 108 early-ad conversations | `classify_advertisements.py`, `p = (null >= observed).mean()` |
| Late family is **3** contrasts (late pooled, implicit late, explicit late) | `run_stages_2_4.py:late_tests` |
| GEE: binomial, exchangeable, clustered on `participant_id`, `delta ~ is_ad + C(task_id) + session_position` | `run_stages_2_4.py:gee_crossing` |
| Dataset B pre/post are **single 4 s epochs**, not medians | `dataset.tex` ("no median over many epochs"), `build_ad_features.py` |

The one-sided permutation forced the convention bullet to read
"two-sided **except where a test is declared one-sided below**". Do not
revert that to a flat "two-sided".

## Table rows added

Was 9 rows, now 14. Added: personality/demographics, free-text findings
and cued recall, behaviour x trajectory, trajectory x EEG, three-way.
Behaviour x EEG is no longer "to be declared": Holm is Fz theta and
posterior alpha x trust, credibility, manipulation. Positive control now
replicates the estimator with `D_i = y_write − y_read`.

Channel-set / Angela ROI is a **caption sentence** pointing at
`sec:app-eeg-channel-sets`, not a fifteenth row. EEG post-hoc (Sebastian)
is **not a row**; it is not a declared family until it is bounded.
Both locks unchanged: `2026-08-24-channel-set-sensitivity-not-confirmatory.md`,
`../data-analysis/2026-08-27-backlog-and-timeline.md`.

## Two things a reviewer would have caught

- Convention 1 says the participant is the inferential unit, but the GEE
  is fitted on transitions. The GEE bullet now says so explicitly and
  states that clustering is what keeps the standard errors at the person
  level. Do not delete that clause.
- Wilcoxon's null is symmetry about zero, not `E[D]=0`. The bullet says
  the two coincide when the distribution is symmetric.

## LaTeX notes

No local TeX toolchain (`pdflatex` absent), so the section was validated
structurally only: balanced math and braces, matched environments, 3
ampersands per table row, all `\cite` keys in `references.bib`, all
`\autoref` targets resolving. **A `>{\raggedright\arraybackslash}`
column spec was deliberately backed out** in favour of plain `p{}`,
because `\arraybackslash` depends on `array` being loaded and that could
not be verified by compiling. Other thesis tables use plain `p{}` too.

## Not touched

`chapters/results.tex` is Walter's live hand pass. It carries a typo
("mehtodology") and a bare `\ref{sec:methods:statistical-framework}` that
should be `\autoref`. Flagged, not edited.
