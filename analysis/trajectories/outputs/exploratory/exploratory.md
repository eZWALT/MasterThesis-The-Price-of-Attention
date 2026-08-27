# Exploratory pass: new estimators, not new subgroups

Primary labelling is the bare utterance. Participant is the unit, N=54.
Nulls are design-based: condition labels are permuted among each
participant's own conversations. Late advertisements are a placebo.

**Nothing here is confirmatory.** Family A is locked in
`stages_2_4/stages_2_4.md` and is unchanged by this file.

## 1. Continuous redirection

Definition 6 is argmax on argmax and lands on 9 of 108. The classifier
emits a 13-dimensional posterior, so the same question can be asked of
the mass on the advertised genre rather than of the winner alone.

The estimand is a difference-in-differences: the change in posterior
mass on the advertised genre from turn 2 to turn 3, minus the change
on the *same* genre across the same turns in the same participant's
no-ad conversation. Person and baseline genre affinity both cancel.

| contrast                                               |   n |    mean |   ci_low |   ci_high |      dz |    p_t |   p_wilcoxon |   p_holm |
|:-------------------------------------------------------|----:|--------:|---------:|----------:|--------:|-------:|-------------:|---------:|
| early pooled: posterior lift on ad genre (DiD)         |  54 | -0.0239 |  -0.0882 |    0.0404 | -0.1015 | 0.4592 |       0.6024 |   1      |
| implicit early: posterior lift (DiD)                   |  54 | -0.021  |  -0.1191 |    0.0772 | -0.0582 | 0.6704 |       0.7664 |   1      |
| explicit early: posterior lift (DiD)                   |  54 | -0.0268 |  -0.0925 |    0.0389 | -0.1115 | 0.4163 |       0.4722 |   1      |
| early pooled: turn-3 mass on ad genre (post only)      |  54 | -0.028  |  -0.0674 |    0.0115 | -0.1937 | 0.1605 |       0.201  |   0.9631 |
| early pooled: best of turns 3-4 (post only)            |  54 | -0.017  |  -0.0524 |    0.0184 | -0.1311 | 0.3398 |       0.4669 |   1      |
| PLACEBO late ads: posterior lift before exposure (DiD) |  54 | -0.0279 |  -0.0817 |    0.0258 | -0.1418 | 0.3022 |       0.1286 | nan      |

Mean posterior mass on the advertised genre at turn 2 is 0.134 with an advertisement and 0.138 without, so the two sides start level.

### How large a redirection is ruled out

The binary Definition 6 could only bound the effect in whole
conversations. In posterior mass, the quantity Definition 6 is a
threshold of, the bound is:

```
baseline mass on the advertised genre  0.134
observed change (DiD)                  -0.0239
95% upper bound                        +0.0404
smallest |dz| excluded                 0.273
```

An advertisement would have to add more than 0.040 of posterior mass to the genre it advertises for this design to have seen it, against a baseline of 0.134. That is a tighter statement than family A could make, and it still contains zero.

### Does the genre ever arrive, even late

| contrast                                        |   n |   with_ad |   without_ad |   only_ad |   only_control |   p_exact |
|:------------------------------------------------|----:|----------:|-------------:|----------:|---------------:|----------:|
| early pooled: ad genre appears at turn 3 or 4   |  54 |        24 |           22 |        15 |             13 |    0.8506 |
| implicit early: ad genre appears at turn 3 or 4 |  54 |        13 |           12 |         9 |              8 |    1      |
| explicit early: ad genre appears at turn 3 or 4 |  54 |        11 |           17 |         7 |             13 |    0.2632 |
| PLACEBO late: ad genre appears at turn 3 or 4   |  54 |        32 |           25 |        16 |              9 |    0.2295 |

## 2. Is the null hiding responders

A mean of zero is also what a population produces when half of it is
pushed one way and half the other. That is a variance question, and it
can be tested without splitting anyone into a subgroup.

```
observed SD of the person-level response  0.4685
randomisation null, mean SD               0.4927
p (observed SD >= null)                   0.7316

observed mean                             +0.0463
p (two-sided, randomisation)              0.5293
```

The spread of individual responses is what shuffling condition labels
inside a person already produces. There is no evidence of responders
cancelling non-responders.

## 3. Omnibus on the transition matrix

Family A tested whether conversations move. This tests whether they
move *differently*: the full joint distribution over (from, to) pairs
at k=2, advertisement against no-ad.

```
observed total variation  0.5370
randomisation null, mean  0.5264
cells with any mass       65
p                         0.4368
```

The observed separation is smaller than chance reassignment produces,
which is what two samples from one distribution look like.

## 4. The slice grid, priced

This is the part Walter asked for. Every subgroup a reader might want
is here, crossed with all three treatment contrasts on hard δ.
The point is the last column: the maximum |t| over the
whole grid, recomputed under within-person randomisation, says what
the best cell is worth once you admit you looked everywhere.

Twenty best cells by nominal p; the full grid is in
`tables/x3_slice_grid.csv`.

| outcome   | contrast               | slice                                     |   n |    mean |       t |   p_nominal |   p_familywise |
|:----------|:-----------------------|:------------------------------------------|----:|--------:|--------:|------------:|---------------:|
| delta     | implicit early - no ad | control session position = 1              |  16 |  0.3125 |  2.0761 |      0.0555 |         0.7924 |
| delta     | early pooled - no ad   | control session position = 1              |  16 |  0.25   |  1.7321 |      0.1038 |         0.9548 |
| delta     | implicit early - no ad | ad session position = 0                   |  41 |  0.1463 |  1.636  |      0.1097 |         0.9718 |
| delta     | explicit early - no ad | control task = swt_study_environment      |  10 |  0.2    |  1.5    |      0.1679 |         0.9896 |
| delta     | implicit early - no ad | control task genre = Informational        |   8 |  0.25   |  1.5275 |      0.1705 |         0.9866 |
| delta     | implicit early - no ad | control task = swt_pet_decision_and_setup |   8 |  0.25   |  1.5275 |      0.1705 |         0.9866 |
| delta     | explicit early - no ad | arm = lab                                 |  18 |  0.1667 |  1.3744 |      0.1872 |         0.998  |
| delta     | early pooled - no ad   | control task = swt_study_environment      |  10 |  0.15   |  1.4056 |      0.1934 |         0.9966 |
| delta     | early pooled - no ad   | arm = lab                                 |  18 |  0.1389 |  1.3171 |      0.2053 |         0.9984 |
| delta     | implicit early - no ad | all participants                          |  54 |  0.0926 |  1.2181 |      0.2286 |         0.999  |
| delta     | explicit early - no ad | control session position = 0              |  24 | -0.125  | -1.141  |      0.2656 |         1      |
| delta     | explicit early - no ad | ad task = swt_laptop_budget               |  24 |  0.125  |  1.141  |      0.2656 |         1      |
| delta     | implicit early - no ad | ad task genre = Informational             |  23 |  0.1304 |  1.1413 |      0.266  |         1      |
| delta     | implicit early - no ad | ad task = swt_pet_decision_and_setup      |  23 |  0.1304 |  1.1413 |      0.266  |         1      |
| delta     | explicit early - no ad | control session position = 1              |  16 |  0.1875 |  1.1448 |      0.2702 |         0.9994 |
| delta     | early pooled - no ad   | ad task = swt_laptop_budget               |  24 |  0.1042 |  1.0956 |      0.2846 |         1      |
| delta     | implicit early - no ad | ad session position = 3                   |  21 |  0.0952 |  1      |      0.3293 |         1      |
| delta     | implicit early - no ad | arm = lab                                 |  18 |  0.1111 |  1      |      0.3313 |         1      |
| delta     | implicit early - no ad | control task = swt_study_environment      |  10 |  0.1    |  1      |      0.3434 |         1      |
| delta     | explicit early - no ad | control task = swt_laptop_budget          |   9 | -0.1111 | -1      |      0.3466 |         1      |

```
cells (slice x contrast x outcome)  81
distinct subgroups                  27
nominal hits at .05                 0
expected by chance                  4.0
best cell                           control session position = 1 · implicit early - no ad · delta
best nominal p                      0.0555
best family-wise p                  0.7924
```

Nothing survives. The nominal p values are uniform, the count of
sub-.05 cells is at or below chance, and the best cell in the entire
grid is ordinary against the max-|t| null. If a subgroup claim is made
later, this table is the reason it cannot be made from this dataset.

## Sensitivity: contextual labels

The continuous estimator repeated on the deployed classifier's own
posteriors. The contextual chain is sticky, so it starts with far more
mass already on the advertised genre and has correspondingly less room
to move; the conclusion is unchanged.

| contrast                                                |   n |    mean |   ci_low |   ci_high |      dz |    p_t |   p_wilcoxon |   baseline_mass |
|:--------------------------------------------------------|----:|--------:|---------:|----------:|--------:|-------:|-------------:|----------------:|
| contextual: early pooled posterior lift (DiD)           |  54 | -0.0058 |  -0.0224 |    0.0108 | -0.0957 | 0.485  |       0.9554 |          0.2712 |
| contextual PLACEBO late: posterior lift before exposure |  54 | -0.0146 |  -0.0296 |    0.0005 | -0.2644 | 0.0573 |       0.094  |          0.2611 |

Note the placebo row. Under contextual labels the *late* condition,
whose advertisement had not yet appeared when the measured turn was
written, comes closer to significance (p = .057) than the condition
that was actually exposed (p = .49). Small negative drifts of this
size are what these turns do on their own. Any future reading of a
comparable coefficient as an advertisement effect has to explain why
the placebo produces a larger one.

## Figures

- `exploratory/figures/sx_continuous_redirection.png`
- `exploratory/figures/sx_heterogeneity.png`
- `exploratory/figures/sx_omnibus.png`
- `exploratory/figures/sx_slice_grid.png`
