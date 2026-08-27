# Stages 2–4: advertisement effects, redirection, moderation

Confirmatory family A. Primary labelling is the bare utterance.
Holm is within each outcome. Destinations are descriptive.
Timing is a negative control. Contextual is sensitivity.

## 2. Do advertisements change the crossing transition?

Estimand: transition 2→3 in early ads vs the same transition in no-ad,
paired within participant. N=54.

### Hard shift

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| early ads pooled - no ad | 54 | 0.046 | -0.082 | 0.174 | 0.099 | 0.471 | 0.343 | 0.942 |
| implicit early - no ad | 54 | 0.093 | -0.060 | 0.245 | 0.166 | 0.229 | 0.225 | 0.914 |
| explicit early - no ad | 54 | 0.000 | -0.150 | 0.150 | 0.000 | 1.000 | 1.000 | 1.000 |
| implicit early - explicit early | 54 | 0.093 | -0.069 | 0.254 | 0.157 | 0.255 | 0.251 | 0.914 |

### Exact McNemar

| contrast | n | shifted_treatment | shifted_control | only_treatment | only_control | p_exact | p_holm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| implicit early - no ad | 54 | 47 | 42 | 11 | 6 | 0.332 | 0.997 |
| explicit early - no ad | 54 | 42 | 42 | 8 | 8 | 1.000 | 1.000 |
| implicit early - explicit early | 54 | 47 | 42 | 12 | 7 | 0.359 | 0.997 |

### How precise is this null

| outcome | unit | n | mean | ci_half | ci_low | ci_high | boot_ci_low | boot_ci_high | excluded_|dz| | between_transition_sd |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| delta | shift probability | 54 | 0.046 | 0.128 | -0.082 | 0.174 | -0.074 | 0.176 | 0.273 | 0.387 |

With n=54 the design rules out medium effects on genre movement but
not small ones. The null is bounded, not merely unobserved.

### Destination shares among shifts (descriptive)

| to_genre | count_crossing | share_crossing | n | count_control | share_control |
| --- | ---: | ---: | ---: | ---: | ---: |
| relationships | 17 | 0.191 | 89 | 8.000 | 0.190 |
| guidance | 13 | 0.146 | 89 | 11.000 | 0.262 |
| obscene/illegal | 12 | 0.135 | 89 | 10.000 | 0.238 |
| academic | 9 | 0.101 | 89 | 5.000 | 0.119 |
| media | 7 | 0.079 | 89 | 1.000 | 0.024 |
| personal writing | 6 | 0.067 | 89 | 0.000 | 0.000 |
| other | 6 | 0.067 | 89 | 3.000 | 0.071 |
| greetings | 6 | 0.067 | 89 | 1.000 | 0.024 |
| writing | 5 | 0.056 | 89 | 0.000 | 0.000 |
| purchasable | 4 | 0.045 | 89 | 0.000 | 0.000 |
| ideation | 3 | 0.034 | 89 | 3.000 | 0.071 |
| creative writing | 1 | 0.011 | 89 | 0.000 | 0.000 |

### Logistic GEE on the like-for-like 2→3 rows

The first-pass GEE mixed all three no-ad transitions with the k=2
crossing rows. That is not family A. The model below is k=2 only.

```
Logistic GEE, like-for-like k=2 only (rows 162, people 54)

                                           coefficient  std_err       z       p  odds_ratio
Intercept                                       0.9828   0.5312  1.8501  0.0643      2.6720
C(task_id)[T.swt_gardening_birthday_gift]      -0.1857   0.6084 -0.3052  0.7602      0.8305
C(task_id)[T.swt_laptop_budget]                 0.6783   0.6438  1.0536  0.2921      1.9705
C(task_id)[T.swt_pet_decision_and_setup]       -0.1983   0.5834 -0.3399  0.7339      0.8201
C(task_id)[T.swt_study_environment]             1.2618   0.8410  1.5005  0.1335      3.5319
is_ad                                           0.2705   0.4078  0.6634  0.5071      1.3107
session_position                                0.1009   0.1818  0.5554  0.5786      1.1062
```

### Arm split of the confirmatory contrast

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | arm | n_people |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| crowd · early pooled − no ad | 36 | 0.000 | -0.162 | 0.162 | 0.000 | 1.000 | 0.905 | crowd | 36 |
| lab · early pooled − no ad | 18 | 0.139 | -0.084 | 0.361 | 0.310 | 0.205 | 0.163 | lab | 18 |

## 2b. The instrument is not dead

Conversational depth occurred in every conversation. If the labels
cannot move with it, an advertisement null is uninformative.

```
academic_help                        turn1 0.130 -> turn4 0.078  diff -0.052  dz -0.25  p_wilcoxon 0.0756  p_holm 0.1511
general_guidance_and_info            turn1 0.478 -> turn4 0.211  diff -0.267  dz -1.00  p_wilcoxon 0.0000  p_holm 0.0000
other                                turn1 0.022 -> turn4 0.089  diff +0.067  dz +0.48  p_wilcoxon 0.0011  p_holm 0.0044
other_obscene_or_illegal             turn1 0.019 -> turn4 0.111  diff +0.093  dz +0.57  p_wilcoxon 0.0003  p_holm 0.0015
personal_writing_or_communication    turn1 0.048 -> turn4 0.119  diff +0.070  dz +0.38  p_wilcoxon 0.0062  p_holm 0.0186
relationships_and_personal_reflection turn1 0.152 -> turn4 0.178  diff +0.026  dz +0.11  p_wilcoxon 0.4442  p_holm 0.4442
(6 genres at or above 5% prevalence, Holm across them)

Cumulative drift from the opening genre:
  turn 2 differs from turn 1 in 0.789 of conversations
  turn 3 differs from turn 1 in 0.785 of conversations
  turn 4 differs from turn 1 in 0.826 of conversations
```

Label-independent checks on the turn-3 message (words, latency):

```
--- early advertisement (exposed) vs no-ad, turn-3 message ---
  words              15.63 vs   15.15 words, diff +0.48, dz +0.05, p_wilcoxon 0.5619
  latency_seconds    66.94 vs   65.34 seconds, diff +1.60, dz +0.03, p_wilcoxon 0.1064

--- late advertisement (not yet exposed) vs no-ad, turn-3 message ---
  words              17.76 vs   15.15 words, diff +2.61, dz +0.16, p_wilcoxon 0.2960
  latency_seconds    65.17 vs   65.34 seconds, diff -0.17, dz -0.00, p_wilcoxon 0.3869

Median latency falls across turns (56, 49, 39 s at turns 2, 3, 4), so the measure is live; it simply does not respond to advertisements.
```

## 3. Did the next utterance land on the advertised genre?

Early advertisements: 108. Same genre 19 (0.176),
unrelated shift 80 (0.741),
ad-aligned shift 9 (0.083).

Conditional q = P(aligned | shifted) = 9/89 = 0.101.

Already in the advertisement genre at turn 2: 25 of 108.
Those conversations cannot produce δ-tilde = 1, because a stay is not
a shift. Primary keeps Definition 6 as written (they count as zeros).
Sensitivity, dropping them: 9 of 83
(0.108) vs primary 9/108 = 0.083.

```
Reassigning advertisement genres across the 108 early conversations, 20,000 permutations:

  lands on the advertisement genre  observed  11  chance  14.28  p=0.9240
  delta-tilde = 1                   observed   9  chance  10.46  p=0.7955

Alignment is no more common than coincidence, and in fact slightly less. The alignments that do occur are concentrated in the modal genre of both distributions (general_guidance_and_info 8, other_obscene_or_illegal 2, greetings_and_chitchat 1), which is what a shared marginal produces without any advertisement effect.
```

Permutation on the observed count: 9 vs chance 10.46,
p = 0.795.

| ad_type | n | same | unrelated | aligned | already_in_ad_genre |
| --- | ---: | ---: | ---: | ---: | ---: |
| implicit | 54 | 7 | 43 | 4 | 14 |
| explicit | 54 | 12 | 37 | 5 | 11 |

Commercial-intent reading (shift into purchasable_products):

```
       contrast  n  shifted_treatment  shifted_control  only_treatment  only_control  p_exact  p_holm
a_imp_2 - no ad 54                  3                4               3             4    1.000     1.0
a_exp_2 - no ad 54                  3                4               3             4    1.000     1.0
a_imp_4 - no ad 54                  1                4               1             4    0.375     1.0
a_exp_4 - no ad 54                  3                4               2             3    1.000     1.0
```

## 4. Moderation

Ad type is tested on the crossing estimand (implicit − explicit row
in the hard-shift table). Timing is not a treatment moderator.

### Negative control: late N_shift vs no-ad

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| late ads pooled - no ad | 54 | -0.074 | -0.361 | 0.213 | -0.070 | 0.607 | 0.394 | 1.000 |
| implicit late - no ad | 54 | -0.018 | -0.347 | 0.310 | -0.015 | 0.910 | 0.942 | 1.000 |
| explicit late - no ad | 54 | -0.130 | -0.444 | 0.184 | -0.113 | 0.411 | 0.398 | 1.000 |

## Sensitivity: contextual labels

### Hard shift

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| early ads pooled - no ad | 54 | -0.018 | -0.137 | 0.100 | -0.043 | 0.755 | 0.559 | 1.000 |
| implicit early - no ad | 54 | -0.018 | -0.143 | 0.106 | -0.041 | 0.766 | 0.763 | 1.000 |
| explicit early - no ad | 54 | -0.018 | -0.164 | 0.127 | -0.035 | 0.799 | 0.796 | 1.000 |
| implicit early - explicit early | 54 | 0.000 | -0.130 | 0.130 | 0.000 | 1.000 | 1.000 | 1.000 |

### Exact McNemar

| contrast | n | shifted_treatment | shifted_control | only_treatment | only_control | p_exact | p_holm |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| implicit early - no ad | 54 | 7 | 8 | 5 | 6 | 1.000 | 1.000 |
| explicit early - no ad | 54 | 7 | 8 | 7 | 8 | 1.000 | 1.000 |
| implicit early - explicit early | 54 | 7 | 7 | 6 | 6 | 1.000 | 1.000 |

Contextual δ-tilde: 2 of 108 
(already in ad genre at turn 2: 53). 
The sticky chain makes the subcase almost unreachable.

## Figures

- `stages_2_4/figures/s24_crossing_forest.png`
- `stages_2_4/figures/s24_depth_versus_ad.png`
- `stages_2_4/figures/s24_person_pairs.png`
- `stages_2_4/figures/s24_mcnemar.png`
- `stages_2_4/figures/s24_destinations.png`
- `stages_2_4/figures/s24_redirection.png`
- `stages_2_4/figures/s24_permutation.png`
- `stages_2_4/figures/s24_adjacent.png`
- `stages_2_4/figures/s24_negative_control.png`
