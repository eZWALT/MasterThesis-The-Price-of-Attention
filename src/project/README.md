# 📡 TARA — Telefonica Advertising RAG Assistant (Experimentation)

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

