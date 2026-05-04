# 📡 TARA — Telefonica Advertising RAG Assistant (Experimentation)

Streamlit-based conversational AI interface for benchmarking advertising strategies
in LLM-powered recommender systems. Built in collaboration with Telefonica Research.

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Environment Variables](#environment-variables)
5. [Running with Docker Compose](#running-with-docker-compose)
6. [Running Locally (no Docker)](#running-locally-no-docker)
7. [Ad Retrieval Pipeline (RAG)](#ad-retrieval-pipeline-rag)
8. [Project Structure](#project-structure)
9. [Architecture](#architecture)

---

## Overview

TARA provides a ChatGPT-like interface with configurable advertising modes
to study how different ad placements affect user interaction in conversational AI systems.

**Features:**
- 4 advertising modes (inline_persuasive, sponsored_conversational,
  sponsored_recommendation, explicit_ad_block)
- Task-based experimental trials with turn tracking (min 6, max 10 turns)
- Attention Shift metric — measures how ads alter conversational semantic trajectory
- Dual UI mode: participant-facing (minimal) and developer mode (`?dev=true`)
- Modular 5-stage RAG retrieval pipeline — swappable at every layer
- Structured logging via **loguru** (level + optional file sink via env vars)
- Dataset adapters for generic JSONL and Amazon Reviews 2023 catalogs
- Session logging with JSON export for offline analysis

## Prerequisites

- **Docker & Docker Compose v2** (`docker compose`, not `docker-compose`)
- **Python 3.13+** (for local development without Docker)
- **Ollama mode** (default): your own `ollama` binary installed
- **vLLM mode**: requires `nvidia-container-toolkit`

## Quick Start

```bash
cd src/project
cp .env.example .env      # edit to match your setup
./launch.sh
```

Open http://localhost:7777 — participant mode.  
Open http://localhost:7777?dev=true — developer mode with free-chat.  
Open http://localhost:7777?dev=flow — participant flow walkthrough.  

### Switching backends

```bash
./launch.sh            # ollama (default)
./launch.sh --ollama   # explicit ollama
./launch.sh --vllm     # vLLM (requires nvidia-container-toolkit)
```

---

## Environment Variables

### Core / LLM

| Variable | Default | Description |
|---|---|---|
| `API_URL` | `http://localhost:11435/v1/chat/completions` | OpenAI-compatible chat endpoint |
| `DEFAULT_MODEL` | `qwen3.6:35b` | Conversational LLM model id |
| `STREAMLIT_PORT` | `7777` | Port exposed by Docker / Streamlit |
| `OLLAMA_PORT` | `11435` | Ollama server port |
| `OLLAMA_BIN` | *(path)* | Path to the `ollama` binary |
| `OLLAMA_MODEL` | `qwen3.6:35b` | Model to pull and serve in Ollama |
| `VLLM_PORT` | `8888` | vLLM server port |
| `VLLM_MODEL` | `Qwen/Qwen3.5-9B` | Model for vLLM |
| `VLLM_TENSOR_PARALLEL_SIZE` | `2` | Tensor parallel size (GPUs) |

### RAG / Retrieval pipeline

| Variable | Default | Description |
|---|---|---|
| `AD_BACKEND` | `mock` | `mock` — static placeholder ad; `rag` — full retrieval |
| `INTENT_MODEL_NAME` | `Thrad/thrad-bert-conversation-classifier` | Intent classifier checkpoint (HF) |
| `INTENT_DEVICE` | `cpu` | Device for the intent model |
| `EMBEDDING_MODEL_NAME` | `Qwen/Qwen3-Embedding-8B` | Embedding model (sentence-transformers) |
| `EMBEDDING_DEVICE` | `cuda:1` | Device for the embedding model |
| `RERANKER_MODEL_NAME` | `Qwen/Qwen3-Reranker-8B` | Cross-encoder reranker (sentence-transformers) |
| `RERANKER_DEVICE` | `cuda:1` | Device for the reranker |
| `CATALOG_PATH` | `data/catalog.jsonl` | Path to the product catalog |
| `FAISS_INDEX_PATH` | `data/faiss.index` | Path to the FAISS index (rebuilt if missing) |
| `CATALOG_ADAPTER` | `generic` | Dataset adapter: `generic` or `amazon` |

### Logging

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Loguru verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FILE` | *(unset)* | If set, write rotating logs to this path (e.g. `logs/tara.log`) |

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

### Convenience wrapper

```bash
./launch.sh                  # default: ollama
./launch.sh --ollama         # explicit
./launch.sh --vllm           # vLLM
./launch.sh --vllm --rebuild # force Docker rebuild
```

---

## Running Locally (no Docker)

```bash
cd src/project
pip install -r requirements.txt
streamlit run app.py
```

**With full RAG pipeline (GPU required):**

```bash
cd src/project
PYTHONPATH=$(pwd) \
  AD_BACKEND=rag \
  CATALOG_ADAPTER=generic \
  EMBEDDING_DEVICE=cuda:1 \
  RERANKER_DEVICE=cuda:1 \
  LOG_LEVEL=DEBUG \
  streamlit run app.py
```

**With Amazon dataset:**

```bash
CATALOG_ADAPTER=amazon CATALOG_PATH=data/amazon_electronics.jsonl streamlit run app.py
```

**Headless pipeline test (no UI):**

```bash
cd src/project
PYTHONPATH=$(pwd) AD_BACKEND=rag python3 -c "
from core.retrieval import retrieve_ad
ad = retrieve_ad('I need new headphones', [])
print(ad.title, '|', ad.relevance_score)
"
```

---

## Ad Retrieval Pipeline (RAG)

Enable with `AD_BACKEND=rag`. Runs lazily on first ad injection; all models
are cached for the process lifetime.

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
| 2 | `DenseRetriever` | Configurable HF embedding (default: Qwen3-Embedding-8B) | GPU 1 |
| 3 | `HybridRefiner` | BM25 Okapi + RRF score fusion | CPU |
| 4 | `Reranker` | Configurable cross-encoder (default: Qwen3-Reranker-8B) | GPU 1 |
| 5 | `AdFormatter` | Pure transform — no inference | — |

The embedding model is loaded once and **shared** between `AdCatalog` (index
build) and `DenseRetriever` (query encoding) to avoid duplicating a large
model in memory.

### Adding a custom stage or swapping a stage

```python
from core.retrieval.pipeline import AdRetrievalPipeline
from core.retrieval.stages.dense import DenseRetriever
from core.retrieval.stages.formatter import AdFormatter
from core.retrieval.stages.intent import IntentClassifier

pipeline = AdRetrievalPipeline(
    catalog=catalog,
    stages=[
        IntentClassifier(),
        DenseRetriever(catalog, embedding_model=embed),
        AdFormatter(),  # skip hybrid + reranker for a fast baseline
    ],
)
```

### Adding a new catalog dataset

1. Create `core/retrieval/adapters/my_dataset.py` subclassing `DatasetAdapter`.
2. Implement `to_catalog_item(raw)` mapping raw fields → normalised schema.
3. Register it in `core/retrieval/adapters/__init__.py` under `_REGISTRY`.
4. Set `CATALOG_ADAPTER=my_dataset` (env var or `CATALOG_ADAPTER` in `core/config.py`).

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
│
├── core/
│   ├── config.py                  # Single source of truth for all constants
│   ├── log.py                     # Loguru configuration (LOG_LEVEL, LOG_FILE)
│   │
│   ├── conversation/
│   │   ├── llm_client.py          # Stateless HTTP client (OpenAI-compat API)
│   │   ├── manager.py             # Multi-turn conversation orchestrator
│   │   └── ollama_stats.py        # ETA estimation helper
│   │
│   ├── ad_injection/
│   │   ├── models.py              # Ad, InjectionResult dataclasses
│   │   ├── injectors.py           # 4 injection strategy classes
│   │   └── provider.py            # get_ad() / get_injector() public API
│   │
│   ├── retrieval/                 # 5-stage RAG pipeline
│   │   ├── __init__.py            # retrieve_ad() public entry point
│   │   ├── pipeline.py            # AdRetrievalPipeline (injectable stages)
│   │   ├── catalog.py             # AdCatalog + FAISS index management
│   │   │
│   │   ├── adapters/              # Dataset schema adapters
│   │   │   ├── base.py            # DatasetAdapter ABC
│   │   │   ├── generic.py         # Generic normalized JSONL
│   │   │   └── amazon.py          # Amazon Reviews 2023 format
│   │   │
│   │   ├── embeddings/            # Embedding model backends
│   │   │   ├── base.py            # EmbeddingModel ABC
│   │   │   └── huggingface.py     # SentenceTransformer backend
│   │   │
│   │   ├── rerankers/             # Reranker backends
│   │   │   ├── base.py            # RerankerModel ABC
│   │   │   └── cross_encoder.py   # CrossEncoder backend
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
│   │   ├── controller.py          # Screen state machine
│   │   └── tasks.py               # Task catalog (Informational/Transactional/Social)
│   │
│   ├── participant/
│   │   └── state.py               # ParticipantState + OCEAN scores
│   │
│   ├── logger/
│   │   └── experiment_logger.py   # Structured experiment event log
│   │
│   ├── persistence/
│   │   └── store.py               # SessionStore (Null / File / Redis)
│   │
│   ├── attention_shift/
│   │   ├── divergence.py          # KL, cosine, JSD divergence functions
│   │   ├── estimators.py          # AttentionEstimator ABC + DummyEstimator
│   │   └── shift.py               # compute_attention_shift() public API
│   │
│   └── ui/
│       ├── participant.py         # Participant-facing screens
│       ├── dev.py                 # Developer free-chat + flow-test mode
│       └── screens.py             # Screen rendering helpers
│
└── data/                          # Gitignored: catalog.jsonl, faiss.index
```

---

## Architecture

```
┌────────────────────────────────────────────────────────┐
│  Streamlit (app.py + pages/)                           │
└──────────────────────┬─────────────────────────────────┘
                       ▼
┌────────────────────────────────────────────────────────┐
│  core/                                                 │
│  ┌──────────────────┐    ┌─────────────────────────┐   │
│  │  Conversation     │───▶│  Logger (loguru-based)  │   │
│  │  Engine           │    └─────────────────────────┘   │
│  └──┬──────────┬────┘                                   │
│     ▼          ▼                                        │
│  ┌──────────┐ ┌────────────────────────────────────┐    │
│  │ Ad       │ │ Retrieval Pipeline (RAG)            │    │
│  │ Inject   │ │  Intent→Dense→Hybrid→Rerank→Format │    │
│  └──────────┘ └────────────────────────────────────┘    │
│  ┌──────────────────┐    ┌─────────────────────────┐    │
│  │  Experiment       │───▶│  Participant State      │    │
│  │  Controller       │    │  + OCEAN scores         │    │
│  └──────────────────┘    └─────────────────────────┘    │
│  ┌──────────────────────────────────────────────────┐   │
│  │  config.py — single source of truth              │   │
│  │  log.py    — loguru sink (LOG_LEVEL / LOG_FILE)  │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────┘
```

### Key Concept: Attention Shift

- **Attention state**: $A_t = P(Z \mid C_{\le t})$
- **Attention Shift**: $\Delta_{attn} = D\bigl(P(Z \mid C_{post}) \,\Vert\, P(Z \mid C_{pre})\bigr)$

Divergence methods: `kl`, `cosine`, `jsd` (default). Controlled via `DEFAULT_DIVERGENCE_METHOD` in `config.py`.

Current estimator: `DummyEstimator` (uniform placeholder).  
Planned: embedding-based (topic clusters), LLM logprob probes.


Streamlit-based conversational AI interface for benchmarking advertising strategies in LLM-powered recommender systems. Built in collaboration with Telefonica Research.

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Environment Variables](#environment-variables)
5. [Running with Docker Compose](#running-with-docker-compose)
6. [Running Locally](#running-locally)
7. [Project Structure](#project-structure)

---

## Overview

This project provides a ChatGPT-like interface with configurable advertising modes to study how different ad placements affect user interaction in conversational AI systems. The UI connects to a vLLM backend for LLM inference.

**Features:**
- 5 advertising modes (classical, in-chat, suggestions, adjacent, implicit)
- Task-based experimental trials with turn tracking (min 6, max 10 turns)
- Attention Shift metric — measures how ads alter conversational semantic trajectory
- Dual UI mode: participant-facing (minimal) and developer mode (`?dev=true`)
- Modular architecture mirroring the paper's 5 system components
- Session logging with JSON export for offline analysis

## Prerequisites

- **Docker & Docker Compose v2** (`docker compose`, not `docker-compose`)
- **Python 3.13+** (for local development without Docker)
- **Ollama mode** (default): your own `ollama` binary installed
- **vLLM mode**: requires `nvidia-container-toolkit` configured in Docker daemon (needs sysadmin)

## Quick Start

```bash
cd src/project
cp .env.example .env   # edit OLLAMA_BIN to your path, adjust other values as needed
./launch.sh            # starts ollama + pulls model + starts Streamlit (default)
```

Open [http://localhost:7777](http://localhost:7777) — participant mode.  
Open [http://localhost:7777?dev=true](http://localhost:7777?dev=true) — developer mode.

### Switching backends

```bash
./launch.sh            # ollama (default)
./launch.sh --ollama   # explicit ollama
./launch.sh --vllm     # vLLM (requires nvidia-container-toolkit)
```

### Local (no Docker)

```bash
pip install -r requirements.txt
streamlit run app.py
```

> `API_URL` and `DEFAULT_MODEL` are read from env vars — set them to point at
> any running OpenAI-compatible endpoint, or leave them to use the defaults
> from `core/config.py`.

## Environment Variables

All values live in `.env` (copy from `.env.example`). The launch script sources
it automatically — no value is hardcoded in the compose files.

```dotenv
# Streamlit
STREAMLIT_PORT=7777

# Ollama
OLLAMA_BIN=/home/<user>/ollama-local/bin/ollama
OLLAMA_PORT=11435
OLLAMA_MODEL=qwen3.6:35b

# vLLM
VLLM_PORT=8888
VLLM_MODEL=Qwen/Qwen3.5-9B
VLLM_TENSOR_PARALLEL_SIZE=2
VLLM_MAX_MODEL_LEN=2048
VLLM_VISIBLE_DEVICES=0,1
```

| Variable | Description |
|---|---|
| `STREAMLIT_PORT` | Port Streamlit listens on |
| `OLLAMA_BIN` | Absolute path to your `ollama` binary |
| `OLLAMA_PORT` | Port for your ollama instance (avoid 11434 if shared) |
| `OLLAMA_MODEL` | Ollama model tag to pull and serve |
| `VLLM_PORT` | Port for the vLLM OpenAI-compatible API |
| `VLLM_MODEL` | HuggingFace model identifier for vLLM |
| `VLLM_TENSOR_PARALLEL_SIZE` | Number of GPUs for tensor parallelism |
| `VLLM_MAX_MODEL_LEN` | Maximum context length |
| `VLLM_VISIBLE_DEVICES` | CUDA visible devices |

## Running with Docker Compose

Use `launch.sh` — it handles ollama lifecycle, model pulling, and compose startup.
The two compose files are:

- `docker-compose.ollama.yml` — Streamlit only, connects to host ollama
- `docker-compose.vllm.yml` — vLLM + Streamlit (requires nvidia-container-toolkit)

## Project Structure

```text
src/project/
├── .streamlit/
│   ├── config.toml                     # Streamlit theme, server & browser settings
│   └── secrets.toml                    # API keys (gitignored)
├── app.py                              # Streamlit entrypoint (main chat page)
├── pages/
│   └── 1_📊_Experiment_Dashboard.py    # Multi-page: metrics & log explorer
├── core/
│   ├── __init__.py                     # Package facade — re-exports everything
│   ├── config.py                       # ALL constants & defaults (single source of truth)
│   ├── conversation/                   # 1. Conversation Engine
│   │   ├── __init__.py
│   │   ├── llm_client.py              #    Stateless HTTP client for vLLM
│   │   └── manager.py                 #    ConversationManager, TurnResult
│   ├── ad_injection/                   # 2. Advertisement Injection Engine
│   │   ├── __init__.py
│   │   ├── models.py                  #    Ad, InjectionResult dataclasses
│   │   ├── injectors.py              #    AdInjector base + 5 strategies
│   │   └── provider.py               #    get_ad(), get_injector() factory
│   ├── experiment/                     # 3. Experiment Controller
│   │   ├── __init__.py
│   │   ├── tasks.py                   #    TaskDefinition, TASK_CATALOG
│   │   └── controller.py             #    Session flow, counterbalancing (stub)
│   ├── participant/                    # 4. Participant State Manager
│   │   ├── __init__.py
│   │   └── state.py                   #    ParticipantState, OceanScores (stub)
│   ├── logger/                         # 5. Multimodal Logging System
│   │   ├── __init__.py
│   │   └── experiment_logger.py       #    ExperimentLogger, LogEntry
│   └── attention_shift/                # Cross-cutting metric (Δ_attn)
│       ├── __init__.py
│       ├── divergence.py              #    KL, cosine, JSD functions
│       ├── estimators.py             #    AttentionEstimator, DummyEstimator
│       └── shift.py                   #    compute_attention_shift()
├── docker-compose.ollama.yml           # Ollama backend (default)
├── docker-compose.vllm.yml             # vLLM + Streamlit orchestration
├── launch.sh                           # Unified launcher (--ollama / --vllm)
├── Dockerfile                          # Streamlit container
├── requirements.txt                    # Python deps (Streamlit container only)
├── .env.example                        # Template for Docker env vars
└── README.md                           # This file
```

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Streamlit (app.py + pages/)                     │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Chat UI     │  │  Experiment Dashboard     │  │
│  │  (app.py)    │  │  (pages/)                │  │
│  └──────┬───────┘  └──────────┬───────────────┘  │
│         └──────────┬──────────┘                   │
└────────────────────┼─────────────────────────────┘
                     ▼
┌──────────────────────────────────────────────────┐
│  core/                                           │
│                                                  │
│  ┌─────────────────┐    ┌───────────────────┐    │
│  │ 1. Conversation │───▸│ 5. Logger         │    │
│  │    Engine       │    └───────────────────┘    │
│  └───┬─────────┬───┘                             │
│      ▼         ▼                                 │
│  ┌─────────┐ ┌──────────────┐                    │
│  │ 2. Ad   │ │ Attention    │                    │
│  │ Inject  │ │ Shift        │                    │
│  └─────────┘ └──────────────┘                    │
│                                                  │
│  ┌─────────────────┐    ┌───────────────────┐    │
│  │ 3. Experiment   │───▸│ 4. Participant    │    │
│  │    Controller   │    │    State          │    │
│  └─────────────────┘    └───────────────────┘    │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │ config.py — single source of truth       │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘
```

### Key Concept: Attention Shift

The core research metric. Given a latent concept space Z:

- **Attention state**: A_t = P(Z | C_≤t) — distribution over topics given conversation so far
- **Attention Shift**: Δ_attn = D( P(Z|C_post) ‖ P(Z|C_pre) ) — how much the ad shifts semantic focus

Currently uses a placeholder estimator. Planned backends:
- Embedding-based (sentence-transformers → topic clusters)
- LLM logprob-based (concept probes)
- Knowledge-graph-based

