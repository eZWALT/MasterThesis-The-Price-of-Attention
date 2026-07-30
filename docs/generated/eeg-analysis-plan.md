# What the EEG data can be used for

Scope: the laboratory arm of the conversational advertising study. Written 29 July
2026 from the production logs, the LSL marker implementation, and the local EEG
literature. This is a feasibility and design document, not a results document.

## The constraint that decides everything

Each participant sees **each ad condition exactly once**. The protocol runs five
conditions of four turns, and one advertisement is injected per ad condition. So
per participant there is:

| Quantity | Count per participant | Total at 15 lab participants |
|---|---|---|
| Ad-locked events | 4 (one per ad condition) | 60 |
| Ad events per condition | **1** | 15 |
| Turn-level reading/writing events | 20 each | 300 each |
| Rest baseline | 1 × 30 s | 15 |
| Continuous recording | ~35–110 min | — |

One trial per participant per condition has direct methodological consequences:

- **Event-related potentials are not viable as a primary measure.** ERP components
  are extracted by averaging tens of trials; a single trial per cell is dominated
  by noise.
- **Sustained spectral and time-frequency measures over multi-second windows are
  viable**, because they integrate power over time rather than relying on
  trial averaging.
- **The replication unit is the participant, not the trial.** Every ad-locked
  analysis reduces to one value per participant per condition, then compares those
  values across participants with paired methods.

Anything proposing single-trial classification of ad format or timing is
arithmetically impossible with this design.

## Tier 1 — Defensible primary uses

### 1. Ad-locked spectral response by condition

Time-lock to `ad_injected` — **not** `ad_displayed` — and compute band power change
relative to a pre-event window in the same conversation. See the marker audit below
for why: `ad_injected` is the only ad marker present, correctly labelled, and
semantically stable across all sessions and both formats.

- Measures: frontal midline theta (4–7 Hz), parieto-occipital alpha (8–12 Hz).
- Contrasts: inline versus labelled block; early versus late.
- Structure: one value per participant per condition, compared with a paired
  model or a mixed model with participant random intercepts.
- Interpretation: theta increase and alpha suppression are conventionally read as
  increased processing demand and increased visual/attentional engagement. They
  are **not** measures of trust or persuasion.

### 2. Interaction-state contrast as a positive control

Compare rest baseline against reading epochs against composing epochs, using
`turn_N_read` and `turn_N_write`.

This is the single most valuable non-headline analysis, because it is the only way
to demonstrate that the markers, the clock alignment, and the preprocessing chain
actually recover a known effect. Without it, a null ad-condition result is
uninterpretable — you cannot distinguish "advertising format does not modulate
neural response" from "the pipeline does not work".

With 20 epochs per state per participant, this analysis is well powered even at
the current sample.

### 3. Sustained condition-level state across the conversation

Average band power across each full condition window (`condition_start` to
`condition_conclusion_submitted`), normalised to the rest baseline.

- Gives five values per participant, including the no-ad condition.
- Answers whether a condition changes tonic engagement or load across the whole
  interaction, not just at the moment of exposure.
- Robust to onset timing uncertainty, which makes it the safest condition-level
  comparison available.

### 4. Matched no-ad control events

The no-ad condition contains no ad marker, so an ad versus no-ad neural contrast
requires a constructed comparison event: the assistant reply display at the
matched turn index in the no-ad conversation. This is legitimate, but only if
reply-display timing can be validated against the XDF stream. If it cannot, keep
the no-ad condition in the sustained analysis (Tier 1.3) and out of the
event-locked analysis.

## Tier 2 — Exploratory but publishable with caveats

| Analysis | Time lock | What it asks | Main caveat |
|---|---|---|---|
| EEG–self-report covariation | Ad onset | Does a participant's ad-locked response track their own rating of that condition? | Four or five points per participant; multilevel model, small effects |
| Pre-exposure brain state | Window before ad onset | Does the state at the moment of insertion predict the subsequent rating? | Directly relevant to the timing question, but only 60 events total |
| Frontal alpha asymmetry | Condition window | Approach versus withdrawal disposition | Weak and contested link to valence; report as one index among several |
| Engagement and cognitive-load indices | Condition window | Replicates the in-house precedent's feature set | Ratio measures inherit noise from both bands |
| Whole-scalp discovery | Ad onset | Unconstrained channel × time × frequency effects | Requires cluster-based permutation; discovery only |
| Inter-subject correlation | Reading window | Do participants show synchronised responses while reading the ad-bearing reply? | Reading durations differ; needs time-warping or fixed windows |

The pre-exposure analysis (row 2) is the most interesting of these, because it is
the only EEG measure that speaks to the placement question the thesis actually
poses: whether some conversational moments are better than others.

## Tier 3 — Not feasible with this dataset

| Proposal | Why not |
|---|---|
| Single-trial decoding of format or timing | One trial per participant per condition |
| Classical ERP components (P300, N400) as primary outcomes | Requires trial averaging; also requires a validated visual onset |
| Direct neural measurement of trust or persuasion | No EEG index has that interpretation; this would be the most damaging overclaim available |
| Predicting crowd-arm condition means from lab EEG | Four ad-condition means gives an effective sample of four |
| Eye-tracking areas of interest | The lab arm stores video, not gaze coordinates; no gaze pipeline exists in the repository |

## Prerequisites before any of this runs

None of the recordings are in the repository. `lab_subject_9` and
`lab_subject_10` contain only the events and export JSONL files. The recordings are
in Drive and the following gates must close first.

1. **Locate and mount the full-session recordings.** The eight pilot files in the
   repository span 2–17 minutes against sessions of 33–110 minutes, so they are
   partial and must not be analysed as if complete.
2. **Build an explicit mapping** from `lab_subject_N` to recording filename to
   `experiment_id`. No join key exists today; filename numbering is not sufficient
   evidence.
3. **Fit and verify clock alignment per participant** using the anchor-marker
   procedure below. The `timestamp` field has microsecond precision, so this is a
   solved problem provided the recording contains anchor markers.
4. **Use `ad_injected` as the ad time lock.** Do not use `ad_displayed`: it is
   absent for three participants, emitted only for labelled blocks in six, and
   quadruplicated where present.
5. **Validate any derived visibility estimate** against the participants who do
   have display markers, and report its error.
6. **Freeze preprocessing and run it blind to condition labels**: filter settings,
   re-referencing, bad-channel criteria, artifact rejection thresholds, and
   independent-component removal policy.

## Marker inventory — verified 29 July 2026

Counted directly from every lab session's events file. The whitelist that governs
what reaches LSL is in `core/modalities/eeg/__init__.py`.

| Marker | Coverage across 13 lab sessions | Usable for |
|---|---|---|
| `ad_injected` | **4 of 4 in every session**, correctly tagged by format | **Primary ad time lock** |
| `ad_displayed` | Unusable as a uniform lock — see era table | Format-specific validation only |
| `baseline_start` / `baseline_end` | All except `lab_subject_4_crowdfail` | Normalisation, quality control |
| `condition_start` | 5 of 5 in every session | Sustained condition windows |
| `turn_N_write` | 20 of 20 in every session | Composing onset, state contrast |
| `turn_N_read` | 20 in eras 1 and 3; **0 for participants 5–7** | Reading onset, stratify by era |
| `condition_conclusion_submitted` | All | Condition window end |
| `post_task_questionnaire_end` | All | Questionnaire block boundary only |
| `experiment_end` | All | Session close |

### Three marker eras

`ad_displayed` behaves differently across three code states, which is why it cannot
serve as the primary lock:

| Era | Participants | Build | `ad_displayed` behaviour |
|---|---|---|---|
| 1 | lab 1–3 | `unknown` | 4 events, both formats, but the `ad_mode` field is **empty**; fires ≈1.5 s after injection, mid-stream, before the reply event |
| 2 | lab 5–7 | `1.1.0-pilot1` | **Absent entirely**, along with `turn_N_read` and `ad_inserted` |
| 3 | lab 8–13 | `1.1.0-pilot1`, `2.2.0` | 8 events, **labelled block only — inline emits none**; four duplicate emissions per block ad; fires ≈0.5 s after the reply completes |

So `ad_displayed` is absent for three participants, format-incomplete for six,
quadruplicated where present, and untagged for three. `ad_injected` has none of
these problems.

### Verified timing relationships

`ad_injected` fires when generation begins: the interval from injection to the
reply event matches `llm_latency_ms` almost exactly (for example 3.069 s against
3.069 s, and 7.141 s against 7.141 s). The reply event marks completed rendering.

| Relationship | Era | Median | Range |
|---|---|---|---|
| `ad_injected` → `ad_displayed` | 1 | 1.57 s (inline), ≈1.4 s (block) | 1.24–2.02 s |
| `ad_injected` → `ad_displayed` | 3 | tracks `llm_latency_ms` | 2.47–7.76 s |
| `assistant_reply` → `ad_displayed` | 3, block | **0.48 s** | 0.45–0.73 s |

The era-3 reply-to-display interval is tight enough (about 0.28 s of spread) to
support a derived visibility estimate for labelled blocks.

## Offline reconstruction of event timing

The missing markers can be recovered offline, but the target should be a **derived
visibility estimate**, not the absent `ad_displayed` event. The `timestamp` field
carries microsecond precision — `unix_ts` is merely a coarse one-second copy — so
log times are exact enough to reconstruct from.

### Step 1 — Fit the clock mapping

Every era retains roughly 42 events that are both logged and whitelisted for LSL:
two baseline bounds, five condition starts, twenty writing onsets, four injections,
five conclusions, five questionnaire ends, and the session close. Match them to the
XDF marker stream by name and ordinal, then robustly fit

```
t_lsl = a + b · t_log
```

Expect a slope of essentially 1. The residual spread is the achievable precision
and should be well under 100 ms, because marker pushing is synchronous and inline.
Once fitted, **any** logged event can be projected into EEG time, including events
that were never pushed to LSL at all.

### Step 2 — Derive ad visibility

For every advertisement in every session:

- Labelled block: visibility ≈ reply timestamp + 0.5 s, using the era-3 calibration.
- Inline: the advertisement text appears progressively during streaming, so
  estimate onset ≈ injection + `llm_latency_ms` × (character offset of the ad text
  within the reply ÷ total reply length). Both the reply `content` and the ad title
  and product identifier are logged, so the offset is computable.

### Step 3 — Validate against the eras that have ground truth

Era 3 supplies twelve genuine block display markers to test the block rule. Era 1
supplies markers for both formats, though its different semantics and empty
`ad_mode` field make it a weak validation set. Report the resulting error
distribution rather than asserting accuracy.

### Step 4 — Choose measures that tolerate the residual error

If reconstruction is accurate to a few hundred milliseconds, that supports
sustained multi-second spectral windows. It does not support event-related
potentials — which the one-trial-per-cell structure already ruled out, so the two
constraints agree.

### Honest limits

- Inline onset is an estimate. Streaming is not exactly linear in characters, and
  no first-token timestamp is logged.
- A naive join of injections to replies by turn index mismatches occasionally; use
  the nearest reply after the injection instead.
- No reconstruction repairs a missing or partial XDF recording. At least some
  anchor markers must exist in the recording for step 1 to be possible.
- Every derived event must be documented as derived, with its estimator and
  measured error stated in the methods section.

## Participant inclusion

- `lab_subject_4_crowdfail` ran the crowd protocol and has no rest baseline. It is
  not an EEG participant.
- That leaves **13 candidate lab participants as of 29 July 2026**, including one
  session recorded that day.
- Participants 5–7 remain usable for injection-locked and sustained analyses; they
  are excluded only from reading-onset analyses.
- Add a prespecified data-quality exclusion based on artifact rate and channel
  loss, and report how many participants each analysis retains. The closest
  in-house precedent excluded roughly a quarter of participants from its spectral
  indices for signal quality, so expect attrition and plan for it.

## How EEG enters the statistical models

EEG does not replace the behavioural analysis; it adds a measurement layer to the
same condition structure.

```
eeg_feature ~ condition + (1 | participant)
```

For the incremental-value question — whether EEG explains anything beyond
behaviour — the comparison must hold the sample fixed:

```
behaviour-only model   on lab participants only
behaviour + EEG model  on the same lab participants
```

Comparing an all-participant behavioural model against a lab-only EEG model would
confound modality with sample and is not a valid test.

## Reporting rules

1. State the one-trial-per-cell structure explicitly in the methods. It is the
   main reason the EEG analysis is spectral rather than event-related.
2. Report the positive control before the condition contrasts.
3. Prespecify regions, bands, and windows; label everything else exploratory.
4. Report participant counts and exclusions per analysis, not once for the study.
5. Frame EEG as evidence about processing and engagement at exposure, converging
   with or diverging from what participants report and remember. Do not frame it
   as access to influence that participants cannot report.

## Bottom line

EEG is best used for three things here: showing that the pipeline recovers a known
interaction-state effect, testing whether integrated and labelled advertising
produce different sustained and ad-locked spectral responses within the same
person, and exploring whether the neural state at the moment of insertion relates
to how the advertisement is subsequently judged. It is not suited to single-trial
decoding, classical ERP components, or any claim of directly measuring trust or
persuasion.
