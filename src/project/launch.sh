#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# launch.sh  —  unified launcher
#
# Usage:
#   ./launch.sh              # defaults to ollama
#   ./launch.sh --ollama     # explicit ollama mode (Docker, no GPU)
#   ./launch.sh --host       # run Streamlit on host with GPU access
#   ./launch.sh --vllm       # vLLM mode (requires nvidia-container-toolkit)
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

# ── Defaults ──────────────────────────────────────────────────────────────────
MODE="ollama"

# ── Argument parsing ──────────────────────────────────────────────────────────
for arg in "$@"; do
    case $arg in
        --ollama) MODE="ollama" ;;
        --vllm)   MODE="vllm"   ;;
        --host)   MODE="host"   ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: $0 [--ollama|--host|--vllm]"
            exit 1
            ;;
    esac
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
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────
case $MODE in
    ollama) launch_ollama ;;
    host)   launch_host   ;;
    vllm)   launch_vllm   ;;
esac

wait
