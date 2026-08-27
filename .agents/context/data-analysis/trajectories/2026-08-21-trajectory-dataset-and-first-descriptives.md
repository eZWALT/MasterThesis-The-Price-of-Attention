# Genre trajectories: dataset build and first descriptives

Date: 21 Aug 2026. Owner: Walter. Status: dataset DONE, schema LOCKED,
first-pass inference DONE, label source DECIDED. Open items are write-up
only (see the end).

JS (23 Aug evening): retired from the analysis. Hard labels only.
Do not quote the Jensen-Shannon row below as a confirmatory result.

Notation (23 Aug): the classifier is \(f_{\mathrm{genre}}\), not
\(f_\theta\). This note still says `f_theta` in places; read it as
\(f_{\mathrm{genre}}\). Lock:
`../../writing/2026-08-23-f-genre-notation.md`.

Implements Definitions 1-6 of Section 3 (`subsec:intent-trajectories`).

## Decision: `f_theta` is the bare utterance (Walter, 21 Aug)

The primary labelling is **the bare utterance**, which is Definition 1 read
literally. The deployed contextual labelling is the **sensitivity analysis**.
Section 3 therefore stands as written and does not need amending; what needs
adding is a disclosure that the live system classified a context window, so
the analysed genre is not the one that routed retrieval.

`PRIMARY_SOURCE = "utterance"` in `analyse_trajectories.py`,
`describe_trajectories.py`, and `classify_advertisements.py`. Flipping that
one constant in all three moves the whole report.

Also decided: `delta-tilde` stays in the paper, reported as specified but
empirically at chance.

### The flip improved three things and broke one test

Not what I expected when I recommended the other way round.

1. **The negative control now passes on the first test.** Under the contextual
   labels, implicit-late against no-ad came out at +0.333, Holm p = 0.029, and
   survived adjustment for task, which is structurally impossible and needed
   an exact-test rescue. Under the bare labels every late contrast is null on
   the parametric test itself (p = 1.00, means -0.02 to -0.13). The anomaly was
   an artefact of the contextual labels being near-floor.
2. **Task stops dominating.** Contextual: Kruskal H = 43.1, p < 0.0001 for
   task. Bare: H = 4.6, p = 0.33, with condition at H = 2.9 and nothing else
   significant. Task dominance was leakage — the task prompt sits inside the
   contextual classifier's input, so the label partly encoded which task the
   participant drew. Removing the prompt removes the effect. `swt_laptop_budget`
   also stops being degenerate, so the logistic GEE no longer drops a task for
   separation.
3. **The measures stop being degenerate.** Mean diversity goes from 1.33 to
   3.10 and mean entropy from 0.195 to 1.054 nats, so trajectory, diversity,
   and entropy become quantities with range rather than constants.
   **Correction (23 Aug):** an earlier version of this line read "3.10 of 13
   genres". That is wrong. Diversity counts distinct genres *within one
   trajectory*, so with \(T=4\) its ceiling is 4, and entropy's is
   \(\ln 4 = 1.386\). Bare therefore sits at 78% and 76% of ceiling. The bare
   reading is not comfortably mid-range; it is near-saturated in the opposite
   direction from contextual. Stage 1 states both ceilings explicitly.
4. **Broken:** the conversation-level "did it shift at all" comparison. 97.4%
   of conversations now contain at least one shift, so that dichotomy carries
   no variance. The binary tests moved to the advertisement-crossing
   transition, where each participant contributes exactly one observation per
   condition and McNemar applies cleanly. `exact_condition_table` now returns
   a degeneracy note alongside the table and says which reading is primary.

## Decisions taken with Walter before building

- Genre space `G` is the 13 ThradBERT conversation-intent classes. Not a
  product taxonomy, not a custom one.
- Classifier `f_theta` is ThradBERT itself
  (`Thrad/thrad-bert-conversation-classifier`, DistilBERT, 13 classes).
- Validation is judge-against-judge rather than hand labelling.
- Late (turn-4) advertisements contribute to global measures only.
- Statistical approach left open; dataset and descriptives first.

## Code and outputs

- `analysis/trajectories/build_trajectory_dataset.py` builds the dataset.
- `analysis/trajectories/validate_trajectory_dataset.py` asserts integrity;
  79 checks, all passing, including that all 18 lab `experiment_id`s join to
  the EEG gold table. Run it after any rebuild.
- `analysis/trajectories/describe_trajectories.py` writes descriptives and
  six figures.
- `analysis/trajectories/analyse_trajectories.py` writes the first-pass
  inference.
- Outputs in `analysis/trajectories/outputs/` (flat; zones are logical).
  **Gold:** `utterances.csv` (2,160), `transitions.csv` (1,620),
  `conversations.csv` (540), `advertisements.csv` (216).
  **Silver:** `classifier_inputs.csv` (1,080), `transition_matrices.csv`
  (715). Reports (`descriptives.md`, `inference.md`, `build_report.json`,
  `eda/`, `stages_2_4/`, `exploratory/`) are outside Gold. Lock:
  `2026-08-23-trajectory-medallion.md`.

Provenance is preserved: the message text is a column in the utterance table
and the exact contextual classifier input is kept in a separate file, so no
number in the analysis requires going back to the JSONL to interpret.

### Schema, rebuilt 21 Aug after Walter said the files were unreadable

The first cut grew one file per definition and ended up inconsistent: the
utterance table was wide on genre source while the derived tables were long,
`conversation_id` existed in only one of them, and the transition matrices
were computed inside the plotting script and thrown away. Rebuilt on two
rules, both chosen by Walter:

1. **`conversation_id` is the spine.** It is a real UUID from the logs, 270 of
   them, exactly one per participant × condition, and it now appears in every
   table. `utterance_id` and `transition_id` derive from it.
2. **Genre source is a row, never a column.** Every table carries
   `genre_source ∈ {utterance, contextual}`, so the utterance table has 2,160
   rows for 1,080 messages and every analysis starts the same way. The 26
   posterior columns collapsed to 13.

`utterances.csv` is the core and the only place a genre label is stored. It
carries the transition *into* each utterance (`from_genre`, `delta_in`,
`js_in`, `tv_in`, `position_in`, blank at turn 1) and a materialised
`latency_seconds`, which `analyse_trajectories.py` used to recompute on every
run. `conversations.csv` lost `genre_1..genre_4` and `delta_1..delta_3`;
anything needing that pivot builds it from the utterance table via
`turn_pivot()`. `transition_matrices.csv` is new: the aggregated edge list
with `count`, `row_total` and row-normalised `probability`, faceted by
`facet_kind ∈ {all, ad_presence, condition}`.

Every reported number was re-derived after the rebuild and is unchanged. The
validator grew from 51 checks to 79, the new ones being key uniqueness,
referential integrity across the three grains, and agreement between the
aggregates and the utterance table they come from.

Coverage is complete: 54 participants (18 lab, 36 crowd) x 5 conditions x 4
user utterances, no dropped conditions. This matches the behavioural roster
exactly, and unlike EEG the trajectory analysis runs at n=54.

## The two readings of Definition 1 (important)

Definition 1 says `g_k = f_theta(u_k)`, the bare utterance. The deployed
system did something else. `ConversationManager._classify_turn_intent`
classifies a concatenation under a 510-token budget:

    task participant_prompt (77 tokens) | last 3 user messages (178) | current message (255)

Both are computed and carried in a `genre_source` column.

- `contextual` reproduces the deployed pipeline. It matches the logged
  `intent_classified` labels **1080/1080 (100%)**, which is a hard check that
  the offline reimplementation is exact.
- `utterance` is Definition 1 as written. It agrees with the runtime only
  32.5% of the time.

They behave completely differently and the choice is consequential:

| | contextual | bare utterance |
| --- | ---: | ---: |
| classes used | 7 of 13 | 13 of 13 |
| top class share | 0.699 guidance | 0.324 guidance |
| mean shifts / conversation (max 3) | 0.40 | 2.45 |
| `other_obscene_or_illegal` | 0 | 86 |

The bare reading assigns `other_obscene_or_illegal` to 86 benign shopping
utterances and flips label on 82% of transitions against 13% for contextual.
The contextual reading is stable, but the task prompt is constant within a
conversation, so it anchors the genre and suppresses shifts. Neither is
neutral. Walter's call is the bare reading as primary; see the decision block
at the top for what that bought and cost.

### What the primary labelling can bear (must be disclosed)

Written by `label_validity()` into Section 0 of the inference report, because
choosing the bare reading makes this a load-bearing caveat rather than a
footnote.

Median message length collapses across turns — 40.5, 14, 13, 10 words — because
later utterances are elliptical once context is established. A single-utterance
classifier has correspondingly less to work with, and the junk classes absorb
it: `other` plus `other_obscene_or_illegal` rise from 4.1% of turn-1 utterances
to 20.0% at turn 4.

The honest reading needs both halves:

- Length matters. Junk labels go to shorter messages (median 11 versus 16
  words, p = 8e-8), and `log(words)` enters the model at -0.289, p = 0.0006.
- It is not only length. The turn term survives adjustment for length
  (+0.338, p = 0.0003), and mean classifier confidence is flat across turns
  (0.427, 0.425, 0.425, 0.430), so the drift is not the model degrading.

So part of the positive control is a length artefact and part is not. Say both.

## Findings

### `purchasable_products` never fires

The class the code annotates as "main signal for ad injection" is predicted
for **0 of 1,080** utterances under the deployed labelling, and 19 under the
bare reading. Across all raw logs it appears once in 2,457 classifications.
All five tasks are purchase-oriented shopping scenarios.

It is worse than that. Running the same classifier over the 156 distinct
advertised product titles, only **4 of 156** are labelled
`purchasable_products`; 98 are `general_guidance_and_info` and 5 are
`other_obscene_or_illegal`. Mean top posterior mass on the titles is 0.402.
The model does not recognise Amazon product listings as commercial, so the
class cannot serve as an ad-allocation signal on either side of the exchange.
This supports the Section 3 argument (via `xu2026ad`) that routing
conversational advertising through an intent label is harder than the
literature assumes.

### Definition 6's subcase, measured two ways

`delta-tilde` needs `g^(a)_k`, and the answer depends on how that is read:

- If `g^(a)` is taken to be `purchasable_products`, i.e. the commercial-intent
  reading, then under the primary labelling **14 of 270** conversations shift
  into it — and the no-ad condition contributes the most of any single
  condition (4, against 3, 3, 3, 1). Every exact paired contrast against no-ad
  is null (p = 0.375 to 1.00), and the labels are as frequent at turn 1, before
  any advertisement, as at turn 3. It is classifier noise, not induced
  commercial intent. Under the contextual labelling it is identically zero.
- If `g^(a)` is `f_theta(ad title)`, which is what the definition literally
  says, then `delta-tilde = 1` in **9 of 108** early-advertisement
  conversations.

The 9 is the number to be careful with, and it is why
`classify_advertisements.py` now runs a permutation null. Both the
advertisements and the utterances are dominated by the same modal genre, so
some alignment is guaranteed by the marginals alone. Reassigning the observed
advertisement genres across conversations (20,000 permutations, preserving
both marginals, destroying only the pairing) gives:

| quantity | observed | chance | p |
| --- | ---: | ---: | ---: |
| lands on the advertisement genre | 11 | 14.28 | 0.924 |
| `delta-tilde = 1` | 9 | 10.46 | 0.796 |

Alignment is *less* common than coincidence would produce, and 8 of the 11
alignments are `general_guidance_and_info` matching itself. So `delta-tilde` is
not merely small, it is at chance. That is a much stronger statement than "0 of
270" and it is the one to write.

A structural point that belongs in the limitations either way: because
advertisements are retrieved from the user's own utterance, the advertisement
genre coincides with the genre the user is already in for **25 of 108** early
conversations. In those, a shift away from the current genre cannot land on
the advertisement genre, so part of the design space is closed to
`delta-tilde` by construction. Contextual retrieval and the
genre-aligned-shift estimand are partly in tension.

Written by `analysis/trajectories/classify_advertisements.py` to
`outputs/advertisements.{md,csv}`.

### Advertisements do not move the genre trajectory, and the null is bounded

Only a turn-2 advertisement can be crossed by a transition, so the estimand
is transition (2 -> 3) in the early conditions against the same transition in
the no-ad condition, paired within participant. Every contrast is null:

| outcome | mean difference | 95% CI | dz | Holm p |
| --- | ---: | ---: | ---: | ---: |
| hard shift | +0.0463 | [-0.082, +0.174] | +0.10 | 0.94 |

Under the exact paired test on the crossing transition, which is the primary
reading for a binary outcome, implicit early against no-ad is 11 versus 6
discordant pairs, p = 0.332, Holm 0.997; explicit early against no-ad is 8
versus 8, p = 1.00. The logistic GEE puts the advertisement odds ratio at 0.99,
p = 0.98.

The interval excludes `|dz| > 0.27`, so this is a bounded null rather than an
absence of evidence: medium effects are ruled out, small ones are not.

Contextual sensitivity: same conclusion, all Holm p = 1.00, point estimates
-0.019 rather than +0.046. The sign flips between labellings and neither is
distinguishable from zero, which is the useful way to report it.

### The measure works, which is what makes the null meaningful

Conversational depth is a positive control, since it happened in every
conversation. The battery is fixed by prevalence rather than hand-picked: every
genre labelling at least 5% of utterances, Holm across them. Under the primary
labelling that is six genres and five of them move:

| genre | turn 1 | turn 4 | dz | Holm p |
| --- | ---: | ---: | ---: | ---: |
| `general_guidance_and_info` | 0.478 | 0.211 | -1.00 | <0.0001 |
| `other_obscene_or_illegal` | 0.019 | 0.111 | +0.57 | 0.0015 |
| `other` | 0.022 | 0.089 | +0.48 | 0.0044 |
| `personal_writing_or_communication` | 0.048 | 0.119 | +0.38 | 0.0186 |
| `academic_help` | 0.130 | 0.078 | -0.25 | 0.151 |
| `relationships_and_personal_reflection` | 0.152 | 0.178 | +0.11 | 0.444 |

So the instrument detects a large effect of conversational depth and nothing
for advertisements, which is a much stronger claim than an unqualified null.

The caveat is unavoidable and is why the length diagnostic above exists: two of
the five moving genres are the junk classes, so the control is partly detecting
the classifier running out of context on short later-turn messages. The
declining `general_guidance_and_info` at `dz = -1.00` is the part that is not
plausibly an artefact, and it is the one to lead with.

Contextual sensitivity: three genres clear 5% prevalence and all three move —
`academic_help` -0.76, `general_guidance_and_info` +0.31, `relationships`
+0.36, Holm p 0.0000 to 0.029. The control passes under either labelling.

### Two classifier-free outcomes agree (exploratory)

Because the labels are noisy it is worth checking measures that need no
classifier at all. The turn-3 message is the one written after an early
advertisement:

| outcome | early ad | no ad | difference | dz | p |
| --- | ---: | ---: | ---: | ---: | ---: |
| message length | 15.63 words | 15.15 | +0.48 | +0.05 | 0.562 |
| latency to write it | 66.9 s | 65.3 | +1.6 | +0.03 | 0.106 |

Both null, and both null in the late-condition negative control too. Median
latency does fall across turns (56, 49, 39 s), so the measure is live. Four
independent outcomes — hard genre shift, posterior divergence, message
length, and response latency — therefore converge on the same conclusion:
an early advertisement leaves no detectable trace in the user's next turn.
These two are exploratory; they are not part of Definitions 1-6.

### The negative control passes cleanly

Late conditions cannot carry an effect: with T=4 and the advertisement in the
reply to turn 4, all four utterances precede it. Under the primary labelling
every contrast is null on the parametric test — late pooled against no-ad
-0.074, implicit late -0.019, explicit late -0.130, all p = 1.00 after Holm —
and the same for mean Jensen-Shannon divergence.

This is where the labelling choice paid off. Under the contextual labels the
same comparison flagged implicit late at +0.333, Holm p = 0.029, surviving
adjustment for task, which is structurally impossible and had to be argued away
with an exact test. That anomaly was a consequence of shifts being near-floor
under the contextual labels (42 of 54 no-ad conversations contained none), which
makes a 0-3 count a poor fit for a continuous test. It does not arise under the
primary labelling.

The mirror-image problem does arise, though: 97.4% of conversations now contain
at least one shift, so the conversation-level "did it shift" dichotomy is
degenerate and is reported for completeness only. Binary tests belong on the
crossing transition.

### Task dominance was classifier leakage, not a design property

Under the primary labelling nothing dominates. Kruskal on shifts per
conversation: task H = 4.6, p = 0.33; condition H = 2.9, p = 0.58; session
position H = 2.3, p = 0.52; arm H = 0.04, p = 0.85. Mean shifts sit between
2.30 and 2.57 across all five tasks.

Under the contextual labelling task looked overwhelming — H = 43.1, p < 0.0001,
with `swt_laptop_budget` at exactly 0.000 shifts in all 54 conversations, which
separated the logistic likelihood and forced the regression helper to drop it.
That was leakage: the task participant prompt sits inside the contextual
classifier's input, so the label partly encoded which task the participant drew
rather than what they wrote. Remove the prompt and the effect goes with it.

Worth stating in the paper. It is a concrete instance of a deployed intent
classifier's own context window manufacturing an apparent effect, which is on
theme for the Section 3 argument about routing advertising through intent
labels. Task is still counterbalanced unevenly (7 to 14 per cell), so keep it
in any model regardless.

## Log-scheme notes for whoever extends this

- Condition brackets are named `condition_start`/`condition_end` in the newer
  scheme and `condition_started`/`condition_complete` in the older one
  (crowd_subject_1 to 5). Handling only the newer pair silently loses 5
  sessions, i.e. 25 conversations.
- Condition and task come from the condition-start payload. Do not use
  `ad_mode` on `ad_inserted`: it is empty in roughly 43% of sessions.
- The warm-up conversation shares `trial_index` with the first condition, so
  attribute utterances by the condition bracket, not by trial index.
- `crowd_subject_1` has one `worker_id_set` record split across two physical
  lines by a literal newline. It is unparseable and carries no
  conversational content; the builder counts and skips it.

### The trajectories have structure, it just is not advertisement structure

Under the contextual labelling, row-normalised transition matrices are strongly
diagonal and nearly identical with and without advertisements:
`general_guidance_and_info` retains 0.97 in the no-ad condition and 0.92 with
advertisements, `academic_help` 0.77 and 0.72, `relationships` 0.78 and 0.74.
Almost everything that does leave a genre goes to `general_guidance_and_info`
(0.22 to 0.24 from both other states), which therefore behaves as an attractor.

The drift shape differs sharply between labellings and it took the length
analysis to explain why. Contextual drift from a conversation's own opening
genre rises monotonically (0.148, 0.219, 0.252 at turns 2, 3, 4), which is what
progressive drift looks like. Bare drift jumps to 0.789 at turn 2 and then stays
flat (0.785, 0.826).

That step at turn 2 is not random relabelling, which is how I first read it. It
coincides exactly with the collapse in message length, from a median of 40.5
words at turn 1 to 14 at turn 2. Turn-1 utterances are long, self-contained
task framings that a single-utterance classifier handles well; everything after
is elliptical. So the step is the classifier losing its footing once the user
stops restating context, and the flatness after turn 2 is consistent with that
rather than with drift. This is the same mechanism as the junk-class growth in
Section 0 and it should be described once, in the Limitations, covering both.

The advertisement null is robust to the labelling choice: null under both, with
the point estimate changing sign (+0.046 bare, -0.019 contextual) and neither
distinguishable from zero.

### The classifier is not confident, which matters for the argmax

Top posterior mass over 13 classes averages 0.427 for the primary bare labels
and 0.471 for the contextual labels (median 0.478, range 0.216 to 0.634), and
65% of contextual labels sit below 0.50.
Chance is 0.077, so the model is clearly informative, but the winning class
is frequently a near-tie with the runner-up. Any measure defined on the
argmax alone inherits that instability, which is the main argument for
carrying the posterior-based companions below and for not over-reading a
single hard label.

## Soft-label companion measures

Because the hard shift only moves when the argmax changes, every transition
also carries the Jensen-Shannon divergence and the total-variation distance
between the consecutive 13-class posteriors. These respond to any
redistribution of mass, are bounded (JS by ln 2), and are the more sensitive
test. They agree with the hard-shift null and tighten it.

## Open questions for Walter

1. ~~Which reading of `f_theta` is primary.~~ DECIDED 21 Aug: bare utterance
   primary, contextual as sensitivity. See the decision block at the top.
2. ~~Whether to report `delta-tilde`.~~ DECIDED 21 Aug: keep it, report it as
   specified but at chance (permutation p = 0.80).
3. Whether the write-up leads with the bounded null plus positive control
   (recommended) or with the descriptive trajectory structure.
4. Section 5.8 has a table row and a sentence waiting for this family. The
   statistical content is now settled enough to fill in: participant as the
   unit, n = 54, the bare-utterance labelling as `f_theta` with the deployed
   contextual labelling as a stated sensitivity, exact paired tests on the
   advertisement-crossing transition for binary outcomes, Jensen-Shannon
   divergence as the continuous companion, Holm within family, task in any
   regression, and a permutation null for the genre-aligned subcase.
5. Section 3 needs one added sentence, not an amendment: Definition 1 is
   correct as written, but the deployed system classified a context window, so
   the paper must say that the analysed genre is not the one that routed
   retrieval. The Limitations also need the length artefact from Section 0 of
   the inference report.
