# Data analysis foundation

Behavioural, self-report, and EEG analysis goals for the implemented
conversational advertising study. Decisions recorded 28 July 2026. The interactive
version is `docs/data-analysis-foundation.canvas.tsx`.

## Core position

Within-person condition differences are the evidential centre of the study.
Between-person variables — study arm, personality, familiarity, demographics —
explain heterogeneity; they do not replace the repeated-measures comparison. EEG
stays narrow and exposure-locked, characterising processing rather than claiming
direct measurement of trust or persuasion.

## Canonical design

The implemented protocol, not the earlier publication draft, defines the analysis.

| Condition | Logged key | Format | Timing |
|---|---|---|---|
| No ads | `no_ads` | none | — |
| Inline early | `inline_early` | integrated into reply | turn 2 |
| Inline late | `inline_late` | integrated into reply | turn 4 |
| Block early | `block_early` | labelled separate block | turn 2 |
| Block late | `block_late` | labelled separate block | turn 4 |

The five-level condition factor is primary. A 2×2 format-by-timing decomposition
among the four ad conditions is secondary.

## Available sample

| Quantity | Count |
|---|---|
| Complete crowd sessions | 27 of 30 |
| Clean crowd sessions after quality rules | ~24 |
| Valid lab sessions | 9 (one lab-labelled folder ran the crowd protocol) |
| Conditions per complete participant | 5 |
| Observed ad clicks | 0 |

## Research questions

1. **Primary — experience and commercial pressure.** How does the presentation
   condition change perceived credibility and perceived manipulation within the
   same participant?
2. **Primary — recognition.** Are integrated inline advertisements remembered or
   identified differently from labelled blocks, and does early versus late
   placement change recognition?
3. **Secondary — observable behaviour.** Do conditions alter reply latency,
   response effort, or pre-to-post-exposure conversational behaviour after
   accounting for task, turn, and model latency?
4. **Lab — neural processing.** Do format and timing change exposure-locked
   spectral responses, and do those covary with recognition or perceived
   manipulation?

## Evidence hierarchy

1. Within participant — condition contrasts.
2. Between arms — crowd versus lab heterogeneity, informative but imprecise.
3. Between people — personality and familiarity as shrinkage-based moderators.
4. Cross-modal — EEG-to-survey associations and any crowd forecasting, exploratory
   only. A condition-level forecasting correlation has an effective sample of four.

## Primary outcomes

| Family | Primary score | Unit | Model |
|---|---|---|---|
| Trust / credibility | mean of `llm_reliable`, reversed `llm_false`, reversed `llm_made_up` | participant × condition | mixed model, ordinal sensitivity |
| Manipulation | mean of `behaviour_pushing`, `behaviour_manipulate` | participant × condition | mixed model, report reliability |
| Recognition | `recall_memory` per ad condition, plus blind coding of open text | participant × ad condition | ordinal mixed model |

The live instrument has 20 rated post-condition items: 15 LLM evaluation, three
chatbot personality, two behaviour, plus five optional text prompts. Older
questionnaire documents in the repository describe a different battery and must not
define scoring. Freeze item direction and scoring before inspecting condition
means.

## Planned contrasts

| Contrast | Definition | Status |
|---|---|---|
| Any advertising | mean of four ad conditions minus no ads | primary |
| Integration format | mean inline minus mean labelled block | primary |
| Timing | mean early minus mean late | primary |
| Format × timing | difference of the two format-specific timing effects | secondary, lower power |
| Arm heterogeneity | each contrast by study arm | sensitivity, wide intervals |

Apply Holm correction within each outcome family. Report estimates with 95 percent
intervals regardless of significance.

## Primary model

```
outcome ~ condition * study_arm + task + position + (1 | participant)
```

Task and position stay in the model because each condition is paired with a
different task, task-by-condition counts are not perfectly balanced, and position
captures learning, fatigue, and growing suspicion.

## Secondary behavioural outcomes

| Outcome | Source | Interpretation rule |
|---|---|---|
| Response latency | `time_to_reply_ms` | log-transform; keep separate from model latency |
| Response effort | message and conclusion length | length is objective; quality needs a blinded rubric |
| Conversational change | post-exposure change from pre-exposure turns | within condition; protocol fixes turn count |
| Retrieval quality | relevance score, product, pool size | nuisance covariates, not outcomes |
| Clicks | zero observed | descriptive only; no click-through model |

## Quality and exclusions

| Layer | Primary rule |
|---|---|
| Behavioural primary set | complete session, all five condition surveys, passes frozen quality rules |
| Behavioural sensitivity | re-run including flagged complete sessions and usable partial trials |
| Task and order | include task identity and condition position |
| Retrieval failures | flag empty candidate pools and malformed display; exclude affected trial in sensitivity only |
| EEG participant | valid lab protocol, mapped recording, required markers, frozen artifact threshold |
| EEG epoch | first display marker only; automated rejection plus logged review |

## Preregistration sequence

Freeze, in order, before looking at outcomes: analysis populations; outcome
families and scoring; contrast weights, covariates, and correction; exclusion
thresholds; EEG regions, bands, windows, and the onset-validation rule; the list of
sensitivity analyses; and the code version plus dataset manifest.

## Pipeline outputs

One participant table, one condition-level table, one turn-level table, one recall
table, one EEG epoch manifest, and one exclusions ledger. Every figure should be
reproducible from those frozen intermediates.

## Strongest available claim

Convergence or divergence across measures: what users report, what they remember,
how their interaction changes, and how exposure-locked neural processing differs.
The design does not support the claim that EEG reveals influence participants
cannot report.
