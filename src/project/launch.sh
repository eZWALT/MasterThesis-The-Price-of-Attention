#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# launch.sh  —  unified launcher
#
# Usage:
#   ./launch.sh              # defaults to ollama
#   ./launch.sh --ollama     # explicit ollama mode (Docker, no GPU)
#   ./launch.sh --host       # run Streamlit on host with GPU access
#   ./launch.sh --vllm       # vLLM mode (requires nvidia-container-toolkit)
#   ./launch.sh --cluster    # multi-GPU Ollama cluster via nginx LB
#     Optional: ./launch.sh --cluster 4  (use 4 GPUs for Ollama)
# ─────────────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Load .env (single source of truth) ────────────────────────────────────────
if [[ -f "${SCRIPT_DIR}/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "${SCRIPT_DIR}/.env"
    set +a
else
    echo "ERROR: .env not found at ${SCRIPT_DIR}/.env"
    exit 1
fi

# ── Stamp the repo VERSION into logs, including from inside containers ────────
# The Docker build context is this directory, so the image cannot see the
# repository root; pass the version through the environment instead.
VERSION_FILE="${SCRIPT_DIR}/../../VERSION"
if [[ -f "${VERSION_FILE}" ]]; then
    export APP_VERSION="$(tr -d '[:space:]' < "${VERSION_FILE}")"
    echo "[launch.sh] version: ${APP_VERSION}"
fi

# ── Defaults ──────────────────────────────────────────────────────────────────
MODE="ollama"

# ── Argument parsing ──────────────────────────────────────────────────────────
CLUSTER_GPUS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --ollama)  MODE="ollama" ;;
        --vllm)    MODE="vllm"   ;;
        --host)    MODE="host"   ;;
        --cluster) MODE="cluster"; shift; CLUSTER_GPUS="${1:-}" ;;
        *)
            echo "Unknown argument: $1"
            echo "Usage: $0 [--ollama|--host|--vllm|--cluster [N]]"
            exit 1
            ;;
    esac
    shift
done

echo "[launch.sh] mode: $MODE"

# ─────────────────────────────────────────────────────────────────────────────
# OLLAMA path
# ─────────────────────────────────────────────────────────────────────────────
launch_ollama() {
    export OLLAMA_HOST="0.0.0.0:${OLLAMA_PORT}"
    export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:--1}"   # default: keep model loaded forever

    echo "[1/4] Starting ollama on port ${OLLAMA_PORT}..."
    "$OLLAMA_BIN" serve &
    OLLAMA_PID=$!

    trap "echo 'Shutting down...'; kill \$OLLAMA_PID 2>/dev/null; docker compose -f '${SCRIPT_DIR}/docker-compose.ollama.yml' down" EXIT INT TERM

    echo "[2/4] Waiting for ollama to be ready..."
    until curl -sf "http://localhost:${OLLAMA_PORT}/api/tags" > /dev/null 2>&1; do
        sleep 1
    done
    echo "      ollama is up."

    if "$OLLAMA_BIN" list | grep -q "^${OLLAMA_MODEL}"; then
        echo "[3/4] Model ${OLLAMA_MODEL} already present, skipping pull."
    else
        echo "[3/4] Pulling ${OLLAMA_MODEL} (this may take a while)..."
        "$OLLAMA_BIN" pull "$OLLAMA_MODEL"
    fi

    echo "[4/4] Starting Streamlit..."
    docker compose -f "${SCRIPT_DIR}/docker-compose.ollama.yml" up --build
}

# ─────────────────────────────────────────────────────────────────────────────
# vLLM path
# ─────────────────────────────────────────────────────────────────────────────
launch_vllm() {
    # Sanity check: nvidia-container-toolkit must be configured
    if ! docker info 2>/dev/null | grep -q "nvidia"; then
        echo "ERROR: nvidia runtime not registered in Docker."
        echo "       Ask your sysadmin to run:"
        echo "         apt-get install -y nvidia-container-toolkit"
        echo "         nvidia-ctk runtime configure --runtime=docker"
        echo "         systemctl restart docker"
        exit 1
    fi

    trap "echo 'Shutting down...'; docker compose -f '${SCRIPT_DIR}/docker-compose.vllm.yml' down" EXIT INT TERM

    echo "[1/1] Starting vLLM + Streamlit..."
    docker compose -f "${SCRIPT_DIR}/docker-compose.vllm.yml" up --build
}

# ─────────────────────────────────────────────────────────────────────────────
# HOST path  —  runs Streamlit directly on the host (full GPU access,
#               no nvidia-container-toolkit needed)
# ─────────────────────────────────────────────────────────────────────────────
launch_host() {
    export OLLAMA_HOST="0.0.0.0:${OLLAMA_PORT}"
    export OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:--1}"

    echo "[1/4] Starting ollama on port ${OLLAMA_PORT}..."
    "$OLLAMA_BIN" serve &
    OLLAMA_PID=$!

    trap "echo 'Shutting down...'; kill \$OLLAMA_PID 2>/dev/null" EXIT INT TERM

    echo "[2/4] Waiting for ollama to be ready..."
    until curl -sf "http://localhost:${OLLAMA_PORT}/api/tags" > /dev/null 2>&1; do
        sleep 1
    done
    echo "      ollama is up."

    if "$OLLAMA_BIN" list | grep -q "^${OLLAMA_MODEL}"; then
        echo "[3/4] Model ${OLLAMA_MODEL} already present, skipping pull."
    else
        echo "[3/4] Pulling ${OLLAMA_MODEL} (this may take a while)..."
        "$OLLAMA_BIN" pull "$OLLAMA_MODEL"
    fi

    # Point the app at the local ollama (not Docker host.docker.internal)
    export API_URL="http://localhost:${OLLAMA_PORT}/v1/chat/completions"
    export OLLAMA_API_BASE="http://localhost:${OLLAMA_PORT}"
    export DEFAULT_MODEL="${OLLAMA_MODEL}"
    export LLM_BACKEND="ollama"
    export LLM_THINK="${LLM_THINK:-false}"

    echo "[4/4] Starting Streamlit on host (GPU-enabled)..."
    cd "${SCRIPT_DIR}"
    streamlit run app.py \
        --server.port "${STREAMLIT_PORT}" \
        --server.address 0.0.0.0
}

# ─────────────────────────────────────────────────────────────────────────────
# CLUSTER path  —  multi-GPU Ollama with nginx round-robin
# ─────────────────────────────────────────────────────────────────────────────
launch_cluster() {
    local cluster_script="${SCRIPT_DIR}/scripts/start_ollama_cluster.sh"
    if [[ ! -x "${cluster_script}" ]]; then
        echo "ERROR: ${cluster_script} not found or not executable."
        exit 1
    fi

    echo "[launch.sh] Starting Ollama cluster with ${CLUSTER_GPUS:-all} GPU(s)…"
    "${cluster_script}" ${CLUSTER_GPUS} &
    CLUSTER_PID=$!

    # Wait for nginx to be ready on the cluster port
    local cluster_port="${OLLAMA_CLUSTER_PORT:-9999}"
    echo "[launch.sh] Waiting for nginx on port ${cluster_port}…"
    until curl -sf "http://localhost:${cluster_port}/api/tags" > /dev/null 2>&1; do
        sleep 2
    done
    echo "      Cluster ready."

    # Point the app at the nginx frontend (no code changes needed)
    export API_URL="http://localhost:${cluster_port}/v1/chat/completions"
    export OLLAMA_API_BASE="http://localhost:${cluster_port}"
    export DEFAULT_MODEL="${OLLAMA_MODEL}"
    export LLM_BACKEND="ollama"
    export LLM_THINK="${LLM_THINK:-false}"

    trap "echo 'Shutting down...'; kill ${CLUSTER_PID} 2>/dev/null" EXIT INT TERM

    echo "[launch.sh] Starting Streamlit on host (multi-GPU cluster)…"
    cd "${SCRIPT_DIR}"
    streamlit run app.py \
        --server.port "${STREAMLIT_PORT}" \
        --server.address 0.0.0.0
}

# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────
case $MODE in
    ollama)  launch_ollama  ;;
    host)    launch_host    ;;
    vllm)    launch_vllm    ;;
    cluster) launch_cluster ;;
esac

wait
