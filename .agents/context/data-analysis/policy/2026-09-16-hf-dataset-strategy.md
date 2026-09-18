# Hugging Face release: streams × grains, not RAW/PROCESSED

Date: 16 Sep 2026. Replaces the two-bucket names in
`2026-09-12-dataset-release-side-quest.md` (`RAW` / `PROCESSED`).
Does not upload anything. Thesis PDF first.

The catalog figure is the table of contents of **Gold**, not a list of
repos:

`src/project/docs/behavioural_pipeline/behavioural_grains.png`
(`python src/project/docs/behavioural_pipeline/behavioural_grains.py`).

Names: `.agents/context/data-analysis/2026-09-07-gold-catalog-and-lineage.md`.

## Three axes (do not collapse them)

The figure has two experimental axes. Lineage is a third, orthogonal
one. Hugging Face repos follow **lineage and consent**, not the 3×3
grid.

| Axis | Values | What it is | Lives where |
|---|---|---|---|
| **Stream** | behavioural, trajectories, EEG | data type | folder / config prefix |
| **Grain** | message, chat, person | one row | folder / config middle |
| **Lineage** | bronze, silver, gold | how far it has been cleaned | **repo** (and visibility) |
| Arm | lab, crowd | recruitment | column / filter, never a repo |
| View | ratings, Dataset A, … | which table | file / config suffix |

Joins are not a fourth stream. They are Gold views (`joins/…`).
A future policy artefact is a **new stream**, not `v2`.

Citation name: **Troiani, W. J.** Handle `eZWALT` may stay as the
account. No Vargas on cards or bib keys.

## How many Hugging Face datasets: eleven public + two gated

Walter 16 Sep: ship **all three streams**, many repos are fine, do not
re-open ethics. That means public = Gold numbers with a strip; gated =
anything a committee can treat as a person (chat text, clocks, worker
IDs, raw EEG). Not “EEG only”. Behavioural and trajectories are the
bulk of the public drop.

**Collection** (family name, never versioned):

`eZWALT/price-of-attention`

Slug: `{family}-{stream}-{grain}` for Gold, `{family}-{stream}-{lineage}`
when lineage is not gold. No `v1` / `RAW` / `PROCESSED`.

### Public Gold — one repo per filled cell of the figure

Empty cells on the figure (trajectory-person, EEG-message, join-message)
do **not** get a repo.

| Repo | Stream | Grain | Files (after the strip below) |
|---|---|---|---|
| `price-of-attention-behavioural-message` | behavioural | message | `messages.csv` (process only: lengths, latencies) |
| `price-of-attention-behavioural-chat` | behavioural | chat | `condition_features.csv`, `advertisement_features.csv` minus free text |
| `price-of-attention-behavioural-person` | behavioural | person | `person_features.csv`, `contrast_scores.csv` |
| `price-of-attention-trajectories-message` | trajectories | message | `utterances.csv`, `transitions.csv` **without `text`** |
| `price-of-attention-trajectories-chat` | trajectories | chat | `conversations.csv`, `advertisements.csv` |
| `price-of-attention-eeg-chat` | EEG | chat | Dataset A \(k=37\), Dataset A window, Dataset B |
| `price-of-attention-eeg-person` | EEG | person | contrast scores, write−read |
| `price-of-attention-joins-chat` | joins | chat | `combo_threeway.csv`, `_lab` |
| `price-of-attention-joins-person` | joins | person | `combo_threeway_D.csv`, `_lab` |

Nine public datasets. That is the figure, one repo per card.

### Public Gold — optional tenth

| Repo | Why it exists |
|---|---|
| `price-of-attention-gold` | A single umbrella that `load_dataset`s the nine as configs, for people who hate clicking. Same files, same strip. Not a second copy of the numbers. |

Skip the umbrella if you only want the nine.

### Gated — the two things that are still “a person”

| Repo | Lineage | Why it is not public |
|---|---|---|
| `price-of-attention-events` | bronze text | JSONL has utterances, Prolific/worker fields, absolute timestamps |
| `price-of-attention-eeg-recordings` | bronze signal | XDF is a 32-channel recording of a named lab session |

ICA (`price-of-attention-eeg-ica`) stays local unless you later need a
rebuild recipe. On-disk `candidate_v1` is an archive name, not a slug.

Kill: `Price-of-Attention-RAW`, `Price-of-Attention-PROCESSED`.
Do not run `scripts/upload_raw_dataset.py` against the old RAW id.

## Ethics strip (this is how you ship everything without a new IRB)

The consent/debrief in App. C.6 does not clearly name **open
redistribution** or, on the jury’s reading, EEG. So public files must
be what a reviewer can only call “anonymous analysis tables”, not
“these people’s chats and brains”.

**Drop from every public CSV**

- `participant_id`, `subject_id`, `folder`, `worker_id`, Prolific IDs
- `unix_ts`, absolute `timestamp` (keep relative latencies)
- `demo_occupation`, and `demo_age` on the lab arm (n=18 + age + sex
  is a re-id)
- any raw `text` / conclusion / free-comment column
- Amazon ASIN is fine; Amazon **catalogue dump** is not (licence)

**Keep**

- remapped `experiment_id` (new random ids, same joins)
- Likert, BFI, planned \(D\), genre labels and probabilities, EEG
  band-power features, combo joins
- `arm`, condition, task, turn

**Never upload**

- `src/project/data/catalogs/` (Amazon 2023)
- `analysis/behavioural/` (Katerina’s tree — not your Gold)
- `analysis/policy/outputs/` until the policy stream exists
- `resources/papers/`, `resources/books/`

Trajectory Gold without `text` still reproduces every thesis number
(the classifier already wrote `genre` and the \(p_*\) columns). The
chat text is how you *built* those columns, not what the paper quotes.

Bronze JSONL and XDF can still go out **gated** (HF click-through:
research use, no re-identification). That is “all the data” for people
who accept the gate. It is not a silent public dump of conversations.

## Interior of each Gold repo: the catalog id

Each public repo is one `{stream}.{grain}` cell. Files inside keep the
catalog **view** name. If you also ship the umbrella `…-gold`, its
Hugging Face **configs** are the same ids:

```
{stream}.{grain}.{view}
```

```
gold/
  behavioural/
    message/turns.csv              # messages.csv
    chat/ratings.csv               # condition_features.csv
    chat/recall.csv
    person/traits.csv              # person_features.csv
    person/contrasts.csv
  trajectories/
    message/labels.csv             # utterances.csv (utterance context primary)
    message/turn-pairs.csv
    chat/shifts.csv
    chat/ad-genre.csv
    # person: empty on the figure — do not invent a file
  eeg/
    # message: empty on the figure
    chat/dataset-a.csv             # k=37 confirmatory
    chat/dataset-a-window.csv      # stored whole-window; not confirmatory
    chat/dataset-b.csv
    person/contrasts.csv
    person/write-read.csv
  joins/
    chat/joined-chat.csv
    chat/joined-chat-lab.csv
    person/joined-contrasts.csv
    person/joined-contrasts-lab.csv
```

Each config in `README.md` / YAML is exactly one of those paths so
`load_dataset("eZWALT/price-of-attention-gold", "eeg.chat.dataset-a")`
is the confirmatory cell. The card states: Dataset A = condition
aggregation \(k=37\); utterance context is primary; participant is the
unit; join key `experiment_id`.

Arm is a column (`arm` ∈ {lab, crowd}), not a config. EEG configs are
lab-only by construction.

## Future policy: add a stream, not a version

When a serving-policy artefact exists it is a fourth **stream**, same
family, same three grains if they apply.

| Kind | Hub | Repo id | Why this name |
|---|---|---|---|
| Training / evaluation tables | datasets | `eZWALT/price-of-attention-policy` | Stream name. Lineage (silver features vs gold bandit rows) is a **config**, `policy.chat.bandit-rows`, not `policy-v2`. |
| Fitted \(\pi\) or scorer weights | models | `eZWALT/price-of-attention-policy` | Same slug on the model hub. HF already separates datasets from models. |
| A later architecture | models | still `…-policy` | Pin a **revision** (`revision="2027-03-ridge"`) or a model card section. Do not mint `…-policy-v2`. |

If policy tables are tiny and share Gold’s licence, they may instead
land as configs inside `price-of-attention-gold` under `policy/`.
Split to `…-policy` only when the licence, gating, or size differs
(the usual case: synthetic expansions, extra candidates per turn).

The Amazon catalogue is **not** stream four. It is a third-party
corpus (thesis §4.1). If it ever ships: `eZWALT/price-of-attention-catalogue`,
gated, licence-first. Never inside Gold.

## Versioning (dates and hashes, never the slug)

| What changes | Where it goes |
|---|---|
| A Gold rebuild that changes a number in the paper | git tag / HF revision `2026-09-08-confirmatory` (or the freeze commit). Dataset card `version`. Bib year stays 2026 until a new paper. |
| A new stream | new repo **or** new config prefix. Slug stays `price-of-attention-*`. |
| A new grain for an old stream | new folder + config. Do not fork the repo. |
| ICA archive name `candidate_v1` | on-disk provenance only. Hub path `silver/ica/`. |

Bib keys, once the files exist:

```
troiani2026priceofattentiongold
troiani2026priceofattentionevents
troiani2026priceofattentioneeg
```

Author on all three: `Troiani, Walter J.` Title: the slug without the
account (`Price of Attention: Gold`, etc.).

## Paper and thesis sentences (when the files exist)

Do not promise XDF in the public drop.

> Analysis tables that reproduce the reported tests are in the public
> dataset *Price of Attention: Gold* (behavioural, trajectory, and EEG
> streams; message, chat, and person grains). De-identified event logs
> and raw EEG recordings are available as separate gated datasets.

Thesis Ch 9 already claims a data card, seeds, and a versioned
identifier. That identifier is the Gold revision, not `PROCESSED`.

## Opinion (16 Sep, afternoon)

Ethics-sensitive ≠ “do not ship”. It means: this column can name a
person or is a biosignal/chat, so it is gated or dropped. Worth
uploading = a reader needs it to trust a number in the paper.

**Ethics-sensitive (do not put on a public repo)**

| Column / artefact | Why it is ethics | Worth uploading at all? |
|---|---|---|
| Utterance `text`, JSONL chats | people’s words | Gated only. Not needed for any reported test. |
| Free-text findings + recall reaction | same, and **the thesis never analysed them** | No. Risk with zero paper payoff. |
| XDF / ICA | identifiable neural recording; consent is thin | Gated, later, if someone wants to refit. Not the paper. |
| Prolific / `participant_id` / `folder` / `subject_id` | direct IDs | No. Remap `experiment_id`. |
| Absolute `unix_ts` / `timestamp` | clock + session can re-id | No. Keep latencies. |
| Lab `demo_age` + `demo_occupation` | n=18 quasi-id | No. Keep sex / education / familiarity / frequency. |

**Not ethics. Upload public. This is the actual contribution.**

| What | Why it is worth it |
|---|---|
| Likert items + composites, planned \(D\), cued memory | Every behavioural headline |
| BFI-10 | The 0/60 moderation |
| Process lengths / latencies (no text) | The 36 interaction checks; latency co-intervention |
| Genre labels, \(p_*\), \(N_{\mathrm{shift}}\), \(\delta^{(a)}\) **without text** | Trajectory chapter; text is already summarised |
| EEG band powers, Dataset A/B, write−read, planned EEG \(D\) | EEG chapter. Summaries, not raw voltage. |
| Combo joins of the above | The \(\rho=.80\) cell |
| Served `ad_id` / title | What was actually inserted |

**What I would actually push first** (six repos, not eleven):

1. `…-behavioural-chat`
2. `…-behavioural-person`
3. `…-eeg-chat`
4. `…-eeg-person`
5. `…-trajectories-chat`
6. `…-joins-person`

Message-level files (`…-behavioural-message`, `…-trajectories-message`
minus text) and `…-joins-chat` are optional. They reproduce nothing
the six do not already pin down.

Skip entirely: Amazon catalogue, Katerina’s tree, policy dumps,
`resources/papers/`, unused free text.

---

## First-drop checklist (after the Thursday PDF)

1. De-id pass on JSONL → `…-events` (gated).
2. Upload Gold folders + card as Troiani → `…-gold` (public).
3. Upload XDF → `…-eeg-recordings` (gated) only if consent allows.
4. Rewrite `sections/08_statements.tex` and the two bib entries.
5. Leave ICA unshipped unless someone needs to refit.

Do not run `scripts/upload_raw_dataset.py` against the old
`Price-of-Attention-RAW` id.
