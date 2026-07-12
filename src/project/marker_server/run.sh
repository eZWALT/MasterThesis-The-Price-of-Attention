#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

MODE="${1:-log}"  # log | lsl | psychopy

echo "[run.sh] Starting marker server  (backend=$MODE)"
echo "         http://0.0.0.0:9876"
echo ""

MARKER_BACKEND="$MODE" python server.py
