# Analysis code in `byron123t/chatbot-ads`

Review of <https://github.com/byron123t/chatbot-ads>, the code release for
Tang et al., *Ads that Talk Back* (IMWUT 2025) — the instrument our post-condition
questionnaire was adapted from. Inspected 30 July 2026.

## Verdict

**Yes, the user-study analysis code is present.** It is not reproducible end to end,
because no participant data is included, but the statistical decisions, scale
construction, and qualitative-coding pipeline are all readable.

## Repository facts

| Property | Value |
|---|---|
| Default branch | `main` |
| Created and last pushed | 8 October 2025, within one minute |
| Stars / forks | 0 / 0 |
| Licence | GPL-3.0 |
| Total tracked entries | 57 |

The single-push history, a 4.3 MB file literally named
`eval/ranked_generations copy 2.json`, and a zero-byte `eval/parse_wildchat.py`
indicate a one-off code dump rather than a maintained artifact. There are no tests
and no notebooks.

## Where the analysis lives

| File | Lines | Role |
|---|---|---|
| `eval/parse_study_data.py` | 1,236 | **The user-study analysis.** Parsing, scale construction, reliability, inferential tests, plots |
| `eval/parse_chat_data.py` | 401 | Conversation-log parsing |
| `eval/analyze_outputs.py` | 148 | Benchmark output analysis, not the user study |
| `eval/power_analysis.py` | 9 | A priori power analysis |
| `eval/evaluator.py` | 128 | Benchmark scoring |
| `eval/curate_profiles.py`, `create_profiles.py` | 40,819 / 10,682 bytes | Persona construction for personalised ads |

## Statistical approach

Stack: `scipy.stats`, `statsmodels`, `pingouin`, `scikit-posthocs`, `seaborn`.

- **Reliability.** `pg.cronbach_alpha(..., ci=.99)` computed per construct.
- **Assumption checks.** Shapiro–Wilk on model residuals; Levene for homogeneity of
  variance. Both written to CSV.
- **Two inferential paths are implemented:**
  - `perform_anova` — OLS via `smf.ols`, `anova_lm` type II, then Tukey HSD if the
    omnibus p < 0.05.
  - `perform_kruskal` — Kruskal–Wallis, then Dunn post-hoc with Bonferroni
    correction if p < 0.05.
- **The path actually executed is the non-parametric one.** The main block loops
  over every outcome calling `perform_kruskal`, for three groupings:
  `overall_mode` (six groups: three ad conditions × two models), `mode`, and
  `model`. The ANOVA function is defined but not called there, and `t_test()` and
  `anova()` at lines 796 and 800 are stubs.
- **Power analysis.** `FTestAnovaPower().solve_power(effect_size=0.5, alpha=0.05,
  k_groups=6, power=0.8)`. Note the committed effect size is 0.5, which yields a
  much smaller target than the sample the paper reports recruiting — treat the
  script as indicative, not as the paper's stated calculation.

## Outcome variables

The `likert_variables` list analysed with Kruskal–Wallis:

```
Sentiment, Credibility, Helpfulness, Convincingness, Relevance, Neutrality,
Godspeed, FeltAdvertising, FeltManipulated, TechIntegrate
```

Additional moderator groupings, applied only to `Sentiment` and `Godspeed`: age,
education, familiarity, frequency, sex, race.

## Most valuable transferable finding: their scales dropped items

Our `LLM_EVAL_CATEGORIES` in `src/project/core/experiment/surveys.py` is adapted
from this instrument with three items per construct. Their code shows that **three
of the five constructs did not survive with all three items** — the excluded items
are commented out of both the composite and the alpha computation.

Reconstructing from their `Q2348_*` mapping and inversion logic:

| Construct | Items retained | Item dropped |
|---|---|---|
| Credibility | the two reverse-keyed items (our `llm_false`, `llm_made_up`) | the positive item (our `llm_reliable`) |
| Helpfulness | all three, one reverse-keyed | none |
| Convincingness | the reverse-keyed item plus one positive | one positive item |
| Relevance | all three, one reverse-keyed | none |
| Neutrality | the two positive items (our `llm_neutral`, `llm_impartial`) | the reverse-keyed item (our `llm_opinionated`) |

`Sentiment` is a separate composite spanning all fifteen items.

**The pattern is direction homogeneity.** In both Credibility and Neutrality they
kept the same-direction pair and dropped the odd one out — in one case discarding
the positive item, in the other the negative one. Short three-item scales mixing
positive and negative wording did not hold together.

This is a direct caution for our plan: the credibility composite proposed in
`data-analysis-foundation.md` mixes `llm_reliable` with two reverse-keyed items,
which is exactly the combination that failed here. Compute our own alpha before
fixing that composite, and pre-register the fallback of a same-direction pair.

Their inversion is `8 − x` on a 1–7 scale, and their Likert map treats
"Strongly Disagree" as 1 through "Strongly Agree" as 7, with a tolerated typo key
(`Strongle Agree`).

## Qualitative coding pipeline

`llm_sentiment`, `llm_yesnomaybe`, `llm_highlights`, `llm_clustering`, `llm_tags`,
and `llm_codes` send open-text responses to `gpt-4o-mini` with prompts held in
`data/prompts.py`, accumulating an open tag and code list across responses.

Relevant to coding our `recall_reaction` free text, but note there is no visible
human double-coding or inter-rater reliability step. If we adopt this, add one.

## Behavioural metrics from conversation logs

`chat_stats` computes, per condition: query count, query and response length in
both characters and tiktoken tokens, product distribution, **ad link clicks**, and
**disclosure clicks**.

Two of those are informative for us. They instrumented and obtained click data,
which our logs do not contain despite clicking being enabled. And they used median
rather than mean for length summaries.

## What is absent

`parse_study_data.py` reads `demographics.csv`, `study_data.csv`, and
`redis_data.json` from hardcoded relative paths. **None of the three is in the
repository**, and there are no `stats/` or `plots/` output directories. The linked
Google Drive covers the LLM benchmark outputs only, not the human-subject data.

So the analysis cannot be re-run, and their published numbers cannot be verified
from this release.

## Limits on transfer to our study

Their design is **between-subjects** with six independent groups, which is why
Kruskal–Wallis with Dunn post-hoc is appropriate for them. Ours is within-subject
with five conditions per participant. Their inferential code is therefore **not
reusable for our contrasts** — applying group-comparison tests to our repeated
measures would ignore participant clustering and misstate the standard errors.

They also have no timing manipulation and no neurophysiological measures.

**Reuse:** scale construction and reverse-keying, reliability grouping, the
qualitative coding pipeline, behavioural metric definitions, and the assumption-check
and CSV-export discipline.

**Do not reuse:** the group-comparison inferential path, or the power analysis,
which is calculated for a between-subjects design.
