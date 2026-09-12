# Work item 3 — Three decisions (Grok 4.6)

Read-only opinion for Walter. Sources: `introduction.tex` `sec:intro:research-questions` (commit `034f5d3` vs previous RQ11), `discussion.tex` `tab:rq-answers` and `sec:disc-limitations`, `results.tex` `sec:results-eeg` / `sec:results-combos` / `tab:results-summary`, `models.tex` `tab:analysis-families`, `system_design.tex` / `related_works.tex` / `references.bib`. Thesis voice: unanswerable RQs are removed, not left open; every remaining RQ is answered yes or no; a Holm survivor is stated as a finding first.

| # | Decision | Recommendation (one line) | Confidence |
|---|---|---|---|
| D1 | RQ11 reframe vs drop | Keep the covariation RQ (do not drop; do not restore the ablation). If one more edit is cheap, name the declared six-pair family, not only trust. | high |
| D2 | RQ8 "Partly" | Keep **Partly**. Do not split. Do not call it Not supported. Add one caption clause that defines Partly. | high |
| D3 | Model comparison sentence | Option (a): delete the ranking sentence. The two sentences before it already do the job. Do not rank Qwen against GPT-4o. | high |

## D1 — Old RQ11: reframe or drop?

**Judged sentences.** Old RQ11 (pre-`034f5d3`): *“Do neurophysiological signals provide additional explanatory power beyond self-reported and behavioural measures of user experience? (Ablation)”.* Walter’s own note above that block: *“RQ11 should probably be dropped because we didn't perform that”.* New RQ9: *“Does the neurophysiological response at the moment the advertisement appears covary with the trust the user goes on to report?”* Lead of `sec:intro:research-questions` still says the fourth block is *“what the neurophysiological record adds to what people report.”* Contributions bullet was already rewritten off the ablation (*“relate the response recorded at the advertisement's onset to what participants report”*). Methods already named the estimand: `tab:analysis-families` Behaviour × EEG = *“6 pairs: Fz θ and posterior α × trust, credibility, manipulation; Holm within six for each score”*, on both \(D^{A}_{i}\) and \(D^{B}_{i}\), *“association and not mediation”*. Chapter 7.6 answers that family: onset-locked trust × posterior \(\alpha\) \(\rho=.80\) \([.48,.93]\), Holm \(p=.0004\) (\(n=18\)); \(\rho=.24\) under condition aggregation; the other five Dataset-B pairs Holm-null.

**Reasoning.** Dropping the *ablation* is mandatory: it was never run, and leaving it would violate the voice rule that unanswerable RQs are removed. Dropping *any* EEG–trust question is the worse of the two remaining options: the association family was declared before the board was read, it is the one Holm survivor in the combo families, and `tab:rq-answers` would then have no row for the result a committee will actually ask about. Reframing from incremental \(R^{2}\) to covariation is therefore the honest move, provided nobody claims incremental value in the defence. The residual HARKing smell is not the reframe itself; it is that RQ9 names **trust only**, while Methods declared six pairs. That is the clause a hostile examiner will read as written after \(\rho=.80\).

**What a hostile examiner would say.** *“You asked for an ablation, did not run it, then wrote a new RQ around the one Spearman that survived. The introduction still says the EEG ‘adds’ something. That is HARKing.”* Rebuttal, one sentence: the six pairs and both EEG scores are in `tab:analysis-families`; RQ9 is that family, not a post-hoc hunt; we did not, and do not, claim incremental explanatory power.

**Risk of each option.**
- **Keep current RQ9 (reframe, trust-only).** Low process risk, medium optics risk if anyone still has the old 11-RQ list. Defence line above is enough.
- **Widen RQ9 to the six pairs, keep Supported.** Lowest HARKing risk. One-line edit in Introduction + the Question cell of `tab:rq-answers`. Worth it if there is one more Overleaf pass.
- **Drop RQ9.** Looks clean against HARKing, but then a declared Holm \(p=.0004\) cell has no RQ, and the fourth block is only the mixed EEG question. The committee will ask about \(\rho=.80\) anyway; better to own it.
- **Restore the ablation RQ as unanswered.** Forbidden by voice; looks unfinished.

**Exact wording proposed (only if there is one more edit).**
- RQ9: *“Do the confirmatory neurophysiological scores at the advertisement’s onset covary with the trust, credibility, and felt manipulation the user goes on to report?”*
- Verdict stays **Supported**; evidence cell already names the one pair and the aggregation null.
- Lead of `sec:intro:research-questions`: replace *“what the neurophysiological record adds to what people report”* with *“whether the neurophysiological record tracks what people report.”* That leftover “adds” is the only remaining ablation word in the RQ section.
- Defence, if asked why not incremental value: *“That would be a nested model of trust on behaviour plus EEG. We did not run it. We ran the declared Spearman family.”*

## D2 — RQ8 verdict “Partly”

**Judged sentences.** RQ8: *“Do format and timing register in the user's neurophysiological response, measured as frontal-midline \(\theta\) power at Fz and posterior \(\alpha\) power, with the published engagement indices as an exploratory battery?”* `tab:rq-answers` RQ8: *“Partly & early − late posterior \(\alpha\) \(-0.22\) dB, Holm \(p=.0496\); format Holm-null on both confirmatory markers; engagement indices silent.”* Caption defines only Not supported (*“the family was estimated and no cell survives Holm”*); Partly is undefined. Prose under the table: *“One is answered in part, in that the moment of insertion registers in the confirmatory neurophysiological markers while the format does not.”* Confirmatory numbers (`sec:results-eeg`, `tab:results-summary`): Dataset A, 6 tests, 1 Holm cell, early−late posterior \(\alpha\) \(-0.22\) dB \([-0.39,-0.04]\), Holm \(p=.0496\) (raw Wilcoxon \(p=.021\)); Dataset B, 8 confirmatory cells, 0 Holm; format (implicit−explicit) Holm-null on both markers under both estimands; exploratory explicit-early slow-power tilt is not a confirmatory format result; engagement indices (FAA, both Pope ratios, Kislov) Holm-null throughout.

**Reasoning.** RQ8 is a conjunction: format **and** timing. Timing has one confirmatory Holm survivor; format does not. English for that is Partly. Calling the whole row Not supported buries a Holm cell and breaks the voice rule that a Holm survivor is stated as a finding first. Splitting after seeing \(p=.0496\) is the actual post-hoc move: it would manufacture a standalone **Supported** whose entire load is one \(n=18\) cell at the Holm fence, while Dataset B (the onset estimand) is confirmatory-null. A committee reads \(p=.0496\) as “survived multiplicity, barely.” That is a caveat in the evidence column, not a reason to change the verdict word. Keep Partly; define it in the caption so it is not a one-off.

**What a hostile examiner would say.** *“You are hanging a research question on \(p=.0496\), \(n=18\), one of six Dataset-A tests, and the onset-locked family is empty. That is not ‘timing registers.’”* Rebuttal: Holm is the pre-specified threshold; the interval excludes zero; we already say Partly, not Supported; format is Not supported in the same cell; we do not recruit the exploratory tilt into the verdict.

**Risk of each option.**
- **Keep Partly + caption gloss.** Honest, matches the conjunction, does not over-claim the fence \(p\). Residual risk: a fourth verdict in a three-word column. Fix: one clause in the caption.
- **Split into timing RQ (Supported) and format RQ (Not supported).** Cleaner table, worse science: a new Supported built after seeing the board, and the defence then has to sell \(p=.0496\) as a full yes. Also renumbers RQ8–RQ9 eleven days before Padova.
- **Call RQ8 Not supported, keep the timing cell in Evidence.** Looks disciplined, reads as hiding the only confirmatory EEG advertisement result. A statistician on the committee will ask why a Holm cell is filed under Not supported when the caption says that word means *no* cell survived.

**Exact wording proposed.** Keep the RQ8 row. Change the caption of `tab:rq-answers` to: *“Not supported means the family was estimated and no cell survives Holm. Partly means the family was estimated and only one of the two factors survives Holm (here: timing, not format).”* Do not touch the evidence numbers. In the defence, say the timing cell first, then *“it is one cell, Holm \(p=.0496\), and the onset-locked confirmatory family is null.”*

## D3 — Comparative model claim in Limitations

**Judged sentence** (`sec:disc-limitations`, paragraph *Design and sample.*, last sentence of the assistant paragraph):

> On public benchmarks the model is comparable to or stronger than the assistants used in the studies this design builds on \cite{tang2025adstalkbackimplications}, so the effects reported here are not an artefact of a weak assistant.

The two sentences immediately before it already state the limitation: *“The assistant was a quantized Qwen 3.6 35B-A3B deployment (`ch:system-design`), the strongest model the available hardware could serve when the study ran. Stronger open-weight models were released within months of data collection, and how the same advertisements land on a better assistant is not something these data can say.”* Walter’s source note (`discussion.tex` comment 6): *“qwen 3.6 is probably better than the models they used for other papers like gpt 4.o or phiads.”* The ranking sentence cites only Tang, claims “the studies” (plural), gives no number, and draws a causal gloss (“not an artefact”) that a benchmark cannot support.

**Models the cited advertising-in-LLM studies actually used** (only what `related_works.tex` names; “PhiAds” is not in that file):

| Study | Bib key | Assistant / generator named in `related_works.tex` |
|---|---|---|
| Tang, Sun, Curran, Schaub, Shin | `tang2025adstalkbackimplications` | Fine-tuned **Phi-4** (sneak-ads); halo comparison **gpt-3.5** vs **gpt-4o** |
| Zelch, Hagen, Potthast | `zelch2024acceptance` | **YouChat** and **ChatGPT** (2024) |
| Meguellati, Civelli, Han, Bernstein, Sadiq, Demartini | `meguellati2025llmads` | Unnamed **multimodal LLMs**; “latest models of 2025” |
| Xu, Chen, Deng, Huang, Schoenebeck | `xu2026ad` | None (theory: bidding on inferred intent) |
| Qiu, Mei | `qiu2026generative` | None (taxonomy / trustworthy commercial intervention) |
| “PhiAds” | — | Not in `related_works.tex`. Only Walter’s comment. Likely a nickname for Tang’s Phi-4 setup. |

Nearby but out of scope for this claim: Zhao et al. (`zhao2025exploring`) conditioned **GPT-4o** in a CRS personality study, not an ads-in-LLM assistant deployment.

**Benchmark citations that exist in `references.bib`.** `artificialanalysis2026qwen36` is the Qwen 3.6 35B-A3B page (note: Intelligence Index 32). `qwen32026` is the Qwen 3 technical report. Neither is a head-to-head against GPT-4o, Phi-4, YouChat, or ChatGPT. There is no Chatbot Arena / LMSYS / MMLU comparison table in the bib that could carry option (c). `muennighoff2023mteb` is an embedding benchmark, not an assistant-quality ranking.

**Reasoning.** A limitation chapter says what the design could not see. The first two sentences already do that. The third sentence is a ranking plus a “therefore not an artefact” claim. Against Phi-4 the ranking is plausible and still uncited; against GPT-4o (which Tang treats as the *stronger* halo model) it is the sentence an examiner will ask you to put a number on, and you do not have one in the bib. Meguellati’s “latest models of 2025” may be frontier multimodal systems; ranking a quantized 35B-A3B above them is not a limitation, it is a fight. Xu and Qiu have no assistant to rank. Option (c) is unavailable. Option (b) is honest but invites the follow-up “so how does Qwen compare?”, which is the fight (a) avoids. Eleven days before Padova, delete the ranking.

**What a hostile examiner would say.** *“Show me the benchmark where Qwen 3.6 35B-A3B Q4_K_M is comparable to GPT-4o. You cite only Tang. Tang’s own halo result is that GPT-4o looked less pushy than GPT-3.5. If model quality changes how ads feel, your effects could still be an artefact of this deployment.”* There is no slide that wins that exchange.

**Risk of each option.**
- **(a) Delete the ranking; keep the two generation sentences.** Safest. Matches Limitations ≠ Future work. Defence: *“one model generation, hardware-limited, newer open weights exist; we do not rank it.”*
- **(b) Name the other studies’ models, no ranking.** Honest, longer, still invites “and therefore?”. Only do this if Walter wants the Tang/Zelch names on the page. Proposed clause, if so: *“The user studies this design builds on used Phi-4, GPT-3.5 and GPT-4o \cite{tang2025adstalkbackimplications} and YouChat and ChatGPT \cite{zelch2024acceptance}; the present results are for this one deployment.”* No “comparable”, no “not an artefact.”
- **(c) Keep the ranking with a benchmark citation.** No supporting bib entry. Do not write one in the next eleven days.

**Exact wording proposed (option a).** Delete the judged sentence. Leave:

> The assistant was a quantized Qwen 3.6 35B-A3B deployment (\autoref{ch:system-design}), the strongest model the available hardware could serve when the study ran. Stronger open-weight models were released within months of data collection, and how the same advertisements land on a better assistant is not something these data can say.
