# WP11 — Fact-check pass

Checked 11 September 2026 against the current thesis tables and the frozen
behavioural, EEG, association, and trajectory CSVs. No analysis was rerun.

Severity means:

- **blocking** — changes a scientific verdict, attributes an unestimated effect,
  contradicts frozen evidence, or prevents a submission-ready PDF;
- **should fix** — a wrong count, scope, sample size, or inferential
  overstatement that does not reverse the main result;
- **cosmetic** — rounding or non-rendering source residue with no verdict change.

Source basenames below resolve under these roots:
`analysis/walter/behavioural/outputs/{confirmatory,exploratory}/`,
`analysis/eeg/statistics/outputs/`,
`analysis/walter/combos/outputs/thesis/`, and
`analysis/trajectories/outputs/`. Thesis table labels resolve in
`docs/overleaf/thesis/`.

## Discrepancies

| ID | File:line | Quoted text | Issue | Source of truth and correction | Severity |
|---|---|---|---|---|---|
| F01 | `docs/overleaf/thesis/chapters/discussion.tex:56` | “The secondary qualities, the omnibus tests, and the ten-pair sweep … add nothing outside manipulation and notice.” | This describes Holm-significant secondary findings as absent. | `appendix_e.tex:65` reports convincingness early−late Holm \(p=.005\) and relevance early−late Holm \(p=.003\). `tab:beh-pairwise` has convincingness implicit-early−explicit-late Holm \(p=.034\). `omnibus_friedman.csv` has relevance Holm \(p=.031\) across eight outcomes. | **blocking** |
| F02 | `discussion.tex:72,75`; `introduction.tex:82,84`; `discussion.tex:258–259` | “Neither the five personality traits nor any demographic factor … changes … the four primary outcomes or on cued memory.” RQ6/RQ7 are then answered without that restriction. | Cued memory and trust after re-exposure were not in the personality family. The full RQ6/RQ7 verdict therefore extends beyond the estimated evidence. Demographics did include cued memory, but personality did not. | `personality_lmm.csv` has exactly 60 rows: four primary outcomes × three contrasts × five traits. `demographic_moderation_lmm.csv` adds cued memory for demographics only. Narrow the personality claim and RQ wording/evidence to the four primary post-condition outcomes, or estimate the omitted cued outcomes. | **blocking** |
| F03 | `discussion.tex:77` | “the cells it flagged sit on education and use-frequency levels filled by two or three people” | Not all inherited raw hits were sparse or confined to those factors. | `demographic_moderation_katerina_design.csv` / `WP1-report.md`: 18 raw hits, 14 on two- or three-person levels; four non-sparse hits involved sex or use frequency. The two Holm survivors were sparse two-person cells. | **should fix** |
| F04 | `discussion.tex:75,79` | effects are “the same size” across BFI/demographic ranges; Latin-square rotation “holds [task] constant” | A failed interaction test is not an equivalence test. Task varies and is balanced by the Latin square; it is not held constant. | `personality_lmm.csv` and `demographic_moderation_lmm.csv` establish 0 corrected interaction hits, not equivalence. State “no moderation was detected.” The Methods describe task rotation/balance. | **should fix** |
| F05 | `discussion.tex:107` | “The orange cells of the Holm board are one column, explicit early” | Even restricted to Dataset B exploratory cells, only five of six are explicit early. The board also contains the two Dataset A timing cells. | `results.tex:256` and `eeg_ad_response_contrasts.csv`: five Dataset B exploratory hits are explicit early; the sixth is implicit-late relative \(\gamma\). Dataset A adds posterior \(\alpha\) and relative \(\theta\), both early−late. | **should fix** |
| F06 | `discussion.tex:107,220` | “the contrast between the two is the substance”; formats are “not interchangeable”; the record “distinguishes those two arrivals” | This infers an implicit–explicit difference from one condition being significant and the other not. The slow-power tilt is supported within explicit early versus matched no-ad, but no corrected direct format contrast supports “distinguishes.” | `tab:app-posthoc-near`: direct implicit-early−explicit-early cells have raw hits but are Holm-null (smallest Holm \(p=.08\)); `eeg_ad_response_contrasts.csv` planned onset format contrasts are secondary, uncorrected, with raw \(p\ge .063\) on the tilt measures. Keep the explicit-early exploratory finding; remove the direct-format verdict. | **blocking** |
| F07 | `discussion.tex:120` | “On Dataset B, eight nominal cells out of 256” | Eight and 256 are totals across A and B, not Dataset B. | `tab:app-posthoc-near`: 8/256 overall = 2 Dataset A raw hits among 160 + 6 Dataset B raw hits among 96. Correct Dataset B to **6 of 96**. | **should fix** |
| F08 | `discussion.tex:146` | “The advertised genre therefore usually equals the genre the conversation was already in” | Corpus-level modal overlap is converted into a false per-conversation claim. | `tab:app-traj-sources`: \(g^{(a)}=\hat g_2\) in 25/108 early-ad conversations (23.1%), not usually. The 98/156 count says that products are predominantly labelled general guidance at corpus level. | **blocking** |
| F09 | `discussion.tex:162` | “Eighteen people resolve \(\lvert\rho\rvert>.47\) and nothing smaller.” | This is an uncited raw-\(p\) critical-correlation/MDE statement, ignores the six-test family, and is explicitly excluded by the Discussion lock. | No frozen result table reports this as an estimand. Remove it; retain the observed estimate and interval. | **should fix** |
| F10 | `discussion.tex:166,228` | “the only change between \(\rho=.24\) and \(\rho=.80\)” proves the variance is an event; “the moment of insertion matters more” | Both correlations are quoted correctly, but their difference was not tested. A significant onset correlation and a null condition-aggregation correlation do not themselves establish that the correlations differ; the two EEG scores also differ in reliability. | `declared_families.csv`: A \(\rho=.237\), raw \(p=.343\); B \(\rho=.803\), Holm-within-six \(p=.000365\). Report those separate verdicts without claiming a tested A–B difference or precedence. | **should fix** |
| F11 | `discussion.tex:199,204` | the effects matrix contains “every estimated effect” | The source explicitly omits estimated cells, including significant ones. | `effects_matrix_cells.csv`: 121 rows; 87 estimated/zero, but only 71 of those are drawn. Sixteen estimated slow-tilt companion cells are `in_figure=False`; four omitted explicit-early companions are Holm-significant (global \(\theta\), relative \(\delta,\alpha,\beta\)). Change “every” and explain the aggregation, or render all cells. | **blocking** |
| F12 | `discussion.tex:209` | “the only filled trust cell anywhere in the grid is the early banner against \(a^{\emptyset}\)” | It is only the sole filled cell in the **post-condition trust row**, not anywhere in the grid. | `effects_matrix_cells.csv` also fills `recall_trust_shift × early_late` and `rho_B × any_ad`. Qualify the sentence to the post-condition trust row. | **should fix** |
| F13 | `introduction.tex:76`; `discussion.tex:257` | RQ5 asks broadly whether format and timing interact; the answer cites “all four post-condition outcomes” | The verdict is narrower than the RQ inherited from RQ1/RQ3, which include cued memory and trust after re-exposure. No interaction was estimated for those cued outcomes. | `confirmatory_planned_D.csv` contains `format_x_timing` only for trust, credibility, manipulation, and notice. Narrow RQ5 to those four outcomes or mark the cued part untested. | **should fix** |
| F14 | `results.tex:182,599` | “Nine logged interaction measures × three planned contrasts give 36” | \(9\times3=27\). The 36 rows include a fourth, uncorrected format×timing contrast. | `stats/run_sweep.py`: nine usable process measures after excluding two logger artefacts, each evaluated on the three planned contrasts **plus the interaction**: \(9\times4=36\). The no-raw-hit verdict is correct. | **should fix** |
| F15 | `results.tex:204` | “age was not recorded” | Age was recorded for all lab participants and 26/36 crowd participants; it was incomplete, not absent. This also contradicts `results.tex:25`. | `results.tex:25` gives the available age ranges; `demographic_moderation_summary.json` records why age was not modelled. Say “age was incomplete and therefore not tested.” | **should fix** |
| F16 | `results.tex:204,209`; `figures/results/tab_beh_demographics.tex:4` | demographic moderation is labelled \(N=54\) without per-model qualification | Sex and education models do not contain 54 people because of missing/excluded values. | `demographic_moderation_lmm.csv`: sex \(n=51\), education \(n=49\), familiarity/frequency/environment \(n=54\). Retain \(N=54\) for the cohort but state the model-specific \(n\). | **should fix** |
| F17 | `results.tex:317` | “none of the three differs by task (\(p=.33\)), arm (\(p=.85\)), or session position (\(p=.52\))” | The three displayed \(p\)-values are for \(N_{\mathrm{shift}}\) only, although the syntax attributes each to all three measures. The null verdict itself is correct. | `t4_variance_checks.csv`: task \(p=.330,.629,.325\); arm \(p=.849,.278,.857\); session \(p=.523,.252,.538\) for \(N_{\mathrm{shift}},H,R\). State that the quoted values are for \(N_{\mathrm{shift}}\), or report “all \(p\ge .25\).” | **should fix** |
| F18 | `results.tex:453,605` | deployed-context estimate \(-0.018\) | Inconsistent rounding within the thesis. | `contextual_sweep/tables/crossing_hard.csv`: \(-0.0185185\), which rounds to \(-0.019\); `appendix_f.tex:111` already prints \(-0.019\). | **cosmetic** |
| F19 | `results.tex:557` | “Personality and demographics … 60 tests” | The count and key estimate cover personality only, while the row label claims demographics too. | `personality_lmm.csv`: 60 tests. `demographic_moderation_lmm.csv`: 70 + 70 additional cells, already listed in `tab:results-checks`. Rename this row “Personality moderation,” or split/count the families explicitly. | **should fix** |
| F20 | `results.tex:595` | “Behavioural omnibus and ten-pair sweep … 80 … 13” | The row cites both layers but counts only the 80 pairwise tests and 13 pairwise Holm hits. | `omnibus_friedman.csv`: 8 omnibus tests, 3 Holm-across-eight hits; `omnibus_pairwise.csv`: 80 pairs, 13 Holm hits. If combined, report 88 tests and 16 Holm hits; otherwise rename the row to the ten-pair sweep and stop citing the omnibus table. | **should fix** |
| F21 | `appendix_f.tex:38–47` | column headed “ICC” contains `.58`, `.33`, `.85`, etc. | Those entries are Kruskal–Wallis \(p\)-values, not intraclass correlations. The actual ICCs are only in the final multicolumn row. | `outputs/eda/tables/t4_variance_checks.csv`: the column is `p`; ICCs are \(0.067,0.111,0.043\). Change the header to \(p\). | **blocking** |
| F22 | `results.tex:128`; `appendix_e.tex:196,201` | credibility Holm \(p=.017\); credibility implicit-late \(d_z=+.01\); manipulation implicit-late Holm \(p=.040\) | Small table/CSV mismatches; no verdict changes. | Frozen exact values are `.016497` (also `.016` in `tab:beh-item-loo`), `d_z=.004980` (two-decimal \(+.00\)), and `.039462` (three-decimal `.039`). | **cosmetic** |
| F23 | comment-only locations: `results.tex:263,276,278`; `discussion.tex:20,160,230–232`; `abstract.tex:12`; `conclusion.tex:30,34` | `BH`, `composites`, old RQ3/RQ8/RQ9, `k=37`, and `card` survive in comments | A strict raw-source lexical scan fails, although rendered prose passes. Several hits are mandatory `% WALTER:` comments and must not be deleted. | Compiled prose has no BH/Benjamini, no stale RQ10/11, no “Wilcoxon Holm,” and no context called a labelling. It uses “banner” except when `appendix_c.tex:115` quotes the interface's literal “Promotional Card” tag. Preserve Walter comments; exclude comments from the lint or reword only non-Walter comments. | **cosmetic** |
| F24 | `frontmatter/abstract.tex:5,15,23` | rendered behavioural placeholder; malformed `α\textbackslash{}alpha`-style symbols; a literal `+` | The current abstract is not a fact-checkable final abstract and will render WIP artefacts. Its supported behavioural and association results remain commented out. | Replace from Chapters 7–8 last, as required. The compiled abstract must include the frozen behavioural verdicts and the declared \(\rho=.80\) association, with valid LaTeX symbols. | **blocking** |
| F25 | `frontmatter/abstract.tex:15,24` | “timing and presentation matter”; future work measures “the price of attention” | Timing has one confirmatory condition-aggregation result. Presentation has an exploratory explicit-early cell, not a corrected direct implicit–explicit finding. “Price of attention” is unsupported and prohibited by the writing lock. | `eeg_condition_contrasts.csv`, `eeg_ad_response_contrasts.csv`, and `tab:app-posthoc-near`; retain the timing result and describe the explicit-early tilt as exploratory without a serving or attention-price claim. | **blocking** |
| F26 | `chapters/conclusion.tex:45` | response “depends on how and when”; relative \(\theta\) grouped into the “confirmatory distinction”; “greater visual processing than otherwise equivalent later insertions” | This fuses the two EEG estimands, upgrades exploratory relative \(\theta\), interprets it as visual processing, and calls depth-confounded conversations equivalent. | Chapter 7: only posterior \(\alpha\) is confirmatory under condition aggregation; relative \(\theta\) is exploratory. `discussion.tex:102` correctly states that early versus late is confounded with conversational depth. | **blocking** |
| F27 | `conclusion.tex:48,51` | implicit response is “substantially weaker”; explicit early demands “allocation of neural processing”; explicit late is an “attractive compromise” | Direct corrected format evidence is absent, neural allocation is not measured, and no serving recommendation follows from an exploratory cell. This repeats the difference-in-significance error in F06. | `tab:app-posthoc-near` and `eeg_ad_response_contrasts.csv`: explicit early has an exploratory slow-power tilt; corrected direct format contrasts do not establish a difference. Chapter 8 explicitly rejects an explicit-late serving rule. | **blocking** |
| F28 | `conclusion.tex:41` (queued behavioural draft comment) | the implicit format was one participants “failed to recognise when it was shown again” | False even though currently commented; it must not enter the final rewrite. | `notice_recall_percentages.csv`: cued memory \(\ge5\) for 31/54 (57%) implicit early and 32/54 (59%) implicit late; among non-noticers, 55% and 59% still recognised it. | **should fix** |
| F29 | `conclusion.tex:73` | product genres “only weakly overlap with the conversational genres” | This says the opposite of Results/Discussion, which identify heavy overlap as the problem. | `tab:traj-aligned-counts` / `tab:app-traj-sources`: 98/156 products are labelled general guidance, the modal conversation genre; 25/108 match \(\hat g_2\) exactly. Say that the target distribution overlaps the conversational background heavily. | **blocking** |
| F30 | `conclusion.tex:89` | a thesis “moment scorer \(m(s)\)” and ad scorer are proposed | This violates the current project hard stop, independently of the numerical fact check. | `AGENTS.md`: do not put the ad-moment scorer in thesis/paper/deck before 17 September. It is currently rendered in the thesis source. | **blocking** |

**Count:** 12 blocking · 15 should fix · 3 cosmetic.

## High-risk claims that do hold

- The planned behavioural directions and verdicts hold: explicit exceeds
  implicit for notice, perceived manipulation, and cued memory; early exceeds
  late for perceived manipulation, while credibility and trust after
  re-exposure are lower early. All are Holm-significant in the stated
  paired-\(t\) families. Post-condition trust is Holm-null on all three planned
  contrasts; its only condition-versus-control Holm hit is explicit early
  (\(-0.69\), Holm \(p=.031\)).
- The format×timing interaction is correctly null and small on the **four
  primary post-condition outcomes** (\(\lvert d_z\rvert\le .06\)); F13 is about
  scope, not those four estimates.
- The notice/recall counts hold exactly: sponsored-item notice is 25/54 and
  20/54 implicit versus 44/54 and 40/54 explicit; cued memory is 31/54 and
  32/54 implicit versus 47/54 and 44/54 explicit. Among implicit
  sponsored-item non-noticers, 16/29 (55%) and 20/34 (59%) report cued memory.
- The corrected personality and demographic verdicts hold within their actual
  scopes: personality 0/60 Holm; demographics 0/70 + 0/70 Holm. The nearest
  demographic cell is cued-memory timing × familiarity, Holm \(p=.443\).
- EEG condition aggregation has exactly one confirmatory hit: posterior
  \(\alpha\) early−late \(-0.22\) dB, Holm \(p=.0496\), raw Wilcoxon
  \(p=.021\). Writing−reading Fz \(\theta\) is \(+0.60\) dB, Holm \(p=.007\).
  All eight 4-s onset-locked confirmatory cells are Holm-null. The
  explicit-early slow-power tilt is real as an exploratory
  condition-versus-matched-control pattern, not as a corrected direct format
  difference.
- The declared trust × onset-locked posterior-\(\alpha\) association holds:
  \(\rho=.803\), 95% CI \([.481,.934]\), Holm-within-six \(p=.000365\),
  \(n=18\); the condition-aggregation counterpart is \(\rho=.237\), raw
  \(p=.343\). The sign interpretation in Chapters 7–8 is correct.
- The trajectory inventory holds: 270 conversations, 1,080 utterances, 810
  transitions, mean \(N_{\mathrm{shift}}=2.45\), all declared advertisement
  contrasts Holm-null, 9 aligned shifts versus 10.46 expected, and guidance
  share falling \(0.478\to0.211\) from turn 1 to turn 4.
- Statistical naming in rendered prose passes: Holm in behavioural paired
  tables is the adjusted paired \(t\); Wilcoxon \(p\) is raw; “Wilcoxon Holm”
  does not occur. The introduction and `tab:rq-answers` use the same RQ1–RQ9
  numbering, with no rendered RQ10/RQ11 or old task-type RQ3. The rendered
  “\(u_5\) does not exist” sentence occurs once. `% WALTER:` counts are exactly
  Results 28, Discussion 45, Conclusion 3, Abstract 1.

## Abstract and conclusion contradictions / stale claims

### Abstract

- F24: behavioural findings and the supported cross-family association are
  absent from rendered prose, while a placeholder, malformed Greek notation,
  and a literal plus sign remain.
- F25: “presentation matter[s]” upgrades a condition-specific exploratory cell
  to a direct presentation verdict; “price of attention” is not supported.
- The commented association paragraph is numerically correct
  (\(\rho=.80\), lower CI .48) but is not currently part of the abstract.

### Conclusion

- F26: the Dataset A paragraph contradicts the two-estimand and depth-confound
  account now fixed in Chapter 8, and treats exploratory relative \(\theta\) as
  part of a confirmatory visual-processing verdict.
- F27: the Dataset B and policy paragraphs infer an implicit–explicit
  difference, neural allocation, and an explicit-late serving compromise that
  Chapters 7–8 do not establish.
- F28: the queued behavioural paragraph says implicit advertisements were not
  recognised when re-shown; 57%/59% report cued recognition.
- F29: “weak overlap” directly contradicts Chapter 8’s heavy-overlap
  explanation.
- The supported trust × onset-locked posterior-\(\alpha\) result is present
  only in a TODO comment, not in the rendered Conclusion.
- F30: the rendered Future Work restores the ad-moment scorer despite the
  pre-17-September hard stop.
