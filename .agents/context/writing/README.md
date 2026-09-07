# Writing context structure

This directory holds durable writing decisions, Overleaf workflow notes, and
handovers for thesis and publication prose.

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

**5 September:** sprint to 17 September. Katerina
is back (two behavioural Holm survivors). Do not permute items to
hunt \(p\). Combos wait on that freeze. Thesis human pass in
progress (4.2.2, 6.3 last paragraph). Abstract 5 Sep.
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
