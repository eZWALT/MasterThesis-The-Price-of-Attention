# 📡 Conversational Ad Retrieval — RAG RecSys

Streamlit-based platform for benchmarking ad strategies in LLM-powered
conversational AI. Built with Telefonica Research.

---

## Quick Start

```bash
cd src/project
cp .env.example .env
python scripts/prepare_amazon_catalog.py --build-index
./launch.sh
```

Open http://localhost:7777 — participant mode (crowd).  
`?study=lab` → lab flow (baseline visible).  
`?webcam=1` → enable session-wide webcam recording (any study type).  
`?dev=true` → free-chat.  
`?dev=flow&dry_run=1` → walkthrough, no GPU.

### Dry run

`?dry_run=1` skips all ML models — mock LLM, no FAISS, no GPU. Runs entirely
on a bare checkout. Combine with `dev=flow` for instant end-to-end testing.

### Backends

```bash
./launch.sh                # ollama (default)
./launch.sh --vllm         # vLLM (nvidia-container-toolkit required)
./launch.sh --host         # Streamlit on host (full GPU access)
./launch.sh --cluster      # multi-GPU Ollama via nginx LB
```

---

## Experiment Flow

5-condition within-subject protocol:

```
consent → baseline [30s eye-tracking] → warmup_chat
→ [condition_intro → condition_chat → conclusion → survey] × 5
→ ads_recall → ocean (BFI-10) → demographics → debrief → done
```

| Study type | `skip` | Webcam | Use case |
|---|---|---|---|
| `crowd` (default) | `baseline` | ❌ | Prolific/MTurk — remote |
| `lab` | — | opt-in via `?webcam=1` | EEG lab, in-person |

Webcam recording runs as a background daemon thread from baseline to `SCREEN_DONE`.
Preview appears in the sidebar during baseline only. Saved to `{run_id}_eyetracking.mp4`.
Opt in with `?webcam=1` on any study type (lab or crowd).

---

## Ad Retrieval Pipeline (RAG)

```
query → IntentClassifier → DenseRetriever → HybridRefiner → Reranker → AdFormatter
                           (FAISS ANN)        (BM25+RRF)    (cross-encoder)
```

| Stage | Model | Device | Runs on |
|---|---|---|---|
| Intent | `Thrad/thrad-bert-conversation-classifier` (DistilBERT) | CPU | **every** turn |
| Embedding | `Qwen/Qwen3-Embedding-0.6B` | GPU/CPU | ad turns only |
| Reranker | `BAAI/bge-reranker-v2-m3` | GPU/CPU | ad turns only |
| LLM | `qwen3.6:35b` (via Ollama/vLLM) | GPU | every turn |

All models load lazily on first use and cache for the process lifetime.

---

## Architecture

```
app.py ─→ run_participant_mode() / run_dev_mode()
              │
              ▼  core/ui/
    participant.py   ← screen dispatcher (if/elif on current_screen)
    dev.py           ← free-chat / flow-test
    screens.py       ← render helpers
              │
              ▼  core/experiment/
    controller.py    ← state machine (advance/back)
    query_params.py  ← URL param parsing
    surveys.py       ← Likert scales, demographics
              │
              ▼  core/conversation/
    manager.py       ← turn orchestrator (intent→retrieval→LLM→log)
    llm_client.py    ← HTTP client for OpenAI-compatible APIs
              │
              ▼  core/retrieval/
    5-stage RAG pipeline + hyde, runtime, log_util
```

### Threads

The process runs **3 daemon threads** — no sidecars, no subprocesses.

| Thread | Work |
|---|---|
| **Main** | Streamlit + all ML (intent→embed→FAISS→rerank→LLM). Blocks during ML; LLM streams. |
| **Webcam** | `cv2.VideoCapture(0)` at `WEBCAM_FPS` fps (default 30), `WEBCAM_WIDTH`×`WEBCAM_HEIGHT` (default 1280×720). Timer-gated capture. Lab only. |
| **Logger** | Drains in-memory event queue to JSONL. ~0.02ms enqueue, flush every 25 events / 60s. |

---

## Experiment Logging

```
logs/{experiment_id}/
  {run_id}.jsonl              ← live append (writer thread)
  {run_id}_export.jsonl       ← clean validated copy
  {run_id}_eyetracking.mp4    ← lab-only webcam recording
```

Event IDs: `session_started`, `user_message`, `intent_classified`, `retrieval`,
`ad_injected`, `assistant_reply`, `eyetracking_recording_started`,
`session_complete`.

---

## Project Structure

```text
src/project/
├── app.py / requirements.txt / Dockerfile / launch.sh / .env.example
├── core/
│   ├── config.py, device.py
│   ├── conversation/       # llm_client, manager (turn orchestrator)
│   ├── ad_injection/       # models, injectors, provider, ad_links
│   ├── retrieval/          # 5-stage RAG + hyde, runtime, log_util
│   │   ├── adapters/       # generic, amazon
│   │   ├── embeddings/     # base, huggingface
│   │   ├── rerankers/      # base, cross_encoder
│   │   └── stages/         # intent, dense, hybrid, reranker, formatter
│   ├── experiment/         # controller, query_params, surveys, tasks
│   ├── logger/             # experiment_logger, identity, payload
│   ├── modalities/         # eeg (LSL), eye_tracking (Tobii)
│   ├── attention_shift/    # divergence, estimators, shift
│   └── ui/                 # participant, dev, screens
├── pages/dashboard.py      # log viewer
├── data/catalogs/          # travel.jsonl, hobby.jsonl (amazon generated)
├── logs/                   # gitignored (production/)
├── scripts/                # catalog builder
└── tests/                  # query_params, baseline, logger
```
