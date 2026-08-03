"""Explain duplicate and extra marker patterns without modifying raw XDF files."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from marker_pipeline import (
    RawMarker,
    best_session_alignment,
    canonical_rows,
    discover_logs,
    discover_xdfs,
    load_xdf_markers,
    write_csv,
)


DEFAULT_BRONZE = Path("src/project/logs/xdf/bronze")
DEFAULT_LOGS = Path("src/project/logs/production")
DEFAULT_OUTPUT = Path("src/project/logs/xdf/silver/audits")


def duplicate_groups(
    markers: tuple[RawMarker, ...],
    tolerance_s: float,
) -> list[list[RawMarker]]:
    by_label: dict[str, list[RawMarker]] = defaultdict(list)
    for marker in markers:
        by_label[marker.label].append(marker)

    groups: list[list[RawMarker]] = []
    for same_label in by_label.values():
        ordered = sorted(same_label, key=lambda marker: marker.timestamp_lsl)
        current: list[RawMarker] = []
        for marker in ordered:
            if (
                current
                and marker.timestamp_lsl - current[-1].timestamp_lsl > tolerance_s
            ):
                if len(current) > 1:
                    groups.append(current)
                current = []
            current.append(marker)
        if len(current) > 1:
            groups.append(current)
    return groups


def classify_cause(
    *,
    expected: int,
    raw: int,
    cross_stream_duplicates: int,
    within_stream_duplicates: int,
    far_repeated_labels: int,
    unexpected_labels: int,
) -> str:
    causes: list[str] = []
    if cross_stream_duplicates:
        causes.append("overlapping_marker_streams")
    if within_stream_duplicates:
        causes.append("repeated_within_stream_emissions")
    if far_repeated_labels:
        causes.append("time_separated_repeated_emissions")
    if unexpected_labels:
        causes.append("unexpected_marker_labels")
    if raw > expected and not causes:
        causes.append("unmatched_extra_markers")
    return "+".join(causes) if causes else "none_detected"


def run(
    bronze_root: Path,
    log_root: Path,
    output_root: Path,
    *,
    near_duplicate_tolerance_s: float,
) -> None:
    logs = discover_logs(log_root)
    xdfs = discover_xdfs(bronze_root)
    subject_rows: list[dict[str, object]] = []
    stream_rows: list[dict[str, object]] = []
    group_rows: list[dict[str, object]] = []
    extra_rows: list[dict[str, object]] = []

    for number in sorted(xdfs):
        xdf = load_xdf_markers(xdfs[number])
        session, alignment = best_session_alignment(xdf, logs.values())
        canonical = canonical_rows(session, xdf, alignment)
        groups = duplicate_groups(xdf.markers, near_duplicate_tolerance_s)

        cross_stream_duplicates = 0
        within_stream_duplicates = 0
        for group_index, group in enumerate(groups):
            stream_counts = Counter(marker.stream_index for marker in group)
            unique_streams = len(stream_counts)
            duplicate_count = len(group) - 1
            if unique_streams > 1:
                cross_stream_duplicates += duplicate_count
            if any(count > 1 for count in stream_counts.values()):
                within_stream_duplicates += sum(
                    max(0, count - 1) for count in stream_counts.values()
                )
            group_rows.append(
                {
                    "subject_id": session.subject_id,
                    "group_index": group_index,
                    "event": group[0].label,
                    "first_timestamp_lsl": f"{group[0].timestamp_lsl:.6f}",
                    "last_timestamp_lsl": f"{group[-1].timestamp_lsl:.6f}",
                    "span_s": f"{group[-1].timestamp_lsl - group[0].timestamp_lsl:.6f}",
                    "raw_count": len(group),
                    "unique_stream_count": unique_streams,
                    "stream_indices": ";".join(
                        str(item) for item in sorted(stream_counts)
                    ),
                    "classification": (
                        "cross_stream"
                        if unique_streams > 1
                        else "within_stream"
                    ),
                }
            )

        selected_ids = {
            marker.marker_id for marker in alignment.matches.values()
        }
        selected_by_label: dict[str, list[RawMarker]] = defaultdict(list)
        for marker in alignment.matches.values():
            selected_by_label[marker.label].append(marker)
        far_repeated_labels = 0
        unexpected_labels = 0
        for marker in xdf.markers:
            if marker.marker_id in selected_ids:
                continue
            candidates = selected_by_label.get(marker.label, [])
            nearest = (
                min(
                    candidates,
                    key=lambda item: abs(
                        item.timestamp_lsl - marker.timestamp_lsl
                    ),
                )
                if candidates
                else None
            )
            delta = (
                marker.timestamp_lsl - nearest.timestamp_lsl
                if nearest is not None
                else None
            )
            if nearest is None:
                classification = "unexpected_label"
                unexpected_labels += 1
            elif abs(delta or 0.0) <= near_duplicate_tolerance_s:
                classification = (
                    "near_duplicate_cross_stream"
                    if marker.stream_index != nearest.stream_index
                    else "near_duplicate_within_stream"
                )
            else:
                classification = "time_separated_repeated_emission"
                far_repeated_labels += 1
            extra_rows.append(
                {
                    "subject_id": session.subject_id,
                    "event": marker.label,
                    "timestamp_lsl": f"{marker.timestamp_lsl:.6f}",
                    "stream_index": marker.stream_index,
                    "stream_name": marker.stream_name,
                    "nearest_selected_timestamp_lsl": (
                        f"{nearest.timestamp_lsl:.6f}"
                        if nearest is not None
                        else ""
                    ),
                    "nearest_selected_delta_s": (
                        f"{delta:.6f}" if delta is not None else ""
                    ),
                    "classification": classification,
                }
            )
        stream_markers: dict[int, list[RawMarker]] = defaultdict(list)
        for marker in xdf.markers:
            stream_markers[marker.stream_index].append(marker)
        for stream_index, markers in sorted(stream_markers.items()):
            stream_rows.append(
                {
                    "subject_id": session.subject_id,
                    "stream_index": stream_index,
                    "stream_name": markers[0].stream_name,
                    "stream_source_id": markers[0].stream_source_id,
                    "marker_count": len(markers),
                    "unique_labels": len({marker.label for marker in markers}),
                    "first_timestamp_lsl": f"{markers[0].timestamp_lsl:.6f}",
                    "last_timestamp_lsl": f"{markers[-1].timestamp_lsl:.6f}",
                    "selected_canonical_count": sum(
                        marker.marker_id in selected_ids for marker in markers
                    ),
                }
            )

        expected = len(session.events)
        observed = sum(row["provenance"] == "observed" for row in canonical)
        derived = sum(row["provenance"] == "derived" for row in canonical)
        duplicate_candidates = sum(
            int(row["duplicate_raw_count"]) for row in canonical
        )
        subject_rows.append(
            {
                "subject_id": session.subject_id,
                "experiment_id": session.experiment_id,
                "xdf_folder_subject_number": number,
                "mapping_matches_folder_number": (
                    "yes" if session.subject_number == number else "no"
                ),
                "source_xdf": str(xdf.path),
                "marker_stream_count": xdf.marker_stream_count,
                "raw_marker_count": len(xdf.markers),
                "expected_event_count": expected,
                "observed_event_count": observed,
                "derived_event_count": derived,
                "selected_marker_count": len(selected_ids),
                "unselected_raw_marker_count": len(xdf.markers) - len(selected_ids),
                "canonical_duplicate_candidate_count": duplicate_candidates,
                "near_duplicate_group_count": len(groups),
                "cross_stream_duplicate_count": cross_stream_duplicates,
                "within_stream_duplicate_count": within_stream_duplicates,
                "time_separated_repeated_emission_count": far_repeated_labels,
                "unexpected_label_count": unexpected_labels,
                "likely_cause": classify_cause(
                    expected=expected,
                    raw=len(xdf.markers),
                    cross_stream_duplicates=cross_stream_duplicates,
                    within_stream_duplicates=within_stream_duplicates,
                    far_repeated_labels=far_repeated_labels,
                    unexpected_labels=unexpected_labels,
                ),
                "anchor_count": (
                    alignment.fit.anchor_count if alignment.fit is not None else 0
                ),
                "fit_p95_abs_residual_s": (
                    f"{alignment.fit.p95_abs_residual_s:.6f}"
                    if alignment.fit is not None
                    else ""
                ),
            }
        )
        print(
            f"{session.subject_id}: {len(xdf.markers)} raw, {expected} expected, "
            f"{observed} observed, {derived} derived"
        )

    write_csv(output_root / "marker_anomaly_report.csv", subject_rows)
    write_csv(output_root / "marker_stream_inventory.csv", stream_rows)
    write_csv(output_root / "near_duplicate_groups.csv", group_rows)
    write_csv(output_root / "extra_marker_details.csv", extra_rows)
    print(f"Wrote anomaly reports to {output_root}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bronze-root", type=Path, default=DEFAULT_BRONZE)
    parser.add_argument("--log-root", type=Path, default=DEFAULT_LOGS)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--near-duplicate-tolerance-s",
        type=float,
        default=0.01,
    )
    args = parser.parse_args()
    run(
        args.bronze_root,
        args.log_root,
        args.output_root,
        near_duplicate_tolerance_s=args.near_duplicate_tolerance_s,
    )


if __name__ == "__main__":
    main()
