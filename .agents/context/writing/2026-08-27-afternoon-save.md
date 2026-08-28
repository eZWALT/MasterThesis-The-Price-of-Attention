# Afternoon save (27 August 2026)

Catch-up note so the late-day Overleaf and figure work is not only in
chat. Earlier 27 August notes still stand (statistical framework,
Results/Discussion skeleton, front matter, writing push, backlog,
Dataset A/B rename, free-text plan, crowd age). This file is the
index plus what those notes do not yet say.

Do not overwrite `thanks.tex` or Walter's dedication quotes. Pull
Overleaf before editing. ICA archive untouched.

## Five Methods/Results comments (thesis `7afc524`)

Walter's `% AI:` notes, resolved the same day:

1. **Flow Design split.** Two subsubsections: biases *ordering can
   mitigate* vs confounds it *cannot* (disclosure confounded with
   \(\lambda\); \(\delta^{(a)}_k\) undefined after turn 4; inattention
   is not an exclusion; EEG is lab-only). Title of the IV section
   stayed **Laboratory conditions**. Details:
   `2026-08-25-experiment-flow-design.md` (27 August addendum).
2. **IVs first.** `Conditions and Independent Variables` is now the
   first Study Design block; Experimental Design points at
   `sec:methods:ivs`. The \(2\times 2\) factorial wording lives in that
   opener (it had only existed in a cut paragraph).
3. **Rainie 2025 was wrong on two claims.** 65% is *spoken* voice
   conversations, not a text-chat justification. 75% products/services
   does **not** exist in the report. Session brevity now cites
   **WildChat** (Zhao et al.: 2.52 turns, 41% \(\ge 2\) turns, 3.7%
   \(>10\)) and **LMSYS-Chat-1M** (Zheng et al.: 2.0 turns). Rainie
   kept only for 51% personal vs 24% work. Bib keys:
   `zhao2024wildchat`, `zheng2024lmsyschat1m`.
4. **Path A/B → Dataset A/B.** Walter overruled `sustained` /
   `onset-locked`. Symbols \(D^{A}\), \(D^{B}\) unchanged. A dataset
   is never the subject of a test: write "the Dataset A **contrasts**
   test…". Lock: `../data-analysis/eeg/2026-08-27-dataset-a-b-rename.md`.
5. **Results 7.1.** Kept. Lead with exclusions. Dropped "as stated in
   Methods." Crowd age added later the same day (below).

## Dataset A/B figures actually rebuilt

The rename commit (`333f903`) only retitled files and LaTeX. Matplotlib
pixels still said "Path A / Path B". Later the same day:

- Fixed `plot_eeg_only_heatmaps.py`: `matrix()` compared
  `grid["path"]` to an undefined `path` after the selector became
  `dataset` (would have crashed a rebuild). The CSV column is still
  named `"path"` with values `"A"` / `"B"`.
- Regenerated Holm heatmaps (including after-reply), channel-set
  Holm boards, the publication suite (forests, epoch grid, ICA
  agreement, …), and `eeg_pipeline_v2.{png,pdf,svg}`. Channel-set
  supertitles: `Path {A/B}` → `Dataset {A/B}`.
- Parent-repo commit: `3fe3243`. **No ICA overwrite.**

Copied into both Overleaf trees:

| Generator | Overleaf stem |
|---|---|
| `figure_08_confirmatory_forests` | `eeg_confirmatory_forests.{pdf,png}` |
| 4 s Holm board | `eeg_holm_board_4s.{pdf,png}` |
| `eeg_pipeline_v2` PNG | `eeg_preprocessing.png` |

- Thesis Overleaf: `16e6ff8`.
- Paper Overleaf: `030471f` — same three figures **and** Path→Dataset
  in `main.tex` (captions, Results, `tab:eeg-dataset-a/b`). Same
  category-error rewordings as the thesis.

Filenames said Dataset before the pixels did. If you rebuild again,
check a Holm board *and* the forests, not only `ls`.

## Crowd age in 7.1 (prose only)

Not Gold. Zip not in git. Among 26 of 36 finished crowd participants
with a numeric age in a Prolific snapshot: \(M=35.69\),
\(\mathrm{SD}=9.51\), range 23–56, \(\mathrm{Mdn}=34.5\). Nine
finished sessions after the zip; one linked participant revoked
demographic consent. Lab age stays intake (21–42, \(M=29.50\),
\(\mathrm{SD}=5.01\)). `fig:sample-demo` still omits age.

Full join and missingness:
`../data-analysis/behavioral/2026-08-27-crowd-age-prolific-estimate.md`.
Thesis Overleaf sentence: `b503482` (later figure commits may have
shortened 7.1 — pull before rewriting).

## Other 27 August notes (already written)

| Note | Job |
|---|---|
| `2026-08-27-statistical-framework-rewritten.md` | Methods estimator primer, then hard cut (no glossary) |
| `2026-08-27-results-discussion-skeleton.md` | Ch 7 ↔ Ch 8 mirror; † rows gated on Goal 1 |
| `2026-08-27-front-matter-pass.md` | dedication / companion / abbr / title page; **hold `thanks.tex`** |
| `2026-08-27-writing-push-and-delivery.md` | Ch 5–6 quality pass; thesis first |
| `../data-analysis/2026-08-27-backlog-and-timeline.md` | five pending analyses |
| `../data-analysis/eeg/2026-08-27-dataset-a-b-rename.md` | naming lock + later figure regen |
| `../data-analysis/behavioral/2026-08-27-free-text-codebook-and-llm-judge.md` | Goal 4 plan |
| `../data-analysis/behavioral/2026-08-27-crowd-age-prolific-estimate.md` | 7.1 estimate |

Parent-repo context dump for the 23–25 August notes that had sat
uncommitted: `8e60c1e` (writing/goals), `0870525` (channel-set),
`017f1f8` (trajectories Gold), `fd5dac5` (pipeline figures).

## Still open (do not forget)

- `abstract.tex` is still `LOREM IPSUM LACKING AN ABSTRACT`.
- `thanks.tex`: surnames for Angela / Sebastian / Katerina; finish
  the younger-self sentence; apply the merged draft only when Walter
  stops editing live Overleaf.
- Related Works and Dataset (Product Catalog / EEG Data) subsections
  still empty.
- Goal 1 battery + combos still block Results 7.2 / 7.6 and H1–H3.
- Trajectories context filenames still peak at 23 August; the pipeline
  itself was git-saved today (`017f1f8`).
- Parent `origin` may lag local `main` (figures `3fe3243`, crowd-age
  note `a0ae2d1`). Do not push unless asked.
