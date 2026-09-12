# Review loop 3 — master checklist (12 Sep 2026, midday)

> **STATUS: running.** Walter is writing Conclusion + Abstract himself,
> then re-reviews Ch 6–8 and pastes the five juries. This loop applies
> his eleven HIGH LEVEL COMMENTS (bottom of `dissertation.tex`) and
> hardens the Statistical Framework (`sec:methods:statistical-framework`).
> Reports go under `review-3/`. Push to Overleaf as each WP lands
> (Walter asked for the loop to run while he is away).

Source of the asks: `dissertation.tex` lines 64–84 (11 numbered items)
plus the standing rule "statistical framework is the crown jewel; any
change there propagates thesis-wide".

Comment tags: `% WALTER:` open, `% WALTER+:` addressed. Never delete one.

## Model policy (unchanged)

| Role | Slug |
|---|---|
| Thesis prose | `claude-opus-5-thinking-high` |
| Fact-check / second reader | `gpt-5.6-sol-max` |
| Statistics, Gold | `inherit` |
| Plot / LaTeX-table code only | `cursor-grok-4.6-xhigh-fast` (never prose) |
| Never | `composer-*` |

## Work packages

Status: `todo` · `running` · `done` · `blocked`.

### WP-A — Titles, 6.2 order, Results↔Discussion match — owner orchestrator — `done` (report `review-3/WP-A-report.md`)

Items 1, 2, 3, 4, 5, 6.

- Chapter titles: `Related Work \& Context` → `Related Work`; `Dataset` → `Datasets`; `AI System Design \& Engineering` → shorter, same information (candidates: `System Design and Engineering`; `Platform Design and Engineering`). Pick one, note alternatives in report.
- Case rule: chapters Title Case; every `\section` and below sentence case. Apply thesis-wide (Ch 1–9 + appendices).
- Methods 6.2: put `Dependent Variables` directly after `Conditions and Independent Variables`. New order: IVs → DVs → Experimental design → Laboratory conditions → Flow design and biases. Text moves only; no rewrite.
- Results 7.5 `Genre trajectories and intent theory` → `Genre trajectories` (Discussion already says that). Check every other Results/Discussion pair.
- `composites` → `outcomes`: grep prose (not `% WALTER` comments). Report count.
- Flip the six `% WALTER:` sub-items in `dissertation.tex` to `% WALTER+:` only as each lands (they are one comment block; add a one-line `% [AI: 1–6 applied; 7–11 see review-3]`).

### WP-B — Figures: drop in-plot legends, high-contrast palette, Holm mark standard — owner `cursor-grok-4.6-xhigh-fast` — `done` (report `review-3/WP-B-report.md`)

Items 9, 10, 11 (figure half).

- Every generator in the WP2 map (`review-2/WP2-report.md` §Analysis figures). Plot functions only; read frozen CSVs; never run stats mains; never touch Gold.
- Remove in-axes legends. Where a legend carried information the reader needs, return that text so the caption can carry it (`review-3/WP-B-report.md`, one row per figure: figure → what the legend said → one-line caption fragment).
- Palette: replace navy/teal/green with high-contrast **red `#D32F2F`, blue `#1565C0`, yellow `#F9A825`, purple `#6A1B9A`**. Holm marker stays the same **orange asterisk `#C45C26`**, placed at `xmax + 0.06·span` on forests; on boards use the same asterisk inside the cell. No text legend for it; the caption says "Asterisk: Holm \(p<.05\)".
- Save `format="pdf"`, no `rasterized`. Copy to `docs/overleaf/thesis/figures/results/`. `pdfimages -list` = 0 rasters.
- Do not edit any `.tex`.

### WP-C — Tables: one bold standard — owner `cursor-grok-4.6-xhigh-fast` — `done` (report `review-3/WP-C-report.md`)

Item 11 (table half).

- Every table in `results.tex`, `appendix_d.tex`, `appendix_e.tex`, `appendix_f.tex` and the generated `figures/results/tab_*.tex` that prints a Holm \(p\).
- Standard = `tab:beh-planned`: **the whole row bold when Holm \(p<.05\)**; nothing else bold; family divider `\midrule`; caption ends with "Bold rows survive Holm." if any row can.
- Wilcoxon is never bolded. Numbers never change. No caption rewrites beyond that one sentence. Report per table: rows bolded / unbolded.

### WP-D — Statistical framework hardening + propagation — owner `claude-opus-5-thinking-high` — `done` (report `review-3/WP-D-report.md`)

The crown jewel. Section `sec:methods:statistical-framework` in `chapters/models.tex`.

Known defects to fix:
- "exploratory families additionally carry a false-discovery-rate \(q\)" — BH is gone thesis-wide. Remove, and the "for the reason set out after that table" clause.
- `tab:analysis-families` free-text row says "descriptive coding, no inferential claim"; footnote says "collected and not analysed". Make them agree (not analysed).
- "6 genres labelling \(\ge 5\%\)" — `labelling` is a banned word; say "six genres carrying \(\ge 5\%\) of utterances".
- GEE, OR, mixed model, McNemar, permutation: each named once with a one-clause definition, or dropped.
- The section must survive: "was this pre-registered?" (no; say post hoc honestly, once, already there), "why Holm and not BH?" (one sentence), "why paired \(t\) on Likert?" (Wilcoxon sensitivity; LMM check), "why \(n=18\) for EEG?" (recorded arm only), "why 37 epochs?" (equal-\(n\) cell; that is Ch 4's number, keep one mention here), "why two EEG estimands?" (condition aggregation vs onset-lock, different questions).
- Keep the equations. Keep `tab:analysis-families`. Keep Walter's register: short paragraphs, direction in words.
- Propagation: any term you rename here must be grepped across `chapters/*.tex`, `frontmatter/*.tex`, `figures/results/tab_*.tex`, and `.agents/context/writing/README.md`. `tab:results-summary` rows must match `tab:analysis-families` rows one-to-one, same order, same names. Report the grep.

### WP-E — Caption audit — owner `gpt-5.6-sol-max` — `done` (report `review-3/WP-E-report.md`; applied 48 captions)

Item 7.

- Every `\caption{}` in `chapters/*.tex` and `figures/results/tab_*.tex`. For figures, open the PNG preview under `analysis/**/outputs/figures/thesis/` or render the PDF page.
- Judge: relevant; ≤ 2 lines; does not repeat the surrounding paragraph; does not restate what the image already labels; names the Holm mark once if the figure has one. After WP-B the in-plot legends are gone, so the caption may need one clause the legend used to carry.
- Output `review-3/WP-E-report.md`: one row per caption → verdict → proposed caption (or "keep"). Do not edit tex.

### WP-F — Page breaks and float placement — `blocked`

Item 8. Walter: "after all the feedback inside of the chapters has been applied". Do last, one agent, after the juries.

## Batches

1. WP-A (orchestrator) ‖ WP-B (grok) ‖ WP-E (sol) — now.
2. WP-D (opus) ‖ WP-C (grok) — after WP-A lands (they touch `models.tex` / table bodies).
3. Orchestrator applies WP-E captions + WP-B legend fragments; compile; push.
4. WP-F after juries.

## Log

- 12 Sep 11:35 — loop opened. `review-3/` created.
- 12 Sep 11:50 — WP-A done (46 headings, 6.2 reordered, 7.5 renamed, items 1–6 → `WALTER+`). WP-B/E launched 11:40; WP-C/D launched 11:48.
- 12 Sep 12:00 — WP-B done. 20 vector PDFs, 0 rasters, legends off, red/blue/yellow/purple. Pushed Overleaf figures only. Captions still need WP-E (EEG forest still says navy/teal).
- 12 Sep 12:02 — WP-C done. Holm-row bold on Results + App D/E; item-loo is cell-bold. Pushed those three tex files. `models.tex` left for WP-D.
- 12 Sep 12:05 — WP-E applied (48 captions). Notice caption stays binary, no sponsored-item. EEG colours follow WP-B (red Fz θ, blue posterior α). `models.tex` analysis-families caption left for WP-D.
- 12 Sep 12:08 — WP-D done. FDR \(q\) gone; four labels; Holm vs Bonferroni; paired-\(t\) defence; two EEG estimands; \(k=37\) once. Pushed `models.tex` + one Results wording fix. Item 8 still blocked.
