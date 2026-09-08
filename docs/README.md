# Documentation

Overleaf working copies and the parent-repo notes that tell you how to
sync them. Manuscript source of truth is `docs/overleaf/`, not this
file and not the committed `docs/` tree.

```text
docs/
├── README.md          # this file
├── generated/         # one leftover: Tang / Ads that Talk Back code review
├── overleaf/          # local Git clones; ignored by the parent repository
│   ├── thesis/
│   ├── presentation/
│   └── publication/
└── final/             # empty on purpose until a camera-ready export
```

Science decisions live in `../.agents/context/`. Code map:
`../analysis/README.md`. Agent router: `../AGENTS.md`.

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

`final/` is tracked normally by this repository. Add reviewed thesis,
presentation, or publication outputs there when they exist.
