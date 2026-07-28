# Query Parameter Guide

Sessions are configured entirely from the URL — craft a link, send it to the
participant, change nothing in the code. Invalid or out-of-range values are
silently ignored and fall back to config defaults.

Parsed by `core/experiment/query_params.py`; defaults come from
`core/config.py`.

---

## Routing

| Param | Values | Effect |
|---|---|---|
| `dev` | `true` \| `1` \| `yes` | Developer free-chat mode |
| `dev` | `flow` | Participant flow with skip buttons and debug panels |
| `dry_run` | `1` | Mock LLM and mock ads — no GPU, no models, no FAISS |

## Study protocol

| Param | Values | Default | Effect |
|---|---|---|---|
| `study` | `lab` \| `crowd` | `crowd` (or `STUDY_TYPE`) | Selects the arm and its skipped screens |
| `webcam` | `1` | off | Session-wide webcam recording, either arm |
| `start_typing` | `1` | off | Two-phase trigger that emits a `user_starts_typing` event |

| Arm | Auto-skipped screens |
|---|---|
| `lab` | `prolific_id`, `validation` |
| `crowd` | `baseline` |

Both arms currently default to BFI-10 and 4 turns per conversation. Anything
present in the URL overrides the arm default.

```text
http://localhost:7777?study=lab&pid=p01
http://localhost:7777?study=crowd&pid=p42
```

## Session identity and plan

| Param | Example | Default | Effect |
|---|---|---|---|
| `pid` | `p01` | auto-generated | Fixed participant ID |
| `n` | `2` | `10` | Trial count for the legacy trial plan (1–20) |
| `tasks` | `swt_laptop_budget,swt_dinner_party` | first N of `TASK_CATALOG` | Ordered task IDs |
| `modes` | `inline_persuasive,explicit_ad_block` | first N of `AD_MODES` | Ordered ad-mode keys |
| `bfi` | `10` \| `44` | `10` | Personality inventory length |

The Workflow B controller always builds **five** conditions from `CONDITIONS`,
so `n` and `modes` affect only the legacy trial plan and dev tooling, not the
number of conditions a participant sees.

## Counterbalancing

| Param | Example | Default | Effect |
|---|---|---|---|
| `cb` | `0`, `1`, `2` | `hash(pid)` | Latin-square row for task rotation |
| `seed` | `42` | non-deterministic | Makes the condition shuffle and ad-turn draw reproducible |

Neither value is logged directly, but the resolved plan they produce is: the
`session_started` event carries the full condition-to-task assignment.

## Turns and ad timing

| Param | Example | Default | Effect |
|---|---|---|---|
| `turns_min` | `4` | `MIN_TURNS_PER_TRIAL` | Turns required before finishing a conversation (1–30) |
| `turns_max` | `8` | `MAX_TURNS_PER_TRIAL` | Turns after which the chat closes (1–30) |
| `finish_from` | `5` | `= turns_min` | Turn from which the "I've finished" button is visible |
| `ad_turns` | `2,5` | `AD_INJECTION_TURNS` | 1-indexed turns that trigger injection |

`turns_min` is clamped to `turns_max`. In the five-condition protocol the ad
turn comes from `CONDITION_TIMING` (turn 2 for early, turn 4 for late), so
`ad_turns` matters mainly in dev and legacy trial modes.

## Retrieval pipeline

| Param | Values | Default | Stage |
|---|---|---|---|
| `qe` | `none` \| `hyde` \| `expand` | `hyde` | Query expansion before dense retrieval |
| `ctx_sum` | `1` \| `0` | off | Summarise conversation history into a one-line intent |
| `ad_sum` | `1` \| `0` | off | Rewrite the ad text to ≤ 25 words before injection |

## LLM

| Param | Example | Default | Effect |
|---|---|---|---|
| `model` | `qwen3.6:35b` | `DEFAULT_MODEL` | Override the model for this session |

## Screen skipping

| Param | Values | Effect |
|---|---|---|
| `skip` | comma-separated screen names | Extra screens to auto-advance past |

Skippable: `consent`, `demographics`, `ocean`, `baseline`, `practice`,
`trial_intro`, `final_survey`, `prolific_id`, `validation`. URL skips are
**merged** with the arm's own skips.

## Dev-only

Ignored unless `dev=true` or `dev=flow`:

| Param | Values | Effect |
|---|---|---|
| `force_ad` | `1` | Inject an ad on every turn, ignoring the schedule |
| `rag` | `0` \| `1` | Force the mock backend or the full RAG pipeline |

---

## Recipes

Lab session, reproducible assignment:

```text
http://localhost:7777?study=lab&pid=p01&cb=0&seed=7
```

Crowd session with webcam recording:

```text
http://localhost:7777?study=crowd&pid=p42&webcam=1
```

Click through the whole flow on a laptop with no GPU:

```text
http://localhost:7777?dev=flow&dry_run=1
```

Iterate on ad rendering without waiting for turns or models:

```text
http://localhost:7777?dev=flow&rag=0&force_ad=1&skip=consent,baseline,demographics,ocean
```

End-to-end retrieval check with HyDE:

```text
http://localhost:7777?dev=flow&rag=1&qe=hyde&force_ad=1&skip=consent,baseline
```
