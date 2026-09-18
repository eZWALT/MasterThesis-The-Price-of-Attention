# Paper jury consensus, five reviewers (17 Sep)

Reviewers: Gemini flash, Grok, ChatGPT, Claude Sonnet 5, and the Deepseek pass
already reported in `2026-09-17-deepseek-after-refinement.md`. Base PDF is the
paper after `7698241` plus the uncommitted Deepseek bookkeeping edits. Every
claim was checked against the current `.tex` before anything was written; no
number was re-estimated, nothing committed, nothing pushed.

**One line: eight of the fifteen consensus items were already true in the
source or false about it. Seven cheap wording items are fixed. Every science
ask stays refused.**

## Item by item

| # | Item | Status |
| --- | --- | --- |
| 1 | Abstract Dataset-A \(\alpha\) missing the depth confound | fixed now |
| 2 | Abstract / Conclusion EEG onset overclaim | fixed now (both) |
| 3 | Conclusion "worth more … than fake friend advice" | fixed now |
| 4 | Results 5.4 "form the slow-power tilt" | false in source |
| 5 | RQ1 isolation vs the bundled \(\lambda+\theta\) | fixed now |
| 6 | RQ6 row of Table 5 missing the depth confound | fixed now |
| 7 | Novelty sentence unqualified | fixed now |
| 8 | Dataset B is banner-vs-control, not like-with-like | fixed now |
| 9 | any-ad = advertisement + retrieval delay | already fixed |
| 10 | Positive-control Holm family unnamed | already fixed |
| 11 | Arm vs Environment naming | false in source |
| 12 | Abstract "did not seem to interact" | fixed now |
| 13 | Notice 69–74% vs the sponsored-item rates | false in source |
| 14 | HyDE placeholders in Appendix B | fixed now (values from `src/project/`) |
| 15 | Body pointer to the orphan appendix material | fixed now (D.3.1); no appendix exists for the 2,560-test map |

### 1. Abstract \(\alpha\) depth confound — fixed now

Claude, ChatGPT, and Grok all flagged it, and Discussion 6.2 plus Conclusion 7.1
already carried the confound. One clause added, no CIs:

> posterior \(\alpha\) aggregated over a condition was lower for early than for
> late insertion, **on a contrast confounded with conversational depth because a
> late advertisement sits on a shorter, later turn**

### 2. Abstract / Conclusion EEG onset overclaim — fixed now

Real, and the widest consensus of the five (ChatGPT, Deepseek, Claude). The
other agent had already qualified "none after the mention" to "at the same
turn"; what was still missing in both places was that the confirmatory
onset-locked family is Holm-null. One clause in the Abstract:

> **the confirmatory onset-locked cells were null, while** at early-banner onset
> an exploratory slow-power tilt appeared and none after the mention at the same
> turn

and the opening clause of the Conclusion EEG sentence, which had promoted the
exploratory cluster to a headline ("The EEG registered the moment of insertion,
not the format"):

> **In the EEG the confirmatory onset-locked contrasts are Holm-null, and what
> does register is the moment of insertion rather than the format:** posterior
> \(\alpha\) was lower for early than late under condition aggregation …

The implicit-late relative \(\gamma\) cell is not hidden: "at the same turn"
keeps the sentence true, Results 5.4 names the cell, and Table 19 prints it.
Nothing else in either paragraph was touched.

### 3. Conclusion "fake friend" sentence — fixed now

It cited `erickson2025fake` but read as a conclusion of this experiment, which
did not compare a recognised advertisement with covert advice. Attributed, and
the user-side claim this study *can* make kept in front:

> What follows for users is that an advertisement they do not recognise is a
> cost they cannot attribute; that a recognisable advertisement is worth more to
> them than advice offered in the register of a ``fake friend'' is an argument
> from the literature \cite{erickson2025fake} rather than a comparison this
> design ran.

### 4. "form the slow-power tilt" — false in source

The phrase is in Appendix D.2 and it points at `sec:disc-eeg`, which is where the
name belongs. Results 5.4 has the cell counts and no tilt name. No edit.

### 5. RQ1 isolation — fixed now

Table 1 promised presentation format; Table 5 already said the tested contrast
is bundled. The RQ text is thesis-matched (Walter's round-2 ask) so it was left
alone and the clause went on the Table 1 caption:

> Research questions, all asked from the user's side. **Presentation format is
> tested as the bundled presentation-plus-disclosure contrast (\(\lambda\) with
> \(\theta\)), as in \autoref{tab:rq-answers}.**

Grok's wider ask — replace every "format" in the paper — refused.

### 6. RQ6 row — fixed now

> early \(-\) late posterior \(\alpha\) \(-0.22\)~dB, Holm \(p=.0496\), **on a
> contrast that shares its variance with conversational depth**; format
> Holm-null on both markers; engagement indices silent

Same clause as Conclusion 7.1, so the three places now agree.

### 7. Novelty sentence — fixed now

Was a bare triple-intersection claim. Qualified to the reviewed literature and
to LLM-native advertising with concurrent recording; the second half of the
sentence (the design claim, which is defensible) is unchanged:

> **In the literature reviewed here, no study sits at the intersection of
> LLM-native conversational advertising and concurrent EEG**, and none compares
> implicit mentions with explicit banners at early and late turns alongside
> their interactions in the same participants while recording them.

### 8. Dataset B as banner-vs-control — fixed now

Discussion 6.2 already said what stands is "the explicit-early response against
its own control, not a demonstrated difference between the formats", and Method
4.4 already printed the two reconstruction errors, but nothing joined them. One
sentence at the end of the Limitations EEG paragraph, no new analysis:

> Reconstruction error is larger for a mention than for a banner (\(0.43\)~s
> against \(0.23\)~s), and a mention arrives inside a reply that is already
> streaming while a banner is painted at once, so the onset-locked comparison is
> strongest as the banner against its matched control rather than as a
> like-with-like comparison of the two formats.

### 9. any-ad = advertisement + delay — already fixed

Limitations *Protocol and self-report* already says the pause does not cancel
against \(a^{\emptyset}\) "nor in the onset-locked pre-onset window, which sits
inside the wait; the any-advertisement cells therefore measure the advertisement
together with its delay". Not expanded. No TTFT covariate model.

### 10. Positive-control Holm family — already fixed

Table 3 row reads "Positive control, writing vs. reading … the 2 confirmatory
measures", and Method 4.5 says the control "is tested on the two confirmatory
measures before any advertisement contrast is read". No edit.

### 11. Arm vs Environment — false in source

`Environment` appears nowhere in the paper. The by-arm table (`tab:beh-arm-cells`)
has an `Arm` column with `laboratory` / `crowd`, and the prose around it says
"arm" throughout. No edit; no Gold CSV touched.

### 12. Abstract "did not seem to interact" — fixed now

Grok was right that it was softer than the evidence. Matched to Results 5.2 and
Discussion 6.1, not made into a new Holm family:

> **The interaction of format and timing was estimated near zero on all four
> outcomes**, neither personality nor demographics moderated any effect, and no
> one clicked.

### 13. Notice 69–74% — false in source

69–74% and 39–46% are the notice **outcome**, which is what Results 5.2 reports;
the sponsored-content item alone is 81/74/46/37/11 and is declared as such in the
`fig:beh-notice-percentages` sentence. Adding "on the sponsored-content item" to
the abstract would have attached the wrong numbers to that label. No edit.

### 14. HyDE placeholders — fixed now

The braces are a reprinted template and the appendix already said the retriever
fills them, so they stay; what was missing was the deployed configuration.
Values from `src/project/core/config.py`
(`HYDE_NUM_DOCS=2`, `HYDE_TOKENS_PER_DOC=100`, `HYDE_MAX_TOKENS=512`) and
`core/retrieval/hyde.py` (`num_predict = min(512, 2×100)`):

> … are filled by the retriever; **the deployed configuration asked for two
> listings of at most 100 tokens each, with the whole response capped at 200
> tokens.**

Consistent with Method 4.2, which already says "two hypothetical catalogue
entries".

### 15. Body pointer to orphan appendix material — fixed now (half)

D.3.1, the literature-regional rebuild, had no pointer from the body at all
(only Appendix E reached it). One `\autoref` on the existing Method 4.4
sensitivity sentence, which is the placement the channel-set lock allows:

> Other epoch widths, **and a literature-regional rebuild of the ten whole-head
> powers,** are sensitivity analyses (\autoref{app:eeg},
> \autoref{sec:app-eeg-channel-sets}); the full pipeline is in
> \autoref{app:eeg-pipeline}.

The 2,560-test exploratory map has **no appendix section in the paper** (the
trajectory and combos appendices are thesis-only), so there is nothing to point
at. Results 5.5 already declares it inline with its family count. No new
appendix was written.

## Deepseek C1 / C2 / M2, re-checked

The other agent's verdicts hold and its edits were left in place: the 16-row
planned table, the personality nearest term, the \(D_i\) ordering, and \(\Pi\)
are all correct in source; "none after the mention" and the positive-control
interpretive tail were the two real ones and are fixed (mine adds the
confirmatory-null clause on top of its "at the same turn"). Its three may-fix
items — Related Work closer, task/position in Limitations, the familywise-burden
clause — are all present in the working tree and untouched.

## Refused

- **Claude C1, the width / no-ICA grid on the Dataset A onset-centred cell.** A
  new analysis on frozen Gold. Locked, won't fix; Appendix D.1 and Results 5.4
  already state the cell is reported at 4 s only.
- **Task and position random effects, an arm × format primary LMM, Holm on the
  four interaction tests, FDR across the sixteen EEG measures.** All new models.
- **"Confirmatory" → "pre-specified" wholesale.** Method 4.5 already says the
  study was not pre-registered and defines four status labels. The split is not
  demoted and no sentence was rewritten.
- **Grok's "bundled presentation-plus-disclosure" everywhere.** One caption
  clause instead (item 5).
- **Funding / Ethics `XXXXX`** (`sections/08_statements.tex`, two lines). Walter's;
  still open.
- **\(k=37\)** stays out of the body per his call; it appears only in the
  Appendix D caption of `tab:eeg-dataset-a`.
- No ICA model, no Gold rebuild, no `--force-overwrite-confirmatory`,
  `analysis/behavioural/` untouched, thesis untouched.

## Greps after the pass

Clean: "worth more to users", "did not seem to interact", "this thesis",
"Path A", "Wilcoxon Holm", "equal-n", "condition state", "greater visual
processing", "approached significance", "MDE", `\rev{`.
Expected hits only: "none after the mention" (Abstract, now qualified twice),
"form the slow-power tilt" (Appendix D.2, pointing at Discussion), `XXXXX`
(statements, Walter's). No `% WALTER:` line was removed or flipped, no
`% [AI:]` added, `% NUMBERS:` untouched.

## Compile

**Not compiled** — no `latexmk` / `pdflatex` / `tectonic` on this machine. Net
change is about +95 words spread over eight files (Abstract +35, Conclusion
+20, Discussion +45, and one clause each in Introduction caption, Related Work,
Method 4.4, Appendix B), so expect a float nudge on pp. 1, 3, 4, 8, 16, 17 and
no change to the page count. Verify in Overleaf.

## Files touched

`main.tex`, `sections/01_introduction.tex`, `sections/02_related_work.tex`,
`sections/04_method.tex`, `sections/06_discussion.tex`,
`sections/07_conclusion.tex`, `sections/appendix_b_prompts.tex`.
`sections/05_results.tex` carries the other agent's edit only.
