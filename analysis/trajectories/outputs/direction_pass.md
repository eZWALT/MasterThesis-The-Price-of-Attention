# Direction pass

## 1. Descriptive / EDA

### Bare utterance (primary)

| genre | utterances | share |
| ---: | ---: | ---: |
| general_guidance_and_info | 350 | 0.324 |
| relationships_and_personal_reflection | 193 | 0.179 |
| academic_help | 110 | 0.102 |
| other_obscene_or_illegal | 86 | 0.080 |
| personal_writing_or_communication | 72 | 0.067 |
| other | 71 | 0.066 |
| creative_writing_and_role_play | 43 | 0.040 |
| creative_ideation | 39 | 0.036 |
| greetings_and_chitchat | 35 | 0.032 |
| writing_and_editing | 34 | 0.031 |
| media_generation_or_analysis | 27 | 0.025 |
| purchasable_products | 19 | 0.018 |
| programming_and_data_analysis | 1 | 0.001 |

| condition_label | n_shift | shift_rate | diversity | entropy_nats | max_persistence |
| ---: | ---: | ---: | ---: | ---: | ---: |
| No ad | 2.481 | 0.827 | 3.111 | 1.055 | 1.519 |
| Implicit early | 2.556 | 0.852 | 3.167 | 1.084 | 1.426 |
| Explicit early | 2.407 | 0.802 | 3.130 | 1.064 | 1.574 |
| Implicit late | 2.463 | 0.821 | 3.000 | 1.008 | 1.537 |
| Explicit late | 2.352 | 0.784 | 3.111 | 1.057 | 1.630 |

Mean shift rate 0.817, diversity 3.10, entropy 1.054 nats, max persistence 1.54.
Conversations with at least one shift: 97.4%.

Turn profile (row shares):

| turn | academic_help | creative_ideation | creative_writing_and_role_play | general_guidance_and_info | greetings_and_chitchat | media_generation_or_analysis | other | other_obscene_or_illegal | personal_writing_or_communication | programming_and_data_analysis | purchasable_products | relationships_and_personal_reflection | writing_and_editing |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.130 | 0.033 | 0.048 | 0.478 | 0.011 | 0.007 | 0.022 | 0.019 | 0.048 | 0.000 | 0.019 | 0.152 | 0.033 |
| 2 | 0.107 | 0.033 | 0.041 | 0.322 | 0.026 | 0.019 | 0.078 | 0.074 | 0.052 | 0.000 | 0.019 | 0.189 | 0.041 |
| 3 | 0.093 | 0.041 | 0.019 | 0.285 | 0.048 | 0.037 | 0.074 | 0.115 | 0.048 | 0.000 | 0.019 | 0.196 | 0.026 |
| 4 | 0.078 | 0.037 | 0.052 | 0.211 | 0.044 | 0.037 | 0.089 | 0.111 | 0.119 | 0.004 | 0.015 | 0.178 | 0.026 |

| position | shift_rate | n |
| ---: | ---: | ---: |
| crosses_ad | 0.824 | 108 |
| no_ad | 0.827 | 162 |
| post_ad | 0.889 | 108 |
| pre_ad | 0.794 | 432 |

### Contextual (sensitivity)

| genre | utterances | share |
| ---: | ---: | ---: |
| general_guidance_and_info | 755 | 0.699 |
| academic_help | 244 | 0.226 |
| relationships_and_personal_reflection | 69 | 0.064 |
| creative_writing_and_role_play | 8 | 0.007 |
| creative_ideation | 2 | 0.002 |
| writing_and_editing | 1 | 0.001 |
| personal_writing_or_communication | 1 | 0.001 |

| condition_label | n_shift | shift_rate | diversity | entropy_nats | max_persistence |
| ---: | ---: | ---: | ---: | ---: | ---: |
| No ad | 0.241 | 0.080 | 1.222 | 0.142 | 3.630 |
| Implicit early | 0.389 | 0.130 | 1.315 | 0.185 | 3.556 |
| Explicit early | 0.370 | 0.123 | 1.352 | 0.203 | 3.556 |
| Implicit late | 0.574 | 0.191 | 1.444 | 0.264 | 3.333 |
| Explicit late | 0.407 | 0.136 | 1.315 | 0.181 | 3.556 |

Mean shift rate 0.132, diversity 1.33, entropy 0.195 nats, max persistence 3.53.
Conversations with at least one shift: 30.0%.

Turn profile (row shares):

| turn | academic_help | creative_ideation | creative_writing_and_role_play | general_guidance_and_info | personal_writing_or_communication | relationships_and_personal_reflection | writing_and_editing |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.304 | 0.000 | 0.000 | 0.652 | 0.000 | 0.041 | 0.004 |
| 2 | 0.248 | 0.000 | 0.007 | 0.693 | 0.000 | 0.052 | 0.000 |
| 3 | 0.185 | 0.000 | 0.011 | 0.730 | 0.000 | 0.074 | 0.000 |
| 4 | 0.167 | 0.007 | 0.011 | 0.722 | 0.004 | 0.089 | 0.000 |

| position | shift_rate | n |
| ---: | ---: | ---: |
| crosses_ad | 0.130 | 108 |
| no_ad | 0.080 | 162 |
| post_ad | 0.120 | 108 |
| pre_ad | 0.155 | 432 |

## 2. Advertisement effects on genre dynamics

Estimand: transition 2→3 in early ads against the same transition in the no-ad condition, paired within participant.

### Bare utterance (primary)

Hard shift (paired mean difference):

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| early ads pooled - no ad | 54 | 0.046 | -0.082 | 0.174 | 0.099 | 0.471 | 0.343 | 0.942 |
| implicit early - no ad | 54 | 0.093 | -0.060 | 0.245 | 0.166 | 0.229 | 0.225 | 0.914 |
| explicit early - no ad | 54 | 0.000 | -0.150 | 0.150 | 0.000 | 1.000 | 1.000 | 1.000 |
| implicit early - explicit early | 54 | 0.093 | -0.069 | 0.254 | 0.157 | 0.255 | 0.251 | 0.914 |

Exact McNemar on the crossing transition:

| contrast | n | shifted_treatment | shifted_control | only_treatment | only_control | p_exact | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| implicit early - no ad | 54 | 47 | 42 | 11 | 6 | 0.332 | 0.997 |
| explicit early - no ad | 54 | 42 | 42 | 8 | 8 | 1.000 | 1.000 |
| implicit early - explicit early | 54 | 47 | 42 | 12 | 7 | 0.359 | 0.997 |

Destination shares among **shifts** on 2→3:

| to_genre | count_crossing | share_crossing | n | count_control | share_control |
| ---: | ---: | ---: | ---: | ---: | ---: |
| relationships_and_personal_reflection | 17 | 0.191 | 89 | 8.000 | 0.190 |
| general_guidance_and_info | 13 | 0.146 | 89 | 11.000 | 0.262 |
| other_obscene_or_illegal | 12 | 0.135 | 89 | 10.000 | 0.238 |
| academic_help | 9 | 0.101 | 89 | 5.000 | 0.119 |
| media_generation_or_analysis | 7 | 0.079 | 89 | 1.000 | 0.024 |
| personal_writing_or_communication | 6 | 0.067 | 89 | 0.000 | 0.000 |
| other | 6 | 0.067 | 89 | 3.000 | 0.071 |
| greetings_and_chitchat | 6 | 0.067 | 89 | 1.000 | 0.024 |
| writing_and_editing | 5 | 0.056 | 89 | 0.000 | 0.000 |
| purchasable_products | 4 | 0.045 | 89 | 0.000 | 0.000 |
| creative_ideation | 3 | 0.034 | 89 | 3.000 | 0.071 |
| creative_writing_and_role_play | 1 | 0.011 | 89 | 0.000 | 0.000 |

### Contextual (sensitivity)

Hard shift (paired mean difference):

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| early ads pooled - no ad | 54 | -0.018 | -0.137 | 0.100 | -0.043 | 0.755 | 0.559 | 1.000 |
| implicit early - no ad | 54 | -0.018 | -0.143 | 0.106 | -0.041 | 0.766 | 0.763 | 1.000 |
| explicit early - no ad | 54 | -0.018 | -0.164 | 0.127 | -0.035 | 0.799 | 0.796 | 1.000 |
| implicit early - explicit early | 54 | 0.000 | -0.130 | 0.130 | 0.000 | 1.000 | 1.000 | 1.000 |

Exact McNemar on the crossing transition:

| contrast | n | shifted_treatment | shifted_control | only_treatment | only_control | p_exact | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| implicit early - no ad | 54 | 7 | 8 | 5 | 6 | 1.000 | 1.000 |
| explicit early - no ad | 54 | 7 | 8 | 7 | 8 | 1.000 | 1.000 |
| implicit early - explicit early | 54 | 7 | 7 | 6 | 6 | 1.000 | 1.000 |

Destination shares among **shifts** on 2→3:

| to_genre | count_crossing | share_crossing | n | count_control | share_control |
| ---: | ---: | ---: | ---: | ---: | ---: |
| general_guidance_and_info | 6 | 0.429 | 14 | 6.000 | 0.750 |
| relationships_and_personal_reflection | 5 | 0.357 | 14 | 2.000 | 0.250 |
| academic_help | 3 | 0.214 | 14 | 0.000 | 0.000 |

## 3. Genre redirection

Early advertisements (primary labels): 108. Same genre 19 (0.176), unrelated shift 80 (0.741), ad-aligned shift 9 (0.083).

Conditional q = P(aligned | shifted) = 9/89 = 0.101.
Already in the advertisement genre at turn 2: 25 of 108.

```
Reassigning advertisement genres across the 108 early conversations, 20,000 permutations:

  lands on the advertisement genre  observed  11  chance  14.28  p=0.9240
  delta-tilde = 1                   observed   9  chance  10.46  p=0.7955

Alignment is no more common than coincidence, and in fact slightly less. The alignments that do occur are concentrated in the modal genre of both distributions (general_guidance_and_info 8, other_obscene_or_illegal 2, greetings_and_chitchat 1), which is what a shared marginal produces without any advertisement effect.
```

| ad_type | n | same | unrelated | aligned |
| ---: | ---: | ---: | ---: | ---: |
| implicit | 54 | 7 | 43 | 4 |
| explicit | 54 | 12 | 37 | 5 |

## 4. Moderation

Ad type (implicit vs explicit) is tested on the crossing estimand. Timing is **not** a treatment moderator: late ads have no following utterance. Late vs no-ad is the negative control.

### Bare utterance (primary)

Implicit early minus explicit early (hard shift):

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| implicit early - explicit early | 54 | 0.093 | -0.069 | 0.254 | 0.157 | 0.255 | 0.251 | 0.914 |

### Contextual (sensitivity)

Implicit early minus explicit early (hard shift):

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| implicit early - explicit early | 54 | 0.000 | -0.130 | 0.130 | 0.000 | 1.000 | 1.000 | 1.000 |

### Timing as negative control (primary labels, conversation N_shift)

| contrast | n | mean | ci_low | ci_high | dz | p_t | p_wilcoxon | p_holm |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| late pooled - no ad | 54 | -0.074 | -0.361 | 0.213 | -0.070 | 0.607 | 0.394 | 1.000 |
| implicit late - no ad | 54 | -0.018 | -0.347 | 0.310 | -0.015 | 0.910 | 0.942 | 1.000 |
| explicit late - no ad | 54 | -0.130 | -0.444 | 0.184 | -0.113 | 0.411 | 0.398 | 1.000 |

## 5. EEG × behavioural

Blocked. Not run.

Figures:

- `outputs/figures/direction/heatmap_overall_both.png`
- `outputs/figures/direction/heatmap_ad_vs_none_utterance.png`
- `outputs/figures/direction/heatmap_ad_vs_none_contextual.png`
- `outputs/figures/direction/heatmap_crossing_utterance.png`
- `outputs/figures/direction/heatmap_crossing_contextual.png`
- `outputs/figures/direction/redirection_stacked.png`
