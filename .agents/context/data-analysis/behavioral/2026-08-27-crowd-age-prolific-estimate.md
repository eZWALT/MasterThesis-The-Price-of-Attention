# Crowd age estimate (Prolific snapshot) — prose only

**27 August 2026.** Estimation for thesis Results 7.1
(`sec:results-sample`). **Do not write these ages into Gold, analysis
CSVs, or any behavioural dataset.** Several Prolific demographic fields
are `CONSENT_REVOKED` or missing, the zip is not the finished \(C=36\)
roster, and the post-experiment `demo_age` item is blank for every
finished participant.

Source zip (local, not in git): five Prolific demographic exports,
37 submissions across five study listings (13 Jul–28 Jul 2026).
Columns are the standard Prolific demographic dump (submission /
participant ids, status, timestamps, completion code, age, sex,
ethnicity, country, student/employment). Do not commit the zip or the
extracted CSVs.

## What was *not* used

- Post-experiment questionnaire `demo_age`: empty for all 36 finished
  crowd sessions (and all 18 lab).
- RETURNED / TIMED-OUT / unfinished rows, `crowd_subject_12_unfinished`
  (APPROVED on Prolific but not in the analysed sample), synthetic,
  lab, beta.
- Primary Gold tables.

## Link to the analysed crowd arm (\(C=36\))

Finished roster as in
`2026-08-18-behavioural-roster-and-log-schemes.md`.
Join was Prolific participant id ↔ logged `worker_id_set.worker_id`
on `tracked/crowd/` exports. One early finished session
(`crowd_subject_1`) has no `worker_id_set` event; it was linked by
session start within 10 s of the first APPROVED row of the first
listing. Nine finished sessions (32, 33, 35, 36, 38, 40, 42, 43, 44)
start on or after 28 Jul evening, after the latest listing in the zip,
and have no row.

Linked finished: 27 / 36.
Numeric age: 26 / 36.
Revoked demographic consent among linked finished: 1
(`crowd_subject_18_unfocused`, Prolific REJECTED; retained in \(C=36\)
because unfocused + instruments complete).
Unlinked finished: 9 / 36.

## Estimate (sample SD, \(n-1\))

Among the 26 of 36 finished crowd participants with a numeric age:

- \(n=26\)
- range 23–56
- \(M=35.69\)
- \(\mathrm{SD}=9.51\)
- \(\mathrm{Mdn}=34.5\)

Thesis sentence is in `docs/overleaf/thesis/chapters/results.tex`
`sec:results-sample`. Figure `fig:sample-demo` stays questionnaire-only
(age still omitted there).
