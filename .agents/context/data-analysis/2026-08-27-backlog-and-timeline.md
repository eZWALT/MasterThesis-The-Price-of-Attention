# Backlog and timeline (27 August 2026)

Walter's status: thesis **writing quality** is the live thread
(Ch 5 System `system_design.tex`, Ch 6 Methods `models.tex`, reducing
AI slop by hand; more iterations still owed). Analysis is **not**
complete. This note is the sprint board until 17 September.

Hard deadline: **thesis 17 September 2026** (21 calendar days from
today). Paper is now **optional** if it fights the thesis. Presentation
starts now, not in the last 48 hours.

Canonical science order is unchanged (do not invert):
`2026-08-23-goal-list.md`. Insertion-policy model stays dropped.

---

## Five pending analyses (open this window)

Walter's list, mapped onto existing goals. **Do not treat 1–2 as a
second confirmatory EEG family.** Combos (item 5) are now **opened**,
but honest tests still need Goal 1 scores.

| # | Walter | Maps to | Grain / n | Status 27 Aug |
|---|---|---|---|---|
| 1 | EEG sensors retry (Angela subset) | Channel-set sensitivity (`literature_roi_v0` George nine-site; `wang2022_v0`; `teaching_atlas_v0`; `angela_code_v0`) | Dataset A/B, \(n=18\) | **Closed 28 August.** Primary 32-ch stays confirmatory. `eeg/2026-08-28-channel-set-closed.md`. **Appendix only.** |
| 2 | EEG restructure (post-hoc) | Exploratory restructure of the 16 measures / Dataset A–B read. Sebastian. | \(n=18\) | **Bounded 28 August**, then run as an exhaustive pairwise sweep (Dataset A 10 pairs, Dataset B 6). Still **not EEG 6.3**, still exploratory, no manuscript text yet. `eeg/2026-08-28-posthoc-pairwise.md`, audit `eeg/2026-08-28-dataset-b-control-audit.md`. |
| 3 | Behavioural EDA | **Goal 1** (trust, credibility, manipulation, notice × condition / format / \(a^{\emptyset}\)) | \(N=54\) | **In review (5 Sep).** Katerina finished a pass; two Holm survivors. Walter helps this weekend. Freeze composites before combos. Do not permute items to hunt \(p\). `../writing/2026-09-05-sprint-to-deadline.md`. |
| 4 | Behavioural free-form text | Findings (≤256 chars × 5, 270 texts, has \(a^{\emptyset}\)) + cued-recall `recall_reaction` (216 texts, **no control**) | \(N=54\) | Not scored. Plan is codebook → LLM-as-judge assignment → prevalence / co-occurrence / length / quotes / word cloud: `behavioral/2026-08-27-free-text-codebook-and-llm-judge.md`. Not a second Likert battery. |
| 5 | Behavioural against the rest → **one final dataset** | Goal 2 (BFI-10, demographics) + Goal 5 combos + free-text columns | person × condition; EEG cells lab \(n=18\) | Join design exists (`eeg/2026-08-19-eeg-behavioural-merge-tables.md`); **no builder**. Trajectory × EEG join already validates (90 rows). |

Locks that still apply while doing 1–5:

- Channel-set / Angela ROI: sensitivity, `sec:app-eeg-channel-sets` only.
  Do not write into primary Gold or the abstract.
  `eeg/2026-08-24-channel-set-policy.md`,
  `../writing/2026-08-24-channel-set-sensitivity-not-confirmatory.md`.
- Post-hoc EEG: no epoch as \(n\); no ERP; do not pick a width or
  electrode set by \(p\). Confirmatory stays 4 s + median + ICA.
- Free text: participant is the unit, so prevalence per condition is
  paired against \(a^{\emptyset}\) or Cochran's Q, never a chi-square
  over the 270 texts. Codebook is frozen and versioned before the
  assignment pass, drafted blind to condition, and gets a reliability
  subset (Tang's pipeline has none). `tab:analysis-families` currently
  declares this family **descriptive**; testing prevalence requires
  changing that row first.
- Combos: association, not mediation; not a causal attention shift.
  One `genre_source` (`utterance` primary). Join
  `experiment_id` + `condition`.
- Do not overwrite ICA models.
- Results ≠ Discussion.

Suggested **analysis order inside this window** (still 1 before 5):

1. Freeze behavioural Gold (item 3): composites already specified in
   Methods / `behavioral/2026-08-18-tang-scoring-vs-ours.md`.
2. Attach free-text columns to that table (item 4), even if coding is
   a later pass.
3. Build the person × condition Gold join (item 5) from that freeze +
   existing EEG \(Y_A\) / \(D_i\) + trajectory conversation grain.
4. Angela sensor retry and post-hoc EEG (items 1–2) can run in
   parallel; they do not unlock Goal 1.

---

## Delivery (after / alongside those five)

1. **Keep pushing the thesis as now.** Ch 5–6 prose quality first;
   Results 7.2 / Discussion 8.1 when Goal 1 numbers exist; Dataset
   behavioural Gold paragraph still pending. Overleaf
   `docs/overleaf/thesis/`.
2. **Paper is optional** this sprint. Do not invent Goal 1 tables.
   Trajectories stay thesis-only.
3. **Presentation skeleton is open** (`docs/overleaf/presentation/`).
   Six spoken sections, 28 August. Fill Goal 1 / combos when they exist.
   `../writing/2026-08-28-presentation-skeleton.md`.

---

## Timeline read (tight, doable if scoped)

**Today–tomorrow (27–28 August) cannot finish all five at thesis
depth.** It *can* freeze Goal 1 scoring, start the join table, and
close or bound the Angela retry. That is the realistic 48-hour cut.

| If we try to… | Verdict |
|---|---|
| Five complete analyses + full combo Results in 48 h | No. Goal 1 ETL + four combo families + post-hoc EEG + free-text coding is more than two days. |
| Freeze Goal 1 tables, build the join Gold, Angela appendix retry, bound post-hoc | Yes, if Katerina stays missing and Walter (or an agent) owns the ETL. |
| Thesis in by 17 September, with Ch 5–6 polish, Goal 1 Results, EEG/trajectories already in, thin Goal 5, slides started | **Tight but doable.** Matches Walter's read. |
| Thesis + polished paper + finished defence deck | Not in 21 days unless the paper stays a light port. |

September split that still fits the old north star
(`2026-08-04-final-month-north-star.md`), updated:

- **27–31 Aug:** Goal 1 freeze + join dataset + Angela retry; keep
  writing Ch 5–6; open a presentation skeleton.
- **1–7 Sep:** Goal 1/2 Results + Discussion 8.1; free-text descriptives
  if coded; one combo table (exploratory); first full slide pass.
- **8–11 Sep:** supervisor / team review (do not plan new science).
- **12–16 Sep:** prose, cites, formatting; no new families.
- **17 Sep:** submit thesis.

What to cut first if Thursday slips: unbounded EEG post-hoc, rich
NLP on free-text, three-way combo, paper polish. What not to cut:
Goal 1 numbers, thesis Ch 5–6, EEG 6.3 as already written, trajectory
thesis Results, a slide skeleton.

---

## Related

- Goals: `2026-08-23-goal-list.md`
- Checklist: `../writing/2026-08-18-remaining-work-checklist.md`
- Writing track: `../writing/2026-08-27-writing-push-and-delivery.md`
- Afternoon catch-up (figures, Dataset A/B, crowd age, Rainie):
  `../writing/2026-08-27-afternoon-save.md`
- EEG × behaviour joins: `eeg/2026-08-19-eeg-behavioural-merge-tables.md`
- EEG tickets C1–C9: `eeg/2026-08-19-eeg-analysis-menu-and-tickets.md`
