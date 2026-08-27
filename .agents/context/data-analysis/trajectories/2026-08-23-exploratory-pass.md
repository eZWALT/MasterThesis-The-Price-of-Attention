# Trajectories: exploratory pass (new estimators, not new subgroups)

Date: 23 Aug 2026. Owner: Walter. Status: RAN. Stage 5 still blocked.
Script: `analysis/trajectories/run_exploratory.py`
Report: `analysis/trajectories/outputs/exploratory/exploratory.md`
Tables: `outputs/exploratory/tables/x1`–`x6`
Figures: `outputs/exploratory/figures/sx_*.{pdf,png}`

**Nothing in this file is confirmatory.** Family A stays exactly as locked
in `2026-08-23-stages-2-4.md`. This pass exists because "the confirmatory
test was null" and "there is nothing there" are different claims, and only
the second one needed evidence.

Walter's instruction was to keep slicing. Slicing the same estimand into
smaller cells was the wrong response, so the grid was run *and priced*
(section 4) rather than mined. The other three sections are new estimators
on the same locked estimand.

## Why a new pass was warranted

Two facts about family A justified it:

- Definition 6 is argmax on argmax. It compresses a 13-dimensional
  posterior and a 13-dimensional advertisement genre into one bit, then
  reports 9 of 108. That is a lossy outcome, and a null on a lossy outcome
  is weak evidence.
- The advertised genre is **58% `general_guidance_and_info`** (126 of 216)
  with mean classifier confidence **0.40**. So the hard redirection test is
  largely asking whether the modal genre lands on the modal genre. This is
  a real limitation of Definition 6 on this corpus and belongs in the
  write-up, not just in this note.

## 1. Continuous redirection (the main addition)

Estimand: difference-in-differences on posterior mass of the advertised
genre. Within an early-ad conversation, the change from turn 2 (before the
advertisement) to turn 3 (after it), minus the change on the *same* genre
across the same turns in the same participant's no-ad conversation. Person
and baseline genre affinity both cancel.

| contrast | mean | 95% CI |
|---|---:|---|
| early pooled (DiD) | −0.024 | [−0.088, +0.040] |
| implicit early (DiD) | −0.021 | [−0.119, +0.077] |
| explicit early (DiD) | −0.027 | [−0.093, +0.039] |
| turn-3 mass, post only | −0.028 | [−0.067, +0.012] |
| best of turns 3–4 | −0.017 | [−0.052, +0.018] |
| **PLACEBO late ads** | −0.028 | [−0.082, +0.026] |

Baseline mass on the advertised genre is 0.134 with an ad and 0.138
without, so the two sides start level.

**The placebo is the point.** Late advertisements appear after turn 4 and
cannot have influenced turn 3, yet their DiD is −0.028, the same size as
the early −0.024. The small negative is therefore generic turn drift, not
an advertisement effect.

Precision, in the units Definition 6 thresholds: an advertisement would
have to add **more than 0.040 of posterior mass** to the genre it
advertises for this design to have caught it, against a baseline of 0.134.
That is a tighter bound than family A could state.

Any-later-appearance (does the ad genre show up at turn 3 *or* 4, relaxing
Definition 6's "immediately next"): 15 discordant with the ad versus 13
without, exact p = .85. Relaxing the window does not find it either.

## 2. No hidden responders

A mean of zero is also what you get if half the sample is pushed one way
and half the other. That is a variance question and needs no subgroup.

```
observed SD of person-level response  0.4685
randomisation null, mean SD           0.4927
p (observed >= null)                  0.73
```

The spread of individual responses is what shuffling condition labels
inside a person already produces. There is no evidence of responders
cancelling non-responders. **This retires "maybe it works for some
people"** as an available explanation of the null.

The same randomisation reproduces the confirmatory mean: +0.0463,
two-sided p = .53, against the t-test's .47. Family A survives a
design-based null, not just a parametric one.

## 3. Omnibus on the transition matrix

Family A tested one summary of the k=2 matrix. If advertisements
rearranged *where* conversations go without changing *how often* they
move, that test would miss it.

```
observed total variation  0.537
randomisation null, mean  0.526
cells with any mass       65
p                         0.44
```

Observed separation is smaller than chance reassignment produces.

## 4. The slice grid, priced

Every subgroup a reader might ask for (arm, task, session position, task
genre, on both the ad and the control side), crossed with both crossing
outcomes and all three treatment contrasts: **162 cells, 27 subgroups**.

```
nominal hits at .05   4
expected by chance    8.1
best cell             ad session position = 0 · implicit early · JS
best nominal p        0.0196
best family-wise p    0.8324
```

There are *fewer* nominally significant cells than chance predicts, and
the best cell anywhere in the grid is ordinary against a max-|t|
randomisation null. The nominal p distribution shows no excess of small
values; its pile-up at 1.0 is binary-outcome discreteness in small cells,
not evidence.

This table is the answer if anyone later proposes a subgroup claim from
this dataset. `swt_laptop_budget` (nominal p = .021) and `arm = lab` are
the two that would have been harvested; both die here.

## Bug fixed this pass

`gee_crossing()` in `run_stages_2_4.py` imported `smf` and then called
`sm`, so the generated report contained
`model failed: name 'sm' is not defined` while the context note quoted
OR 1.31. The number was right and the report was broken. Fixed; the
report now prints the fitted model (`is_ad` OR 1.31, p = .51). Two paper
figures and `s24_paper_pack.pdf` were also listed but absent, and are now
on disk.

## What this changes for the write-up

- The trajectory null can now be stated as bounded on a *continuous*
  outcome, with a placebo that behaves correctly, rather than only as a
  binary null on 9 of 108.
- "Maybe some participants responded" is testable and tested. It did not
  happen.
- The Definition 6 weakness (ad genres concentrate on the modal genre,
  confidence 0.40) is a limitation to disclose in §7.5, not a result.
- Do **not** promote any of this into family A. It is exploratory and
  labelled as such in the report header.

## Figure cut (proposed, Walter decides)

Stages 1 and 2–4 both have a decided cut; this pass needs one too. The
recommendation is that **one** of these earns paper space, because §6.4
must not carry four separate pictures of nothing.

| Slot | Figure | Why |
|---|---|---|
| **Paper (recommended)** | `sx_continuous_redirection` | Turns the binary 9/108 null into a bounded continuous one, and the placebo panel is visible. Strongest single defence of the null. |
| Appendix | `sx_slice_grid` | The pre-emptive answer to "did you check subgroups". Cite in text even if the figure is cut. |
| Appendix | `sx_heterogeneity` | Retires "it worked for some people". |
| Appendix or drop | `sx_omnibus` | Reassuring but the least surprising of the four. "TV 0.537 vs 0.526, p = .44" survives fine as a sentence. |

If §6.4 is tight, the minimum viable version is: keep
`sx_continuous_redirection` as a figure and carry the other three as one
sentence each. Do **not** pair this with `s24_permutation`; they make the
same point about Definition 6 and the continuous one is stronger.

## Convergence

Four genuinely different estimators, a design-based null, a placebo, and a
priced slice grid all land in the same place. The remaining ways to get a
positive result from this dataset require either a different labelling
scheme or a different experiment, not another test. Stage 5 is blocked.
Writing is Walter's.
