# Query String Guide

All experiment configuration is controlled via URL query parameters.
No code changes are needed — craft the URL, share it with the participant.

The full parameter reference lives in `core/experiment/query_params.py`.

---

## Parameters

### Routing

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `dev` | `true` \| `1` \| `yes` | — | Developer free-chat mode |
| `dev` | `flow` | — | Participant flow with skip buttons in sidebar |

### Session identity

| Param | Example | Default | Description |
|-------|---------|---------|-------------|
| `pid` | `p01` | auto UUID | Force a specific participant ID |

### Trial plan

| Param | Example | Default | Description |
|-------|---------|---------|-------------|
| `n` | `2` | `TRIALS_PER_SESSION` (=10) | Number of trials (1–20) |
| `tasks` | `swt_dev_role_setup,swt_birthday_surprise` | first N from catalog | Ordered task IDs |
| `modes` | `2_in_chat,4_adjacent` | first N from `AD_MODES` | Ordered ad mode keys |

### Counterbalancing & reproducibility

| Param | Example | Default | Description |
|-------|---------|---------|-------------|
| `seed` | `42` | non-deterministic | Integer seed for reproducible task/mode shuffle |
| `cb` | `0` \| `1` \| `2` | `hash(pid) % n` | Explicit Latin-square rotation row |

The ad mode sequence is rotated circularly by the `cb` row so every group
sees each mode in a different trial position. With 5 modes:

```
cb=0  →  [A, B, C, D, E]
cb=1  →  [B, C, D, E, A]
cb=2  →  [C, D, E, A, B]
…
```

### Turn constraints

| Param | Example | Default | Description |
|-------|---------|---------|-------------|
| `turns_min` | `4` | `MIN_TURNS_PER_TRIAL` | Turns required before "I've finished" actually ends the trial |
| `turns_max` | `8` | `MAX_TURNS_PER_TRIAL` | Turns at which chat is force-closed |
| `finish_from` | `5` | `FINISH_BUTTON_VISIBLE_FROM_TURN` (= `turns_min`) | Turn from which the "I've finished" button becomes visible |
| `ad_turns` | `2,5` | `AD_INJECTION_TURNS` | 1-indexed turns that trigger ad injection |

### Study protocol (lab vs crowdsourcing)

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `study` | `lab` \| `crowd` | `crowd` (or `STUDY_TYPE` env) | Protocol preset — controls auto-skipped screens and turn defaults |

| Study | Baseline (EEG) | Default `turns_min` | Auto-skipped screens |
|-------|----------------|---------------------|----------------------|
| `lab` | shown | 5 | `demographics` |
| `crowd` | skipped | 3 | `baseline`, `demographics` |

Add more auto-skipped screens per study in `STUDY_SKIP_SCREENS` in `core/config.py`.
URL `skip=` extras are **merged** with the study protocol (e.g. `?study=crowd&skip=consent` skips baseline + consent).

**Lab session (full protocol)**
```
http://localhost:7777?study=lab&pid=p01
```

**Crowdsourcing session (no EEG baseline)**
```
http://localhost:7777?study=crowd&pid=p42
```

### Screen skipping (dev / extras)

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `skip` | comma-separated screen names | — | Additional screens to auto-advance (merged with `study` skips) |

Valid screen names: `consent`, `demographics`, `ocean`, `baseline`, `practice`, `trial_intro`, `final_survey`

### LLM

| Param | Example | Default | Description |
|-------|---------|---------|-------------|
| `model` | `qwen2.5:32b-instruct-q4_K_M` | `DEFAULT_MODEL` | Override LLM model for this session |

## Example URLs

**Standard production session — assigned group**
```
http://localhost:7777?pid=p01&cb=0&seed=7
```

**Specific task and mode assignment**
```
http://localhost:7777?pid=p02&tasks=swt_dev_role_setup,swt_birthday_surprise&modes=2_in_chat,4_adjacent
```

**Reduced turns and early ad injection (pilot)**
```
http://localhost:7777?pid=pilot01&turns_min=2&turns_max=4&ad_turns=1,3
```

**Dev flow test — skip boring screens**
```
http://localhost:7777?dev=flow&skip=consent,baseline,demographics
```

**Single-trial debug with implicit ads**
```
http://localhost:7777?dev=flow&n=1&modes=5_implicit&skip=consent,baseline,demographics,ocean
```

**Reproduce exact session from logs**
```
http://localhost:7777?pid=p01&seed=42&cb=2&tasks=swt_dev_role_setup&modes=5_implicit&turns_min=6&turns_max=10&ad_turns=3,6
```

---

## Ad mode keys

| Key | Label |
|-----|-------|
| `1_classical_ui` | Classical UI (banner beside chat) |
| `2_in_chat` | Contextual In-Chat (sponsored messages) |
| `3_suggestions` | Sponsored Suggestions (follow-up prompts) |
| `4_adjacent` | Adjacent (panel next to response) |
| `5_implicit` | Implicit / Hidden (embedded in LLM output) |

---

## Validation notes

- Invalid or out-of-range values are **silently ignored** — the system falls back to config defaults.
- `turns_min` is clamped to `≤ turns_max` automatically.
- `finish_from` defaults to `FINISH_BUTTON_VISIBLE_FROM_TURN`, which itself defaults to `MIN_TURNS_PER_TRIAL` (= `turns_min`). The button appears from that turn onward as soft guidance — clicking it always ends the trial regardless of `turns_min`.
- `tasks` and `modes` lists are padded or trimmed to match `n` if lengths differ.
- `cb` and `seed` are logged in the session export for reproducibility audits.
