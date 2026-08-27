# Contextual labelling sweep

Date: 23 Aug 2026. Owner: Walter. Status: RAN. Sensitivity only.
Not family A. Hard labels only.

Script: `analysis/trajectories/run_contextual_sweep.py`
Report: `analysis/trajectories/outputs/contextual_sweep/contextual_sweep.md`

The live classifier prepended the task prompt and recent history. That
is Gold `contextual` / recipe `deployed`. Walter asked whether a
different window would produce a significant advertisement effect.

Six recipes, locked before looking at p-values. Task prompts recovered
for 270/270 conversations from the turn-1 deployed string.

| recipe | what the model sees |
|---|---|
| `bare` | current message only (Gold primary) |
| `deployed` | task + last 3 + current (Gold sensitivity) |
| `no_task` | last 3 + current, no task |
| `prev_only` | previous user message + current |
| `task_only` | task + current, no history |
| `opening` | first user message + current |

## Headline

No recipe clears .05 on the confirmatory contrast. The smallest
unadjusted p is **0.096**, and it is the wrong sign: under `prev_only`,
early ads **reduce** crossing shifts by 0.14 relative to no-ad.

Holm across the six early-pooled tests: all ≥ 0.58.

δ-tilde stays at chance under every window (p = 0.79 to 0.97).

## What the windows do to the labels

| recipe | genres used | mean N_shift / 3 | share fully sticky |
|---|---:|---:|---:|
| bare | 13 | 2.45 | 3% |
| prev_only | 13 | 1.59 | 10% |
| opening | 12 | 1.28 | 37% |
| no_task | 12 | 0.94 | 38% |
| task_only | 5 | 0.50 | 68% |
| deployed | 7 | 0.40 | 70% |

The task prompt is the glue. Dropping it (`no_task`) more than doubles
movement versus deployed, and still does not produce an ad effect
(+0.009, p = .90). `task_only` is almost as dead as deployed.

So the pain point is real: the live window under-moves. It is not why
family A is null. A livelier window (`bare`, `prev_only`) still does
not give a positive ad contrast.

## Do not claim

- Contextual labelling “would have found it.” It did not.
- `prev_only` p = .10 is an ad effect. Wrong sign, unadjusted, dies
  under Holm.
- This sweep replaces family A. Primary remains bare utterance.
