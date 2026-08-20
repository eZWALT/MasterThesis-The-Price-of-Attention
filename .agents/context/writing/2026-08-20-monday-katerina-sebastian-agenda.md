# Monday agenda: Katerina + Sebastian

Date: 20 August 2026
Meeting: first working day after their vacation (week of 24 August).
Thesis deadline: **17 September 2026**. Paper after that.

Walter's instinct after EEG is “trajectory → paper → thesis.”
**Do not invert the study.** After EEG, the next science is Goal 1
(Katerina's ETL + trust/credibility/manipulation), then paper Results
for that, then Goal 2, then EEG Results prose. Genre / insertion model
are 4 and 5. Drop 5 first if September is short.

This meeting is for **decisions and ownership**, not a methods seminar.

## What is already frozen (do not re-open unless the freeze is reopened)

- Cohort: lab EEG \(n=18\) (Subject 4 out); behavioural finished \(N=54\)
  (\(L=18\), \(C=36\)); unfocused kept if complete.
- Design: implicit vs explicit; early = turn 2; late = turn 4; five
  conditions + \(a^{\emptyset}\). Implicit ≠ subliminal ≠ covert.
- Inferential unit is the **participant**.
- EEG primary: 4 s + median + ICA. Path A/B confirmatory Holm-null.
- 8 s late-block alpha and 2 s early-block theta are sensitivity only.
- Read vs write: one sentence (Fz theta Holm 0.007). Not an ad result.
- No ERP. No epoch-as-\(n\). No entropy/PLV. Session baseline not in
  confirmatory tests (eyes uncontrolled).
- \(\delta^{(a)}_k\) only after early ads; not a causal attention shift.

Show the heatmap and the onset timeline. Ask them to **confirm**, not
to pick a prettier \(p\).

## Ask Sebastian (reviewer / senior)

Confirm the confirmatory framing; this is not another ICA tutorial.

1. **ICA 99%.** `n_components=0.99` is fit dimensionality, not variance
   kept after `apply`. Held-after-apply: median 65%, min 25%, Subjects
   11/15 ~75% removed. ICA is primary; no-ICA is mandatory sensitivity.
   Six Path B exploratory hits are ICA-only and stay labelled that way.
   Ask: is that an acceptable primary, or does he want no-ICA in the
   main text too?
2. **Epoch width.** 4 s was frozen before the grid. Path A null at every
   width. 2 s and 8 s light up *different* cells (early theta vs late
   alpha). Confirm: do not switch primary to 8 s.
3. **Null framing.** Pipeline is alive (read/write). Path A CI is tight
   around zero. Ask: one confirmatory EEG sentence + appendix
   robustness, or does he want a longer EEG Results?
4. **Paper cut.** 14 RQs + H1–H3 must collapse to the five-goal order.
   Ask which of these are main text vs appendix:
   - figure 08 forests (main)
   - figure 07 rainclouds (optional main)
   - epoch heatmap / ICA vs no-ICA / threshold (appendix)
   - read/write slopes (not main)
5. **Method leftover.** EEG Method still has red ERP / ICA-list text
   that fights the spectral paragraph. Ask whether that leftover Method text can go.
6. **Sample line.** Draft still said \(L=19\). Confirm \(L=18\) in every
   abstract/method sentence.

## Ask Katerina (behavioural lead)

This is the critical path. Without her freeze, Walter cannot write
Goal 1 Results or do C1.

1. **One ETL.** Prefer validated `export.jsonl`. Map numeric conditions
   `1`–`5` via `condition_plan`. No double-counting `events.jsonl`.
   Roster to confirm: \(N=54\).
2. **Scoring.** She saw negative dimension scores. That is not Tang and
   not our plan (both stay in \([1,7]\) after \(8-x\)). Freeze item
   directions *before* looking at condition means. Cronbach on the
   three-item credibility mix; fallback is Tang's two-item pair.
   Manipulation = mean of the two items. `personality_trust` stays
   separate.
3. **Primary outcomes for Goal 1.** Trust, credibility, perceived
   manipulation, notice. Same three \(D\) as EEG. Ask her to name the
   confirmatory family so Walter does not invent one.
4. **Exclusions ledger.** Unfocused in if complete. Testers out.
   `lab_subject_4_crowdfail` out of lab EEG; decide behavioural arm.
5. **Ownership this week.** Who runs Goal 1 models, who writes the
   Results paragraph, what file is Gold. Walter can implement if she
   hands the contract. He cannot guess scoring.
6. **Goal 4 classifier.** Is anything frozen? If not, genre stays a
   Theory object until after Goal 1–2. Do not start trajectory code
   on Monday.

## Shared (both in the room)

1. **Calendar.** Thesis 17 September. Paper after. This week: freeze
   behavioural Gold + Goal 1 numbers. Next: Goal 2 light, EEG Results
   prose, paper cut. Goal 5 drops first.
2. **Admin still open on the paper.** Author roles, funding, ethics
   number, colleague ping comments still in the TeX.
3. **Heineking.** Implicit/explicit is \(\lambda\), not their covert/
   overt. Confirm the Related Work fix in one pass.
4. **What Walter does after this meeting.** Help freeze Goal 1, write
   those Results, then EEG Results (A7). Trajectory only if 1–3 are
   stable. Thesis ports the paper; it does not get a second analysis.

## Do not put on the agenda

- More epoch lengths or onset games
- Mixed models as the primary EEG test
- EEG × survey before Goal 1 Gold
- Entropy / PLV / ERP
- Promoting 2 s or 8 s
- Changing the ad product from EEG
- Rewriting Theory live (it is the golden section)

## Bring to the table

- Holm heatmap (ICA + no-ICA): `figure_10b_epoch_grid_heatmap_ica_noica`
- Onset timeline: `figure_17_epoch_timeline`
- Confirmatory forests: `suite/figure_08_confirmatory_forests`
- One-pager: this file
- Overleaf paper STATUS map: `2026-08-19-completion-snapshot.md`

## Exit criteria (leave with these written down)

- [ ] Sebastian: 4 s + ICA + median stays primary
- [ ] Sebastian: 8 s is appendix/sensitivity
- [ ] Sebastian: EEG Results length (one section vs short paragraph)
- [ ] Katerina: ETL + scoring contract owner and date this week
- [ ] Katerina: Goal 1 confirmatory outcome list
- [ ] Both: who writes Goal 1 Results
- [ ] Both: Goal 4/5 deferred until 1–3 exist
- [ ] Both: \(L=18\), \(N=54\) in the paper
