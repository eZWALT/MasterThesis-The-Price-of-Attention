# Paper jury v2 (16 Sep, 20:10) — same three reviewers, PDF after the v1 fixes

PDF judged: paper `a66e803` (48 pp, after round-2 comments + v1 fixes +
British title + whole-window removal). Same brief, no context, no access
to the v1 reviews.

## Scores v1 → v2

| Axis | Luna | Grok | Kimi |
| --- | --- | --- | --- |
| Research question / contribution | 7 → 7 | 7 → 7 | 8 → 8 |
| Design | 5 → 5 | 6 → 6 | 6 → 7 |
| Statistical validity | 5 → 6 | 5 → 7 | 7 → 8 |
| Technical correctness | 6 → 6 | 6 → 8 | 7 → 8 |
| Results / interpretation discipline | 6 → 6 | 6 → 5 | 7 → 9 |
| Internal consistency | 7 → 7 | 5 → 6 | 6 → 7 |
| Reproducibility | 5 → 6 | 6 → 6 | 7 → 8 |
| Writing / short-form craft | 8 → 7 | 7 → 7 | 8 → 9 |
| **Overall** | **5 → 6** | **6 → 6** | **6 → 7** |

Mean overall 5.7 → 6.3. Statistical validity and technical correctness
moved most (the v1 consistency errors are gone). Grok's
results-discipline dip is the abstract keeping the post hoc trust cell
and "none after the mention".

## What v2 still attacks (all three)

1. Dataset A early−late posterior α at Holm .0496, n = 18, depth-confounded,
   not re-estimated at other widths.
2. "Confirmatory" without pre-registration; 4 s, epoch count, ICA
   thresholds, 1,050 µV all fixed by the authors.
3. Dataset B pre-onset window contains the ~3 s retrieval wait; mention
   onset reconstructed mid-stream.
4. Abstract: "none after the mention" (Discussion says the direct format
   comparison is null); post hoc trust cell in the abstract; "did not seem
   to interact".
5. ρ = .80: n = 18, single-item trust, split-half .56, two score families.
6. Task and arm not in any model; five repetitions of the battery.
7. Title/first sentence promise trust and attention; trust is Holm-null on
   every planned contrast.

## Applied after v2 (`1d4a881`, `7698241`)

Table 5 questions use Table 1 wording and RQ1/RQ2 answers are qualified;
§6.3 no longer says "visual cortex reacted"; D.2 exploratory-cell count
(five of seven); Table 3 completeness clause; the two unmapped
felt-influence items named in 4.4; "no primary-outcome cell";
Fig. 6 cited; Intro "aggregated over the condition"; bib initial.

## Deepseek 4.1 flash, after the refinement (17 Sep)

Fourth reviewer, on the PDF after `7698241`. Six "must fix" claims checked
against the source and Gold: **four are wrong about the current files**
(Table 4 already has all 16 rows, the personality nearest term already prints
Gold's \(.178\), \(D_i\) already lists five conditions, `\(\Pi\)` was only a
PDF text-extraction artefact). Two were real and are fixed: the Abstract and
Conclusion "none after the mention" is now qualified to the same turn, since
implicit-late relative \(\gamma\) survives Holm at \(.037\) in Table 19; and
the positive-control paragraph in Results 5.4 lost its interpretive tail.
Three cheap extras applied: Related Work closer now credits Tang and Salvi,
Limitations says task and position are balanced rather than modelled, and
Method 4.5 states that the fourteen exploratory EEG measures carry no
across-measure error control. Nothing re-estimated; not compiled (no local
TeX). Report: `2026-09-17-deepseek-after-refinement.md`.

## For Walter before the next external review

- Abstract (yours): the three v2 abstract hits above.
- k = 37 stays covert per your call; the whole-window aggregation is out
  of the PDF.
- Placeholders XXXXX; HF/GitHub must exist; acknowledgement register.

## 17 Sep — five more juries, consensus applied

Deepseek flash, Gemini flash, Grok, ChatGPT, and Claude Sonnet 5 on the
PDF after `7698241`. Deepseek bookkeeping was applied by a separate
agent (`2026-09-17-deepseek-after-refinement.md`); the cross-jury
consensus pass sits on top of it and reverted none of it. Report:
`2026-09-17-jury-consensus.md`.

Eight of fifteen consensus items were already true in the source or
false about it (Results tilt name, arm naming, positive-control family,
any-ad delay, the abstract notice rates). Seven cheap wording fixes are
in, all one clause or one sentence: the depth confound on the Abstract
and Table 5 RQ6 \(\alpha\) cells; confirmatory onset-locked null stated
in the Abstract and Conclusion; the "fake friend" sentence attributed to
the literature; the bundled \(\lambda+\theta\) clause on the Table 1
caption; the novelty sentence qualified to the reviewed literature;
Dataset B named as banner-vs-control in Limitations; HyDE deployed
values in Appendix B; one `\autoref` from Method 4.4 to D.3.1.

Still his, still refused here: the `XXXXX` statements; the width /
no-ICA grid on the Dataset A onset-centred cell (new analysis on frozen
Gold); task or position random effects; "confirmatory" → "pre-specified"
wholesale. Not compiled locally, not committed, not pushed.
