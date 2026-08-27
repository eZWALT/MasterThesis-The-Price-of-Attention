# Results and Discussion skeletons locked (27 August 2026)

Chapters 7 and 8 of the thesis now mirror each other section for section.
Do not reorder either without reordering the other, and do not reorder
`tab:analysis-families` in `sec:methods:statistical-framework`, which is
the third document in the set.

## The three documents that must agree

| Methods `tab:analysis-families` | Results §7 | Discussion §8 |
|---|---|---|
| — | 7.1 Sample, exclusions, and descriptives | — |
| Behavioural battery† / Free-text† | 7.2 Behavioural outcomes | 8.2 Behavioural outcomes `sec:disc-behaviour` |
| Personality and demographics† | 7.3 Personality and demographic moderation | 8.3 Personality and demographic moderation `sec:disc-personality` |
| Dataset A / Dataset B / positive control | 7.4 Neurophysiological outcomes `sec:results-eeg` | 8.4 Neurophysiological outcomes `sec:disc-eeg` |
| Four genre-trajectory rows | 7.5 Genre trajectories and intent theory `sec:results-trajectories` | 8.5 Genre trajectories `sec:disc-trajectories` |
| Four association rows† | 7.6 Associations across the three families | 8.6 Associations across the three families `sec:disc-combos` |
| — | 7.7 Summary of outcomes (`tab:results-summary`) | 8.1 Summary of findings `sec:disc-summary` |
| — | — | 8.7 Implications `sec:disc-implications` |
| — | — | 8.8 Limitations `sec:disc-limitations` |

† = specified but not estimated in this draft.

**The ordering principle in Results is that no section depends on one that
has not yet been presented.** Single-modality results come first, the
cross-modality associations last, because each association needs two of
the preceding sections. That is why 7.6 exists and why EEG no longer
forward-references the behavioural analysis.

## Section names changed on 27 August

Old Discussion names, now dead — fix any note or draft still using them:

- "Behavioural battery" → **Behavioural outcomes**
- "EEG" → **Neurophysiological outcomes**
- "Cross-arm associations" → **Associations across the three families**
  (the old name was wrong: the arms are laboratory and crowd, whereas
  these are cross-*family*)

Labels were deliberately **not** renamed. `sec:disc-eeg`,
`sec:disc-behaviour`, `sec:disc-trajectories`, `sec:disc-combos` still
resolve, so `.cursor/rules/results-vs-discussion.mdc` and every existing
cross-reference stay valid. New labels added: `sec:disc-summary`,
`sec:disc-personality`, `sec:disc-implications`, `sec:disc-limitations`.

## Three summaries, three different jobs

Do not let these collapse into one another.

1. **Results 7.7 `tab:results-summary`** — mirrors `tab:analysis-families`
   row for row so a reader can verify every declared family was either
   estimated or explicitly not. Numbers only, no interpretation.
2. **Discussion 8.1 `sec:disc-summary`** — prose restatement of what the
   estimated families found, in Results order, so the chapter that
   interprets opens by saying what it is interpreting. Currently: the EEG
   sustained null with its ±0.3 dB bound and the writing-vs-reading
   positive control; the trajectory Holm-nulls with the turn-1-vs-turn-4
   contrast that shows the classifier is not dead; and the explicit
   statement that the battery, personality, free text, and the four
   associations are not estimated.
3. **Conclusion `sec:conclusion:summary`** — still empty, marked "write
   last, once the behavioural battery is estimated". This is the
   thesis-level wrap (contributions, answer to the research questions),
   not a repeat of 8.1.

## Locks that still apply

- Results report numbers, Discussion interprets.
  `.cursor/rules/results-vs-discussion.mdc` is unchanged by this and
  still governs. EEG 6.3 / 7.4 is confirmatory numbers only.
- Trajectories are thesis-only. This skeleton is the **thesis**; the
  paper does not get 7.5 or 8.5.
  (`2026-08-24-trajectories-thesis-only.md`)
- Associations are association, never mediation, and are laboratory-only
  (\(n=18\)) wherever EEG enters.
- Nothing in Results draws an inferential claim from a † family.

## Related

- Statistical framework rewrite: `2026-08-27-statistical-framework-rewritten.md`
- Chapter 7 restructure rationale: `2026-08-21-results-vs-discussion-and-eeg-6-3-pushed.md`
- Backlog and what fills the † rows:
  `../data-analysis/2026-08-27-backlog-and-timeline.md`
