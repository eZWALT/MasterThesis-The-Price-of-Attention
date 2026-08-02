# Context — Overleaf literature merge and writing preferences

Written 31 July 2026 after reconciling and pushing the publication's Related Work
section. This is a handover for future agents and collaborators. It records both the
technical state of the Overleaf mirrors and the author's preferred writing workflow.

## Repository topology

The parent repository and the Overleaf mirrors are separate Git repositories:

```text
MasterThesis-RAG-RecSys/
├── docs/overleaf/thesis/       # independent Overleaf Git repository
├── docs/overleaf/publication/  # independent Overleaf Git repository
└── docs/overleaf/presentation/ # independent Overleaf Git repository
```

The parent repository ignores the mirror contents. A clean parent `git status` says
nothing about whether an Overleaf mirror is clean or current. Always run Git commands
inside the relevant mirror.

## Current Overleaf state

Both thesis and publication were pulled from Overleaf on 31 July before the final
merge.

- Thesis fast-forwarded from `00c3d47` to `e8aeb8e`.
- Publication fast-forwarded from `2458055` to `6a342bb`.
- A first, overly compressed publication Related Work was pushed as `a226bb0`.
- A concurrent Overleaf edit was then pushed as `e2ceb79`; it added colour-state
  markup around Related Work and was preserved during the correction.
- The faithful expanded Related Work was rebased on top and pushed as:
  `b22b468 Expand publication related work faithfully`.
- At handover, the publication mirror was clean and synchronized with `origin/main`.
- The thesis mirror was also clean and synchronized. No final literature rewrite was
  pushed to the thesis.

## What the publication Related Work now contains

The final publication section is intentionally faithful to the source material in
`thesis/chapters/related_works.tex`, especially its `Publication Related Work`
section. It preserves the original sequence, papers, examples, and reported
statistics while correcting grammar and using more academic transitions.

The sequence is:

1. LLMs as conversational information interfaces.
2. Dataset limitations and NaiAD.
3. Engineering foundations: Feizi, Duetting, Xu, and Qiu.
4. Advertising-style taxonomy: explicitness and type of appeal.
5. LLM advertisement quality: Meguellati and Zelch.
6. Big Five/OCEAN foundations and personality-aware CRS work.
7. Tang et al.'s chatbot advertising study and questionnaire relevance.
8. Detection and persuasion: Salvi, Heineking, and Schmidt.
9. Commercial conflicts of interest: Wu, Erickson, and OpenAI policy.
10. LLM–EEG work: Zhang, Kosmyna, NeuroChat, and Subramanian.
11. Neuromarketing: Quiles Pérez and Afshar.
12. The LLM–advertising–EEG research gap and user-centred motivation.

The accepted taxonomy treats explicitness and appeal as independent dimensions:

- Explicitness: overt/separated/disclosed versus covert/integrated.
- Appeal: informational/rational versus transformational/emotional.
- The experiment manipulates presentation and disclosure, not appeal.
- The implemented comparison is **integrated inline advertising** versus a
  **labelled advertising block**. Integrated does not mean subliminal; the
  advertisement is visible in both conditions.

## Canonical experimental terminology

Use these labels consistently in new prose:

| Concept | Canonical wording |
|---|---|
| Format 1 | integrated inline advertising |
| Format 2 | labelled advertising block |
| Early timing | turn 2 |
| Late timing | turn 4 |
| Control | no-advertising condition |
| Design | five-condition repeated-measures design |

Avoid describing the study as “subliminal versus explicit.” Older publication
placeholders still contain this framing outside Related Work and will need a
separate, explicitly approved cleanup.

## Bibliography state

The publication's active bibliography is:

```latex
\bibliography{bibliography}
```

The file is `publication/bibliography.bib`. The remote had introduced that file but
still referenced the nonexistent `references.bib`; the directive was corrected. Two
misplaced braces around repository/software entries were also corrected because they
made the BibTeX structure invalid.

The faithful expansion required publication entries for:

- `zelch2024acceptance`
- `schmidt2024detecting`
- `quilesperez2023neuromarketing`
- `john1999bigfive`
- `rammstedt2007bfi10`
- `donnellan2010types`
- timing and EEG review papers added in the preceding focused commit

Static validation found no missing or duplicate citation keys and balanced braces in
`main.tex` and `bibliography.bib`.

No local LaTeX compiler (`latexmk`, `xelatex`, `pdflatex`, `bibtex`, or `tectonic`)
was installed, so validation was structural rather than a complete PDF build. The
Overleaf build should be checked after substantive changes.

## Author's writing and approval preferences

These preferences are important and override a generic “improve the prose” workflow:

1. **Pull the latest Overleaf changes before drafting or editing.**
2. **Show the proposed text before applying it.**
3. **Do not push until the author explicitly approves the displayed version.**
4. **When merging thesis prose into the publication, preserve content faithfully.**
   Keep the papers, claims, statistics, examples, argument order, and motivation.
5. Make only minimal grammar, spelling, sentence-boundary, and transition edits
   unless a deeper rewrite is explicitly requested.
6. Do not replace a long evidence-rich section with a shorter synthesis merely
   because the synthesis is stylistically cleaner.
7. Do not silently delete strongly worded motivations. Translate informal wording
   into an academic register while retaining the underlying claim.
8. Preserve concurrent Overleaf edits during rebases; never force-push an Overleaf
   project.

The failure mode to avoid is treating “merge” as “summarize.” In this project,
“merge faithfully” means retaining the source's information density and making the
smallest wording changes necessary for the target document.

## Possible next task: the Introduction

The author is considering the same thesis-to-publication process for the
Introduction. This likely makes sense because the thesis contains useful motivation:

- the transition from search interfaces to conversational assistants;
- the economic motivation for advertising-supported AI services;
- the user/advertiser/platform welfare conflict;
- why presentation and timing are policy decisions;
- why behavioural, self-report, and EEG evidence are complementary;
- why the work is user-centred rather than an auction-mechanism contribution.

The correct next workflow is:

1. Pull both mirrors.
2. Compare the full thesis Introduction with the publication Introduction.
3. Propose a faithful publication-length draft in chat without editing files.
4. Identify claims that need citations, especially company revenue figures.
5. Let the author request small changes.
6. Apply, compile/check, commit, and push only after explicit approval.

Do not automatically copy thesis-specific scope, chapter previews, repository
details, or unsupported financial claims into the paper. Flag them for a decision
rather than deleting or rewriting them without discussion.

## Other state worth retaining

- The publication contains a newly added 14-question research agenda. Preserve it
  unless the author separately asks to revise it.
- Raw author notes and placeholders remain elsewhere in `publication/main.tex`;
  they were intentionally left untouched during the Related Work task.
- The EEG analysis is constrained by one advertisement event per participant per
  condition. Spectral/time-frequency analyses are feasible; classical ERP averaging
  is not a defensible primary analysis.
- `ad_injected` is the stable event marker across logging eras. `ad_displayed` is
  inconsistent and should only be used for validation.
- Behavioural analysis is primarily within-participant on the five-condition factor,
  with crowd/lab arm comparisons treated as sensitivity or moderation analyses.

