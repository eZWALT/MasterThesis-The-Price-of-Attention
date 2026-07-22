#!/usr/bin/env bash
# housekeep_production.sh — Dry-run safe cleanup of tiny test logs.
# Usage: bash housekeep_production.sh          # dry-run (shows what would be deleted)
#        bash housekeep_production.sh --exec    # actually delete

set -e

BASE_DIR="$(cd "$(dirname "$0")/production" && pwd)"
EXEC=false
if [[ "${1:-}" == "--exec" ]]; then
    EXEC=true
fi

echo "=== Housekeeping Production Logs ==="
echo "Scanning: $BASE_DIR"
echo ""

deleted=0
kept=0

for d in "$BASE_DIR"/exp_*/; do
    folder="$(basename "$d")"
    events_file=""
    for pat in "*_events.jsonl" "events.jsonl" "run_*.jsonl"; do
        found=$(ls "$d"/$pat 2>/dev/null || true)
        if [[ -z "$found" ]]; then
            continue
        fi
        for fp in $found; do
            if [[ "$fp" != *_export.jsonl ]]; then
                events_file="$fp"
                break 2
            fi
        done
    done
    if [[ -z "$events_file" ]]; then
        continue
    fi
    count=$(wc -l < "$events_file")
    if [[ "$count" -le 2 ]]; then
        if $EXEC; then
            echo "  DELETING  $folder  ($count events)"
            rm -rf "$d"
        else
            echo "  WOULD DELETE  $folder  ($count events)"
        fi
        deleted=$((deleted + 1))
    else
        kept=$((kept + 1))
    fi
done

echo ""
echo "Summary: $deleted candidates to remove, $kept to keep"
if ! $EXEC; then
    echo ""
    echo "Run with --exec to actually delete."
fi
