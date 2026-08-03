"""Build and validate advertisement visual-onset estimates.

Observed ``ad_displayed`` events are preferred. Missing block onsets are
estimated from reply completion; missing inline onsets are estimated from ad
injection. Each estimator is calibrated only on protocol-eligible recordings
that contain the corresponding legacy/modern display event.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np


DEFAULT_MANIFEST = Path(
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
DEFAULT_EVENTS = Path(
    "src/project/logs/xdf/gold/windows/ad_visibility_events.csv"
)
DEFAULT_CALIBRATION = Path(
    "src/project/logs/xdf/gold/windows/ad_visibility_calibration.csv"
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


def unix_time(event: dict[str, Any]) -> float:
    return datetime.fromisoformat(event["timestamp"]).timestamp()


def load_log(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def condition_blocks(
    events: list[dict[str, Any]],
) -> list[list[dict[str, Any]]]:
    starts = [
        index
        for index, event in enumerate(events)
        if event["event"] == "condition_start"
    ]
    return [
        events[
            start : starts[index + 1]
            if index + 1 < len(starts)
            else len(events)
        ]
        for index, start in enumerate(starts)
    ]


def nearest_reply(
    block: list[dict[str, Any]],
    injection_time: float,
) -> dict[str, Any] | None:
    candidates = [
        event
        for event in block
        if event["event"] == "assistant_reply"
        and unix_time(event) >= injection_time
    ]
    return min(candidates, key=unix_time) if candidates else None


def first_display(
    block: list[dict[str, Any]],
    injection_time: float,
) -> dict[str, Any] | None:
    candidates = [
        event
        for event in block
        if event["event"] == "ad_displayed"
        and unix_time(event) >= injection_time
    ]
    return min(candidates, key=unix_time) if candidates else None


def collect_cases(
    manifest: list[dict[str, str]],
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for source in manifest:
        for condition_index, block in enumerate(
            condition_blocks(load_log(Path(source["source_log"])))
        ):
            condition_start = block[0]
            condition = condition_start.get("data", {}).get("condition", "")
            injection = next(
                (
                    event
                    for event in block
                    if event["event"] == "ad_injected"
                ),
                None,
            )
            if injection is None:
                continue
            injection_time = unix_time(injection)
            reply = nearest_reply(block, injection_time)
            display = first_display(block, injection_time)
            conclusion = next(
                (
                    event
                    for event in block
                    if event["event"] == "condition_conclusion_submitted"
                ),
                None,
            )
            cases.append(
                {
                    "source": source,
                    "condition_index": condition_index,
                    "condition": condition,
                    "ad_mode": injection.get("ad_mode", ""),
                    "ad_turn": injection.get("turn", ""),
                    "injection": injection,
                    "injection_time": injection_time,
                    "reply": reply,
                    "reply_time": unix_time(reply) if reply else None,
                    "display": display,
                    "display_time": unix_time(display) if display else None,
                    "conclusion_time": (
                        unix_time(conclusion) if conclusion else None
                    ),
                }
            )
    return cases


def leave_one_out_errors(values: list[float]) -> list[float]:
    return [
        abs(value - median(values[:index] + values[index + 1 :]))
        for index, value in enumerate(values)
        if len(values) > 1
    ]


def calibration(
    cases: list[dict[str, Any]],
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    block_lags = [
        case["display_time"] - case["reply_time"]
        for case in cases
        if case["source"]["study_protocol_eligible"] == "yes"
        and case["ad_mode"] == "explicit_ad_block"
        and case["display_time"] is not None
        and case["reply_time"] is not None
        and 0.0 <= case["display_time"] - case["reply_time"] <= 2.0
    ]
    inline_lags = [
        case["display_time"] - case["injection_time"]
        for case in cases
        if case["source"]["study_protocol_eligible"] == "yes"
        and case["ad_mode"] == "inline_persuasive"
        and case["display_time"] is not None
        and case["reply_time"] is not None
        and case["display_time"] < case["reply_time"]
        and 0.0 <= case["display_time"] - case["injection_time"] <= 3.0
    ]
    if not block_lags or not inline_lags:
        raise ValueError("Insufficient observations to calibrate ad visibility")
    values = {
        "block_reply_lag_s": median(block_lags),
        "inline_injection_lag_s": median(inline_lags),
    }
    rows: list[dict[str, Any]] = []
    for name, lags, origin in (
        (
            "block_reply_plus_median_lag",
            block_lags,
            "assistant_reply",
        ),
        (
            "inline_injection_plus_median_lag",
            inline_lags,
            "ad_injected",
        ),
    ):
        errors = leave_one_out_errors(lags)
        rows.append(
            {
                "estimator": name,
                "origin_event": origin,
                "calibration_observation_count": len(lags),
                "median_lag_s": f"{median(lags):.6f}",
                "observed_min_lag_s": f"{min(lags):.6f}",
                "observed_max_lag_s": f"{max(lags):.6f}",
                "loo_median_abs_error_s": f"{median(errors):.6f}",
                "loo_p95_abs_error_s": (
                    f"{np.percentile(errors, 95):.6f}"
                ),
                "loo_max_abs_error_s": f"{max(errors):.6f}",
            }
        )
        values[f"{name}_p95_error_s"] = float(
            np.percentile(errors, 95)
        )
    return values, rows


def xdf_projection(
    markers: list[dict[str, str]],
    log_time: float,
) -> tuple[float, float, float]:
    anchor = next(
        row
        for row in markers
        if row.get("log_timestamp_unix")
        and row.get("xdf_timestamp_lsl")
        and row.get("eeg_offset_s")
    )
    slope = float(anchor["fit_slope"])
    xdf_time = float(anchor["xdf_timestamp_lsl"]) + slope * (
        log_time - float(anchor["log_timestamp_unix"])
    )
    eeg_offset = float(anchor["eeg_offset_s"]) + slope * (
        log_time - float(anchor["log_timestamp_unix"])
    )
    alignment_uncertainty = float(anchor["fit_p95_abs_residual_s"])
    return xdf_time, eeg_offset, alignment_uncertainty


def build_rows(
    cases: list[dict[str, Any]],
    calibration_values: dict[str, float],
) -> list[dict[str, Any]]:
    marker_cache: dict[str, list[dict[str, str]]] = {}
    rows: list[dict[str, Any]] = []
    for case in cases:
        source = case["source"]
        marker_path = source["canonical_table"]
        markers = marker_cache.setdefault(
            marker_path,
            read_csv(Path(marker_path)),
        )
        observed = case["display_time"] is not None
        if observed:
            onset = float(case["display_time"])
            estimator = "observed_ad_displayed"
            calibration_error: float | None = None
            calibration_uncertainty = 0.0
            if (
                case["ad_mode"] == "explicit_ad_block"
                and case["reply_time"] is not None
                and 0.0
                <= case["display_time"] - case["reply_time"]
                <= 2.0
            ):
                predicted = (
                    case["reply_time"]
                    + calibration_values["block_reply_lag_s"]
                )
                calibration_error = predicted - onset
            elif (
                case["ad_mode"] == "inline_persuasive"
                and case["reply_time"] is not None
                and case["display_time"] < case["reply_time"]
            ):
                predicted = (
                    case["injection_time"]
                    + calibration_values["inline_injection_lag_s"]
                )
                calibration_error = predicted - onset
        elif case["ad_mode"] == "explicit_ad_block":
            if case["reply_time"] is None:
                continue
            onset = (
                case["reply_time"]
                + calibration_values["block_reply_lag_s"]
            )
            estimator = "block_reply_plus_median_lag"
            calibration_error = None
            calibration_uncertainty = calibration_values[
                "block_reply_plus_median_lag_p95_error_s"
            ]
        else:
            onset = (
                case["injection_time"]
                + calibration_values["inline_injection_lag_s"]
            )
            estimator = "inline_injection_plus_median_lag"
            calibration_error = None
            calibration_uncertainty = calibration_values[
                "inline_injection_plus_median_lag_p95_error_s"
            ]
        xdf_time, eeg_offset, alignment_uncertainty = xdf_projection(
            markers,
            onset,
        )
        inside_condition = (
            case["conclusion_time"] is None
            or onset < case["conclusion_time"]
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
                "visibility_status": (
                    "observed" if observed else "derived_validated"
                ),
                "estimator": estimator,
                "injection_log_unix": f"{case['injection_time']:.6f}",
                "reply_log_unix": (
                    f"{case['reply_time']:.6f}"
                    if case["reply_time"] is not None
                    else ""
                ),
                "observed_display_log_unix": (
                    f"{case['display_time']:.6f}" if observed else ""
                ),
                "visual_onset_log_unix": f"{onset:.6f}",
                "visual_onset_xdf_timestamp_lsl": f"{xdf_time:.6f}",
                "visual_onset_eeg_offset_s": f"{eeg_offset:.6f}",
                "alignment_uncertainty_s": (
                    f"{alignment_uncertainty:.6f}"
                ),
                "calibration_p95_uncertainty_s": (
                    f"{calibration_uncertainty:.6f}"
                ),
                "combined_timing_uncertainty_s": (
                    f"{alignment_uncertainty + calibration_uncertainty:.6f}"
                ),
                "calibration_prediction_error_s": (
                    f"{calibration_error:.6f}"
                    if calibration_error is not None
                    else ""
                ),
                "inside_condition": "yes" if inside_condition else "no",
                "study_protocol_eligible": (
                    source["study_protocol_eligible"]
                ),
                "primary_analysis_eligible": "yes" if eligible else "no",
                "source_log": source["source_log"],
                "source_xdf": source["source_xdf"],
                "source_xdf_sha256": source["source_xdf_sha256"],
            }
        )
    return rows


def run(
    manifest_path: Path,
    events_path: Path,
    calibration_path: Path,
) -> None:
    manifest = read_csv(manifest_path)
    cases = collect_cases(manifest)
    values, calibration_rows = calibration(cases)
    rows = build_rows(cases, values)
    write_csv(events_path, rows)
    write_csv(calibration_path, calibration_rows)
    print(f"Wrote {len(rows)} ad visibility events")
    for row in calibration_rows:
        print(
            f"{row['estimator']}: n="
            f"{row['calibration_observation_count']}, "
            f"p95 LOO error={row['loo_p95_abs_error_s']} s"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--events-output", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument(
        "--calibration-output",
        type=Path,
        default=DEFAULT_CALIBRATION,
    )
    args = parser.parse_args()
    run(args.manifest, args.events_output, args.calibration_output)


if __name__ == "__main__":
    main()
