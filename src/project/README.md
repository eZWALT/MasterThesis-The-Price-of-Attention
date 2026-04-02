# 📡 TARA — Telefonica Advertising RAG Assistant (Experimentation)

Streamlit-based conversational AI interface for benchmarking advertising strategies in LLM-powered recommender systems. Built in collaboration with Telefonica Research.

---

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Variables](#environment-variables)
4. [Running with Docker Compose](#running-with-docker-compose)
5. [Running Locally](#running-locally)
6. [Project Structure](#project-structure)

---

## Overview

This project provides a ChatGPT-like interface with configurable advertising modes to study how different ad placements affect user interaction in conversational AI systems. The UI connects to a vLLM backend for LLM inference.

**Features:**
- 5 advertising modes (classical, in-chat, suggestions, adjacent, implicit)
- Adjustable model parameters (temperature, max tokens)
- Attention Shift metric — measures how ads alter conversational semantic trajectory
- Modular architecture (ad injection, conversation manager, experiment logger)
- Styled ad panels alongside the chat
- Session logging with JSON export for offline analysis

## Prerequisites

- **Docker & Docker Compose** with NVIDIA runtime (for GPU inference)
- **Python 3.13** (for local development without Docker)

## Environment Variables

Create a `.env` file in this directory with the following variables:

```dotenv
# vLLM Docker Compose variables
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
1. **vLLM** — OpenAI-compatible LLM inference server on port `VLLM_PORT`
2. **Streamlit** — Chat UI on [http://localhost:7777](http://localhost:7777)

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

> **Note:** Port and address are configured in `.streamlit/config.toml`. You still need a running vLLM instance (or change `API_URL` in `core/config.py`).

## Project Structure

```text
.streamlit/
    config.toml              # Streamlit theme, server & browser settings
    secrets.toml             # API keys (gitignored)
app.py                       # Streamlit entrypoint (main chat page)
pages/
    1_📊_Experiment_Dashboard.py  # Multi-page: metrics & log explorer
core/
    __init__.py              # Package exports
    config.py                # Centralised constants & defaults
    ad_injection.py          # Ad content retrieval & injection strategies
    attention_shift.py       # Semantic trajectory analysis (Δ_attn)
    conversation.py          # Multi-turn state & LLM orchestration
    experiment_logger.py     # Structured event logging & export
docker-compose.yml           # vLLM + Streamlit orchestration
Dockerfile                   # Container definition
requirements.txt             # Python dependencies
.env                         # Environment variables
README.md                    # This file
```

## Architecture

```
┌──────────────────────────────────────┐
│  Streamlit                           │
│  ┌──────────┐  ┌──────────────────┐  │
│  │  app.py  │  │  pages/          │  │
│  │  (chat)  │  │  (dashboard)     │  │
│  └────┬─────┘  └───────┬──────────┘  │
│       └───────┬─────────┘            │
└───────────────┼──────────────────────┘
                ▼
┌──────────────────────────────────────┐
│  core/                               │
│  ┌─────────────────┐  ┌───────────┐ │
│  │ ConversationMgr │─▸│  Logger   │ │
│  └───┬─────────┬───┘  └───────────┘ │
│      ▼         ▼                     │
│  ┌────────┐ ┌───────────────┐       │
│  │ Ad     │ │ Attention     │       │
│  │Injection│ │ Shift         │       │
│  └────────┘ └───────────────┘       │
└──────────────────────────────────────┘
```

### Key Concept: Attention Shift

The core research metric. Given a latent concept space Z:

- **Attention state**: A_t = P(Z | C_≤t) — distribution over topics given conversation so far
- **Attention Shift**: Δ_attn = D( P(Z|C_post) ‖ P(Z|C_pre) ) — how much the ad shifts semantic focus

Currently uses a placeholder estimator. Planned backends:
- Embedding-based (sentence-transformers → topic clusters)
- LLM logprob-based (concept probes)
- Knowledge-graph-based

