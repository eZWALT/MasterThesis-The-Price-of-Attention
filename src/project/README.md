# 📡 Conversational Ad Retrieval — RAG RecSys (Experimentation)

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

The platform provides a ChatGPT-like interface with configurable advertising modes
to study how different ad placements affect user interaction in conversational AI systems.

## Prerequisites

- **Docker & Docker Compose v2** (`docker compose`, not `docker-compose`)
- **Python 3.13+** (for local development without Docker)
- **Ollama mode** (default): your own `ollama` binary installed
- **vLLM mode**: requires `nvidia-container-toolkit`

## Quick Start

```bash
cd src/project
cp .env.example .env      # edit to match your setup
python scripts/prepare_amazon_catalog.py --build-index          
./launch.sh
```

Open http://localhost:7777 — participant mode.  
Open http://localhost:7777?dev=true — developer mode with free-chat.  
Open http://localhost:7777?dev=flow — participant flow walkthrough.  
Open http://localhost:7777?dev=flow&dry_run=1 — flow walkthrough without GPU/models.

### Dry-Run Mode

`?dry_run=1` launches the full participant flow **without loading any ML models**
or requiring a GPU. Useful for UI development, questionnaire testing, and CI.

What it does:
- Skips LLM warmup (no model download, no Ollama/vLLM needed)
- Skips retrieval pipeline config (no sentence-transformers download)
- `LLMClient` returns mock replies instantly (no HTTP call)
- Forces `use_rag=False` so ads are synthetic placeholders
- No FAISS index required — works on a bare checkout

Combines with `dev=flow` to walk through every screen end-to-end in seconds:

```bash
open http://localhost:7777?dev=flow&dry_run=1
```

### Switching backends

```bash
./launch.sh            # ollama (default)
./launch.sh --ollama   # explicit ollama
./launch.sh --vllm     # vLLM (requires nvidia-container-toolkit)
```

---

## Data Setup

The RAG pipeline needs ad catalog(s) (`data/catalogs/*.jsonl`) and a FAISS
index (`data/faiss.index`). The index is auto-rebuilt when missing; catalog
JSONL files are git-tracked.

Use the provided script to pull from
[`milistu/AMAZON-Products-2023`](https://huggingface.co/datasets/milistu/AMAZON-Products-2023)
(117 k products, pre-filtered to 2023 listings):

```bash
# Quick test — 500 Electronics items, no GPU needed
python scripts/prepare_amazon_catalog.py \
    --category meta_Electronics \
    --max-items 500 \
    --build-index

# Full Electronics + Mobile catalog, then build FAISS index
python scripts/prepare_amazon_catalog.py \
    --category meta_Electronics meta_Cell_Phones_and_Accessories \
    --build-index

# All 117 k products
python scripts/prepare_amazon_catalog.py --build-index

# List all available categories
python scripts/prepare_amazon_catalog.py --list-categories
```

Additional catalogs (travel, hobby, etc.) are already provided in
`data/catalogs/` — just delete `data/faiss.index` to rebuild.

See [`scripts/README.md`](scripts/README.md) for the full reference (streaming,
append, HF Hub upload, env var overrides).



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
| 2 | `DenseRetriever` | `Qwen/Qwen3-Embedding-4B` (BF16) | GPU 1 |
| 3 | `HybridRefiner` | BM25 Okapi + RRF score fusion | CPU |
| 4 | `Reranker` | `Qwen/Qwen3-Reranker-4B` (BF16) | GPU 1 |
| 5 | `AdFormatter` | Pure transform — no inference | — |


### Multi-Source Ad Catalogs

All ad sources live as equal JSONL files in `data/catalogs/`:

```
data/catalogs/
  amazon.jsonl     ← 1000 Amazon products
  travel.jsonl     ← synthetic travel ads
  hobby.jsonl      ← synthetic hobby ads
```

Drop a new `.jsonl` file → delete `data/faiss.index` → pipeline auto-rebuilds.  
Each item can have `"metadata": {"source": "synthetic_travel"}` for filtering.

---

## Per-Turn Parallel Execution

After the LLM reply arrives, CPU-bound post-processing runs in a shared
`ThreadPoolExecutor(4)` — never blocking the UI or future modality streams:

```
LLM reply arrives (2-5s wall-clock)
       │
       ├───── _CPU_POOL (4 daemon threads) ─────────────────────┐
       │                                                        │
       │  Thread 1: compute_attention_shift()         ~1ms      │
       │  Thread 2: BERT intent classification        ~30ms     │
       │  Thread 3: EEG marker emission (LSL)         ~0ms      │
       │  Thread 4: Eye-tracking gaze snapshot        ~0ms      │
       │                                                        │
       ├────────────────────────────────────────────────────────┘
       │          .result() ← blocks only on shift + intent
       │          (modality hooks are fire-and-forget)
       │
       └── Return TurnResult to Streamlit UI
```

Register modality hooks (non-blocking, best-effort):

```python
from core.modalities.eeg import eeg_turn_hook
from core.modalities.eye_tracking import eye_tracking_turn_hook

manager.register_modality_hook(eeg_turn_hook)
manager.register_modality_hook(eye_tracking_turn_hook)
```

---

## Experiment Logging

Production-grade structured event logging with zero-copy async writes:

```
logs/{experiment_id}/{run_id}.jsonl
```

- **Experiment ID**: `exp_20260524T154233Z_a83f2c1d` (timestamp + config hash)
- **Non-blocking**: `log()` puts to queue (~0.02ms), background writer does disk I/O
- **Flush policy**: every 25 events OR every 60s (whichever first)
- **Crash-safe**: `atexit` + daemon thread drain
- **Export**: `.export_csv()` for pandas, `.export_jsonl()` for clean validated copy

Events logged per turn: `user_message`, `retrieval`, `assistant_reply`,
`ad_injected`, `attention_shift`, `eye_tracking_ad_exposure`

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

The default adapter is `amazon`, used by `scripts/prepare_amazon_catalog.py`.
See [`scripts/README.md`](scripts/README.md) for data preparation details.

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
│   ├── device.py                  # Smart GPU/CPU device allocator
│   ├── log.py                     # Loguru configuration (LOG_LEVEL, LOG_FILE)
│   │
│   ├── conversation/
│   │   ├── llm_client.py          # Stateless HTTP client (OpenAI-compat API)
│   │   ├── manager.py             # Multi-turn orchestrator + ThreadPoolExecutor
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
│   │   ├── catalog.py             # AdCatalog + multi-source FAISS index
│   │   │
│   │   ├── adapters/              # Dataset schema adapters
│   │   │   ├── base.py            # DatasetAdapter ABC
│   │   │   ├── generic.py         # Generic normalized JSONL (+ metadata merge)
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
│   │   ├── controller.py          # Screen state machine
│   │   └── tasks.py               # Task catalog (Informational/Transactional/Social)
│   │
│   ├── participant/
│   │   └── state.py               # ParticipantState + OCEAN scores
│   │
│   ├── logger/
│   │   ├── experiment_logger.py   # Async queue-based JSONL event logger
│   │   └── identity.py            # Deterministic experiment/run ID generation
│   │
│   ├── modalities/
│   │   ├── eeg/                   # EEG LSL marker hooks
│   │   └── eye_tracking/          # Tobii Pro gaze snapshot hooks
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
├── data/
│   ├── catalogs/                  # Multi-source ad JSONL files (git-tracked)
│   │   ├── amazon.jsonl
│   │   ├── travel.jsonl
│   │   └── hobby.jsonl
│   └── faiss.index                # Auto-built, gitignored
│
├── logs/                          # Experiment JSONL logs (git-tracked)
│
└── scripts/
    └── prepare_amazon_catalog.py  # Amazon dataset → catalog.jsonl builder
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

