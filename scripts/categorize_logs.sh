#!/usr/bin/env bash
# categorize_logs.sh — Categorize production logs by study type (lab / crowd / other).
# Usage: bash categorize_logs.sh

set -e

BASE_DIR="$(cd "$(dirname "$0")/../src/project/logs/production" && pwd)"

# Total counter (only used in the summary print, not in arithmetic comparison)
total_logs=0

lab=()
crowd=()
other=()
unknown=()

echo "=== Categorizing Production Logs ==="
echo ""

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
        unknown+=("$folder")
        continue
    fi
    study_type=$(python3 -c "
import json
with open('$events_file') as f:
    for line in f:
        try:
            d = json.loads(line)
            if d.get('event') == 'session_started':
                print(d.get('data', {}).get('study_type', 'other'))
                break
        except:
            pass
" 2>/dev/null || echo "other")

    case "$study_type" in
        lab)
            lab+=("$folder")
            ;;
        crowd)
            crowd+=("$folder")
            ;;
        other)
            other+=("$folder")
            ;;
        *)
            unknown+=("$folder")
            ;;
    esac
done

echo "LAB sessions (${#lab[@]}):"
for f in "${lab[@]}"; do
    echo "  $f"
done

echo ""
echo "CROWD sessions (${#crowd[@]}):"
for f in "${crowd[@]}"; do
    echo "  $f"
done

if [[ ${#other[@]} -gt 0 ]]; then
    echo ""
    echo "OTHER (${#other[@]}):"
    for f in "${other[@]}"; do
        echo "  $f"
    done
fi

if [[ ${#unknown[@]} -gt 0 ]]; then
    echo ""
    echo "UNKNOWN (${#unknown[@]}):"
    for f in "${unknown[@]}"; do
        echo "  $f"
    done
fi

echo ""
echo "Total: ${#lab[@]} lab + ${#crowd[@]} crowd + ${#other[@]} other + ${#unknown[@]} unknown = $(( ${#lab[@]} + ${#crowd[@]} + ${#other[@]} + ${#unknown[@]} ))"
