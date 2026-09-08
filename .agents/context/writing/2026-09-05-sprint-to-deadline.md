# Sprint to the deadline (5 September 2026)

Pokemon save. Last context dump was **31 August** (equal-n \(k=37\),
slow-power, MDE, waves slide). Four calendar days and a human thesis
pass later; this is the board until 17 September.

Thesis due **17 September**. Defence talks **18–20 September**.
Graduation **25 September**. Paper is still optional if it fights
the thesis. Journal send is after.

Walter’s task log 29 August–4 September is the source of the calendar
below. Do not invent Goal 1 tables. Do not overwrite ICA.

## What landed since 31 August

- **7 September:** behavioural Gold + combo joins exist
  (`analysis/walter/behavioural/outputs/gold/`). Process variables
  are in. Catalog / lineage locked the same evening:
  `../data-analysis/2026-09-07-gold-catalog-and-lineage.md`.
  Figure on Overleaf as `gold_tables.png` (not included). Thesis
  §4.2.2 is still the stub. Combo *tests* are in
  (`analysis/walter/combos/`, 0 Holm / BH); Goal 1 freeze:
  `../data-analysis/behavioral/2026-09-07-goal1-freeze-sweep-and-combos.md`.
  Reduced blocks 0–7 (same night, four reviewer passes):
  `../data-analysis/behavioral/2026-09-07-combos-reduced-blocks.md`
  — 336 tests, 0 Holm / BH; Block 0 is the finding. Nothing from
  those blocks goes in Results.

- Equal-n Dataset A \(k=37\) is confirmatory and **on Overleaf**
  (thesis `4310044`, paper `8a6d9e2`, presentation `8a72e61`,
  31 August). Parent GitHub has it after a linear rebase onto
  Katerina’s two notebook commits (`d8adde7`, `2334317`).
  Discussion read: early vs late posterior alpha (Walter’s sentence);
  Fz \(\theta\) same direction, Holm-null; relative \(\theta\) is a
  lower share, not extra control. Lock:
  `2026-08-31-equal-n-k37-manuscript.md`.
- EEG \(t\) vs Wilcoxon is **not** a Shapiro switch. Both always;
  \(t\) is primary (mean, CI, \(d_z\)); Wilcoxon is the
  \(n=18\) robustness check. Holm families are separate. Timing
  posterior alpha: \(t\) Holm \(p=.050\), Wilcoxon Holm \(p=.062\);
  report the disagreement, do not pick the nicer \(p\).
  **MDE withdrawn 6 September** — do not put it back.
- Presentation skeleton + flow + title page + EEG slides exist.
  Record a long-cut session still owed. Do **not** rewrite his `%`
  comments or the High-level discussion enumerate.
- Thesis human revision: Ch 1–6 touched 2–3 September; 7–8 were the
  4 September block. Walter’s own leftover flags: **4.2.2**, and
  **6.3 last paragraph** (fact-check). Abstract still empty
  (`LOREM IPSUM`) until the 4–5 September pass.

## Analysis: Katerina is back

She finished a behavioural pass this week. **Two things survived
Holm.** Same honesty rule as EEG: a Holm-null is a result, not a
licence to hunt. Walter helps this weekend; she still owns the
missing Goal 1 review. Sebastian meeting **7 September**.

**Do not** permute, drop, or regroup Likert items *to get more
significant results*. That is the same class of error as picking
EEG \(k\) or a montage by \(p\). Allowed: freeze the composites
already specified in Methods / Tang scoring, report the two Holm
cells, put the rest as Holm-null with CIs. Item-level descriptives
are appendix, not a second confirmatory family.

Combos (Goal 5) ran on those frozen scores (7 Sep night).
Association, not mediation. Lab \(n=18\) wherever EEG enters.
Join `experiment_id` + `condition`. EEG side is \(D_i\) from
condition aggregation \(k=37\), not Gold whole-window medians
(whole-window is a sensitivity only). Trajectory side: one
`genre_source` (`utterance` primary). Lock:
`../data-analysis/behavioral/2026-09-07-combos-reduced-blocks.md`.
Do not invert 1 → 5.

Free-text (item 4) is still not a second Likert battery.

## Delivery this window

| When | What |
|---|---|
| 5 Sep (Sat) | Final abstract. Flight / Erasmus+ / UniPD paperwork. Help Katerina a bit; no item-hunt. |
| 6 Sep (Sun) | Thesis appendices. Paper: skeletonize, define final structure; push only if it does not steal thesis hours. |
| 7 Sep | Behavioural analysis meeting with Sebastian. |
| 10 Sep | Walter’s mental deadline: analysis + thesis document. |
| 17 Sep | Thesis in. |
| 18–20 Sep | Presentation. Record long vs short (30 vs 40 slides) before then. |
| 25 Sep | Graduation. Journal after. |

Priority if hours collide: **thesis prose → Goal 1 freeze → combos →
deck recording → paper skeleton.** Not the other way.

## Locks that still apply

- Results ≠ Discussion. H1–H3 live on the behavioural composites.
- Dataset A/B, implicit/explicit, early = turn 2, late = turn 4.
- Trajectories thesis-only. \(f_{\mathrm{genre}}\).
- Channel-set / exhaustive ad-local \(k\) / post-hoc pairwise:
  exploratory or sensitivity. Equal-n \(k=37\) is confirmatory
  Dataset A (shortest chat), not a search hit.
- Do not overwrite `src/project/logs/xdf/silver/ica/candidate_v1/`.
- Do not write “approached significance.”
- EEG MDE is withdrawn (6 September). Do not restore `eq:mde`.
- High-level discussion slide is his. Any-ad Dataset A stays
  Holm-null; that is the “no overall condition difference” line.

## Open on the manuscripts (do not silently “finish”)

- Thesis `abstract.tex` (write 5 Sep, do not invent EEG claims the
  Discussion does not already make).
- Thesis 4.2.2 and EEG Results 6.3 last paragraph.
- Results 7.2 / Discussion 8.1 behavioural numbers, once Katerina’s
  two Holm cells and the rest of the battery are frozen.
- Combos Results / Discussion: grey until Goal 1 freeze.
- Deck: Goal 1 takeaways, combo slide only if Goal 5 ran, long-cut
  recording.
- Paper: structure pass 6 Sep; no Goal 1 tables until the freeze.
