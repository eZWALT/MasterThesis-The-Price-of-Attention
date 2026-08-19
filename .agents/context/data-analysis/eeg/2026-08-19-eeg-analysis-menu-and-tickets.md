# EEG analysis menu and tickets

Date: 19 August 2026

High-level inventory of what this EEG dataset can support, what already
exists, and what must not be treated as confirmatory. Ticket status:

- **APPROVED** = artefact exists (script + numbers)
- **PENDING** = not built
- **OUT** = decided against, do not build for the thesis

Scientific verdict (do / later / don't) is separate from ticket status.
A PENDING item can still be a don't.

EEG cohort is 18 laboratory people (Subjects 1–3, 5–19). Crowd has no
EEG. Any EEG–survey join is lab-only. Participant is \(n\), never epoch.

Do not claim EEG measures trust, UX, or persuasion. Cross-modal work is
association after both contracts are frozen.

## Answers to the two design questions

### Should we correlate EEG with trust / UX?

Yes, but only as exploratory, and only at the same grain as the surveys.

Post-condition trust, credibility, manipulation, and the UX-like
composites (helpfulness, convincingness, relevance, neutrality) are
**person × condition** scores, same geometry as Path A \(Y_A\). The
honest correlation is therefore:

- same person's \(D_{\mathrm{EEG}}\) with that person's \(D_{\mathrm{survey}}\)
  on the same planned contrast, or
- a repeated-measures association of the five condition medians with the
  five post-condition scores.

There is no instrument labelled UX. Closest live items: helpfulness
family, `personality_trust`, credibility mix, and session
`overall_usefulness`. Do not dump all 16 EEG features against every
Likert item.

Blocked until Person A freezes the behavioural ETL (scoring, IDs,
missingness). Goal 1 behavioural contrasts are still PENDING.

### Should we look between subjects at a global metric?

A person-level EEG summary is possible. It is a **different estimand**
and must not replace the within-person \(D\).

Three things people mix under “global”:

1. **Global band power** (already in the 16 features) — mean across
   channels, still tested inside the within-person \(D\). Not a new
   analysis.
2. **Person-mean EEG** — average of the five condition medians, or the
   baseline row, one number per person. This is trait-like.
3. **Session survey** — `overall_trust`, `overall_usefulness`,
   `ad_awareness`, `ad_disruption`, `willingness_reuse`. One number per
   person after all five chats.

(2) × (3) or (2) × BFI-10 is a between-person Spearman on \(n=18\).
Power is poor (\(\rho=0.3\) is almost invisible; even \(\rho=0.5\) is
weak). Baseline was uncontrolled and mostly eyes-open, so a “resting”
global score is messy. Allowed as a labelled exploratory appendix after
Goal 1. Not confirmatory. Not a substitute for \(D\).

## Ticket board

### A. Within-person EEG (Goal 3)

| ID | Item | Ticket | Verdict |
|---|---|---|---|
| A1 | Path A: 3 primary \(D\) (any-ad, inline vs block, early vs late) on 16 features; \(t\) + Wilcoxon + Holm | APPROVED | keep; write Results |
| A2 | Path B: 4 primary ad-minus-matched-control \(D\); same tests | APPROVED | keep; write Results |
| A3 | Publication layer: forest plots, bootstrap, LOO, Subject 14, onset provenance | APPROVED | keep |
| A4 | Threshold sensitivity 1000 / 1050 / 1500 µV | APPROVED | keep as robustness |
| A5 | ICA vs no-ICA comparison; ICA is primary (`frozen_v5`) | APPROVED | do not pick ICA to rescue six ad hits |
| A6 | Secondary / exploratory feature tables (FAA, global bands, Pope, Kislov) | APPROVED | stay non-confirmatory |
| A7 | Manuscript EEG Results / Statistical Analysis prose | PENDING | do next for EEG writing |

### B. EEG-only still open

| ID | Item | Ticket | Verdict |
|---|---|---|---|
| B1 | Read vs write positive control (static 4 s after `assistant_reply` / before `user_message`) | APPROVED | one-sentence mention only; not a paper result. See `2026-08-19-read-vs-write-what-it-proved.md` |
| B2 | Mixed model `EEG ~ condition + task + order + (1\|person)` | PENDING | later; paired \(D\) already answers the planned contrasts |
| B3 | Mean-of-epoch-dB instead of median | APPROVED | Y_A 0/48 Holm; keep median primary |
| B4 | Epoch-length grid 2/4/8/16/32 s | APPROVED | Path A null at every width; do not freeze 8 s alpha |
| B5 | ERP / P1–P3 | OUT | onset error 0.23–0.43 s; one trial per cell |
| B6 | Epoch as independent \(n\) | OUT | COBIDAS; already refused |
| B7 | Entropy / connectivity / PLV | OUT | no frozen estimator; thesis time |
| B8 | Subject 4 in primary EEG | OUT | crowd protocol |
| B9 | First vs last condition (session order) | APPROVED | exploratory null; not fatigue |

### C. Cross-modal (the missing layer)

Join grain: person × condition or person × ad-response. Never epoch.
Lab \(n=18\) only. Freeze behavioural ETL first.

| ID | Item | Ticket | Verdict |
|---|---|---|---|
| C1 | Spearman / rmcorr of Path A \(D_{\mathrm{EEG}}\) with the same three \(D\) on trust, credibility, manipulation | PENDING | **do this** after Goal 1; exploratory; 2 primary EEG features only |
| C2 | Person × condition: \(Y_A\) vs post-condition UX-like scores (helpfulness, convincingness, `personality_trust`) | PENDING | later; same grain as C1, more tests |
| C3 | Path B \(D\) vs notice / `recall_memory` / `recall_trust_shift` | PENDING | later; recall has no no-ad cell |
| C4 | Between-person: person-mean EEG vs session `overall_trust` / `overall_usefulness` / BFI-10 | PENDING | appendix only; \(n=18\) |
| C5 | Between-person: baseline EEG vs traits | PENDING | weaker than C4; eyes uncontrolled |
| C6 | Incremental model: behaviour vs behaviour+EEG, grouped by person | PENDING | don't for thesis; Goal 5 / tiny \(n\) |
| C7 | EEG \(D\) moderated by BFI-10 | PENDING | Goal 2 is behavioural first; EEG×trait is extra |
| C8 | Claim that EEG measures trust or UX | OUT | standing rule |
| C9 | Kislov-style EEG → population ad efficiency | OUT | no CTR; four ad cells |

## Recommended thesis EEG package

1. A1–A6 numbers + B4/B9 + figure suite 07–13/16 + A7 prose.
   B1 is one sentence in Results, not a results block.
2. C1 once Goal 1 scores exist, confirmatory EEG features only
   (Fz theta, posterior alpha), Holm inside that small family.
3. One sentence that C4 was inspected or deferred, not a third Goal.

Do not invert the study order: behavioural Goal 1 → personality Goal 2
→ EEG Goal 3 → C1.

## Related

- Priority order: `../2026-08-18-analysis-priority-order.md`
- North star Action 4 / 5: `../2026-08-04-final-month-north-star.md`
- Join gate: `2026-08-06-remaining-human-signoff-checklist.md`
- Gold shapes: `2026-08-19-gold-paths-shapes-and-ica.md`
