"""Validate reconstruction by hiding observed markers and predicting their times."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

from marker_pipeline import (
    LogEvent,
    best_session_alignment,
    discover_logs,
    discover_xdfs,
    fit_alignment,
    load_xdf_markers,
    write_csv,
)


DEFAULT_BRONZE = Path("src/project/logs/xdf/bronze")
DEFAULT_LOGS = Path("src/project/logs/production")
DEFAULT_OUTPUT = Path("src/project/logs/xdf/silver/validation")


def metric_row(subject_id: str, errors: list[float]) -> dict[str, object]:
    absolute = np.abs(np.asarray(errors, dtype=float))
    return {
        "subject_id": subject_id,
        "held_out_count": len(errors),
        "median_abs_error_s": f"{np.median(absolute):.6f}",
        "p95_abs_error_s": f"{np.percentile(absolute, 95):.6f}",
        "max_abs_error_s": f"{np.max(absolute):.6f}",
        "rmse_s": f"{np.sqrt(np.mean(np.square(errors))):.6f}",
        "within_0_050_s_fraction": f"{np.mean(absolute <= 0.050):.4f}",
        "within_0_100_s_fraction": f"{np.mean(absolute <= 0.100):.4f}",
        "within_0_250_s_fraction": f"{np.mean(absolute <= 0.250):.4f}",
    }


def run(
    bronze_root: Path,
    log_root: Path,
    output_root: Path,
    *,
    minimum_training_anchors: int,
) -> None:
    logs = discover_logs(log_root)
    xdfs = discover_xdfs(bronze_root)
    event_rows: list[dict[str, object]] = []
    subject_rows: list[dict[str, object]] = []
    all_errors: list[float] = []

    for number in sorted(xdfs):
        xdf = load_xdf_markers(xdfs[number])
        session, alignment = best_session_alignment(xdf, logs.values())
        if alignment.fit is None:
            print(f"{session.subject_id}: skipped, no valid alignment")
            continue

        event_by_index: dict[int, LogEvent] = {
            event.index: event for event in session.events
        }
        subject_errors: list[float] = []
        for held_out_index, held_out_marker in alignment.matches.items():
            if held_out_index not in event_by_index:
                continue
            event = event_by_index[held_out_index]
            hidden_ids = {
                marker.marker_id
                for marker in xdf.markers
                if marker.label == event.label
                and abs(
                    marker.timestamp_lsl - held_out_marker.timestamp_lsl
                )
                <= 0.25
            }
            reduced_markers = [
                marker
                for marker in xdf.markers
                if marker.marker_id not in hidden_ids
            ]
            held_out_alignment = fit_alignment(
                session.events,
                reduced_markers,
            )
            fit = held_out_alignment.fit
            if fit is None or fit.anchor_count < minimum_training_anchors:
                continue
            predicted = fit.predict(event.timestamp_unix)
            error = predicted - held_out_marker.timestamp_lsl
            subject_errors.append(error)
            all_errors.append(error)
            event_rows.append(
                {
                    "subject_id": session.subject_id,
                    "experiment_id": session.experiment_id,
                    "event_index": held_out_index,
                    "event": event.label,
                    "trial_index": (
                        event.trial_index if event.trial_index is not None else ""
                    ),
                    "turn": event.turn if event.turn is not None else "",
                    "observed_xdf_timestamp_lsl": (
                        f"{held_out_marker.timestamp_lsl:.6f}"
                    ),
                    "predicted_xdf_timestamp_lsl": f"{predicted:.6f}",
                    "signed_error_s": f"{error:.6f}",
                    "absolute_error_s": f"{abs(error):.6f}",
                    "training_anchor_count": fit.anchor_count,
                    "hidden_raw_marker_count": len(hidden_ids),
                    "held_out_event_rematched": (
                        "yes"
                        if held_out_index in held_out_alignment.matches
                        else "no"
                    ),
                }
            )

        if subject_errors:
            subject_rows.append(metric_row(session.subject_id, subject_errors))
            print(
                f"{session.subject_id}: {len(subject_errors)} held out, "
                f"p95={np.percentile(np.abs(subject_errors), 95):.6f}s"
            )

    if all_errors:
        subject_rows.append(metric_row("ALL_SUBJECTS", all_errors))
    write_csv(output_root / "leave_one_marker_out_events.csv", event_rows)
    write_csv(output_root / "reconstruction_validation_summary.csv", subject_rows)

    global_p95 = (
        float(np.percentile(np.abs(all_errors), 95))
        if all_errors
        else math.nan
    )
    print(
        f"Wrote reconstruction validation to {output_root}; "
        f"global p95={global_p95:.6f}s"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bronze-root", type=Path, default=DEFAULT_BRONZE)
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOGS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--minimum-training-anchors", type=int, default=10)
    args = parser.parse_args()
    run(
        args.bronze_root,
        args.log_root,
        args.output_root,
        minimum_training_anchors=args.minimum_training_anchors,
    )


if __name__ == "__main__":
    main()
