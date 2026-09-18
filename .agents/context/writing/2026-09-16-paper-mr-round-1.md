# Paper MR round 1 applied (16 Sep)

Paper Overleaf `8d21a0b` (MR asks) + `19c2b95` (coherence pass), both
on top of Walter's live edits. One commit per round so he can revert.

## What the round changed

- Every `% WALTER:` from abstract through Conclusion applied and flipped
  to `% WALTER+:`. Left open on purpose: his LGTM / "near perfect" /
  "theory may fall if space" / MR-header notes.
- Where he asked a question, one `% [AI: …]` line under the flipped tag
  (keywords rationale, age not tested, forest vs heatmap, section name,
  what survived from the old paper, taxonomy fact-check result).
- Overleaf layout collision fixed earlier the same day: Gold assets live
  only under `Figures/results/` (capital F). Never recreate `figures/`.
- Macros in `main.tex`: `\Rev{}` (green review marks) and `\Bf{}`
  (`\useBoldClaims` 1/0) for the bold claims in Discussion.
- Structure now: RQs as `tab:rqs` (Intro); `tab:analysis-families` in
  Methods 4.5 with interaction / secondary / logged / localisation /
  pairwise / exploratory-EEG / sensitivity rows (App. C copy removed);
  Results 5.5 and Discussion 6.3 both titled **Behaviour–EEG
  associations**; Conclusion split into 7.1 Conclusion + 7.2 Future work.
- Figures: localisation forest + notice percentages → App. C; EEG
  confirmatory forest → App. D under the per-cell tables; Holm board
  `fig:eeg-holm-board` is the one EEG visual in the body.
- k=37 is now written as "standardised to the shortest eligible
  conversation"; the number stays only in the pipeline appendix.
- Thesis footnote on p.1 points to
  `https://ezwalt.github.io/harness/advertisement/advertisement-in-llms-1/`.

## Fact-check of record

Taxonomy table, instance equations, and held-fixed list are
cell-identical to thesis `theory.tex` (one dropped article restored).
Policy text carries the thesis's μ "does not decide whether/which/whom"
and π "learned from data" clauses. Thesis has no numbers for
Feizi/Duetting/Xu/Qiu/Yun; none were invented.

## State

Body runs to p.17 before References (v1 was 14.5; several asks were
"you compressed too much"). 47 pp total. Local build 0 errors; one
pre-existing overfull vbox in App. C personality table (round 2).

## Round 2 (his)

Statements (`08_statements.tex`: stray `i mean`, XXXXX funding/ethics,
HF processed cite) and remaining appendix polish. Page-cut options for
≤10 body pages are still his call: theory 3.2 → appendix, related work
to three paragraphs, RQ table → list, families table → appendix.

## Appendix / cite pass (16 Sep evening, paper `867b6f0`)

- `\clearpage` before A–E so each appendix chapter starts on a new page.
- Dropped App. A timing retell (lives in Method 4.3); Friedman table and
  item-diagnostics table from C; recording-volume and “estimators not
  used” from D; Dataset A/B jacket retell in E.
- Why 60/70 is in Method 4.5 and Results 5.3: personality is
  5 traits × 3 contrasts × 4 primary outcomes, not 22 items
  (item-level would be 330). Demographics is 5 factors × 3 contrasts
  on 4 outcomes + 2 cued-recall = 70, two level-codings.
- BibTeX authors `Troiani, Walter J.` so apalike prints Troiani, not
  Vargas. Same author-field fix is sitting uncommitted in thesis
  `references.bib`; thesis cover still `\author{Walter J. Troiani Vargas}`.
