#!/bin/bash
# After Qwen3-0.6B LoRA releases GPU 1, score Qwen3-Reranker-4B features.
set -u
cd "$(dirname "$0")"
LOG=outputs/experiments/full
while pgrep -f "python3 -u train_tfm_fusion.py" >/dev/null; do
  echo "[$(date -Is)] waiting for LoRA" >> "$LOG/loop.log"
  sleep 45
done
echo "[$(date -Is)] LoRA gone; Qwen reranker on GPU 1" | tee -a "$LOG/loop.log"
CUDA_VISIBLE_DEVICES=1 PYTHONUNBUFFERED=1 HF_HUB_DISABLE_PROGRESS_BARS=1 \
  /home/wtroi/miniconda3/bin/python3 -u train_qwen_rerank.py > "$LOG/qwen_rerank.log" 2>&1
echo "[$(date -Is)] rerank exit $?" | tee -a "$LOG/loop.log"
# freeze only if a new pred clearly wins — freeze_best stays same_t unless we edit it
CUDA_VISIBLE_DEVICES= PYTHONUNBUFFERED=1 \
  /home/wtroi/miniconda3/bin/python3 -u freeze_best.py >> "$LOG/loop.log" 2>&1
echo "[$(date -Is)] followup done" | tee -a "$LOG/loop.log"
