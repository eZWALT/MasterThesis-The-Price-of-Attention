# Genre trajectories

Implements Definitions 1-6 of the Theoretical Foundations
(`subsec:intent-trajectories`) on the tracked conversation logs.

## Pipeline

Run in order. Stage 1 needs the ThradBERT checkpoint; it is in the local
Hugging Face cache, so the offline flags below are enough.

```bash
HF_HUB_OFFLINE=1 python3 analysis/trajectories/build_trajectory_dataset.py
python3 analysis/trajectories/validate_trajectory_dataset.py
python3 analysis/trajectories/describe_trajectories.py
python3 analysis/trajectories/analyse_trajectories.py
HF_HUB_OFFLINE=1 python3 analysis/trajectories/classify_advertisements.py
python3 analysis/trajectories/eda_stage1.py
python3 analysis/trajectories/run_stages_2_4.py
python3 analysis/trajectories/run_exploratory.py
HF_HUB_OFFLINE=1 python3 analysis/trajectories/run_contextual_sweep.py
```

Stage 1 takes about 50 s (2,160 forward passes on CPU). Validation must
report 79 passed, 0 failed before any number is quoted downstream.

The build is deterministic: the model runs in eval mode and the label is an
argmax, so rebuilding reproduces the tables byte for byte (verified by
checksum). No seed is required.

## The genre space

`G` is the 13 conversation-intent classes of
`Thrad/thrad-bert-conversation-classifier`, the same model the live system
used to route retrieval.

## Two readings of `f_genre`, both carried

Every table has a `genre_source` column. Always say which one a number came
from, because they disagree substantively.

| | `utterance` (primary) | `contextual` (sensitivity) |
| --- | --- | --- |
| input | the bare message | task prompt + last 3 messages + current |
| matches the runtime log | 351/1080 | 1080/1080 |
| classes used | 13 of 13 | 7 of 13 |
| mean shifts per conversation, of 3 | 2.45 | 0.40 |
| mean diversity, of 4 | 3.10 | 1.33 |

Diversity counts distinct genres inside one trajectory, so with \(T=4\) turns its
ceiling is **4, not 13**. Bare therefore sits at 78% of ceiling, near-saturated,
which is the mirror image of the contextual reading's degeneracy rather than a
comfortable middle.

`utterance` is Definition 1 as literally written and is the **primary** source.
`contextual` reproduces `ConversationManager._classify_turn_intent` exactly,
including its 510-token budget split 50/35/15 across current message, history,
and task prompt; it is what the live system computed, so it is reported as a
sensitivity analysis.

Set `PRIMARY_SOURCE` in `analyse_trajectories.py`, `describe_trajectories.py`,
and `classify_advertisements.py` to switch. Two things change with it, so do
not switch one script alone:

- Which tests are valid. Under `utterance` 97% of conversations contain a
  shift, so the conversation-level "did it shift" dichotomy is degenerate and
  binary tests belong on the advertisement-crossing transition. Under
  `contextual` shifts are near-floor instead and the count needs an exact test.
- Whether task appears to dominate. It does under `contextual` (Kruskal
  H = 43.1) and does not under `utterance` (H = 4.6), because the task prompt
  sits inside the contextual classifier's own input.

The cost of the primary choice: the bare reading assigns
`other_obscene_or_illegal` to 86 benign shopping utterances, and those junk
classes grow from 4% of turn-1 utterances to 20% at turn 4 as messages get
shorter. `label_validity()` quantifies how much of that is length.

## Outputs

All under `outputs/` (flat; Bronze / Silver / Gold are logical zones, same
contract as EEG). Gold is the four tables the analysis reads. Silver
tables are provenance and kernels — do not test on them. Heatmaps rebuild
from Gold `transitions.csv`. Statistics (`eda/`, `stages_2_4/`,
`exploratory/`) are outside Gold. Lock:
`.agents/context/data-analysis/trajectories/2026-08-23-trajectory-medallion.md`.

| file | zone | grain | rows |
| --- | --- | --- | ---: |
| `utterances.csv` | Gold, turn | utterance × genre source | 2,160 |
| `transitions.csv` | Gold, turn | transition × genre source | 1,620 |
| `conversations.csv` | Gold, conversation | conversation × genre source | 540 |
| `advertisements.csv` | Gold, conversation | advertised conversation | 216 |
| `classifier_inputs.csv` | Silver | provenance only | 1,080 |
| `transition_matrices.csv` | Silver | faceted edge list | 715 |

Two rules hold everywhere. `conversation_id` is the spine and appears in every
table, so any two of them join on it. And the two readings of Definition 1 are
**rows, not columns**: every Gold table that is long on labelling carries a
`genre_source` of `utterance` or `contextual`, and every analysis begins by
selecting one. That is why the utterance table has 2,160 rows for 1,080
messages. `advertisements.csv` is the exception: one row per advertised
conversation, because \(g^{(a)}\) is the product title, not a turn label.

`utterances.csv` is the core. Alongside the message text and the 13-class
posterior it carries the transition *into* that utterance — `from_genre`,
`delta_in`, `js_in`, `tv_in`, `position_in`, blank at turn 1 — so the common
questions need no join. `latency_seconds` is the gap since the previous
message in the same conversation.

`conversations.csv` holds only the Definition 3-5 aggregates. It deliberately
does not store the per-turn genres: a label lives in exactly one place, and
anything that wants the pivot builds it from the utterance table (see
`turn_pivot()` in `classify_advertisements.py`).

`transition_matrices.csv` is the aggregated edge list, faceted three ways by
`facet_kind`: `all`, `ad_presence` (advertised against no-ad), and `condition`.
Each row gives `count`, `row_total` and a row-normalised `probability`; only
observed genre pairs appear.

Participants wrote multi-line messages, so `text` and
`classifier_input_contextual` contain embedded newlines. The fields are
properly quoted and any CSV reader handles them, but `wc -l` and other
line-oriented tools will overcount. Count rows with a CSV reader.

## Measures

Hard measures follow the definitions: `delta_k`, `n_shift`, `diversity`,
`entropy_nats`, `max_persistence`, and `ad_associated_shift`. The last is
missing for late conditions on purpose, because an advertisement in the reply
to turn 4 has no following utterance.

Analysis uses hard labels only. Columns `js_divergence` and
`total_variation` still exist on the Gold tables from the rebuild; they
are not tested or reported.

## Analysis notes

- Participant is the inferential unit, n=54. Both arms have conversations.
- Shift indicators are binary, so the primary test is **exact McNemar** on the
  advertisement-crossing transition, where each participant contributes one
  observation per condition. Mean differences are descriptive.
- Late conditions are a negative control, not a treatment arm.
- Task is counterbalanced unevenly (7 to 14 per cell) and belongs in any model
  even though it no longer dominates under the primary labelling.
- The positive-control battery is fixed by prevalence (every genre labelling at
  least 5% of utterances, Holm across them) rather than hand-picked.
- The genre-aligned subcase of Definition 6 needs a permutation null, because
  advertisements and utterances share a modal genre and some alignment is
  guaranteed by the marginals.

## Stages 2–4

Confirmatory family A on the crossing transition (2→3 vs no-ad 2→3).
Script: `run_stages_2_4.py`. Report and figures:
`outputs/stages_2_4/`. Canvas: `trajectory-stages-2-4.canvas.tsx`.
Headline: early pooled δ +0.046, Holm p = 0.94; like-for-like GEE OR
1.31 (p = .51); δ-tilde 9 vs 10.5 chance, p = 0.80; implicit − explicit
Holm p = 0.91; late negative control Holm p = 1.00. |dz| > 0.27 is
excluded. Depth (guidance 0.48→0.21, dz=−1.00) is the positive control.
The first-pass GEE OR 0.99 is retired (wrong estimand).

## Exploratory pass (not confirmatory)

`run_exploratory.py` → `outputs/exploratory/`. Four estimators family A
could not see, each with a design-based null that permutes condition
labels inside a participant's own five conversations.

- **Continuous redirection.** Definition 6 in posterior mass instead of
  argmax, as a difference-in-differences against the same genre in the
  same person's no-ad conversation: −0.024 [−0.088, +0.040]. A gain of
  more than 0.040 mass is excluded, against a 0.134 baseline. The late-ad
  placebo gives −0.028, the same size, so the small negative is turn
  drift and not an advertisement.
- **Heterogeneity.** Observed SD of the person-level response 0.469
  against a randomisation null of 0.493, p = .73. No hidden responders.
- **Omnibus.** Whole k=2 transition matrix, total variation 0.537 versus
  a null mean of 0.526, p = .44.
- **Priced slice grid.** 27 subgroups × 3 contrasts on hard δ = 81
  cells. Zero clear .05 where chance predicts 4.1, and the best cell
  anywhere has family-wise p = .79 against a max-|t| null.

Caveat worth carrying into the write-up: the advertised genre is 58%
`general_guidance_and_info` at mean confidence 0.40, so Definition 6 is
largely modal-genre-onto-modal-genre on this corpus.

## Stage 1 EDA

Deep descriptives live in `outputs/eda/`. Interactive recap:
`trajectory-eda-stage1.canvas.tsx` (repo copy; also in the Cursor canvases
folder). Headline: conditions are indistinguishable; bare labels sit at
~80% of the T=4 ceiling; fallback labels rise 4%→20% as messages shorten;
nothing — condition, task, arm, session, or person — explains the variance.

## Findings, in one paragraph (stages 2–3)

Advertisements do not move the genre trajectory: the transition crossing an
early advertisement is indistinguishable from the same transition without one
(hard shift +0.046, Holm p = 0.94;
exact McNemar p = 0.33; like-for-like logistic GEE odds ratio 1.31, p = .51),
with `|dz| > 0.27`
excluded, and the same holds under the contextual sensitivity. The measure is
not inert, because conversational depth moves it strongly
(`general_guidance_and_info` 0.478 to 0.211 across turns, dz = -1.00,
p < 0.0001). Definition 6's genre-aligned shift occurs 9 times in 108 early
conversations against 10.5 expected under permutation (p = 0.80), so it is at
chance rather than merely rare. And the class the pipeline relies on for ad
injection, `purchasable_products`, is assigned to 19 of 1,080 utterances and to
only 4 of 156 advertised products.
