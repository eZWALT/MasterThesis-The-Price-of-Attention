# Documentation

This directory separates local Overleaf working copies from thesis deliverables
that belong to this repository.

## Layout

```text
docs/
├── overleaf/       # local Git clones; ignored by the parent repository
│   ├── thesis/
│   ├── presentation/
│   └── publication/
└── final/          # versioned final files and supporting material
    ├── thesis/
    ├── presentation/
    └── publication/
```

## Overleaf mirrors

`overleaf/` contains three independent Git repositories backed by Overleaf.
They remain local working copies and are intentionally ignored by this
repository, so their separate histories and remotes are never committed as
nested repositories.

Update all mirrors after editing in Overleaf:

```bash
git -C docs/overleaf/thesis pull --ff-only
git -C docs/overleaf/presentation pull --ff-only
git -C docs/overleaf/publication pull --ff-only
```

Use the Overleaf projects as the source of truth for their editable source
files. Keep local mirrors clean so fast-forward-only pulls are safe.

## Final deliverables

`final/` is tracked normally by this repository. Add any reviewed thesis,
presentation, or publication outputs there, including PDFs, source snapshots,
figures, or supplementary material that should be preserved with the project.
