# Behavioural roster and log-scheme audit (18 August 2026)

Sanity check after the notice/recall loaders missed early crowd
sessions. Participants remain the inferential unit. This note records
what is on disk, not a frozen Gold table.

## Walter's inclusion rule (this session)

Count **finished** lab and crowd sessions only.

**Out:** beta testers, `*_unfinished`, `*_synthetic`, `*_crowdfail`.

**In:** finished `*_unfocused` if the instruments are complete
(`crowd_subject_5_unfocused`, `crowd_subject_18_unfocused`).

`development` is not a cohort. No such folder exists under
`tracked/lab` or `tracked/crowd`. It drops nobody.

## Loader bugs (first notice/recall plots)

Scripts used `tracked/{lab,crowd}/**/*_export.jsonl` and required
`condition` ∈ `{inline_early, inline_late, block_early, block_late, no_ads}`.

Two independent misses:

1. **Filename.** Early crowd files are `export.jsonl` or
   `export_<id>.jsonl`, not `exp_*_export.jsonl`.
2. **Condition encoding.** Those same sessions store condition as trial
   index `1`–`5`. Map through `session_started.data.condition_plan`.

Only **five** tracked folders were hit by both bugs. Lab was not.

| Folder | File | Condition field |
|---|---|---|
| `crowd_subject_1` | `export_69ef30e061e0267d5dcca812.jsonl` | 1–5 via plan |
| `crowd_subject_2` | `export.jsonl` | 1–5 via plan |
| `crowd_subject_3` | `export.jsonl` (+ `events.jsonl` duplicate) | 1–5 via plan |
| `crowd_subject_4` | `export.jsonl` (+ `events.jsonl` duplicate) | 1–5 via plan |
| `crowd_subject_5_unfocused` | `export.jsonl` (+ `events.jsonl` duplicate) | 1–5 via plan |

All five have `session_complete`, five post-condition surveys, and four
cued-recall steps. `crowd_subject_1` has two malformed JSON lines; the
session is still complete.

Later sessions use `exp_*_export.jsonl` and string condition keys. The
old glob finds those. Unfinished crowd folders often have only
`*_events.jsonl` (no export) and never reach recall.

## Tracked finished roster

Complete = 5 mapped notice conditions **and** 4 recall conditions.

| Arm | n | Folders |
|---|---|---|
| Lab | 18 | `lab_subject_1`–`3`, `5`–`19` |
| Crowd | 36 | `crowd_subject_1`–`4`, `5_unfocused`, `6`–`11`, `13`–`16`, `18_unfocused`, `19`–`26`, `28`–`30`, `32`, `33`, `35`, `36`, `38`, `40`, `42`, `43`, `44` |
| **Total** | **54** | |

Out of tracked, by rule (even if complete):

- `lab_subject_4_crowdfail` — complete instruments; lab folder / crowd
  protocol. EEG already excludes. Behavioural: out under this rule.
- `crowd_subject_37_synthetic` — complete but fake.
- `tracked/beta/beta_tester_*` — 9 complete testers (`1`–`4`, `6`, `7`,
  `9`, `10`, `12`). Sensitivity only.

Unfinished crowd (`12`, `17`, `27`, `31`, `34`, `39`, `41`) do **not**
have five surveys plus recall. Closest: `12` and `41` have 4/5 notice,
0/4 recall.

## Production sessions copied into tracked (18 August 2026)

Copied from `logs/production/` into `tracked/crowd/`:

- `crowd_subject_42`
- `crowd_subject_43`
- `crowd_subject_44`

All three are complete. Tracked finished crowd is now **36**. Combined
finished *N* is **54** (18 lab + 36 crowd).

Still production-only and incomplete: `crowd_42_unfinished`,
`exp_20260802T150349Z_*`, `exp_20260803T095359Z_*`,
`exp_20260818T103157Z_*`.

## What the first plots actually used

n = 45: new-filename tracked sessions, minus `unfocused` and
`crowdfail` by substring. That dropped `18_unfocused` and
`lab_subject_4_crowdfail`, and never opened crowd 1–5.

Corrected tracked count under the current rule is **54**, not 45.

## ETL contract (next loader)

1. Walk `tracked/lab/*` and `tracked/crowd/*` only for the primary set.
2. Read every `*.jsonl` in the folder; prefer `*export*.jsonl` when both
   `events` and `export` exist so rows are not doubled.
3. Map numeric `condition` through `session_started` `condition_plan`.
4. Exclude folders by **tag**, not random substrings:
   `synthetic`, `unfinished`, `crowdfail`. Do not exclude `unfocused`.
   Do not use a `development` token. Beta lives under `tracked/beta/`.
5. One row per participant × condition; latest export wins.

## Method prose

Method should use the finished counts: \(L=18\), \(C=36\), \(N=54\).
Lab enrolled 19; Subject 4 is out of the finished behavioural and EEG
sets. Do not write a `development` exclusion.