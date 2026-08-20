"""After-reply Path B onsets. Writes only under sensitivity/after_reply/.

t=0 is assistant_reply plus the frozen explicit banner lag, for every
ad format. This is not the confirmatory visual-onset lock.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_ad_visibility import (  # noqa: E402
    collect_cases,
    read_csv,
    write_csv,
    xdf_projection,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_MANIFEST = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
GOLDEN_CALIBRATION = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/ad_visibility_calibration.csv"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/sensitivity/after_reply/"
    "ad_visibility_events.csv"
)
ESTIMATOR = "assistant_reply_plus_banner_lag"


def assert_parallel(path: Path) -> None:
    text = str(path.resolve())
    if "sensitivity/after_reply" not in text:
        raise RuntimeError(f"refusing to write outside after_reply/: {path}")
    if path.name == "ad_visibility_events.csv" and "sensitivity" not in text:
        raise RuntimeError(f"refusing to overwrite golden visibility: {path}")


def banner_lag_s(calibration_path: Path) -> tuple[float, float]:
    rows = read_csv(calibration_path)
    row = next(
        item
        for item in rows
        if item["estimator"] == "block_reply_plus_median_lag"
    )
    return float(row["median_lag_s"]), float(row["loo_p95_abs_error_s"])


def build_rows(
    cases: list[dict[str, Any]],
    *,
    lag_s: float,
    lag_p95_s: float,
) -> list[dict[str, Any]]:
    marker_cache: dict[str, list[dict[str, str]]] = {}
    rows: list[dict[str, Any]] = []
    for case in cases:
        source = case["source"]
        if case["reply_time"] is None:
            continue
        onset = float(case["reply_time"]) + lag_s
        markers = marker_cache.setdefault(
            source["canonical_table"],
            read_csv(Path(source["canonical_table"])),
        )
        xdf_time, eeg_offset, alignment_uncertainty = xdf_projection(
            markers,
            onset,
        )
        inside_condition = (
            case["conclusion_time"] is None or onset < case["conclusion_time"]
        )
        eligible = (
            source["study_protocol_eligible"] == "yes"
            and inside_condition
            and source["fit_valid"] == "yes"
        )
        rows.append(
            {
                "subject_id": source["subject_id"],
                "experiment_id": source["experiment_id"],
                "condition_index": case["condition_index"],
                "condition": case["condition"],
                "ad_mode": case["ad_mode"],
                "ad_turn": case["ad_turn"],
                "visibility_status": "derived_after_reply",
                "estimator": ESTIMATOR,
                "injection_log_unix": f"{case['injection_time']:.6f}",
                "reply_log_unix": f"{case['reply_time']:.6f}",
                "observed_display_log_unix": (
                    f"{case['display_time']:.6f}"
                    if case["display_time"] is not None
                    else ""
                ),
                "visual_onset_log_unix": f"{onset:.6f}",
                "visual_onset_xdf_timestamp_lsl": f"{xdf_time:.6f}",
                "visual_onset_eeg_offset_s": f"{eeg_offset:.6f}",
                "alignment_uncertainty_s": f"{alignment_uncertainty:.6f}",
                "calibration_p95_uncertainty_s": f"{lag_p95_s:.6f}",
                "combined_timing_uncertainty_s": (
                    f"{alignment_uncertainty + lag_p95_s:.6f}"
                ),
                "calibration_prediction_error_s": "",
                "inside_condition": "yes" if inside_condition else "no",
                "study_protocol_eligible": source["study_protocol_eligible"],
                "primary_analysis_eligible": "yes" if eligible else "no",
                "source_log": source["source_log"],
                "source_xdf": source["source_xdf"],
                "source_xdf_sha256": source["source_xdf_sha256"],
            }
        )
    return rows


def run(manifest_path: Path, output_path: Path, calibration_path: Path) -> None:
    assert_parallel(output_path)
    lag_s, lag_p95_s = banner_lag_s(calibration_path)
    cases = collect_cases(read_csv(manifest_path))
    rows = build_rows(cases, lag_s=lag_s, lag_p95_s=lag_p95_s)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_csv(output_path, rows)
    eligible = sum(row["primary_analysis_eligible"] == "yes" for row in rows)
    shifts = []
    for row in rows:
        if row["primary_analysis_eligible"] != "yes":
            continue
        reply = float(row["reply_log_unix"])
        onset = float(row["visual_onset_log_unix"])
        shifts.append(onset - reply)
    print(f"Wrote {len(rows)} after-reply visibility rows to {output_path}")
    print(f"Eligible ads: {eligible}")
    print(
        f"Lock = assistant_reply + {lag_s:.3f} s "
        f"(p95 lag error {lag_p95_s:.3f} s)"
    )
    print(f"Onset minus reply: mean {float(np.mean(shifts)):.3f} s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--calibration",
        type=Path,
        default=GOLDEN_CALIBRATION,
        help="Read-only golden calibration. Never written.",
    )
    args = parser.parse_args()
    run(args.manifest, args.output, args.calibration)


if __name__ == "__main__":
    main()
