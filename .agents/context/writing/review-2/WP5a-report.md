# WP5a — Discussion 8.1–8.3 + WP1/WP3 integration into 7.2 / 7.3 / App E

Date: 11 September 2026. Owner: `claude-opus-5-thinking-high`. Status:
**done**. Files edited (targeted `StrReplace` only, no file rewritten):
`chapters/discussion.tex` (8.1–8.3 only), `chapters/results.tex`
(7.2 notice subsection, 7.3, one `tab:results-checks` row, two `% [AI: …]`
lines under Walter comments), `chapters/appendix_e.tex` (two paragraphs).
8.4–8.7 untouched. All 45 `% WALTER:` lines in `discussion.tex` intact
(`git diff | rg "^-.*WALTER"` empty). Nothing committed or pushed.

---

## 1. Per WALTER comment (line numbers of the pre-edit file)

| Line | Comment | What changed |
|---|---|---|
| 28 / 45 | paragraph titles are trash / here is a better example | Every 8.1 title is now a short noun phrase; Walter's three approved titles kept verbatim (`Notice as a manipulation check`, `Perceived manipulation as the main cost of advertisement.`, `Temporal effects on memory and trust.`) |
| 36 / 40 | "notice my comments" / "the last point reads dull" | `Credibility and trust barely move.` → **`Trust and credibility in a short session.`**, split into two short paragraphs. Walter's bold idea kept as the opening claim in plain prose (`\textbf` removed, "percieved" gone, "Trust is therefore not shown to be unaffected completely" gone). Ends on the trust-drop sentence, not on a hedge. |
| 41 | direction of implicit vs explicit is missing | Every contrast now names its direction in words: "the labelled banner is noticed more than the written-in mention, felt as more manipulative, and remembered better". Same in the notice, memory and interaction paragraphs. |
| 49 | emphasise the null interaction | New own paragraph **`No format-by-timing interaction.`** (interaction null on all four post-condition outcomes, every effect at most \(|d_z|=0.06\), read as two additive main effects). Removed the interaction clause from the format/timing paragraph so it is said once. |
| 53 | no WIP prose | None left in 8.1–8.3. No new WIP sentence added. |
| 55 | "RQ's are not answered" | One line added: `% [AI: the nine RQs are answered one by one in tab:rq-answers, sec:disc-implications.]` No RQ answers written in 8.1 (WP5b owns the table). |
| 60 / 62 | "I divided into paragraphs" / "is this WIP?" | 8.2 rewritten as five short paragraphs (claim · personality · demographics · what the null means for the user · sample caveat). Stale `% [AI: …]` note replaced with the estimated-family note. |
| 80 | "erase this claim" | `The pipeline is not dead.` paragraph **deleted**; the writing-minus-reading fact survives as one sentence inside the next paragraph. `% [AI: erased; …]` line added under Walter's comment. |
| 84 | title unintelligible | `No sustained advertisement-versus-none state.` → **`Condition-aggregated markers.`**; content kept, writing–reading sentence folded in. |
| 89 / 94 | destructive, kills the posterior α finding / drop the Fz θ clause | `Early versus late is not greater visual processing.` → **`Timing and posterior \(\alpha\).`** Finding first (posterior α lower early than late, the one confirmatory Dataset A Holm cell, relative θ the same way as exploratory support), depth confound stated **once** (no "ignores… ignores… ignores"), **Fz θ apples-and-pears clause dropped**, no "greater visual processing" phrase anywhere. |
| 97 / 101 | merge, caveman prose | `Early Explicit Onset.` + `The dull readings win.` merged into **`The explicit-early onset response.`** (two short paragraphs): one column, one slow-power tilt, the implicit mention shows nothing comparable and why; then the evoked-leak / ocular alternatives stated once as what the design cannot separate. "posterior α did not fall at onset" kept. The "before the text" / 0.49 s sentence **deleted**. |
| 112 | improve the title | `The pairwise sweep localises.` → **`Post hoc pairwise comparisons.`** |
| 116 | "lean? what the hell" | `A hypothesis, not a finding.` **deleted**, folded into the pairwise paragraph; "lean" replaced by "the Fz θ point estimates are negative in every comparison implicit late enters, none of them surviving Holm", then one sentence naming it a replication target. |
| results 585 | reconcile Katerina | WP1 numbers integrated into 7.3 + App E; `% [AI: reconciled on Gold N=54 …]` under his comment. |
| results 588 | "90% didn't notice implicit" | WP3 shares integrated into 7.2 + App E; `% [AI: Gold says about half, not 90% …]` under his comment (see §4). |

Also fixed in scope: `perturbed by of an ad insertion` → `perturbed by an
advertisement insertion` (8.3 opener); `The engagement indices are silent.`
→ `Silence of the engagement indices.` (noun-phrase rule).

## 2. New paragraph titles

8.1: `Notice as a manipulation check` (Walter) · `Perceived manipulation as
the main cost of advertisement.` (Walter) · **`Trust and credibility in a
short session.`** · **`Format, timing, and the outcomes each one moves.`** ·
**`No format-by-timing interaction.`** · `Temporal effects on memory and
trust.` (Walter) · **`Limits of the battery.`**

8.3: **`Condition-aggregated markers.`** · **`Timing and posterior
\(\alpha\).`** · **`The explicit-early onset response.`** · **`Silence of the
engagement indices.`** · **`Post hoc pairwise comparisons.`**

8.2 has no `\paragraph` heads (Walter's paragraph split is preserved).

## 3. Every number introduced, with its source

**Discussion 8.1** (all descriptive, WP3 report §1, `notice_recall_percentages.csv`):
about half did not report the implicit mention as sponsored (52 % / 56 %);
one in five to one in four for the banner (19 % / 26 %); four in ten reported
the banner and not the mention at the same turn (39 % / 41 %); reverse under
one in ten (6 % / 9 %); close to six in ten recognised the implicit mention
when cued (57 % / 59 %); more than eight in ten for the banner (87 % / 81 %);
more than half of the non-noticers still recognised the mention (55 % / 59 %).
Written as shares in words, not as digits, because Discussion interprets.

**Discussion 8.1, existing numbers unchanged**: ICC .39, third of a point,
two thirds of a point, point and a half, half a point, \(|d_z|\le0.06\)
(`tab:beh-planned`, `tab:beh-localisation`, results.tex:149).

**Discussion 8.2** (WP1 report §2): 60 personality cells / 0 Holm; 70 + 70
demographic cells / 0 Holm; "two or three people" sparse levels. Holm .44 is
in Results, not repeated in 8.2.

**Discussion 8.3**: no new number. 0.60 dB, 4.60 dB, \(|d_z|\le0.37\),
2–4 dB, 256 / 8 cells all pre-existing.

**Results 7.2** (WP3 report §1, verbatim counts with Wilson intervals):
6/54 (11 %, [5, 22]) · 47 (87 %) · 25/54 (46 %, [34, 59]) · 20/54 (37 %,
[25, 50]) · 44/54 (81 %, [69, 90]) · 40/54 (74 %, [61, 84]) · 21/54 (39 %) ·
22/54 (41 %) · 3 and 5 participants · 31, 32, 47, 44 of 54 (57 %, 59 %, 87 %,
81 %) · 55 % / 59 %.

**Results 7.3** (WP1 report §2): 0 of 70 with levels kept, 0 of 70 two-level,
regression agrees on every cell, nearest cued memory early − late by
familiarity Holm \(p=.44\), age not recorded, sparse education levels merged
or excluded.

**`tab:results-checks`**: row `Demographic factor screen on \(D_i\) & 54 & 48
& 0 & … & §app-beh-personality` → `Demographic moderation (mixed model) & 54
& 70 + 70 & 0 & five factors × three planned contrasts, two codings; nearest
cued memory early − late by familiarity, Holm \(p=.44\) & Table
\ref{tab:beh-demographics}`.

**Appendix E**: 18 raw \(p<.05\) of 440, 14 on two- or three-person levels,
two Holm survivors on the same two participants (WP1 §1). No participant IDs.

## 4. Where Gold disagrees with a Walter comment

1. **"90 % of people didn't notice implicit"** (results.tex:645). Gold: 52 %
   and 56 % per implicit condition. Written as "about half … against one in
   five to one in four for the banner", and `% [AI: Gold says about half, not
   90 % …]` added directly under his comment.
2. **"The implicit mentions are largely not recognised when re-shown"**
   (existing 8.1 prose, not a Walter comment). Gold contradicts it: 57 % / 59 %
   rated cued memory ≥ 5 for the implicit mentions and 80 % recognised at
   least one. The sentence was replaced by the positive version ("the mention
   was read and retained; what it was not was recognised as advertising while
   it was doing its work"). **This changes an inherited claim, not a number —
   WP11 should confirm.**
3. **"Remove the RQ3 sentence" (brief).** There is no RQ3 sentence left in
   8.2; WP7 had already stripped the label. The *fact* (task type is balanced
   by the Latin square, not modelled) is kept without an RQ number, as WP7 §6
   asks.
4. **Trust wording.** Walter's "trust does not seem to decrease" is honoured
   as the paragraph's claim, but the post hoc explicit-early drop (−0.69,
   Holm .031) is kept in the same head, so the section says both.

## 5. Cross-file notes for WP5b / WP8 / WP9 / WP11 / WP12

- **New labels now live**: `fig:beh-notice-percentages` (7.2),
  `tab:beh-notice-percentages` (App E.1), `fig:beh-demographics` (7.3),
  `tab:beh-demographics` (App E, personality section). Both `\input`ed
  snippets are complete `table[H]` environments; no wrapper was needed.
- **8.2 no longer says "collapsed screen, 0 of 48"**; that sentence is gone
  from 7.3, App E and `tab:results-checks`. Anyone quoting 48 tests is stale.
- **User-centric sentences in 8.1 that the abstract (WP9) and the conclusion
  (WP8) should echo**, in priority order:
  1. "Trust holds up. It is Holm-null on all three planned contrasts, so in
     under an hour of use, with an advertisement in four conversations out of
     five, participants ended the session trusting the assistant about as much
     as they trusted it without advertisements."
  2. "The cost to trust is not spread across the design; it concentrates
     where the banner is both labelled and early, and the rest of the design
     leaves trust where it was."
  3. "An implicit mention therefore reaches a large share of users without
     being recognised as advertising, and those users rated a reply they did
     not read as sponsored."
  4. "A lower notice score is therefore not a discount for the user, it is a
     cost the user is less able to attribute."
  5. 8.2: "Who the user is does not change what the advertisement costs them."
- **8.3 sentences WP5b's Implications must stay consistent with**: "the moment
  of insertion registers in the neurophysiological record, not only in what
  participants report afterwards" (timing × posterior α) and "the two formats
  are not interchangeable at the moment of insertion, whatever the
  condition-aggregated markers say about the window as a whole". The depth
  confound is now stated exactly once, in 8.3; do not restate it in 8.6.
- **WP12**: `labellings` still appears at `discussion.tex` line ~206
  (Limitations, WP5b's region) and in `appendix_f.tex`; not touched here.
  `composite` does not appear in 8.1–8.3.
- **WP11 fact-check targets** in what I wrote: the eight WP3 share sentences
  in 7.2 against `notice_recall_percentages.csv`; the 70 + 70 / Holm .44 line
  in 7.3 against `demographic_moderation_lmm.csv`; "every interaction effect
  is at most \(|d_z|=0.06\)" against results.tex:149.
- No LaTeX compiler is installed in this environment, so the edits were
  checked by balance scan only (figure/table/`\(`/brace counts balanced in all
  three files). A compile is still owed before Walter sees the PDF.
