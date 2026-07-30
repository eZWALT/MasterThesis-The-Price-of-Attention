# Which models this dataset can support

Feasibility assessment for statistical and predictive models, recorded 29 July
2026. The interactive version, including the full candidate search log, is
`model-feasibility-evolution.canvas.tsx` in this folder.

## The decisive constraint

The unit of independence is the participant, not the conversation. Roughly fifty
participants contributing five correlated observations each supports strong
within-person contrasts, modest choice modelling, and small regularised
predictors — but no policy learning that requires repeated decisions or reward
feedback.

## Effective sample

| Quantity | Count | Derivation |
|---|---|---|
| Usable participants today | 33 | 24 clean crowd plus 9 valid lab |
| Projected participants | ~50 | enrolment target across both arms |
| Condition conversations | ~250 | five per participant |
| Ad-insertion rows | ~200 | four per participant |
| No-ad control rows | ~50 | one per participant |
| Turn-level rows | ~1,000 | four turns per conversation, not independent |
| Lab EEG participants | ~15 | valid protocol with mapped recordings |
| Ad-locked EEG epochs | ~60 | four per lab participant, one per condition |

## Capacity ceilings used to judge feasibility

| Component | Effective sample | Ceiling |
|---|---|---|
| Between-person predictors | ~50 clusters | 5–8 free parameters |
| Within-person contrasts | 5 per participant | supports the four planned contrasts |
| Choice model | ~50 choice sets × 5 alternatives | 4–6 alternative-specific terms |
| Embedding features | ~250 rows | ≤8 components after reduction |
| EEG contrasts | ~15 participants | 2–3 prespecified features per band |

## Recommended models, ranked

### 1. Hierarchical multi-outcome mixed model — primary

```
credibility, manipulation, recall ~ condition * study_arm + task + position + (1 | participant)
```

Estimated jointly with weakly informative priors, summarised through the four
preregistered contrasts, reported with intervals and equivalence tests so null
results stay interpretable. This carries the thesis; everything else is supporting
evidence.

### 2. Within-subject choice model plus action-conditioned reward — policy prototype

Two components, trained separately and combined only at decision time so that
reward weights never enter the fitted parameters.

**Choice component.** Each participant contributes one choice set of five
alternatives. A conditional logit over format and timing attributes, with
hierarchical shrinkage across participants, estimates which presentation each
person prefers. This is the only legitimate multinomial formulation available: a
classifier of the *logged* condition would only recover the randomisation
procedure, because assignment was random rather than chosen.

**Reward component.** Ridge regression predicts each outcome from pre-exposure
context plus the candidate action, so any action can be scored for a context that
was never observed with that action.

**Decision rule.** Choose the action maximising predicted credibility, minus
weighted manipulation, plus weighted recall. Because the no-ad alternative is in
the choice set, the rule can recommend showing nothing — it is a user-experience
aware placement rule, not a revenue maximiser.

**Why off-policy evaluation is legitimate.** Condition assignment was randomised,
so the probability of each logged action is known rather than estimated. That
permits an honest inverse-probability estimate of the learned rule's average
outcome, which is unusual in offline policy work. At ~200 rows the estimate is
coarse and its interval wide: present it as a feasibility demonstration, never as
evidence of beating current industry placement.

### 3. Exposure-locked EEG condition contrasts — lab contribution

About 15 participants and 60 epochs, averaged to one value per participant per
condition. See `eeg-analysis-plan.md` for the full specification.

### 4. Conversational dynamics and attention shift — secondary novelty

Turn-level multilevel models of latency, effort, and intent-trajectory change
around exposure, with permutation-based inference for the shift statistics.

### 5. Frozen-embedding auxiliary covariates — supporting evidence

Frozen sentence embeddings of the pre-exposure conversation, reduced to at most
eight components, entered as covariates. Validate with nested,
participant-grouped cross-validation and report incremental variance with
intervals. Never a standalone predictor at this sample size.

## Ruled out, and what would unlock each

| Strategy | Why it fails here | What would unlock it |
|---|---|---|
| Offline reinforcement learning | one predetermined intervention per conversation, no sequential decisions, no reward signal | a system that repeatedly decides whether and how to advertise |
| Click-through or conversion model | zero clicks observed although clicking was enabled | a deployment where clicks occur |
| Abandonment or survival model | turn count is fixed by protocol, so variance is near zero | free-length conversations |
| Single-trial EEG decoding of format | one ad epoch per participant per condition | many more exposures per participant |
| End-to-end fine-tuning of a 0.6B model | ~250 correlated rows against hundreds of millions of parameters | frozen encoder with a small head is the substitute |
| Confirmatory factor analysis of the 20-item battery | item count large relative to independent participants | reliability and exploratory structure only |
| EEG versus behaviour across different samples | confounds modality with sample | fit both models on the same lab participants |

## Validation rules

- Split by participant, never by conversation row.
- Leave-one-participant-out or grouped k-fold for every predictive model.
- Compare against fixed baselines: always no-ad, always block-late, uniform
  random, and the mixed-effects outcome model.
- Report intervals, not point estimates alone.

## Build order

Fit the hierarchical outcome model first. The choice model, the reward regression,
and every EEG contrast reuse its condition coding, exclusions, and derived tables.
