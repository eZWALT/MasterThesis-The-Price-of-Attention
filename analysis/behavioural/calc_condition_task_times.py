"""
Average condition time, reply time, and message length per condition.

Reads Experiment/**/*_export.jsonl:

1) Condition-task duration from condition_end events (trial_start_ts -> trial_end_ts).
2) Reply latency from user_message.data.time_to_reply_ms, mapped to the
   active condition via the most recent condition_start in that file.
   First turns (null time_to_reply_ms) and warmup messages are skipped.
3) Message character length from user_message / assistant_reply data.msg_len
   inside each condition (warmup excluded).

Outputs:
  - participant_condition_task_times.csv
  - condition_avg_task_times.csv
  - participant_condition_reply_times.csv  (one row per numeric reply)
  - condition_avg_reply_times.csv
  - participant_condition_message_lengths.csv
  - condition_avg_message_lengths.csv

Code by Katerina, 2026-08-06 
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parent
EXPERIMENT_DIR = ROOT / "Experiment"


def parse_ts(value: str) -> datetime:
    """Parse ISO timestamps from exports (with or without timezone / microseconds)."""
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(text[:26], fmt)
            except ValueError:
                continue
        raise


def duration_seconds(start: str, end: str) -> float:
    return (parse_ts(end) - parse_ts(start)).total_seconds()


def collect_task_times(experiment_dir: Path) -> list[dict]:
    rows: list[dict] = []

    for path in sorted(experiment_dir.rglob("*_export.jsonl")):
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                rec = json.loads(line)
                if rec.get("event") != "condition_end":
                    continue

                data = rec.get("data") or {}
                start = data.get("trial_start_ts")
                end = data.get("trial_end_ts")
                condition = data.get("condition_id") or data.get("condition")
                task_id = data.get("task_id")
                participant = rec.get("participant_id") or data.get("participant_id")

                if not (participant and condition and start and end):
                    continue

                seconds = duration_seconds(start, end)
                rows.append(
                    {
                        "participant_id": participant,
                        "condition": condition,
                        "task_id": task_id,
                        "trial_index": rec.get("trial_index"),
                        "trial_start_ts": start,
                        "trial_end_ts": end,
                        "duration_sec": round(seconds, 3),
                        "duration_min": round(seconds / 60.0, 3),
                        "source_file": str(path.relative_to(ROOT)),
                    }
                )

    return rows


def collect_reply_times(experiment_dir: Path) -> list[dict]:
    """Collect numeric time_to_reply_ms values tagged with active condition."""
    rows: list[dict] = []

    for path in sorted(experiment_dir.rglob("*_export.jsonl")):
        current_condition = None
        current_task_id = None

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                rec = json.loads(line)
                event = rec.get("event")
                data = rec.get("data") or {}

                if event == "condition_start":
                    current_condition = data.get("condition") or data.get("condition_id")
                    current_task_id = data.get("task_id")
                    continue

                if event == "condition_end":
                    # Condition chat is over; later messages (surveys) are not replies.
                    current_condition = None
                    current_task_id = None
                    continue

                if event != "user_message":
                    continue

                ttr = data.get("time_to_reply_ms")
                if ttr is None:
                    continue
                if not current_condition:
                    # Warmup / outside a condition trial
                    continue

                participant = rec.get("participant_id")
                rows.append(
                    {
                        "participant_id": participant,
                        "condition": current_condition,
                        "task_id": current_task_id,
                        "trial_index": rec.get("trial_index"),
                        "turn": rec.get("turn"),
                        "time_to_reply_ms": round(float(ttr), 3),
                        "time_to_reply_sec": round(float(ttr) / 1000.0, 3),
                        "source_file": str(path.relative_to(ROOT)),
                    }
                )

    return rows


def collect_message_lengths(experiment_dir: Path) -> list[dict]:
    """Collect msg_len for user and assistant messages inside each condition."""
    rows: list[dict] = []

    for path in sorted(experiment_dir.rglob("*_export.jsonl")):
        current_condition = None
        current_task_id = None

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                rec = json.loads(line)
                event = rec.get("event")
                data = rec.get("data") or {}

                if event == "condition_start":
                    current_condition = data.get("condition") or data.get("condition_id")
                    current_task_id = data.get("task_id")
                    continue

                if event == "condition_end":
                    current_condition = None
                    current_task_id = None
                    continue

                if event not in ("user_message", "assistant_reply"):
                    continue
                if not current_condition:
                    continue

                msg_len = data.get("msg_len")
                if msg_len is None and data.get("content") is not None:
                    msg_len = len(data["content"])
                if msg_len is None:
                    continue

                rows.append(
                    {
                        "participant_id": rec.get("participant_id"),
                        "condition": current_condition,
                        "task_id": current_task_id,
                        "role": "user" if event == "user_message" else "assistant",
                        "trial_index": rec.get("trial_index"),
                        "turn": rec.get("turn"),
                        "msg_len": int(msg_len),
                        "source_file": str(path.relative_to(ROOT)),
                    }
                )

    return rows


def average_task_by_condition(rows: list[dict]) -> list[dict]:
    by_cond: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_cond[row["condition"]].append(row["duration_sec"])

    summary = []
    for condition, values in sorted(by_cond.items()):
        summary.append(
            {
                "condition": condition,
                "n": len(values),
                "mean_sec": round(mean(values), 3),
                "median_sec": round(median(values), 3),
                "mean_min": round(mean(values) / 60.0, 3),
                "median_min": round(median(values) / 60.0, 3),
                "min_sec": round(min(values), 3),
                "max_sec": round(max(values), 3),
            }
        )
    return summary


def average_reply_by_condition(rows: list[dict]) -> list[dict]:
    by_cond: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_cond[row["condition"]].append(row["time_to_reply_ms"])

    summary = []
    for condition, values in sorted(by_cond.items()):
        summary.append(
            {
                "condition": condition,
                "n_replies": len(values),
                "mean_ms": round(mean(values), 3),
                "median_ms": round(median(values), 3),
                "mean_sec": round(mean(values) / 1000.0, 3),
                "median_sec": round(median(values) / 1000.0, 3),
                "min_ms": round(min(values), 3),
                "max_ms": round(max(values), 3),
            }
        )
    return summary


def average_message_length_by_condition(rows: list[dict]) -> list[dict]:
    """One summary row per condition, with user and assistant stats side by side."""
    by_cond_role: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in rows:
        by_cond_role[(row["condition"], row["role"])].append(row["msg_len"])

    conditions = sorted({cond for cond, _ in by_cond_role})
    summary = []
    for condition in conditions:
        user_vals = by_cond_role.get((condition, "user"), [])
        asst_vals = by_cond_role.get((condition, "assistant"), [])
        summary.append(
            {
                "condition": condition,
                "n_user": len(user_vals),
                "mean_user_chars": round(mean(user_vals), 3) if user_vals else None,
                "median_user_chars": round(median(user_vals), 3) if user_vals else None,
                "min_user_chars": min(user_vals) if user_vals else None,
                "max_user_chars": max(user_vals) if user_vals else None,
                "n_assistant": len(asst_vals),
                "mean_assistant_chars": round(mean(asst_vals), 3) if asst_vals else None,
                "median_assistant_chars": round(median(asst_vals), 3) if asst_vals else None,
                "min_assistant_chars": min(asst_vals) if asst_vals else None,
                "max_assistant_chars": max(asst_vals) if asst_vals else None,
            }
        )
    return summary


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not EXPERIMENT_DIR.exists():
        raise SystemExit(f"Experiment folder not found: {EXPERIMENT_DIR}")

    # --- Task durations ---
    task_rows = collect_task_times(EXPERIMENT_DIR)
    if not task_rows:
        raise SystemExit("No condition_end events with trial timestamps found.")

    task_summary = average_task_by_condition(task_rows)

    task_detail_path = ROOT / "participant_condition_task_times.csv"
    task_summary_path = ROOT / "condition_avg_task_times.csv"

    write_csv(
        task_detail_path,
        task_rows,
        [
            "participant_id",
            "condition",
            "task_id",
            "trial_index",
            "trial_start_ts",
            "trial_end_ts",
            "duration_sec",
            "duration_min",
            "source_file",
        ],
    )
    write_csv(
        task_summary_path,
        task_summary,
        [
            "condition",
            "n",
            "mean_sec",
            "median_sec",
            "mean_min",
            "median_min",
            "min_sec",
            "max_sec",
        ],
    )

    print(f"Wrote {len(task_rows)} rows to {task_detail_path.name}")
    print(f"Wrote {len(task_summary)} conditions to {task_summary_path.name}")
    print()
    print("Average task time per condition (trial_start_ts -> trial_end_ts):")
    print(f"{'condition':<16} {'n':>3} {'mean_min':>10} {'median_min':>11} {'mean_sec':>10}")
    for row in task_summary:
        print(
            f"{row['condition']:<16} {row['n']:>3} "
            f"{row['mean_min']:>10.3f} {row['median_min']:>11.3f} {row['mean_sec']:>10.1f}"
        )

    # --- Reply times ---
    reply_rows = collect_reply_times(EXPERIMENT_DIR)
    if not reply_rows:
        raise SystemExit("No numeric time_to_reply_ms values found inside conditions.")

    reply_summary = average_reply_by_condition(reply_rows)

    reply_detail_path = ROOT / "participant_condition_reply_times.csv"
    reply_summary_path = ROOT / "condition_avg_reply_times.csv"

    write_csv(
        reply_detail_path,
        reply_rows,
        [
            "participant_id",
            "condition",
            "task_id",
            "trial_index",
            "turn",
            "time_to_reply_ms",
            "time_to_reply_sec",
            "source_file",
        ],
    )
    write_csv(
        reply_summary_path,
        reply_summary,
        [
            "condition",
            "n_replies",
            "mean_ms",
            "median_ms",
            "mean_sec",
            "median_sec",
            "min_ms",
            "max_ms",
        ],
    )

    print()
    print(f"Wrote {len(reply_rows)} rows to {reply_detail_path.name}")
    print(f"Wrote {len(reply_summary)} conditions to {reply_summary_path.name}")
    print()
    print("Mean time to reply per condition (user_message.time_to_reply_ms):")
    print(f"{'condition':<16} {'n':>3} {'mean_sec':>10} {'median_sec':>11} {'mean_ms':>12}")
    for row in reply_summary:
        print(
            f"{row['condition']:<16} {row['n_replies']:>3} "
            f"{row['mean_sec']:>10.3f} {row['median_sec']:>11.3f} {row['mean_ms']:>12.1f}"
        )

    # --- Message lengths ---
    msg_rows = collect_message_lengths(EXPERIMENT_DIR)
    if not msg_rows:
        raise SystemExit("No message lengths found inside conditions.")

    msg_summary = average_message_length_by_condition(msg_rows)

    msg_detail_path = ROOT / "participant_condition_message_lengths.csv"
    msg_summary_path = ROOT / "condition_avg_message_lengths.csv"

    write_csv(
        msg_detail_path,
        msg_rows,
        [
            "participant_id",
            "condition",
            "task_id",
            "role",
            "trial_index",
            "turn",
            "msg_len",
            "source_file",
        ],
    )
    write_csv(
        msg_summary_path,
        msg_summary,
        [
            "condition",
            "n_user",
            "mean_user_chars",
            "median_user_chars",
            "min_user_chars",
            "max_user_chars",
            "n_assistant",
            "mean_assistant_chars",
            "median_assistant_chars",
            "min_assistant_chars",
            "max_assistant_chars",
        ],
    )

    print()
    print(f"Wrote {len(msg_rows)} rows to {msg_detail_path.name}")
    print(f"Wrote {len(msg_summary)} conditions to {msg_summary_path.name}")
    print()
    print("Average user message length per condition (characters):")
    print(
        f"{'condition':<16} {'n':>3} {'mean_chars':>12} {'median_chars':>13} "
        f"{'min':>6} {'max':>6}"
    )
    for row in msg_summary:
        print(
            f"{row['condition']:<16} {row['n_user']:>3} "
            f"{row['mean_user_chars']:>12.1f} {row['median_user_chars']:>13.1f} "
            f"{row['min_user_chars']:>6} {row['max_user_chars']:>6}"
        )


if __name__ == "__main__":
    main()
