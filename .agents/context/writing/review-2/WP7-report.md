# WP7 — Research questions redefinition (11 Sep 2026)

Owner: `claude-opus-5-thinking-high`. Scope: `docs/overleaf/thesis/`.
Eleven RQs → nine, renumbered consecutively, each answerable positively or
negatively by Chapter 7. Nothing pushed.

## 1. Old → new mapping

| Old | Topic | New | Note |
|---|---|---|---|
| RQ1 | Format → subjective UX | **RQ1** | Rewritten: names the five measured outcomes instead of "trust, perceived usefulness, perceived intrusiveness" (usefulness and intrusiveness were never outcomes). |
| RQ2 | Format → intent trajectory | **RQ2** | Kept, answered negatively. "Attention shifts" dropped from the wording (the shift metric is not attention; Ch 8 lock). |
| RQ3 | Task type moderation | **dropped** | Never estimated; Latin square holds task constant. |
| RQ4 | Format × timing interaction | **RQ5** | Merged with old RQ7. |
| RQ5 | Timing → subjective UX | **RQ3** | Adds trust after re-exposure, which the family estimates. |
| RQ6 | Timing → intent trajectory | **RQ4** | Kept, answered negatively. |
| RQ7 | Timing effect varies by format | **RQ5** | Merged with old RQ4. |
| RQ8 | Personality × format | **RQ6** | |
| RQ9 | Personality × timing | **RQ7** | |
| RQ10 | Format/timing → cognitive load, attention, arousal | **RQ8** | Reworded to the two confirmatory markers (Fz \(\theta\), posterior \(\alpha\)) plus the exploratory engagement battery. "Cognitive load / attention / affective arousal" removed: not measured as such. |
| RQ11 | Ablation, incremental value of EEG | **RQ9** | Reframed to the estimand of the associations family: does the onset response covary with reported trust. |

Section blocks kept: format · temporal · user heterogeneity ·
neurophysiological mechanisms. The fourth now holds the EEG RQ and the
association RQ. Manual "1. / 2. / 3. / 4." prefixes dropped from the
subsection titles (LaTeX numbers them).

## 2. New RQ text (as inserted in `introduction.tex`)

Lead paragraph:

> The questions below ask what an advertisement placed inside a
> conversational assistant costs the person using it. They come in four
> blocks: what the presentation format does, what the moment of insertion
> does, whether the individual user changes either answer, and what the
> neurophysiological record adds to what people report. Each question names
> the measures that answer it, so that Chapter 7 can answer every one of
> them positively or negatively.

**Advertisement format**

- **RQ1:** How does the presentation format of the advertisement, a product
  mention written into the assistant's reply against a labelled sponsored
  banner, affect the user's trust in the assistant, the credibility they
  grant it, the manipulation they feel, whether they notice the
  advertisement, and whether they remember it afterwards?
- **RQ2:** Does the format change the conversation itself, measured as an
  advertisement-associated shift in the genre of the user's next message?

**Temporal effects**

- **RQ3:** How does the moment of insertion, an early advertisement at
  turn 2 against a late one at turn 4, affect the same reported outcomes,
  and the trust the user reports once the advertisement is shown to them
  again?
- **RQ4:** Does the moment of insertion change the genre trajectory of the
  conversation?
- **RQ5:** Do format and timing interact, so that the cost of an early
  insertion is different for a banner than for a mention?

**User heterogeneity**

- **RQ6:** Do personality traits, measured on the Big Five inventory,
  change how much the format costs the user?
- **RQ7:** Do personality traits change how much the moment of insertion
  costs the user?

**Neurophysiological mechanisms**

- **RQ8:** Do format and timing register in the user's neurophysiological
  response, measured as frontal-midline \(\theta\) power at Fz and
  posterior \(\alpha\) power, with the published engagement indices as an
  exploratory battery?
- **RQ9:** Does the neurophysiological response at the moment the
  advertisement appears covary with the trust the user goes on to report?

## 3. `tab:rq-answers` snippet (for WP5b to insert in `sec:disc-implications`)

Not inserted by WP7. Every number is from `results.tex`
(`tab:beh-planned`, `tab:traj-crossing`, `tab:traj-late`,
`fig:beh-personality` / `tab:results-summary`, `fig:eeg-forests`,
`sec:results-combos-behaviour-eeg`).

```latex
\begin{table}[!htb]
\centering
\footnotesize
\caption{Answers to the nine research questions of \autoref{sec:intro:research-questions}.
Not supported means the family was estimated and no cell survives Holm.}
\label{tab:rq-answers}
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.15}
\begin{tabular}{@{}l >{\raggedright\arraybackslash}p{0.20\linewidth} l >{\raggedright\arraybackslash}p{0.35\linewidth} >{\raggedright\arraybackslash}p{0.13\linewidth}@{}}
\toprule
 & Question & Answer & Evidence & Where \\
\midrule
RQ1 & Does format change the reported experience? & Supported & explicit above implicit on notice \(+1.15\), perceived manipulation \(+0.62\), cued memory \(+1.45\), all Holm \(p<.05\); trust and credibility Holm-null & \autoref{sec:results-behaviour} \\
RQ2 & Does format shift the conversation's genre? & Not supported & implicit \(-\) explicit early \(\delta^{(a)}_2\) \(+0.093\), Holm \(p=.91\) & \autoref{sec:results-trajectories} \\
RQ3 & Does timing change the reported experience? & Supported & early raises perceived manipulation \(+0.58\) and lowers credibility \(-0.33\) and trust on re-exposure \(-0.49\); notice and memory unmoved & \autoref{sec:results-behaviour} \\
RQ4 & Does timing shift the conversation's genre? & Not supported & early pooled \(\delta^{(a)}_2\) \(+0.046\), Holm \(p=.94\); late \(N_{\mathrm{shift}}\) \(-0.074\), Holm \(p=1.00\) & \autoref{sec:results-trajectories} \\
RQ5 & Do format and timing interact? & Not supported & interaction null on all four post-condition outcomes, \(|d_z|\le0.06\) & \autoref{sec:results-behaviour} \\
RQ6 & Does personality moderate the format effect? & Not supported & no trait \(\times\) format term below Holm \(.05\); 0 of 60 in the family & \autoref{sec:results-personality} \\
RQ7 & Does personality moderate the timing effect? & Not supported & no trait \(\times\) timing term survives Holm; nearest extraversion on credibility, Holm \(p=.18\) & \autoref{sec:results-personality} \\
RQ8 & Do format and timing register in the EEG? & Partly & early \(-\) late posterior \(\alpha\) \(-0.22\)~dB, Holm \(p=.0496\); format Holm-null on both confirmatory markers; engagement indices silent & \autoref{sec:results-eeg} \\
RQ9 & Does the onset response track reported trust? & Supported & onset-locked posterior \(\alpha\) \(\times\) trust \(\rho=.80\) \([.48,\,.93]\), Holm \(p=.0004\) (\(n=18\)); \(\rho=.24\) under condition aggregation & \autoref{sec:results-combos} \\
\bottomrule
\end{tabular}
\end{table}
```

If the `\autoref` strings make the last column too wide, `\S\ref{...}` is
the house style already used in `tab:results-summary`.

## 4. Files edited

| File | Replacements |
|---|---|
| `chapters/introduction.tex` | RQ block rewritten (11 RQs → 9); 4 stale `% we could drop…` / `% RQ11 should…` / `% RQ2 and RQ6…` / `% The golden ones…` comments and the `% TODO: List the research questions` line removed; lead paragraph tightened; 4 subsection titles de-numbered; 1 contributions clause fixed (see §6) |
| `chapters/discussion.tex` | 4 prose replacements (l. 69 `RQ8, RQ9`→`RQ6, RQ7`; l. 71 `(RQ3)` clause rewritten without an RQ reference; l. 180 `RQ1, RQ4, RQ5, RQ7`→`RQ1, RQ3, RQ5`; l. 188 `RQ2 or RQ6`→`RQ2 or RQ4`; l. 196 sentence reduced to the personality claim, `RQ6, RQ7`), 1 `% [AI: …]` note updated |

No RQ numbers exist in `models.tex`, `related_works.tex`, `theory.tex`,
`dataset.tex`, `system_design.tex`, `conclusion.tex`, `abstract.tex`
(`models.tex:85` says "research questions" in prose only, no number).
All 45 `% WALTER:` lines in `discussion.tex` and all 3 in `conclusion.tex`
are intact; `git diff | rg "^-.*WALTER"` is empty.

## 5. Left for the orchestrator (files WP7 must not edit)

`chapters/results.tex` — two mentions, both in the personality section:

| Line | Current | Change to |
|---|---|---|
| 176 | `% term, within outcome across 15. RQ8 = format column; RQ9 = timing.` | `RQ6 = format column; RQ7 = timing` |
| 183 | `\caption{… Left: RQ8. Right: RQ9. …}` (`fig:beh-personality`) | `Left: RQ6. Right: RQ7.` |

`chapters/conclusion.tex`: no `RQ\d+` mention. `frontmatter/abstract.tex`:
no `RQ\d+` mention. Nothing to remap there; if WP8/WP9 add RQ references,
they should use the new numbering.

Also for WP5b: `discussion.tex:198` is now a one-sentence orphan
("Personality moderation (RQ6, RQ7) is estimated and Holm-null…") that WP5b
should fold into the surrounding Implications prose or replace with
`tab:rq-answers`; Walter's `% WALTER:` question above it (l. 194) still
refers to the old numbers and was left untouched by instruction.

## 6. Disagreements and judgement calls

1. **`Partly` as a fourth verdict (RQ8).** The brief allows Supported /
   Not supported / Null. RQ8 is honestly mixed: timing survives Holm on
   posterior \(\alpha\) under condition aggregation, format does not.
   Forcing it to one word would either bury a Holm-surviving result or
   overclaim the format null. I used `Partly` and let the evidence cell
   carry the split. Change it if the orchestrator prefers two rows.
2. **`Null` folded into `Not supported`.** Two near-synonyms in one column
   make a reader stop and work out the difference. One word plus the
   caption gloss ("estimated and no cell survives Holm") reads better;
   the nuance (tight interval vs failed instrument) lives in the evidence
   cell.
3. **Contributions bullet edited.** `introduction.tex` promised to
   "evaluate their incremental value beyond behavioral and self-reported
   measures" — the ablation that old RQ11 named and that was never run.
   Left as-is it contradicts the reframed RQ9, so I changed the clause to
   "relate the response recorded at the advertisement's onset to what
   participants report about the same advertisement". Revert if
   contributions belong to another WP.
4. **Old RQ1 wording.** It named "perceived usefulness" and "perceived
   intrusiveness"; neither is an outcome in `sec:behavioral-measures`.
   The new RQ1 names the five that exist. This is a correction, not a
   scope change.
5. **"Attention shifts" removed from RQ2/RQ4.** Ch 8 already locks
   \(\delta^{(a)}\) as an association, not attention. Leaving the phrase
   in the introduction would make the trajectory answer look like a
   failure to measure attention rather than a negative answer to the
   question actually asked.
6. **Task type.** Dropping old RQ3 leaves `discussion.tex:71` saying task
   type is balanced by the Latin square and not modelled. That fact is
   worth keeping in 8.2; it just no longer carries an RQ label.
