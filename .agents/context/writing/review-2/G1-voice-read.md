# Work item 1 — Voice read (Grok 4.6)

## Summary
- Chapters read: abstract, introduction, related_works, theory, dataset, system_design, models, results, discussion, conclusion, appendix_a–f (comments skipped except unfulfilled `% WALTER:` requests still visible in the prose below them).
- Findings: 72 (by type: titles 9, AI-ish 16, WIP 5, jargon 8, nomenclature 5, redundancy 6, results/discussion boundary 13, length 8, direction 2)
- Top 10 fixes by reader impact (one line each, file:line)
  1. `dataset.tex:226` — live WIP: Gold “still being frozen”.
  2. `models.tex:88` — “sessionmonly” garbles the implicit-format sentence.
  3. `dataset.tex:112` — truncated “The pipeliene c” prints in the PDF.
  4. `related_works.tex:56` — informal “landspace” closer; company-first.
  5. `discussion.tex:131` — slogan title “A Holm-null is not a verdict…”.
  6. `results.tex:104` — Gold filename and freeze date in the PDF.
  7. `models.tex:290` — “not estimated in this draft” still on the page.
  8. `discussion.tex:88` — restores “depends on how and when”.
  9. `results.tex:316` / `:334` — finding-titles, not noun phrases.
  10. `discussion.tex:224` — WALTER: “too AI-ish”; opener still slogan.

## Findings
| # | File:line | Quote (≤ 20 words) | Type | Why it hurts | Suggested fix (≤ 20 words) |
|---|---|---|---|---|---|
| 1 | introduction.tex:23 | “the landscape of the world has been changed forever” | AI-ish | Banned filler; first page already sounds generated. | Cut “landscape”; one concrete sentence on chatbots. |
| 2 | introduction.tex:35 | “Alphabet (Google)… 402.8$… 294.7B$… Meta's 2025 revenue of 201B$” | length | One blob; reader must reread the revenue parade. | Split into two short sentences; fix $ units. |
| 3 | introduction.tex:46 | “improve AI companies data driven decision-making to create advertising policies” | AI-ish | Company-yield frame; voice lock is user-cost. | Say what ads cost the user, not the firm. |
| 4 | introduction.tex:52 | “So to summarize… steer their advertisement policies to maximize everyone's welfare” | AI-ish | Throat-clearing plus serving-rule close. | Drop “So to summarize”; end on the user. |
| 5 | related_works.tex:14 | “Publication Related Work” | titles | Leftover paper heading; not a thesis noun phrase. | Retitle “Conversational advertising literature.” |
| 6 | related_works.tex:17 | “The rapid adoption of large language models has fundamentally changed…” | length | Template opener; paragraph then never stops. | Cut the throat-clearer; start at conversational ads. |
| 7 | related_works.tex:53 | “To the best of our knowledge, no research to date sits at the intersection” | AI-ish | Stock claim, then says the same gap twice. | One clause: no LLM–ad–EEG study yet. |
| 8 | related_works.tex:56 | “Summarizing everything informally, the landspace in one-sentence is” | AI-ish | Slang closer; “landspace”; “screw you over”. | Delete; the chapter already made the point. |
| 9 | related_works.tex:56 | “besides serving companies improve their advertisement policies” | AI-ish | User-centric lock broken in the last sentence. | Lead with what users notice and feel. |
| 10 | theory.tex:41 | “the most ethical and interesting for companies wanting to push advertisements” | AI-ish | Advertiser ethics in the genre definition. | Keep the allocation fact; drop “ethical for companies”. |
| 11 | theory.tex:41 | “hard-labels… due to the labelling effort, this is why our work will be” | length | Run-on; “labelling” here is annotation, not `contexts`. | Split; say hard labels because that is what was logged. |
| 12 | dataset.tex:112 | “The pipeliene c” | WIP | Broken sentence prints before the figure. | Delete, or finish one caption sentence. |
| 13 | dataset.tex:124 | “will be able to leverage items semantically” | AI-ish | Banned verb; empty. | “retrieve products by meaning, not wording.” |
| 14 | dataset.tex:215 | “participant \(\times\) condition grain” | jargon | `grain` never glossed for a non-specialist. | “one row per person and condition”. |
| 15 | dataset.tex:218 | “Folder tags remove… unfinished… synthetic, crowdfail… unfocused remain in” | redundancy | Roster filter again at models.tex:151 and results.tex:15. | Keep Methods; Results one clause; drop Dataset retell. |
| 16 | dataset.tex:226 | “still being frozen and will be described here once that ETL is locked” | WIP | PDF says the battery is unfinished; it is not. | Describe the Gold tables that already exist. |
| 17 | dataset.tex:255 | “Late advertisements have no following utterance” | redundancy | Same structural fact: 261; models 78, 191, 309; results 365, 419; discussion 294. | Keep Results 7.5 once (`u_5`); cut the rest. |
| 18 | dataset.tex:324 | “Dataset A (condition aggregation) and Dataset B (onset-locked contrast)” | redundancy | Two-estimand lesson retold at results.tex:216, discussion.tex:88, conclusion.tex:32. | Define in Ch 4; later chapters point, do not reteach. |
| 19 | dataset.tex:324 | “median of the 37 epochs nearest visual onset… \(Y_A\in\mathbb{R}^{18\times 5\times 16}\)” | length | Whole-window, \(k\), shapes, and both estimands in one blob. | One estimand per paragraph. |
| 20 | system_design.tex:21 | “give better latencies than more complex hierarchies leveraging persistent disk” | AI-ish | `leveraging` filler in a requirements list. | “without paging to disk”. |
| 21 | system_design.tex:83 | “A critical model for the retrieval pipeline is the embedding model” | AI-ish | `critical` opener; adds no fact. | Start with the model name and the job. |
| 22 | system_design.tex:110 | “context and semantics… is crucial to deliver acceptable advertisements” | AI-ish | `crucial`; sentence also missing a subject. | “Need meaning, not only keywords.” |
| 23 | system_design.tex:183 | “Despite the merits and robustness of this agentic system, its needless to say” | AI-ish | `robustness` + “needless to say” + “agentic”. | “Limits of the deployed stack.” |
| 24 | models.tex:6 | “which estimands enter each analysis family” | jargon | First `estimand` has no one-clause gloss. | “which person-level quantity each family tests”. |
| 25 | models.tex:85 | “A crucial part of both the experimental methodology and the system design” | AI-ish | Throat-clearing before \(\lambda\). | Start at “This study manipulates only presentation.” |
| 26 | models.tex:88 | “for the rest of the sessionmonly cue that a passage is sponsored” | AI-ish | Garbled join; reader must reconstruct the sentence. | “session. The only cue that a passage is sponsored”. |
| 27 | models.tex:237 | “exploratory families additionally carry a false-discovery-rate \(q\)” | nomenclature | BH leftover; “reason set out after that table” never appears. | Drop FDR \(q\), or define it and use it. |
| 28 | models.tex:290 | “Specified and not estimated in this draft.” | WIP | Draft language on the Methods page. | “Specified; not analysed.” |
| 29 | models.tex:309 | “A participant-clustered logistic GEE adjusting for task” | jargon | `GEE` never expanded. | “generalised estimating equation (clustered logistic)”. |
| 30 | results.tex:104 | “frozen Gold table confirmatory_planned_D.csv (8 September freeze)” | WIP | Repo path and freeze date in the PDF. | Drop; the table is the source. |
| 31 | results.tex:115 | “Paired \(t\) on \(D_i\); Holm within outcome. Wilcoxon \(p\) is raw. LMM Holm \(p\)…” | length | Caption longer than two lines. | One line: paired \(t\), Holm within outcome. |
| 32 | results.tex:149 | “Eight of sixteen survive Holm. Manipulation and notice rise…” | results/discussion boundary | Table already holds every cell; prose restates the board. | One claim: which two outcomes move. |
| 33 | results.tex:178 | “21 of 54 (39%)… 22 of 54 (41%)… 57% and 59%… 87% and 81%” | results/discussion boundary | Figure + App E table already carry the shares. | Keep the one cell the figure cannot show. |
| 34 | results.tex:199 | “Nearest cell extraversion on credibility early minus late, Holm \(p=.18\)” | direction | Contrast named; which way extraversion goes is omitted. | “Higher extraversion, larger credibility drop, Holm \(p=.18\).” |
| 35 | results.tex:204 | “Sex, education, chatbot familiarity, use frequency, and environment each entered…” | length | One paragraph dumps \(n\), two codings, and 140 tests. | Split: design one sentence; 0/70 one sentence. |
| 36 | results.tex:216 | “Dataset A is condition aggregation… Dataset B is onset-locked” | redundancy | Third full two-estimand lecture (see #18). | One cross-ref to Ch 4. |
| 37 | results.tex:245 | “the only Holm cell is early minus late on posterior \(\alpha\) (\(-0.22\) dB” | direction | Sign in the number; words never say early is lower. | “Posterior \(\alpha\) is lower early than late.” |
| 38 | results.tex:257 | “Absolute \(\alpha\) and \(\beta\), FAA, both Pope ratios, and the Kislov ratio” | jargon | `FAA` unexplained on the Results page. | “frontal alpha asymmetry (FAA)”. |
| 39 | results.tex:260 | “Fz \(\theta\), implicit early minus explicit late (\(-0.28\) dB” | direction | Pair named; which cell is lower only in the sign. | “Fz \(\theta\) is lower for implicit early than explicit late.” |
| 40 | results.tex:301 | “Two contexts can be fed to \(f_{\mathrm{genre}}\)… Definition 6 is written here…” | length | Opener is one notation dump; >45 words twice. | Two short sentences; leave aliases to Ch 3. |
| 41 | results.tex:316 | “Whole-conversation scores do not differ by condition.” | titles | Full-sentence finding, not a noun phrase. | “Whole-conversation scores by condition.” |
| 42 | results.tex:317 | “the participant ICC on the three scores is 0.043 to 0.111” | jargon | `ICC` never expanded; also a \(p\)-parade after the claim. | “participant intra-class correlation”; drop the extra \(p\)s. |
| 43 | results.tex:317 | “so it has little room left… The confirmatory estimand is therefore” | results/discussion boundary | Interprets why the family was chosen; that is Discussion. | Report the Kruskal–Wallis; point at \(\delta^{(a)}_2\). |
| 44 | results.tex:334 | “Later messages are shorter and more often labelled fallback.” | titles | Twitter finding-title. | “Turn length and fallback labels.” |
| 45 | results.tex:356 | “the turn coefficient is \(\beta=0.43\)… \(\beta=0.34\)… \(\beta=-0.29\)” | results/discussion boundary | Table already has the shares; three \(\beta\)s add a second parade. | One sentence: turn still predicts fallback after length. |
| 46 | results.tex:453 | “pooled \(\delta^{(a)}_2\) contrast is \(-0.019\), 95% CI \([-0.137, 0.100]\), Holm \(p=1.00\)” | results/discussion boundary | App F tables hold these cells; prose reprints the CI. | “Deployed context: same null; shifts far less often.” |
| 47 | results.tex:460 | “This section showcases the relationships… and the grain they are computed on” | AI-ish | `showcases`; `grain` still unexplained here. | “Associations are person-level difference scores.” |
| 48 | results.tex:500 | “Two survive: posterior \(\alpha\)… whole-scalp \(\alpha\) (\(\rho=.69\), \([.27,.89]\” | results/discussion boundary | Figure already shows the sixteen; CI parade repeats it. | Name the two survivors; leave numbers on the figure. |
| 49 | discussion.tex:25 | “Notice as a manipulation check” | titles | Missing period; reads as a slogan, not a noun phrase. | “Notice as a delivery check.” |
| 50 | discussion.tex:32 | “It rises with any advertisement, more under explicit than implicit” | AI-ish | Caveman pronoun; title carries the noun. | “Perceived manipulation rises with any advertisement…” |
| 51 | discussion.tex:36 | “the any-ad difference is a third of a point with an interval that reaches zero… ICC .39” | results/discussion boundary | Re-serves the Ch 7 interval and adds ICC. | Keep the trust-held claim; drop the CI and ICC. |
| 52 | discussion.tex:79 | “An earlier pass over these factors on the same data read uncorrected \(p\)-values” | length | Reconciliation blob; 14 of 18, two people, two codings. | One sentence: uncorrected sparse-level hits did not replicate. |
| 53 | discussion.tex:88 | “the response depends on how and when the advertisement enters” | nomenclature | Forbidden fusion, even as a denial. | “They are two questions, not one combined claim.” |
| 54 | discussion.tex:96 | “writing minus reading raises Fz \(\theta\) by \(0.60\) dB on the same pipeline” | results/discussion boundary | Re-reports the Ch 7 control CI/mean. | “Writing raises Fz \(\theta\); cite the table, no dB.” |
| 55 | discussion.tex:109 | “absolute \(\delta\) rises by \(4.60\) dB… smallest Holm \(p\) being .08” | results/discussion boundary | Long blob; reprints the tilt size and a Holm \(p\). | Finding first; one caveat; no dB, no .08. |
| 56 | discussion.tex:131 | “A Holm-null is not a verdict on the theory.” | titles | Banned slogan register (`pipeline is not dead` kin). | “Instrument failure, not a theory test.” |
| 57 | discussion.tex:139 | “The two contexts fail in opposite directions.” | titles | Full-sentence slogan. | “Bare versus deployed contexts.” |
| 58 | discussion.tex:140 | “Saturation and floor are not a spectrum” | jargon | `saturation` / `floor` used as if already taught. | “Too many shifts versus almost none.” |
| 59 | discussion.tex:147 | “Advertised genres overlap the conversation genres.” | titles | Finding-as-title. | “Overlap of advertised and conversation genres.” |
| 60 | discussion.tex:151 | “The classifier is not silent; it is reading something else.” | AI-ish | Staccato fragment pair. | “The classifier tracks turn depth, not the advertisement.” |
| 61 | discussion.tex:168 | “Against the condition-aggregated score the correlation is \(\rho=.24\)… \(\rho=.80\)” | results/discussion boundary | Re-reports both \(\rho\) and Holm \(p\) from 7.6. | “Found at onset, not under condition aggregation.” |
| 62 | discussion.tex:177 | “not .80 but the lower bound of its interval, .48” | results/discussion boundary | Third pass on the same interval. | Interpret the bound; do not reprint it. |
| 63 | discussion.tex:209 | “Triangles give direction and \(|d_z|\) band (\(|\rho|\) for associations); filled orange…” | length | Caption exceeds two lines. | “Direction and size; filled = Holm \(p<.05\).” |
| 64 | discussion.tex:224 | “Where the neurophysiological record has something to say about presentation, it says it” | AI-ish | WALTER: “too AI-ish”; still a slogan opener. | “The format effect, if any, is at onset.” |
| 65 | discussion.tex:281 | “The finished behavioural sample of fifty-four participants is modest…” | length | One limitations paragraph stacks sample, tasks, clicks, age, \(\theta\). | Split sample from design confounds. |
| 66 | conclusion.tex:23 | “perceived manipulation rose by \(+1.27\) points… early banner (\(-0.69\))” | results/discussion boundary | Jacket re-serves Ch 7 cells. | Direction in words; no \(+1.27\) / \(-0.69\). |
| 67 | conclusion.tex:27 | “Who the user is.” | titles | Question, not a noun phrase. | “Personality and background.” |
| 68 | conclusion.tex:32 | “Averaged over whole condition windows (Dataset A, condition aggregation)” | redundancy | Fourth two-estimand lecture (see #18). | One clause; cross-ref Methods. |
| 69 | conclusion.tex:43 | “(\(\rho=.80\), 95% CI \([.48,.93]\)); … \(\rho=.24\)” | results/discussion boundary | Same pair’s CI again. | “The onset pair survives; the aggregated pair does not.” |
| 70 | appendix_c.tex:115 | “explicit insertions were tagged “Promotional Card”” | nomenclature | Thesis name for the unit is `banner`, not `card`. | “tagged Promotional Card in the UI (the banner)”. |
| 71 | appendix_e.tex:96 | “Robustness to item choice” | AI-ish | Banned `robustness` as a section title. | “Sensitivity to item choice.” |
| 72 | appendix_f.tex:60 | “The bare reading is close to saturation… contextual reading is close to the floor” | jargon | First use of saturation/floor; no one-clause gloss. | “Bare: almost always shifts. Deployed: almost never.” |

Unfulfilled `% WALTER:` still visible in the prose below the comment:
- `discussion.tex:223` (“too AI-ish”) → #64 still slogan.
- `models.tex:237` (FDR \(q\) “after that table”) → no such reason exists; #27.
- `discussion.tex:20` (composites → outcomes) → live Discussion now says “outcomes”; request met.
- `results.tex:361` (late-utterance said “MANY times”) → still #17 across chapters; inside 7.5 it is once.

## Chapter-by-chapter verdict
- Abstract: reads well — user-centric, directions in words; one long sentence only.
- Introduction: needs a rewrite — company-policy close, `landscape`, revenue blob, typos.
- Related work: needs a rewrite — stock openers, then the informal “landspace” closer.
- Theory: needs a pass — one company-ethics run-on; definitions otherwise fine.
- Dataset: needs a rewrite — broken “pipeliene c”, live “still being frozen”, 4.2.2 stub vs finished Gold.
- System design: needs a pass — `crucial` / `leverage` / `robustness`; engineering facts are usable.
- Methods: needs a pass — “sessionmonly”, “this draft”, undefined GEE, leftover FDR \(q\).
- Results: needs a pass — slogan titles, Gold filename, number parades, two-estimand reteach.
- Discussion: needs a pass — slogan titles, “how and when”, CI reprints, one onset blob, AI-ish 8.6.
- Conclusion: needs a pass — voice is right; still reprints Ch 7 cells and reteaches Dataset A/B.
- Appendix A: reads well — prompts, not thesis voice.
- Appendix B: reads well — formula plus boxes.
- Appendix C: needs a pass — “Promotional Card” as the explicit name.
- Appendix D: reads well — technical; `robust` here is an estimator, not filler.
- Appendix E: needs a pass — “Robustness” title; dense but tables do the work.
- Appendix F: needs a pass — saturation/floor unexplained; otherwise the right appendix.
