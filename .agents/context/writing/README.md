# Writing context structure

This directory holds durable writing decisions, Overleaf workflow notes, and
handovers for thesis and publication prose.

## Live now

**15 Sep evening, paper v1 rebuilt from thesis v2** (paper `4c1f3bc`,
pushed). `main.tex` → `sections/01…08` + appendices A–E; new abstract,
7 RQs, no trajectories, Gold figures under `figures/results/`. ~14.5
body pages; seven page-cut options wait for Walter in
`2026-09-15-paper-rebuild-golden-inventory.md` §0. Edits from here go
in `\Rev{}`.

**15 Sep evening, thesis text frozen.** All `\rev{}` wrappers
stripped; review-mark macro gone. Boxplots stay on
`fig:beh-profiles`. Still open: teacher comments if any, float /
page-break pass, cover flag, Thu 17 PDF.

**15 Sep evening.** Defence deck synced to the 15 Sep thesis
PDF: Goal 1 / personality / combos filled, rehearsal cut
applied (intent theory → appendix; retrieval before system).
`2026-09-15-presentation-results-sync.md`.

Newest first. Dated notes below this box are history; they do not
re-open a closed lock.

0. **Loop 3b reconciled, green pass in the source** (15 Sep midday).
   Ten jury dumps mapped onto one taxonomy
   (`review-3/reconcile/issue-taxonomy-seed.md`,
   `map-GM-MU-KK.md`, `map-DS-GX-CG-CS.md`), every claim checked
   against the `.tex` and frozen Gold, then ranked:
   `review-3/reconcile/ranked-issues.md` (canvas
   `loop-3b-jury-reconciliation`). Tier 1 (26 verified, cheap
   items, incl. Abstract and Ch 9 sentence-level) is applied in
   `\rev{}` green; `\useReviewMarks=1` is back in
   `dissertation.tex`. Tier 0 (nine science decisions, first the
   \(k\)-sweep on the early−late posterior \(\alpha\) cell) waits
   for Walter. Local compile:
   `docs/overleaf/thesis/_build/dissertation-rev-15sep.pdf`.
   Flip `\useReviewMarks` to 0 and strip `\rev{}` before the
   submission PDF. Not pushed.
0. **Five-LLM jury, two iterations** (15 Sep). Plan: judge on v1 →
   apply v2 → judge on v2 → apply v3 → final. Prompt:
   `2026-09-11-thesis-review-metaprompt.md`. Index:
   `review-3/jury-README.md`. v1 five-pack is in: Deepseek,
   Grok 4.6 web think-low, ChatGPT, Claude Sonnet 5, Gemini 3
   Pro (`review-3/jury-v1-gemini-3-pro-full.md`; full 156-pp
   PDF. Truncated first pass kept as
   `jury-v1-gemini-3-pro.md`).
   Extra in-IDE dumps: Muse 1.3, Kimi K3 Max, Opus 5,
   Fable 5.1, GPT 5.6 Sol
   (`review-3/jury-v1-gpt-5.6-sol.md`). Reconcile-later
   prompt:
   `review-3/ensemble-jury-reconciliation.md`. Wait for Walter
   before apply. Full local PDF:
   `docs/overleaf/thesis/_build/dissertation.pdf`
   (156 pp; do not commit/push).
   Do not apply from one jury unless Walter says so. Do not treat
   jury table cells as Gold.
0. **Thesis v1, source cleaned for the jury** (14 Sep evening).
   Walter accepted the loop-3 prose. Green marks off; every
   `\rev{}`, `% WALTER:` / `% WALTER+:`, `% [AI:]`, and the
   reviewer-attack-surface block are gone from the `.tex`. Provenance
   `% NUMBERS:` lines stay. Do not put review chat back in the
   manuscript. Note:
   `2026-09-14-thesis-v1-source-clean.md`.
0. **Weekend finish board** (12 Sep midday). Section finish %, what
   Walter still writes, what must not be reopened:
   `2026-09-12-weekend-finish-board.md`. Cover title switch is
   `\usePaperTitle` in `dissertation.tex` (**1** = paper title).
   `AGENTS.md` is the router only; details live here and in
   `analysis/README.md`.
0. **PNG + merge audit** (12 Sep morning). Montage is now a vector PDF
   (`fig:eeg-montage`). Three PNG includes remain (two UI screenshots,
   Qwen architecture). Eight `WALTER:` lines dropped at `d4f47a7` are
   restored in `results.tex` (36 again, matching `8559732`). Gold-tables
   figure no longer breaks the §4.2 sentence. Report:
   `2026-09-12-png-and-merge-audit.md`. Not pushed until Walter says so.
1. **Review loop 2 closed and pushed** (12 Sep 09:20, Overleaf `034f5d3`;
   later HEAD `ba05649` after Walter's Overleaf edits + gold-tables /
   RQ9 / D3). Compile verified, 156 pp, 0 undefined refs. Walter
   rewrites §4.2.2 from the draft, attacks the statistics, runs the
   five-chatbot jury with `2026-09-11-thesis-review-metaprompt.md`, then
   loop 3. G1 voice-read is parked for that loop. Checklist:
   `2026-09-11-review-loop-2-checklist.md`. Reports: `review-2/`.
   Voice: `.cursor/rules/thesis-voice.mdc`.
1. **External-reviewer meta-prompt** (11 Sep; closer updated 14 Sep
   evening). Copy-paste block for chatbots that get the thesis PDF
   only (no repo): `2026-09-11-thesis-review-metaprompt.md`.
   Everything after the `---` is the prompt. Full-PDF pass with
   suggestions in every chapter; weight on Abstract, Methods §6.3,
   Results, Discussion, Conclusion. PDF-only wording; no LaTeX
   labels or Gold filenames.
1. **Review loop 1 closed** (10 Sep evening, thesis `1f93146`).
   Table-first Results, `\promptbox` appendices, App **E** =
   behavioural (was F), App **F** = trajectories (was E), BH gone,
   rainclouds / D.4 / confirmatory EEG appendix tables / traj
   exploratory estimators gone.
1. **Personality family estimated** (10 Sep). Declared LMM on Walter Gold
   \(N=54\): 0/60 Holm. Results `sec:results-personality`, Discussion 8.2
   rewritten, App E `sec:app-beh-personality`. Not Katerina's \(n=19\)
   Spearman. Script:
   `analysis/walter/behavioural/stats/run_personality_declared.py`.

1. **Final narrative from Walter's notebook** (8 Sep evening):
   `2026-09-08-final-narrative-from-notebook.md`. His TLDR, fabricated
   narrative, EEG two angles, provider / people takeaways. Register
   only. Do not paste into `conclusion.tex`.
2. Four-family narrative example (longer register, **not** live LaTeX):
   `2026-09-08-four-family-narrative-example.md`. Implication-first
   paragraphs with signs and variable names. Do not paste into
   `conclusion.tex`.
3. **Do not drop** `llm_reliable` / `llm_opinionated` /
   `llm_skeptical` from the battery. Item-correlation rerun is held;
   answered 8 Sep evening as **sensitivity only** (Appendix F
   `sec:app-beh-items`: odd-polarity artefact; credibility early − late
   is carried by `llm_reliable`; LOO grid 4/45 verdicts move both ways).
   Also new that evening: `fig:beh-holm-board`, `fig:beh-d-rainclouds`,
   `fig:beh-item-forest`, 8.2 personality declared gap, Results opener
   fixed for combos, Appendix C marks the four secondary reversals.
   `../data-analysis/behavioral/2026-09-08-item-correlations-held.md`.
3. **Calendar (read first).** Thesis still due **Thu 17 Sep**. Defence
   is **Wed 23 Sep morning** in Padova, not 18–20. Fri 18 morning →
   Madrid HackSpain (weekend there). Mon 21 midday fly Padova. Tue 22
   rehearse. Fri 25 graduation. Paper after that, before SF.
   Barcelona Grok bot meetup he hosts: **Tue 29 Sep**. Full board:
   `2026-09-08-travel-and-delivery-calendar.md`.
4. Behavioural Ch 7.2 / 8.1 + Methods row + Appendix F — **applied and
   pushed 8 Sep, thesis `15cf438`**. Paired \(t\) primary (LMM adjusted
   check), 16 confirmatory tests, Katerina's omnibus/pairwise design on
   Gold \(N=54\) as post hoc appendix, her `fb7e426` reviewed (n = 19 incl.
   crowdfail; α double-reversal bug). Abstract / Conclusion comments only.
   `2026-09-08-behavioural-ch7-ch8-applied.md`.
5. Combos into Ch 7.5 / 8.5 — **applied and pushed 8 Sep, `d206df3`**:
   `2026-09-07-combos-ch7-ch8.md`.
6. (history) Behavioural readiness inventory:
   `2026-09-07-ch7-ch8-behavioural-ready.md`. Its open decision is closed.
7. Gold catalog for Ch 4 (`fig:gold-tables` included 12 Sep; §4.2.2 draft
   in, Walter rewriting):
   `../data-analysis/2026-09-07-gold-catalog-and-lineage.md`.
8. Do **not** overwrite live `conclusion.tex`. Chapter 8 must not
   restore fused how-and-when / serving-rule / MDE language:
   `2026-09-06-conclusion-critique-and-ch8.md`.
9. Results figure-first; Dataset A is **condition aggregation**;
   EEG MDE withdrawn: `2026-09-06-results-readability.md`.
10. Standing: Results ≠ Discussion; trajectories thesis-only;
   \(f_{\mathrm{genre}}\); implicit / explicit.

## Source of truth

**The only source of truth for manuscript content is the Overleaf Git
repositories under `docs/overleaf/`.** Context documents here summarize
decisions and working agreements; they do not override LaTeX. Before drafting
or editing, pull the relevant mirror and verify claims against the current
`.tex` / `.bib` files.

```text
docs/overleaf/publication/   # publication paper (primary writing target)
docs/overleaf/thesis/          # dissertation
docs/overleaf/presentation/    # slides
docs/overleaf/angela-paper/    # teammate EEG/ACL reference
docs/overleaf/example-eeg/     # EEG report template reference
```

Each Overleaf folder is an independent Git repository. The parent repository
ignores their contents. Run `git` commands inside the relevant mirror.

**Results ≠ Discussion (standing).** Results report numbers. Discussion
interprets. EEG 6.3 is confirmatory; 7.3 is the EEG read. Lock:
`2026-08-21-results-vs-discussion-and-eeg-6-3-pushed.md`.

**Ch 7.2 / 8.1 behavioural ready (7 September, evening).** Thesis-grade
figures + LaTeX tables in
`analysis/walter/behavioural/outputs/figures/thesis/`; inventory,
Results sentences, Discussion claims, and the one open decision
(Methods row says LMM; framework says paired \(t\); they differ on
one cell, trust early − late) in
`2026-09-07-ch7-ch8-behavioural-ready.md`. Not applied to Overleaf.

Behavioural Gold / combo joins (7 September):
`../data-analysis/behavioral/2026-09-07-behavioural-gold-and-combos.md`.
Catalog and lineage (same evening, **read this for Ch 4**):
`../data-analysis/2026-09-07-gold-catalog-and-lineage.md`.
Thesis §4.2.2 had been a stub; a Gold draft is in as of 12 Sep and
Walter is rewriting it. `fig:gold-tables` (`gold_tables.pdf`) now
opens §4.2. Draft plan (applied):
`2026-09-07-ch4-gold-tables.md`. Combo tests are in (0 Holm / BH).
Reduced blocks (7 Sep night):
`../data-analysis/behavioral/2026-09-07-combos-reduced-blocks.md`
— 336 tests, Block 0 is the finding; Discussion only, not Results.

Dataset A display name is **condition aggregation** (6 September).
Estimator is still the median of \(k=37\) tiles nearest onset.
Do not write “equal-n neighbourhood” or “condition state”.
`2026-09-06-condition-aggregation-and-traj-position.md`.

Equal-n Dataset A \(k=37\) (31 August). Applied and **pushed** to
thesis, paper, and presentation the same day. Discussion read:
`2026-08-31-equal-n-k37-manuscript.md`.

Channel-set / literature-ROI EEG is sensitivity, not confirmatory
Results. George nine-site and Wang-zone branches stay appendix-only.
Lock: `2026-08-24-channel-set-sensitivity-not-confirmatory.md`.

Genre classifier notation (23 August): \(f_{\mathrm{genre}}\), not
\(f_\theta\). Lock: `2026-08-23-f-genre-notation.md`.

Thesis experimental-data section (Ingestion / Trajectories Gold /
EEG lake) drafted locally 23 August, **not pushed**:
`2026-08-23-thesis-experimental-data-drafted.md`.
EEG preprocessing + Dataset A/B Gold tables ported from paper 5.6:
`2026-08-23-thesis-eeg-gold-ported.md`.
Broader paper→thesis ports (theory chapter, Methods, EEG Results,
appendix, Future Work), pushed 23 August:
`2026-08-23-thesis-paper-ports.md`.
Trajectory `head(5)` examples + EEG construction math restored
in Dataset (local thesis, not pushed):
`2026-08-23-thesis-examples-and-eeg-math.md`.
Thesis EEG Preprocessing / Epoching rewritten to the paper's register
(named paragraphs, purpose of each transform stated; numbers and locks
unchanged), **pushed 25 August (thesis `28c22c8`)**:
`2026-08-25-thesis-eeg-preprocessing-rewritten.md`.
Thesis Methods **Statistical Framework** rewritten: estimator primer with
each null before the table, no "as above", 14 families, every formula
checked against the analysis code, **pushed 27 August (thesis `041e1d5`)**:
`2026-08-27-statistical-framework-rewritten.md`. Cut hard the same day
(`1a3df60`): the estimator glossary is gone, the section opens with a
six-bullet design/sample/unit/status/threshold/reporting itemize, \(D_i\)
is a named planned contrast introduced through a worked instance, and the
prose after the table is ~400 words holding the two equations and the
Dataset A weight vectors.

Thesis **Results §7 and Discussion §8 skeletons** now mirror each other
section for section, with three distinct summaries (Results 7.7 table,
Discussion 8.1 prose, Conclusion still empty). Do not reorder one
without the other or without `tab:analysis-families`:
`2026-08-27-results-discussion-skeleton.md`.

Front matter audited and three files pushed the same day (`c34f9e2`):
the Descartes epigraph said "functions" where the Latin is *chimerae*,
the companion note promised publication pre-review, and `abbr.tex` still
shipped the template's "FTC, Fundamental Theorem of Calculus" as its only
acronym. `thanks.tex` is **held** — Walter writes it live on Overleaf and
the merged draft is stored in the note, not in the repo. `abstract.tex`
still reads `LOREM IPSUM LACKING AN ABSTRACT`:
`2026-08-27-front-matter-pass.md`.

EEG Results 6.3 is on Overleaf (pushed 21 August). Local-draft history:
`2026-08-20-eeg-results-section-drafted.md`.

Trajectory Results 6.4 + a new trajectory appendix, **pushed to the
publication Overleaf 23 August (`eef01b5`)**. Walter retouches in
Overleaf from here; the thesis port waits until the paper version is
agreed. Reference copy of the draft, with the provenance comments:
`2026-08-23-trajectory-results-draft.tex`. That commit also carried the
`f_theta` → `f_genre` rename, which had been sitting uncommitted.

6.4 replaces the old SKELETON block: descriptives summarised in three
paragraphs, the confirmatory family in four, one table, two figures.
The appendix (`sec:app-trajectories`) carries the full per-condition
tables, the bare-versus-contextual trade-off, the six-window context
sweep, and the exploratory estimators. Four figures already copied into
`publication/Figures/` as `s24_crossing_forest`, `s24_depth_versus_ad`,
`traj_heatmap_both`, `traj_label_validity`.

Two standing constraints in that text. Hard labels only: the continuous
posterior version of Definition 6 was cut for the same provenance reason
as Jensen--Shannon (runtime logged argmax; posteriors were recomputed
offline), and a comment in `main.tex` records that. And nothing in 6.4
interprets — the bounded-null reading, the advertising implications,
Definition 6 as a weak instrument, and classifier stickiness as a
limitation are all still owed to 7.3 and 7.5.

EEG paper figure cut and Results sentences (20 August):
`../data-analysis/eeg/2026-08-20-paper-figures-and-narrative.md`.

Monday agenda (Katerina + Sebastian):
`2026-08-20-monday-katerina-sebastian-agenda.md`.

Newest snapshot (completion %, STATUS map):
`2026-08-19-completion-snapshot.md`.

**7 September evening (newest writing):** combos into Ch 7.5 / 8.5.
Methods declares **6** behaviour × EEG pairs (not 8) and does not fix
\(D^A\) vs \(D^B\); both reported, Holm within six each. Dataset A
0/6; Dataset B trust × posterior \(\alpha\) \(\rho=.80\) \([.48,.93]\),
Holm .0004 (also Holm-12 .0007, Holm-16 .001). Trajectory pairs and
three-way null; Fz \(\theta\) × \(\delta^{(a)}_2\) is .47, Holm .095,
reverses under the contextual labelling. **Applied and pushed 8 Sep,
thesis `d206df3`** (7.5, 8.5, Methods 6.1 association rows, two summary
tables, figures); abstract and conclusion got `% [TODO combos]` comment
drafts only, nothing live. The push also carried the 6 Sep Ch 8 rewrite.
Text: `2026-09-07-combos-ch7-ch8-draft.tex`. Lock and the `spearman_ci`
positional-alignment bug: `2026-09-07-combos-ch7-ch8.md`. Behavioural
agent's 7.2 / Methods-row edits were in the same working tree and were
**not** staged; they sit on top of `d206df3`.

**6 September evening (HIGH IMPORTANT):** Conclusion critique +
Chapter 8 lock. Do not overwrite live `conclusion.tex`. Do not
restore “depends on how and when”, “greater visual processing”,
explicit-late-as-compromise, or MDE. Discussion has no
`sec:disc-summary`. Note:
`2026-09-06-conclusion-critique-and-ch8.md`.
Rule: `.cursor/rules/discussion-interpret-not-serve.mdc`.

**6 September (newest writing):** Results figure/table-first.
Holm = paired \(t\) only; Wilcoxon raw. Dataset A is
**condition aggregation**. `fig:traj-position` navy bar is
\(\delta_2\) only. Pushed thesis `f6b7ecf` (on Walter's
`0fb0881`) and paper `8ef03d4`.
`2026-09-06-results-readability.md`.
EEG MDE withdrawn from thesis, paper, and deck the same day.
Do not restore `eq:mde`. `2026-08-31-thesis-eeg-mde.md`
is historical only.

**5 September (historical):** sprint calendar. Defence 18–20 is
**wrong** — see the 8 Sep travel board. Combos no longer wait.
`2026-09-05-sprint-to-deadline.md`.

**31 August:** equal-n Dataset A \(k=37\)
applied and pushed to thesis, paper, and presentation.
`2026-08-31-equal-n-k37-manuscript.md`.

**4 September:** defence rehearsal cut. Intro gets ~5
minutes. Intent theory (`Theoretical Work (2)`) off the
spoken path. Retrieval pipeline image immediately before
the system-architecture slide. Stay inside 20 minutes.
Deck not edited in that pass.
`2026-09-04-presentation-rehearsal-cut.md`.

**31 August:** “slow-power response” lock for
the High-level discussion slide. Five explicit-early cells are
one low-frequency tilt, not five findings. Dataset A any-ad is the
“no overall condition difference.” Do not rewrite his wording.
`2026-08-31-slow-power-and-high-level-discussion.md`.

**31 August:** thesis EEG MDE. Formula
`eq:mde` in Methods; dB / observed power / \(n_{80}\) in
Results; “precise A / underpowered B” stays Discussion.
`2026-08-31-thesis-eeg-mde.md`.

**31 August:** defence save. Appendix EEG now
opens on the five bands + `images/misc/waves.jpg`. How Holm MDE
and observed power are computed, and the \(n=18\) numbers
(Dataset A 0.22–0.44 dB after equal-n \(k=37\); Dataset B 1.7–3.7 dB):
`2026-08-31-presentation-eeg-waves-and-power.md`.

**29 August:** defence **title page** (UniPD top;
UPC+Telefónica footer; two-column people, name flush left, colons,
type below the titles smaller than the titles).
`2026-08-29-presentation-title-page.md`.

**29 August:** defence-deck flow pass. Intro is the live spoken
thread. Rollback SHA `d5d42ab`. Iteration commits `deck-iter-N:`.
`2026-08-29-presentation-flow-pass.md`.

**28 August:** defence Beamer skeleton in `docs/overleaf/presentation/`.
Six spoken sections (Intro, RQs, Methods, Results, Discussion,
Conclusions). Theory off the clock. Goal 1 / combos are grey blocks.
`2026-08-28-presentation-skeleton.md`.

**28 August:** EEG framing locked as three tiers (confirmatory /
exploratory / post hoc). Report the six Dataset B cells as a
**format-specific** result, do not lead with caveats, and never write
"approached significance". MDE is withdrawn (6 September).
Methods, Results and Discussion updated in the thesis.
`2026-08-28-eeg-three-tier-framing.md`.

**28 August (newest analysis save):** channel-set retry closed;
primary 32-ch stays confirmatory. Do not pick a montage by Holm.
`../data-analysis/eeg/2026-08-28-channel-set-closed.md`.

**27 August:** afternoon catch-up so figure regen, Dataset A/B
pixels, Rainie/WildChat, Flow Design split, and crowd age in 7.1 are
not chat-only: `2026-08-27-afternoon-save.md`.

**27 August:** Walter is hand-polishing thesis Ch 5–6. Five analyses
are the remaining science this window (Angela sensors, EEG post-hoc,
behavioural EDA, free-text, joined dataset). Thesis first; paper
optional; start the presentation. Board:
`../data-analysis/2026-08-27-backlog-and-timeline.md`.
Writing track: `2026-08-27-writing-push-and-delivery.md`.

**25 August:** experiment flow / questionnaire order / why-this-order
assumptions for thesis Methods **Flow Design**. Live source is
`controller.py`. 27 August addendum: IVs first, two-subsubsection
split (mitigable biases vs remaining confounds).
`2026-08-25-experiment-flow-design.md`.

**24 August:** Trajectories are thesis-only. Paper keeps taxonomy and
\(\pi\); no Defs 1–6, no 6.4, no trajectory Discussion/appendix.
Thesis order: Dataset → System → Methods → Results → Discussion →
Conclusion. A short front-matter note (`frontmatter/companion.tex`)
states that discrepancy (pushed 25 August, thesis `3dc42f5`). Lock:
`2026-08-24-trajectories-thesis-only.md`.

**24 August:** Discussion split into the four analyses
(`sec:disc-behaviour`, `sec:disc-eeg`, `sec:disc-trajectories`,
`sec:disc-combos`). Trajectory lock: Holm-null \(\neq\) theory is
wrong; refine with what is fed to \(f_{\mathrm{genre}}\).
`2026-08-24-discussion-four-analyses.md`.

**24 August:** erase the insertion-policy model from paper and thesis
(contribution, Predictive Analysis / RQ12–RQ14, Results skeleton,
Discussion / Future Work apology). Keep \(\pi\) as theory and timing.
Locks: `2026-08-24-insertion-policy-model-dropped.md` and
`../data-analysis/2026-08-24-insertion-policy-model-dropped.md`.

Canonical goals until the thesis is in (science 1–5 + thesis / paper /
presentation). List: `../data-analysis/2026-08-23-goal-list.md`.

Crossable leftover items (paper / thesis / analysis / slides):
`2026-08-18-remaining-work-checklist.md`.

EEG Method comments parked in Overleaf (median / \(Y_A,Y_B,D\) / short cite
set). Visible `EEG Epoching` was pushed 20 August (`cf48a14`):
`2026-08-20-eeg-epoching-section-drafted.md`.
Parked-comment history:
`../data-analysis/eeg/2026-08-19-literature-justifications-in-overleaf.md`.

## Entry order

1. Read this README.
2. Prefer the newest dated entry in this directory.
3. For analysis facts that constrain writing (sample sizes, EEG constraints,
   exclusions), verify against `.agents/context/data-analysis/` and executable
   code/manifests—then confirm the manuscript still matches Overleaf after
   any rewrite.

## Author workflow

1. Pull Overleaf before drafting or editing.
2. Show proposed text before applying it.
3. Do not push until Walter explicitly approves the displayed version.
4. Do not commit or push Overleaf mirrors unless explicitly requested.
