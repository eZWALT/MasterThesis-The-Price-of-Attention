# WP-D — Statistical framework hardening + propagation (12 Sep 2026)

Files touched: `docs/overleaf/thesis/chapters/models.tex` (Methods),
`docs/overleaf/thesis/chapters/results.tex` (one row label). No analysis,
no commit, no push.

## 1. What changed, paragraph by paragraph

1. `Conversational outcomes` stub → two short paragraphs: genre trajectory from Definitions 1–6 on the bare utterance, deployed context as sensitivity; free text collected and not analysed.
2. `EEG measures` stub → two short paragraphs: sixteen measures per 4 s epoch with the decibel gloss; confirmatory pair Fz theta and posterior alpha with channels and direction; other fourteen exploratory; both tables named as two estimands.
3. Conventions, **Sample** bullet: adds "runs on those eighteen participants" so the EEG \(n\) is answered in place.
4. Conventions, **Status** bullet: "everything else is labelled exploratory" → "carries one of the labels set out below" (post hoc statement itself untouched, stays once).
5. Conventions, **Threshold** bullet: false-discovery-rate \(q\) clause and the dangling "reason set out after that table" removed; now "Holm is the only correction used", nonparametric \(p\) raw.
6. New paragraph after the bullets: the four labels — confirmatory, exploratory, post hoc, sensitivity — one sentence each.
7. New paragraph after the one-sample \(t\): why a paired \(t\) on Likert outcomes, with Wilcoxon as sensitivity and the random-intercept mixed model as adjusted check; the "not a Holm \(p\)" sentence moved here.
8. \(t\) paragraph: \(d_z\) glossed in words; Wilcoxon sentences moved out to 7.
9. Table lead-in: Spearman glossed ("monotone covariation … not a mediation claim").
10. `tab:analysis-families`: free-text row estimator → "collected, not analysed", correction → "none", dagger and footnote dropped; "6 genres labelling ≥5%" → "the six genres that carry ≥5% of utterances"; "Personality moderation (demographics as covariates)" → "Personality moderation" (estimator cell still carries the covariates). No \(n\), estimator or family size changed.
11. Post-table paragraph: was "Holm is the correction throughout … The five relative powers share a denominator." (orphan). Now the three-reason justification of Holm, with the relative-power denominator folded in as the reason correction never runs across measures.
12. EEG paragraph split in two: a new opening paragraph states the two estimands and why they are separate; the mechanics paragraph keeps both displayed equations, mentions \(k=37\) once as the equal-\(n\) cell and cites Ch 4 for the number.
13. Post hoc paragraph: Friedman glossed ("a rank-based test of whether the five conditions differ at all").
14. Trajectory paragraph split in two: confirmatory estimand with McNemar and GEE glossed ("a participant-clustered logistic regression (GEE)"); then the three non-confirmatory trajectory tests with the permutation and Kruskal–Wallis glossed, and \(H\), \(R\) named in words.
15. Both displayed equations, `tab:analysis-families`, the six conventions, and every `% WALTER` / `% NUMBERS` / `% To-Do` comment kept.

## 2. The six attacks and where each answer sits

| Attack | Answer | Location |
|---|---|---|
| (a) not pre-registered | "The analysis is post hoc, and the sample size was set by recruitment rather than by an a priori power calculation." Stated once, not repeated. | **Status** bullet |
| (b) why Holm, not BH or Bonferroni | Family-wise control within the declared family; no dependence assumption (planned contrasts on five conditions are correlated by construction); rejects at least as often as Bonferroni at the same level. | paragraph after `tab:analysis-families` |
| (c) why a paired \(t\) on Likert means | \(D_i\) averages items within an outcome and conditions within a participant, so the tested between-participant distribution is approximately continuous; Wilcoxon on the same \(D_i\) is the sensitivity, the random-intercept mixed model the adjusted check. | new paragraph after the one-sample \(t\) |
| (d) why \(n=18\) for EEG | "Only the laboratory arm was recorded, so every family involving EEG is laboratory-only and runs on those eighteen participants." | **Sample** bullet (and the structural-confound bullet in 6.2 already says it) |
| (e) why two EEG estimands | Condition aggregation asks whether the sustained state over a condition differs; the onset-locked contrast asks whether the moment of the advertisement differs; different epochs, corrected separately, one is not evidence about the other. | first EEG paragraph, plus the closing sentence of the `EEG measures` stub |
| (f) why 37 epochs | "\(k=37\) makes that an equal-\(n\) cell, so a short and a long conversation weigh the same", with the number itself fixed in `subsubsec:dataset:eeg-dataset-a`. One mention. | second EEG paragraph |

## 3. Propagation grep

Scope: `chapters/*.tex`, `frontmatter/*.tex`, `figures/results/tab_*.tex`.
Comment lines (`%`) were read and left alone throughout.

| Pattern | Before | After | Note |
|---|---|---|---|
| `false.discovery` (prose) | 1 (`models.tex:238`) | 0 | the removed \(q\) clause |
| `FDR` (prose) | 0 | 0 | remaining hits are `% WALTER+` comments in `results.tex` and `references.bib` entries |
| `Benjamini` | 1 comment | 1 comment | `results.tex:234` is a `% WALTER+` line, untouched |
| `descriptive coding` | 1 | 0 | free-text row |
| `no inferential claim` | 1 | 0 | free-text row |
| `dagger` in `models.tex` | 2 (marker + footnote) | 0 | footnote folded into the row |
| `labelling` / `labelled` as a naming term in Methods | 2 (`:281` table cell, `:310` "labelled \(\hat g_k\)") | 0 | now "carry ≥5% of utterances" and "computed on" |
| `Statistical Framework` (title case, prose) | 0 | 0 | `related_works.tex:30` is OCEAN's "statistical framework", lower case, unrelated |
| `q\)` as a statistic | 0 | 0 | only `dataset.tex` query vector \(\mathbf q\) |
| `writing vs reading` | 1 (`results.tex`, summary row) | 0 | now "writing versus reading", bold preserved |
| `genres that label at least 5\%` | 1 (`results.tex`, 7.5 depth check) | 0 | now "carry at least 5%", matching the Methods correction-family cell |

`tab:results-summary` against `tab:analysis-families`: same families, same
order, same names after the two label fixes above. Two deliberate
differences remain, both additive rather than contradictory:

- `tab:results-summary` carries an extra row, "Fourteen exploratory measures, A and B". That family is declared in Methods prose ("each measure is its own Holm family … the other fourteen are exploratory") rather than as a table row, and the label now matches the Methods word. Numbers untouched.
- The summary row "\(\hat g_1\) vs \(\hat g_4\) (instrument check)" keeps its parenthetical; Methods names the family, Results says what it is for. Trajectory rows drop the "Genre trajectories," prefix because the italic family header above them carries it, exactly as the EEG block does.

## 4. Left alone on purpose

- `theory.tex:41` "due to the labelling effort" — annotation cost, not the bare-utterance/deployed-window sense the rule bans. Out of WP-D scope; flag for WP-A/E if the word is to go thesis-wide.
- `\label{sec:app-traj-labelling}` and its four `\ref`s — a label name, not prose; renaming it is churn with a compile risk and no reader benefit.
- The `% To-Do (Mostly Katerina)`, `% To-Do (improve this with AI lol)`, and `%%%% free text forms belong to here?` comment lines above/below the two rewritten stubs: they are author comments, invisible in the PDF, and the rule is never to delete one. The prose they asked for is now written.
- `tab:analysis-families` numbers, estimators, and family sizes: untouched.
- Appendix D tiering (two confirmatory, four secondary, ten exploratory) was not rewritten; Methods now says "exploratory" for the fourteen and points at the appendix for the finer tiers, which is the usage `tab:results-summary` already prints.
- No compile check was possible: no `pdflatex` / `latexmk` on this machine. Edits are prose plus two table cells; column counts in both edited rows are unchanged.
