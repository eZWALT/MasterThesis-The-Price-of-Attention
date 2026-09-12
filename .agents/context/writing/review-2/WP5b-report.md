# WP5b — Discussion 8.4 Trajectories, 8.5 Associations, 8.6 Implications, 8.7 Limitations

Date: 11 September 2026. Owner: `claude-opus-5-thinking-high`. Status: **done**.
File edited: `docs/overleaf/thesis/chapters/discussion.tex` only, sections
`sec:disc-trajectories`, `sec:disc-combos`, `sec:disc-implications`,
`sec:disc-limitations`. Targeted `StrReplace` throughout; the file was never
rewritten; 8.1–8.3 untouched. Diff +150 / −59. All `% WALTER:` lines intact
(`git diff -- chapters/discussion.tex | rg -i "^-.*WALTER"` is empty in the
Overleaf mirror repo). Nothing committed, nothing pushed.

Structural checks (no TeX toolchain here): `\(`/`\)` 129/129, braces 160/160,
1 `figure`, 1 `table`, 1 `tabular`, every `tab:rq-answers` row has exactly 4
ampersands for 5 columns. Every new `\autoref` target verified to exist:
`sec:app-traj-sweep`, `sec:app-eeg-measures`, `sec:methods:study-design`,
`ch:system-design`, `sec:conclusion:future-work`,
`sec:intro:research-questions`, `sec:results-behaviour`,
`sec:results-personality`, `sec:results-eeg`, `sec:results-trajectories`,
`sec:results-combos`, `fig:traj-depth`, `tab:results-checks`. A compile is
still owed.

---

## 1. Per WALTER comment

| Comment (text, since lines moved) | What changed |
|---|---|
| 8.4 "again the mention of the fucking u5 not existing" | The sentence `Local \(\delta^{(a)}_4\) is undefined: there is no \(u_5\)` **deleted**. `% [AI: removed here; the point is made once, in Results 7.5.]` added. |
| 8.4 "labellings? i think contexts" | Walter's own title `The two contexts fail in opposite directions.` kept verbatim; `labellings` elsewhere in the chapter (8.7) changed to `contexts`. No `labelling` string left in `discussion.tex` prose. |
| 8.4 "This section neeeds further explainig of findings" | Two new paragraphs and one rewritten one (see §2). `% [AI: expanded — …]` added. |
| 8.4 "the title here is stupid … what even is the inventory?" | `The inventory is a weak target.` → **`Advertised genres overlap the conversation genres.`**, rewritten in full sentences: 98 of 156 served products labelled general guidance, four purchasable products, advertised genre usually equals the genre the conversation was already in, equals the pre-insertion label in a quarter of early conversations, nine aligned shifts against 10.46 expected. |
| 8.4 "both title and prose here is again non-sense" | `Depth moves; the insertion does not.` → **`Conversational depth as the dominant signal.`**, four sentences: guidance share falls by more than half, fallback labels roughly quintuple, median message forty words → ten, rise only partly explained by shortening; **the implication Walter asked for in Results** (turn depth, not the advertisement, is what the genre label tracks) closes it, together with the "not yet usable as measures" statement moved here from the old inventory paragraph. |
| 8.5 "This first sentence is a bit crptic" | Opener rewritten: what a person-level difference score is, what a Spearman correlation between two of them says, laboratory eighteen wherever EEG enters, association not mediation, no direction of effect. |
| 8.5 "the title is sus … k=37 SHOULDN'T BE MENTIONED" | `The condition-aggregation nulls are weak nulls.` → **`Reliability of the condition-aggregated scores.`**; `k=37` removed; split-half point kept and made the claim of the paragraph (a score that does not reproduce across halves cannot correlate strongly with anything); posterior \(\alpha\) now stated as the score that *does* reproduce. |
| 8.5 "make the results sound good without faking … posterior alpha description lacks depth" | Retitled **`Trust and the posterior \(\alpha\) response at onset.`**, claim first, and split in two. New depth: posterior \(\alpha\) is 8–13 Hz over O1, Oz, O2, P3, Pz, P4, the band/region where the visual system's idling rhythm is strongest; it falls as visual attention engages the display and rises as attention withdraws (`sec:app-eeg-measures`); so a drop in the four seconds after the insertion is the signature of the visual system taking up the new object, and those participants are the ones who trusted the assistant less with advertisements than without. |
| 8.5 "i would jsut cut out this sentence wtf The marker that passed…" | Already absent from prose (Walter had moved it into his comment). `% [AI: cut, as asked.]` added; not reinstated. |
| 8.5 "I dont get the point of this sectiona t all" | `One cell in eighteen people is a bounded hypothesis.` → **`What the interval supports.`** Kept as its own paragraph (merging would have pushed the previous head past ten lines). First sentence now carries the point explicitly: the number to carry is the lower bound `.48`, of which `.80` is the optimistic end; then the two inflating factors (selection at \(n=18\); reliabilities `.56` and a single trust item); then that the *pair* was fixed in Methods. Closing sentence is now user-centric instead of a study prescription. |
| 8.5 "Title is too informal and be sure to not be too agressive discarding evidence" | `The rest of the map is noise with one exploratory pattern.` → **`The exploratory map.`**, split in two paragraphs and rewritten: declared pairs fixed in Methods before any correlation; 2,560 + 336 tests return raw hits at about the chance rate with none surviving correction; the one coherent block (implicit − explicit: longer and slower conversations with a lower fast-band engagement index, largest cell reply latency \(\rho=-.69\)) is "a pattern worth testing in a design built for it", explicitly not dismissed; trajectories join neither side; partial \(\rho\) `.80` / `.83`. "noise", "judgmental", "contextual labelling" all gone. |
| 8.6 "fact check this section deeply" | Whole section rewritten against the tables; see §4 for the claim → source table. Two inherited claims were **false** and are corrected (see §4, rows marked ✗). `% [AI: …]` note records both. |
| 8.6 "visual matrix with marginals" | `fig:effects-matrix` inserted at the top of 8.6 with the WP6 two-line caption, `[!htbp]`, `width=\linewidth`. New paragraph **`Reading the matrix.`** (split in two for readability) reads the behavioural block, the two EEG blocks, the trajectory rows and the association rows, directions in words, and closes with the hollow-cell gloss ("estimated and not distinguishable from zero in this sample, not shown to be absent"). `% [AI: …]` records the provenance CSV. |
| 8.6 "this section reads too AI-ish" | `Presentation is not interchangeable at onset.` → **`Format at onset.`**, rewritten. The wrong clause "the formats are interchangeable as a neighbourhood-of-onset state" (Dataset A is condition aggregation, not a neighbourhood of onset) replaced by "averaged over a whole condition window". `\lambda` dropped in favour of "presentation". |
| 8.6 "Title bad, prose can be improved a bit but the message is good" | `A genre label is not an advertisement-impact measure on this input.` → **`Genre labels as impact measures.`**, rewritten in full sentences; "either of the two contexts the classifier can be given" replaces the bare \(f_{\mathrm{genre}}\) clause; RQ numbers dropped here (the table now carries them). |
| 8.6 "What is even this goofy ass title? … onset is more improtant than condition level to set up a precedent" | `Advertisement versus none is the wrong EEG question if the variance is an event.` → **`Onset-locked designs.`** Walter's idea kept as the opening claim ("the methodological precedent this study sets … is that the moment of insertion matters more than the level of the condition"). The two imperative design recipes were removed and handed to WP8 (§5). |
| 8.6 "is this true to this day? Task moderation (RQ3) and personality moderation (RQ8, RQ9)…" + "we should include all the RQ's here right? maybe in a small table?" | The orphan sentence `Personality moderation (RQ6, RQ7) is estimated and Holm-null…` **deleted** and absorbed into the new `\subsection{Answers to the research questions}` (`sec:disc-rq-answers`), which holds the WP7 `tab:rq-answers` verbatim plus one lead sentence and two short reading paragraphs (three supported, one partly, five negative, each negative given a user-centric gloss). |
| 8.6 "THIS STUDY IS IMPORTANTLY USER CENTRIC …" | Section opener now opens on it (see §6, sentence 1). `% [AI: …]` points WP9/WP8 at this report. |
| 8.7 eight numbered limitations + "differentiate limitations from future work" | 8.7 restructured from three blobs into a one-line framing sentence plus four headed paragraphs: `Design and sample.` (three paragraphs), `Measures.`, `Neurophysiological measures.`, `Genre trajectories.` All eight of Walter's items added, plus the extras found by scanning Ch 4–7. Every prescription moved out (§5). `% [AI: …]` records where the future-work list lives. |

## 2. Final paragraph titles, 8.4–8.7

**8.4 `sec:disc-trajectories`**
1. `A Holm-null is not a verdict on the theory.` (kept)
2. **`What the advertisement contrasts show.`** (new)
3. `The two contexts fail in opposite directions.` (Walter's, kept verbatim)
4. **`Advertised genres overlap the conversation genres.`**
5. **`Conversational depth as the dominant signal.`**

**8.5 `sec:disc-combos`** (opener has no head)
1. **`Reliability of the condition-aggregated scores.`**
2. **`Trust and the posterior \(\alpha\) response at onset.`**
3. **`What the interval supports.`**
4. **`The exploratory map.`**

**8.6 `sec:disc-implications`** (opener has no head; `fig:effects-matrix` follows it)
1. **`Reading the matrix.`**
2. **`Felt pressure as the user-side cost.`**
3. **`Format at onset.`**
4. **`Genre labels as impact measures.`**
5. **`Onset-locked designs.`**
6. `\subsection{Answers to the research questions}` → `tab:rq-answers`

**8.7 `sec:disc-limitations`**
1. **`Design and sample.`**
2. **`Measures.`**
3. **`Neurophysiological measures.`**
4. **`Genre trajectories.`**

## 3. Every number introduced, with its source

All numbers come from `results.tex`, `appendix_e.tex`, `appendix_d.tex` or the
WP reports. No existing number was changed and no CI was added to prose.

| Number | Where I put it | Source |
|---|---|---|
| 9 aligned shifts, 10.46 expected, 108 conversations | 8.4 overlap paragraph | `tab:traj-aligned-counts`, results.tex:424 |
| 156 distinct products, 98 general guidance, 4 purchasable products | 8.4 overlap paragraph | results.tex:424 |
| "a quarter of the early-advertisement conversations" (25 of 108) | 8.4 overlap paragraph | results.tex:424 |
| "falls by more than half" (guidance 0.478 → 0.211) | 8.4 depth paragraph | results.tex:456, `fig:traj-depth` |
| "roughly quintuples" (fallback 4.1 % → 20.0 %) | 8.4 depth paragraph | `tab:traj-turn-length` |
| "about forty words to ten" (median 40.5 → 10.0) | 8.4 depth paragraph | `tab:traj-turn-length` |
| "only partly explained by that shortening" (turn \(\beta=0.34\) with \(\log\) words in) | 8.4 depth paragraph | results.tex:361, `tab:results-checks` |
| Fz \(\theta\) split-half not detectable; posterior \(\alpha\) reproduces well (`.78`) | 8.5 reliability paragraph | `tab:results-checks`, split-half row |
| \(\rho=.24\) vs \(\rho=.80\) | 8.5 onset paragraph | results.tex:498 (pre-existing in 8.5) |
| 8–13 Hz; O1, Oz, O2, P3, Pz, P4; falls as visual attention engages | 8.5 onset paragraph | `sec:app-eeg-measures`, appendix_d.tex:56 |
| `.48` lower bound; `.56` onset-locked split-half | 8.5 interval paragraph | results.tex:498 / pre-existing in 8.5 |
| 2,560 and 336 tests; 105 vs 128 and 10 vs 17 expected, read as "about the rate chance predicts" | 8.5 exploratory map | results.tex:539, `tab:results-checks` |
| \(\rho=-.69\) reply latency | 8.5 exploratory map | results.tex:513 (WP4 note 5: the "21 cells" figure is **not** in Results and was not used) |
| partial \(\rho\) `.80` / `.83` | 8.5 exploratory map | results.tex:516 |
| "about half … did not report the written-in mention as sponsored" | 8.6 felt-pressure paragraph | WP3 report §1 (52 % / 56 %); 7.2 |
| Whole `tab:rq-answers` table | 8.6 | WP7 report §3, inserted verbatim |
| p95 onset uncertainty `0.43` s; notice \(\alpha=.61\); credibility mean 6 of 7 | 8.7 | pre-existing in 8.7 |
| Qwen 3.6 35B-A3B (quantized) | 8.7 design paragraph | `system_design.tex:59` — the exact thesis name. "Qwen 3.8" was **not** written; it appears nowhere in the thesis. |

## 4. Fact-check of 8.6 (claim → support)

✓ = supported as written · ✗ = inherited claim that was wrong and is now corrected.

| Claim in 8.6 | Support |
|---|---|
| ✓ Notice and manipulation rise in **every** advertisement condition against \(a^{\emptyset}\) | `tab:beh-localisation`: notice +1.60 / +1.40 / +2.81 / +2.49, all Holm \(<.001\); manipulation +1.20 (.006), +0.72 (.040), +1.92 (\(<.001\)), +1.24 (\(<.001\)) |
| ✓ Banner noticed more, felt as pushing more, remembered better than the mention | `tab:beh-planned` implicit − explicit: notice −1.15, manipulation −0.62 (.022), cued memory −1.45, all Holm-significant |
| ✓ Both formats noticed; **implicit is not free** (raises manipulation above \(a^{\emptyset}\) at both timings) | `tab:beh-localisation` implicit early / late manipulation rows, both bold |
| ✗ → corrected | "the format participants mostly fail to recognise when it is re-shown" was **false**: cued memory ≥ 5 for 57 % / 59 % of participants on the implicit mentions (WP3 §1; 7.2). Replaced by "about half the participants did not report the written-in mention as sponsored". |
| ✓ Early insertion felt more manipulative, slightly less credible, lower trust on re-exposure | `tab:beh-planned` early − late: manipulation +0.58 (.007), credibility −0.33 (.017), trust after re-exposure −0.49 (.047) |
| ✓ The only filled trust cell is early banner vs \(a^{\emptyset}\) | `tab:beh-localisation` explicit early −0.69, Holm .031; the three planned trust contrasts are Holm-null (`tab:beh-planned`) |
| ✗ → avoided | WP6 flagged "late increases credibility" as **not estimated** (late − \(a^{\emptyset}\) is +0.01 / +0.04, hollow). 8.6 says only "an early insertion lowers credibility", never that late raises it. |
| ✓ No format × timing interaction | `tab:beh-planned` prose, results.tex:149: \(|d_z|\le0.06\) on all four outcomes |
| ✓ Condition-aggregated markers separate neither any-ad nor format | results.tex:245, `fig:eeg-forests`: only Holm cell is early − late posterior \(\alpha\) |
| ✓ Slow-power tilt after an early banner, on the exploratory battery; mention shows nothing comparable | results.tex:257, `fig:eeg-holm-board`: five of six exploratory orange cells on explicit early; 8.3 states \(|d_z|\le0.37\) for implicit |
| ✓ Posterior \(\alpha\) lower early than late is the one condition-aggregated filled cell | \(-0.22\) dB, Holm \(p=.0496\) |
| ✓ No advertisement contrast moves a planned trajectory measure, under either context | `tab:traj-crossing`, `tab:traj-late`, deployed-context row of `tab:results-checks` |
| ✓ Trust covaries with the onset-locked posterior \(\alpha\) and not with the condition-aggregated one | \(\rho=.80\) Holm \(p=.0004\) vs \(\rho=.24\) (`sec:results-combos-behaviour-eeg`) |
| ✓ RQ verdicts (3 supported, 1 partly, 5 not supported) | each row of `tab:rq-answers` re-checked against `tab:beh-planned`, `tab:traj-crossing`, `tab:traj-late`, `fig:beh-personality`, `fig:eeg-forests`, 7.6; all agree at printed precision |

Two cosmetic rounding notes from WP6 §"disagreements" (credibility early − late Holm
printed `.017` vs CSV `.016`; manipulation implicit late `.040` vs `.039`) do not appear
in 8.6 prose, which quotes no Holm \(p\) outside `tab:rq-answers` (where WP7's `.017`-free
wording is used).

## 5. For WP8 (Conclusion → Future Work): exact sentences moved out

These were prescriptions sitting in 8.5 / 8.6 / 8.7. They are **removed from
`discussion.tex`** and belong in `sec:conclusion:future-work`. Ch 9 already covers
extending the intervention space, late-advertisement designs, eye tracking, personalisation
and longitudinal use, degradation benchmarks, retrieval evaluation and cross-lingual work,
so only the onset-lock items below are genuinely new.

1. (from 8.5 `What the interval supports.`) "Its test is a study that fixes the
   onset-locked pair in advance, records more than eighteen people, and asks for trust
   per advertisement rather than per condition."
2. (from 8.6 `Onset-locked designs.`) "A design that wants a neural contrast on format
   should lock to onset, not only to condition aggregation."
3. (from 8.6 `Onset-locked designs.`) "A design that wants to relate a neural response
   to trust should lock to onset and ask for trust per advertisement."
4. Implied by 8.7 and worth one clause in Ch 9: log the visual onset of the written-in
   mention in the client rather than reconstructing it; record a dedicated EOG or eye
   track; more than one onset trial per cell; ask the trust item per advertisement.
5. Also worth one clause: a longer-horizon or repeated-session design, since the
   sub-hour session cannot see the trust cost of a mention that a user only later
   recognises as advertising.

**Left in place by judgement** (Walter's own paragraph, `The two contexts fail in
opposite directions.`, 8.4): "The theory has to be refined with the engineering: which
tokens enter the model, how short later turns may become, and how the fallback classes
absorb those turns." It is his sentence and reads as a diagnosis of the instrument
rather than a work plan. If WP8 wants it as future work, it moves cleanly.

## 6. User-centric sentences for WP9 (abstract) and WP8 to echo

In priority order, all now in the thesis:

1. 8.6 opener: "What this study measures is what an advertisement placed inside a
   conversational assistant costs the person using it: the trust and the credibility
   they grant the assistant, the commercial pressure they feel, what they notice, what
   they remember, and how they respond at the moment of insertion. It does not measure
   click-through, revenue, or anything else on the advertiser's side."
2. 8.6: "What an advertisement costs the user here is felt commercial pressure, and it
   costs most when the advertisement is a labelled banner arriving early."
3. 8.6: "Both formats are noticed and both raise perceived manipulation above
   \(a^{\emptyset}\) at both timings, so the written-in mention is not free."
4. 8.5: "At the moment an advertisement appears, the strength of a person's visual
   response to it and the trust that person withdraws from the assistant move together."
5. 8.4: "Read from the user's side, an advertisement inserted into one of these
   four-turn conversations did not visibly redirect what the person asked next."
6. 8.6 RQ reading: "Who the user is, on the traits and the background this sample
   covers, does not change what the advertisement costs them."

These sit alongside the five WP5a listed from 8.1–8.2 (trust holds up; the cost
concentrates on the early labelled banner; a lower notice score is a cost the user is
less able to attribute).

## 7. Cross-references that must exist

- **`fig:effects-matrix`** — defined in 8.6, file `figures/results/effects_matrix.pdf`
  (present, 45 kB, vector, WP6). Referenced once, in the 8.6 opener.
- **`tab:rq-answers`** — defined in `sec:disc-rq-answers`. Referenced once there.
  WP8/WP9 may reference it; nothing else does yet.
- **`sec:disc-rq-answers`** — new label, not yet referenced anywhere else.
- New outbound references introduced by this WP, all verified to resolve:
  `sec:app-traj-sweep`, `sec:app-eeg-measures`, `sec:methods:study-design`,
  `ch:system-design`, `sec:conclusion:future-work`, `sec:intro:research-questions`,
  `fig:traj-depth`, and the five `sec:results-*` labels used by `tab:rq-answers`.
- Citation added: `tang2025adstalkbackimplications` in 8.7 (model-generation limitation).
  Already in `references.bib`.

## 8. Open questions for Walter

1. **RQ8 verdict word.** WP7 used a fourth verdict, `Partly`, because timing survives
   Holm on posterior \(\alpha\) and format does not. Kept as-is. Say the word and it
   splits into two rows.
2. **Model-generation claim.** 8.7 says the assistant is "comparable to or stronger
   than the assistants used in the studies this design builds on". That is your
   notebook claim (Qwen 3.6 vs GPT-4o / Phi-4) and it is defensible from the
   Artificial Analysis score already cited in Ch 5, but it is the one comparative
   sentence in 8.7 that a reviewer could ask for a number on.
3. **`fig:effects-matrix` placement.** It is 16 × 19.5 cm, so at `\linewidth` it is
   close to a full page and will almost certainly float to its own page. That is
   probably what you want for a summary grid; if not, WP2 can rebuild it at a wider
   aspect ratio.
4. **WP6's two open cell questions** (keep the eight hollow post hoc EEG marginals?
   keep the four sensitivity association cells?) are unresolved and affect the figure,
   not the prose. `Reading the matrix.` works either way.
