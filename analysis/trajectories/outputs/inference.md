# Genre trajectories: first-pass inference

Genre source: the bare utterance, which is Definition 1 read literally. The deployed classifier saw a context window instead and is reported as a sensitivity analysis in Section 6. Participant is the inferential unit, n=54. Holm is applied within each family.

## 0. What the primary labelling can bear

```
agreement with the logged runtime labels: utterance 0.325, contextual 1.000
distinct genres used: utterance 13, contextual 7 of 13

median words and junk-label rate by turn:
      median_words  junk_rate  mean_confidence
turn                                          
1             40.5      0.041            0.427
2             14.0      0.152            0.425
3             13.0      0.189            0.425
4             10.0      0.200            0.430

junk ~ turn                turn +0.432 (p=0.0000)
junk ~ turn + log_words    turn +0.338 (p=0.0003), log_words -0.289 (p=0.0006)

Short messages do attract the junk classes, so part of the drift is a length artefact. The turn term survives adjustment for length, and classifier confidence is flat across turns, so the drift is not only an artefact. Both statements belong in the write-up.
```

## 1. Targeted advertisement test (the only causally coherent one)

Transition 2 -> 3, which crosses an early advertisement, against the same transition in the no-ad condition.

### Hard shift indicator

                       contrast  n   mean  ci_low  ci_high     dz    p_t  p_wilcoxon  p_holm
       early ads pooled - no ad 54 0.0463 -0.0816   0.1742 0.0988 0.4710      0.3429  0.9419
         implicit early - no ad 54 0.0926 -0.0599   0.2451 0.1658 0.2286      0.2253  0.9143
         explicit early - no ad 54 0.0000 -0.1500   0.1500 0.0000 1.0000      1.0000  1.0000
implicit early - explicit early 54 0.0926 -0.0688   0.2540 0.1566 0.2551      0.2513  0.9143

### The hard shift under an exact paired test

The shift indicator is binary and each participant contributes one crossing transition per condition, so McNemar on the discordant pairs is the primary test and the mean difference above is descriptive.

                       contrast  n  shifted_treatment  shifted_control  only_treatment  only_control  p_exact  p_holm
         implicit early - no ad 54                 47               42              11             6   0.3323  0.9969
         explicit early - no ad 54                 42               42               8             8   1.0000  1.0000
implicit early - explicit early 54                 47               42              12             7   0.3593  0.9969

### How precise is this null

```
delta          mean +0.0463 shift probability, 95% CI +/-0.1279, so |dz| > 0.27 is excluded; the interval spans 0.66 of a between-transition SD.

With n=54 the design rules out medium effects on genre movement but not small ones. The null is bounded, not merely unobserved.
```

## 2. Negative control: late advertisements

All four utterances precede a turn-4 advertisement, so any difference here is nuisance structure rather than an advertisement effect.

### Shifts per conversation

               contrast  n    mean  ci_low  ci_high      dz    p_t  p_wilcoxon  p_holm
late ads pooled - no ad 54 -0.0741 -0.3613   0.2132 -0.0704 0.6072      0.3935     1.0
  implicit late - no ad 54 -0.0185 -0.3475   0.3104 -0.0154 0.9105      0.9418     1.0
  explicit late - no ad 54 -0.1296 -0.4435   0.1843 -0.1127 0.4112      0.3978     1.0

### The same comparisons on whether the conversation shifted at all

97.4% of conversations contain at least one shift. The dichotomy is near-degenerate, so this table is reported for completeness only and the count tests above are primary.

       contrast  n  shifted_treatment  shifted_control  only_treatment  only_control  p_exact  p_holm
a_imp_2 - no ad 54                 53               53               1             1    1.000     1.0
a_exp_2 - no ad 54                 53               53               1             1    1.000     1.0
a_imp_4 - no ad 54                 51               53               1             3    0.625     1.0
a_exp_4 - no ad 54                 53               53               1             1    1.000     1.0

## 3. What actually drives the shift signal

```
condition_label    range 2.352-2.556  Kruskal H=  2.89  p=0.5757
task_id            range 2.296-2.574  Kruskal H=  4.61  p=0.3302
session_position   range 2.352-2.574  Kruskal H=  2.25  p=0.5229
arm                range 2.422-2.511  Kruskal H=  0.04  p=0.8492
```

Mixed model on shifts per conversation, participant random intercept. If the late-condition gap is a task artefact it should not survive adjustment.

```
--- condition only ---
                                                    coefficient  std_err       p
C(condition_label, Treatment('a_none'))[T.a_exp_2]      -0.0741   0.1385  0.5928
C(condition_label, Treatment('a_none'))[T.a_exp_4]      -0.1296   0.1385  0.3494
C(condition_label, Treatment('a_none'))[T.a_imp_2]       0.0741   0.1385  0.5928
C(condition_label, Treatment('a_none'))[T.a_imp_4]      -0.0185   0.1385  0.8937

--- condition adjusted for task ---
                                                    coefficient  std_err       p
C(condition_label, Treatment('a_none'))[T.a_exp_2]      -0.0704   0.1369  0.6072
C(condition_label, Treatment('a_none'))[T.a_exp_4]      -0.1338   0.1364  0.3265
C(condition_label, Treatment('a_none'))[T.a_imp_2]       0.0956   0.1368  0.4845
C(condition_label, Treatment('a_none'))[T.a_imp_4]       0.0339   0.1390  0.8076

```

```
Logistic GEE: delta ~ is_ad + task + session position

rows 270, participants 54
                                           coefficient  std_err       z       p  odds_ratio
Intercept                                       1.4792   0.4611  3.2082  0.0013      4.3893
C(task_id)[T.swt_gardening_birthday_gift]       0.0429   0.5424  0.0791  0.9370      1.0438
C(task_id)[T.swt_laptop_budget]                 0.2862   0.6552  0.4368  0.6623      1.3313
C(task_id)[T.swt_pet_decision_and_setup]       -0.3666   0.4996 -0.7338  0.4631      0.6931
C(task_id)[T.swt_study_environment]             0.2609   0.5829  0.4475  0.6545      1.2980
is_ad                                          -0.0068   0.3163 -0.0214  0.9829      0.9933
session_position                                0.0481   0.1698  0.2834  0.7769      1.0493
```

## 4. Genre mix across the four turns, and a positive control

```
genre  academic_help  creative_ideation  creative_writing_and_role_play  general_guidance_and_info  greetings_and_chitchat  media_generation_or_analysis  other  other_obscene_or_illegal  personal_writing_or_communication  programming_and_data_analysis  purchasable_products  relationships_and_personal_reflection  writing_and_editing
turn                                                                                                                                                                                                                                                                                                                                         
1              0.130              0.033                           0.048                      0.478                   0.011                         0.007  0.022                     0.019                              0.048                          0.000                 0.019                                  0.152                0.033
2              0.107              0.033                           0.041                      0.322                   0.026                         0.019  0.078                     0.074                              0.052                          0.000                 0.019                                  0.189                0.041
3              0.093              0.041                           0.019                      0.285                   0.048                         0.037  0.074                     0.115                              0.048                          0.000                 0.019                                  0.196                0.026
4              0.078              0.037                           0.052                      0.211                   0.044                         0.037  0.089                     0.111                              0.119                          0.004                 0.015                                  0.178                0.026
```

Conversational depth is a manipulation that occurred in every conversation, so it serves as a positive control: the measure should move with it even though it does not move with advertisements.

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

## 5. Exploratory: outcomes that need no classifier

```
--- early advertisement (exposed) vs no-ad, turn-3 message ---
  words              15.63 vs   15.15 words, diff +0.48, dz +0.05, p_wilcoxon 0.5619
  latency_seconds    66.94 vs   65.34 seconds, diff +1.60, dz +0.03, p_wilcoxon 0.1064

--- late advertisement (not yet exposed) vs no-ad, turn-3 message ---
  words              17.76 vs   15.15 words, diff +2.61, dz +0.16, p_wilcoxon 0.2960
  latency_seconds    65.17 vs   65.34 seconds, diff -0.17, dz -0.00, p_wilcoxon 0.3869

Median latency falls across turns (56, 49, 39 s at turns 2, 3, 4), so the measure is live; it simply does not respond to advertisements.
```

## 6. Sensitivity: the deployed contextual classifier

The same analyses under the labelling the live system actually produced, which conditioned on the task prompt and the preceding three messages rather than on the utterance alone. It agrees with the logged runtime labels on every utterance but collapses onto three genres, so it is the sensitivity analysis and not the estimand.

```
                       contrast  n    mean  ci_low  ci_high      dz    p_t  p_wilcoxon  p_holm
       early ads pooled - no ad 54 -0.0185 -0.1370   0.0999 -0.0427 0.7551      0.5592     1.0
         implicit early - no ad 54 -0.0185 -0.1428   0.1057 -0.0407 0.7661      0.7630     1.0
         explicit early - no ad 54 -0.0185 -0.1636   0.1266 -0.0348 0.7990      0.7963     1.0
implicit early - explicit early 54  0.0000 -0.1299   0.1299  0.0000 1.0000      1.0000     1.0

                       contrast  n  shifted_treatment  shifted_control  only_treatment  only_control  p_exact  p_holm
         implicit early - no ad 54                  7                8               5             6      1.0     1.0
         explicit early - no ad 54                  7                8               7             8      1.0     1.0
implicit early - explicit early 54                  7                7               6             6      1.0     1.0

academic_help                        turn1 0.304 -> turn4 0.167  diff -0.137  dz -0.76  p_wilcoxon 0.0000  p_holm 0.0000
general_guidance_and_info            turn1 0.652 -> turn4 0.722  diff +0.070  dz +0.31  p_wilcoxon 0.0293  p_holm 0.0293
relationships_and_personal_reflection turn1 0.041 -> turn4 0.089  diff +0.048  dz +0.36  p_wilcoxon 0.0124  p_holm 0.0248
(3 genres at or above 5% prevalence, Holm across them)

Cumulative drift from the opening genre:
  turn 2 differs from turn 1 in 0.148 of conversations
  turn 3 differs from turn 1 in 0.219 of conversations
  turn 4 differs from turn 1 in 0.252 of conversations
```

## 7. Definition 6 subcase

Conversations shifting into purchasable_products: 14 of 270. By condition: a_exp_2 3, a_exp_4 3, a_imp_2 3, a_imp_4 1, a_none 4.

The no-ad condition contributes as many as any advertised one and the labels are as frequent at turn 1 as at turn 3, so the commercial-intent subcase of Definition 6 is populated by classifier noise rather than by advertisement-induced intent. Under the deployed labelling it is identically zero. Under the literal reading of g^(a), where the classifier is applied to the served product, the genre-aligned shift is 9 of 108, which is below the 10.5 expected when advertisement genres are permuted across conversations (p=0.80); the alignment that occurs is a shared modal genre rather than an effect. See classify_advertisements.py and outputs/advertisements.md.

```
       contrast  n  shifted_treatment  shifted_control  only_treatment  only_control  p_exact  p_holm
a_imp_2 - no ad 54                  3                4               3             4    1.000     1.0
a_exp_2 - no ad 54                  3                4               3             4    1.000     1.0
a_imp_4 - no ad 54                  1                4               1             4    0.375     1.0
a_exp_4 - no ad 54                  3                4               2             3    1.000     1.0
```

