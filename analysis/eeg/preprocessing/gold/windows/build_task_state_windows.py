"""Build reading and writing 4 s windows from trusted log events.

Reading is the first complete 4 s after ``assistant_reply``. Writing is the
last complete 4 s before the next ``user_message``. Pairs live only inside
``condition_start`` → ``condition_conclusion_submitted``. Overlapping or
incomplete pairs are dropped. ``turn_N_read`` / ``turn_N_write`` are not
used; those markers share the submit timestamp in the deployed lab app.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from build_ad_visibility import (
    condition_blocks,
    load_log,
    read_csv,
    unix_time,
    write_csv,
    xdf_projection,
)
from build_ad_windows import condition_lookup


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_MANIFEST = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
DEFAULT_CONDITIONS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/task_state_windows.csv"
)
WINDOW_SECONDS = 4.0


def pair_bounds(
    reply_eeg_s: float,
    user_eeg_s: float,
    *,
    window_seconds: float = WINDOW_SECONDS,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    read_start = reply_eeg_s
    read_end = reply_eeg_s + window_seconds
    write_start = user_eeg_s - window_seconds
    write_end = user_eeg_s
    if write_start < read_end:
        return None
    return (read_start, read_end), (write_start, write_end)


def inside_condition(
    start_s: float,
    end_s: float,
    condition_window: dict[str, str],
) -> bool:
    return (
        start_s >= float(condition_window["start_eeg_offset_s"])
        and end_s <= float(condition_window["end_eeg_offset_s"])
    )


def block_pairs(
    block: list[dict[str, Any]],
    *,
    subject_id: str,
    experiment_id: str,
    condition_window: dict[str, str],
    markers: list[dict[str, str]],
    source_log: str,
    source_canonical_markers: str,
    window_seconds: float = WINDOW_SECONDS,
) -> list[dict[str, Any]]:
    start = next((event for event in block if event["event"] == "condition_start"), None)
    end = next(
        (
            event
            for event in block
            if event["event"] == "condition_conclusion_submitted"
        ),
        None,
    )
    if start is None or end is None:
        return []
    start_unix = unix_time(start)
    end_unix = unix_time(end)
    replies = [
        event
        for event in block
        if event["event"] == "assistant_reply"
        and start_unix <= unix_time(event) < end_unix
    ]
    users = [
        event
        for event in block
        if event["event"] == "user_message"
        and start_unix < unix_time(event) <= end_unix
    ]
    rows: list[dict[str, Any]] = []
    condition = condition_window["condition"]
    ad_mode = condition_window.get("ad_mode", "")
    for reply_index, reply in enumerate(replies, start=1):
        reply_unix = unix_time(reply)
        user = next(
            (event for event in users if unix_time(event) > reply_unix),
            None,
        )
        if user is None:
            continue
        user_unix = unix_time(user)
        _, reply_eeg, reply_uncertainty = xdf_projection(markers, reply_unix)
        _, user_eeg, user_uncertainty = xdf_projection(markers, user_unix)
        bounds = pair_bounds(
            reply_eeg,
            user_eeg,
            window_seconds=window_seconds,
        )
        pair_id = f"{subject_id}__{condition}__turn_{reply_index:02d}"
        if bounds is None:
            continue
        (read_start, read_end), (write_start, write_end) = bounds
        for state, start_s, end_s, onset, uncertainty in (
            ("reading", read_start, read_end, reply_eeg, reply_uncertainty),
            ("writing", write_start, write_end, user_eeg, user_uncertainty),
        ):
            eligible = inside_condition(start_s, end_s, condition_window)
            rows.append(
                {
                    "subject_id": subject_id,
                    "experiment_id": experiment_id,
                    "window_id": f"{pair_id}__{state}",
                    "pair_id": pair_id,
                    "state": state,
                    "condition": condition,
                    "ad_mode": ad_mode,
                    "turn_index": reply_index,
                    "reference_onset_eeg_offset_s": f"{onset:.6f}",
                    "start_eeg_offset_s": f"{start_s:.6f}",
                    "end_eeg_offset_s": f"{end_s:.6f}",
                    "duration_s": f"{end_s - start_s:.6f}",
                    "gap_s": f"{user_eeg - reply_eeg:.6f}",
                    "inside_condition": "yes" if eligible else "no",
                    "primary_analysis_eligible": "yes" if eligible else "no",
                    "exclusion_reason": "" if eligible else "outside_condition",
                    "combined_timing_uncertainty_s": f"{uncertainty:.6f}",
                    "source_log": source_log,
                    "source_canonical_markers": source_canonical_markers,
                    "source_xdf": condition_window["source_xdf"],
                    "source_xdf_sha256": condition_window["source_xdf_sha256"],
                }
            )
    return rows


def run(
    manifest_path: Path,
    conditions_path: Path,
    output_path: Path,
    *,
    window_seconds: float = WINDOW_SECONDS,
) -> list[dict[str, Any]]:
    manifest = read_csv(manifest_path)
    conditions = condition_lookup(read_csv(conditions_path))
    rows: list[dict[str, Any]] = []
    for source in manifest:
        if source["study_protocol_eligible"] != "yes":
            continue
        markers = read_csv(Path(source["canonical_table"]))
        blocks = condition_blocks(load_log(Path(source["source_log"])))
        for block in blocks:
            start = next(
                (event for event in block if event["event"] == "condition_start"),
                None,
            )
            if start is None:
                continue
            condition = start.get("data", {}).get("condition")
            key = (source["subject_id"], condition)
            if key not in conditions:
                continue
            rows.extend(
                block_pairs(
                    block,
                    subject_id=source["subject_id"],
                    experiment_id=source["experiment_id"],
                    condition_window=conditions[key],
                    markers=markers,
                    source_log=source["source_log"],
                    source_canonical_markers=source["canonical_table"],
                    window_seconds=window_seconds,
                )
            )
    write_csv(output_path, rows)
    eligible = sum(row["primary_analysis_eligible"] == "yes" for row in rows)
    pairs = {row["pair_id"] for row in rows}
    print(f"Wrote {len(rows)} task-state windows ({len(pairs)} pairs) to {output_path}")
    print(f"Eligible windows: {eligible}")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--conditions", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--window-seconds", type=float, default=WINDOW_SECONDS)
    args = parser.parse_args()
    run(
        args.manifest,
        args.conditions,
        args.output,
        window_seconds=args.window_seconds,
    )


if __name__ == "__main__":
    main()
