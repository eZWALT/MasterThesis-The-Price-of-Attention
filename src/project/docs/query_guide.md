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
| `n` | `2` | `TRIALS_PER_SESSION` | Number of trials (1–20) |
| `tasks` | `trans_plan_trip,social_new_hobby` | first N from catalog | Ordered task IDs |
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
| `turns_min` | `4` | `MIN_TURNS_PER_TRIAL` | Turns required before "Done" button appears |
| `turns_max` | `8` | `MAX_TURNS_PER_TRIAL` | Turns at which chat is force-closed |
| `ad_turns` | `2,5` | `AD_INJECTION_TURNS` | 1-indexed turns that trigger ad injection |

### Screen skipping

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `skip` | comma-separated screen names | — | Silently auto-advance past these screens |

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
http://localhost:7777?pid=p02&tasks=trans_plan_trip,social_new_hobby&modes=2_in_chat,4_adjacent
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
http://localhost:7777?pid=p01&seed=42&cb=2&tasks=trans_plan_trip&modes=5_implicit&turns_min=6&turns_max=10&ad_turns=3,6
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
- `tasks` and `modes` lists are padded or trimmed to match `n` if lengths differ.
- `cb` and `seed` are logged in the session export for reproducibility audits.
