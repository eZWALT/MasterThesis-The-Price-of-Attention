"""Build baseline and sustained condition windows from Silver markers.

Ad-centred windows are intentionally excluded. They require the separate visual
onset validation contract.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path(
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
DEFAULT_WINDOWS = Path(
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
DEFAULT_SUMMARY = Path(
    "src/project/logs/xdf/gold/windows/condition_window_summary.csv"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def timestamp(row: dict[str, str]) -> float:
    return float(row["xdf_timestamp_lsl"])


def timing_eligible(row: dict[str, str]) -> bool:
    return (
        row.get("event_timing_eligible") == "yes"
        and row.get("inside_eeg_span") == "yes"
        and bool(row.get("xdf_timestamp_lsl"))
    )


def window_row(
    *,
    source: dict[str, str],
    window_index: int,
    window_type: str,
    start: dict[str, str],
    end: dict[str, str],
    condition: str,
    ad_mode: str,
    trial_index: str,
) -> dict[str, Any]:
    start_time = timestamp(start)
    end_time = timestamp(end)
    valid_order = end_time > start_time
    event_timing_valid = timing_eligible(start) and timing_eligible(end)
    protocol_valid = source["study_protocol_eligible"] == "yes"
    eligible = valid_order and event_timing_valid and protocol_valid
    return {
        "subject_id": source["subject_id"],
        "experiment_id": source["experiment_id"],
        "window_id": (
            f"{source['subject_id']}__{window_type}_{window_index:02d}"
        ),
        "window_type": window_type,
        "trial_index": trial_index,
        "condition": condition,
        "ad_mode": ad_mode,
        "start_event": start["event"],
        "end_event": end["event"],
        "start_event_index": start["event_index"],
        "end_event_index": end["event_index"],
        "start_xdf_timestamp_lsl": f"{start_time:.6f}",
        "end_xdf_timestamp_lsl": f"{end_time:.6f}",
        "start_eeg_offset_s": start.get("eeg_offset_s", ""),
        "end_eeg_offset_s": end.get("eeg_offset_s", ""),
        "duration_s": f"{end_time - start_time:.6f}",
        "start_provenance": start["provenance"],
        "end_provenance": end["provenance"],
        "event_timing_valid": "yes" if event_timing_valid else "no",
        "study_protocol_eligible": "yes" if protocol_valid else "no",
        "primary_analysis_eligible": "yes" if eligible else "no",
        "exclusion_reason": (
            ""
            if eligible
            else "wrong_protocol"
            if not protocol_valid
            else "invalid_event_timing"
            if not event_timing_valid
            else "non_positive_duration"
        ),
        "source_canonical_markers": source["canonical_table"],
        "source_xdf": source["source_xdf"],
        "source_xdf_sha256": source["source_xdf_sha256"],
    }


def build_subject_windows(
    source: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    markers = read_csv(Path(source["canonical_table"]))
    windows: list[dict[str, Any]] = []

    baseline_start = next(
        (row for row in markers if row["event"] == "baseline_start"),
        None,
    )
    baseline_end = next(
        (row for row in markers if row["event"] == "baseline_end"),
        None,
    )
    if baseline_start and baseline_end:
        windows.append(
            window_row(
                source=source,
                window_index=0,
                window_type="baseline",
                start=baseline_start,
                end=baseline_end,
                condition="baseline",
                ad_mode="none",
                trial_index="",
            )
        )

    condition_starts = [
        (index, row)
        for index, row in enumerate(markers)
        if row["event"] == "condition_start"
    ]
    for condition_index, (marker_index, start) in enumerate(condition_starts):
        next_start_index = (
            condition_starts[condition_index + 1][0]
            if condition_index + 1 < len(condition_starts)
            else len(markers)
        )
        end = next(
            (
                row
                for row in markers[marker_index + 1 : next_start_index]
                if row["event"] == "condition_conclusion_submitted"
            ),
            None,
        )
        if end is None:
            continue
        windows.append(
            window_row(
                source=source,
                window_index=condition_index,
                window_type="condition",
                start=start,
                end=end,
                condition=start.get("condition", ""),
                ad_mode=start.get("ad_mode", ""),
                trial_index=start.get("trial_index", ""),
            )
        )

    condition_windows = [
        row for row in windows if row["window_type"] == "condition"
    ]
    eligible_conditions = sum(
        row["primary_analysis_eligible"] == "yes"
        for row in condition_windows
    )
    summary = {
        "subject_id": source["subject_id"],
        "study_type": source["study_type"],
        "study_protocol_eligible": source["study_protocol_eligible"],
        "baseline_window_present": (
            "yes" if any(row["window_type"] == "baseline" for row in windows) else "no"
        ),
        "condition_window_count": len(condition_windows),
        "eligible_condition_window_count": eligible_conditions,
        "expected_condition_window_count": 5,
        "five_conditions_present": (
            "yes" if len(condition_windows) == 5 else "no"
        ),
        "conditions": ";".join(
            row["condition"] for row in condition_windows
        ),
        "automatic_subject_exclusion": (
            "yes" if source["study_protocol_eligible"] != "yes" else "no"
        ),
        "exclusion_reason": (
            "wrong_protocol"
            if source["study_protocol_eligible"] != "yes"
            else ""
        ),
    }
    return windows, summary


def run(
    manifest_path: Path,
    windows_path: Path,
    summary_path: Path,
) -> None:
    manifest = read_csv(manifest_path)
    windows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    for source in manifest:
        subject_windows, summary = build_subject_windows(source)
        windows.extend(subject_windows)
        summaries.append(summary)
        print(
            f"{source['subject_id']}: "
            f"{summary['condition_window_count']} conditions, "
            f"{summary['eligible_condition_window_count']} eligible"
        )
    write_csv(windows_path, windows)
    write_csv(summary_path, summaries)
    print(f"Wrote {len(windows)} windows to {windows_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--windows-output", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    run(args.manifest, args.windows_output, args.summary_output)


if __name__ == "__main__":
    main()
