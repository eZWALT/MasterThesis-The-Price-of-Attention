"""Fail-fast verification of EEG recording and marker recovery invariants."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np


DEFAULT_XDF_ROOT = Path("src/project/logs/xdf")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(xdf_root: Path, *, expected_lab_count: int, maximum_p95_s: float) -> None:
    canonical = read_csv(
        xdf_root / "silver" / "canonical_marker_manifest.csv"
    )
    laboratory = [
        row for row in canonical if row["study_protocol_eligible"] == "yes"
    ]
    laboratory_ids = {row["subject_id"] for row in laboratory}
    require(
        len(laboratory) == expected_lab_count,
        f"Expected {expected_lab_count} laboratory recordings, "
        f"found {len(laboratory)}",
    )
    require(
        all(row["mapping_matches_folder_number"] == "yes" for row in laboratory),
        "At least one XDF independently maps to another participant log",
    )
    require(
        all(row["fit_valid"] == "yes" for row in laboratory),
        "At least one laboratory clock alignment is invalid",
    )
    expected_events = sum(
        int(row["expected_event_count"]) for row in laboratory
    )
    observed_events = sum(
        int(row["observed_event_count"]) for row in laboratory
    )
    derived_events = sum(
        int(row["derived_event_count"]) for row in laboratory
    )
    unavailable_events = sum(
        int(row["unavailable_event_count"]) for row in laboratory
    )
    require(
        observed_events + derived_events == expected_events,
        "Observed and governed derived events do not cover expected events",
    )
    require(
        unavailable_events == 0,
        f"{unavailable_events} laboratory events are unavailable",
    )

    holdouts = [
        row
        for row in read_csv(
            xdf_root
            / "silver"
            / "validation"
            / "leave_one_marker_out_events.csv"
        )
        if row["subject_id"] in laboratory_ids
    ]
    require(
        len(holdouts) == observed_events,
        f"Expected {observed_events} holdouts, found {len(holdouts)}",
    )
    require(
        not any(row["held_out_event_rematched"] == "yes" for row in holdouts),
        "A hidden event rematched to another raw marker",
    )
    absolute_errors = np.asarray(
        [abs(float(row["signed_error_s"])) for row in holdouts],
        dtype=float,
    )
    p95_error = float(np.percentile(absolute_errors, 95))
    require(
        p95_error <= maximum_p95_s,
        f"Holdout p95 {p95_error:.6f}s exceeds {maximum_p95_s:.6f}s",
    )

    acquisition = [
        row
        for row in read_csv(
            xdf_root / "silver" / "audits" / "xdf_mne_acquisition_audit.csv"
        )
        if row["study_protocol_eligible"] == "yes"
    ]
    require(
        len(acquisition) == expected_lab_count,
        "Acquisition audit does not cover every laboratory recording",
    )
    require(
        all(row["conversion_status"] == "passed" for row in acquisition),
        "At least one XDF-to-MNE conversion failed",
    )
    maximum_annotation_error = max(
        float(row["annotation_max_nearest_sample_error_s"])
        for row in acquisition
    )

    windows = [
        row
        for row in read_csv(
            xdf_root / "gold" / "windows" / "condition_window_summary.csv"
        )
        if row["study_protocol_eligible"] == "yes"
    ]
    require(
        len(windows) == expected_lab_count,
        "Condition-window summary does not cover every laboratory recording",
    )
    require(
        all(
            row["baseline_window_present"] == "yes"
            and row["five_conditions_present"] == "yes"
            and int(row["eligible_condition_window_count"]) == 5
            for row in windows
        ),
        "At least one laboratory recording lacks an eligible baseline or "
        "five-condition window set",
    )
    eligible_condition_windows = sum(
        int(row["eligible_condition_window_count"]) for row in windows
    )

    ad_events = [
        row
        for row in read_csv(
            xdf_root / "gold" / "windows" / "ad_visibility_events.csv"
        )
        if row["study_protocol_eligible"] == "yes"
        and row["primary_analysis_eligible"] == "yes"
    ]
    require(
        len(ad_events) == expected_lab_count * 4,
        f"Expected {expected_lab_count * 4} eligible ad events, "
        f"found {len(ad_events)}",
    )

    duplicate_holdouts = sum(
        int(row["hidden_raw_marker_count"]) > 1 for row in holdouts
    )
    print(f"laboratory_recordings={len(laboratory)}")
    print(f"expected_events={expected_events}")
    print(f"observed_events={observed_events}")
    print(f"governed_derived_events={derived_events}")
    print(f"unavailable_events={unavailable_events}")
    print(f"holdout_predictions={len(holdouts)}")
    print(f"holdouts_with_duplicates_removed={duplicate_holdouts}")
    print("held_out_events_rematched=0")
    print(f"holdout_p95_error_s={p95_error:.6f}")
    print(f"holdout_max_error_s={float(np.max(absolute_errors)):.6f}")
    print(f"mne_conversions_passed={len(acquisition)}")
    print(f"maximum_annotation_sample_error_s={maximum_annotation_error:.9f}")
    print(f"eligible_condition_windows={eligible_condition_windows}")
    print(f"eligible_ad_events={len(ad_events)}")
    print("RECOVERY_INVARIANTS_PASSED")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xdf-root", type=Path, default=DEFAULT_XDF_ROOT)
    parser.add_argument("--expected-lab-count", type=int, default=18)
    parser.add_argument("--maximum-p95-s", type=float, default=0.050)
    args = parser.parse_args()
    run(
        args.xdf_root,
        expected_lab_count=args.expected_lab_count,
        maximum_p95_s=args.maximum_p95_s,
    )


if __name__ == "__main__":
    main()
