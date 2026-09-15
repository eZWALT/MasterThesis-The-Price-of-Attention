# Paper rebuild: golden inventory, skeleton, and build plan

Date: 15 September 2026. Dig only. Paper source
(`docs/overleaf/publication/main.tex`) is unchanged except for the
`\Rev` macro (preamble). The rebuild itself starts when thesis **v3**
is frozen (after the 17 Sep PDF and the second jury round).

Ground truth at the dig: paper HEAD `b28b698` (Walter, 14 Sep), thesis
HEAD `920abd8` (loop 3b, v2 in construction; local tree dirty, not
touched).

## 1. How authorship was traced, and why blame alone is wrong

- `git blame` on `main.tex`: eZWALT 1280 lines, Walter (Overleaf) 277,
  Sebastian 163, `lympa` 106. That under-counts hand text: the agent
  commits of 20–24 Aug rewrote most hand paragraphs in place, so blame
  moved to eZWALT while the argument stayed Walter's or Sebastian's.
- Overleaf attribution is per session, not per paragraph. `lympa`
  `d698eca` (6 Aug, +439 lines) is Walter's text: its comments address
  "KATERINA: SEBASTIAN:", it carries the RQ block, the Method intro, the
  EEG ETL walk-through, and Future Work. Sebastian's `6a342bb` (31 Jul)
  also carries Walter's RQ list next to Sebastian's own paragraphs.
- Sebastian's hand paragraphs, by content: participants (`677720f`, now
  §5.1), EEG acquisition (`7d9fd27` actiCHamp paragraph, now §5.6, with
  250 Hz corrected to 500 Hz), the four-phase lab procedure
  (`6a342bb`, merged into §5.2.1), the appeal/explicitness paragraph
  with `puto1984` / `nuweihed2024` (now Related Work ¶4), H1–H3, title,
  Funding / Disclosure / Ethics / Data statements.
- Katerina's hand text in the paper source: none found under her own
  name that is not Walter's. Her contribution is the experimental
  procedure she ran and the behavioural analysis tree
  (`analysis/behavioural/`, read-only); thesis numbers come from
  `analysis/walter/behavioural/` on Gold \(N=54\).
- Sentence-level trace: 240 hand-added sentences over the paper's
  history; 32 survive verbatim/fuzzy, 208 were superseded by rewrites
  (mostly Sebastian's July template instructions, which were
  placeholders, not prose). Nothing golden was lost: every hand
  argument that mattered is still in the current file in rewritten
  form, listed below.
- The paper already carries a `%%%% STATUS | DONE (GOLDEN)` header on
  the sections Walter signed as keep-as-is. Those headers agree with
  the trace and are used as the primary signal below.

## 2. Golden inventory (keep; rebuild around it)

Line numbers are `main.tex` at `b28b698` (+5 after the `\Rev` insert).
"Keep-as" is what the rebuild may do to it.

| # | Section | Lines | Origin | Keep-as | Paper placement |
|---|---|---|---|---|---|
| G1 | Problem statement: *advertere* etymology + welfare triad (advertiser / user / platform) | 189–215 | Walter (thesis Ch 1, his hand) | verbatim, trimmed | §1, two paragraphs |
| G2 | Contributions list (theory arm / experimental arm) | 245–284 | Walter | keep structure, cut to 4 bullets, drop "open-source dataset" until it is public | §1 close |
| G3 | Appeal × explicitness paragraph | 340–356 | **Sebastian** | verbatim | §2 |
| G4 | Related-work spine: engineering → quality → users → detection → conflicts → LLM×EEG → neuromarketing | 300–469 | agent from Walter's thesis Ch 2 | keep spine, cut to ~500 words (one sentence per cited work) | §2 |
| G5 | Taxonomy of the served instance \(a_k=\langle\iota,(\alpha,\epsilon),(\sigma,\lambda,\theta),\phi\rangle\) + `tab:ad-taxonomy` + the three instances | 531–642 | **Walter hand** (4d27e0d, 0690dad, f13bb04) | verbatim; delete the stub "The 3 advertisement instances used:" | §3.1 |
| G6 | Policy \(\Pi=\langle\Gamma,\mu,\pi\rangle\) | 650–699 | **Walter hand** | verbatim; if page budget bites, keep equation + one paragraph in body, itemize to appendix | §3.2 |
| G7 | Method intro (two arms, Atlas, symbols restated) | 796–798 | Walter hand + agent | keep, \(N\) already \(54\) | §4 opener |
| G8 | Laboratory conditions (participants) | 813 | **Sebastian** | verbatim | §4.1 |
| G9 | Laboratory workflow, four phases, two data forms | 825–837 | Walter + Sebastian, agent-merged | keep; drop the `.jsonl`/`.xdf` itemize to appendix | §4.2 |
| G10 | Crowd adaptations (Prolific ID, validation check, run id) | 843–852 | Walter (thesis) | keep, compress the three bullets to one paragraph | §4.2 |
| G11 | Tasks, Latin square, exclusions, inferential unit | 858–861 | Walter | verbatim | §4.2 |
| G12 | Independent variables opener | 884 | **Walter hand** | verbatim | §4.3 |
| G13 | Timing rationale: short sessions (Rainie), serial position, Hsu & Karahalios, turn-1 free, turn index not clock | 891–932 | **Walter hand** (1c73557), agent-polished | verbatim | §4.3 (this is the best-argued page of the paper) |
| G14 | Presentation \(\lambda\): implicit / explicit definitions + UI figure | 939–964 | **Walter hand** | verbatim; `banner` not `card` | §4.3 |
| G15 | Behavioural measures (22-item battery, planned outcomes, cued memory ≠ recognition) | 978–982 | agent from Walter | keep; rename `composites` → `outcomes` | §4.4 |
| G16 | EEG acquisition + montage figure | 990–998 | **Sebastian** | verbatim | §4.5 |
| G17 | EEG preprocessing: zones, Dataset A vs B, cleaning, ICA, Gold cell, \(k=37\) | 1006–1066 | agent (ported to thesis Ch 4) | keep 250 words in body (Dataset A/B definitions, ICA, rejection, 16 measures), rest to appendix | §4.5 + App. |
| G18 | Epoching: induced spectrum not ERP, onset jitter, 4 s | 1073–1083 | agent | one paragraph in body, rest to appendix | §4.5 |
| G19 | Statistics: participant is the unit, Holm within family, \(D^A_i\), \(D^B_i\), Wilcoxon raw, two confirmatory markers, positive control | 1092–1137 | agent | keep; **add** the behavioural estimator from thesis `models.tex` §Statistical framework (LMM, item-level, Holm families) | §4.6 |
| G20 | Sample + BFI-10 descriptives paragraph and table | 1155–1229 | **Walter hand** (98f1ba6) | keep paragraph; table and boxplot to appendix | §5.1 |
| G21 | EEG Results (positive control, forests, width sensitivity, 14-measure board) | 1244–1285 | agent, Gold-matched 6 Sep | keep structure; re-sync every number to thesis v3 Results 7.4 | §5.4 |
| G22 | EEG Discussion: readings of the slow-power rise, ICA both directions, consumer-neuroscience nulls | 1319–1338 | agent | reuse sentences, but rebuild from thesis v3 `sec:disc-eeg` (it carries the locks: two estimands, write−read, depth confound) | §6.2 |
| G23 | Limitations | 1362–1364 | **Walter hand** | keep his two paragraphs, merge with thesis Ch 8 limitations | §6.4 |
| G24 | Future Work | 1374–1391 | **Walter hand** (d698eca), agent-expanded 24 Aug | his; keep list, cut to five bullets | §7 |
| G25 | Acknowledgements | 1417–1420 | **Walter hand** | verbatim (fix "willigness") | back matter |
| G26 | Funding / Disclosure / Data availability / Ethics | 1427–1453 | **Sebastian** | keep; fill XXXXX (ethics board, grant) | back matter |
| G27 | Appendix: task prompts, LLM prompts, HyDE | 1463–1655 | agent from `src/project` catalog | verbatim | App. A–B |
| G28 | Appendix: EEG QC provenance, 16 measures, confirmatory tables, literature channel sets | 1667–1795 | agent | verbatim; channel sets stay sensitivity-only | App. D |

## 3. Reusable, but rewrite from thesis v3 (do not port from the paper)

| Section | Why | Source in thesis v3 |
|---|---|---|
| Abstract | current one is a 6 Aug placeholder | `frontmatter/abstract.tex`, cut to 180 words; written **last** |
| Introduction ¶1–4 (history of LLM funding, Alphabet/Meta revenue) | fine prose, too long for a paper | `introduction.tex` §Motivation, keep one paragraph |
| Research gap | Walter's own header: "OUTDATED AI SLOP" | `related_works.tex` closer (user-first) |
| Research questions | numbering is the July list; RQ2/RQ4 (trajectories) are thesis-only | `introduction.tex` §1.3: keep RQ1, 3, 5, 6, 7, 8, 9 → renumber 1–7 |
| Hypotheses H1–H3 | Sebastian's July template; thesis has none | decide (see §7) |
| Behavioural Results | SKELETON in paper | `results.tex` §7.2–7.3, figure-first |
| Personality / demographics Results | absent | `results.tex` §7.3 |
| Associations Results | SKELETON | `results.tex` §7.6.1 (behaviour × EEG only) |
| Discussion behaviour / personality / associations / implications | SKELETON or MID | `discussion.tex` §8.1, 8.2, 8.5, 8.6 + `tab:rq-answers` |
| Conclusion | TO-START, Walter's outline in comments 1400–1408 | `conclusion.tex` §Summary, one paragraph, his four-point order |

## 4. Drop from the paper (thesis-only or engineering)

- Intent / attention-shift theory, genre trajectories, \(f_{\mathrm{genre}}\),
  \(\delta^{(a)}\): already removed 24 Aug; stale figure files remain in
  `Figures/` (`traj_*`, `s24_*`, `gold_tables.*`, `pipeline_temporary.png`). Delete at build.
- System design and engineering (thesis Ch 5), product catalogue and
  vector database (Ch 4 §4.1): one sentence in §4 ("real products from
  Amazon Reviews 2023, retrieved by a bi-/cross-encoder pipeline;
  details in the thesis"). Architecture diagram → appendix at most.
- Dataset chapter EEG walk-through beyond the 250-word body version.
- `\tableofcontents`, `\clearpage` after the abstract, the STATUS
  headers, `\color{red}` / `\color{black}` toggles, the `Questions for
  analysis.tex` scratch file, `old_backups/`.
- Ad-moment scorer, `analysis/policy/`: never.

## 5. Target skeleton and word budget (NeurIPS wide preprint, 5–10 pp)

| § | Title | Words | Visuals |
|---|---|---|---|
| — | Abstract | 180 | — |
| 1 | Introduction (motivation, problem, contributions, RQs) | 650 | — |
| 2 | Related Work | 500 | — |
| 3 | Theoretical Foundations (taxonomy, policy) | 450 | `tab:ad-taxonomy` |
| 4 | Method (arms, design, IVs, DVs, EEG, statistics) | 1300 | flow figure (lab+crowd merged), UI pair, families table |
| 5 | Results (sample, behaviour, personality, EEG, associations) | 1200 | behavioural forest, EEG forests, trust × posterior \(\alpha\) |
| 6 | Discussion (behaviour, EEG, associations, implications + `tab:rq-answers`, limitations) | 900 | RQ-answers table |
| 7 | Conclusion and Future Work | 300 | — |
| | **Body total** | **≈5500** | ≈ 8–9 pages |
| A–F | Appendices: task prompts; LLM prompts; behavioural items, reliability, item-LOO, pairwise sweep, personality; EEG QC, 16 measures, confirmatory tables, channel sets; realised design and arm split; sample descriptives table | unbounded | |

## 6. Vocabulary sync before any port

- `outcomes`, not `composites` (paper has 10 hits).
- `banner`, not `card`. `contexts`, not `labellings` (n/a after trajectories are out).
- Dataset A display name is **condition aggregation**; Dataset B is
  **onset-locked**. Thesis uses "Dataset~A/B" as the symbol and the
  display name in prose; mirror the thesis exactly, never Path A/B or
  equal-n.
- Holm \(p\) = Holm-adjusted paired \(t\); Wilcoxon raw; no BH, no FDR
  \(q\) (thesis `models.tex` still has one FDR mention on the board).
- \(k=37\) only in Methods. "\(u_5\) does not exist" is thesis-only.
- RQ numbering: the paper gets its own 1–7 (see §3). Every RQ must be
  answered in `tab:rq-answers`.
- Paper title stays `The Price of Attention: Behavioral and EEG
  Responses to Advertising in LLM Conversations` (thesis cover uses
  it via `\usePaperTitle=1`).

## 7. Open decisions for Walter (answer before the build)

1. **H1–H3.** Sebastian's hypotheses are EEG-only and pre-date the
   design. Thesis has no hypothesis section. Options: drop, or keep one
   sentence in §1 with the directional predictions the thesis
   Discussion actually tests (explicit noticed more than implicit;
   early−late on posterior \(\alpha\)).
2. **Policy \(\Pi\) itemize** in body or appendix (≈ 250 words).
3. **BFI-10 table**: body or appendix.
4. **Author contributions footnote and Ethics / Funding XXXXX**: needs
   the board name, approval number, and grant from Sebastian.
5. **Data availability**: keep the HF raw citation
   `troiani2026priceofattentionraw` or wait for the release side quest.
6. **Section files vs one `main.tex`.** Recommended: split into
   `sections/*.tex` (one owner per subagent), keep `main.tex` as the
   assembler, and move the current file to
   `old_backups/main_2026-09-15_pre-rebuild.tex`.

## 8. `\Rev` workflow (mirrors the thesis review loop)

Preamble of `main.tex` now has:

```latex
\def\useReviewMarks{1}
\definecolor{ReviewGreen}{rgb}{0.0,0.55,0.16}
\newcommand{\Rev}[1]{\ifnum\useReviewMarks=1\textcolor{ReviewGreen}{#1}\else#1\fi}
```

- Every sentence an agent adds or changes after paper v1 is wrapped in
  `\Rev{...}`. Walter reads green in Overleaf, comments with
  `% WALTER:`; the agent applies and flips to `% WALTER+:`.
- Flip `\useReviewMarks` to `0` for a clean read; strip the wrappers
  with the thesis cleaner (`/tmp/thesis_source_clean.py` pattern,
  adapted to `\Rev`) before submission.
- Paper v1 itself is **not** wrapped: it is the baseline the loop
  starts from.

## 9. Build plan (when v3 is frozen)

One subagent per work package, each reads this note, the paper
`main.tex`, and the thesis v3 chapter it ports from; each writes a
report under `.agents/context/writing/paper-v1/`.

| WP | Owner slug | Package |
|---|---|---|
| P0 | inherit | Split into `sections/`, delete stale figures, drop STATUS headers and colour toggles, sync vocabulary (§6) |
| P1 | claude-opus-5-thinking-high | §1 + §2 from G1–G4 and thesis Ch 1–2 (≤ 1150 words) |
| P2 | inherit | §3 verbatim G5–G6, §4 from G7–G19 + thesis `models.tex` statistical framework |
| P3 | inherit | §5 Results from thesis v3 Results 7.1–7.4, 7.6.1; numbers only; figure-first |
| P4 | claude-opus-5-thinking-high | §6 Discussion from thesis v3 Ch 8 + `tab:rq-answers`; limitations merged with G23 |
| P5 | gpt-5.6-sol-max | Fact-check pass: every number in §5 against Gold CSVs; every citation key exists in `bibliography.bib` |
| P6 | inherit, last, one agent | Abstract + Conclusion + Future Work (G24), then page count |

Never in the paper: trajectories, scorer, `analysis/policy/`,
Katerina's `analysis/behavioural/` numbers, rainclouds.
