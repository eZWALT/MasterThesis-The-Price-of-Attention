#!/bin/bash
# Overnight iteration: fat behavioural features → residual models → transformer fusion.
set -u
cd "$(dirname "$0")"
PY=/home/wtroi/miniconda3/bin/python3
LOG=outputs/experiments/full
mkdir -p "$LOG"

echo "[$(date -Is)] iterate behavioural+14B" | tee -a "$LOG/loop.log"
CUDA_VISIBLE_DEVICES=1 PYTHONUNBUFFERED=1 HF_HUB_DISABLE_PROGRESS_BARS=1 \
  $PY -u train_iterate.py > "$LOG/iterate.log" 2>&1
echo "[$(date -Is)] iterate exit $?" | tee -a "$LOG/loop.log"

echo "[$(date -Is)] transformer fusion" | tee -a "$LOG/loop.log"
CUDA_VISIBLE_DEVICES=1 PYTHONUNBUFFERED=1 HF_HUB_DISABLE_PROGRESS_BARS=1 \
  $PY -u train_tfm_fusion.py > "$LOG/tfm.log" 2>&1
echo "[$(date -Is)] tfm exit $?" | tee -a "$LOG/loop.log"

# If a new pred beats BEST, freeze it
CUDA_VISIBLE_DEVICES= PYTHONUNBUFFERED=1 \
  $PY -u freeze_best.py >> "$LOG/loop.log" 2>&1

echo "[$(date -Is)] loop done" | tee -a "$LOG/loop.log"
