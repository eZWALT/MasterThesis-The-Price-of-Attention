# Generated analysis notes

Planning and feasibility documents produced with AI assistance while designing the
analysis for this study. They are kept under version control so the reasoning
behind the analysis plan survives, but they are **working notes, not results and
not peer-reviewed method sections**.

## Contents

| File | Purpose |
|---|---|
| `data-analysis-foundation.md` | Analysis goals, outcomes, contrasts, model structure, exclusions, preregistration sequence |
| `eeg-analysis-plan.md` | What the lab EEG data can and cannot support, with prerequisites and epoch specifications |
| `model-feasibility.md` | Which statistical and predictive models the sample supports, and what is ruled out |
| `related-code-chatbot-ads.md` | Review of the *Ads that Talk Back* code release: what is reusable for our scoring and what is not |
| `*.canvas.tsx` | Interactive Cursor Canvas versions of the two overview documents |

The Markdown files are the durable record. The `.canvas.tsx` files render the same
material as interactive views inside Cursor and duplicate rather than extend it.

## How to treat these documents

- Counts and sample sizes reflect the production logs as audited on the date stated
  in each file. Re-verify before citing them, since collection is ongoing.
- Every recommendation is conditional on decisions already taken: the implemented
  five-condition protocol is canonical, behavioural data from both arms are
  analysed jointly with arm sensitivity checks, and a frozen analysis
  specification precedes outcome inspection.
- Anything labelled exploratory must stay labelled exploratory in the thesis and
  the paper.
- These notes do not contain participant data. Session logs live under
  `src/project/logs/`.
