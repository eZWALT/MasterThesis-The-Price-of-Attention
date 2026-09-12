# WP8 — Conclusion (Chapter 9)

Date: 11 September 2026. Owner: `claude-opus-5-thinking-high`. Status: **done**.
File edited: `docs/overleaf/thesis/chapters/conclusion.tex` **only**, by targeted
`StrReplace`. Diff +35 / −62. All three `% WALTER:` lines intact
(`git diff | rg "^-.*WALTER"` is empty). Nothing committed, nothing pushed.

Structural checks (no TeX toolchain here): `\(`/`\)` 25/25, braces 32/32, one
`itemize` with six `\item`s matching the new "six complementary directions",
seven `\paragraph` heads. Both `\autoref` targets verified to exist:
`sec:intro:research-questions` (`introduction.tex:56`), `tab:rq-answers`
(`discussion.tex:251`). A compile is still owed.

---

## 1. Kept verbatim

- **Jacket, paragraph 1** (`% WALTER: I remember we cooked this jacket section
  text`): unchanged except **one appended sentence** making the user-centric
  frame explicit, as the voice rule requires: *"The perspective throughout is
  the user's: what an advertisement placed inside the conversation costs the
  person having it, rather than what it yields the advertiser or the platform."*
  Nothing else in that paragraph was touched; \(\lambda\), \(N=54\), \(n=18\)
  and the 32-channel EEG clause stand as written.
- **Jacket, paragraph 2** ("The contribution is therefore not a definitive
  model…"): untouched.
- **The "beyond conclusion" artifacts paragraph**: untouched; it only gained a
  `\paragraph{Reusable artifacts.}` head (spelling matched to the body, which
  says *artifacts*).
- **Future Work**: opening paragraph, and the bullets *Extending the
  experimental space*, *Personalisation and long-term interaction*, *Response
  degradation and attention*, *Retrieval and system evaluation*, *Cross-lingual
  evaluation* — all Walter's, all kept, with only the two additions in §3.
- **All three `% WALTER:` comments** kept exactly where they were.

## 2. Added — the five findings paragraphs (§9.1 Summary)

One lead sentence, then one `\paragraph` per analysis in Chapter 7 order, each
ending in a prescription that is about the user's welfare or about measurement,
never about how to serve. Order: behavioural · personality and demographics ·
neurophysiological · genre trajectories · cross-family association. Then two
closing heads.

| Head (short noun phrase) | Carries |
|---|---|
| *(lead sentence)* | five analyses below; the nine RQs are answered one by one in `tab:rq-answers` |
| `The user-side cost of an advertisement.` (2 paragraphs) | manipulation \(+1.27\); banner > mention, early > late; trust holds up (Holm-null on all three planned contrasts); its one drop is the early banner \(-0.69\); credibility \(-0.33\) early − late; no interaction on the four post-condition outcomes. Prescription: **disclosure, not placement** — the mention is not the cheap option, about half did not report it as sponsored, a lower notice score is a cost the user is less able to attribute |
| `Who the user is.` | personality 0 of 60 on the **four post-condition outcomes**; the five background factors 0 of 70 and 0 of 70 (two-level coding), on those outcomes **and cued memory**; the word used is **moderation**, explicitly "not mediation"; one caveat (n modest; a null interaction is not equivalence). Prescription: no trait or demographic profile is the group for whom advertising is cheap, and experience with these systems is not a discount |
| `The moment of insertion.` (2 paragraphs) | two estimands named; Dataset A separates neither any-ad nor format, one corrected cell posterior \(\alpha\) \(-0.22\)~dB early − late, **depth-confounded**; Dataset B eight confirmatory cells Holm-null, exploratory slow-power tilt after an early banner that the mention does not produce; positive control Fz \(\theta\) \(+0.60\)~dB, so the null is about the estimand, not the instrument. Prescription: lock to the onset; the tilt recommends neither presentation |
| `Genre trajectories as a measure.` (2 paragraphs) | no declared contrast separates an advertising condition from its control; 9 aligned shifts against 10.46 expected; Walter's scarcity/proprietary-data diagnosis kept; short later turns + **heavy** overlap (98 of 156 products labelled general guidance). Prescription: failure report — a genre shift cannot be an annotation-free proxy until such a model is shown to detect the insertion |
| `Trust and the response at onset.` | one of the six declared behaviour–EEG pairs survives: \(\rho=.80\) \([.48,\,.93]\), \(n=18\), against \(\rho=.24\) under condition aggregation; neither mean moves, so what couples is people; caveat (18 people, lower bound \(.48\), single trust item) → hypothesis about individual sensitivity. Prescription is user-side: the cost is not spread evenly, and the users who respond most at the moment are the users whose trust is most at stake |
| `The overall picture.` | Walter's notebook register: a real user-side cost, smaller than the debate suggests; felt pressure and a small credibility loss, not a trust collapse and not a hijacked conversation; unevenly placed (early labelled banner · at the insertion · some users more than others). For a platform that wants to keep trust: **not a placement rule but an obligation to disclose and to measure**. For users: an advertisement they can recognise, and argue with, is worth more than a recommendation offered as advice with no receipt |
| `Reusable artifacts.` | Walter's existing paragraph, head added |

## 3. Added — Future Work

1. **New bullet, `Onset-locked measurement of the user response.`** (placed
   second, after *Extending the experimental space*). Absorbs WP5b's three
   prescriptive sentences moved out of Chapter 8 (§5 items 1–3) and the
   Limitations → Future Work moves (item 4): lock to onset for a format
   contrast; lock to onset **and ask for trust per advertisement** for the
   trust relation; fix the pair of measures in advance; more than eighteen
   participants; log the visual onset of a written-in mention in the client
   instead of reconstructing it; a dedicated electro-oculogram channel; more
   than one insertion per cell. Eye tracking was **not** repeated here — it
   already lives in Walter's *Response degradation and attention* bullet.
2. **One sentence appended to `Personalisation and long-term interaction.`**
   (WP5b §5 item 5): a session of under an hour cannot see the trust a user
   withdraws once they recognise, after longer familiarity, that a piece of
   advice was an advertisement — the horizon on which the labelled banner may
   compare better than it does here. Placed there rather than in a new bullet
   so the section stays coherent instead of becoming a dump.
3. "five complementary directions" → **"six"**.

WP5b's item left in place by judgement (Walter's "The theory has to be refined
with the engineering…" sentence in 8.4) was **not** moved; it still reads as a
diagnosis, and the trajectory prescription in 9.1 covers the work plan.

## 4. Removed

| ID | What was removed |
|---|---|
| **F26** | The whole Dataset A paragraph: "the response depends on how and when the advertisement enters the conversation"; relative \(\theta\) presented as part of the "clearest confirmatory distinction"; "greater visual processing than otherwise equivalent later insertions". Replaced by the two-estimand paragraph with posterior \(\alpha\) as the single corrected cell and the depth confound stated as its caveat. |
| **F27** | "The corresponding implicit intervention produces a substantially weaker response"; "demand a stronger immediate allocation of neural processing"; the entire *price of attention* / explicit-late-as-"attractive compromise" policy paragraph; and the commented salience–intrusion trade-off draft that followed it. No direct format verdict is now claimed; the tilt is stated in the same words Chapter 8 uses ("a slow-power tilt that the written-in mention does not produce"). |
| **F29** | "a product inventory whose predicted genres only weakly overlap with the conversational genres" → the advertised products **overlap the conversational background heavily**, 98 of 156 labelled general guidance, which is why an aligned shift cannot be told apart from a chance one. The banned word *inventory* is gone. |
| **F30** | The moment scorer \(m(s)\) and ad scorer \(q(s,a)\) sentence. The idea is kept generic: "one model would score insertion moments from the conversational state, and another would rank candidate advertisements for the moment chosen." Added `% [AI: ad-moment scorer held back until after 17 Sep per AGENTS.md]` — the only `% [AI: …]` line in the file. |
| **F28** | The queued behavioural draft comment (never rendered) is deleted, so "the format participants failed to recognise when it was shown again" cannot re-enter. The rendered text now says the opposite and correct thing: about half did not report the mention as sponsored, **and most recognised it once it was shown again**. |
| Slop comments | `%%%%%%%%%%% THE STRUCTURE IS CLEAR…` (3 lines), `% Behavioural (WIP)` + the 17-line `% [TODO behavioural]` draft, the 11-line `% [TODO combos]` draft, the `% EEG` / `% Combos` / `% Trajectories` stub markers, `%%%%%% Final prescriptions summary`, `%%%%%% BEYOND CONCLUSION`, and the commented trade-off paragraph. Lint is clean for: `TODO`, `price of attention`, `depends on how and when`, `visual processing`, `allocation of neural`, `captured attention`, `compromise`, `m(s)`, `q(s,a)`, `weakly overlap`, `card`, `composite`, `k=37`, `labelling`, `MDE`, `approached significance`, `BH`/`Benjamini`. |

Also gone: the `\\` line-break hack between summary paragraphs (replaced by
`\paragraph` heads), and the American "summarized below" duplication.

## 5. Every number, with its source

| Number | Where | Source |
|---|---|---|
| \(N=54\), \(n=18\), 32 channels, five conditions | jacket (unchanged) | `results.tex` §7.1 |
| manipulation any ad \(-\) no ads \(+1.27\), seven-point scale | user-side cost | `tab:beh-planned` (`confirmatory_planned_D.csv`) |
| banner > mention and early > late on manipulation | user-side cost | `tab:beh-planned`: implicit \(-\) explicit \(-0.62\); early \(-\) late \(+0.58\) |
| trust Holm-null on all three planned contrasts | user-side cost | `tab:beh-planned` trust block (`.153`, `.405`, `.063`) |
| trust \(-0.69\) under the early banner | user-side cost | `fig:beh-localisation`, results.tex:161 (Holm \(p=.031\)) |
| "the condition that feels most manipulative" | user-side cost | results.tex:161 ("largest under explicit early"); `tab:beh-localisation` \(+1.92\) |
| credibility "a third of a point" early \(-\) late | user-side cost | `tab:beh-planned` \(-0.33\), Holm \(.017\) |
| no interaction on the four post-condition outcomes | user-side cost | results.tex:149, \(|d_z|\le0.06\) |
| "about half … did not report it as sponsored" | prescription | `notice_recall_percentages.csv` / WP3: 52 %, 56 % |
| "most of them recognised it once it was shown again" | prescription | results.tex:179: cued memory \(\ge5\) for 57 % / 59 % implicit; 55 % / 59 % among non-noticers |
| personality 0 of 60, four post-condition outcomes | who the user is | `personality_lmm.csv`, results.tex:199 (F02 scope respected) |
| demographics 0 of 70 and 0 of 70, five factors, incl. cued memory | who the user is | `demographic_moderation_lmm.csv`, results.tex:204 |
| posterior \(\alpha\) early \(-\) late \(-0.22\)~dB | moment of insertion | results.tex:245, `tab:results-summary` (Holm \(p=.0496\)) |
| eight Dataset B confirmatory cells Holm-null | moment of insertion | results.tex:245, `tab:results-summary` |
| Fz \(\theta\) writing \(-\) reading \(+0.60\)~dB | moment of insertion | `tab:eeg-task-state` (Holm \(p=.007\)) |
| nine aligned shifts against 10.46 expected | trajectories | `tab:traj-aligned-counts`, `tab:results-summary` |
| 98 of 156 served products labelled general guidance | trajectories | results.tex:424; WP11 F29 |
| \(\rho=.80\), 95 % CI \([.48,\,.93]\), \(n=18\); \(\rho=.24\) | trust at onset | `tab:results-summary`, `declared_families.csv` (Holm-within-six \(p=.0004\)) |
| "one of the six behaviour–EEG pairs" | trust at onset | `tab:results-summary` row *Behaviour \(\times\) EEG*, 6 tests |
| "more than eighteen participants" | future work | descriptive, from the EEG cohort size |

No Holm \(p\) is printed in the Summary prose (the tables and `tab:rq-answers`
carry them), no CI other than the one that carries its sentence, and no number
was invented or re-rounded.

## 6. Sentences the abstract (WP9) should echo

In priority order, all now rendered in Chapter 9:

1. Jacket: "The perspective throughout is the user's: what an advertisement
   placed inside the conversation costs the person having it, rather than what
   it yields the advertiser or the platform."
2. "Advertisements were noticed and they were felt as commercial pressure, and
   that is where their cost to the user registers."
3. "Trust held up. It is Holm-null on all three planned contrasts, so after
   under an hour of use … participants ended the session trusting the assistant
   about as much as they trusted it without advertisements."
4. "A lower notice score is therefore not a discount for the user; it is a cost
   the user is less able to attribute."
5. "Neither personality nor background changes what an advertisement costs the
   user."
6. "The neurophysiological cost of an advertisement in this design is measurable
   at the moment the advertisement appears."
7. "Neither mean moves, so what couples here is people rather than conditions:
   an average that stays flat can still hide the participants whose trust
   falls."
8. "An advertisement inserted into one of these four-turn conversations did not
   visibly redirect what the user asked next."
9. Overall: "felt commercial pressure and a small loss of credibility, not a
   collapse of trust and not a conversation steered towards the product … It
   concentrates on the labelled banner arriving early."

WP9 must not import: any *price of attention*, any explicit-late compromise,
"presentation matters" as a corrected verdict (only the exploratory tilt), or
relative \(\theta\) as confirmatory (F24–F27).

## 7. Open for Walter

1. **Jacket sentence.** One sentence was appended to your golden paragraph
   because the voice rule requires the Conclusion to say the study is
   user-centric. Delete it if you prefer the jacket exactly as it was — the
   frame is also carried by `The overall picture.` and by 8.6's opener.
2. **RQ count.** The Summary now points at `tab:rq-answers` for the nine
   questions instead of listing verdicts; the jacket still does not state a
   count, which reads better. Say the word if you want "nine research
   questions" in the jacket itself.
3. **Six directions.** Future Work grew from five to six bullets. If you would
   rather keep five, the onset-locked bullet folds into *Extending the
   experimental space* at the cost of a longer bullet.
4. **`m(s)` / `q(s,a)`.** Removed for the 17 September hard stop, not because
   the decomposition is wrong. The generic sentence is a one-line restore after
   the deadline if you want the notation back.
