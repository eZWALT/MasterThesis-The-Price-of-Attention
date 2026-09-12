# WP4 — Results Ch 7 prose pass (7.4 EEG, 7.5 trajectories, 7.6 combos, 7.7 summary)

**Date** 11 Sep 2026 · **Owner** `claude-opus-5-thinking-high` · **File touched**
`docs/overleaf/thesis/chapters/results.tex` only (7.4–7.7; 7.1–7.3 untouched).
No number, CI, \(p\), \(\rho\), \(d_z\) or count was changed anywhere. All 28
`% WALTER:` lines are still in place and in the same order (verified against
`HEAD`); nine short `% [AI: …]` notes were added directly under the comments they
answer, and nothing else was added as a comment. Diff: +112 / −79 lines.

## Per-comment log (line numbers as in the file WP4 received)

| WALTER line | What changed |
|---|---|
| 271 (EEG prose) | 7.4 opener now defines Dataset~A (condition aggregation, one score per condition window, ref `subsubsec:dataset:eeg-dataset-a`) and Dataset~B (onset-locked, 4 s post vs pre minus the matched \(a^{\emptyset}\) change, ref `subsubsec:dataset:eeg-dataset-b`) in one clause each; each of the four paragraphs gained one connective sentence saying what its artefact answers (control = does the recording register a within-conversation change; forests = the two estimands side by side; board = where a Holm cell falls among sixteen; pairwise = which single pair carries a difference). "as that table already names" now points at `tab:analysis-families`. |
| 299 | Rewritten as the reason for the estimand: whole-conversation counts are near their ceiling (2.45 of 3, 97.4 % shift at least once), so the confirmatory estimand is the single transition crossing the insertion, \(\delta^{(a)}_2\) on \(\tau_2\). Nothing dropped. |
| 301 | `fig:traj-position` caption cut to one line; the test pointer (`tab:traj-crossing`) moved into the following sentence. |
| 315 | Fallback classes now quoted, ``other'' and ``other obscene or illegal'', in both the prose and the `tab:traj-turn-length` caption. |
| 337 / 365 | 7.5 opener now declares the shorthand against Ch 3: \(\delta^{(a)}_k\) for \(\delta_k(a_k)\) `\eqref{eq:ad-associated-genre-shift}`, \(\tilde\delta^{(a)}_k\) for \(\tilde\delta_k(a_k)\) `\eqref{eq:genre-aligned-ad-shift}`, \(g^{(a)}\) for \(g_k(a_k)\); \(\tau_k\) and \(N_{\mathrm{shift}}\) carry `\eqref{eq:genre-shift}`, and \(D\), \(H\), \(R\), \(N_{ij}\) their own equations. **Open item, see below.** |
| 339 | "only a turn-2 advertisement is followed by a user utterance … \(u_5\) does not exist" is now said exactly once, in the \(\delta^{(a)}\) paragraph. Removed from the `fig:traj-examples` caption and from the late-control paragraph (which now says only that the late conditions have no \(\delta^{(a)}\) to score). |
| 343 | Before `tab:traj-crossing`: the four rows are named as the declared family of `tab:analysis-families` (early pooled vs \(a^{\emptyset}\), each early condition vs \(a^{\emptyset}\), implicit vs explicit early, Holm across four), with the reason no late row can appear. |
| 361 | "OR" and "GEE" dropped. The same model and estimate now read: a participant-clustered logistic model of the turn-2 rows, which lets a participant's five conversations be correlated, puts the odds of a shift with an early advertisement at 1.31 times the odds without (\(p=.51\)). `tab:results-checks` row renamed to match ("shift odds \(\times1.31\)"). |
| 388, 409 | Untouched (Walter's positive example and Walter's edited instrument-check paragraph). |
| 422 | Paragraph retitled "Sensitivity to the context fed to \(f_{\mathrm{genre}}\)"; the deployed window is described before use, with refs to `subsec:dataset:trajectories`, `sec:app-traj-labelling` and `sec:app-traj-sweep`. Cross-refs added through 7.5 (theory equations, `tab:analysis-families`, `sec:app-traj-descriptives`). |
| 433 | 7.6 opener keeps Walter's granularity sentence and makes the grain explicit: person-level \(D_i\) per planned contrast `\eqref{eq:person-contrast}`, not an epoch/turn/conversation; laboratory eighteen wherever EEG enters, \(N=54\) otherwise. Six lines. |
| 440, 468 | New paragraph in 7.6.1: at implicit − explicit, longer and slower conversations (reply latency, message length) go with a lower fast-band Pope engagement index, largest cell \(\rho=-.69\), Holm \(p=.35\); the process measures are mutually correlated and the indices share bands, so the cells repeat one pattern and none survives correction, with `\autoref{tab:results-checks}`. The duplicate sentence in the exploratory-sweep paragraph now points back to 7.6.1 instead of repeating the numbers. |
| 442 | `fig:combos-declared` caption cut to two lines (samples now live in the opener). |
| 446 | `fig:combos-declared` moved to just after the 7.6 opener, before `\subsection` 7.6.1; the first sentence of 7.6.1 now reads off panel (a). |
| 465 | Now says what is correlated: `fig:combos-trust-alpha`b screens the trust \(D_i\) against each of the sixteen onset-locked measures, Holm within sixteen. |
| 479 | The "whole-window EEG medians it is .27" clause deleted; only the deployed-context reversal and the onset-locked early score remain. |
| 486 | `\subsection{The three-way association}` and `\label{sec:results-combos-three-way}` deleted. Grain sentence → 7.6 opener; \(|\rho|\le.34\) and the partial \(\rho=.80\)/\(.83\) sentences → new short paragraph at the end of 7.6.1. The orphaned exploratory paragraph was retitled `\paragraph{Exploratory map across all three families.}` so its section scope is clear. |
| 500, 502 | Both summary tables: italic family labels with `\midrule` dividers (Behavioural / EEG / Trajectories / Associations — `tab:results-checks` had none before), column "Headline" → "Key estimate", every cell cut to one estimate + CI + Holm \(p\), captions ≤ 2 lines, `Key estimate` column widened to 0.375\linewidth. EEG rows in `tab:results-summary` reordered to the `tab:analysis-families` order (Dataset A, Dataset B, positive control, exhaustive pairwise) with the fourteen-measure row appended last, since Methods has no row for it. |
| global | `labelling(s)` → `context(s)` in all 7.4–7.7 prose, captions and table rows; `k=37` removed from the split-half row of `tab:results-checks`; no `composite` or `card` was present. |

## Labels and cross-references

- **Removed:** `sec:results-combos-three-way`. Its only reference in the thesis was
  the `tab:results-summary` row, now pointing at `sec:results-combos-behaviour-eeg`.
  A repo-wide `rg` over `docs/overleaf/thesis/**.tex` finds no other use;
  `discussion.tex` does **not** reference it (its three-way sentence at
  discussion.tex:167 is prose only, no `\ref`). `publication/` and `presentation/`
  do not reference it either.
- **New references used, all verified to resolve:** `subsubsec:dataset:eeg-dataset-a`,
  `subsubsec:dataset:eeg-dataset-b`, `subsec:dataset:trajectories`,
  `sec:app-traj-labelling`, `sec:app-traj-descriptives`, `sec:app-traj-sweep`,
  `tab:analysis-families`, `eq:person-contrast`, `eq:genre-diversity`,
  `eq:genre-entropy`, `eq:genre-persistence`, `eq:genre-transition-count`.
- 7.5 no longer cites the chapter-level `sec:app-trajectories`; it cites the three
  App F sections instead. `tab:results-checks` rows follow the same change.
- Both tables re-checked: 6 columns, 5 ampersands on every body row, group rows
  are `\multicolumn{6}`. No LaTeX toolchain is installed here, so this is a manual
  structural check, not a compile.

## Open items for the orchestrator

1. **Notation congruence (WALTER 337/365) is only half-closed.** Ch 3 writes
   \(\delta_k(a_k)\), \(\tilde\delta_k(a_k)\), \(g_k(a_k)\); Methods (8 hits),
   Results (19), App F (9), dataset.tex (5), discussion.tex (4) and conclusion.tex
   (1) all write \(\delta^{(a)}_k\) / \(g^{(a)}\). Results now declares the
   shorthand against the defining equations, which removes the ambiguity, but one
   symbol should win thesis-wide. Cheapest fix: add the same one-clause shorthand
   line to `theory.tex` after Definition 6. That edit is outside WP4's file.
2. **`sec:app-traj-labelling`** is now the anchor Results points at for the two
   contexts, while the section is still titled "The two readings of Definition 1".
   If WP12 renames the label to `…-contexts`, the four references in 7.5 and
   `tab:results-checks` must move with it.
3. **Bold Holm-significant rows** was not applied to `tab:results-summary` /
   `tab:results-checks`: these are family inventories where most rows carry at
   least one hit, so bolding would mark almost everything. The rule is applied in
   the test tables (`tab:beh-planned`). Flagging in case Walter wants it anyway.
4. **`% REVIEWER ATTACK SURFACE`** comment above the Kruskal–Wallis paragraph
   (7.5) is an agent-instruction comment and belongs to WP10 hygiene; left alone.
5. The "21 cells" figure used in `discussion.tex:167` for the process × engagement
   pattern is not in Results and was not imported: only \(\rho=-.69\) and
   Holm \(p=.35\), which are in the frozen text, are quoted.
