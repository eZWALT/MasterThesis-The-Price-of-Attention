# 📡 Conversational Ad Retrieval — RAG RecSys (Experimentation)

Streamlit-based conversational AI interface for benchmarking advertising strategies
in LLM-powered recommender systems. Built in collaboration with Telefonica Research.

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [URL Parameters](#url-parameters)
5. [Running with Docker Compose](#running-with-docker-compose)
6. [Running Locally (no Docker)](#running-locally-no-docker)
7. [Experiment Flow](#experiment-flow)
8. [Ad Retrieval Pipeline (RAG)](#ad-retrieval-pipeline-rag)
9. [Architecture](#architecture)
10. [Experiment Logging](#experiment-logging)
11. [Project Structure](#project-structure)

---

## Overview

The platform provides a ChatGPT-like interface where participants complete 5 short
conversation tasks, each with a different advertising strategy. After each conversation
they answer a brief survey, followed by a personality questionnaire (BFI-10),
demographics, and a deception disclosure.

A **lab study mode** (`?study=lab`) adds eye-tracking baseline + persistent webcam
recording for EEG-synchronised experiments.

---

## Prerequisites

- **Docker & Docker Compose v2** (`docker compose`, not `docker-compose`)
- **Python 3.13+** (for local development without Docker)
- **Ollama** (default): `ollama` binary installed locally
- **vLLM**: requires `nvidia-container-toolkit`

---

## Quick Start

```bash
cd src/project
cp .env.example .env      # edit to match your setup
python scripts/prepare_amazon_catalog.py --build-index          
./launch.sh
```

Open http://localhost:7777 — participant mode (default: crowd study).  
Open http://localhost:7777?dev=true — developer free-chat.  
Open http://localhost:7777?dev=flow — participant flow walkthrough.  
Open http://localhost:7777?dev=flow&dry_run=1 — flow without GPU/models.  

### Dry-Run Mode

`?dry_run=1` launches the full participant flow **without loading any ML models**
or requiring a GPU. Useful for UI development, questionnaire testing, and CI.

- Skips LLM warmup (no model download, no Ollama/vLLM needed)
- Skips retrieval pipeline config (no sentence-transformers download)
- `LLMClient` returns mock replies instantly (no HTTP call)
- Ads are synthetic placeholders
- No FAISS index required — works on a bare checkout

```bash
open http://localhost:7777?dev=flow&dry_run=1
```

### Switching backends

```bash
./launch.sh                # ollama (default)
./launch.sh --ollama       # explicit ollama
./launch.sh --vllm         # vLLM (requires nvidia-container-toolkit)
./launch.sh --host         # run Streamlit on host (full GPU access)
./launch.sh --cluster      # multi-GPU Ollama cluster via nginx LB
```

---

## URL Parameters

| Param | Values | Default | Description |
|---|---|---|---|
| `study` | `lab`, `crowd` | `crowd` | Study type. Lab = EEG/eye-tracking, crowd = remote Prolific |
| `dev` | `true`, `flow` | — | `true` → free-chat; `flow` → screen walkthrough |
| `dry_run` | `0`, `1` | `0` | Mock LLM + ads, zero cost |
| `calibration` | `0`, `1` | `0` | Calibration mode (logs to separate dir) |
| `force_ad` | `0`, `1` | `0` | Force ad on every turn |
| `rag` | `0`, `1` | `1` | Enable/disable RAG retrieval |
| `qe` | `none`, `hyde` | from config | Query expansion mode |
| `ctx_sum` | `0`, `1` | `0` | Enable context summarization |
| `ad_sum` | `0`, `1` | `0` | Enable ad summarization |
| `bfi` | `10` | `10` | BFI version (only 10 supported) |
| `seed` | int | random | Random seed for condition ordering |
| `cb` | int | derived from pid | Counterbalancing group |
| `turns_min` | int | from config | Min turns per condition |
| `turns_max` | int | from config | Max turns per condition |
| `finish_from` | int | from config | Turn from which "Finish" button appears |
| `skip` | comma-sep screen names | per study | Screens to auto-advance (e.g. `consent,demographics`) |
| `pid` | string | auto | Participant ID override |

---

## Running with Docker Compose

### Ollama backend (CPU/GPU, default)

```bash
docker compose -f docker-compose.ollama.yml up --build
```

### vLLM backend (GPU, multi-GPU)

```bash
docker compose -f docker-compose.vllm.yml up --build
```

---

## Experiment Flow

Workflow B — 5-condition within-subject protocol:

```
consent → baseline [30s eye-tracking] → warmup_chat
→ [condition_intro → condition_chat → condition_conclusion → post_condition_survey] × 5
→ ads_recall → ocean (BFI-10) → demographics → deception_disclosure → done
```

### Screen details

| Screen | Purpose |
|---|---|
| `consent` | Informed consent form |
| `baseline` | 30s eye-tracking calibration (lab only). Webcam records the entire session |
| `instructions` | Brief task explanation |
| `warmup_chat` | Practice conversation (no ads, no survey) |
| `condition_intro` | Brief the participant on the current task |
| `condition_chat` | Main conversation with configured ad strategy |
| `condition_conclusion` | Qualitative reflection on the conversation |
| `post_condition_survey` | Likert-scale questionnaire about the assistant and ads |
| `ads_recall` | 4-step ad recall test (one per ad condition) |
| `ocean` | BFI-10 personality inventory |
| `demographics` | Age, sex, education, chatbot familiarity |
| `deception_disclosure` | Debrief with withdrawal option |
| `done` | Thank-you screen, data export |

### Study types

- **`crowd`** (default): skips `baseline` (no webcam). For Prolific/MTurk.
- **`lab`**: shows all screens including baseline. Webcam recording runs for the
  entire session, saved to `{log_dir}/{run_id}_eyetracking.mp4`.

---

## Ad Retrieval Pipeline (RAG)

Models load lazily on first ad injection and are cached for the process lifetime.

```
query ──▶ 1. IntentClassifier ──▶ 2. DenseRetriever ──▶ 3. HybridRefiner
                                         │ FAISS ANN         │ BM25 + RRF
                                   embedding model            │
                                    (shared with              ▼
                                     catalog build)  4. Reranker (cross-encoder)
                                                              │
                                                              ▼
                                                     5. AdFormatter ──▶ Ad
```

### Stages

| # | Stage | Model | Device |
|---|---|---|---|
| 1 | `IntentClassifier` | `Thrad/thrad-bert-conversation-classifier` (DistilBERT) | CPU |
| 2 | `DenseRetriever` | `Qwen/Qwen3-Embedding-0.6B` (BF16) | GPU / CPU |
| 3 | `HybridRefiner` | BM25 Okapi + RRF score fusion | CPU |
| 4 | `Reranker` | `BAAI/bge-reranker-v2-m3` (BF16) | GPU / CPU |
| 5 | `AdFormatter` | Pure transform — no inference | — |

### Per-turn execution

| Model | Ad turns | Non-ad turns |
|---|---|---|
| Intent (ThradBERT) | ✅ every turn | ✅ every turn |
| Embedding (Qwen3-0.6B) | ✅ | ❌ |
| FAISS search | ✅ | ❌ |
| Reranker (BGE) | ✅ | ❌ |
| LLM | ✅ | ✅ |

Intent runs on **every** user message (~50ms). The full retrieval pipeline only
fires on ad-injection turns (configurable interval).

---

## Architecture

```
┌─ app.py ─────────────────────────────────────────────────────────┐
│  Routes: ?dev= → run_dev_mode(), else run_participant_mode()      │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌─ core/ui/ ───────▼──────────────────────────────────────────────┐
│  participant.py  ← screen dispatcher (if/elif on current_screen) │
│  dev.py           ← free-chat / flow-test                        │
│  screens.py       ← render helpers for each screen               │
│  dashboard.py     ← experiment log viewer (pages/dashboard.py)   │
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌─ core/experiment ─▼─────────────────────────────────────────────┐
│  controller.py   ← state machine (screen sequence, advance/back) │
│  query_params.py ← URL parameter parsing                        │
│  surveys.py      ← Likert scales, demographic forms             │
│  tasks.py        ← task catalog (Informational/Transactional/..)│
└──────────────────┬───────────────────────────────────────────────┘
                   │
┌─ core/conversation ─▼───────────────────────────────────────────┐
│  manager.py      ← turn orchestrator (intent→retrieval→LLM→log)  │
│  llm_client.py   ← HTTP client for OpenAI-compatible APIs        │
└──────────────────┬───────────────────────────────────────────────┘
                   ▼
┌─ core/retrieval (5-stage RAG pipeline) ─────────────────────────┐
│  Intent → DenseRetriever → HybridRefiner → Reranker → Formatter  │
│  + hyde.py, runtime.py, query_text.py, log_util.py               │
└──────────────────────────────────────────────────────────────────┘
```

### Thread Architecture

The process runs **three daemon threads** — no separate containers, no subprocesses:

```
┌─ Main thread ──────────────────────────────────────────────────────┐
│  Streamlit event loop + all Python code                            │
│                                                                    │
│  On every user turn (sequential, blocking):                        │
│    intent (BERT) → embed (BERT) → FAISS → reranker → LLM          │
│         ~50ms         ~200ms      ~10ms    ~500ms    ~2-10s        │
│                                                                    │
│  Intent runs on EVERY turn. Retrieval pipeline runs ONLY on        │
│  ad-injection turns. UI freezes during ML calls (single-threaded). │
│  LLM streams token-by-token via st.write_stream.                   │
└────────────────────────────────────────────────────────────────────┘

┌─ Webcam daemon thread ─────────────────────────────────────────────┐
│  _WebcamCapture._capture_loop()  [lab study only]                  │
│  cv2.VideoCapture(0) in a tight loop:                              │
│    read frame → store latest (for preview) → buffer every 2nd      │
│    frame (for session video). Runs at camera framerate (~30fps).   │
│  Started at baseline, stopped at SCREEN_DONE.                      │
│  Preview shown in sidebar during baseline only.                    │
└────────────────────────────────────────────────────────────────────┘

┌─ Logger daemon thread ─────────────────────────────────────────────┐
│  ExperimentLogger._writer_loop()                                   │
│  log() → queue.put(event) (~0.02ms, non-blocking)                  │
│  writer thread → json.dumps + fsync                                │
│  Flush: every 25 events OR every 60s. Crash-safe via atexit.       │
└────────────────────────────────────────────────────────────────────┘
```

All three threads terminate automatically when the main process exits.

---

## Experiment Logging

Structured event logging with async queue-based writes:

```
logs/{experiment_id}/
  {run_id}.jsonl         ← live append file (writer thread)
  {run_id}_export.jsonl  ← clean validated copy
  {run_id}_eyetracking.mp4  ← session webcam recording (lab only)
```

- **Experiment ID**: `exp_20260524T154233Z_a83f2c1d` (timestamp + config hash)
- **Non-blocking**: `log()` enqueues (~0.02ms), background writer does disk I/O
- **Flush**: every 25 events OR every 60s
- **Crash-safe**: `atexit` + daemon thread drain
- **Export**: `.export_jsonl()` for clean validated copy

Events logged per turn: `session_started`, `user_message`, `intent_classified`,
`retrieval`, `ad_injected`, `assistant_reply`, `eyetracking_recording_started`,
`baseline_video_saved`, `session_complete`.

---

## Project Structure

```text
src/project/
├── app.py                         # Streamlit entrypoint (routing only)
├── requirements.txt
├── Dockerfile
├── docker-compose.ollama.yml
├── docker-compose.vllm.yml
├── launch.sh                      # CLI convenience wrapper
├── .env.example
├── pytest.ini
├── LICENSE
│
├── core/
│   ├── config.py                  # Single source of truth for all constants
│   ├── device.py                  # Smart GPU/CPU device allocator
│   │
│   ├── conversation/
│   │   ├── llm_client.py          # Stateless HTTP client (OpenAI-compat API)
│   │   └── manager.py             # Multi-turn orchestrator + ThreadPoolExecutor(4)
│   │
│   ├── ad_injection/
│   │   ├── models.py              # Ad, InjectionResult dataclasses
│   │   ├── injectors.py           # 4 injection strategy classes
│   │   ├── provider.py            # get_ad() / get_injector() public API
│   │   └── ad_links.py            # Ad click tracking helpers
│   │
│   ├── retrieval/                 # 5-stage RAG pipeline
│   │   ├── __init__.py            # retrieve_ad() public entry point
│   │   ├── pipeline.py            # AdRetrievalPipeline (injectable stages)
│   │   ├── catalog.py             # AdCatalog + multi-source FAISS index
│   │   ├── hyde.py                # HyDE query expansion
│   │   ├── runtime.py             # Runtime pipeline config
│   │   ├── query_text.py          # Query text utilities
│   │   ├── log_util.py            # Retrieval event logging
│   │   │
│   │   ├── adapters/              # Dataset schema adapters
│   │   │   ├── base.py            # DatasetAdapter ABC
│   │   │   ├── generic.py         # Generic normalized JSONL
│   │   │   └── amazon.py          # Amazon Reviews 2023 format
│   │   │
│   │   ├── embeddings/            # Embedding model backends
│   │   │   ├── base.py            # EmbeddingModel ABC
│   │   │   └── huggingface.py     # SentenceTransformer backend (BF16)
│   │   │
│   │   ├── rerankers/             # Reranker backends
│   │   │   ├── base.py            # RerankerModel ABC
│   │   │   └── cross_encoder.py   # CrossEncoder backend (BF16)
│   │   │
│   │   └── stages/                # Individual pipeline stages
│   │       ├── state.py           # PipelineState, CatalogItem, RankedCandidate
│   │       ├── base.py            # PipelineStage ABC
│   │       ├── intent.py          # Stage 1 — intent classification
│   │       ├── dense.py           # Stage 2 — FAISS dense retrieval
│   │       ├── hybrid.py          # Stage 3 — BM25 + RRF fusion
│   │       ├── reranker.py        # Stage 4 — cross-encoder reranking
│   │       └── formatter.py       # Stage 5 — Ad dataclass assembly
│   │
│   ├── experiment/
│   │   ├── controller.py          # Screen state machine (Workflow B)
│   │   ├── query_params.py        # URL parameter parsing
│   │   ├── surveys.py             # Survey / scale definitions
│   │   └── tasks.py               # Task catalog
│   │
│   ├── logger/
│   │   ├── experiment_logger.py   # Async queue-based JSONL event logger
│   │   ├── identity.py            # Deterministic experiment/run ID generation
│   │   └── payload.py             # Event payload builders
│   │
│   ├── modalities/
│   │   ├── eeg/                   # EEG LSL marker hooks (BrainVision/OpenBCI)
│   │   └── eye_tracking/          # Tobii Pro gaze snapshot hooks
│   │
│   ├── attention_shift/
│   │   ├── divergence.py          # KL, cosine, JSD divergence functions
│   │   ├── estimators.py          # AttentionEstimator ABC + DummyEstimator
│   │   └── shift.py               # compute_attention_shift() public API
│   │
│   └── ui/
│       ├── participant.py         # Participant screen dispatcher
│       ├── dev.py                 # Developer free-chat + flow-test mode
│       └── screens.py             # Screen rendering helpers
│
├── pages/
│   └── dashboard.py               # Experiment log analytics dashboard
│
├── data/
│   ├── catalogs/                  # Multi-source ad JSONL files (git-tracked)
│   │   ├── travel.jsonl
│   │   └── hobby.jsonl
│   │   # amazon.jsonl generated by prepare script (gitignored)
│   └── faiss.index                # Auto-built, gitignored
│
├── logs/                          # Experiment logs (gitignored at production/)
│
├── resources/
│   └── mock_ad.webp
│
├── docs/
│
├── scripts/
│   ├── prepare_amazon_catalog.py  # Amazon dataset → catalog.jsonl builder
│   └── README.md
│
├── tests/
│   ├── test_query_params.py
│   ├── test_baseline.py
│   └── test_logger.py
│
└── .streamlit/
    ├── config.toml
    └── secrets.toml
```
