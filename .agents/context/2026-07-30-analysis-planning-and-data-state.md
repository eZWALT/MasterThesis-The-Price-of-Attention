# Project context — analysis planning and data state

Written 30 July 2026. This document exists so that a person or an agent joining the
project can see, without re-deriving it, what stage the study is in, which decisions
are already fixed, and where the reasoning behind them is recorded.

It describes state, not results. Nothing here has been through statistical analysis.

## Where the study stands

Data collection is **ongoing but nearly complete for the crowd arm and still
running for the lab arm**. The implemented protocol is stable and canonical: five
conditions of four turns each, one advertisement injected per ad condition, one
condition with no advertising.

The five conditions, as logged:

| Condition label | `ad_mode` | Meaning |
|---|---|---|
| `inline_early` | `inline_persuasive` | Advertisement woven into the reply, early turn |
| `inline_late` | `inline_persuasive` | Advertisement woven into the reply, late turn |
| `block_early` | `explicit_ad_block` | Labelled advertising block, early turn |
| `block_late` | `explicit_ad_block` | Labelled advertising block, late turn |
| `no_ads` | *(empty)* | Control condition, no injection |

Condition order is randomised per participant. Because each participant sees every
condition, the design is **within-participant on condition** and between-participant
only on arm (crowd versus lab) and on individual differences.

## Sample as of 30 July 2026

Counted directly from `src/project/logs/production/`.

| Group | Sessions on disk | Complete | Quality-flagged | Notes |
|---|---|---|---|---|
| `beta_tester_*` | 12 | 10 | 2 unfinished | Pilot builds; not study data |
| `crowd_subject_*` | 35 | 30 | 5 unfinished, 2 unfocused | Plus `lab_subject_4_crowdfail`, which ran the crowd protocol |
| `lab_subject_*` | 17 | 17 | 1 mislabelled arm | 16 are genuine EEG-arm participants |

Quality flags live in the directory name itself: `_unfinished` (session did not reach
`experiment_end`), `_unfocused` (participant inattentive), `_crowdfail` (lab
participant who ended up running the crowd protocol and has no rest baseline).

Working figures for planning: roughly **29 clean crowd participants** and **16 lab
participants**, of which the lab count is the binding constraint on anything EEG.

## Logging drift you must account for

The logging implementation changed three times during collection. This is the single
most common source of confusion when writing analysis code, so it is recorded here
in full.

### File naming

| Scheme | Sessions |
|---|---|
| `run_<hex>.jsonl` + `run_<hex>_export.jsonl` | `beta_tester_1`–`7`, `9` |
| `events.jsonl` + `export.jsonl` | `beta_tester_8`–`12`, `crowd_subject_1`–`5` |
| `exp_<UTC>_<hex>_events.jsonl` + `..._export.jsonl` | `crowd_subject_6` onward, all lab sessions |

Any loader must glob all three patterns, not just the current one.

### Marker eras

| Era | Sessions | `ad_displayed` | `turn_N_read` | Event count |
|---|---|---|---|---|
| 0 | `crowd_subject_1`–`5` | — | — | ~121, earlier and shorter protocol |
| 1 | `lab_subject_1`–`3`, `crowd_subject_6`–`13` | 4 events, both formats, `ad_mode` field **empty** | 20 | ~195–200 |
| 2 | `lab_subject_5`–`7`, `crowd_subject_14`–`24` | **absent entirely** | **absent entirely** | ~146–150 |
| 3 | `lab_subject_8`–`17`, `crowd_subject_25`–`35` | 8 events, **labelled block only**, quadruplicated | 20 | ~198–202 |

`ad_injected` is the one ad marker that is present four times in every complete
session, in every era, correctly tagged by format. It is therefore the **primary
time lock** for all event-locked analysis. `ad_displayed` is validation material
only.

`baseline_start` / `baseline_end` appear only in lab sessions, and not in
`lab_subject_4_crowdfail`.

## Decisions already taken

These are settled. Do not relitigate them without the author's involvement.

1. **The implemented five-condition protocol is canonical.** Earlier design variants
   in older notes are historical.
2. **Both arms are analysed jointly** for behavioural outcomes, with arm as a
   sensitivity check rather than a separate analysis.
3. **Condition is treated as a five-level factor**, with planned contrasts rather
   than a full factorial of format × timing, because the no-ad control does not fit
   a factorial.
4. **The analysis specification is frozen before outcomes are inspected.** Anything
   discovered afterwards is reported as exploratory and labelled as such.
5. **The primary modelling approach is a hierarchical mixed model** with participant
   random intercepts, chosen over choice models, EEG-first designs, and
   embedding-heavy models after an explicit feasibility comparison.
6. **EEG analysis is spectral, not event-related.** With one advertisement per
   participant per condition, ERP components cannot be averaged into existence.
7. **Ad clicks are not an outcome.** There were none.

## What the data cannot support

Recorded here because these were checked and ruled out, and re-proposing them wastes
time:

- Single-trial decoding of advertising format or timing from EEG.
- Classical ERP components (P300, N400) as primary outcomes.
- Any claim that EEG directly measures trust or persuasion.
- Eye-tracking areas of interest — the lab arm stores video, not gaze coordinates,
  and no gaze pipeline exists in this repository.
- Predicting crowd-arm condition means from lab EEG; the effective sample is four.

## Open blockers

1. **The EEG recordings are not in this repository.** They are in Drive, and the
   pilot files that were inspected are partial (2–17 minutes against sessions of
   33–110 minutes). Nothing EEG can run until the full recordings are mounted.
2. **No join key exists** from `lab_subject_N` to recording filename to
   `experiment_id`. This mapping has to be built explicitly; filename numbering is
   not evidence.
3. **Clock alignment is unfitted.** The procedure is specified in
   `docs/generated/eeg-analysis-plan.md`; the `timestamp` field carries microsecond
   precision, so this is tractable, but it has not been done.
4. **Ad visibility timing for inline advertisements must be reconstructed offline**,
   since `ad_displayed` never fires for the inline format. The estimator and its
   validation set are specified in the same document.
5. **The related-work chapter needs restructuring**, not just prose editing. Findings
   and candidate literature were gathered but the chapter has deliberately been left
   untouched.

## Where the reasoning is written down

| Document | Contains |
|---|---|
| `docs/generated/data-analysis-foundation.md` | Research questions, outcomes, contrasts, model structure, exclusions, preregistration order |
| `docs/generated/model-feasibility.md` | Which models the sample supports and which were rejected, with the comparison that produced the ranking |
| `docs/generated/eeg-analysis-plan.md` | Feasible EEG uses by tier, the marker audit, and the offline timing-reconstruction procedure |
| `docs/generated/related-code-chatbot-ads.md` | Review of the *Ads that Talk Back* code release and what transfers to this study |
| `docs/generated/*.canvas.tsx` | Interactive views of the first two documents; they duplicate rather than extend the Markdown |

Everything under `docs/generated/` is a working note produced with AI assistance. It
is version-controlled so the reasoning survives, but it is not a results section and
not peer-reviewed. Counts in those files are dated; re-verify before citing.

## Working agreements

- **Do not edit the thesis, presentation, or publication sources unless asked to.**
  `docs/overleaf/` holds three independent Git mirrors of Overleaf projects, ignored
  by this repository. When the request is for recommendations, deliver
  recommendations and leave the LaTeX alone.
- Use `scripts/overleaf-sync` for those mirrors; the default pull is fast-forward
  only.
- Keep sample counts and marker claims traceable to a dated audit of the logs rather
  than to an earlier document.

## Log handling workflow

Session logs live in two places:

```text
src/project/logs/
├── production/   # what the application writes; ignored by Git
└── tracked/      # curated copy that is committed
    ├── beta/
    ├── crowd/
    └── lab/
```

`production/` is deliberately outside version control. Promoting sessions into
`tracked/` is a manual, reviewed step:

```bash
bash scripts/sync_tracked.sh          # dry-run; lists what would be copied
bash scripts/sync_tracked.sh --exec   # copy new sessions into tracked/<type>/
git add src/project/logs/tracked
git commit -m "data: sync new tracked sessions"
```

The script copies whole session directories, routes them by name prefix, and never
overwrites a directory that already exists in `tracked/`. Because it skips existing
directories, editing a session after promotion requires removing the tracked copy
first. `--delete` removes tracked sessions no longer present in production; use it
only deliberately.

Related helpers in `scripts/`: `label_sessions.py` and `categorize_logs.sh` for
naming and grouping, `housekeep_production.sh` for cleanup.
