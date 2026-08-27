# Trajectory analysis direction (initial)

Date: 23 Aug 2026. Owner: Walter. Status: DIRECTION LOCKED, revisable as
the analysis advances. ChatGPT's long protocol was discussed and is **not**
adopted; only the five stages below are standing.

Implements Definitions 1–6 of Section 3. Primary labelling is the bare
utterance; contextual is sensitivity. Dataset lock:
`2026-08-21-trajectory-dataset-and-first-descriptives.md`.

## The five stages

1. **Descriptive / EDA.** Shift rates, diversity, entropy, persistence,
   transition heatmaps, turn profiles. All descriptives. No inferential
   claims.
2. **Advertisement effects on genre dynamics.** Do ads change shifts, and
   *to what*? Tests. The estimand is the transition that can actually
   cross an advertisement.
3. **Genre redirection.** Did the next utterance land on the advertised
   genre? Definition 6 / \(\tilde{\delta}^{(a)}\).
4. **Moderation.** Ad type (implicit vs explicit): yes. Timing as a
   treatment moderator: **no** — a turn-4 ad has no following utterance,
   so late is a negative control, not a second timing level of the same
   estimand.
5. **Exploratory associations with EEG and behavioural.** **Blocked.**
   Do not start until Walter opens it. This stage **is** science Goal 5
   in `../2026-08-23-goal-list.md`: all four combos (behaviour × EEG,
   behaviour × trajectory, trajectory × EEG, three-way), not a single
   merge. Association, not mediation. Lab \(n=18\) wherever EEG is in.

## Design constraints any later plan must respect

- Five conditions, repeated measures: no-ad, implicit-early, implicit-late,
  explicit-early, explicit-late. Paper names implicit / explicit; log keys
  stay `inline_*` / `block_*`.
- \(T=4\), so three transitions. Only turn-2 ads can be crossed. Late
  conditions contribute to global descriptives and to the negative
  control, not to \(\delta^{(a)}\) or \(\tilde{\delta}^{(a)}\).
- Inferential unit is the participant, \(N=54\). Binary tests sit on the
  advertisement-crossing transition, one observation per participant per
  condition. Conversation-level "did it shift at all" is degenerate under
  the primary labelling (97.4%).
- There is no mid-conversation timing, no eye tracking, and no
  Travel/Shopping/Food genre space. \(G\) is the 13 ThradBERT classes.
- Stage 5, when opened, is laboratory-only for EEG (\(n=18\)) and an
  association, not a mediation claim.

## What the first pass already covers

Most of stage 1, the crossing-transition tests of stage 2, and the
permutation null of stage 3 are already in `outputs/inference.md`,
`descriptives.md`, and `advertisements.md`. Remaining work is to finish
those stages as a paper-shaped family, not to rebuild the dataset.

Open write-up items from 21 Aug (lead sentence, §5.8, one §3 disclosure)
stay write-up items. They are not new analysis.
