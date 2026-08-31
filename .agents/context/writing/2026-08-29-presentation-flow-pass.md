# Presentation flow pass (29 August 2026)

Pokemon save before a multi-iteration defence-deck rewrite. Walter
is away ~15 minutes. He may ask to **roll the Overleaf presentation
back**. Do not squash. One Overleaf commit per iteration, messages
prefixed `deck-iter-N:`.

## Rollback

Presentation Overleaf `https://git.overleaf.com/69b05745e534a779b65aae63`.

**Restore point (before this pass):** `d5d42ab`
`Add Vaswani 2017 to the presentation bibliography.`

That HEAD already has: filled intro (OpenAI costs, Big Tech ads, AI
Race + Artificial Analysis, welfare triad with capital Π, system
architecture at end of Methods), tiny footnotes, Vaswani closer.
Empty slide still: **The Era of Conversational Neural Networks**.

To roll back the whole pass:

```text
git -C docs/overleaf/presentation fetch
git -C docs/overleaf/presentation reset --hard d5d42ab
git -C docs/overleaf/presentation push --force
```

Only do that if Walter explicitly asks. `--force` on Overleaf is his
call. Parent repo is not part of this pass unless he asks to commit
context.

## What he asked for (this session)

1. Fill the first *content* slide (after title + agenda): image + text.
   The obvious asset is `images/introduction/chat_example.png` (ChatGPT
   screenshot). Not the prefill/decode sketch (`inference.png`) — that
   is isolated engineering slop in an intro that now argues money → ads
   → ads in the reply.
2. Kill **isolated slides**: thesis/paper ports and GPT-ad-hoc frames
   that break the spoken arc now that the intro is good.
3. Revise the skeleton to match the new intro.
4. At least 5 iterations (5–10 nice), labeled so a single iter can be
   reverted.

## Spoken arc (locked for this pass)

```text
Title → Agenda
1  Era of conversational nets   ← chat screenshot (was empty)
2  Inference is not free        ← OpenAI costs (The Information)
3  Big Tech already lives on ads
4  The AI Race                  ← Artificial Analysis index
5  Welfare triad                ← Π, Xu footnote
6  The next medium is the reply  ← implicit/explicit example
RQs (four families, not eleven questions)
Methods: 2×2, two formats, lab flow, biases named, Atlas stack last
Results: grey Goal 1; EEG forests; Holm board; trajectories
Discussion: how to read; limits
Close: artifacts, takeaways, next, Vaswani joke
```

Stay off the clock: theory Defs 1–6, retrieval funnel, ICA/Holm
theology, pairwise boards, empty appendix section cards.

## Iteration log

| Iter | Overleaf SHA | What |
|---|---|---|
| 1 | `5d7555f` | Fill Era slide (ChatGPT screenshot) |
| 2 | `7cce686` | Stitch intro as one money argument |
| 3 | `fa74745` | One RQ slide; drop isolated sample recap |
| 4 | `e63f45e` | Methods: flow + biases; drop sample dump |
| 5 | `5ec257a` | Welfare spelling, grey battery, no empty appendix cards |
| 6 | `c9765ff` | Discussion leads with EEG / trajectories |
| 7 | `95fa3fe` | Drop blank appendix pause |
| 8 | `5dc0409` | Era closer + biases title |

After the push, HEAD is `deck-iter-8`. To undo **one** iter: `git revert <sha>`. To undo **the whole pass**: reset to `d5d42ab`.

## Locks that still apply

- Do not invent Goal 1 numbers.
- Trajectories thesis-only in the paper; they stay in this talk.
- Dataset A/B, implicit ≠ subliminal, ICA archive.
- Do not overwrite `thanks.tex` or Walter's dedication quotes.
- Paper intro/related-work polish is **not** in thesis Ch 1–2 yet.

## Related

- Title page (same day): `2026-08-29-presentation-title-page.md`
- Prior skeleton: `2026-08-28-presentation-skeleton.md`
- Afternoon 27 Aug: `2026-08-27-afternoon-save.md`
