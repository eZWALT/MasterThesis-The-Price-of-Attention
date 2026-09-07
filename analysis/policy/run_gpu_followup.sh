#!/bin/bash
set -u
cd "$(dirname "$0")"
PY=/home/wtroi/miniconda3/bin/python3
LOG=outputs/experiments/full
mkdir -p "$LOG"

echo "[$(date -Is)] instruct embeddings" | tee -a "$LOG/orchestrator.log"
CUDA_VISIBLE_DEVICES=1 PYTHONUNBUFFERED=1 HF_HUB_DISABLE_PROGRESS_BARS=1 \
  $PY -u embed_instruct.py > "$LOG/instruct.log" 2>&1
echo "[$(date -Is)] instruct exit $?" | tee -a "$LOG/orchestrator.log"

echo "[$(date -Is)] 14B last+mean on 1080" | tee -a "$LOG/orchestrator.log"
CUDA_VISIBLE_DEVICES=1 PYTHONUNBUFFERED=1 HF_HUB_DISABLE_PROGRESS_BARS=1 \
  $PY -u embed_14b_1080.py > "$LOG/emb14b1080.log" 2>&1
echo "[$(date -Is)] 14b1080 exit $?" | tee -a "$LOG/orchestrator.log"

echo "[$(date -Is)] GPU followup embeddings done" | tee -a "$LOG/orchestrator.log"
