# WP-E — figure and table caption audit

Scope: all 73 active captions in `chapters/*.tex` and
`figures/results/tab_*.tex`. This includes the optional short caption on the
retrieval pipeline and excludes the commented pseudocode caption in
`dataset.tex:566`. Every figure was opened from its PNG preview or rendered
from the PDF. `introduction.tex`, `related_works.tex`, `conclusion.tex`, and
Appendices A--B contain no active captions.

| file:line | label | current caption (truncated) | verdict | proposed caption | reason |
|---|---|---|---|---|---|
| `chapters/theory.tex:284` | `tab:ad-taxonomy` | Two-level morphological taxonomy of a conversational advertisement instance… | de-duplicate | Morphological taxonomy of the conversational advertisement instance \(a_k\). | Equation and layers already precede the table. |
| `chapters/system_design.tex:77` | `fig:qwen-arch` | High-level Qwen 3.6 35B-A3B architecture overview. | de-duplicate | Qwen 3.6 35B-A3B block architecture. | Repeats the body and in-image title. |
| `chapters/system_design.tex:129` | `fig:retrieval-pipeline` | Online ad-retrieval pipeline executed on an advertised turn divided in a 3 stage funnel. | shorten | Three-stage retrieval funnel on an advertised turn. | Stages are labelled inside the diagram. |
| `chapters/system_design.tex:175` | `fig:system-architecture` | Multi-Node System architecture overview. | de-duplicate | Physical and network architecture of the laboratory and crowdsourced deployments. | Current text repeats the in-image title. |
| `chapters/models.tex:99` | `fig:ad-implicit-example` | Implicit (\(a^{\mathrm{imp}}\)). | keep | keep | Concise identifier for the screenshot. |
| `chapters/models.tex:105` | `fig:ad-explicit-example` | Explicit (\(a^{\mathrm{exp}}\)). | keep | keep | Concise identifier for the screenshot. |
| `chapters/models.tex:108` | `fig:ad-presentation-examples` | Advertisement presentation formats ($\lambda\in\{\mathrm{implicit},\mathrm{explicit}\}$) used… | keep | keep | Short and distinguishes the experimental manipulation. |
| `chapters/models.tex:187` | `fig:lab-flow` | Laboratory participant flow. Five within-participant conditions in random order… | shorten | Laboratory participant flow, including EEG setup and cued recall after the five-condition loop. | Diagram and body already enumerate every condition. |
| `chapters/models.tex:194` | `fig:crowd-flow` | Crowd participant flow. Same five conditions as the laboratory arm. Baseline is replaced… | shorten | Crowd participant flow, adding Prolific identification and close-out validation; no EEG. | Removes details already labelled in the diagram. |
| `chapters/models.tex:268` | `tab:analysis-families` | Analysis families, each with its estimator and its correction family… | de-duplicate | Analysis families, estimators, and correction families. | Preceding sentence states the same description. |
| `chapters/dataset.tex:19` | `tab:catalog_statistics` | Summary statistics of the preprocessed Amazon Products 2023 catalogue. | keep | keep | Accurate, short, and not interpretive. |
| `chapters/dataset.tex:61` | `tab:amazon_categories` | Distribution of products across Amazon categories. | keep | keep | Accurate and minimal. |
| `chapters/dataset.tex:116` | `fig:data-pipeline` | Offline data transformation pipeline used to clean, normalize, embed, and index… | de-duplicate | Offline product-catalogue transformation into the FAISS index. | Stage labels already name every operation. |
| `chapters/dataset.tex:215` | `fig:gold-tables` | Gold tables by stream and grain. Numbers are rows per arm; grey cells are empty… | add-legend-clause | Gold tables by stream and grain. Blue: laboratory; red: crowd; purple: joined; grey: empty by design. EEG is laboratory-only. | Preserves colour mapping after legend removal. |
| `chapters/dataset.tex:260` | `tab:beh-gold` | Gold behavioural views. Laboratory rows are the ones in which EEG is filled. | keep | keep | Short and explains the laboratory join rows. |
| `chapters/dataset.tex:289` | `fig:trajectory-preprocessing` | Trajectory preprocessing pipeline summarized. | de-duplicate | Trajectory preprocessing from tracked session logs to turn- and conversation-grain Gold tables. | Replaces a redundant title with the output. |
| `chapters/dataset.tex:322` | `tab:trajectory-examples` | First five rows of the Gold tables, primary \texttt{utterance} source… | shorten | Example rows from the four trajectory Gold tables under the primary bare-utterance context. | Each displayed block contains fewer than five rows. |
| `chapters/dataset.tex:380` | `tab:eeg-gold` | Final golden zone EEG tables with different grains. | shorten | Gold EEG tables for condition aggregation and onset-locked responses (\(n=18\)). | Replaces vague wording and banned path names. |
| `chapters/dataset.tex:395` | `fig:eeg-preprocessing` | The four stage laboratory EEG pipeline from ingestion to analysis. | de-duplicate | EEG lineage from raw recording and event log to condition-aggregation and onset-locked Gold tables. | In-image title already identifies the pipeline. |
| `chapters/dataset.tex:410` | `fig:eeg-montage` | 32-channel actiCHamp 10--20 layout. Red: confirmatory Fz \(\theta\). Blue… | de-duplicate | 32-channel actiCHamp 10--20 layout. Red: Fz \(\theta\); blue: posterior \(\alpha\); yellow: other recorded channels. | Ground and reference are stated immediately before. |
| `chapters/dataset.tex:531` | `tab:eeg-gold-examples` | Gold EEG rows for one laboratory participant for visualization purposes… | shorten | Example Gold EEG rows for one laboratory participant; two of sixteen spectral measures are shown. | Removes filler while retaining the display limitation. |
| `chapters/results.tex:20` | `fig:sample-demo` | Finished-sample demographics from the post-experiment questionnaire. Bars are the percentage… | add-legend-clause | Finished-sample sex, education, chatbot familiarity, and use frequency. Blue: laboratory (\(n=18\)); red: crowd (\(n=36\)). | Preserves arm mapping after legend removal. |
| `chapters/results.tex:32` | `tab:bfi10-descriptives` | Big Five scores from the BFI-10 in the finished sample. Each trait is the mean… | shorten | BFI-10 trait scores in the finished sample (\(N=54\)). \(n_1\) and \(n_5\) count scale endpoints; \(p_{\mathrm{Holm}}\) adjusts the five arm comparisons. | Current caption exceeds two printed lines. |
| `chapters/results.tex:101` | `fig:beh-profiles` | Post-condition outcomes by condition (\(N=54\)). | keep | keep | Minimal identification; prose supplies the pattern. |
| `chapters/results.tex:119` | `tab:beh-planned` | Planned behavioural contrasts (\(N=54\)). Paired \(t\) on \(D_i\); Holm within… | de-duplicate | Planned behavioural contrasts (\(N=54\)). Holm-adjusted paired \(t\); Wilcoxon \(p\) is raw; LMM is the adjusted check. Bold rows survive Holm. | Removes repetition while preserving estimator distinctions. |
| `chapters/results.tex:161` | `fig:beh-localisation` | Each advertisement condition minus \(a^{\emptyset}\) (\(N=54\)). Asterisk: Holm… | keep | keep | Short, post-hoc status and marker are explicit. |
| `chapters/results.tex:185` | `fig:beh-notice-percentages` | Percentage of participants who noticed, by condition (\(N=54\)). Whiskers: Wilson… | add-legend-clause | Sponsored-item notice by condition (\(N=54\)). Segments: noticed, midpoint, and not noticed; whiskers: Wilson 95\% interval for noticed. | Legend removal otherwise loses segment meanings. |
| `chapters/results.tex:209` | `fig:beh-personality` | Trait \(\times\) contrast slope on \(D_i\) per BFI point (\(N=54\)). Left… | add-legend-clause | BFI-10 moderation of format and timing (\(N=54\)). Cells give slope per BFI point and Holm \(p\); shade groups \(p\)-value ranges. | Preserves shading semantics without restating the null. |
| `chapters/results.tex:223` | `fig:beh-demographics` | Demographic moderation of the planned contrasts (\(N=54\)): spread of \(\overline{D}\)… | add-legend-clause | Demographic moderation of planned contrasts (\(N=54\)). Cells give contrast spread and joint-test Holm \(p\); shade groups \(p\)-value ranges. | Preserves shading semantics after legend removal. |
| `chapters/results.tex:243` | `tab:eeg-task-state` | Writing minus reading (\(n=18\)). Holm on the two confirmatory \(t\) tests. Bold rows… | keep | keep | Concise and defines correction and bolding. |
| `chapters/results.tex:261` | `fig:eeg-forests` | Confirmatory EEG contrasts at 4~s (\(n=18\)). Left: Dataset~A. Right: Dataset~B… | fix-colour | Confirmatory EEG contrasts at 4~s (\(n=18\)): condition aggregation (left) and onset-locked (right). Blue: Fz \(\theta\); red: posterior \(\alpha\). Asterisk: Holm \(p<.05\). | Navy, teal, and Dataset A/B will be stale. |
| `chapters/results.tex:273` | `fig:eeg-holm-board` | Holm \(p\) within each measure (\(n=18\)). Rows above the line are confirmatory… | add-Holm-clause | Holm \(p\) within each EEG measure at 4~s (\(n=18\)). Rows above the rule are confirmatory. Asterisk: Holm \(p<.05\). | Board is gaining asterisks; orange wording will stale. |
| `chapters/results.tex:329` | `fig:traj-examples` | Six observed genre trajectories \(\hat{\mathbf{G}}\) under the bare-utterance context… | fix-colour | Observed trajectories under the bare-utterance context. Filled boxes mark genre shifts; vertical rules mark advertisement insertion. | Removes stale orange and duplicates fewer labels. |
| `chapters/results.tex:348` | `fig:traj-position` | Share of transitions with \(\delta_k=1\) by position relative to the advertisement… | keep | keep | Accurate; varying transition counts are printed above bars. |
| `chapters/results.tex:361` | `tab:traj-turn-length` | Bare-utterance context, \(N=54\) participants, 270 utterances per turn. Fallback is… | de-duplicate | Turn-wise message length and fallback-label share under the bare-utterance context (\(N=54\); 270 utterances per turn). | Preceding sentence already defines both fallback classes. |
| `chapters/results.tex:393` | `tab:traj-crossing` | Ad-associated shift \(\delta^{(a)}_2\) against \(a^{\emptyset}\) (\(N=54\)… | shorten | Ad-associated turn-2 shifts under the bare-utterance context (\(N=54\)). Holm-adjusted paired \(t\); McNemar for the two-condition rows. | Keeps estimators without repeating every row contrast. |
| `chapters/results.tex:419` | `tab:traj-aligned-counts` | Outcomes on \(\tau_2\) in the 108 early-advertisement conversations… | de-duplicate | Turn-2 outcomes in the 108 early-advertisement conversations under the bare-utterance context. | Formula and alignment definition immediately precede it. |
| `chapters/results.tex:443` | `tab:traj-late` | Late advertisements against \(a^{\emptyset}\) on \(N_{\mathrm{shift}}\), paired within… | shorten | Late advertisements versus \(a^{\emptyset}\) on \(N_{\mathrm{shift}}\) (\(N=54\), bare-utterance context). Holm-adjusted paired \(t\); Wilcoxon \(p\) is raw. | Shortens while retaining raw-Wilcoxon status. |
| `chapters/results.tex:463` | `fig:traj-depth` | Change in genre share, turn~1 to turn~4 (\(N=54\)). Holm across six… | add-Holm-clause | Change in genre share from turn~1 to turn~4 (\(N=54\)). Hollow markers are fallback classes. Asterisk: Holm \(p<.05\) across six genres. | Forest needs the standard Holm marker clause. |
| `chapters/results.tex:489` | `fig:combos-declared` | Declared association families, Spearman \(\rho\) with 95\% intervals. (a) Behaviour… | add-legend-clause | Spearman \(\rho\) with 95\% intervals. (a) Circles/squares: condition aggregation/onset-lock (\(n=18\)). (b) Circles/diamonds: behaviour--trajectory (\(N=54\))/trajectory--EEG (\(n=18\)). Asterisk: Holm \(p<.05\). | Shapes, samples, and Holm marker otherwise disappear. |
| `chapters/results.tex:514` | `fig:combos-trust-alpha` | Surviving pair. (a) Trust \(D_i\) against onset-locked posterior \(\alpha\)… | add-legend-clause | Trust--EEG associations (\(n=18\)). In panel (b), circles show condition aggregation and squares onset-lock. Asterisk: Holm \(p<.05\). | Removes slogan and preserves marker mapping. |
| `chapters/results.tex:567` | `tab:results-summary` | Every analysis family of \autoref{tab:analysis-families}, in the same order… Bold rows… | de-duplicate | Declared analysis families in Methods order. ``Sig.'' counts Holm-surviving tests; ``Key estimate'' gives one representative contrast. Bold rows survive Holm. | Preceding sentence already explains table coverage. |
| `chapters/results.tex:605` | `tab:results-checks` | Sensitivity and exploratory checks that are not families in \autoref{tab:analysis-families}… | keep | keep | Short and distinguishes checks from declared families. |
| `chapters/discussion.tex:209` | `fig:effects-matrix` | Planned contrasts, condition-versus-no-advertisement marginals, and declared associations… | fix-colour | Planned contrasts, condition marginals, and declared associations. Triangles encode direction and \(|d_z|\) (\(|\rho|\) for associations); dots are unestimated. Asterisk: Holm \(p<.05\). | Current caption is long and orange will stale. |
| `chapters/discussion.tex:249` | `tab:rq-answers` | Answers to the nine research questions of \autoref{sec:intro:research-questions}… | shorten | Answers to the nine research questions of \autoref{sec:intro:research-questions}. ``Not supported'' means no Holm-surviving cell; ``partly'' means only one named factor survives. | Definitions are retained within two printed lines. |
| `chapters/appendix_c.tex:49` | `tab:post-condition-eval` | Post-condition Section~1 (Evaluation). R: reversed (\(8-x\)) into credibility… | keep | keep | Necessary reversal key; short and accurate. |
| `chapters/appendix_c.tex:77` | `tab:post-condition-personality` | Post-condition Section~2. Direct trust is item~16; notice is items~19--20. | keep | keep | Concise scoring map not visible in headers. |
| `chapters/appendix_c.tex:95` | `tab:post-condition-behaviour` | Post-condition Section~3. Perceived manipulation is the mean of the two items. | keep | keep | Concise scoring information. |
| `chapters/appendix_c.tex:122` | `tab:recall-items` | Cued-recall items, once per advertisement condition. | keep | keep | Minimal and accurate. |
| `chapters/appendix_c.tex:153` | `tab:bfi10-items` | BFI-10 items \cite{rammstedt2007bfi10}. R: reversed. E extraversion… | keep | keep | Abbreviation key is necessary and compact. |
| `chapters/appendix_c.tex:183` | `tab:demographics-items` | Demographic items. Options in screen order. | keep | keep | Minimal and accurate. |
| `chapters/appendix_d.tex:29` | `tab:eeg-width` | Dataset~B confirmatory cells that reach Holm \(p<.05\) off 4~s… Bold rows… | shorten | Onset-locked cells with Holm \(p<.05\) outside the pre-specified 4~s width; sensitivity only. Bold rows survive Holm. | Uses the estimand name and removes repetition. |
| `chapters/appendix_d.tex:91` | `fig:app-posthoc-board` | Holm \(p\) for the 256 post-hoc pairs. One Dataset~A cell is below… | add-Holm-clause | Holm \(p\) across 256 post-hoc EEG pairs (\(n=18\)): condition aggregation (left) and onset-locked (right). Asterisk: Holm \(p<.05\). | Removes banned path name and supports new marker. |
| `chapters/appendix_d.tex:98` | `tab:app-posthoc-near` | Post-hoc pairs with raw \(p<.05\) (8 of 256). Bold rows survive Holm. | keep | keep | Short and distinguishes raw screening from Holm bold. |
| `chapters/appendix_e.tex:21` | `tab:beh-descriptives` | Outcomes by condition, \(M\) (SD), \(N=54\). Bold: lowest trust and highest… | shorten | Behavioural outcomes by condition (\(N=54\)); values are \(M\) (SD). | Bold description is incomplete and may be removed. |
| `chapters/appendix_e.tex:47` | `fig:beh-likert` | Item distributions behind the four primary outcomes (\(N=54\)). (R) reversed. | add-legend-clause | Item distributions behind the four primary outcomes (\(N=54\)). Segments run from response 1 to 7 left to right; (R) marks reversed items. | Legend removal otherwise loses response ordering. |
| `chapters/appendix_e.tex:62` | `fig:beh-holm-board` | Planned \(\overline{D}\) and Holm \(p\) (\(N=54\)). Orange: Holm \(p<.05\)… | add-Holm-clause | Planned behavioural contrasts (\(N=54\)). Cells give \(\overline{D}\) and Holm \(p\); secondary-quality rows are exploratory. Asterisk: Holm \(p<.05\). | Replaces stale orange with the standard marker. |
| `chapters/appendix_e.tex:76` | `tab:beh-alpha` | Cronbach \(\alpha\) on 270 condition rows. Trust is a single item. | keep | keep | Correct unit and single-item exception are explicit. |
| `chapters/appendix_e.tex:106` | `tab:beh-item-diag` | Item diagnostics after the single reversal. Bold: items queried on the raw scores. | keep | keep | Bold meaning is not recoverable from headers. |
| `chapters/appendix_e.tex:141` | `tab:beh-item-loo` | Leave-one-item-out \(\overline{D}\) (Holm \(p\)). Bold cells: Holm p<.05. | shorten | Leave-one-item-out \(\overline{D}\) with Holm \(p\). Bold cells survive Holm. | Restores mathematical formatting and shortens the key. |
| `chapters/appendix_e.tex:173` | `fig:beh-item-forest` | Item-level planned contrasts (\(N=54\)). Orange: Holm \(p<.05\) within item. | fix-colour | Item-level planned contrasts (\(N=54\)). Asterisk: Holm \(p<.05\) within item. | Orange wording will stale after recolouring. |
| `chapters/appendix_e.tex:183` | `tab:beh-localisation` | Each ad condition against \(a^{\emptyset}\) (\(N=54\)). Holm within outcome… | shorten | Each advertisement condition versus \(a^{\emptyset}\) (\(N=54\)). Holm-adjusted paired \(t\); Wilcoxon \(p\) is raw. Bold rows survive Holm. | States both estimators and uses thesis terminology. |
| `chapters/appendix_e.tex:217` | `tab:beh-friedman` | Friedman \(\chi^2_4\) over the five conditions (\(N=54\)). Post hoc; \(p\) raw. | keep | keep | Concise and identifies raw post-hoc test. |
| `chapters/appendix_e.tex:239` | `tab:beh-pairwise` | Pairwise sweep, pairs with Holm \(p<.10\) (\(N=54\)). Holm within outcome… | shorten | Post-hoc pairwise sweep: rows with Holm \(p<.10\) (\(N=54\)). Holm-adjusted paired \(t\); Wilcoxon \(p\) is raw. Bold rows survive Holm. | Clarifies screening, estimator, and raw sensitivity. |
| `chapters/appendix_e.tex:279` | `tab:beh-personality` | Personality family (\(N=54\)). Slope is Likert points on \(D_i\) per BFI point… | de-duplicate | BFI-10 moderation slopes on \(D_i\) per trait point (\(N=54\)); Holm within outcome across fifteen terms. | Body already reports that no cell survives. |
| `chapters/appendix_e.tex:367` | `fig:beh-estimators` | Sixteen planned contrasts under paired \(t\), LMM, and raw Wilcoxon… | add-legend-clause | Sixteen planned contrasts (\(N=54\)). Circles: paired-\(t\) Holm \(p\); squares: LMM Holm \(p\); triangles: raw Wilcoxon \(p\). Values below \(10^{-6}\) are plotted at 6. | Preserves estimator shapes after legend removal. |
| `figures/results/tab_beh_notice_percentages.tex:4` | `tab:beh-notice-percentages` | Participants rating each item \(\geq 5\) of 7, by condition (\(N=54\); Wilson… | shorten | Participants rating each item at least 5 of 7, by condition (\(N=54\)); counts and percentages. | Removes provenance and cross-reference from caption. |
| `figures/results/tab_beh_demographics.tex:4` | `tab:beh-demographics` | Demographic moderation of the planned contrasts (cohort \(N=54\); sex \(n=51\)… | shorten | Demographic moderation of planned contrasts: joint Wald tests with Holm within outcome. Cohort \(N=54\); sex \(n=51\), education \(n=49\). Two-level and OLS columns are checks. | Current caption exceeds two printed lines. |
| `chapters/appendix_f.tex:15` | `tab:app-traj-measures` | Trajectory measures by condition, bare-utterance context (\(N=54\), 270 conversations)… | keep | keep | Compact sample, context, and scale information. |
| `chapters/appendix_f.tex:34` | `tab:app-traj-variance` | Kruskal--Wallis on 270 conversations. Not a test of \(\delta^{(a)}\)… | keep | keep | Correct unit and inferential boundary are essential. |
| `chapters/appendix_f.tex:64` | `tab:app-traj-sources` | Two readings of Definition~1 on the same 1{,}080 utterances. Last block… | shorten | Bare-utterance and deployed-window readings on 1{,}080 utterances, with genre-aligned outcomes for 108 early-advertisement conversations. | Replaces informal “chats” and opaque block reference. |
| `chapters/appendix_f.tex:91` | `fig:app-traj-heatmap` | Transition counts \(N_{ij}\) under both readings of Definition~1 (810 steps)… | de-duplicate | Row-normalised transition shares for the bare utterance and deployed window (810 steps each). | Cells show shares, not raw counts. |
| `chapters/appendix_f.tex:104` | `tab:app-traj-sweep` | Context-window sweep. \(\delta^{(a)}_2\) is early ads pooled against… | shorten | Context-window sensitivity for early advertisements pooled versus \(a^{\emptyset}\) (\(N=54\)). Holm across six windows; ``Sticky'' is the share with \(N_{\mathrm{shift}}=0\). | Uses formal terminology and retains the column key. |

## Problems in the figures themselves

- `fig:qwen-arch`: visible “Sebastian Raschka” watermark; raster text also
  contains an unmatched quotation mark in the gated-attention heading.
- `fig:data-pipeline`, `fig:retrieval-pipeline`,
  `fig:trajectory-preprocessing`, `fig:eeg-preprocessing`,
  `fig:system-architecture`, and `fig:qwen-arch`: in-image titles duplicate
  the captions.
- `fig:sample-demo`, `fig:beh-notice-percentages`, `fig:beh-personality`,
  `fig:beh-demographics`, `fig:combos-declared`,
  `fig:combos-trust-alpha`, `fig:beh-likert`, `fig:beh-holm-board`,
  `fig:beh-item-forest`, `fig:beh-estimators`, `fig:effects-matrix`,
  `fig:gold-tables`, and `fig:beh-localisation`: in-plot legends remain in
  the inspected versions.
- `fig:beh-demographics`: “Cued memory” collides with the italic “not
  defined” note; the bottom explanatory line is too small and duplicates the
  proposed caption.
- `fig:beh-localisation`: the in-image title renders
  \(a^{\emptyset}\) as malformed “a∅” and duplicates the caption.
- `fig:eeg-holm-board`, `fig:beh-holm-board`, `fig:effects-matrix`,
  `fig:traj-depth`, `fig:combos-declared`, `fig:combos-trust-alpha`, and
  `fig:app-posthoc-board`: Holm-significant cells/estimates do not yet use
  the standard orange asterisk.
- `fig:eeg-forests`, `fig:eeg-holm-board`, `fig:combos-trust-alpha`,
  `fig:app-posthoc-board`, and `fig:eeg-preprocessing`: the image itself
  still prints Dataset A/B; use “condition aggregation” and “onset-locked”.
- `fig:app-traj-heatmap`: the right panel says “Contextual”; use “Deployed
  window”. Its overall title duplicates the caption.
- `fig:effects-matrix`: the legend and dense four-line footnote are too small
  at thesis width; move only indispensable decoding to the caption.
- `fig:gold-tables`: the bottom key is illegible at thesis width and
  duplicates information already encoded in the grid.

## Counts

- Total captions: **73**
- Keep: **23**
- Change: **50**
