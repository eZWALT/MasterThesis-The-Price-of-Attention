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

- **Docker & Docker Compose** with NVIDIA runtime (for GPU inference via vLLM)
- **Python 3.13+** (for local development without Docker)

## Quick Start

### Local (Streamlit only, no GPU needed)

```bash
cd src/project
pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:7777](http://localhost:7777) — participant mode.
Open [http://localhost:7777?dev=true](http://localhost:7777?dev=true) — developer mode.

> Without a running vLLM backend, LLM calls will fail gracefully. You can
> change `API_URL` in `core/config.py` to point to any OpenAI-compatible
> endpoint (e.g. `http://localhost:11434/v1/chat/completions` for Ollama).

### Docker Compose (full stack with GPU)

```bash
cd src/project
cp .env.example .env   # edit as needed
docker compose up --build
```

## Environment Variables

Create a `.env` file (or copy `.env.example`):

```dotenv
VLLM_PORT=8888
VLLM_MODEL=Qwen/Qwen3.5-9B
VLLM_TENSOR_PARALLEL_SIZE=2
VLLM_MAX_MODEL_LEN=2048
VLLM_VISIBLE_DEVICES=0,1
```

| Variable | Description | Default |
|---|---|---|
| `VLLM_PORT` | Port for the vLLM OpenAI-compatible API | `8888` |
| `VLLM_MODEL` | HuggingFace model identifier | `Qwen/Qwen3.5-9B` |
| `VLLM_TENSOR_PARALLEL_SIZE` | Number of GPUs for tensor parallelism | `2` |
| `VLLM_MAX_MODEL_LEN` | Maximum context length | `2048` |
| `VLLM_VISIBLE_DEVICES` | CUDA visible devices | `0,1` |

## Running with Docker Compose

```bash
docker compose up --build
```

This starts:
1. **vLLM** — OpenAI-compatible LLM inference server on port `VLLM_PORT` (waits for health check)
2. **Streamlit** — Chat UI on [http://localhost:7777](http://localhost:7777)

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

> Port and address are configured in `.streamlit/config.toml`.
> You need a running LLM endpoint — set `API_URL` in `core/config.py`
> or the `API_URL` environment variable.

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
├── docker-compose.yml                  # vLLM + Streamlit orchestration
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

