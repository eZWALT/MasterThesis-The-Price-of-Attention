# Study Platform

Streamlit application that runs the conversational-advertising experiment: a
local LLM assistant, a RAG pipeline that retrieves real products as ads, the
participant protocol, and event-sourced logging. One codebase serves both the
in-person EEG lab and the remote crowdsourcing arm.

This directory is the **study app**, not analysis Gold. Live runs land in
`logs/production/` (git-ignored). Reviewed sessions are Bronze under
`logs/tracked/{lab,crowd,beta}/`. Inferential Gold is
`analysis/walter/behavioural/` and `analysis/eeg/`.
**`analysis/behavioural/` is Katerina’s tree — do not open, edit, run,
or quote it.** Science entrypoint: repository `AGENTS.md`. Leave
application code here alone unless the task is the platform itself.

---

## Quick start

```bash
cd src/project
cp .env.example .env                 # then set OLLAMA_BIN to a real binary
                                     # (the example path will fail)
./launch.sh --host                   # Ollama + Streamlit on the host GPU
```

Open <http://localhost:7777>. Without a catalog and FAISS index the app still
runs — ads fall back to a placeholder. To build the real index, see
[`docs/catalog_build.md`](docs/catalog_build.md).

**No GPU? No models?** `?dev=flow&dry_run=1` mocks the LLM and the retrieval
pipeline, so the entire participant flow is clickable on a bare checkout.

### Session URLs

| URL | Mode |
|---|---|
| `/` | participant session, `crowd` protocol by default |
| `/?study=lab&pid=p01` | lab protocol: EEG baseline, no Prolific screens |
| `/?study=crowd&pid=p42` | crowd protocol: Prolific ID + attention validation |
| `/?webcam=1` | add session-wide webcam recording (either arm) |
| `/?dev=true` | developer free-chat with ad controls |
| `/?dev=flow` | participant flow with skip buttons and debug panels |
| `/?dev=flow&dry_run=1` | same, with everything mocked |

Every knob is a URL parameter — see the [query guide](docs/query_guide.md).

### Backends

```bash
./launch.sh              # Ollama on the host + Streamlit in Docker (default)
./launch.sh --host       # both on the host — full GPU access, no Docker
./launch.sh --vllm       # vLLM in Docker (needs nvidia-container-toolkit)
./launch.sh --cluster 4  # 4 Ollama instances behind an nginx round-robin
```

`launch.sh` requires `.env` and reads every setting from it. The Ollama paths
also pull the model if it is not present locally before serving Streamlit on
`STREAMLIT_PORT`.

---

## Experiment protocol

Five within-subject conditions, one task each, 4 turns per conversation:

```text
consent → [baseline | prolific_id] → warmup_chat
  → [ task briefing → conversation → findings → questionnaire ] × 5
  → ad recall → BFI-10 → demographics → [validation] → debrief → done
```

The arms differ only in which screens are skipped: lab shows the eye-tracking
baseline, crowd shows Prolific ID entry and the validation check. Conditions and
tasks are counterbalanced per participant.

![Lab participant flow](docs/participant_flow/flow_lab.png)

Full details — conditions, instruments, item counts, counterbalancing — are in
[`docs/workflow_b.md`](docs/workflow_b.md).

---

## Ad retrieval pipeline

```text
query → [context summary] → [HyDE] → dense (FAISS) → hybrid (BM25 + RRF)
      → reranker → formatter → injector
```

Bracketed stages that actually toggle: `?ctx_sum=1` (context summary)
and `?qe=hyde|expand|none` (HyDE is the default). `?ad_sum=` is parsed
but is **not** wired into `build_default_stages()` — do not expect an
ad-text rewrite. Candidates are filtered to the Amazon categories
declared by the current task, so a gardening task cannot surface
laptops.

| Component | Model | Device | Runs |
|---|---|---|---|
| Intent (log only) | `Thrad/thrad-bert-conversation-classifier` | CPU | every turn; does not gate ads |
| Embedding | `Qwen/Qwen3-Embedding-0.6B` (bfloat16) | GPU | ad turns |
| Reranker | `BAAI/bge-reranker-v2-m3` | GPU | ad turns |
| Assistant | `qwen3.6:35b` via Ollama/vLLM | GPU | every turn |

Devices are allocated at import time by free VRAM (`core/device.py`), with the
LLM's GPUs excluded and a CPU fallback. Models load once at startup so no
participant waits for a cold cache.

Ads reach the participant through one of two **injectors**:
`inline_persuasive` rewrites the reply to mention one product
naturally; `explicit_ad_block` renders a labelled banner above the
reply. Protocol / Gold **condition** ids are `inline_early`,
`inline_late`, `block_early`, `block_late` (plus `no_ads`). JSONL
`condition_start` stores the condition id in `data.condition` and the
injector in `data.ad_mode` (and on the envelope `ad_mode`). Do not
treat those two strings as the same key.

---

## Logging

```text
logs/production/{experiment_id}/      # live participant sessions
logs/development/{experiment_id}/     # ?dev=true and ?dev=flow
  {experiment_id}_events.jsonl        append-only live log
  {experiment_id}_export.jsonl        validated copy written at session end
  {experiment_id}_eyetracking.mp4     webcam recording, when enabled
```

`ExperimentLogger` is an event-sourcing mini-system: `log()` never touches disk,
it enqueues to a writer thread that batches to JSONL every 25 events or 60
seconds. Each row carries full context — experiment, participant, conversation,
condition, trial, turn — so any event is queryable on its own.

Representative events: `session_started`, `experiment_config` (VERSION
stamp), `condition_start`, `user_message`, `intent_classified`,
`retrieval`, `ad_injected`, `ad_displayed`, `ad_clicked`,
`turn_N_read`, `turn_N_write`, `post_condition_survey_submitted`,
`ads_recall_submitted`, `session_complete`. Envelope `ad_mode` is the
injector, not the condition id.

Inspect sessions in the browser with the bundled pages: **Log Viewer** replays a
session screen by screen, **Dashboard** aggregates across sessions. Both find
the logs relative to this directory, or wherever `LOG_DIR` points.

### Promoting sessions

`logs/production/` is git-ignored. Once a session is reviewed:

```bash
python3 ../../scripts/label_sessions.py --exec     # lab_subject_N / crowd_subject_N
bash ../../scripts/sync_tracked.sh --exec          # copy into logs/tracked/
```

Dry-run is the default; pass `--exec` to write. Names are
`lab_subject_N` / `crowd_subject_N` (plus `_unfocused` / `_unfinished`),
not a `lab_` prefix. `logs/tracked/{lab,crowd,beta}/` is versioned
**Bronze**. Inferential Gold is built in `analysis/`, not here.

### Threads

Everything runs in one process: a main thread plus up to three daemons, no
sidecar services.

| Thread | Work |
|---|---|
| Main | Streamlit and all ML: intent, embedding, FAISS, reranking, LLM streaming |
| Log writer | Drains the event queue to JSONL |
| Ad clicks | Small HTTP server on `:7780` that records clicks and redirects |
| Webcam | `cv2` capture at `WEBCAM_FPS`, only when `?webcam=1` |

---

## Layout

```text
app.py                  entrypoint — routing only
core/
  config.py             single source of truth: prompts, conditions, screens, models
  device.py             VRAM-aware device allocation
  conversation/         turn orchestrator + LLM client
  retrieval/            pipeline, catalog, stages/, embeddings/, rerankers/, adapters/
  ad_injection/         injectors, ad models, click tracking
  experiment/           controller (state machine), query_params, surveys, tasks
  logger/               experiment logger, identity, payload
  modalities/           eeg (LSL markers), eye_tracking
  ui/                   participant screens, dev mode, shared widgets
pages/                  log_viewer.py, dashboard.py
docs/                   protocol docs + generated diagrams
experiments/            offline prompt-tuning harness
scripts/                catalog builder, Ollama cluster, pilot XDF inspection
tests/                  pytest suite
```

## Development

```bash
# from this directory (src/project), after pip install -r requirements.txt
pytest -m unit              # fast — no GPU models; four query-param tests
                            # currently fail (stale skip-list expectations)
pytest -m e2e               # needs GPU + catalog + FAISS index
pytest tests/retrieval      # one area
```

There is no pytest.ini at the repository root. Bare `pytest` collects
unit and e2e.

Configuration belongs in `core/config.py`; no other module should hardcode
numbers, key strings, or prompt text. Anything that varies per session should be
a URL parameter, not a code change. Paths are resolved relative to this
directory, never to an absolute home directory, so a fresh clone runs anywhere.

### Versioning

The **study-app** stamp is the repository `VERSION` file (currently
2.2.0), exported as `APP_VERSION` by `launch.sh`. `core/version.py`
resolves it. Every session logs it in `experiment_config`. Collection
is finished; do not bump it to collect more. Recipe if you ever must:

```bash
echo 2.3.0 > ../../VERSION
git commit -am "chore: bump VERSION to 2.3.0" && git tag v2.3.0
```

Docker images are built from this directory and cannot see the repository root,
so `launch.sh` exports `APP_VERSION` and the compose files pass it through.
`core/version.py` prefers that variable and falls back to the file, which is
also the hook for stamping a build ID in any other deployment.

---

## Running the study on a server

Keep the app alive across SSH drops with tmux:

```bash
tmux new-session -d -s experiment 'cd ~/MasterThesis-RAG-RecSys/src/project && ./launch.sh --host'
tmux attach -t experiment       # Ctrl+B then D to detach
tmux kill-session -t experiment
```

To survive reboots, let cron re-create the session if it disappears:

```cron
* * * * * tmux has-session -t experiment 2>/dev/null || tmux new-session -d -s experiment 'cd ~/MasterThesis-RAG-RecSys/src/project && ./launch.sh --host'
```
