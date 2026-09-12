# PNG conversion + Overleaf-merge audit (12 Sep morning)

Two jobs Walter asked for after loop 2: (1) finish PNG → vector PDF;
(2) check whether yesterday's merges dropped backlog.

## 1. Figures

Yesterday's WP2 already swapped every matplotlib Results/Appendix figure
and the four diagram includes (`system_architecture`, `ads_data_pipeline`,
`trajectory_preprocessing`, `eeg_preprocessing`) to PDF. What was still
a PNG *include* this morning was the montage.

`fig:eeg-montage` now includes `figures/preprocessing/eeg_montage.pdf`
(0 embedded rasters). Generator: `src/project/docs/eeg_montage/make_eeg_montage.py`.
The 32 labels are the XDF contract, not the 16-channel test fixture the
old script was reading. Confirmatory sites (Fz; O1 Oz O2 P3 Pz P4) are
filled. The old PNG is still on disk as a preview; it is not included.

Three PNG includes remain, on purpose:

| File | Why it stays PNG |
|---|---|
| `figures/ui/implicit_ad.png` | UI screenshot |
| `figures/ui/explicit_ad_2.png` | UI screenshot |
| `figures/models/qwen3.6.png` | third-party architecture drawing (Sebastian Raschka); no vector source in the repo |

Diagram PDFs from the `diagrams` library still embed their icon PNGs
(system architecture 28, ads pipeline 12, trajectory pipeline 16,
retrieval 14, flow_lab 24, flow_crowd 26). The page include is PDF;
the icons were not redrawn. `gold_tables.pdf` is fully vector.

All 26 other thesis includes: 0 rasters (`pdfimages -list`).

## 2. Merge: what was dropped, what was not

Comment counts against Walter's review-2 dump (`8559732`):

| File | `8559732` | after first merge | HEAD after this restore |
|---|---|---|---|
| `results.tex` | 36 | 28 | **36** |
| `discussion.tex` | 45 | 45 | 45 |
| `conclusion.tex` | 3 | 3 | 3 |
| `abstract.tex` | 1 | 1 | 1 |
| `dataset.tex` | 0 | 0 | 2 (Walter added today on Overleaf; kept) |

The eight `results.tex` comments that vanished at `d4f47a7` sat on the
*old* Results Walter commented without reading. They were treated as
review-1 closures and deleted. That broke the "never delete a `WALTER:`
line" rule. They are back, each with a one-line `% [AI: …]` status:

- boxplot vs four-arm profile — **still his call** (we kept the profile)
- Friedman sentence, notice shortening, figure pile-up, Wilcoxon primer,
  epoch-width table, BH — work already done; comment restored so the
  thread is visible

Labels that "disappeared" from `8559732` are the review-1 punch-list,
not merge loss: `fig:beh-forests` and `sec:results-combos-three-way`
removed; `tab:eeg-width` moved to App D; E/F swapped (behavioural is
now E, trajectories F); D.4 channel-sets / confirmatory appendix tables
erased as he asked. Zero undefined `\ref` / `\autoref` remain.

Today's three Overleaf merges (`a849d04`, `a984d3c`, `ba05649`) only
touched `dataset.tex`. They did not drop comments. They *did* glue the
gold-tables figure into the middle of a sentence
(`\end{figure}; laboratory runs carry both`). That sentence is restored.

## 3. Tables: no leftover backlog rows

- `tab:rq-answers`: nine questions, every cell filled (3 supported, 1
  partly, 5 not supported). No empty / TBD / WIP cell.
- `tab:results-summary` / `tab:results-checks`: every Methods family and
  every reported check has a row. The free-text row says "not analysed"
  on purpose (declared, not estimated). `--` in Tests/Sig. is for
  non-Holm or non-tested rows, not unfinished work.
- Review-loop-2 checklist: all WPs `done`. Voice-read (G1) is the only
  item parked for loop 3, as Walter ruled this morning.

Rendered PDF has no `WIP` / `TODO` / `XXXXX` / "still being frozen".
Those strings survive only inside `% WALTER:` comments.

## 4. Not destroyed (intentional closures)

Review-1 items that look like "missing backlog" if you diff `8559732`:
rainclouds, BH columns, confirmatory EEG appendix tables, D.4, traj
exploratory estimators, three-way combos subsection. All closed on
purpose, tagged `% [AI: closed in review 1 …]` above the appendix
punch-list.
