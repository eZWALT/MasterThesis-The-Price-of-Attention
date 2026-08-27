# Experiment flow design — assumptions for Methods §Flow Design

Date: 25 August 2026.
Thesis hole: `chapters/models.tex` subsection **Flow Design**
(`sec:methods:study-design`) is an empty `\item`. Walter is writing it.
Do not push LaTeX from this note until he asks.

**Source of truth is the live state machine**, not stale docstrings,
not leftover survey lists in `surveys.py`, and not the consent/debrief
cover-story wording if they disagree.

```text
src/project/core/experiment/controller.py   # screen lists + advance()
src/project/core/config.py                  # STUDY_SKIP_SCREENS, consent, turns
src/project/core/experiment/surveys.py      # items actually rendered
src/project/core/ui/screens.py              # what the participant sees
src/project/core/ui/participant.py          # skip = auto-advance, no render
src/project/docs/workflow_b.md
src/project/docs/participant_flow/participant_flow.py
src/project/docs/architecture/README.md     # figure ↔ SCREEN_* map
```

Figures: `figures/workflows/flow_lab.pdf` and `flow_crowd.pdf` in the
thesis. The four phase panels (Onboarding / Condition loop / Measures /
Close-out) are **presentational**. The controller has three stages:
`_PRE_CONDITION_SCREENS`, `_CONDITION_SCREENS` × 5,
`_POST_CONDITION_SCREENS`.

---

## Live screen sequence

```text
consent
  → [lab: baseline 30 s] | [crowd: prolific_id]
  → warmup_chat                    # 2 turns, no ads, not a condition
  → [ condition_intro
      → condition_chat             # 4 turns, ≤ 1 ad at turn 2 or 4
      → condition_conclusion       # findings, ≤ 256 chars
      → post_condition_survey      # 22 Likert, 3 sections
    ] × 5
  → ads_recall_interpretation      # 4 steps, ad conditions only
  → ocean                          # BFI-10
  → demographics
  → [crowd: validation]            # pick 5 of 10 tasks
  → deception_disclosure
  → done
```

Arm difference is **only** `STUDY_SKIP_SCREENS` (`config.py`):

| Arm | Shown extra | Auto-skipped (no render) |
|---|---|---|
| lab | `baseline` | `prolific_id`, `validation` |
| crowd | `prolific_id`, `validation` | `baseline` |

Skipped screens still emit `screen_skipped` and `advance()`. EEG/LSL
recording for the lab arm is session-wide (figure title), not a screen.
The 30 s baseline is rest / stillness, not the whole recording.

Turns are fixed: `MIN_TURNS_PER_TRIAL = MAX_TURNS_PER_TRIAL = 4`.
The “I've finished” button appears at turn 4. `EXIT_N_TRIALS = 5`
(sidebar early-exit exists in code; finished \(N=54\) completed all five).

Counterbalancing (`build_condition_plan`):

1. Five tasks, Latin-square rotated by `cb_group` or `hash(pid)`.
2. Five conditions shuffled **independently**.
3. Zip, so task identity is not confounded with condition across people.
4. Plan is written into `session_started`.

Warm-up task id `swt_new_hobby_lifestyle`, 2 turns, casual prompt, no
ads, **not** in the condition plan and **no** post-chat Likert.

---

## Why the order is this order

These are the assumptions to write. Each is a bias the protocol is
trying not to bake into the ratings.

### 1. Cover story until the last screen

Consent title is “User Study: AI Interaction”. Body: interact with an
LLM to improve decision-making, then note results; after each task,
brief questionnaires about **how the system behaves**. Duration 30–60
min. Ads are not named.

Debrief (`DECEPTION_DISCLOSURE_TEXT`) tells them the primary focus was
advertising, that deception was used so they would not hunt for ads or
treat the chatbot as an adversary, that products were not real
sponsorships, and that they may type `Withdraw` and still be paid.

**Trap:** the debrief also says they were “studying the viability of
creating personalities for AI”. Live consent does **not** say that. Do
not write a personality cover story unless Walter confirms it was
spoken in the lab script outside Streamlit. Write: participants were
not told the study was about advertising until debrief.

### 2. Warm-up before any rated conversation

Interface, streaming, and turn-taking are practiced on a 2-turn chat
with no ads and no survey. First Likert is therefore not also a first
use of the UI. Warm-up is excluded from Gold condition tables.

### 3. Lab baseline before the loop, not between conditions

30 s sit-still (`BASELINE_INSTRUCTION`) after consent, before warm-up.
Gives EEG a rest epoch without inserting a physiological ritual
between advertised conditions (which would itself be a condition).
Crowd replaces this slot with Prolific ID so the state machine stays
one list.

### 4. Independent-conversation warning at every briefing

`TASK_CONTEXT_WARNING` (yellow box on `condition_intro`):

- Each conversation is independent; “responses may be generated using
  different AI assistant models”; evaluate each interaction separately.
- Interact naturally; short “ok” spam / copy-paste may be flagged.
- Inattentive responses may withhold payment (crowd-facing language;
  shown to both arms).

**Assumptions:** (a) carry-over as *one* agent with memory would
confound the five within-person ratings; (b) planting “different
models” gives an alternative explanation for condition differences
other than ads; (c) quality language is for crowd, not a lab exclusion
rule (unfocused stays if instruments were completed).

### 5. Findings **before** the post-condition questionnaire

`condition_conclusion` is free text ≤ 256 characters, task prompt
re-shown, then Submit. Only then the 22-item survey.

**Assumptions:** (a) the Likert is about the whole condition, including
the participant’s own wrap-up; (b) writing “what I decided” before
“did I notice a brand / sponsored button” keeps the findings from
being rewritten as an ad-detection essay; (c) the findings are the
prompt-cued terminal complement in trajectory Methods, not a second
trust scale.

### 6. Post-condition survey: quality first, notice second, manipulation last

Three **gated** sections (must finish 1 to see 2, 2 to see 3). Fixed
item order, not shuffled. 7-point, 1 = strongly disagree. Adapted from
Tang et al. *Ads that Talk Back* (IMWUT 2025); `docs/generated/related-code-chatbot-ads.md`.

| Section | UI label | Rated items | Job |
|---|---|---|---|
| 1 | Evaluation | 15 | Assistant quality **before** any ad cue |
| 2 | Personality | 5 | Trust / influence, then **notice** |
| 3 | Behaviours | 2 | Commercial pressure **after** notice |

**Section 1** (`POST_CONDITION_LLM_ITEMS`), presentation order:

`llm_reliable`, `llm_helpful`, `llm_made_up`, `llm_changed_mind`,
`llm_not_useful`, `llm_neutral`, `llm_false`, `llm_addressed`,
`llm_impartial`, `llm_suggestions`, `llm_opinionated`, `llm_not_aid`,
`llm_skeptical`, `llm_relevant`, `llm_convincing`.

Planned composites (Methods DVs / analysis foundation; not estimated):

- Credibility = mean(`llm_reliable`, reversed `llm_false`, reversed `llm_made_up`).
- Direct trust = `personality_trust`, **not** folded into credibility.

**Section 2** Likert (all five are radios, not open-only):

- `personality_trust` — “I felt I could trust the chatbot.”
- `personality_influence` — approach to handling tasks.
- `personality_changed_mind`.
- `personality_brands` — mentioned products or brands.
- `personality_sponsored` — noticed or clicked sponsored buttons.

Optional text areas exist in code (`SHOW_OPTIONAL_QUESTIONS`) but
**default is off** (`SHOW_OPTIONAL` unset). Production participants
did not see the elaboration boxes unless that env was set. Do not
write “22 Likert plus five open fields” as the administered
instrument unless Walter confirms SHOW_OPTIONAL was on.

**Section 3:**

- `behaviour_pushing` — pushing or marketing content.
- `behaviour_manipulate` — steer my choice rather than neutrally assist.

**Why this order:** asking notice or manipulation first would recode
the whole conversation as advertising and then contaminate trust /
helpfulness. Brand mention is **not** advertisement detection (it
fires under \(a^{\emptyset}\) too). Sponsored-button is the notice
item that tracks \(\lambda\). See
`../data-analysis/behavioral/2026-08-18-ad-notice-and-cued-recall.md`.

### 7. Cued recall after **all five** conditions, not after each

Four steps, **ad conditions only** (`no_ads` has no recall step).
Order = order those four appeared in *this* participant’s plan, not a
fixed format order. Each step **shows the ad again** (title, text,
image, task, and for implicit the conversation excerpt with the
product name highlighted), then:

- `recall_memory` — “I feel I remember this content well.”
- `recall_trust_shift` — “After seeing this content, I felt I could trust the chatbot overall.”
- `recall_reaction` — open text (required in the renderer).

**Assumptions:** (a) re-showing the ad inside the condition loop would
teach later conditions what to look for; (b) this is **cued
self-report**, not objective recognition — Methods already says so;
(c) there is no \(a^{\emptyset}\) recall step, so recall cannot be
contrasted with no-ad the way notice can.

**Trap:** `render_ads_recall` docstring still says “7 Likert”. Live
list is 2 Likert + 1 open. Architecture README already flags this.

### 8. BFI-10 after recall, not before the loop

10 items, 5-point, Rammstedt & John 2007. Stem: describe yourself as
you generally are **now**. Reprinted in thesis `app:bfi10`.

**Assumptions:** (a) traits are moderators of the battery (Goal 2),
not inputs to \(a_k\) or \(\phi\) — \(\phi\) stays session-level;
(b) administering BFI **before** the chats would make the session look
like a personality study and would sit on the clock during cap-fit
anyway; (c) administering it **between** conditions would be a
condition; (d) after recall, the trait ratings cannot change the
already-logged post-condition composites. Do not cluster participants
into types.

BFI-44 exists in code (`?bfi=44`). Production default is `"10"`.

### 9. Demographics after BFI

Select items always shown: sex, education, chatbot familiarity,
frequency. Age and occupation are the optional text fields and follow
`SHOW_OPTIONAL` (default hidden). Every finished participant left the
post-experiment age item blank in the Results sample section — consistent
with optional/hidden.

**Assumption:** framing the session as a demographics / OCEAN study
during the chats would change how people talk to the assistant.
Collecting them at the end cannot change condition ratings. Thesis
Methods currently mentions an “intake questionnaire” while the EEG
cap is fitted — that is **lab procedure outside Streamlit**. Streamlit
demographics are the post-loop screen. Do not merge the two without
checking the lab script.

### 10. Crowd validation after demographics, before debrief

Pick exactly 5 of 10 task titles (5 real + 5 distractors from
`TASK_CATALOG`). `validation_failed` if mistakes ≥ 2. Lab skips this
(experimenter present). It is an attention check, not a second
notice instrument.

### 11. Debrief last

Until this screen, advertising has not been named by the protocol
(explicit banners are labelled in the UI; the *study* is not).
Withdrawal is still paid. Nothing after this except `done`.

---

## Instruments defined in `surveys.py` that are **not** in the live flow

Do not write these into Flow Design as administered:

- `GLOBAL_EVAL_*`, `ADS_AWARENESS_*`, `ADS_PERCEPTION_*`,
  `LLM_EVAL_CATEGORIES` (duplicate of section 1 under other ids),
  `GODSPEED_*`, `POST_TRIAL_*`, `FINAL_SURVEY_*`,
  `POST_CONDITION_ITEMS_LEGACY`.

`SCREEN_INSTRUCTIONS` / `render_instructions` exists; the controller
starts at `consent`, not that screen.

---

## What Methods already says (do not contradict)

`models.tex` already has: five within-subject conditions; Latin-square
tasks × independent condition shuffle; findings ≤ 256 chars; 22-item
Likert in three sections; cued recall for four ad conditions; BFI-10
after the loop; crowd validation; \(\theta\) co-varies with \(\lambda\);
BFI is not an input to \(a_k\). Flow Design should explain **why the
screens sit in that order**, not repeat the factorial design.

Suggested bullet spine for the empty `\item` list:

1. Cover story / ads unnamed until debrief.
2. Warm-up isolates UI learning from the first rating.
3. Baseline once, not between conditions.
4. Independence warning (carry-over + “maybe different models”).
5. Findings before Likert.
6. Likert: quality → notice → manipulation (gated sections).
7. Cued re-display of ads only after all five conditions.
8. BFI-10 and demographics after outcomes (moderators, not primes).
9. Crowd validation; debrief last.

---

## Thesis vs paper

Flow Design is **thesis Methods** (`chp:methods`). Paper Methods may
get a shorter version later. Trajectories stay thesis-only. Do not
put H1–H3 or “what this means for ads” in this subsection.

Related: `../data-analysis/behavioral/2026-08-18-ad-notice-and-cued-recall.md`,
`../data-analysis/2026-07-28-data-analysis-foundation.md` (composites,
task + position in the mixed model because order is randomised but
not balanced perfectly).
