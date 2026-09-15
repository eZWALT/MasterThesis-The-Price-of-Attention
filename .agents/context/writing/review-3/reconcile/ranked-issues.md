# Loop 3b: ranked issues from the ten-jury review of thesis v1

15 Sep, late morning. Inputs: `issue-taxonomy-seed.md` (seeded from OP /
FB / GS), `map-GM-MU-KK.md`, `map-DS-GX-CG-CS.md`, and my own `rg` /
Gold checks. Canvas: `loop-3b-jury-reconciliation.canvas.tsx`.

Coverage column = number of the ten dumps that raise the item
(CG DS GX CS GM MU KK web; OP FB GS in-IDE). Because the taxonomy was
seeded from OP / FB / GS, those three count as raising every seed ID by
construction; the honest independent count is the web number plus
"seed". Verified = I checked the claim against the `.tex` or a frozen
Gold file today, not against a jury.

Status: **rev** = applied in green (`\rev{}`) in the source, compiles;
**decision** = needs Walter; **open** = cheap, not yet done; **park** =
not before Thu.

## Tier 0: decisions only Walter can take (science, not prose)

| # | Issue | Evidence I verified | Options | Effort |
|---|---|---|---|---|
| D1 | **The one confirmatory EEG survivor is fragile to \(k\).** Early − late posterior \(\alpha\) on condition aggregation: \(k=37\) gives \(-0.22\) dB, Holm .0496. The frozen \(k\)-sweep (`sensitivity/ad_local_epochs/dataset_a/around/k{1,3,5,10,20,37}`) gives \(k=1\): \(-0.31\), raw .28; \(k=3\): \(-0.20\), raw .41; \(k=5\): \(+0.17\), raw .45 (sign flips); \(k=10\): \(-0.04\), raw .78; \(k=20\): \(-0.13\), raw .18. Only \(k=37\) is significant. The epoch-width grid Table 7.9 cites was run on the whole-window Dataset A (4 s: \(-0.09\), raw .20), so it never re-estimated this cell. Nothing in the thesis says any of this. | \(k\)-sweep CSVs, `epoch_length_grid_comparison.csv`, `analysis/README.md` | (a) Print the \(k\)-sweep as one sensitivity row in App D + one sentence in §8.3 ("the cell is specific to \(k=37\), the pre-specified value; at smaller \(k\) it is null") — honest, defensible, \(k=37\) was fixed before Gold. (b) Say nothing and hope no examiner asks "did you vary \(k\)". (c) Demote the cell in the Abstract to "one boundary cell". I recommend (a) + keep the Abstract sentence as now rewritten (with depth caveat). | S: one table row, two sentences. Re-plot allowed; no rebuild. |
| D2 | **\(\rho=.80\) selection.** Pair evaluated on two EEG scores (A: \(\rho=.24\), raw .34; B: \(\rho=.80\)); Table 7.8 counts the family as 6, text promises "across twelve" Holm. Split-half of the B score is .56, so \(\rho=.80\) exceeds the reliability ceiling of the pair (\(\sqrt{.56\times r_{tt}(\text{trust})}\)). | S4, L5, L6 (7 of 10 juries) | Print \(\rho_A\) beside \(\rho_B\) in §7.6.1, count the family as 12, and add one clause on the ceiling in §8.5. Holm .001 at 12 cells is still \(<.05\). | S once decided |
| D3 | **"Confirmatory" without pre-registration.** DS, GX, KK, MU make it CRITICAL; CS, CG do not. The thesis never claims pre-registration; it says "before the results were read". | S6 | One sentence in §6.3: "planned and fixed in the analysis repository (commit, date) before Gold was read; not pre-registered externally." Needs the commit hash from you. | S |
| D4 | **Task × condition realised table; task not in the LMM.** \(N=54\) is not a multiple of 25; balance is in expectation. Asserted "not confounded", table not printed. | S5 (7 of 10) | Print the realised 5 × 5 count table in App E from `advertisement_features.csv` (task_id × condition). One paragraph. Optionally add task as a fixed effect in the LMM check — that is a re-estimation, your call. | S (table) / M (LMM) |
| D5 | **Arm pooling.** Lab vs crowd differ in age (29.5 vs 35.7) and extraversion (raw .039); arm never a factor; no by-arm headline. | S10 (6 of 10) | Print manipulation any-ad and notice any-ad by arm (two numbers each) in App E; one sentence in §8.7. | S |
| D6 | **RQ2 / RQ4 verdict wording.** Table 8.1 says "Not supported" where §8.4 says the instrument failed. Ch 9 "not a conversation steered towards the product" states the null as a fact. | L24, NEW-KK-2 | Table 8.1: "Not testable with this instrument"; Ch 9: "and no steering that the genre instrument could detect". RQ answers are yours. | S |
| D7 | **Demographic model description.** Methods says demographics enter the personality LMM as covariates; they were tested as moderators in a separate 70 + 70 check, with \(n\) 51 / 49 / 54. | L3, L4 | Reword Methods; add the check as a row in Table 6.1 or say in §6.3 that it is not a family. | S |
| D8 | **Holm-within-measure rationale.** "Dependence would distort" is not why one chooses a family; Holm is valid under dependence. The choice is a family definition. | S14 (4 of 10) | Reword the App D sentence: "the family is the three planned contrasts on one measure; a correction across the sixteen measures would answer a different question, whether any measure moves, which the exploratory board reports uncorrected." | S |
| D9 | **Seven exploratory Holm cells have only a \(p\).** 4.60 dB appears first in §8.3. | L11, L12 (5 of 10) | Add M and CI for the seven asterisked cells as a small table in App D (or a column in Fig 7.8's data). Grok subagent, table code only. | M |

## Tier 1: verified, cheap, applied in green today

| ID | Where | What changed |
|---|---|---|
| S1 latency co-intervention (10/10) | `models.tex` §6.2.5 new bullet; `discussion.tex` §8.7 "Four features" | 3.03 s pre-token wait on the advertised turn stated as a confound; pre-onset window note |
| I1 / I2 / I10 Ch 9 prescription (7/10) | `conclusion.tex` | "prescription is about disclosure" → disclosure vs presentation not separable; "be patient / earliest turns" → "measure what a placement costs before adopting it"; "concentrates on early banner" → post hoc |
| I3 "informative answer is at the event" | `conclusion.tex` two places | corrected = aggregated, exploratory = onset; "not dead" language → "Fz \(\theta\) pipeline" |
| I4 post hoc trust cell (6/10) | `abstract.tex`, `conclusion.tex` | "trust did not differ on any planned contrast; in a post hoc localisation…" |
| I5 / I6 / I7 / I14 Abstract EEG (8/10) | `abstract.tex` | "aggregated over each condition", depth caveat, "exploratory", arrows spelled out (relative \(\alpha,\beta\)), "formats not shown to differ", "candidate correlate … replication", \(n=18\) |
| I8 moderation sentence | `abstract.tex` | "no moderation by personality or by the recorded demographics was detected" |
| I9 / I13 Ch 9 uneven cost, "smaller than the debate" | `conclusion.tex` | one-association caveat; referent-less clause dropped |
| I11 "Trust holds up" (4/10) | `discussion.tex` §8.1 | "Trust is not shown to fall"; CI \([-0.71, 0.03]\) printed |
| I12 attention shift in §1.4 | `introduction.tex` | reserved for the causal case |
| I15 Abstract serving-policy framing | `abstract.tex` | user-side cost framing, twice |
| L1 behavioural interaction (4/10) | `results.tex` §7.2.1 + Table 7.9 row | Gold: trust \(+0.09\) \([-0.31, 0.49]\), credibility \(-0.03\), manipulation \(-0.10\), notice \(-0.06\); raw \(p\ge.65\) |
| L2 EEG interaction (6/10) | `models.tex` §6.3 + Table 7.9 row | "coded, not halved, descriptive"; Gold \(k=37\): Fz \(\theta\) \(+0.02\) \([-0.26, 0.31]\), posterior \(\alpha\) \(+0.04\) \([-0.58, 0.66]\) |
| L8 negative control (3/10) | `results.tex` §7.5 | points to §6.2.5, says what a difference would mean |
| L9 "not a test but a check" | `results.tex` §7.5 | instrument check, Holm across six genres |
| L10 "nothing omitted" | `results.tex` §7.7 | "every family and check has a row" |
| L13 width grid contradiction (3/10) | `appendix_d.tex` D.1 + Table 7.9 | grid is whole-window A + B; \(k=37\) cell not re-estimated off 4 s (feeds D1) |
| L14 "under 3 %" | `appendix_d.tex` D.2 | largest is \(-0.22\) dB ≈ 5 % |
| L21 "borderline significant" ×2 | `results.tex` | both removed |
| S7 no-ICA tilt numbers (6/10) | `appendix_d.tex`, `discussion.tex` §8.3 | \(+4.60\) dB (Holm .007) with ICA vs \(+3.04\) (raw .073) without; no-EOG caveat |
| S9 trust ceiling (5/10) | `results.tex` §7.2.1, `discussion.tex` §8.1 | credibility 5.7–6.1 at ceiling; trust 4.7–5.4, SD 1.6–1.9 |
| S12 debrief text (2/10) | `appendix_c.tex` | note: "ChatGPT" and "selected randomly" inherited from Tang et al.; not what ran |
| S22 embedding dimension | `dataset.tex` ×3 | 1536 → 1024 (index 117,343 × 1024 float32 = 459 MB) |
| S25 mechanical | 9 × `\autoref{subsubsec:…}` → `\S\ref{subsec:…}` (Equation 4.2.4 / Figure 4.2.4 gone); "Figure Figure 5.3"; truncated "at most 1"; "It has been proven"; bare `\ref` in Ch 9 | |

Compiled locally (XeLaTeX, Docker): `docs/overleaf/thesis/_build/dissertation-rev-15sep.pdf`, 151 pp, no undefined references. Green = `\useReviewMarks=1` in `dissertation.tex`; flip to 0 for the submission PDF.

## Tier 2: verified, cheap — **applied in green 15 Sep midday (`f2132a7`)**

| ID | Fix | Effort |
|---|---|---|
| L7 \(\delta^{(a)}_2\) McNemar declared primary, Table 7.5 Holm column is the paired \(t\) | print the exact McNemar \(p\) in the table or re-declare | S |
| L16 "Holm \(p\)" covers \(t\), Spearman, Wald | one clause in §6.3 naming the estimator per family | S |
| L17 / L18 / L19 Fig 8.1 caption asterisk with no asterisks; Fig 7.12 / 7.13 captions contradict; Table 7.9 "Sig." for raw \(p\) | caption edits | S |
| L22 "four values" → five; L23 Table 7.1 test not named; L25 "shorter form"; L26 Table 4.6 Kc whole-window in a "confirmatory" table; L27 onset uncertainty stated two ways; L28 ".050*" | wording | S |
| S2 notice item is format-specific ("sponsored buttons") | one limitation sentence §8.7 | S |
| S8 format contrasts carried by one item | sentence in §8.1 | S |
| S15 / S16 / S17 timing = exposure regime; format = bundle; implicit onset during streaming | §8.7 already has depth; add one sentence each | S |
| S23 117,343 vs 117,243 | say "100 products lack a rating" if true (check `catalog_pipeline.py`) | S |
| S25 rest: "Behavioral" in a title, "Promotional Card", Related Work exclamation marks / "barely nobody", DistilBERT 0.5 GB, Eq 4.5 argmax, ref years | one pass | S |
| §1.2 "prescriptions for companies" | drop | S |
| NEW-CS-3 Abstract credibility "by about a third of a point" lacks "against a late one" | add referent | S |
| NEW-CS-1 "environment" = arm never defined | one clause | S |
| NEW-KK-3 nine logged measures never listed | footnote | S |
| NEW-MU-6 same \(k\) for shortlist (30) and epochs (37) | rename shortlist to \(m\) or \(k_{\mathrm{ret}}\) | S |

## Tier 3 — **all applied in green 15 Sep afternoon (`b7823dd`)**, incl. the Fig 7.12a re-plot

Each row: what the juries said, where it lives, the fix applied. S11 got the 83.8 % / 32.5 % validity sentence in §8.5; NEW-GM-1 got a bridging sentence, not a cut; S26 kept as open-source (Walter: it will be true soon); added data card, seeds, identifier; S29 fixed the two arXiv years (Salvi, Wu → 2026) and the Kosmyna summary. Mention-position distribution (S13) not added: not in Gold.

| # | ID | Issue | Where | Smallest fix | Effort | Recommend |
|---|---|---|---|---|---|---|
| [x] | S24 | Theory: \(A\) has \(T-1\) slots so \(a_4\) is undefined; \(A\) written both as set and sequence; \(R_{\max}\) "maximal contiguous run" ambiguous; "It has been proven"; \(D\) overloaded | Ch 3 Definitions 1–6 | one clarifying clause per item, no change to any definition | S–M | **Do before PDF** (S24 is the only Tier 3 item an examiner reads in Ch 3) |
| [x] | S20 | EEG filter type / phase not stated | §4.2.4 Preprocessing | one clause: filter family, zero-phase, cutoffs | S | Do before PDF, verify against `clean_recording()` first |
| [x] | S21 | "50 Hz inside gamma" (gamma is 30–40 here); Wilcoxon "assumes no distributional form" overstated | §4.2.4 / §6.3 | fix two phrases | S | Do before PDF |
| [x] | S13 | Fig 6.1 illegible at print size; banner disclosure label string never quoted; mention position distribution not reported | Ch 6 | quote the exact "Sponsored" label string (S); re-export Fig 6.1 (plot, grok); position distribution = one sentence from Gold | S + plot | Quote the string; Fig re-export only if time |
| [x] | NEW-DS-8 | 2,560-test map: "105 raw hits where 128 expected" read as a finding when it is the chance expectation | §7.6, Table 7.11 | say "consistent with chance" in the same sentence | S | Do before PDF |
| [x] | NEW-CG-1 | Five explicit-early exploratory cells compressed into one "slow-power tilt" | Abstract, §8.3 | Abstract rewrite already lists them as exploratory; §8.3 keep "one tilt" but name the five cells once | S | Optional |
| [x] | S19 | Kruskal–Wallis on 270 conversation rows (pseudoreplication); global permutation breaks pairing | §7.5, App E | already declared exploratory; add "conversation-level, not person-level" once | S | Optional |
| [x] | S11 | Genre classifier: no target-domain validation; mean max posterior .43 unused | §8.7, App C | limitation sentence exists; could add the .43 figure | S | Skip (already a stated limitation) |
| [x] | S29 | Related Work reads as an annotated list; [22] antecedent unclear; [25] summary mismatch | Ch 2 | check [22] and [25] (S); restructure (L) | S / L | Fix the two citations; restructure is paper work |
| [x] | NEW-GM-1 | Neuromarketing literature does not feed the EEG method used; compress | Ch 2 | cut ½ page | M | Skip for thesis; paper |
| [x] | S26 | Open-release claim without DOI / manifest / seeds | Ch 9, App F | soften to "will be released" or add manifest | S / M | Soften only; release is a side quest |
| [x] | — | Jury scores (7.5–8.5 ranges) | — | none | — | Ignore; UniPD scale differs |

Fig 7.12a re-plotted from frozen `declared_families.csv` (B filled squares, A hollow circles, same as 7.13b); caption updated.

## Suspected false premises, not applied

**Corrections (15 Sep):** CG's "Holm .047 for re-exposure trust" is **correct**, not a false premise. Gold `confirmatory_planned_D.csv`: trust after re-exposure early − late \(D=-0.49\) \([-0.90,-0.08]\), raw .023, Holm .047, significant; Table 7.2 prints it in bold and the Abstract, §7.2 and RQ3 keep it. It was never removed from the thesis. MU's "Theory already writes \(\delta^{(a)}_k\)" is also correct (theory.tex Eq. ad-associated-genre-shift); the Results "shorter form" sentence was the stale one and is now fixed (L25).


Kept out of the ranking after checking: "depends on how and when" in the Abstract (DS) — not in the source; "greater visual processing" — not in the source; Fz \(\beta\) for Fz \(\theta\) throughout DS; GX's "prescription does not appear" (it does, Ch 9 line 46); GM's "confirmatory cells appear only off 4 s" (inverted); GM's 6/7 trust ceiling (that is credibility); DS's 3 × 16 / 4 × 16 family sizes.

## Critique of the ensemble metaprompt (short)

1. **The brief leaked.** Every web jury reproduced the checklist order, the "Wilcoxon Holm" check, "equal-n neighbourhood", the verdict opener, and in two cases (DS, GX) built a Top-1 on a phrase that exists only in the brief. Counting juries therefore does not count evidence. Effective independent web juries ≈ 1.5, not 7.
2. **Dependence weights must be per item, not per dump.** A brief-listed item gets no extra credit from a web jury; a novel item from a web jury (NEW-CS-1, NEW-KK-3, NEW-MU-6) gets full credit. The current metaprompt weights the dump.
3. **Verification was delegated to readers who cannot grep.** Only the in-IDE dumps could check the source; the web dumps produced a dozen wrong numbers (DS Fz \(\beta\), GM "safe"). Pipeline should be: juries propose → agent verifies against `.tex` and Gold → only verified items are ranked. That is what this file does.
4. **Jury severity is uncalibrated.** GM CRITICAL on Kruskal–Wallis (declared exploratory), DS CRITICAL on a false premise. Use severity as a tie-breaker only; rank on verified × surface (Abstract / Ch 9 / RQ table) × cost to fix.
5. **The seed biases coverage.** Seeding the taxonomy from OP / FB / GS makes those three cover every ID; coverage should be reported as "web count + seed", as here.
6. **Drop the 0–10 scores.** 5.5–6.5 across ten juries with different premises is noise.
7. **What the juries did well and the metaprompt should keep:** the Job-1 declared-vs-reported ledger. It produced every L-item, and those were the cheap, real fixes.
