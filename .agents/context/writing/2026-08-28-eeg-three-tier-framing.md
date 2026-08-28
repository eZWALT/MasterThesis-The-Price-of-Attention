# EEG framing: three tiers, one positive result (28 August 2026)

How the EEG arm is presented in the thesis. Settled with Walter after
the post-hoc sweep came back null and the question became "what do we
actually have". Numbers and locks:
`../data-analysis/eeg/2026-08-28-posthoc-pairwise.md`.

## The frame: three tiers, not four analyses

| Tier | What | Where |
|---|---|---|
| 1. Confirmatory | Dataset A 3 contrasts, Dataset B 4 contrasts, on Fz theta and posterior alpha | Results main text. Null, with the \(\pm 0.3\) dB bound and the MDE |
| 2. Exploratory, same contrasts | the other 14 measures | Results main text, labelled. **This is the positive result** |
| 3. Post hoc | the two pairwise sweeps | One paragraph in Results, detail in appendix. Localisation only |

## Do not lead with the caveats

The earlier framing led with "not confirmatory, ICA-only, probably an
artefact" and read as an apology. Correct the emphasis, keep the
caveats as scope:

- **Report the six cells.** \(d_z\) from 0.69 to 0.93, every CI excludes
  zero, **Wilcoxon agrees on all six**. These are medium-to-large
  effects that survive a parametric and a non-parametric test after
  correction.
- **The headline is that it is format-specific.** Explicit-early
  produces the response; implicit-early does not (all six measures
  Holm-null, \(|d_z|\le 0.37\)). That is the paper's \(\lambda\) axis
  appearing in the EEG.
- **"Five measures are one event" is a strength, not a weakness.**
  Interdependent measures moving together in the direction one
  underlying event predicts is internal consistency. Say it that way,
  and it is also why you do not inflate them into five findings.
- **"ICA-only" is the protocol, not a concession.** ICA is the primary,
  pre-specified, human-signed pipeline (19 August). Attenuation in the
  no-ICA branch has a benign reading: ICA removes blink variance,
  dispersion falls, power rises. Report both columns.

Two guardrails, one clause each, and nothing more: call them
exploratory, and show the no-ICA column.

## Never write "approached significance"

The rigorous version of "more subjects would find it" is the minimum
detectable effect, not a near-miss \(p\).

| Correction | Smallest \(|d_z|\) detectable at 80%, \(n=18\) |
|---|---|
| uncorrected | 0.70 |
| Holm within 4 | **0.87** |
| Holm within 6 | 0.92 |
| Holm within 10 | 0.97 |

The only cell that cleared correction (global delta, explicit-early) is
\(d_z=0.88\), sitting **at** the bound. The design was powered for
exactly one size of effect and found the one effect of that size.

## The replication target

Implicit-late Fz theta is the one coherent candidate in the whole sweep:

| Fz theta comparison | M (dB) | \(d_z\) | raw \(p\) |
|---|---|---|---|
| implicit-late vs own control | \(-1.38\) | \(-0.48\) | .056 |
| implicit-early \(-\) implicit-late | \(+1.99\) | \(+0.57\) | .028 |
| implicit-late \(-\) explicit-early | \(-2.12\) | \(-0.55\) | .031 |
| implicit-late \(-\) explicit-late | \(-1.26\) | \(-0.48\) | .058 |
| *any comparison excluding it* | | \(\le 0.28\) | \(\ge .24\) |

Honest qualifier, must be kept: these share the same eighteen
\(\Delta_{IL}\) values, so it is **one condition seen four ways, not
four independent confirmations**. 26% power at \(n=18\); **52
participants** for 80% under the same correction, 37 uncorrected.

Supporting provenance: 8 nominal cells out of 320 against ~16 by
chance. The sweep is not a dredge that surfaced scattered noise, it is
a broad search that returned exactly one candidate.

## Reporting decision: \(\Delta\) space only in the thesis

The pairwise analysis computes Dataset B twice, in \(\Delta\) space and
in raw post-minus-pre. **The thesis reports \(\Delta\) only**, giving
160 + 96 = **256 tests**, 7 nominal against 13 expected, 0 Holm, 0 BH.

Reporting both would require explaining the control-drift term and, with
it, that the code's `early_vs_late` sits in raw space and was never
pre-specified. That is an undeclared estimand on an uncorrected
secondary row with no consequence for any reported claim, so airing it
costs the reader a subsection and buys nothing. The raw companion stays
in `outputs/posthoc/` and in the 32-page report.

## What went into the thesis (28 August)

**`chapters/models.tex`.** Threshold bullet kept **declarative and two
sentences**, matching its siblings; it names the \(q\) and points
forward. The argument moved to prose immediately after
`tab:analysis-families`, where it gives the mechanism (the five
relative powers share a denominator and sum to one), names BY once, and
ends on why Holm is primary. Column header and caption changed from
"Holm family" to "correction family", since two corrections now run.
New table row "Exhaustive pairwise, post hoc". The 450-word EEG
paragraph was **split in three**: construction, then the two checks,
then the post-hoc sweep with the redundancy consequence as its closing
clause. Bib: `benjamini1995fdr`, `benjamini2001dependency`.

**`chapters/results.tex`.** Two paragraphs, "Exhaustive pairwise
comparisons" and "Minimum detectable effects". Roadmap sentence in the
EEG opening extended to name them. Missing row added to
`tab:results-summary`, which its own caption promises mirrors
`tab:analysis-families` row for row.

**`chapters/discussion.tex`.** Chapter opening now names the
format-specific result as the one carrying most of what follows.
"What separates the two formats" **moved up** to sit after the ICA
caveat, so the positive claim lands after the objections rather than
after an unrelated paragraph. New "What the pairwise sweep added". The
MDE argument went into the Dataset~B paragraph, where the imprecision
is discussed, and one line into Limitations. Replication paragraph
trimmed to remove the restatement it shared with the sweep paragraph.

## Style rules extracted from Walter's own prose, for future passes

1. Every unit declares its own job in its first sentence.
2. Justification is welded to the claim in the same sentence, never
   deferred: "so that", "because", "which is what lets".
3. Name the two things and say they differ before explaining either.
4. Intuition precedes formalism ("Take one outcome, say Fz theta").
5. Pre-empt the reviewer inside the sentence.
6. Numbers carry their meaning ("+4.60 dB, roughly a threefold rise").
7. Discussion paragraphs land on a short verdict.
8. **No `---` anywhere.** Semicolons and colons carry the load.
9. `\\` after paragraphs in `models.tex` and `results.tex`, **never** in
   `discussion.tex`.
10. Conventions declare; prose argues. Do not put an argument in a
    bullet whose siblings are rules.
