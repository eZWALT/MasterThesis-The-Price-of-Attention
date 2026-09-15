# Ensemble jury reconciliation

Paste everything after the `---` into the reconciling agent together
with the v1 dumps listed below. Do not paste extra Gold numbers. Do
not apply prose from this pass; it only ranks issues for the later
apply (v2). Abstract and Conclusion last when applying. Do not put
review chat back in the `.tex`. Jury table cells are not Gold:
verify every quotation against
`docs/overleaf/thesis/_build/dissertation.pdf` (156 pp) or the
Overleaf source.

What this file is: ChatGPT’s K-sensor reconciliation strategy, stored
15 Sep for later use. Edits below are only where that draft would
mislead on *this* jury (shared brief, sensor classes, thesis locks).
The \(S,E,H,R,D\) weights and the \(V\) map are ChatGPT’s heuristics,
not probabilities and not Gold.

Dumps (iteration 1):

| ID | Class | File |
|---|---|---|
| DS | web, PDF-only | `jury-v1-deepseek.md` |
| GX | web, PDF-only | `jury-v1-grok-4.6.md` |
| CG | web, PDF-only | `jury-v1-chatgpt.md` |
| CS | web, PDF-only | `jury-v1-claude-sonnet-5.md` |
| GM | web, PDF-only | `jury-v1-gemini-3-pro-full.md` |
| MU | in-IDE, PDF + source | `jury-v1-muse-1.3.md` |
| KK | in-IDE, PDF + source | `jury-v1-kimi-k3-max.md` |
| OP | in-IDE, PDF + source | `jury-v1-opus-5.md` |
| FB | in-IDE, PDF + source | `jury-v1-fable-5.1.md` |
| GS | in-IDE, PDF + source | `jury-v1-gpt-5.6-sol.md` |

Ignore `jury-v1-gemini-3-pro.md` (truncated mid-Ch 5). Do not treat
the in-IDE extras as additional independent web votes.

---

You are the senior examiner reconciling K independent reviews of the same thesis (*The Price of Attention*, v1, 156 pp).

Treat reviewers as **noisy, strongly dependent expert sensors**, not as independent votes. All web jurors received the same examiner brief (`.agents/context/writing/2026-09-11-thesis-review-metaprompt.md`). That brief already named latency, Holm vs Wilcoxon, confirmatory-without-registration, Dataset A naming, \(\theta\)–\(\lambda\), “depends on how and when”, serving-rule language, \(\rho=.80\) multiplicity, classifier 32.5%, and the Abstract/Discussion/§6.3 focus. Agreement on a briefed item is **prompt-induced consensus**, not independent discovery. Your task is to infer the underlying genuine thesis vulnerabilities, not to majority-vote reviewer prose.

Fact-check every quotation and every table cell against the PDF or the Overleaf `.tex`. A reviewer’s number is not Gold. Deepseek mixed Fz \(\beta\) for Fz \(\theta\); Gemini’s first pass never saw Ch 6–9; several jurors wrote “trust at ceiling” when the means are credibility’s problem (trust \(\approx 4.7\)–\(5.4\)). Discard or downweight a reviewer’s claim when the thesis page contradicts it.

Do not invent new analyses, shrink Holm families after seeing \(p\), or reopen frozen Gold. Trajectory theory is thesis-only by design. Holm \(p\) on planned contrasts is Holm-adjusted paired \(t\); Wilcoxon \(p\) is raw. Association Holm is Holm-adjusted Spearman — that is declared, not a secret mix-up, unless Methods still says “Holm only on \(t\)” and Results labels “LMM Holm” / “Holm Spearman” without saying so. Dataset A display name is **condition aggregation**.

## Sensor classes and independence weights

Two classes:

* **Web (DS, GX, CG, CS, GM).** Same brief, PDF only, no repo. Within-class observations of a *briefed* issue are highly dependent. Default \(w_{ji}=0.35\) for a briefed issue; \(w_{ji}=1\) for an issue the brief did not name.
* **In-IDE (MU, KK, OP, FB, GS).** Same brief plus source / local PDF. They can see broken `\ref`s, appendix numbers, and debrief wording the web jurors missed. Default \(w_{ji}=0.5\) on briefed issues (they still saw the brief); \(w_{ji}=1\) on unbriefed, source-visible issues.

If two reviews share near-identical phrasing or the same invented premise (e.g. “trust mean \(\approx 6/7\)”), set the later \(w_{ji}\) near 0.2. Never give Gemini’s truncated dump a weight. Never let \(C_i=7/7\) on a briefed item look like seven independent discoveries: report web-class \(C_i\) and in-IDE extras separately, then a brief-adjusted \(C_i\).

## 1. Canonicalize issues

Convert every criticism into a canonical issue with:

* issue (one causal claim, not a topic label)
* thesis evidence / quotation (page or section, verified)
* reviewer IDs
* domain (design / EEG / behaviour / trajectories / associations / consistency / writing)
* severity \(S\) 0–10
* evidence strength \(E\) 0–10 (from the thesis, not from reviewer confidence)
* validity (see §3)
* already acknowledged? (see §5)
* briefed? (was this item in the examiner metaprompt?)
* independent or likely copied/dependent?

Cluster semantically equivalent criticisms. Do **not** merge distinct causal problems because they share a topic. Latency in the Dataset B pre-window is not the same issue as latency in the behavioural any-ad contrast. \(\theta\)–\(\lambda\) in Methods is not the same as an “obligation to disclose” in the Conclusion. Exploratory tilt in the Abstract is not the same as Holm-within-measure on 98 cells.

## 2. Estimate consensus

For issue \(i\), let \(x_{ji}=1\) if reviewer \(j\) raises it, otherwise 0.

Give each observation an independence weight \(w_{ji}\in[0,1]\) as above.

Effective consensus:

\[
C_i=\frac{\sum_j w_{ji}x_{ji}}{\sum_j w_{ji}}
\]

Interpret roughly: \(<0.25\) low; \(0.25\)–\(0.50\) mixed; \(0.50\)–\(0.75\) high; \(\ge 0.75\) very high.

Do not treat consensus as correctness. More reviewers only means stronger **weighted** agreement. On a briefed issue, high \(C_i\) is the expected default.

## 3. Estimate validity separately

Classify each issue against the thesis (and Gold only if you must check a number the PDF already prints):

* **Established** — demonstrated from the thesis/data/design.
* **Probable** — strong methodological inference, little ambiguity.
* **Plausible** — reasonable but materially uncertain.
* **Probably invalid**
* **Invalid**

A criticism is not valid because several reviewers made it. Map, as ChatGPT’s heuristic only:

\[
V\in\{1.0,\ 0.8,\ 0.55,\ 0.2,\ 0\}
\]

Known false or overstated reviewer premises to test before assigning \(V\):

* “depends on how and when” still in the Abstract (Discussion already refuses it; several jurors quoted the brief’s *test phrase*, not the live Abstract).
* Trust at ceiling / trust Holm-null as “safe format”.
* Dataset B confirmatory cells harvested as a “tilt finding” when the thesis already labels them exploratory.
* Off-4 s cells as the confirmatory family (they are sensitivity).
* Interaction \((1,-1,-1,1,0)\) “never estimated” without checking the \(|d_z|\le 0.06\) sentence and whether EEG interaction is actually missing.
* Holm-on-Spearman as a Wilcoxon mix (it is not).

## 4. Score importance

For each issue, 0–10:

* \(S\) = severity for a defence examiner
* \(E\) = evidence strength on the page
* \(H\) = impact on headline claims (Abstract / Ch 9)
* \(R\) = impact on RQ answers
* \(D\) = cross-document inconsistency (Methods vs Results vs Discussion vs Abstract/Conclusion)

\[
P_{\mathrm{raw}}=0.30S+0.25E+0.15H+0.15R+0.15D
\]

\[
P=P_{\mathrm{raw}}V
\]

Do **not** multiply priority by consensus. Consensus is robustness of the observation, not truth.

## 5. Account for acknowledgement

* \(A=1.0\) — new, or acknowledged in one chapter and contradicted in another (Abstract/Conclusion vs Discussion is the usual case).
* \(A=0.5\) — acknowledged but under-bounded (the honest sentence exists; the citable sentence does not carry it).
* \(A=0.25\) — explicitly acknowledged and correctly bounded on every surface that cites the cell.

\[
P_{\mathrm{final}}=P\times A
\]

Do not discount an acknowledged limitation if Abstract or Conclusion still makes the claim the limitation undermines. That is unresolved (\(A=1\)).

A declared limitation that is *not* contradicted is not an apply item. Do not reopen science (families, \(k=37\), ICA archive, Katerina’s tree, item drops by \(p\)).

## 6. Minority-expert rule

A criticism from one reviewer can still be high priority.

If \(V=1\), \(E\ge 8\), \(S\ge 8\), do not suppress it because \(C_i\) is low.

This is where KK/CS source-visible items usually sit: Discussion-only numbers (e.g. \(4.60\) dB), broken `\ref`s, Appendix C.6 naming ChatGPT / “positive light” / “random” products, catalogue \(117{,}343\) vs \(117{,}243\), Fig 7.8 printing \(.050^*\), recognition-share quantifier drift, McNemar-vs-\(t\) column, promised across-12 Holm never printed.

Conversely, a briefed item raised by all five web jurors stays low priority when \(V\) is weak.

## 7. Detect dependence and false consensus

Identify cases where several reviewers inherit the same incorrect premise, or several criticisms are downstream of one root problem. Report the **canonical root**, not every consequence.

Likely roots on this thesis (test, do not assume):

1. Advertised-turn retrieval wait vs like-with-like baselines (behaviour any-ad **and/or** Dataset B pre-window — keep the split if the pre-window argument differs by format).
2. Surfaces (Abstract/Conclusion) drop labels and confounds that Ch 7–8 attach (post hoc trust cell, exploratory tilt, depth confound, instrument-bounded trajectory null, serving prescription vs “not a recommendation”).
3. “Confirmatory” without registration, plus the word’s weight on a boundary EEG cell.
4. \(\theta\) bundled with \(\lambda\), then Conclusion “obligation to disclose”.
5. \(\rho=.80\) selected across two EEG scores / a 16-measure screen at \(n=18\).

Do not list “ Holms within measure”, “ocular/ICA”, “n=18”, and “compositional \(\delta/\theta/\alpha/\beta\)” as four equal findings if they are one tilt-overclaim.

## 8. Final synthesis

### Consensus

What **unbriefed** or **brief-adjusted** independent reviewers genuinely converge on. Then, separately, what the brief already forced them to say.

### Ranked issues

| Rank | Canonical issue | Reviewers | Briefed? | Consensus | Validity | S | E | \(P_{\mathrm{final}}\) | Action |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |

Rank by **final priority**. Consensus is a robustness tag, not the sort key. Action is one of: `fix surface` (Abstract/Ch 9 / one sentence), `fix contract` (Table 6.1 / 7.8 / Methods wording), `add limitation` (already-true fact not on the confound list), `verify number`, `ignore` (invalid or already bounded).

Prefer `fix surface` and `add limitation` over new tests. Do not propose shrinking Holm families, new Gold, ICA overwrite, or Katerina’s tree.

### Minority-critical

Strong, verified objections from one or two reviewers (especially KK, CS).

### False consensus / duplicated issues

Popular but weak, brief-induced, dependent, incorrect, or redundant.

### Already-addressed limitations

Acknowledged and bounded on every citing surface. Not apply items.

### Top defence vulnerabilities

For the five highest-\(P_{\mathrm{final}}\) issues: the hostile examiner question most likely to expose it.

The objective is not “what did most reviewers say?”

It is: **which weaknesses are real, consequential, and still undefended under hostile scrutiny?**

Consensus = robustness of the observation. Validity = truth on the page. Severity and impact = importance. Acknowledgement × contradiction = whether v2 must still touch the sentence.
