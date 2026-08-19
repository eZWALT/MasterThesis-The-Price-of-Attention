# Tang scoring vs ours (18 August 2026)

Sanity check after Katerina reported negative behavioural dimension
scores. Her scripts were not in this repo (`analysis/behavioural/` has
only notice/recall plots). Judged from Tang's public code and our plan.

## Tang does disclose the formulas

Repo: https://github.com/byron123t/chatbot-ads
File: `eval/parse_study_data.py` (reviewed in
`docs/generated/related-code-chatbot-ads.md`).

- Map labels to 1–7, then reverse with `invert_dict` = \(8-x\).
- Composite = mean of the retained items. That mean stays in \([1,7]\).
- They **dropped** items that did not hang with the others (commented
  out of both the mean and Cronbach).

Credibility in their code is **only** the two negative items, both
reversed (`Q2348_3`, `Q2348_7` = our `llm_false`, `llm_made_up`).
The positive item (`Q2348_1` = `llm_reliable`) is commented out.
Neutrality keeps the two positive items and drops `llm_opinionated`.
Convincingness drops one positive item. Helpfulness and Relevance keep
all three (one reversed each).

Manipulation / felt advertising are single items, not reversed.

They never produce a negative composite if you follow that file.

## What we planned (not Tang)

`2026-07-28-data-analysis-foundation.md` and Method:

- Credibility = mean(`llm_reliable`, reversed `llm_false`, reversed
  `llm_made_up`). That is the mix Tang abandoned.
- Manipulation = mean(`behaviour_pushing`, `behaviour_manipulate`).
- Trust (`personality_trust`) stays separate.
- Reverse = \(8-x\) on a 1–7 item. Composite still in \([1,7]\).

Compute Cronbach before freezing the three-item credibility mix.
Fallback is Tang's same-direction pair.

## If scores are negative, the script is not using either formula

Likely mix-ups:

- reverse as \(-x\) or \(1-x\) instead of \(8-x\)
- centre as \(x-4\)
- condition-minus-control difference (can be negative; say so)
- Cronbach's **alpha** (can be negative if items fight; not a person score)
- copying Tang's `likert_dict` 5-point remap
  (`'2': 3, '3': 4, '4': 6, '5': 7`) onto our already 1–7 numbers
