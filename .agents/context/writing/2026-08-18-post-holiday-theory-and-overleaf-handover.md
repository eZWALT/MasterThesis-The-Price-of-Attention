# Context — Post-holiday theory, Overleaf, and writing handover

Written 18 August 2026 after Walter returned from holidays. This dump
records Theoretical Foundations decisions, Overleaf commits, citation
plans, Future Work gaps, and the remaining manuscript attention map.

**This file does not override LaTeX.** If it disagrees with Overleaf,
trust Overleaf. Pull `docs/overleaf/publication/` before drafting or
editing.

Related prior writing notes:

- `2026-08-06-publication-taxonomy-and-writing-handover.md` — still
  useful for experimental labels, STS/late-ad estimands, and sample
  planning counts. Several theory details below **supersede** that note.
- `2026-07-31-overleaf-literature-merge-and-writing-preferences.md` —
  workflow still in force; format labels superseded by implicit/explicit.
- Interactive remaining-work checklist (not source of truth):
  `~/.cursor/projects/home-wtroi-MasterThesis-RAG-RecSys/canvases/publication-manuscript-attention-map.canvas.tsx`

## Source of truth (mandatory)

Only the Overleaf Git repositories under `docs/overleaf/` are
authoritative for manuscript content, especially:

- `docs/overleaf/publication/main.tex`
- `docs/overleaf/publication/bibliography.bib`
- `docs/overleaf/publication/glossary.tex`
- `docs/overleaf/publication/Figures/`

Chat drafts, plan files, canvases, and this handover are working memory.

## Overleaf state at this dump

Publication remote: `https://git.overleaf.com/69bc4212f5ce9e2503edc596`

Publication HEAD after push on 18 August 2026: **`9aed03f`**.
Thesis HEAD: **`dfc7dc3`**. Both bibliographies now share the same
66 keys. Catalog cite is `hou2024bridging` (Amazon Reviews 2023).
Timing subsection is written (turn 2 vs 4). Pull before any further
edit.

Notation settled and in Overleaf:

- Instances are angle-bracket tuples:
  \(a_k=\langle\iota,(\alpha,\epsilon),(\sigma,\lambda,\theta),\phi\rangle\).
  Inner pairs/triples stay in parentheses.
- Null advertisement is \(a^{\emptyset}=\emptyset\)
  (`eq:ad-null`), the same value as
  \(a_k\in\mathcal{A}\cup\{\emptyset\}\) in §3.1. Do not write an
  empty tuple. Do not use \(a^{\mathrm{no}}\) or \(\epsilon\) (the
  latter is Heineking explicitness).
- Study instances: \(a^{\mathrm{imp}}\), \(a^{\mathrm{exp}}\),
  \(a^{\emptyset}\). They differ in \((\lambda,\theta)\); timing is
  \(\pi\). Do not write four instances.

Relevant local-agent commits (all pushed):

| Commit | What it did |
|---|---|
| `0f27bf6` | Numbered Theory equations; pinned taxonomy table with `[H]`; renamed intent-to-genre map from \(\Gamma\) to \(\kappa\) |
| `de23ce7` | Demoted introductory definitions and the shift-inclusion inequality to unnumbered display |
| `4a1364f` | Morphological taxonomy table (symbol / dimension / question / levels) |
| `90d4f6e` | Concurrent Overleaf edit (Walter); pull before any new edit |

Writing workflow still in force: pull → show proposed text → apply only
after approval → push only when Walter asks.

## Canonical experimental terminology (unchanged)

| Concept | Canonical wording |
|---|---|
| Format 1 | **implicit** advertisement (woven into assistant response) |
| Format 2 | **explicit** advertisement (structurally/visually distinct unit) |
| Early | turn 2 |
| Late | turn 4 |
| Control | no-advertisement condition |
| Design | five-condition repeated-measures (2×2 presentation \(\lambda\) × timing + control) |

**Implicit ≠ subliminal.** Implicit means integration, not
below-threshold awareness. Method still contains subliminal-style
placeholders; do not treat those as current theory.

## Section 3.1 — Intent, genres, trajectories (in Overleaf)

Xu et al. (2026), *Ad Insertion in LLM-Generated Responses*, remains the
main engineering inspiration: intents are latent and intractable; genres
are a finite partition used as a bidding/coherence proxy. This paper
extends that idea from **allocation input** to **multi-turn observable
trajectory after exposure**.

Settled notation (verify in `main.tex`):

- Intent \(t\in\mathcal{T}\); needs \(n\in\mathcal{N}\) mentioned but
  unused in later maths.
- Genre partition (unnumbered): \(\kappa:\mathcal{T}\rightarrow\mathcal{G}\).
  **Do not use \(\Gamma\) for this map.** \(\Gamma\) is governance in §3.3.
- Conversation (unnumbered): \(C=(u_1,\ldots,u_T)\).
- Utterance (unnumbered): \(u_k\sim\mathcal{U}(t_k)\).
- Ad trajectory (unnumbered): \(\mathbf{A}=(a_1,\ldots,a_{T-1})\),
  \(a_k\in\mathcal{A}\cup\{\emptyset\}\).
- Classifier (unnumbered): \(f_\theta:\mathcal{U}\rightarrow\mathcal{G}\).
- Numbered core objects:
  - \(\hat{\mathbf{G}}\) genre trajectory (`eq:genre-trajectory`)
  - \(\delta_k\), \(N_{\mathrm{shift}}\) (`eq:genre-shift`)
  - persistence, frequency, \(N_{ij}\), diversity, entropy
  - \(\delta^{(a)}_k\) ad-associated genre shift
  - \(\tilde{\delta}^{(a)}_k\) genre-aligned ad-associated shift
- Unnumbered: \(\tau_k=(\hat g_k,\hat g_{k+1})\) and the inclusion
  \(\tilde{\delta}^{(a)}_k\leq\delta^{(a)}_k\leq\delta_k\).

**Keep \(\delta\) for shifts.** Walter confirmed. Taxonomy disclosure is
now \(\theta\), so there is no \(\delta\) collision.

**Attention shift** is reserved for a *causal* ad-associated genre shift.
Establishing causality is **outside the present work**. Do not equate
\(\delta^{(a)}_k\) with attention shift.

**Late-ad limitation (still true, still under-written in Theory):** local
\(\delta^{(a)}_k\) needs a post-ad user utterance. Turn-4 ads have none.
Do not invent that message. Complementary estimands remain: local STS /
genre shift for early ads vs matched no-ad pseudo-events; terminal
conclusion text for all conditions; assistant-side displacement;
questionnaire / recall / EEG.

Hard-label genre classification is the intended empirical centre (vs
soft labels), pending a frozen classifier in Method.

## Section 3.2 — Taxonomy (settled 18 August; Overleaf still older)

Overleaf `0690dad` already has the hierarchical tuple. Settled form:

\[
a_k=\bigl(\iota,\,(\alpha,\epsilon),\,(\sigma,\lambda,\theta),\,\phi\bigr)
\]

| Layer | Symbol | Dimension | Levels |
|---|---|---|---|
| Influence | \(\iota\) | influence target | product exposure; framing; redirection; preference shaping |
| Style | \(\alpha\) | appeal | rational/informational; emotional/transformational |
| Style | \(\epsilon\) | explicitness (Heineking) | covert; overt |
| Surface | \(\sigma\) | channel | text; image/video; audio/voice; multimodal; actionable |
| Surface | \(\lambda\) | presentation | implicit; explicit |
| Surface | \(\theta\) | realised disclosure | none; **on request**; nature disclosed; sponsor identified; rationale disclosed |
| Adaptation | \(\phi\) | realised personalisation | none; utterance; session; persistent; trait |

**Heineking reconciliation.** Their explicitness \(\epsilon\) is
rhetorical prominence of a *native* mention inside generated text
(covert vs overt wording). Our experiment varies presentation
\(\lambda\) (woven reply vs labelled unit). Do not cite Heineking as the
source of implicit/explicit. Implicit ≠ subliminal ≠ covert. Overleaf
Related Work still conflates Heineking covert/overt with
separated-vs-integrated presentation; fix that when rewriting §2/§3.2.

**Letters.** \(\epsilon\) is Heineking explicitness. \(\lambda\) is
presentation (name = presentation, not layout). \(\pi\) remains the
serving policy. Table columns: Layer / Dimension / Question / Levels.

**Why \(\phi\) and \(\theta\) are taxonomy, not policy**

If the same artefact is delivered at a different turn or to a different
user, taxonomy is unchanged; policy changes. \(\phi\) and \(\theta\)
describe the served artefact. \(\Gamma\) and \(\pi\) describe permitted
data and required disclosure.

### Realised personalisation \(\phi\) (nailed 18 August)

\(\phi\) is the **user evidence actually used to form the served
artefact**. It is not the retrieval stack and not the assigned scenario.

| \(\phi\) | User evidence in \(a_k\) | Anchor |
|---|---|---|
| None | Same creative regardless of user or utterance | generic / run-of-network |
| Utterance | Current message only | keyword / one-shot match |
| Session | This dialogue thread | Jannach ephemeral user model; OpenAI ads with personalisation off (current chat thread only) |
| Persistent | Other sessions, memory, or account history | Jannach long-term profiles; OpenAI ads personalisation on (other threads, memory, ad history) |
| Trait | Demographics or personality encoded in the creative | Meguellati personality-tailored ads |

**Task-contextual is not a level.** The simulated work task is the
shared information need (Borlund-style scenario). It is experimental
scaffolding, not evidence about *this user*. Drop “query-contextual,”
“task-contextual,” and “longitudinally personalised” as separate rungs.
Query ⊂ utterance. Longitudinal ⊂ persistent.

This experiment: \(\phi=\) **session**. Retrieval uses the current
utterance and the ongoing conversation. It does not use a stored
profile, memory, other conditions as user history, or BFI-10. OCEAN is
an outcome moderator, not an input to \(a_k\). Two participants on the
same task can still get different products because their session text
differs.

Cite in the table: `jannach2021crs`, `meguellati2025llmads`,
`openai_ads_chatgpt`. Add `jannach2021crs` to the bib if missing.

### Heineking \(\epsilon\) — held covert, not crossed (nailed 18 August)

Earlier draft said \(\epsilon\) was confounded with \(\lambda\)
(implicit≈covert, explicit≈overt). **That mixed layers. Drop it.**

Heineking covert/overt is wording prominence *inside a native generated
mention*. This study does not cross that factor.

- **Implicit** (`inline_persuasive`):
  `INLINE_INJECTION_PROMPT` requires a brief, factual mention and
  “do not sound salesy or promotional.” That is instructed **covert**
  register. The injector name `inline_persuasive` is leftover and
  misleading relative to the prompt.
- **Explicit** (`explicit_ad_block`): the assistant reply is not
  rewritten to mention the product. The banner is catalog title +
  generic CTA (`Discover More` / `Shop Now` / …), not Heineking-style
  overt native-ad prose. What marks it as an advertisement is the
  **Advertisement** header (\(\theta\)) and the separated chrome
  (\(\lambda\)), not salesy wording.

So \(\epsilon\) is **held at covert / factual** in both ad conditions.
A leftover CTA on the banner is ordinary UI chrome, not an overt
rhetorical level. Occasional implicit mentions that sound more
promotional than instructed are implementation leakage, not a designed
overt cell.

Do **not** write that the study manipulates Heineking explicitness.
The honest confound with \(\lambda\) is **\(\theta\)**, not \(\epsilon\).

### Realised disclosure \(\theta\) — add on-request (nailed 18 August)

“None” is too strong for the implicit condition. After any injection,
`POST_INJECTION_AWARENESS_PROMPT` stays in context: if the user brings
the product up, answer truthfully; otherwise do not mention it
(`src/project/core/config.py`, applied in `manager.py` for both ad
modes). That is not a visible label, and it is not concealment (Wu).

Treat \(\theta\) as the **strongest disclosure the served instance
makes available**, not only pixels at onset. Widen the table question
from “actually visible” to “made available to the user.”

| \(\theta\) | Meaning |
|---|---|
| None | Conceal even if asked, or no capacity to disclose |
| **On request** | Do not volunteer; answer truthfully if asked |
| Nature disclosed | Commercial nature labelled at exposure |
| Sponsor identified | Named payer |
| Rationale disclosed | Why this user / this ad |

This study: implicit \(=\) on request; explicit \(=\) nature disclosed
(header `Advertisement`). Neither names a sponsor or a targeting
rationale. Explicit also answers if asked; the standing level is the
stronger one (nature).

This is slightly more than “what is on screen at onset,” but
conversational ads need the extra rung. Tang’s users asked the chatbot
to stop advertising in natural language; that behaviour only makes
sense if disclosure can be elicited.

Do not call on-request “nature disclosed.” The implicit artefact still
has no banner.

### Study mapping (four ad conditions)

Implemented injectors: `inline_persuasive` weaves one product into the
reply; `explicit_ad_block` renders a labelled “Advertisement” banner
above the reply (`EXPLICIT_AD_LABEL` in `src/project/core/config.py`;
see also `src/project/README.md`, `workflow_b.md`).

| Coordinate | Value in this experiment | Status |
|---|---|---|
| \(\iota\) | product exposure (specific catalog items; Qiu tier 1) | held |
| \(\alpha\) | informational (instructed: brief, factual, not salesy) | held. Hedge only if claiming a coded appeal audit; the injector *name* `inline_persuasive` is misleading vs the prompt |
| \(\epsilon\) | covert / factual register in both ad conditions | **held**. Not crossed. Not confounded with \(\lambda\). See “Heineking \(\epsilon\)” above |
| \(\sigma\) | text / chat UI | held. The block has visual chrome and a CTA, but it is still a textual chat surface, not image, voice, or an agentic tool |
| \(\lambda\) | **implicit vs explicit** | **manipulated** |
| \(\theta\) | implicit: **on request** (no banner; truthful if asked). explicit: nature disclosed (`EXPLICIT_AD_LABEL = "Advertisement"`) | **confounded with \(\lambda\)**. Sponsor and rationale are not disclosed in either condition |
| \(\phi\) | session (current utterance + this dialogue) | held. Not persistent profile/memory; not trait-targeted. The assigned task is the information need, not a \(\phi\) level |

No-ad control: \(\pi\) returns \(\emptyset\); there is no \(a_k\).

Policy, not taxonomy: timing (turn 2 vs 4), system initiative, at most
one ad per condition, and \(\mu\) as server-side injection (inline
rewrite vs post-generation banner).

Honest closing sentence for the paper: the study varies presentation
\(\lambda\) in text, holds appeal \(\alpha\) and Heineking \(\epsilon\)
at an informational/covert register, and lets realised disclosure
\(\theta\) co-vary with \(\lambda\). Do not describe \(\epsilon\) or
\(\theta\) as independently crossed factors.

### §3.2 rewrite status

Hierarchy, on-request \(\theta\), two instances plus
\(a^{\emptyset}=\emptyset\), and angle-bracket tuples are **in
Overleaf** (`ea88acc`). Pull before any further edit.

Citations for the table:

- \(\iota\): `qiu2026generative`
- \(\alpha\), \(\epsilon\): Heineking; Puto; Nuweihed
- \(\sigma\): Qiu; `jannach2021crs` (add if missing)
- \(\lambda\): no Heineking cite
- \(\theta\): Tang; OpenAI ads
- \(\phi\): Jannach; Meguellati. Drop Zhao/Martina from the table.

## Section 3.3 — Company policy (in Overleaf, provisional)

\[
\Pi=(\Gamma,\mu,\pi)
\]

- **\(\Pi\)**: overall company advertising policy.
- **\(\Gamma\)**: governance constraints and objectives (eligibility,
  disclosure rules, privacy, safety, allowed mechanisms, welfare weights).
- **\(\mu\)**: intervention *architecture* / execution layer. It does not
  decide whether/which/to whom. Examples: post-generation insertion,
  retrieval/prompt, generation-time, neurons (Feizi, Duetting, Xu, Yun).
- **\(\pi\)**: online serving policy. May be rules, auctions, bandits, or
  later multi-objective RL. **RL is one possible implementation of
  \(\pi\), not of \(\Pi\).**

Boundary between \(\mu\) and \(\pi\) can blur; the split is an analytical
checklist, not an exhaustive theory. Do not re-introduce
\(d=(i,t,f,g)\) or a detailed \(\pi(\cdot)\) signature unless Walter asks.
That over-formalises a preview section.

**Section 3.4 (Position of the Present Study) was removed** as a
standalone subsection. The unique mapping — presentation \(\lambda\) is
taxonomic, timing is a serving-policy decision — should close §3.2 or
§3.3, not repeat the five-condition design already in the Research Gap.

## Equation numbering policy

`\numberwithin{equation}{section}` is on. Number only objects later cited
as estimators or compact claims:

Keep numbered: \(\hat{\mathbf{G}}\), \(\delta_k\), persistence/frequency
summaries, \(\delta^{(a)}\), \(\tilde{\delta}^{(a)}\), \(a=(\ldots)\),
\(\Pi=(\ldots)\).

Unnumbered display: \(\kappa\), \(C\), \(u_k\sim\mathcal{U}(t_k)\),
\(\mathbf{A}\), \(f_\theta\), \(\tau_k\), shift inclusion.

The Travel/Shopping run remains an unnumbered example.

## Future Work — needs a rewrite (not yet done)

Current Future Work (~two weeks old) is an engineering wishlist and
partly contradicts the Introduction (“this work does not focus primarily
on auction algorithms [or] intent clustering”).

Keep: ecological UI, languages, other taxonomic cells, degradation
metrics, eye-tracking later, RL as downstream \(\pi\).

Missing / must add:

1. Validate \(\hat{\mathbf{G}}\) and \(\delta^{(a)}_k\); late-ad
   follow-up utterance or terminal estimand.
2. Causal attention-shift is future work; \(\delta^{(a)}\) is association.
3. Open cells of \(a\) and of \(\Pi\) named with the new symbols
   (\(\epsilon\times\theta\), \(\alpha\), \(\phi\), \(\sigma\), initiative,
   frequency, comparisons of \(\mu\)).
4. Personalisation through \(\Gamma\) / \(\pi\) / \(\phi\), not as a
   vague “OCEAN memory” blob.
5. Open genre classifiers and human agreement; not “optimize bidding.”
6. Learned \(\pi\) under \(\Gamma\) through \(\mu\); do not claim this
   paper already built quality policies.
7. EEG next steps: ocular/ICA sensitivity, onset uncertainty / no ERP,
   larger EEG \(n\), incremental value over questionnaires and
   trajectories.
8. Dataset reuse if the open-data contribution is retained.
9. Tone down “alleviate this burden”; fix typos; drop “visibility.”

Suggested order: trajectories/late ads → remaining cells of \(a\) and
\(\Pi\) → EEG limitations then eye-tracking → ecological/language →
quality benchmarks → downstream learned \(\pi\).

Rewrite Future Work only after the approved §3.2 text is in Overleaf, so
vocabulary matches.

## What is still missing in the rest of the paper

Theory 3.1–3.3 is the strongest new material. The rest of the manuscript
is not submission-ready. Highest-attention items (see also the canvas):

- Freeze contribution set and tier/cut the 14 RQs (eye-tracking is not
  an empirical RQ; predictive model may be overclaimed).
- Align RQ2/RQ6 with genre trajectory / \(\delta^{(a)}\), not latent
  “intent trajectory” or causal attention shift.
- One canonical design everywhere: implicit/explicit × early/late +
  no-ad. Kill NO/IN/BL/EA/LA and subliminal Method text.
- Write Statistical Analysis; participant is the inferential unit.
- Behavioral instruments, recall, trajectory method, terminal semantic
  outcomes, exclusion ledger.
- EEG Method must match the spectral pipeline (not ERP boilerplate);
  EEG analysis cohort is n=18, not enrolled L=19.
- Results, Discussion, Conclusion are still templates.
- Broken cites (`raw...`, `cite-of-arxiv-thesis`), possible
  `bibliography.bib` trailing prose, ethics/funding XXXXX.
- Research Gap still needs a conceptual paragraph (intent-as-allocation
  vs post-ad trajectories; taxonomy vs policy) if Walter wants that in
  §2.1 rather than only in Theory.

Sample sizes in the draft (L=19, C=36, N=55) remain planning figures
until the behavioural exclusion ledger is frozen. Verify against
`.agents/context/data-analysis/`.

## Xu et al. (2026) — what we inherited vs what we added

Inherited: fleeting conversational intents; genres as partition of
\(\mathcal{T}\); decoupling insertion from generation; decoupling
bidding from raw queries; contextual coherence; welfare triad.

Added / not in Xu: multi-turn user genre trajectory after exposure;
ad-associated vs causal shift; morphological ad-instance taxonomy;
company policy \(\Pi\) broader than a learned serving rule; human
factorial UX × timing × EEG study.

Do not cite Xu as having “proven” ethics of decoupled insertion.

## Agent working rules for the next session

1. Pull publication Overleaf.
2. Prefer this note, then the 6 August writing handover.
3. Next writing tasks Walter already queued:
   - Apply the hierarchical §3.2 rewrite
     \(a_k=(\iota,(\alpha,\epsilon),(\sigma,\lambda,\theta),\phi)\)
     plus Jannach bib, then push if asked.
   - \(\lambda\) is the manipulated taxonomic factor. \(\theta\)
     co-varies with \(\lambda\). \(\epsilon\) is held covert in both
     ad conditions. \(\phi=\) session. Task is not a \(\phi\) level.
   - Rewrite Future Work in the new vocabulary.
   - When touching Related Work, stop mapping Heineking covert/overt
     onto separated-vs-integrated presentation.
4. Do not commit parent-repo `.agents/` files unless asked.
5. Do not push Overleaf unless asked.
