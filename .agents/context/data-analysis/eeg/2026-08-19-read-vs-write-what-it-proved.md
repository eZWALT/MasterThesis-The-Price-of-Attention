# Read vs write: what it proved

Date: 19 August 2026

## TLDR

It proved the **EEG chain is alive**, not that ads work.

Same 4 s, same ICA, same 16 features, same 18 people: Fz theta is higher
while the user is composing than while they are reading the assistant
(**+0.60 dB**, Holm **0.007**, \(d_z=0.80\)). Posterior alpha does not
separate those two states (Holm 0.75).

Therefore a Holm-null on ads/conditions is **“these spectra do not move
with ad format or timing”**, not **“we cannot measure anything.”**

It did **not** prove:

- that ads change EEG;
- that EEG measures trust, load, or persuasion;
- that people “think harder” in a clinical sense;
- that we should change epoch length, drop ICA, or rewrite the product.

This is ticket B1. It is a pipeline sanity check, not Q1 and not Q2.

## Paper placement

**One sentence in EEG Results (or Method), then stop.** Not a subsection,
not a main-text figure, not the abstract, not a discussion claim about
mental effort or advertising. Figures 14–15 stay in the analysis folder
or an appendix if a reviewer asks. Secondary bands stay unpublished.

## Why it exists

Q1 (Dataset A) and Q2 (Dataset B) came back Holm-null on the two confirmatory
features. A null has two readings:

1. ads do not move Fz theta / posterior alpha in this design;
2. the cleaner + 4 s + person-level median cannot recover any known
   difference, so (1) is uninterpretable.

B1 tries to recover a difference we already believe exists *inside the
same chat*: reading the reply vs composing the next message.

## What we actually cut

Do **not** use `turn_N_read` / `turn_N_write` / `user_starts_typing`.
In the deployed lab app those often share the submit timestamp.

Contract (frozen 2026-08-06, coded 2026-08-19):

| State | Window |
|---|---|
| reading | first complete 4 s after `assistant_reply` |
| writing | last complete 4 s before the next `user_message` |

Only inside `condition_start` → `condition_conclusion_submitted`. Drop
warmup, surveys, overlapping pairs (gap must be ≥ 8 s).

268 eligible turn pairs (13–15 per person, all 18 people). Inferential
unit is still the **person**: median of that person’s turn-level
(writing − reading), then a one-sample test. Holm family = the two
confirmatory features.

Runner: `analysis/eeg/preprocessing/run_task_state_positive_control.py`.
Stats: `analysis/eeg/statistics/outputs/task_state/`.
Figures: `figure_14_task_state`, `figure_15_task_state_slopes`.

## Numbers

| Feature | Mean (write − read) | 95% CI | Holm \(p\) | \(d_z\) | Read as |
|---|---|---|---|---|---|
| Fz theta | +0.60 dB | [0.22, 0.97] | 0.007 | 0.80 | chain sees a state difference |
| Posterior alpha | +0.08 dB | [−0.43, 0.59] | 0.75 | 0.08 | this feature does not separate the two states |

Secondary (uncorrected, do not promote): more delta, less beta/gamma
and lower Pope ratios while writing. Compatible with a slower spectrum
during composition. Not confirmatory.

## Paper sentence (that is the whole mention)

As a sanity check, the same 4 s ICA chain distinguished writing from
reading on Fz theta (\(M=+0.60\) dB, 95% CI \([0.22, 0.97]\), Holm
\(p=0.007\), \(d_z=0.80\), \(n=18\)).

## Related

- Contract history: `2026-08-19-ica-primary-and-visual-signoff.md`
- Stop line: `2026-08-19-eeg-only-analyses-complete.md`
- Ticket B1: `2026-08-19-eeg-analysis-menu-and-tickets.md`
