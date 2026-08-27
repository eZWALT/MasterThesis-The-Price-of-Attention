# Free-text analysis: codebook and LLM-as-judge (27 August 2026)

Walter's plan for backlog item 4 (`../2026-08-27-backlog-and-timeline.md`),
recorded here with the repo facts that constrain it. Thesis home is
§7.2.3 `sec:results-behaviour-freetext`.

## Walter's plan (as given)

```
IF POSSIBLE BEHAVIOURAL FREE TEXTS ANALYZE x2
--> Create codebooks (inspiration from Ads that Talk Back)
--> Codebook assignment to each observation
--> analysis
      1. Prevalence overall and per condition + significance (chi^2 or F)
      2. Co-occurrence heatmap or network graph
      3. Response length (boxplots)
      4. Representative quotes (table)
      5. Word cloud (stopwords removed)
```

Codebook creation is the hard part and is expected to be **iterative**.
Assignment is LLM-as-judge, and Walter wants **both** execution routes
available: a scripted LLM API pass, and an agentic pass through the
coding agent.

## The two corpora are not symmetric

"x2" is these two, and they have different grains and different \(n\):

| Corpus | Field | Prompt | When | Texts |
|---|---|---|---|---|
| Findings | `conclusion` | "What did you find? What conclusions or decisions did you reach?" | after **every** condition, before the Likert battery | 5 x 54 = **270** |
| Cued-recall reaction | `recall_reaction` | "Please describe your reaction to this content..." | post-experiment, **ad conditions only** | 4 x 54 = **216** |

Required field, max 256 characters, submit blocked on empty
(`core/ui/screens.py`; `app:findings` and `app:cued-recall` in the
thesis appendix).

**The asymmetry matters for analysis 1.** Findings has an \(a^{\emptyset}\)
row, so a code can be tested against the within-person control the rest
of the thesis uses. `recall_reaction` has **no \(a^{\emptyset}\)**, because
there is nothing to re-show for the no-ad condition. Its condition factor
has four levels and no control, so it supports implicit-vs-explicit and
early-vs-late only. Do not silently pool the two corpora.

## Statistical trap in analysis 1 — read before writing any test

A chi-square over 270 findings rows treats five texts from the same
person as five independent observations. That breaks convention 1 of
`sec:methods:statistical-framework` (the participant is the inferential
unit) and would be the easiest thing for an examiner to attack, because
the thesis states the opposite rule two chapters earlier.

Correct options, in order of preference:

1. **Collapse to the person.** For binary code \(c\), score each
   participant with the proportion (or presence) of their texts carrying
   \(c\), then use the same \(D_i\) machinery already declared: paired
   \(t\) / Wilcoxon against \(a^{\emptyset}\), Holm within the codebook.
   This reuses the existing estimators and needs no new Methods text
   beyond a correction family.
2. **Cochran's Q** across the five conditions for a binary code, which is
   the k-sample extension of McNemar and respects the pairing. A plain
   chi-square is the *unpaired* test and is the wrong one here.
3. **Mixed logistic / GEE** clustered by participant, code presence as
   outcome, condition as predictor. Same structure as the trajectory
   crossing check (`run_stages_2_4.py:gee_crossing`).

"F test" implies ANOVA on a continuous outcome; that fits **response
length** (analysis 3), not code prevalence. Even there, use the
repeated-measures form or collapse to person means.

## This contradicts the Methods table as currently written

`tab:analysis-families` has the free-text row as
`descriptive coding, no inferential claim` with correction family
`none, descriptive`, and §7.2.3 was drafted on that basis. Walter's
analysis 1 is inferential.

**Decide before running anything**, because the direction changes what
must be pre-declared:

- Keep it descriptive: prevalence tables and figures, no \(p\) values.
  No Methods change. Safest given the 17 September deadline.
- Make it inferential: the Methods row must name the estimator (option 1
  or 2 above), the correction family (Holm within the codebook), and
  \(n\). Declare it **before** the codebook is applied, otherwise the
  codebook was chosen after seeing which codes separate conditions.

Do not leave the two documents disagreeing.

## Codebook construction

Tang et al. (`tang2025adstalkbackimplications`) is the inspiration, and
their code release is reviewed in
`docs/generated/related-code-chatbot-ads.md`. Their qualitative pipeline
is `llm_sentiment`, `llm_yesnomaybe`, `llm_highlights`, `llm_clustering`,
`llm_tags`, `llm_codes`, all `gpt-4o-mini`, prompts in `data/prompts.py`,
accumulating an open tag list across responses.

**The gap to close: they have no visible human double-coding and no
inter-rater reliability step.** If we borrow the pipeline we have to add
one, or a reviewer will ask why an LLM's labels are treated as data.

Working rules:

- Draft the codebook from a **sample blind to condition**. If the drafter
  can see which texts are \(a^{\mathrm{exp}}\), the codes will encode the
  manipulation.
- Iterate on the sample, then **freeze the codebook** with a version
  string before the full assignment pass. Frozen codebook goes in the
  repo, not only in a chat.
- Include an explicit fallback code (uncodable / no content) rather than
  forcing every text into a substantive code. Findings boxes are required
  fields, so some will be perfunctory.
- Codes should be independently assignable (multi-label), which is what
  makes analysis 2 meaningful.
- Reliability: double-code a subset (20% is the usual floor) and report
  agreement. Options are human vs LLM, or two LLM passes under different
  models. Report Cohen's kappa per code, or Krippendorff's alpha for the
  multi-label set. A code that cannot be applied reliably does not enter
  analysis 1.

## LLM-as-judge, both routes

Walter wants both available. They are for different stages:

- **Agentic (through the coding agent).** Good for drafting the codebook,
  iterating definitions, adjudicating hard cases, and spot-checking the
  scripted pass. Not the artifact of record: a thesis needs a rerunnable
  pass, and an agent session is not one.
- **Scripted API pass.** The artifact of record for assignment. Should
  live next to the other behavioural code, for example
  `analysis/behavioural/freetext/` with a versioned `codebook.json`,
  an `assign_codes.py`, and `outputs/`.

Whichever runs the assignment, log enough to reproduce it: model name and
date, prompt version, temperature 0, seed where the API exposes one, and
the raw model output alongside the parsed codes. Pin the model; do not
let "latest" drift mid-corpus. Keep the judge **blind to condition**, and
present texts in shuffled order so position cannot leak.

## Notes on analyses 2-5

- **2, co-occurrence.** Descriptive. With a codebook of realistic size the
  number of pairs will exceed what 54 people can support, so publish the
  heatmap and do not test the cells.
- **3, response length.** Two known confounds already documented
  elsewhere: message length falls sharply with turn index in this corpus
  (median 40 words at turn 1 to 10 at turn 4,
  `sec:results-trajectories`), and condition order is randomised per
  participant, so session position is available as a covariate. Report
  length by condition, not by turn, and say which one is which.
- **4, representative quotes.** Select by a stated rule (highest code
  confidence, or nearest to median length within the code) rather than by
  eye, and say what the rule was. Quote verbatim, tag with condition and
  a participant pseudonym, never the `participant_id` hash.
- **5, word cloud.** Presentation only. It cannot carry an argument and
  should not be the evidence for any claim in the Discussion. Fine as a
  figure; state the stopword list.

## Locks that still apply

- Results report numbers, Discussion interprets. Any reading of what a
  code *means* for advertising belongs in `sec:disc-behaviour`.
- Free text is Goal 1-adjacent but is **not** a second Likert battery.
  It does not substitute for trust, credibility, or manipulation.
- Participant is the inferential unit.
- Findings text exists for \(a^{\emptyset}\); cued recall does not.

## Related

- Backlog item 4: `../2026-08-27-backlog-and-timeline.md`
- Tang code review: `docs/generated/related-code-chatbot-ads.md`
- Scoring vs Tang: `2026-08-18-tang-scoring-vs-ours.md`
- Notice / cued recall: `2026-08-18-ad-notice-and-cued-recall.md`
- Live instruments: `src/project/core/experiment/surveys.py`,
  `src/project/core/ui/screens.py`
- Statistical framework: thesis `sec:methods:statistical-framework`
