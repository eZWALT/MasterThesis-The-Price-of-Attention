# Context — Publication taxonomy, terminology, and writing handover

Written 6 August 2026 after pulling Overleaf mirrors and iterating the
Theoretical Foundations taxonomy and attention-shift framing with Walter.

## Source of truth (mandatory)

**Only the LaTeX documents in the Overleaf Git repositories are authoritative.**

- Publication: `docs/overleaf/publication/` (especially `main.tex`,
  `bibliography.bib`, `glossary.tex`, `Figures/`).
- Thesis: `docs/overleaf/thesis/`.
- Other mirrors: `presentation/`, `angela-paper/`, `example-eeg/`.

This file and other `.agents/context/writing/` notes are handovers. If they
disagree with Overleaf, **trust Overleaf**. Pull before editing. Never treat a
chat draft, plan file, or agent summary as the manuscript.

## Overleaf topology

```text
docs/overleaf/
├── publication/     # NeurIPS-style paper; current push focus
├── thesis/          # dissertation
├── presentation/    # slides
├── angela-paper/    # teammate ACL/EEG reference
└── example-eeg/     # EEG report template
```

Each folder is its own Overleaf Git remote. Parent `git status` is silent about
mirror dirtiness.

Publication HEAD at this handover (after pull): `d698eca`.
Thesis HEAD at this handover (after pull): `5188039`.

## Canonical experimental terminology

Use Walter’s current labels:

| Concept | Canonical wording |
|---|---|
| Format 1 | **implicit** advertisement (woven into assistant response) |
| Format 2 | **explicit** advertisement (structurally/visually distinct unit) |
| Early timing | turn 2 |
| Late timing | turn 4 |
| Control | no-advertisement condition |
| Design | five-condition repeated-measures (2×2 format×timing + control) |

**Implicit ≠ subliminal.** Implicit means integration, not below-threshold
awareness. Older publication placeholders and some Method leftovers may still
say “integrated inline / labelled block” or “subliminal”. Paper names are
implicit / explicit. Clean leftover Overleaf wording only with
explicit approval and after pulling.

Older handover (31 July) preferred “integrated inline / labelled advertising
block.” That preference is **superseded** by Walter’s 6 August instruction to
use **implicit / explicit**.

## Publication draft maturity (verify in Overleaf)

Rough state of `publication/main.tex` as of the 6 August pull—re-check after
any Overleaf edit:

- Title: *The Price of Attention: Behavioral and EEG Responses to Advertising
  in LLM Conversations*
- Abstract: draft present; colleagues invited to iterate
- Introduction + Related Work: largely written; Related Work includes Yun et al.
  Neuron Auctions
- Theoretical Foundations: stub (taxonomy list incomplete; attention shift TBD)
- Research questions: clustered RQs; H1–H3 already use implicit/explicit
- Method: expanded (architecture figure, lab/crowd workflows, EEG bronze→gold);
  still mixed red TODOs and duplicate paragraphs
- Results / Discussion: mostly placeholders
- Future Work: drafted
- Sample sizes stated in draft: L=19, C=36, N=55 (confirm against frozen
  behavioural exclusions before treating as final)

Colleague ping comments remain in the TeX (Sebastian / Katerina). Use the
pre-holiday window for abstract tone, Intro register, RQ/hypothesis cuts, and
ethics ID.

## Theoretical Foundations: settled architecture

Section order in Theory (conceptual dependency, not length):

1. Conversational intent and intent trajectories
2. Conversational attention shift + semantic trajectory shift
3. Taxonomy of advertisement instances
4. Company advertising policy \(\Pi=(\Gamma,\mu,\pi)\)
5. Position of the present study

### Taxonomy vs policy boundary

Operational test:

> If the same advertising artifact is delivered at a different turn, to a
> different user, or a different number of times, its taxonomy does not change;
> its policy configuration changes.

**Taxonomy (intrinsic ad instance)** \(a=(o,e,r,p,m,\delta)\):

- \(o\) influence target (Qiu & Mei: product exposure → framing → behavioural
  redirection → preference shaping; adapted with attribution)
- \(e\) explicitness: implicit / explicit
- \(r\) appeal: rational/informational vs emotional/transformational
- \(p\) realised personalisation
- \(m\) modality
- \(\delta\) realised disclosure (not vague “transparency”; independent of
  explicitness)

**Policy** \(\Pi=(\Gamma,\mu,\pi)\):

- \(\Gamma\) governance: allowed formats, disclosure rules, privacy, frequency
  caps, welfare/safety weights
- \(\mu\) implementation mechanism: surface insertion, RAG/context, prompt/token
  steering, fine-tuning/neurons, agentic tools (company-level policy, not
  taxonomy)
- \(\pi\) online serving rule with delivery \(d=(i,t,f,g)\): initiative, timing,
  frequency, targeting/matching

**Outcomes** (outside taxonomy): trust, usefulness, intrusiveness, recall,
semantic trajectory shift, EEG, revenue, clicks.

### Study mapping

- Manipulated taxonomy factor: **explicitness** (implicit vs explicit)
- Manipulated policy factor: **timing** (turn 2 vs turn 4)
- Control: \(\pi(\cdot)=\emptyset\)
- Fixed approx.: product exposure, informational appeal, text UI,
  system-initiated, ≤1 ad per condition, task-contextual matching

A LaTeX draft for taxonomy/policy was proposed in chat (6 August); it is **not**
in Overleaf until Walter approves and an agent applies it.

## Attention shift / semantic trajectory shift

Terms:

- **Conversational attention shift:** higher-level construct (redirection of
  conversational goals after commercial intervention).
- **Semantic trajectory shift (STS):** observable embedding-based
  operationalisation of user-text change. Not latent cognitive attention; not
  EEG attention.

Local STS after ads needs a post-ad user chat message. Turn-4 ads have none.
Do not invent that message.

Complementary estimands (analysis design; Methods must freeze exact metrics
against code):

1. Primary local STS: early ads only vs matched no-ad turn-2 pseudo-events.
2. Secondary terminal semantic outcomes from ≤256-char findings
   (`condition_conclusion_submitted`): task alignment \(A_{\mathrm{task}}\) and
   candidate-adjusted commercial pull \(P_{\mathrm{ad}}\) for all timings;
   conclusion screen re-shows the task prompt (prompt-cued).
3. Assistant-side displacement at ad/pseudo-ad turns.
4. Questionnaire, recall, EEG as downstream outcomes; EEG×text exploratory.

## Early-ad pair inventory (planning counts, not frozen N)

After globbing all three JSONL filename schemes under
`src/project/logs/production/`:

| Source | Intact early-ad → next-user-message pairs |
|---|---|
| Beta testers (12 sessions) | 21 |
| Crowd-labelled folders | 81 |
| Lab-labelled folders | 38 |
| Total production | 140 |
| Minus synthetic | 138 human-origin before exclusions |

Likely clean completed primary cohort ≈ 49 participants / 98 pairs; behavioural
exclusion ledger decides the final N. Participants—not pairs—are inferential
units.

Inclusion hierarchy:

1. Primary: eligible production; unfinished runs may contribute intact pairs
   under pre-frozen available-case rules.
2. Sensitivity: beta/legacy with cohort or protocol terms; not pooled only to
   chase significance (demand characteristics; pilot 5-turn protocol).
3. Metric development only: synthetic/development runs.

Power note: ~49 participants is adequate for moderate paired effects
(\(d\approx0.4\) near 80%); adding ~10 beta testers gains little power relative
to bias risk.

Verify counts against current logs if collection continued after this note.

## Writing preferences (unchanged)

From the 31 July Overleaf handover, still in force:

1. Pull Overleaf before drafting or editing.
2. Show proposed text before applying.
3. Push only after Walter explicitly approves.
4. When merging thesis → publication, preserve content faithfully; do not
   compress evidence-rich sections into thin syntheses.
5. Do not force-push Overleaf projects; preserve concurrent Overleaf edits.

## Related prior writing context

- `2026-07-31-overleaf-literature-merge-and-writing-preferences.md` — Related
  Work merge history and workflow (terminology for formats partly superseded
  by this note).
- Analysis constraints that affect writing claims:
  `.agents/context/data-analysis/` (especially north star and behavioural/EEG
  ownership).

## Next writing steps (when Walter asks)

1. Pull `docs/overleaf/publication/`.
2. Propose Theory section LaTeX in chat (intent → STS → taxonomy → policy →
   study map); apply only after approval.
3. Align Intro/Related Work wording to implicit/explicit.
4. Clean Method subliminal leftovers with approval.
5. Do not commit/push Overleaf unless requested.
