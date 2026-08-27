# Advertisement genres and Definition 6's subcase

156 distinct products across 216 advertisement conversations, classified from the product title by the same model.

## What genre is an advertisement

| genre of the advertisement | distinct products | share |
| --- | ---: | ---: |
| general_guidance_and_info | 98 | 0.628 |
| academic_help | 15 | 0.096 |
| other | 10 | 0.064 |
| media_generation_or_analysis | 8 | 0.051 |
| creative_ideation | 7 | 0.045 |
| other_obscene_or_illegal | 5 | 0.032 |
| purchasable_products | 4 | 0.026 |
| personal_writing_or_communication | 3 | 0.019 |
| creative_writing_and_role_play | 2 | 0.013 |
| greetings_and_chitchat | 2 | 0.013 |
| relationships_and_personal_reflection | 1 | 0.006 |
| programming_and_data_analysis | 1 | 0.006 |

Mean top posterior mass on the advertisement titles: 0.402.

## Is the subcase reachable

Early advertisements (the only ones with a following utterance): 108.

- Advertisement genre equals the genre the user was already in (g^(a) = g_2): 25 of 108.
- Crossed by a genre shift (delta^(a) = 1): 89 of 108.
- Next utterance lands on the advertisement genre: 11 of 108.
- **delta-tilde = 1**: 9 of 108.

## Is the subcase more than coincidence

```
Reassigning advertisement genres across the 108 early conversations, 20,000 permutations:

  lands on the advertisement genre  observed  11  chance  14.28  p=0.9240
  delta-tilde = 1                   observed   9  chance  10.46  p=0.7955

Alignment is no more common than coincidence, and in fact slightly less. The alignments that do occur are concentrated in the modal genre of both distributions (general_guidance_and_info 8, other_obscene_or_illegal 2, greetings_and_chitchat 1), which is what a shared marginal produces without any advertisement effect.
```

Where the advertisement genre equals the genre the user is already in, a shift away from that genre necessarily lands elsewhere, so those conversations cannot contribute to delta-tilde. This is a structural consequence of retrieving advertisements from the user's own utterance.

