#!/usr/bin/env python3
"""
label_sessions.py — Auto-label production log dirs as lab/crowd with quality suffixes.

Usage:
    python3 label_sessions.py                   # dry-run (shows what would be renamed)
    python3 label_sessions.py --exec            # execute renaming
    python3 label_sessions.py --exec --track    # execute + copy to tracked/
"""

import json, glob, os, sys, shutil, re

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "project", "logs", "production")
TRACK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "project", "logs", "tracked")

EXEC = "--exec" in sys.argv
TRACK_ENABLED = "--track" in sys.argv

# --- Helpers ---

def find_events_file(d):
    for pat in ("*_events.jsonl", "events.jsonl", "run_*.jsonl"):
        for fp in sorted(glob.glob(os.path.join(d, pat))):
            if "_export" not in os.path.basename(fp):
                return fp
    return None

def is_gibberish(msg):
    if len(msg) < 3:
        return True
    alpha = sum(c.isalpha() for c in msg)
    return alpha / len(msg) < 0.4

def classify_session(events_file):
    with open(events_file) as f:
        lines = f.readlines()

    first = json.loads(lines[0])
    pid = first.get("participant_id", "")

    study_type = None
    version = None
    worker_id = None
    ocean_raw = None
    user_msgs = []
    conclusions = []
    conditions_completed = 0
    conditions_started = 0
    has_session_complete = False
    has_exp_complete = False
    demo_age = None
    demo_occupation = None

    for line in lines:
        d = json.loads(line)
        evt = d.get("event", "")
        data = d.get("data", {})

        if evt == "session_started" and isinstance(data, dict):
            study_type = data.get("study_type")
        elif evt == "experiment_config" and isinstance(data, dict):
            version = data.get("version")
        elif evt == "session_complete" and isinstance(data, dict):
            has_session_complete = True
            worker_id = data.get("worker_id")
            ocean_raw = data.get("ocean_raw")
        elif evt == "experiment_completed":
            has_exp_complete = True
        elif evt in ("condition_started", "condition_start"):
            conditions_started += 1
        elif evt in ("condition_complete", "condition_end"):
            conditions_completed += 1
        elif evt == "user_message" and isinstance(data, dict):
            msg = data.get("content", "")
            user_msgs.append(msg)
        elif evt == "condition_conclusion_submitted" and isinstance(data, dict):
            conclusions.append(data.get("conclusion", ""))
        elif evt == "demographics_post_submitted" and isinstance(data, dict):
            demo_age = data.get("demo_age", "")
            demo_occupation = data.get("demo_occupation", "")

    # --- Classification ---
    if study_type == "lab":
        prefix = "lab"
    elif study_type == "crowd":
        prefix = "crowd"
    else:
        prefix = "test"

    # --- Quality checks for suffixes ---
    reasons_unfocused = []
    reasons_unfinished = []

    # 1) OCEAN straight-line check
    if ocean_raw and isinstance(ocean_raw, list) and len(ocean_raw) >= 5:
        if len(set(ocean_raw)) == 1:
            reasons_unfocused.append("ocean_straight_line")

    # 2) Gibberish / very short messages
    if user_msgs:
        avg_len = sum(len(m) for m in user_msgs) / len(user_msgs)
        if avg_len < 15:
            reasons_unfocused.append(f"avg_msg_{avg_len:.0f}c")
        gibberish_msgs = sum(1 for m in user_msgs if is_gibberish(m))
        if len(user_msgs) > 0 and gibberish_msgs / len(user_msgs) > 0.5:
            reasons_unfocused.append(f"gibberish_msgs_{gibberish_msgs}/{len(user_msgs)}")

    # 3) First message gibberish
    if user_msgs and is_gibberish(user_msgs[0]) and len(user_msgs) > 0:
        if not any("gibberish" in r for r in reasons_unfocused):
            reasons_unfocused.append("first_msg_gibberish")

    # 4) Gibberish conclusions
    if conclusions:
        bad_conc = [c for c in conclusions if is_gibberish(c)]
        if bad_conc:
            reasons_unfocused.append(f"gibberish_conclusions_{len(bad_conc)}/{len(conclusions)}")

    # 6) Incomplete but has quality data
    completed = has_session_complete or has_exp_complete
    if not completed and conditions_completed > 0:
        if not reasons_unfocused and len(user_msgs) >= 10:
            reasons_unfinished.append(f"{conditions_completed}/{conditions_started}_conds")

    # --- Determine suffix ---
    if reasons_unfocused:
        suffix = "_unfocused"
    elif reasons_unfinished:
        suffix = "_unfinished"
    else:
        suffix = ""

    return {
        "prefix": prefix,
        "suffix": suffix,
        "pid": pid,
        "worker_id": worker_id,
        "version": version,
        "study_type": study_type,
        "msgs": len(user_msgs),
        "conditions": conditions_completed,
        "completed": completed,
    }


def get_next_number(prefix, suffix, existing):
    max_n = 0
    for name in existing:
        esc_prefix = re.escape(prefix)
        esc_suffix = re.escape(suffix) if suffix else ""
        pat = re.compile(rf"^{esc_prefix}_(\d+){esc_suffix}$")
        m = pat.match(name)
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return max_n + 1


def main():
    print("=== Label Production Logs ===")
    print(f"Scanning: {BASE}")
    if TRACK_ENABLED:
        print(f"Track to: {TRACK}")
    print()

    dirs = sorted(glob.glob(os.path.join(BASE, "exp_*")))
    if not dirs:
        print("No unlabeled (exp_*) directories found.")
        return

    all_names = {os.path.basename(d) for d in glob.glob(os.path.join(BASE, "*"))}

    renamed = 0
    skipped = 0

    for d in dirs:
        name = os.path.basename(d)
        events_file = find_events_file(d)
        if not events_file:
            print(f"  SKIP  {name}  (no events file)")
            skipped += 1
            continue

        try:
            info = classify_session(events_file)
        except Exception as e:
            print(f"  ERROR {name}  ({e})")
            skipped += 1
            continue

        prefix = info["prefix"]
        suffix = info["suffix"]

        next_n = get_next_number(prefix, suffix, all_names)
        new_name = f"{prefix}_subject_{next_n}{suffix}"
        new_path = os.path.join(BASE, new_name)

        status = "COMPLETE" if info["completed"] else "PARTIAL"
        wid = info["worker_id"] if info["worker_id"] else "no-id"
        print(f"  {name:45s} -> {new_name:35s}  {status:8s}  msgs={info['msgs']:2d}  conds={info['conditions']}  {wid[:25]}")

        if EXEC:
            try:
                os.rename(d, new_path)
                all_names.add(new_name)
                print(f"           renamed ok")
                renamed += 1

                if TRACK_ENABLED:
                    if info["study_type"] == "lab":
                        track_sub = "lab"
                    elif suffix == "_unfinished":
                        track_sub = "incomplete-crowd"
                    else:
                        track_sub = "crowd"

                    track_dir = os.path.join(TRACK, track_sub)
                    os.makedirs(track_dir, exist_ok=True)
                    track_path = os.path.join(track_dir, new_name)
                    if os.path.isdir(track_path):
                        shutil.rmtree(track_path)
                    shutil.copytree(new_path, track_path)
                    print(f"           tracked to {track_sub}/")
            except Exception as e:
                print(f"           FAILED: {e}")
        else:
            renamed += 1

    print()
    print(f"Summary: {renamed} candidates to label, {skipped} skipped")
    if not EXEC:
        print()
        print("Run with --exec to actually rename.")
        if not TRACK_ENABLED:
            print("Add --track to also copy to tracked/.")

if __name__ == "__main__":
    main()
