# Writing context structure

This directory holds durable writing decisions, Overleaf workflow notes, and
handovers for thesis and publication prose.

## Source of truth

**The only source of truth for manuscript content is the Overleaf Git
repositories under `docs/overleaf/`.** Context documents here summarize
decisions and working agreements; they do not override LaTeX. Before drafting
or editing, pull the relevant mirror and verify claims against the current
`.tex` / `.bib` files.

```text
docs/overleaf/publication/   # publication paper (primary writing target)
docs/overleaf/thesis/          # dissertation
docs/overleaf/presentation/    # slides
docs/overleaf/angela-paper/    # teammate EEG/ACL reference
docs/overleaf/example-eeg/     # EEG report template reference
```

Each Overleaf folder is an independent Git repository. The parent repository
ignores their contents. Run `git` commands inside the relevant mirror.

Monday agenda (Katerina + Sebastian):
`2026-08-20-monday-katerina-sebastian-agenda.md`.

Newest snapshot (completion %, STATUS map):
`2026-08-19-completion-snapshot.md`.

Crossable leftover items (paper / thesis / analysis):
`2026-08-18-remaining-work-checklist.md`.

EEG Method comments parked in Overleaf (median / \(Y_A,Y_B,D\) / short cite
set, not yet visible prose):
`../data-analysis/eeg/2026-08-19-literature-justifications-in-overleaf.md`.

## Entry order

1. Read this README.
2. Prefer the newest dated entry in this directory.
3. For analysis facts that constrain writing (sample sizes, EEG constraints,
   exclusions), verify against `.agents/context/data-analysis/` and executable
   code/manifests—then confirm the manuscript still matches Overleaf after
   any rewrite.

## Author workflow

1. Pull Overleaf before drafting or editing.
2. Show proposed text before applying it.
3. Do not push until Walter explicitly approves the displayed version.
4. Do not commit or push Overleaf mirrors unless explicitly requested.
