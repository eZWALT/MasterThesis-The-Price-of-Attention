# 2026-09-18 — Defence checkpoint

Defence: Wed 23 Sep morning, Padova, 20 min + Q&A.
Committee names on the deck: Michele Rossi, Ioannis Arapakis.

This is the list. Tick before the first full rehearsal. Do not start
the clock until 1–3 are in a form you can speak, even if rough.

Narrative and time budget:
`2026-09-18-defence-narrative.md`.
Deck Overleaf: `docs/overleaf/presentation` (`f8cef8c` as of this note).

## The list

| # | Artifact | Status | Where |
| --- | --- | --- | --- |
| 1 | 20-min deck (section cards on; parked frames recoverable) | have | `docs/overleaf/presentation/main.tex` |
| 2 | Spoken script (one beat per slide, timed) | **missing** | `%` comments in `main.tex` are a draft, not a script |
| 3 | Breadcrumbs (holes you plant so they ask what you can answer) | **missing** | seeds below; pick 4–6, write the 15 s answer |
| 4 | Anticipated questions + 20 s answers | **partial** | appendix is the figure dump; no spoken crib |
| 5 | Do-not-say card | have, not printed | `2026-08-31-slow-power-and-high-level-discussion.md`; Results rules |
| 6 | Timing sheet (actual vs budget) | **after rehearsal** | fill the table in the narrative note |
| 7 | Thesis PDF (handout / backup) | have | `docs/overleaf/thesis/_build/dissertation.pdf` |
| 8 | Deck PDF on USB + offline laptop | **do today** | `/tmp/deck_20min.pdf` is a stale build; re-export from Overleaf |
| 9 | Paper | not the defence object | leave it; do not open it in the talk |
| 10 | Parked-slide ladder | have | `\ifsecondplane` / `\sectioncardsfalse` in the deck header |

Rehearse once the script and breadcrumbs exist. Questions get rewritten
after the first timed run, not before.

## 1. Script

Not a transcript. One spoken beat per slide, 8–20 words, plus the
handoff to the next slide. Write it in the `%` comments so the source
stays one file. Clock it against:

Intro 5:00 · Question 1:30 · Method 4:00 · Results 7:00 · Discussion 1:30 · Close 1:30

The holes in today's comments: Era, Formats, Flow, EEG two markers,
onset, Limits. Those four need a line before the first run.

## 2. Breadcrumbs

A breadcrumb is a sentence you *leave unfinished* so a reviewer
attacks a place you already have a 15 s answer and a backup slide.
Four to six, not twelve. Each one needs: the plant (what you say),
the likely question, the answer, the appendix slide if any.

Seeds (pick; do not plant all of them):

1. **Disclosure rides with format.** Plant: "the banner is labelled;
   the mention is not." Question: so you cannot separate \(\lambda\)
   from \(\theta\)? Answer: yes, bundled by design; a covert banner
   and an overt mention were not tested. That is the next experiment,
   said in Implications.
2. **Any-ad includes the extra wait.** Plant: "any advertisement,
   together with its retrieval delay." Question: is +1.27 the ad or
   the pause? Answer: format and timing cancel the delay (both sides
   advertised); any-ad against \(a^{\emptyset}\) does not. We say so
   in Limitations.
3. **\(n=18\), one trial per cell.** Plant: "laboratory \(n=18\)."
   Question: is the EEG underpowered? Answer: Dataset B confirmatory
   is Holm-null and the intervals are 2–4 dB; a null is not absence.
   Write–read moved Fz \(\theta\) (+0.60 dB), so the pipeline is
   alive. Next design: more than one insertion per cell.
4. **Onset is reconstructed.** Plant: "onset-locked." Question: how
   do you know when the mention appeared? Answer: client paint for
   the banner; reconstructed for most written-in mentions (p95
   0.43 s vs 0.23 s). Strongest as banner vs matched control, not
   like-with-like format at onset.
5. **Four turns, late ads have no next user turn.** Plant: "turn 2
   or turn 4." Question: then \(\delta^{(a)}_4\) is undefined?
   Answer: yes. That is why the trajectory estimand is early-only,
   and why Future Work wants a fifth turn.
6. **The classifier is the limit, not the theory.** Plant: "no
   steering seen." Question: so ads do not change intent? Answer:
   not testable here. 81.7 % of steps already change genre; 98 of
   156 products are already "guidance." Instrument + inventory.
   Appendix: heatmaps, Defs 1–6.
7. **Nobody clicked.** Plant: leave it unsaid on Results; it sits
   in Limitations. Question: where is the behavioural outcome?
   Answer: the cost we measure is experience, not CTR. No one
   clicked; that was expected on simulated tasks.
8. **Crowd and lab are pooled.** Plant: "\(N=54\), of which 18 EEG."
   Question: can you pool them? Answer: four primary any-ad
   contrasts have the same sign and order; no between-arm cell at
   raw \(p<.05\) (`tab:beh-arm-cells`).

Do not breadcrumb: ICA overwrite, \(k=37\), Holm-80% / MDE, Katerina's
tree, the ad-moment scorer, "processing before the text."

## 3. Questions they will ask anyway

Write a 20 s answer for each, even if you also have an appendix slide.
The appendix is already there (Q&A only):

- Biases and confounds
- Task briefings
- Prompts (implicit injection)
- Questionnaires
- EEG bands / sixteen measures / preprocessing
- Trajectory preprocessing + catalog
- Genre: intent vs genre, Theoretical Work (2), Defs 1–6

Likely without a plant:

- Why not ERP / eye-tracking?
- Why Qwen / why not a vendor API?
- Why these two EEG markers?
- Why four turns / why not a fifth?
- Why no interaction, and is that a power problem?
- Personality 0/60 — is that equivalence?
- Is \(\rho=.80\) just \(n=18\)?
- What should OpenAI actually do? (refuse a serving rule; measurement
  obligation + disclose)
- Why user-centric, not advertiser yield?

## 4. Do not say

- Slow tilt = "active processing" / "registered before the text"
- Dataset A is all-null (early−late posterior \(\alpha\) Holm \(p=.0496\))
- "Wilcoxon Holm" / "approached significance" / Holm-80% / MDE sermon
- Explicit-late as the serving compromise / price of attention as policy
- Path A/B, equal-n neighbourhood, condition state
- Trajectories "proved" no steering

## 5. Practical, today

- Export a fresh deck PDF from Overleaf after the last slide tweak
- USB + offline copy; do not depend on the cluster
- Clicker / laser if the room has a lectern PC
- Printed thesis or marked PDF for them; you do not read it
- Water, time check at 5 / 10 / 15 / 18

## After the first timed run

If ≤ 18:00, add from the parked ladder (narrative note).
If ≥ 21:00, shorten *Frontier chatbots feel free* first, then Platform
spoken time (keep the figure).
Rewrite breadcrumbs that did not land. Do not add new science.
