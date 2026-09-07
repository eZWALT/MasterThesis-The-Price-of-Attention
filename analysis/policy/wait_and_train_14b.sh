#!/bin/bash
# Wait for embed_14b_1080.py to write both npy files, then train.
set -u
cd "$(dirname "$0")"
PY=/home/wtroi/miniconda3/bin/python3
LAST=outputs/experiments/full/emb_qwen3-14b_last_1080.npy
MEAN=outputs/experiments/full/emb_qwen3-14b_mean_1080.npy
for i in $(seq 1 180); do
  if [[ -f "$LAST" && -f "$MEAN" ]]; then
    echo "[$(date -Is)] 14B 1080 embeddings ready"
    CUDA_VISIBLE_DEVICES= PYTHONUNBUFFERED=1 $PY -u train_14b_1080.py \
      > outputs/experiments/full/train14b1080.log 2>&1
    echo "[$(date -Is)] train14b exit $?"
    exit 0
  fi
  sleep 20
done
echo "timeout waiting for 14B 1080 embeddings"
exit 1
