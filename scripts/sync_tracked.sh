#!/usr/bin/env bash
# sync_tracked.sh — Mirror production log dirs into tracked/ by study type.
# Usage:
#   bash sync_tracked.sh            # dry-run — show what would be copied
#   bash sync_tracked.sh --exec     # actually copy (rsync -a)
#   bash sync_tracked.sh --exec --delete  # copy + remove stale tracked dirs

set -e

BASE_DIR="$(cd "$(dirname "$0")/../src/project/logs/production" && pwd)"
TRACK_DIR="$(cd "$(dirname "$0")/../src/project/logs/tracked" && pwd)"

EXEC=false
DELETE=false
for arg in "$@"; do
    case "$arg" in
        --exec) EXEC=true ;;
        --delete) DELETE=true ;;
    esac
done

echo "=== Sync Tracked ==="
echo "  From: $BASE_DIR"
echo "  To:   $TRACK_DIR"
echo "  Mode: $($EXEC && echo "exec" || echo "dry-run")"
$DELETE && echo "  Delete stale: yes"
echo ""

mkdir -p "$TRACK_DIR"

declare -A TYPE_MAP=(
    [beta_tester_]="beta"
    [crowd_subject_]="crowd"
    [lab_subject_]="lab"
)

copied=0
exists=0
declare -A tracked_set

for d in "$BASE_DIR"/*/; do
    name="$(basename "$d")"
    target=""
    for prefix in "${!TYPE_MAP[@]}"; do
        if [[ "$name" == "$prefix"* ]]; then
            target="${TYPE_MAP[$prefix]}"
            break
        fi
    done

    if [[ -z "$target" ]]; then
        echo "  SKIP  $name  (unknown type)"
        continue
    fi

    dest="$TRACK_DIR/$target/$name"
    tracked_set["$target/$name"]=1

    if [[ -d "$dest" ]]; then
        echo "  EXISTS $target/$name"
        exists=$((exists + 1))
        continue
    fi

    if $EXEC; then
        mkdir -p "$TRACK_DIR/$target"
        cp -a "$d" "$dest"
        echo "  COPY  $name -> $target/"
    else
        echo "  WOULD COPY  $name -> $target/"
    fi
    copied=$((copied + 1))
done

echo ""
echo "Summary: $copied copied, $exists already present"

if $EXEC && $DELETE; then
    echo ""
    echo "--- Checking for stale tracked dirs ---"
    for target_dir in beta crowd lab; do
        td="$TRACK_DIR/$target_dir"
        [[ -d "$td" ]] || continue
        for existing in "$td"/*/; do
            rel="${target_dir}/$(basename "$existing")"
            if [[ -z "${tracked_set[$rel]}" ]]; then
                if $EXEC; then
                    echo "  DELETE stale $rel"
                    rm -rf "$existing"
                else
                    echo "  WOULD DELETE stale $rel"
                fi
            fi
        done
    done
fi

if ! $EXEC; then
    echo ""
    echo "Run with --exec to actually copy."
    echo "Add --delete to remove tracked dirs no longer in production."
fi
