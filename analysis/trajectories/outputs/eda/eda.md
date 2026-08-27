# Stage 1: exploratory analysis of genre trajectories

Descriptive only. No advertisement contrast is tested here.
The primary labelling is the bare utterance (Definition 1 read literally);
the contextual labelling appears only in the appendix section at the end.

## 1.1 Corpus

| quantity | value |
| --- | --- |
| Participants | 54 |
| Arms | crowd 36, lab 18 |
| Conditions per participant | 5 |
| Conversations | 270 |
| User utterances | 1080 |
| Turns per conversation | 4 |
| Transitions per conversation | 3 |
| Words per message, median [IQR] | 15 [8, 29] |
| Characters per message, median [IQR] | 77 [44, 153] |
| Response latency (s), median [IQR] | 49 [30, 75] |
| Genre space | 13 ThradBERT conversation-intent classes |

Arms are pooled throughout. Shifts per conversation do not differ between
the laboratory and crowd arms (see the variance table in 1.4).

## 1.2 Genre distribution

| genre | utterances | share | participants | mean_top_posterior | median_words |
| --- | ---: | ---: | ---: | ---: | ---: |
| general_guidance_and_info | 350 | 0.324 | 54 | 0.428 | 21 |
| relationships_and_personal_reflection | 193 | 0.179 | 53 | 0.451 | 13 |
| academic_help | 110 | 0.102 | 45 | 0.451 | 25 |
| other_obscene_or_illegal | 86 | 0.080 | 42 | 0.408 | 11 |
| personal_writing_or_communication | 72 | 0.067 | 37 | 0.443 | 9 |
| other | 71 | 0.066 | 39 | 0.367 | 11 |
| creative_writing_and_role_play | 43 | 0.040 | 31 | 0.425 | 23 |
| creative_ideation | 39 | 0.036 | 26 | 0.442 | 24 |
| greetings_and_chitchat | 35 | 0.032 | 24 | 0.456 | 9 |
| writing_and_editing | 34 | 0.031 | 25 | 0.376 | 16 |
| media_generation_or_analysis | 27 | 0.025 | 19 | 0.371 | 19 |
| purchasable_products | 19 | 0.018 | 15 | 0.360 | 13 |
| programming_and_data_analysis | 1 | 0.001 | 1 | 0.360 | 4 |

All 13 classes are used. `purchasable_products` reaches 19 of 1080 utterances despite every task being a shopping scenario.

## 1.3 Trajectory measures

Ceilings are imposed by the design: with T=4 turns there are at most 3
shifts, at most 4 distinct genres, entropy at most ln 4 = 1.386 nats, and
persistence at most 4. Diversity is **not** bounded by the 13 classes.

| measure | ceiling | condition | n | mean | sd | ci_low | ci_high | q25 | median | q75 | min | max |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Genre shifts N_shift | 3.000 | No ad | 54 | 2.481 | 0.771 | 2.271 | 2.692 | 2.000 | 3.000 | 3.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | Implicit early | 54 | 2.556 | 0.664 | 2.374 | 2.737 | 2.000 | 3.000 | 3.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | Explicit early | 54 | 2.407 | 0.714 | 2.212 | 2.602 | 2.000 | 3.000 | 3.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | Implicit late | 54 | 2.463 | 0.818 | 2.240 | 2.686 | 2.000 | 3.000 | 3.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | Explicit late | 54 | 2.352 | 0.781 | 2.139 | 2.565 | 2.000 | 3.000 | 3.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | All | 270 | 2.452 | 0.749 | 2.362 | 2.542 | 2.000 | 3.000 | 3.000 | 0.000 | 3.000 |
| Diversity D | 4.000 | No ad | 54 | 3.111 | 0.744 | 2.908 | 3.314 | 3.000 | 3.000 | 4.000 | 1.000 | 4.000 |
| Diversity D | 4.000 | Implicit early | 54 | 3.167 | 0.694 | 2.977 | 3.356 | 3.000 | 3.000 | 4.000 | 1.000 | 4.000 |
| Diversity D | 4.000 | Explicit early | 54 | 3.130 | 0.754 | 2.924 | 3.335 | 3.000 | 3.000 | 4.000 | 1.000 | 4.000 |
| Diversity D | 4.000 | Implicit late | 54 | 3.000 | 0.801 | 2.781 | 3.219 | 3.000 | 3.000 | 3.750 | 1.000 | 4.000 |
| Diversity D | 4.000 | Explicit late | 54 | 3.111 | 0.691 | 2.922 | 3.300 | 3.000 | 3.000 | 4.000 | 1.000 | 4.000 |
| Diversity D | 4.000 | All | 270 | 3.104 | 0.734 | 3.016 | 3.192 | 3.000 | 3.000 | 4.000 | 1.000 | 4.000 |
| Entropy H (nats) | 1.386 | No ad | 54 | 1.055 | 0.305 | 0.971 | 1.138 | 1.040 | 1.040 | 1.386 | 0.000 | 1.386 |
| Entropy H (nats) | 1.386 | Implicit early | 54 | 1.084 | 0.277 | 1.008 | 1.159 | 1.040 | 1.040 | 1.386 | 0.000 | 1.386 |
| Entropy H (nats) | 1.386 | Explicit early | 54 | 1.064 | 0.305 | 0.980 | 1.147 | 1.040 | 1.040 | 1.386 | 0.000 | 1.386 |
| Entropy H (nats) | 1.386 | Implicit late | 54 | 1.008 | 0.347 | 0.914 | 1.103 | 1.040 | 1.040 | 1.300 | 0.000 | 1.386 |
| Entropy H (nats) | 1.386 | Explicit late | 54 | 1.057 | 0.287 | 0.979 | 1.136 | 1.040 | 1.040 | 1.386 | 0.000 | 1.386 |
| Entropy H (nats) | 1.386 | All | 270 | 1.054 | 0.304 | 1.017 | 1.090 | 1.040 | 1.040 | 1.386 | 0.000 | 1.386 |
| Max persistence R | 4.000 | No ad | 54 | 1.519 | 0.771 | 1.308 | 1.729 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | Implicit early | 54 | 1.426 | 0.633 | 1.253 | 1.599 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | Explicit early | 54 | 1.574 | 0.690 | 1.386 | 1.762 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | Implicit late | 54 | 1.537 | 0.818 | 1.314 | 1.760 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | Explicit late | 54 | 1.630 | 0.760 | 1.422 | 1.837 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | All | 270 | 1.537 | 0.735 | 1.449 | 1.625 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |

Pooled across conditions, conversations average 2.45
shifts of a possible 3, visit 3.10 distinct genres of a possible 4
(78% of ceiling), and reach 1.05 nats of a possible 1.386
(76% of ceiling). 97.4% of conversations contain at
least one shift. Under this labelling a trajectory rarely repeats a genre.

## 1.4 Where the variance sits

Descriptive omnibus checks. These ask which design factor a measure varies
with at all; they are not advertisement tests.

| measure | factor | levels | kruskal_H | p | eta_squared |
| --- | --- | ---: | ---: | ---: | ---: |
| N_shift | Condition | 5 | 2.8944 | 0.5757 | 0.0085 |
| N_shift | Task | 5 | 4.6053 | 0.3302 | 0.0208 |
| N_shift | Arm | 2 | 0.0361 | 0.8492 | 0.0031 |
| N_shift | Session position | 4 | 2.2461 | 0.5229 | 0.0092 |
| N_shift | Participant (ICC) | 54 | nan | nan | 0.0665 |
| Entropy | Condition | 5 | 1.1649 | 0.8838 | 0.0067 |
| Entropy | Task | 5 | 2.5863 | 0.6293 | 0.0156 |
| Entropy | Arm | 2 | 1.1773 | 0.2779 | 0.0104 |
| Entropy | Session position | 4 | 4.0879 | 0.2521 | 0.0092 |
| Entropy | Participant (ICC) | 54 | nan | nan | 0.1110 |
| Max persistence | Condition | 5 | 2.7958 | 0.5926 | 0.0084 |
| Max persistence | Task | 5 | 4.6507 | 0.3250 | 0.0222 |
| Max persistence | Arm | 2 | 0.0324 | 0.8571 | 0.0033 |
| Max persistence | Session position | 4 | 2.1673 | 0.5384 | 0.0094 |
| Max persistence | Participant (ICC) | 54 | nan | nan | 0.0430 |

## 1.5 Transition structure

| quantity | value |
| --- | --- |
| Transitions | 810 |
| Self-transitions (diagonal mass) | 0.183 |
| Shift rate | 0.817 |
| Distinct genre pairs observed | 120 of 169 |
| Modal destination | guidance (0.273) |
| Top three edges | guidance→guidance 82; guidance→relationships 56; relationships→guidance 36 |

## 1.6 What the labelling can bear

This subsection is a property of the instrument and qualifies everything above.

| turn | utterances | median_words | q25_words | q75_words | junk_share | mean_top_posterior | distinct_genres |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 270 | 40 | 22 | 58 | 0.041 | 0.427 | 12 |
| 2 | 270 | 14 | 8 | 24 | 0.152 | 0.425 | 12 |
| 3 | 270 | 13 | 7 | 20 | 0.189 | 0.425 | 12 |
| 4 | 270 | 10 | 6 | 17 | 0.200 | 0.430 | 13 |

Logistic models for a fallback label, clustered by participant:

| model | term | beta | se | p |
| --- | --- | ---: | ---: | ---: |
| junk ~ turn | turn | 0.4317 | 0.0845 | 0.0000 |
| junk ~ turn + log(words) | turn | 0.3381 | 0.0933 | 0.0003 |
| junk ~ turn + log(words) | log_words | -0.2892 | 0.0855 | 0.0007 |

Messages shorten sharply across turns and the fallback classes absorb the
difference. Length explains part of it: `log(words)` enters the model
negatively and the turn coefficient shrinks once length is adjusted for.
It does not explain all of it: the turn term survives, and mean classifier
confidence is flat across turns, so the drift is not the model degrading.
Both halves belong in the write-up.

## Appendix: contextual labelling

| genre | utterances | share | participants | mean_top_posterior | median_words |
| --- | ---: | ---: | ---: | ---: | ---: |
| general_guidance_and_info | 755 | 0.699 | 54 | 0.482 | 15 |
| academic_help | 244 | 0.226 | 52 | 0.465 | 15 |
| relationships_and_personal_reflection | 69 | 0.064 | 23 | 0.409 | 23 |
| creative_writing_and_role_play | 8 | 0.007 | 3 | 0.299 | 23 |
| creative_ideation | 2 | 0.002 | 2 | 0.353 | 14 |
| writing_and_editing | 1 | 0.001 | 1 | 0.248 | 208 |
| personal_writing_or_communication | 1 | 0.001 | 1 | 0.334 | 22 |

| measure | ceiling | condition | n | mean | sd | ci_low | ci_high | q25 | median | q75 | min | max |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Genre shifts N_shift | 3.000 | No ad | 54 | 0.241 | 0.473 | 0.112 | 0.370 | 0.000 | 0.000 | 0.000 | 0.000 | 2.000 |
| Genre shifts N_shift | 3.000 | Implicit early | 54 | 0.389 | 0.685 | 0.202 | 0.576 | 0.000 | 0.000 | 1.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | Explicit early | 54 | 0.370 | 0.623 | 0.200 | 0.541 | 0.000 | 0.000 | 1.000 | 0.000 | 2.000 |
| Genre shifts N_shift | 3.000 | Implicit late | 54 | 0.574 | 0.815 | 0.352 | 0.797 | 0.000 | 0.000 | 1.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | Explicit late | 54 | 0.407 | 0.740 | 0.205 | 0.609 | 0.000 | 0.000 | 1.000 | 0.000 | 3.000 |
| Genre shifts N_shift | 3.000 | All | 270 | 0.396 | 0.681 | 0.315 | 0.478 | 0.000 | 0.000 | 1.000 | 0.000 | 3.000 |
| Diversity D | 4.000 | No ad | 54 | 1.222 | 0.420 | 1.108 | 1.337 | 1.000 | 1.000 | 1.000 | 1.000 | 2.000 |
| Diversity D | 4.000 | Implicit early | 54 | 1.315 | 0.507 | 1.176 | 1.453 | 1.000 | 1.000 | 2.000 | 1.000 | 3.000 |
| Diversity D | 4.000 | Explicit early | 54 | 1.352 | 0.588 | 1.191 | 1.512 | 1.000 | 1.000 | 2.000 | 1.000 | 3.000 |
| Diversity D | 4.000 | Implicit late | 54 | 1.444 | 0.604 | 1.280 | 1.609 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Diversity D | 4.000 | Explicit late | 54 | 1.315 | 0.543 | 1.167 | 1.463 | 1.000 | 1.000 | 2.000 | 1.000 | 3.000 |
| Diversity D | 4.000 | All | 270 | 1.330 | 0.537 | 1.265 | 1.394 | 1.000 | 1.000 | 2.000 | 1.000 | 4.000 |
| Entropy H (nats) | 1.386 | No ad | 54 | 0.142 | 0.270 | 0.068 | 0.216 | 0.000 | 0.000 | 0.000 | 0.000 | 0.693 |
| Entropy H (nats) | 1.386 | Implicit early | 54 | 0.185 | 0.296 | 0.104 | 0.266 | 0.000 | 0.000 | 0.562 | 0.000 | 1.040 |
| Entropy H (nats) | 1.386 | Explicit early | 54 | 0.203 | 0.331 | 0.113 | 0.293 | 0.000 | 0.000 | 0.562 | 0.000 | 1.040 |
| Entropy H (nats) | 1.386 | Implicit late | 54 | 0.264 | 0.340 | 0.171 | 0.356 | 0.000 | 0.000 | 0.562 | 0.000 | 1.386 |
| Entropy H (nats) | 1.386 | Explicit late | 54 | 0.181 | 0.307 | 0.097 | 0.265 | 0.000 | 0.000 | 0.562 | 0.000 | 1.040 |
| Entropy H (nats) | 1.386 | All | 270 | 0.195 | 0.310 | 0.158 | 0.232 | 0.000 | 0.000 | 0.562 | 0.000 | 1.386 |
| Max persistence R | 4.000 | No ad | 54 | 3.630 | 0.734 | 3.429 | 3.830 | 4.000 | 4.000 | 4.000 | 2.000 | 4.000 |
| Max persistence R | 4.000 | Implicit early | 54 | 3.556 | 0.769 | 3.346 | 3.765 | 3.000 | 4.000 | 4.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | Explicit early | 54 | 3.556 | 0.744 | 3.352 | 3.759 | 3.000 | 4.000 | 4.000 | 2.000 | 4.000 |
| Max persistence R | 4.000 | Implicit late | 54 | 3.333 | 0.911 | 3.085 | 3.582 | 3.000 | 4.000 | 4.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | Explicit late | 54 | 3.556 | 0.793 | 3.339 | 3.772 | 3.000 | 4.000 | 4.000 | 1.000 | 4.000 |
| Max persistence R | 4.000 | All | 270 | 3.526 | 0.793 | 3.431 | 3.621 | 3.000 | 4.000 | 4.000 | 1.000 | 4.000 |

| quantity | value |
| --- | --- |
| Transitions | 810 |
| Self-transitions (diagonal mass) | 0.868 |
| Shift rate | 0.132 |
| Distinct genre pairs observed | 16 of 169 |
| Modal destination | guidance (0.715) |
| Top three edges | guidance→guidance 522; academic→academic 144; academic→guidance 47 |

## Figures

- `eda/figures/eda_genre_distribution.png`
- `eda/figures/eda_measures_by_condition.png`
- `eda/figures/eda_transition_heatmap.png`
- `eda/figures/eda_turn_profile.png`
- `eda/figures/eda_example_trajectories.png`
- `eda/figures/eda_persistence.png`
- `eda/figures/eda_label_validity.png`
- `eda/figures/eda_appendix_contextual.png`
