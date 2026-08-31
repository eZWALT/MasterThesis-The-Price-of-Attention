# Presentation skeleton (28 August 2026; flow pass 29 August)

Defence deck in Overleaf `docs/overleaf/presentation/`. Title:
**The Price of Attention**. Theme: UniPD Beamer (keep).

**29 August rollback:** `d5d42ab`. Iteration commits `deck-iter-N:`.
Full save: `2026-08-29-presentation-flow-pass.md`.

Walter's spine, not the thesis chapter order:

1. Introduction (why it matters — now a six-slide money argument)
2. Research questions (four families, one slide)
3. Methodology (2×2, formats, flow, biases named, Atlas last)
4. Results
5. Discussion (leads with what we have)
6. Conclusions and future work

Theory, ICA, Holm-vs-BH, pairwise boards, Definitions 1--6, the
**retrieval funnel**, and **prefill/decode sketches**
(`inference.png`, `inference2.png`): **backup or dissertation**.
Exception: methodology ends on `system_architecture.png`. Do not walk
GPU 0 / GPU 1 / FAISS. Empty appendix section cards are commented out.

Per-section TOCs are off (one agenda slide after the title).

## Spoken intro (29 August)

```text
Era (chat screenshot)
  → inference is not free (OpenAI costs)
  → Big Tech lives on ads
  → the AI Race (Artificial Analysis)
  → welfare triad (Π)
  → the next medium is the reply
```

`chat_example.png` is the Era image. Do not put `inference.png` there.

## What is frozen vs grey

**Frozen:** five conditions, \(N=54\) / EEG \(n=18\), implicit \(\neq\)
subliminal, EEG confirmatory forests + Holm board, trajectory Holm-null
and the "null \(\neq\) theory is wrong" read, no insertion-policy
results, no channel-set in the main deck.

**Grey (`\pending` blocks):** Goal 1 battery, Goal 2 moderation, Goal 5
combos. Do not invent numbers. The grey Results slide is the missing
pillar, not a leftover TODO.

## Assets (`presentation/images/`)

Walter's section folders, 29 August. No `study/` dump.

| Folder | What |
|---|---|
| `introduction/` | Era chat screenshot, OpenAI losses, Artificial Analysis, ads example, welfare triad |
| `ui/` | Implicit / explicit screenshots |
| `workflows/` | Lab and crowd participant flows |
| `results/` | EEG forests and Holm board, sample, BFI, trajectories, pairwise |
| `preprocessing/` | EEG pipeline, montage, trajectory pipeline, ads data pipeline |
| `arch/` | System architecture and retrieval (this thesis, not BCI-MI) |
| `misc/` | Closer joke + Vaswani cite, leftover TikZ assets |

Off the spoken path: `inference.png`, `inference2.png`, `openai_burn.png`
(second The Information chart; the losses slide already carries the burn).

Old BCI-MI TikZ stays in an `\iffalse` archive at the bottom of `main.tex`.
