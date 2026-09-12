# Agent entrypoint

Router for a new agent. This file is not a changelog, not a Results
sheet, and not the place for dated status. Those live under
`.agents/context/`.

> **CRITICAL (EEG / ICA).** Do not run `fit_ica_cohort.py --overwrite`
> or `run_ica_sensitivity.py --overwrite-models`. Do not replace files
> under `src/project/logs/xdf/silver/ica/candidate_v1/`. Those 18 models
> are human-signed (2026-08-19).
> `.agents/context/data-analysis/eeg/CRITICAL-do-not-overwrite-ica-models.md`

## Pending (temporary — remove after 17 Sep)

Visible board. Science 1–5 is frozen. Details:
`.agents/context/writing/2026-09-12-weekend-finish-board.md`

### Thesis, this weekend

- [ ] **§4.2.2** — text is in; leftover comments only (spine→grains, \(N=54\) once, optional pipeline figure)
- [ ] **Ch 1 / 5** (~85%) — content is in; user-centric pass only. Not a rewrite
- [ ] **Ch 2** (~85%) — stays compact on purpose. Do not add context. User-centric closer only; drop the leftover “Publication Related Work” heading
- [ ] **Statistics attack** — Walter on Overleaf Ch 7–8. Open = `% WALTER:`; done = `% WALTER+:`
- [ ] **Five juries** — compile PDF; paste `2026-09-11-thesis-review-metaprompt.md`; save under `.agents/context/writing/review-3/`
- [ ] **Loop 3** — apply his comments + the five juries. Abstract and Ch 9 last, one agent, no wholesale rewrite
- [ ] **Mechanical leftovers** — `models.tex` still mentions an FDR \(q\); Results still prints a Gold filename; boxplot-vs-profile on `fig:beh-profiles` is still his call
- [x] **Chapter titles** (his 12 Sep Overleaf note) — Related Work & Context → Related Work; Dataset → Datasets; shorten “AI System Design & Engineering”; unify title case
- [x] **Methods 6.2** — put dependent variables next to independent variables; reorder the subsection
- [x] **Results / Discussion titles** — match 100% (genre trajectories is the example)
- [ ] **Captions** — final pass (loop 3 WP-E running): relevant, not repeating the figure; OCR the images
- [ ] **Page breaks / float placement** — after chapter feedback is applied
- [ ] **Tell Katerina** — design re-run on Gold \(N=54\), 0/70; her tree stays read-only
- [ ] **Thesis PDF** — Thu 17 Sep. Cover is `\usePaperTitle=1` (paper title). Flip to `0` for the long thesis title

Parked, not this weekend: G1 voice-read, free-text coding, ad-moment scorer, dataset release, paper, deck fill.

### Public-release housekeeping (after the PDF)

Data upload is a **side quest**, same shelf as the scorer. Do not start
it this week. Strategy:
`.agents/context/data-analysis/policy/2026-09-12-dataset-release-side-quest.md`

**Navigation (repo is hard to walk)** — after 17 Sep, no Gold moves:

- [ ] Root `README.md` title still says “Conversational Advertising…”; align with paper title after submit
- [ ] Two behavioural trees: `analysis/walter/behavioural/` is Gold; `analysis/behavioural/` is Katerina. Archive or rename hers so a stranger does not run it
- [ ] Empty / leftover docs: `docs/context/`, `docs/final/*`, `docs/generated/` (one Tang review). Archive or drop
- [ ] `src/notebooks/0_problem_definition.ipynb` (April leftover) — archive
- [ ] `scripts/Pilot_data_Inspection_Sebastian.py` — archive
- [ ] `.agents/context/` has ~150 dated notes. After 17 Sep, move closed ones under `context/_history/` so only Live now READMEs show
- [ ] EEG preprocessing READMEs are not live status (said in this file); add a one-line banner on each
- [ ] Duplicate matplotlib PNG+PDF pairs: keep PDF, drop PNG from git after public (UI screenshots stay PNG)
- [ ] Local folder is still `MasterThesis-RAG-RecSys`; GitHub is `MasterThesis-The-Price-of-Attention`. Rename local clone when convenient
- [ ] Overleaf extras `docs/overleaf/{angela-paper,example-eeg}` are reference clones, not this thesis
- [ ] `resources/papers/` (~139 MB PDFs) + `resources/books/` (copyrighted handbook): do not publish; git-lfs or a private bundle
- [ ] Executed analysis notebooks (2–8 MB) → HF or `analysis/_viewers/`, not the landing tree
- [ ] Root license: only `src/project/LICENSE` exists. Add a root LICENSE / CITATION.cff / dataset card
- [ ] `.gitmodules` points at someone else’s ad-insertion repo. Keep or drop on purpose
- [ ] Decide whether `.agents/` and `.cursor/rules/` ship in the public repo (useful for agents; contains review voice)

**Do not**

- Move Gold paths or rename confirmatory CSVs
- Touch ICA models
- Flatten `analysis/eeg/preprocessing/` Bronze/Silver/Gold
- Put `analysis/policy/` in the thesis or the public abstract

## Live now

Thesis PDF **Thu 17 Sep**. Defence **Wed 23 Sep** morning, Padova.
Paper after 25 Sep.

**Open this, then stop:**
`.agents/context/writing/2026-09-12-weekend-finish-board.md`

Loop-2 memory (comment → work package, model policy):
`.agents/context/writing/2026-09-11-review-loop-2-checklist.md`.

## How memory works

`.agents/context/` is the journal. Every track README has a **Live now**
box at the top. Dated files below that box are history. Do not reopen
them. Do not copy their unchecked boxes back into a to-do list.


| Track                               | Open, then **stop at Live now**                                 |
| ----------------------------------- | --------------------------------------------------------------- |
| Weekend board / manuscripts         | `.agents/context/writing/README.md`                             |
| Science decisions                   | `.agents/context/data-analysis/README.md` → then the arm README |
| Code map (which script, which Gold) | `analysis/README.md`                                            |
| Side project (not the thesis)       | `.agents/context/data-analysis/policy/README.md`                |


Root `README.md`, `.agents/README.md`, and
`analysis/eeg/preprocessing/README.md` are **not** live status.

Context notes never override the LaTeX. Manuscript source of truth is
only `docs/overleaf/{thesis,publication,presentation}/`. Pull before
drafting.

Always-on writing rules (voice, Results ≠ Discussion, figure-first,
Discussion locks) are the `.cursor/rules/*.mdc` files. Do not duplicate
them here.

## What this repo is

A master’s thesis on what advertising costs the user inside a
conversational assistant: theory, a purpose-built RAG platform
(`src/project/`), and five frozen analyses (behaviour, personality /
demographics, EEG, genre trajectories, associations). The platform is
not the analysis tree. The paper and the defence deck are later
targets, not this weekend.

## Hard stops

- Do not push unless asked. When merging Overleaf, never drop a
  `% WALTER:` / `% WALTER+:` comment. Flip to `% WALTER+:` when the
  ask is applied. Show text before applying when he is online.
- Conclusion and abstract are edited **last** in a review loop, by one
  agent, never rewritten wholesale. Jacket and Future Work are his.
- Do not put the ad-moment scorer in thesis / paper / deck before
  17 September. `analysis/policy/` is a side project.
- Do not pick a \(k\), montage, or questionnaire item by \(p\).
  `llm_reliable` / `llm_opinionated` / `llm_skeptical` stay in.
- Leave `src/project/` alone unless the task is the platform itself.
- **`analysis/behavioural/` is Katerina’s tree.** Read for
  reconciliation only. Never edit, run, or quote it. Thesis numbers
  come from `analysis/walter/behavioural/` on Gold \(N=54\).
- Never run `python analysis/eeg/preprocessing/run_pipeline.py`.
  Never quote suite rainclouds as confirmatory. Never pass
  `--force-overwrite-confirmatory` to `build_condition_contrasts.py`.
- Rebuilds and Gold paths: `analysis/README.md`. Re-plot from frozen
  outputs is always allowed; rebuild only if asked.

## Subagents

One work package per subagent. Each one reads the live board, does
that package, writes a report under `.agents/context/writing/review-2/`
(or `review-3/` in the next loop). Do not one-shot the whole thesis
in one context.


| Role                           | Slug                                       |
| ------------------------------ | ------------------------------------------ |
| Thesis / paper prose           | `claude-opus-5-thinking-high`              |
| Fact-check, second reader      | `gpt-5.6-sol-max`                          |
| Statistics, Gold re-estimation | `inherit`                                  |
| Plotting / table code only     | `cursor-grok-4.6-xhigh-fast` (never prose) |
| Never                          | any `composer-*`                           |


