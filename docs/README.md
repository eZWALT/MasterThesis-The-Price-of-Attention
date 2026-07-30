# Documentation

This directory separates local Overleaf working copies from thesis deliverables
that belong to this repository.

## Layout

```text
docs/
├── data-analysis-foundation.canvas.tsx  # analysis goals and statistical foundation
├── context/        # dated handover notes on project state and settled decisions
├── generated/      # AI-assisted planning and feasibility notes
├── overleaf/       # local Git clones; ignored by the parent repository
│   ├── thesis/
│   ├── presentation/
│   └── publication/
└── final/          # versioned final files and supporting material
    ├── thesis/
    ├── presentation/
    └── publication/
```

## Start here

`context/` holds dated handover documents describing where the study stands, which
design and analysis decisions are settled, which logging eras exist in the session
data, and what is still blocked. Read the most recent one before picking up work.

## Research artifacts

`data-analysis-foundation.canvas.tsx` preserves the study's behavioral,
self-report, and EEG analysis foundation. It records the canonical five
conditions, primary outcomes and contrasts, mixed-model structure, EEG
feasibility gates, exclusion strategy, and preregistration sequence.

`generated/` contains the analysis-planning notes that back those decisions,
including the model feasibility comparison and the EEG feasibility and timing
reconstruction plan. They are working notes rather than results.

## Overleaf mirrors

`overleaf/` contains three independent Git repositories backed by Overleaf.
They remain local working copies and are intentionally ignored by this
repository, so their separate histories and remotes are never committed as
nested repositories.

### First-time setup

This workflow requires access to Overleaf Git integration (included with
Overleaf Commons and Premium plans). In each Overleaf project, open
**Integrations → Git** and copy its Git URL. It has this form:

```text
https://git@git.overleaf.com/<project-id>
```

Create an Overleaf Git authentication token in Account Settings. Do not put
that token in this repository, its `.env` file, or a remote URL. Store it once
for the local Unix user with Git's credential helper:

```bash
mkdir -p ~/.config/git
chmod 700 ~/.config ~/.config/git
git config --global credential.helper 'store --file ~/.config/git/overleaf-credentials'
```

Clone each project from the root of this repository, replacing the placeholders
with the three URLs copied from Overleaf:

```bash
git clone https://git@git.overleaf.com/<thesis-project-id> docs/overleaf/thesis
git clone https://git@git.overleaf.com/<presentation-project-id> docs/overleaf/presentation
git clone https://git@git.overleaf.com/<publication-project-id> docs/overleaf/publication
```

On the first clone or fetch, Git prompts for credentials. Use `git` as the
username if prompted and paste the Overleaf authentication token as the
password. The same token works for all Overleaf projects available to that
account. Once saved, restrict the credential file:

```bash
chmod 600 ~/.config/git/overleaf-credentials
```

### Easy synchronization command

This repository includes `scripts/overleaf-sync`, which safely pulls all three
mirrors by default. To make it available as the `overleaf-sync` command, run
the following from the root of this repository once:

```bash
printf "alias overleaf-sync='%s/scripts/overleaf-sync'\n" "$PWD" >> ~/.bash_aliases
source ~/.bash_aliases
```

Use these commands day-to-day:

```bash
overleaf-sync                      # pull all three mirrors safely
overleaf-sync status               # inspect all mirror branches and changes
overleaf-sync pull thesis          # pull one mirror
overleaf-sync pull presentation
overleaf-sync pull publication
overleaf-sync push thesis          # push committed local edits for one mirror
```

The default pull uses Git's `--ff-only` mode. It updates only when doing so
cannot overwrite or merge local work. If it refuses, inspect the affected
mirror with `overleaf-sync status`, then resolve its local changes before
pulling again. The command never pushes unless `push` and one named project
are supplied explicitly.

Use the Overleaf projects as the source of truth for editable source files.
Keep local mirrors clean so fast-forward-only pulls remain safe. If editing
locally is intentional, commit inside the relevant mirror before pushing:

```bash
cd docs/overleaf/thesis
git add .
git commit -m "docs: update thesis source"
cd ../../..
overleaf-sync push thesis
```

For a scheduled update (for example, every 30 minutes), call the script
directly rather than the interactive alias:

```bash
mkdir -p ~/.local/state
crontab -e
```

Add this line to the crontab, replacing `/absolute/path/to/MasterThesis-RAG-RecSys`
with the clone's actual absolute path:

```cron
*/30 * * * * flock -n /tmp/overleaf-sync.lock /absolute/path/to/MasterThesis-RAG-RecSys/scripts/overleaf-sync >> ~/.local/state/overleaf-sync.log 2>&1
```

## Final deliverables

`final/` is tracked normally by this repository. Add any reviewed thesis,
presentation, or publication outputs there, including PDFs, source snapshots,
figures, or supplementary material that should be preserved with the project.

After copying reviewed material into `final/`, version it in the parent
repository as usual:

```bash
git add docs/final
git commit -m "docs: add final thesis export"
```
