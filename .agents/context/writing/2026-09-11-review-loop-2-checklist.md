# Review loop 2 — master checklist (11 Sep 2026)

> **STATUS 12 Sep 10:00 — LOOP CLOSED; PNG + MERGE AUDIT DONE LOCALLY (not pushed).** All packages done. Montage include is now `eeg_montage.pdf`. Eight `WALTER:` lines that the first merge dropped from `results.tex` are restored (36 = `8559732`). Gold-tables sentence unglued. Report: `2026-09-12-png-and-merge-audit.md`. Next loop (his + five chatbots' feedback) starts a new checklist file; purge the `% [AI: …]` replies then. G1 voice-read stays parked.

**Status board for the second `WALTER:` review of thesis Ch 7 / 8 / 9 /
abstract.** This file is the memory of the loop. Every subagent reads it
first and appends its report under `review-2/WP<n>-report.md`. The
orchestrator updates the Status column here. Nothing is pushed to
Overleaf until Walter says so.

Source of the comments: `docs/overleaf/thesis/` commit `8559732`
("Update on Overleaf", 85 `WALTER` lines), merged locally into the
review‑1 PR as `d4f47a7`. Review‑1 comments (forests, BH, boxplots,
appendix items 1–18) are already closed and tagged `% [AI: closed …]`
in the tex. **Do not delete Walter's comments.** Add `% [AI: …]` only
for critical notes.

## Order of work (do not reorder)

1. Batch 1 (parallel): WP1 Katerina reconciliation · WP2 figures ·
   WP3 notice percentages · WP4 Results prose · WP6 effects matrix ·
   WP7 RQ redefinition.
2. Batch 2: WP5a Discussion 8.1–8.3 (+ integrate WP1/WP3 into 7.2/7.3).
3. Batch 3: WP5b Discussion 8.4–8.7 (RQ table, matrix, limitations).
4. Batch 4: WP11 fact-check (different model) · WP10 comment hygiene ·
   WP12 nomenclature sweep.
5. Batch 5: WP8 Conclusion (Ch 9). **Batch 6: WP9 Abstract. LAST.**
6. Report to Walter; push only on his word.

## Model policy (Walter, 11 Sep)

| Role | Model slug |
|---|---|
| Thesis prose (Results/Discussion/Conclusion/Abstract) | `claude-opus-5-thinking-high` |
| Fact-check / second reader | `gpt-5.6-sol-max` |
| Statistics + Gold re-estimation | `inherit` (Fable) |
| Pure plotting / LaTeX-table code | `cursor-grok-4.6-xhigh-fast` (**never** for prose) |
| Never | any `composer-*` |

Grok 4.7 was requested for code but is not in the available list; 4.6
xhigh is used for plotting code only.

## New rules introduced by this review (also in `.cursor/rules/thesis-voice.mdc`)

- **User-centric narrative.** The study is about the user's experience,
  not the advertiser's or the platform's yield. Abstract, Implications,
  Conclusion lead with that.
- **Positive, on-Walter's-side narrative.** Critical, never destructive.
  Do not undersell a Holm-surviving result (posterior α early−late,
  explicit-early slow-power tilt, trust × posterior α ρ=.80). State the
  caveat once, after the finding.
- **Paragraph titles** are short noun phrases (`Temporal effects on
  memory and trust.`), never slogans (`The pipeline is not dead.`,
  `The dull readings win.`, `A hypothesis, not a finding.`).
- **No WIP prose in the PDF.** Gaps are `% [AI: …]` comments only.
- **No unexplained jargon.** OR, GEE, lean, inventory, labelling → either
  define in one clause or drop. Reader is a strong non-specialist.
- **`contexts` not `labellings`** for bare vs deployed \(f_{\mathrm{genre}}\)
  input. Apply thesis-wide incl. figures, tables, `.agents`.
- **Composites → outcomes** everywhere (behavioural sense).
- **\(k=37\)** appears only in preprocessing (Ch 4) and Methods.
  "\(u_5\) does not exist" is said once (Results 7.5), not again.
- **Figures**: vector PDF from matplotlib; every forest plot marks
  Holm \(p<.05\) with the same orange asterisk; captions ≤ 2 lines.
- **Tables**: bold Holm-significant rows; family divider rules; no BH.
- **Results paragraphs**: model = the `tab:traj-aligned-counts` paragraph
  and the trust × posterior α paragraph (Walter's positive examples).
- **Limitations ≠ Future work.** Limitations (Ch 8) say what the design
  could not see. Future work (Ch 9) says what to build next.
- **Katerina's tree** (`analysis/behavioural/`) may be **read** for
  reconciliation. Never edit, run, or quote its CSVs; re-estimate on
  Walter Gold \(N=54\).

---

## Work packages

Status: `todo` · `running` · `done` · `blocked`. Owner = model slug.

### WP1 — Katerina reconciliation (analysis) — owner `inherit` — `done` (report `review-2/WP1-report.md`)

> Katerina's demographic "findings" = raw p on condition-dummy × level terms, uncorrected MixedLM, sparse levels (n=2–3). Refit on Gold: 14/18 raw hits sit on 2–3-person levels; the two Holm survivors are the same two participants (relevance, secondary). **Declared design on N=54: 0/70 Holm (her levels), 0/70 (collapsed), OLS agrees 140/140; secondary 0/60.** Nearest: cued memory early−late × familiarity (Holm .44). Her n=19 OCEAN Spearman: 0 Holm, 0 BH. Ignore commit `c4ceea3` (item drop). Age not recorded. Outputs: `beh_demographics_board.pdf`, `tab_beh_demographics.tex` in thesis `figures/results/`. Proposed 7.3 / 8.2 / App E text in report → WP5a.

Comments: results.tex:585 ("reconciliating katerina's work … demographics
… some in results+discussion and some in appendices").

- Read (do not run) `analysis/behavioural/moderation_model_gold.py`,
  `temp_demo_moderation_model.py`, `calc_condition_ocean_correlations.py`,
  `ocean_corr_outputs/*.csv`, `outputs/ad_notice/*.csv`, `README.md`,
  `variable_dictionary.md`. Summarise: which demographic factors, which
  coding, which model, which p, what sample (\(n=19\) lab incl.
  crowdfail vs \(N=54\)?).
- Re-estimate her demographic moderation design on Walter Gold
  \(N=54\) in `analysis/walter/behavioural/stats/run_demographic_moderation.py`
  (new). Declared: one factor at a time × three planned contrasts, LMM
  random intercept, Holm within outcome. Keep her factor coding if it is
  defensible (education levels, frequency levels uncollapsed) and report
  both her coding and the collapsed screen already in
  `personality_demo_screen.csv`.
- Output: CSV + `tab_*.tex` + one board figure (vector PDF) under
  `analysis/walter/behavioural/outputs/{confirmatory|exploratory,figures/thesis}`.
- Report: what survives Holm, what she found that does not replicate on
  \(N=54\), proposed Results 7.3 sentences, proposed Discussion 8.2
  sentences, proposed appendix table. **Do not edit thesis tex.**

### WP2 — Figures: vector + unified Holm star + PNG audit — owner `cursor-grok-4.6-xhigh-fast` — `done` (report `review-2/WP2-report.md`)

> All `figures/results/*.pdf` re-plotted from frozen CSVs, 0 embedded rasters (imshow boards → pcolormesh). One Holm marker everywhere: clay `#C45C26` `*` at `xmax + 0.06·span`, legend "Holm p < .05" (localisation, item, EEG confirmatory, both combo forests, depth). Diagram PNGs → existing PDFs in `dataset.tex` / `system_design.tex` (`system_architecture`, `ads_data_pipeline`, `trajectory_preprocessing`, `eeg_preprocessing`); `eeg_montage.png`, `qwen3.6.png`, UI screenshots stay PNG. Orchestrator visually checked `eeg_confirmatory_forests` and `beh_demographics_board`.

Comments: results.tex:444 (pdf vectorised), 446 (all forest plots need
the Holm star; unify), 442/301/502 (captions too big → handled by
prose WPs, not here).

- All `figures/results/*.pdf` already have 0 embedded rasters; confirm
  every generator saves `format="pdf"` with no `rasterized=True`.
- Audit the PNGs the thesis includes: `figures/system_architecture.png`,
  `figures/preprocessing/{trajectory_preprocessing,eeg_preprocessing,eeg_montage,ads_data_pipeline}.png`,
  `figures/models/qwen3.6.png`, `figures/ui/*.png`. Report DPI/size; if
  a vector source exists (drawio/svg/mermaid) export PDF and swap the
  `\includegraphics`; UI screenshots stay PNG.
- Unify Holm marker on: `beh_localisation_forest`,
  `eeg_confirmatory_forests`, `combos_declared_forests`,
  `combos_trust_alpha` (panel b), `beh_item_forest`,
  `s24_depth_versus_ad`. Same orange `*` at the same offset; legend
  text "Holm \(p<.05\)". Only re-plot from frozen outputs; never rerun
  a pipeline; never touch ICA.
- Copy regenerated PDFs to `docs/overleaf/thesis/figures/results/`.
  Report the list.

### WP3 — Notice / recall descriptive percentages (analysis) — owner `inherit` — `done` (report `review-2/WP3-report.md`)

> Result: ~half (52–56%) did not report the implicit mention as sponsored; 19–26% missed the banner; ~40% per timing noticed the banner but not the mention. The "90% did not notice implicit" claim is **not** supported; use the half/one-in-five wording.

Comments: results.tex:588 ("simple percentages of how many people noticed
ads per condition … 90% of people didn't notice implicit").

- On Walter Gold (`analysis/walter/behavioural/outputs/gold/`), per
  condition and per format: share of participants with
  sponsored-button item ≥ 5 (agree side) and ≥ 4; brand-mention item
  the same; cued memory ≥ 5; joint (noticed ∧ remembered). Wilson 95%
  intervals. \(N=54\).
- Read Katerina's `outputs/ad_notice/notice_by_condition.csv` for
  cross-check only; do not quote it.
- Output: `outputs/exploratory/notice_recall_percentages.csv`,
  `figures/thesis/beh_notice_percentages.pdf` (vector, one panel),
  `tab_beh_notice_percentages.tex`.
- Report: numbers + proposed 3–4 Results sentences for 7.2 (notice
  subsection) + the Discussion-safe wording (descriptive, no test).
  **Do not edit thesis tex.**

### WP4 — Results Ch 7 prose pass (7.4 EEG, 7.5 trajectories, 7.6 combos, 7.7 summary) — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP4-report.md`)

> All 28 WALTER comments kept; no number changed. 7.6.4 three-way deleted (partial ρ moved to 7.6.1); `fig:combos-declared` now opens 7.6; OR/GEE in words; `u_5` once; contexts not labellings; summary tables with family dividers + "Key estimate". Orchestrator then: `results.tex` RQ8/RQ9 → RQ6/RQ7 (done); `theory.tex` \(\delta_k(a_k)\) → \(\delta^{(a)}_k\), \(\tilde\delta\) and \(g^{(a)}_k\) likewise (done, 4 forms). **Batch 1 complete.**

Every open `WALTER` comment in `results.tex` from line 271 down. Edit
`results.tex` only, with targeted `StrReplace`; never rewrite the file.

- 271: EEG section prose readability (still Results, no interpretation).
- 299: the `fig:traj-position` lead-in sentence unclear → rewrite or drop.
- 301, 442, 502: captions to ≤ 2 lines.
- 315: quote the two fallback classes (`other`, `other obscene or illegal`).
- 337, 365: notation must match Ch 3 (`eq:ad-associated-genre-shift`,
  `eq:genre-aligned-ad-shift`, \(\tau_k\), \(\delta_k\)); fix or add
  `\eqref`.
- 339: "only turn 2 has a following utterance" said once; remove repeats.
- 343: `tab:traj-crossing` — one sentence on why those four contrasts
  (the declared family of `tab:analysis-families`), so it is not random.
- 361: OR → define ("odds ratio, the ratio of shift odds with an early
  advertisement to without") or drop the GEE sentence.
- 422: reference where contextual vs bare **contexts** are defined
  (Ch 3 / Ch 4 / App F) at first mention; add cross-refs throughout 7.5.
- 433: keep Walter's granularity sentence in the 7.6 opener; ≤ 5 lines.
- 440, 468: cite the "tautological" exploratory pattern (implicit−explicit
  reply latency / words × Pope engagement) in 7.6.1, one sentence.
- 446: move `fig:combos-declared` before 7.6.1 as the section summary.
- 465: "correlation against what" → say trust \(D_i\) in the sentence.
- 479: drop the whole-window medians clause; Dataset A or B only.
- 486: delete 7.6.4 three-way; move the grain sentence to the 7.6 opener
  and the partial-ρ sentence to 7.6.1.
- 500, 502: `tab:results-summary` and `tab:results-checks`: family
  divider rules (`\midrule` + italic group label), rename "Headline" →
  "Key estimate", ≤ 1 line per cell, captions ≤ 2 lines, order synced
  with `tab:analysis-families`.
- `labellings` → `contexts`; remove `k=37` from Results.
- Leave 7.2/7.3 alone (WP5a integrates WP1/WP3 there).

### WP5a — Discussion 8.1 Behavioural, 8.2 Personality/demographics, 8.3 EEG — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP5a-report.md`)

> 8.1–8.3 rewritten; all titles noun phrases; "pipeline is not dead" gone; `Timing and posterior α.` finding-first; onset paragraphs merged. WP3 shares in 7.2 + 8.1; WP1 demographics in 7.3 + 8.2 + App E. **Gold corrections:** "90% did not notice implicit" → about half (52%/56%); "implicit mentions largely not recognised when re-shown" was false (57%/59% recognised) → now an attribution finding. Balance-checked; a compile is still owed (no TeX locally).

Inputs: WP1 + WP3 reports. Edit `discussion.tex` (8.1–8.3) and
`results.tex` 7.2/7.3 (integration of WP1/WP3 snippets only).

- 28/45: retitle every paragraph as a short noun phrase.
- 36/40: make the trust paragraph read less dull; keep Walter's bold
  sentence idea (trust Holm-null in short usage) in his voice.
- 41: give the **direction** of implicit vs explicit in words every time.
- 49: emphasise the null format × timing interaction (one sentence, own
  paragraph or end of the format/timing paragraph).
- 53: no WIP prose; gaps as `% [AI: …]`.
- 60–66: 8.2 already estimated; integrate WP1 demographics (what
  survives on \(N=54\); what Katerina saw on \(n=19\) that does not).
  Short paragraphs, never a blob.
- 80: delete "The pipeline is not dead" paragraph; keep the
  writing−reading fact in one sentence inside the next paragraph.
- 84: retitle "No sustained…"; 89: rewrite the early-vs-late paragraph
  constructively (finding first, depth confound second, no "not greater
  visual processing" slogan); 94: drop the Fz θ apples/pears clause.
- 97/101: merge "Early Explicit Onset" + "dull readings" into one
  well-written paragraph: onset tilt is real and format-specific;
  ocular/evoked alternative stated once.
- 112: retitle pairwise sweep; 116: rewrite/remove the "lean"
  hypothesis (define or drop).
- Add WP3 percentages to 8.1 where they carry a claim (descriptive).

### WP5b — Discussion 8.4 Trajectories, 8.5 Combos, 8.6 Implications, 8.7 Limitations — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP5b-report.md`)

> 8.4–8.7 rewritten (+150/−59). `fig:effects-matrix` + `Reading the matrix.` and `tab:rq-answers` (3 supported, 1 partly, 5 negative) now in 8.6; 8.6 opens with the user-centric sentence. 8.7 = Design and sample / Measures / Neurophysiological / Trajectories, all eight of Walter's limitations in. Three prescriptive sentences moved out for WP8 (in report). Model named as in thesis (Qwen 3.6 35B-A3B). Open for Walter: RQ8 verdict "Partly"; the "comparable or stronger than reference-study models" sentence in 8.7 is the one comparative claim without a number.

Inputs: WP7 RQ mapping, WP6 matrix figure, WP1/WP3.

- 123: remove repeated \(u_5\) sentence. 127: `contexts`.
- 132/134/138: expand the trajectory findings; retitle "inventory" and
  "Depth moves" paragraphs; add the one-line fallback-by-turn implication
  (results.tex:335).
- 148/150: 8.5 opener clearer; remove \(k=37\); retitle.
- 154/158/160: deepen posterior α description; cut the "marker that
  passed" sentence; make the bounded-hypothesis paragraph's point
  explicit or merge it.
- 164: less dismissive title/prose for the exploratory map.
- 172: fact-check Implications against Ch 7 (numbers, directions).
- 174: insert the effects matrix (`fig:effects-matrix`, WP6) with a
  2-line caption; one paragraph reads it.
- 182/186/190: retitle and de-AI the three implication paragraphs.
- 194/198: replace the RQ sentence with the **RQ answer table**
  (`tab:rq-answers`, from WP7): RQ · verdict · evidence (one line) ·
  where.
- 209–221: Limitations: add cued recall, unknown ad performance,
  carry-over of manipulation items, baseline unused, warm-up length,
  model generation (Qwen 3.6 vs newer), short-usage horizon for implicit
  trust, free text unanalysed; scan Ch 4–7 for more. Move anything that
  is "next study should…" to Ch 9 Future work (list them in report for
  WP8).
- 224: user-centric framing sentence in Implications.

### WP6 — Effects matrix figure — owner `inherit` — `done` (report `review-2/WP6-report.md`)

> `figures/results/effects_matrix.pdf` (vector; 15 rows × 7 cols; visually checked by orchestrator against `tab:beh-planned` / localisation: signs, arrow counts and fills agree). Provenance: `analysis/walter/combos/outputs/thesis/effects_matrix_cells.csv`. Caption + `\label{fig:effects-matrix}` in the report. **For WP5b prose:** implicit *raises* notice and manipulation above \(a^{\emptyset}\) (it is lower only relative to explicit); "late increases credibility" is not estimated (only early − late is significant); onset-locked planned columns are not estimated; condition-aggregation EEG marginals are the post hoc sweep (all hollow).

Comment: discussion.tex:174.

- Python (matplotlib, vector PDF) from frozen CSVs:
  `analysis/walter/behavioural/outputs/confirmatory/confirmatory_planned_D.csv`,
  posthoc_vs_control, `analysis/eeg/statistics/outputs/eeg_condition_*.csv`
  (Dataset A) and Dataset B tables, `analysis/walter/combos/outputs/thesis/`.
- Rows: notice, perceived manipulation, credibility, trust, cued memory,
  trust on re-exposure, posterior α (Dataset A), Fz θ (Dataset A),
  explicit-early onset tilt (Dataset B, exploratory), trust × posterior α
  (onset). Columns: any ad vs none · explicit vs implicit · early vs late
  (+ four condition marginals vs \(a^{\emptyset}\) from the localisation
  grid). Cell: ↑/↓ with 1–3 arrows by \(|d_z|\) band (<.2, .2–.5, >.5),
  filled if Holm \(p<.05\), hollow if not, "·" if not estimated.
- Output `analysis/walter/combos/outputs/thesis/effects_matrix.pdf` +
  copy to `docs/overleaf/thesis/figures/results/effects_matrix.pdf` +
  `effects_matrix_cells.csv` (every cell with source file and value).
- Report: the CSV path and any cell whose direction is ambiguous.
  **Do not edit thesis tex.**

### WP7 — Research questions redefinition — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP7-report.md`)

> **RQ mapping (11 → 9), binding for WP5b / WP8 / WP9:** RQ1→RQ1 · RQ2→RQ2 · RQ3 dropped · RQ5→RQ3 · RQ6→RQ4 · RQ4+RQ7→RQ5 (interaction) · RQ8→RQ6 · RQ9→RQ7 · RQ10→RQ8 (verdict "Partly": timing on posterior α survives, format does not) · RQ11→RQ9 (onset-locked response × trust, Supported). `introduction.tex` + `discussion.tex` remapped; contributions bullet no longer promises the EEG ablation. `tab:rq-answers` snippet is in the report.
> **Orchestrator to do after WP4 finishes:** `results.tex:176` comment and `:183` `fig:beh-personality` caption RQ8→RQ6, RQ9→RQ7. `discussion.tex:198` orphan sentence → absorbed by WP5b into the RQ table.

Comments: discussion.tex:7, 9, 198; introduction.tex:55–60.

- Current RQ1–RQ11 in `introduction.tex` (`sec:intro:research-questions`).
  Orchestrator decision: drop RQ3 (task moderation, not estimated);
  merge RQ4 + RQ7 (same interaction question); reframe RQ11 from
  "ablation" to "do onset-locked neural responses covary with reported
  trust?" (answered by 7.6); keep the rest, each answerable
  positively or negatively. Renumber consecutively.
- Update `introduction.tex` RQ block (prose, user-centric wording), then
  every `RQ\d+` mention in `discussion.tex`, `conclusion.tex`,
  `models.tex`, `frontmatter/abstract.tex`, `related_works.tex` with
  the new numbers. **Do not edit `results.tex`**; list its RQ mentions
  in the report for the orchestrator.
- Produce `tab:rq-answers` as a tex snippet in the report (RQ · verdict ·
  one-line evidence · section ref) for WP5b to insert.

### WP8 — Conclusion Ch 9 — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP8-report.md`)

> Jacket paragraphs kept (+1 user-centric sentence), every Future Work bullet kept (+1 onset-locked bullet, "five"→"six"). §9.1 now: five findings paragraphs + `The overall picture.` in Walter's register. Removed F26/F27/F29/F30 and all slop comments; `m(s)`/`q(s,a)` → generic scorer sentence with `% [AI: held until after 17 Sep]`. Recompiled after WP11-fix + WP8: 156 pages, 0 undefined refs.

Comments: conclusion.tex:6, 21, 23.

- Keep the jacket summary and Future Work (Walter: golden). Remove all
  AI-slop comments and `[TODO …]` drafts. Add concise per-analysis
  findings (behavioural, personality/demographics, EEG, trajectories,
  associations) as prescriptions, user-centric, positive. Absorb the
  future-work items WP5b moved out of Limitations. No serving rule, no
  explicit-late compromise, no MDE.

### WP9 — Abstract — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP9-report.md`, full text inside)

> 369 words, fits one page (checked in the compiled PDF, p. iii). User-centric opener and closer; F24/F25/F28 gone; "Holm-null" written as "after correction". Walter's `% WALTER:` line kept.

Comment: abstract.tex:29. Single concentrated agent: remove TODO
drafts, rewrite on Walter's narrative + latest numbers, user-centric,
≤ 1 page. Show text to Walter before applying if he is online.

### WP10 — Comment hygiene — owner orchestrator — `done`

> Removed from `results.tex` / `discussion.tex`: REVIEWER-ATTACK-SURFACE block, three table-maintenance blocks, two lock-pointer blocks, one stale notation note. Kept: every `% WALTER:` line (28 / 45), Gold-provenance comments, and the `% [AI: …]` response notes under Walter's comments (they document this PR for his next pass; purge them in loop 3 once he has read them). `conclusion.tex` / `abstract.tex` comments are WP8 / WP9's.

discussion.tex:22, conclusion.tex:21. Remove agent-instruction comments
(lock pointers, "REVIEWER ATTACK SURFACE", `[TODO …]` drafts). Keep:
Walter's comments, Gold-provenance comments (results.tex:8–10, 82–85),
`% [AI: …]` critical notes.

### WP11 — Fact-check pass — owner `gpt-5.6-sol-max` — `done` (report `review-2/WP11-report.md`: 12 blocking · 15 should-fix · 3 cosmetic)

> F01–F22 (Ch 7–8 wording/scope: secondary qualities not "nothing"; personality family = four primary outcomes only; "one column" = five of six; no direct implicit−explicit onset verdict; 6/96 not 8/256; genre overlap is corpus-level, \(g^{(a)}=\hat g_2\) in 25/108; drop "|ρ|>.47"; matrix ≠ "every" effect; 36 = 9×4; age incomplete not absent; per-model n; App F ICC header → p; rounding) → **WP11-fix** (Opus). F24–F30 (abstract/conclusion: "how and when", relative θ as confirmatory, "allocation of neural processing", explicit-late compromise, "price of attention", "weak overlap", ad-moment scorer in Future Work) → WP8 / WP9 must not re-import them. High-risk claims verified as holding are listed in the report.

### WP11-fix — apply F01–F22 — owner `claude-opus-5-thinking-high` — `done` (report `review-2/WP11-fix-report.md`)

> All 22 applied. Verdict flips to know: Dataset B post hoc = 6 of 96 raw hits, "about what chance predicts" (not fewer); onset format = explicit-early response against its own control, direct implicit−explicit Holm-null (smallest .08). Orchestrator aligned `models.tex` family row → "Personality moderation (demographics as covariates)" to match `tab:results-summary`. WALTER lines verified identical to remote set.

Read-only. Every number and direction in Ch 8 (esp. Implications, RQ
table, effects matrix) and Ch 7 prose against `tab:beh-planned`,
`tab:beh-localisation`, EEG tables, combos section, and the frozen
CSVs. Report discrepancies; orchestrator fixes.

### WP12 — Nomenclature sweep — owner orchestrator — `done`

> Thesis-wide greps clean: no `labelling` in the \(f_{\mathrm{genre}}\)-input sense (App F ×2 and dataset.tex fixed; `sec:app-traj-labelling` label name kept, internal), no `composite`, no `card` outside old drafts in conclusion/abstract (WP8/WP9), \(k=37\) only in dataset/models, `u_5` once (results 7.5), no BH/Benjamini, no OR/GEE/lean. Ch 3 notation unified to \(\delta^{(a)}_k\).

`labelling(s)` → `context(s)` (13 hits results, 3 discussion, 3 App F,
1 theory, 1 models, 1 dataset — check each is the \(f_{\mathrm{genre}}\)
input sense); `k=37` outside Ch 4/Methods; `composite`; `OR` undefined;
`u_5`/"no following utterance" repeats; `card` → `banner` for explicit.

---

## Comment → WP map (line numbers in the merged tex, `d4f47a7`)

| File:line | WP |
|---|---|
| results 271 | WP4 |
| results 299, 301, 315, 335, 337, 339, 343, 361, 365, 388, 409, 422 | WP4 (335 → WP5b) |
| results 433, 440, 442, 444, 446, 455, 465, 468, 472, 479, 486 | WP4 (444/446 figures → WP2) |
| results 500, 502 | WP4 |
| results 585 | WP1 → WP5a |
| results 588 | WP3 → WP5a |
| discussion 7, 9, 194, 198 | WP7 → WP5b |
| discussion 11, 22, 53 | WP10 |
| discussion 24 | done (merge) |
| discussion 28–55 | WP5a |
| discussion 60–66 | WP5a (+WP1) |
| discussion 80–116 | WP5a |
| discussion 123–138 | WP5b |
| discussion 148–164 | WP5b |
| discussion 172–190 | WP5b (+WP6, WP11) |
| discussion 209–221 | WP5b (+WP8 for future work) |
| discussion 224 | WP5b, WP8, WP9 |
| discussion 227 | done (this file, `thesis-voice.mdc`, AGENTS.md) |
| conclusion 6, 21, 23 | WP8 (+WP10) |
| abstract 29 | WP9 |

## Local compile (11 Sep, 22:40)

`docker run texlive/texlive:latest` + `latexmk -xelatex` on a **scratch copy** in `/tmp/thesis_src` with one class line patched (`Dissertate.cls:95` `justification={justified,RaggedRight}` → `RaggedRight`; TeX Live 2026's caption package aborts on the original, Overleaf's does not — repo class untouched). Result: 153 pages, PDF built, **0 undefined references / citations**, only the pre-existing harmless class error (`Too many }'s`, cls line 392). Overfull boxes from this loop fixed: `tab:beh-planned` (→ footnotesize, tabcolsep 3pt), `tab:beh-pairwise` (→ footnotesize); 7.2 notice paragraph trimmed to figure-first. Pre-existing overfulls left for Walter: theory.tex 288–337 (35 pt), dataset.tex 246 (29 pt), appendix_c.tex 79–90 (32 pt). Recipe: `docker run --rm -v /tmp/thesis_src:/work -v /tmp/thesis_build:/out -w /work -e OSFONTDIR=/work/fonts texlive/texlive:latest bash -lc 'fc-cache -f; latexmk -f -xelatex -interaction=nonstopmode -output-directory=/out dissertation.tex'`.

## Grok jury (12 Sep 09:30, Walter's four work items, read-only reports)

**Walter's rulings (12 Sep 09:45):** Grok output is *input, not truth*. Item 1 (voice read) → **backlog**, to be merged with the five external-model reviews for loop 3. Item 2 → §4.2.2 text is his *initial draft*; he will rewrite it himself. Item 3 → D1: RQ9 kept but broadened to the user's **neurophysiological state** at onset vs reported experience (intro + `tab:rq-answers` updated); D2: RQ8 kept, "Partly" defined in the caption; D3: the "comparable to or stronger" sentence **deleted**. Gold-grain figure `fig:gold-tables` (`figures/gold_tables.pdf`, cropped) now opens §4.2 and is referenced from §4.2.2.

| Item | Report | Agent |
|---|---|---|
| 1 Voice read | `review-2/G1-voice-read.md` — **done**: 72 findings (titles 9, AI-ish 16, WIP 5, jargon 8, nomenclature 5, redundancy 6, Results/Discussion boundary 13, length 8, direction 2). Orchestrator applied the mechanical ones (3 typos/truncations, "in this draft" footnote, 5 slogan titles); Walter's own titles kept. Ch 1–2 and §4.2.2 are the rewrite zone; the rest of the 72 is loop-3 input. | 703558ca |
| 2 §4.2.2 draft | `review-2/G2-section-4.2.2-draft.{tex,md}` — **done and applied** (orchestrator tightened to ~500 words, Bronze/Silver/Gold paragraphs + `tab:beh-gold`; all counts from `build_report.json`; labels verified). Open questions resolved: no `gold_tables.pdf` here; cued memory on the 216-row recall view; \(g^{(a)}\) points at the trajectory table; `tab:beh-gold` kept; turns sentence kept short. §4.2.2 is no longer WIP. | 1c2ebad2 |
| 3 Three decisions (RQ11, RQ8 "Partly", model comparison) | `review-2/G3-three-decisions.md` — **done**: D1 keep reframe (widen RQ9 to the six declared pairs, intro "adds"→"tracks"); D2 keep Partly + define it in the `tab:rq-answers` caption; D3 delete the "comparable to or stronger" sentence. Awaiting Walter's yes/no. | 3713e637 |
| 4 Statistics attack | `review-2/G4-statistics-attack.md` — **done**: 32 attacks (0 fatal / 18 serious / 14 minor); no frozen Holm verdict reverses if the Methods families stand. Closest kill shot: posterior α early−late Holm .0496 within the measure's 3 contrasts; Holm across the six Dataset A confirmatory tests would be .099 (RQ8 "Partly" rides on it). Five expected committee questions + one-line answers are in the report (defence prep). | 025e6c62 |

Grok 4.6 xhigh used on Walter's explicit request for these four; item 2 is prose and therefore lands as a draft for Opus/Walter review before it touches `dataset.tex`.

## Reports

`review-2/WP1-report.md` … `WP12-report.md`. Each report: what changed
(file:label), numbers produced (path), open questions for Walter.
