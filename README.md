# Conversational Advertising in LLM Assistants

[![Status](https://img.shields.io/badge/status-data%20analysis-brightgreen)](#project-status)
[![Version](https://img.shields.io/badge/version-2.2.0-blue)](VERSION)
[![Python](https://img.shields.io/badge/python-3.11%E2%80%933.13-blue)](src/project/requirements.txt)
[![License](https://img.shields.io/badge/license-Apache--2.0-lightgrey)](src/project/LICENSE)

Master's thesis with **Telefónica Research**: how does advertising inside an
LLM assistant change what users trust, notice, and do?

This repository holds the full apparatus — a Streamlit study platform with a
RAG ad-retrieval pipeline, the two-arm experimental protocol (in-person EEG lab
and remote crowdsourcing), the collected session data, and the thesis sources.

![System architecture](src/project/docs/architecture/architecture.png)

---

## What's inside

- **A running experiment platform.** Participants chat with a local LLM
  (`qwen3.6:35b` via Ollama or vLLM) that retrieves real Amazon products and
  weaves them into replies as ads.
- **A 5-condition within-subject design.** Every participant sees no-ad control,
  inline ads, and ad blocks, each early and late in the conversation.
- **Two study arms from one codebase.** `?study=lab` adds the rest baseline that
  anchors the EEG recording; `?study=crowd` adds Prolific ID entry and an
  attention check. LSL markers stream either way.
- **Event-sourced logging.** Every message, retrieval, ad exposure, click, and
  questionnaire answer lands in append-only JSONL, ready for analysis.
- **Reproducible figures.** Architecture, participant-flow, and catalog-pipeline
  diagrams are generated from code, not drawn by hand.

## Study design at a glance

| Condition | Ad format | Injected at |
|---|---|---|
| `no_ads` | none (control) | — |
| `inline_early` | woven into the assistant's reply | turn 2 |
| `inline_late` | woven into the assistant's reply | turn 4 |
| `block_early` | labelled ad block above the reply | turn 2 |
| `block_late` | labelled ad block above the reply | turn 4 |

Five conditions × one task each, 4 turns per conversation, order
counterbalanced per participant. Full screen-by-screen protocol:
[`workflow_b.md`](src/project/docs/workflow_b.md).

## Quick start

**Requirements:** 1x NVIDIA GPU with >=24 GB VRAM (e.g. A100 40 GB).

```bash
cd src/project
cp .env.example .env
# Edit .env -- set OLLAMA_BIN to the path of your ollama binary
./launch.sh --host
```

Then open http://localhost:7777. To click through the whole study without a
GPU, use `?dev=flow&dry_run=1`. Setup details, backends, and cluster deployment
live in the [platform README](src/project/README.md).

## Repository layout

```text
src/project/        Streamlit study platform — app, RAG pipeline, protocol, logs
  core/               config, conversation, retrieval, experiment, logging, EEG
  docs/               protocol + operations docs and generated diagrams
  experiments/        offline prompt-tuning harness (separate from the study)
  scripts/            catalog builder, Ollama cluster, pilot XDF inspection
  tests/              pytest suite
src/notebooks/      exploratory analysis
scripts/            log labelling, tracking, and LSL bridge utilities
docs/               thesis, paper, and presentation sources (Overleaf-backed)
analysis/           statistical analysis of collected sessions (WIP)
resources/          literature corpus: papers, blogs, books
```

## Data

Curated session exports are versioned under
`src/project/logs/tracked/{lab,crowd,beta}/`, one directory per subject. Quality
issues are carried in the directory name (`_unfinished`, `_unfocused`), and
per-arm notes sit alongside as `lab-notes.txt` and `crowd_notes.txt`. Live runs
land in `src/project/logs/production/` and stay git-ignored until reviewed and
promoted with `scripts/sync_tracked.sh`.

Models and datasets used throughout the work are collected in this
[HuggingFace collection](https://huggingface.co/collections/eZWALT/tfm).

## Documentation

| Document | What it covers |
|---|---|
| [Platform README](src/project/README.md) | Setup, backends, RAG pipeline, logging, operations |
| [Protocol](src/project/docs/workflow_b.md) | Screens, conditions, counterbalancing, instruments |
| [Query guide](src/project/docs/query_guide.md) | Every URL parameter that configures a session |
| [LSL markers](src/project/docs/lsl_marker_protocol.md) | EEG marker stream and time-locking |
| [Catalog build](src/project/docs/catalog_build.md) | Rebuilding the product catalog and FAISS index |
| [Diagrams](src/project/docs/architecture/README.md) | How the figures are generated and kept in sync |
| [Thesis docs](docs/README.md) | Overleaf mirrors, sync workflow, final deliverables |

Read-only Overleaf views of the write-up:
[thesis](https://www.overleaf.com/read/jmpfyvkdxcnt#deeda3) ·
[presentation](https://www.overleaf.com/read/tvwscngdpyfp#e86fdc) ·
[paper](https://www.overleaf.com/read/tcggxdnhjgmm#739137)

## Project status

Data analysis + paper writing in progress. Collection is complete.

## Versioning

`VERSION` at the repository root is the single source of truth, and every
session stamps it into its `experiment_config` event — so each dataset records
the build that produced it. Bump it before collecting data under changed
behaviour and tag the commit (`v2.2.0`); releases are tagged, and the
`experiment-pilot-v1.*` tags are the earlier pilot line.

Sessions collected before this was consolidated carry `1.1.0-pilot1`, and
containerised runs from that period may carry `unknown`, because the image could
not see the version file. Both are fixed as of 2.2.0; treat those strings as
"pilot 1" when analysing.

## Background reading

<details>
<summary>Recommender systems and LLM advertising sources</summary>

- [ACM RecSys Conference](https://www.youtube.com/@acmrecsys/playlists)
- [Awesome RecSys](https://github.com/jihoo-kim/awesome-RecSys)
- [Awesome LLMs for RecSys](https://github.com/WLiK/LLM4Rec-Awesome-Papers)
- [Awesome LLMs in RecSys](https://github.com/CHIANGEL/Awesome-LLM-for-RecSys)
- [Awesome LLM-enhanced RecSys](https://github.com/nancheng58/Awesome-LLM4RS-Papers)
- [Ludo's RecSys deep dives](https://machinelearningatscale.substack.com/p/deep-dive-series)

Industry moves on advertising inside assistants:

- [OpenAI ads principles](https://www.youtube.com/watch?v=2agJo3Jf_O4&t=1233s)
  and the [Agentic Commerce Protocol](https://developers.openai.com/commerce)
- [Google ads in AI Overviews](https://support.google.com/google-ads/answer/16297775)
- [Perplexity pausing ad tests](https://searchengineland.com/perplexity-stops-testing-advertising-469452)
- [Thrad](https://www.thrad.ai/), an LLM-advertising startup
  ([founder interview](https://www.youtube.com/watch?v=CxAxt1xUpW0))

</details>

The literature corpus itself lives in `resources/papers/`, clustered by topic:
`ADS`, `CRS`, `EEG`, `LLM`, `RAG`, `RecSys`, `RL`, `Economics`, plus an
`IMPORTANT` shortlist.

## License

Apache-2.0 — see [LICENSE](src/project/LICENSE).
