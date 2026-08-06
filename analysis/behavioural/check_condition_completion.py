"""
Check whether each participant completed all 5 conditions.

Reads Experiment/**/*_export.jsonl and, per participant, records which
conditions were started (condition_start), ended (condition_end), and
had a post-condition survey (post_condition_survey_submitted).

A condition counts as completed when condition_end is present.
All 5 expected conditions must be completed for completed_all=True.

Outputs:
  - participant_condition_completion.csv  (one row per participant)

Script by Katerina, 2026-08-06
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPERIMENT_DIR = ROOT / "Experiment"

EXPECTED_CONDITIONS = (
    "block_early",
    "block_late",
    "inline_early",
    "inline_late",
    "no_ads",
)


def collect_completion(experiment_dir: Path) -> list[dict]:
    # participant_id -> {condition -> {started, ended, surveyed, task_id, ...}}
    by_part: dict[str, dict[str, dict]] = defaultdict(dict)
    source_files: dict[str, set[str]] = defaultdict(set)

    for path in sorted(experiment_dir.rglob("*_export.jsonl")):
        rel = str(path.relative_to(ROOT))

        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                rec = json.loads(line)
                event = rec.get("event")
                data = rec.get("data") or {}
                participant = rec.get("participant_id") or data.get("participant_id")
                if not participant:
                    continue

                source_files[participant].add(rel)

                if event == "condition_start":
                    condition = data.get("condition") or data.get("condition_id")
                    if not condition:
                        continue
                    entry = by_part[participant].setdefault(
                        condition,
                        {
                            "started": False,
                            "ended": False,
                            "surveyed": False,
                            "task_id": None,
                            "trial_index": None,
                            "turns": None,
                        },
                    )
                    entry["started"] = True
                    entry["task_id"] = data.get("task_id") or entry["task_id"]
                    if rec.get("trial_index") is not None:
                        entry["trial_index"] = rec.get("trial_index")
                    continue

                if event == "condition_end":
                    condition = data.get("condition_id") or data.get("condition")
                    if not condition:
                        continue
                    entry = by_part[participant].setdefault(
                        condition,
                        {
                            "started": False,
                            "ended": False,
                            "surveyed": False,
                            "task_id": None,
                            "trial_index": None,
                            "turns": None,
                        },
                    )
                    entry["ended"] = True
                    entry["started"] = True  # end implies it was started
                    entry["task_id"] = data.get("task_id") or entry["task_id"]
                    entry["turns"] = data.get("turns")
                    if rec.get("trial_index") is not None:
                        entry["trial_index"] = rec.get("trial_index")
                    continue

                if event == "post_condition_survey_submitted":
                    condition = data.get("condition") or data.get("condition_id")
                    if not condition:
                        continue
                    entry = by_part[participant].setdefault(
                        condition,
                        {
                            "started": False,
                            "ended": False,
                            "surveyed": False,
                            "task_id": None,
                            "trial_index": None,
                            "turns": None,
                        },
                    )
                    entry["surveyed"] = True

    rows: list[dict] = []
    for participant in sorted(by_part):
        cond_map = by_part[participant]
        completed = [c for c in EXPECTED_CONDITIONS if cond_map.get(c, {}).get("ended")]
        missing = [c for c in EXPECTED_CONDITIONS if c not in completed]
        started_only = [
            c
            for c in EXPECTED_CONDITIONS
            if cond_map.get(c, {}).get("started") and not cond_map.get(c, {}).get("ended")
        ]
        missing_survey = [
            c
            for c in completed
            if not cond_map.get(c, {}).get("surveyed")
        ]
        unexpected = sorted(set(cond_map) - set(EXPECTED_CONDITIONS))

        row = {
            "participant_id": participant,
            "n_completed": len(completed),
            "n_expected": len(EXPECTED_CONDITIONS),
            "completed_all": len(missing) == 0,
            "completed_conditions": ";".join(completed),
            "missing_conditions": ";".join(missing),
            "started_not_ended": ";".join(started_only),
            "missing_survey": ";".join(missing_survey),
            "unexpected_conditions": ";".join(unexpected),
            "source_file": ";".join(sorted(source_files[participant])),
        }

        for condition in EXPECTED_CONDITIONS:
            entry = cond_map.get(condition, {})
            row[f"{condition}_started"] = bool(entry.get("started"))
            row[f"{condition}_ended"] = bool(entry.get("ended"))
            row[f"{condition}_surveyed"] = bool(entry.get("surveyed"))
            row[f"{condition}_task_id"] = entry.get("task_id") or ""

        rows.append(row)

    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not EXPERIMENT_DIR.exists():
        raise SystemExit(f"Experiment folder not found: {EXPERIMENT_DIR}")

    rows = collect_completion(EXPERIMENT_DIR)
    if not rows:
        raise SystemExit("No participants / condition events found.")

    fieldnames = [
        "participant_id",
        "n_completed",
        "n_expected",
        "completed_all",
        "completed_conditions",
        "missing_conditions",
        "started_not_ended",
        "missing_survey",
        "unexpected_conditions",
        "source_file",
    ]
    for condition in EXPECTED_CONDITIONS:
        fieldnames.extend(
            [
                f"{condition}_started",
                f"{condition}_ended",
                f"{condition}_surveyed",
                f"{condition}_task_id",
            ]
        )

    out_path = ROOT / "participant_condition_completion.csv"
    write_csv(out_path, rows, fieldnames)

    n_complete = sum(1 for r in rows if r["completed_all"])
    n_incomplete = len(rows) - n_complete

    print(f"Wrote {len(rows)} participants to {out_path.name}")
    print(f"Expected conditions: {', '.join(EXPECTED_CONDITIONS)}")
    print(f"Completed all 5: {n_complete}")
    print(f"Incomplete:      {n_incomplete}")
    print()
    print(
        f"{'participant_id':<16} {'n':>3}/{len(EXPECTED_CONDITIONS)} "
        f"{'all':>5}  missing"
    )
    for row in rows:
        missing = row["missing_conditions"] or "-"
        print(
            f"{row['participant_id']:<16} {row['n_completed']:>3}/"
            f"{row['n_expected']} {str(row['completed_all']):>5}  {missing}"
        )


if __name__ == "__main__":
    main()
