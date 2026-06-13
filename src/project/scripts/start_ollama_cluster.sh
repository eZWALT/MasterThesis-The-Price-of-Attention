#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# start_ollama_cluster.sh  —  multi-GPU Ollama cluster with nginx LB
#
# Starts one Ollama instance per GPU (on consecutive ports starting from
# OLLAMA_CLUSTER_BASE_PORT), then launches nginx to round-robin across them.
# Streamlit (or any client) hits localhost:OLLAMA_PORT as usual —
# zero code changes.
#
# Prerequisites
# ─────────────
#   - nginx installed (apt install nginx)
#   - OLLAMA_BIN set in .env or passed via env
#   - OLLAMA_MODEL already pulled (or pulls it once)
#
# Usage
# ─────
#   ./scripts/start_ollama_cluster.sh [NUM_GPUS]
#
#   NUM_GPUS  — number of GPUs to use (default: all visible)
#
# Example
# ────────
#   # Use 2 GPUs (0 and 1) for Ollama, rest for retrieval pipeline
#   CUDA_VISIBLE_DEVICES=0,1 ./scripts/start_ollama_cluster.sh 2
#
#   # Use all 4 GPUs for Ollama
#   ./scripts/start_ollama_cluster.sh 4
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Load .env ──────────────────────────────────────────────────────────────
if [[ -f "${PROJECT_DIR}/.env" ]]; then
    set -a
    source "${PROJECT_DIR}/.env"
    set +a
fi

# ── Config ─────────────────────────────────────────────────────────────────
NUM_GPUS="${1:-$(python3 -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo 1)}"
CLUSTER_BASE_PORT="${OLLAMA_CLUSTER_BASE_PORT:-9991}"   # first backend port
CLUSTER_PORT="${OLLAMA_CLUSTER_PORT:-9999}"              # frontend (nginx) port
OLLAMA_BIN="${OLLAMA_BIN:-ollama}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3.6:35b}"
NGINX_CONF="/tmp/ollama_cluster_$$.conf"

_PIDS=()

cleanup() {
    echo "[cluster] Shutting down..."
    # Kill Ollama instances
    for pid in "${_PIDS[@]}"; do
        kill "${pid}" 2>/dev/null || true
    done
    # Remove nginx config
    rm -f "${NGINX_CONF}"
    echo "[cluster] Done."
    exit 0
}
trap cleanup EXIT INT TERM

# ── 1. Kill any existing Ollama on cluster ports ──────────────────────────
echo "[cluster] Checking for existing Ollama processes on cluster ports..."
for (( i=0; i<NUM_GPUS; i++ )); do
    port=$(( CLUSTER_BASE_PORT + i ))
    lsof -ti "tcp:${port}" 2>/dev/null | xargs kill 2>/dev/null || true
done

# ── 2. Pull model (once) ──────────────────────────────────────────────────
if ! "${OLLAMA_BIN}" list 2>/dev/null | grep -q "^${OLLAMA_MODEL}"; then
    echo "[cluster] Pulling ${OLLAMA_MODEL} (one-time)…"
    "${OLLAMA_BIN}" pull "${OLLAMA_MODEL}"
fi

# ── 3. Start one Ollama per GPU ───────────────────────────────────────────
echo "[cluster] Starting ${NUM_GPUS} Ollama instances…"
UPSTREAM_SERVERS=()
for (( i=0; i<NUM_GPUS; i++ )); do
    port=$(( CLUSTER_BASE_PORT + i ))
    export CUDA_VISIBLE_DEVICES="${i}"
    export OLLAMA_HOST="0.0.0.0:${port}"
    export OLLAMA_KEEP_ALIVE="-1"
    export OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-4}"   # concurrent requests per instance

    echo "  GPU ${i} → port ${port}"
    "${OLLAMA_BIN}" serve &
    _PIDS+=($!)

    UPSTREAM_SERVERS+=("localhost:${port}")
    unset CUDA_VISIBLE_DEVICES
done

# ── 4. Wait for all Ollama instances to be ready ──────────────────────────
echo "[cluster] Waiting for all instances to be ready…"
for (( i=0; i<NUM_GPUS; i++ )); do
    port=$(( CLUSTER_BASE_PORT + i ))
    for try in $(seq 1 30); do
        if curl -sf "http://localhost:${port}/api/tags" > /dev/null 2>&1; then
            echo "  GPU ${i} (port ${port}) ready."
            break
        fi
        sleep 1
    done
done

# ── 5. Warm up every instance (load model into VRAM on each GPU) ──────────
echo "[cluster] Warming up model on each GPU…"
for (( i=0; i<NUM_GPUS; i++ )); do
    port=$(( CLUSTER_BASE_PORT + i ))
    echo "  Warming GPU ${i} (port ${port})…"
    curl -sf -X POST "http://localhost:${port}/api/chat" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "'"${OLLAMA_MODEL}"'",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": false,
            "keep_alive": -1,
            "options": {"num_predict": 1}
        }' > /dev/null 2>&1 || echo "  Warning: warmup failed on GPU ${i}"
done

# ── 6. Generate nginx config ──────────────────────────────────────────────
echo "[cluster] Generating nginx config…"
UPSTREAM_BLOCK=""
for server in "${UPSTREAM_SERVERS[@]}"; do
    UPSTREAM_BLOCK+="    server ${server};\n"
done

sed "s/{CLUSTER_PORT}/${CLUSTER_PORT}/g" > "${NGINX_CONF}" << NGINX_EOF
upstream ollama_backends {
    least_conn;
$(printf "${UPSTREAM_BLOCK}")
}

server {
    listen ${CLUSTER_PORT};

    proxy_connect_timeout       600;
    proxy_send_timeout          600;
    proxy_read_timeout          600;
    send_timeout                600;

    proxy_buffering             off;
    proxy_cache                 off;
    proxy_set_header            Connection '';
    chunked_transfer_encoding   on;

    location /api/chat {
        proxy_pass http://ollama_backends;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /api/ {
        proxy_pass http://ollama_backends;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX_EOF

# ── 7. Start nginx with cluster config ────────────────────────────────────
echo "[cluster] Starting nginx on port ${CLUSTER_PORT}…"
nginx -c "${NGINX_CONF}" -p "${PROJECT_DIR}" 2>&1 || {
    echo "ERROR: nginx failed to start. Is it installed?"
    echo "  apt-get install nginx  (or brew install nginx)"
    exit 1
}

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Ollama cluster ready!"
echo "  Frontend : http://localhost:${CLUSTER_PORT}  (nginx, round-robin)"
echo "  Backends : ${NUM_GPUS} GPUs on ports ${CLUSTER_BASE_PORT}-$(( CLUSTER_BASE_PORT + NUM_GPUS - 1 ))"
echo ""
echo "  Set in .env:"
echo "    OLLAMA_API_BASE=http://localhost:${CLUSTER_PORT}"
echo "    OLLAMA_PORT=${CLUSTER_PORT}"
echo "    LLM_BACKEND=ollama"
echo ""
echo "  Press Ctrl+C to stop everything."
echo "═══════════════════════════════════════════════════════════════════"

# ── 8. Wait (foreground) ─────────────────────────────────────────────────
wait
