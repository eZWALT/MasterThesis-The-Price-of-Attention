# WP9 — Abstract

Date: 12 September 2026. Owner: `claude-opus-5-thinking-high`. Status: **done**.
File edited: `docs/overleaf/thesis/frontmatter/abstract.tex` **only**. Diff
+6 / −24. Walter's one `% WALTER:` line is preserved character for character
(the diff shows it only because the file previously had no final newline and
two stray blank lines above it). Nothing committed, nothing pushed.

Structural checks (no TeX toolchain here): `\(`/`\)` 7/7, braces 2/2, no
`\begin{...}` environment needed — `Dissertate.cls:362` sets `\chapter*{Abstract}`
and `\input`s this file, so the file stays plain paragraphs with no wrapper.
Class is single-spaced (`dnormalspacing` 1.2, `dsingle` default), so 369 words
sits inside one page.

Lint clean for: `TODO`, `textbackslash`, `---`, a bare `+`, `price of attention`,
`how and when`, `serving rule`, `visual processing`, `captured attention`,
`approached significance`, `MDE`, `Holm`, `BH`, `composite`, `card`,
`labelling`, `k=37`. All Greek is `\(\alpha\)` / `\(\rho\)`; all percentages
are gone except "about half".

---

## 1. Final abstract text (verbatim, for Walter)

Advertising is entering conversational assistants, where a provider chooses not only which advertisement to serve, but how it is presented and when it appears in the conversation. This thesis measures what those choices cost the user rather than what they yield the advertiser.

It contributes a theory and an experiment. The theory pairs a taxonomy of advertising interventions with an intent-trajectory formalism that defines annotation-free impact measures on sequences of user intents, instantiated by a genre classifier \(f_{\mathrm{genre}}\). On a purpose-built retrieval-based assistant, \(N=54\) participants completed five four-turn guided tasks, one per condition: a product mention written into the reply, or a labelled sponsored banner, inserted early at turn 2 or late at turn 4, plus an advertisement-free control. \(n=18\) of them were recorded with synchronised 32-channel EEG.

Advertisements were noticed and raised perceived manipulation by 1.27 points on a seven-point scale, more for the banner than for the mention and more for early than late insertions, which also cost a third of a point of credibility. Trust did not differ on any planned contrast after correction, dropping only under the early banner. Banners were remembered better than mentions on cued recall, and about half the participants did not report the mention as sponsored. Presentation and timing did not interact, and neither personality nor background moderated them, across 60 and 140 corrected interaction tests.

Neurophysiologically, no confirmatory marker separates an advertising condition from the advertisement-free control; the one corrected contrast is a lower posterior \(\alpha\) early than late, averaged over whole condition windows. Exploratory measures show a slow-power response within four seconds of an early banner’s onset. The genre trajectories register conversational depth rather than the advertisement, every declared advertisement contrast being null. Locked to the onset, however, the posterior \(\alpha\) response covaries with the change in reported trust across participants (\(\rho=.80\), \(n=18\)), an association the condition-aggregated score does not show.

The theory, the platform, the analysis code and the linked behavioural, conversational and EEG dataset are released. The user-side cost of advertising is real, more modest than feared, concentrated at the moment of insertion and on some users more than others, and measurable: a foundation for assistants that advertise without spending the trust of the people they serve.

**Word count: 369** (five paragraphs: 43 · 84 · 96 · 87 · 59). Roughly 2.5 k
characters, one page at 1.2 spacing.

## 2. Every number, with its source

| Number / claim in the abstract | Source |
|---|---|
| \(N=54\), five conditions, five four-turn guided tasks | `results.tex` §7.1; jacket paragraph of `conclusion.tex` |
| \(n=18\), synchronised 32-channel EEG | `results.tex` §7.1 |
| early = turn 2, late = turn 4; mention vs labelled banner; advertisement-free control | Methods naming lock (`AGENTS.md`), `sec:methods:study-design` |
| \(f_{\mathrm{genre}}\) as the instantiation of the trajectory measures | `chp:theory`; `analysis/trajectories/` |
| perceived manipulation "1.27 points on a seven-point scale", any ad \(-\) no ads | `tab:beh-planned` (`results.tex:130`), `confirmatory_planned_D.csv` |
| manipulation "more for the banner than for the mention" | `tab:beh-planned`, implicit \(-\) explicit \(-0.62\) |
| manipulation "more for early than late insertions" | `tab:beh-planned`, early \(-\) late \(+0.58\) |
| credibility "a third of a point" for early insertions | `tab:beh-planned`, early \(-\) late \(-0.33\) |
| "Trust did not differ on any planned contrast after correction" | `tab:beh-planned` trust block, Holm \(.153\) / \(.405\) / \(.063\) |
| trust "dropping only under the early banner" | `fig:beh-localisation`, `results.tex:161`: explicit early \(-0.69\), Holm \(p=.031\) |
| "Banners were remembered better than mentions on cued recall" | `tab:beh-planned` cued memory, implicit \(-\) explicit \(-1.45\) |
| "about half the participants did not report the mention as sponsored" | `notice_recall_percentages.csv` (52 % / 56 %), `results.tex` 7.2, WP3 |
| "Presentation and timing did not interact" | `results.tex:149`, \(|d_z|\le0.06\) on the four post-condition outcomes |
| "60 … corrected interaction tests" (personality) | `tab:results-summary`, Personality moderation 54 / 60 / 0; `personality_lmm.csv` |
| "140 corrected interaction tests" (background factors) | `tab:results-checks`, Demographic moderation 70 + 70 / 0; `demographic_moderation_lmm.csv` |
| "no confirmatory marker separates an advertising condition from the advertisement-free control" | `tab:results-summary`: Dataset A 6 tests / 1 hit (timing only), Dataset B 8 tests / 0 hits; `fig:eeg-forests` |
| "lower posterior \(\alpha\) early than late, averaged over whole condition windows" | `tab:results-summary`, Dataset A key estimate \(-0.22\)~dB, Holm \(p=.0496\) |
| "slow-power response within four seconds of an early banner's onset" (exploratory) | `results.tex:257`, `fig:eeg-holm-board`; `tab:results-summary` exploratory row, explicit early relative \(\delta\) \(+0.19\) |
| "genre trajectories register conversational depth" | `fig:traj-depth`, `tab:results-summary` instrument-check row (guidance share \(0.478\to0.211\)) |
| "every declared advertisement contrast being null" | `tab:traj-crossing` (4 / 0), `tab:traj-late` (3 / 0), `tab:traj-aligned-counts` (9 aligned against 10.46 expected) |
| \(\rho=.80\), \(n=18\); "an association the condition-aggregated score does not show" | `tab:results-summary` Behaviour \(\times\) EEG row, `declared_families.csv` (onset-locked Holm-within-six \(p=.0004\); condition aggregation \(\rho=.24\)) |
| released artefacts (theory, platform, code, linked dataset) | `sec:conclusion:summary`, `Reusable artifacts.` paragraph |

No CI, no Holm \(p\), no \(d_z\) and no percentage is printed in the abstract;
the only digits are \(1.27\), the two turn numbers, the two test counts, the
channel count, \(N=54\), \(n=18\), \(\rho=.80\) and "four seconds".

## 3. What was removed (WP11 F24, F25, F28)

| ID | Removed |
|---|---|
| **F24** | The rendered placeholder `\textit{[\% behavioural findings \%]}`; the 7-line `% [TODO behavioural]` draft; the 7-line `% [TODO combos]` draft; the stray line consisting of a single `+`; the malformed `α\textbackslash{}alpha`, `δ\textbackslash{}delta`, `θ\textbackslash{}theta`, `β\textbackslash{}beta` sequences. The behavioural verdicts and the \(\rho=.80\) association are now rendered prose rather than comments. |
| **F25** | "Instead, timing and presentation matter" (presentation has no corrected direct contrast) and the closing "supporting future research to measure the price of attention" (unsupported, and forbidden by the Discussion lock). The timing result survives as the one corrected condition-aggregation contrast; the explicit-early tilt is stated as exploratory and recommends neither presentation. |
| **F28** | Never entered: the abstract does not say the mention was unrecognised when re-shown. It says only that about half the participants did not report it as sponsored, which is what `notice_recall_percentages.csv` supports. |
| Also gone | "captured attention or deeper processing", "the clearest transient spectral response", the four-band tilt list (exploratory detail, not abstract material), and the Fz \(\theta\) / posterior \(\alpha\) caveat sentence that only made sense next to it. |

## 4. Narrative alignment

- **Order** is the one WP9 was given: problem · what was built · behavioural ·
  heterogeneity · EEG · trajectories · association · release · closing.
- **User-centric frame** is the second sentence ("what those choices cost the
  user rather than what they yield the advertiser"), echoing the 8.6 opener
  (WP5b §6.1) and the jacket sentence in Ch 9 (WP8 §1).
- **Walter's register** (`2026-09-08-final-narrative-from-notebook.md`): "real,
  more modest than feared, concentrated at the moment of insertion" is his
  "ads have a user-side cost, but not as large as first feared; the cost lives
  at insertion, not in the condition"; "on some users more than others" is his
  "the people whose posterior \(\alpha\) falls more at insertion are the people
  whose trust falls more".
- **Findings first, caveat second** (WP8 §6): trust holds up, then the early
  banner; the posterior \(\alpha\) timing contrast, then "averaged over whole
  condition windows"; the \(\rho=.80\) association, then the estimand that
  does not show it. The trajectory sentence is a negative result stated plainly
  rather than an apology.
- Nothing from the forbidden list: no *price of attention*, no serving rule, no
  "depends on how and when", no explicit-late compromise, no relative
  \(\theta\) as confirmatory, no MDE.

## 5. Open for Walter

1. **Word count.** 369 words, above the 350 target but one page at the class's
   1.2 spacing. If you want it at 330, the two cheapest cuts are "one per
   condition:" plus the turn numbers (the design detail repeats in Methods) and
   the clause "and on some users more than others".
2. **"after correction" instead of "Holm-null".** The abstract avoids the word
   Holm on the no-jargon rule, so trust reads "did not differ on any planned
   contrast after correction". Say the word and it becomes "Holm-null on all
   three planned contrasts".
3. **"60 and 140 corrected interaction tests".** Two counts in one clause is
   dense; the alternative is "no personality trait and no background factor
   moderated them" with the counts dropped to Ch 7.
4. **"purpose-built retrieval-based assistant".** Kept short; the platform is
   named again in the release sentence. If you want the system named (or the
   model named) in the abstract, it is a one-clause addition.
5. **Compile still owed.** No LaTeX toolchain in this environment; checks were
   balance scans only.
