"""Build ad-locked and matched no-ad spectral windows."""

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


DEFAULT_MANIFEST = Path(
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
DEFAULT_VISIBILITY = Path(
    "src/project/logs/xdf/gold/windows/ad_visibility_events.csv"
)
DEFAULT_CONDITIONS = Path(
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
DEFAULT_OUTPUT = Path(
    "src/project/logs/xdf/gold/windows/ad_analysis_windows.csv"
)
WINDOW_SECONDS = 4.0


def condition_lookup(
    rows: list[dict[str, str]],
) -> dict[tuple[str, str], dict[str, str]]:
    return {
        (row["subject_id"], row["condition"]): row
        for row in rows
        if row["window_type"] == "condition"
    }


def window_pair(
    *,
    subject_id: str,
    experiment_id: str,
    reference_id: str,
    reference_kind: str,
    condition: str,
    ad_mode: str,
    matched_timing: str,
    matched_ad_conditions: str,
    onset_eeg_offset_s: float,
    onset_xdf_timestamp_lsl: float,
    onset_log_unix: float,
    onset_estimator: str,
    onset_status: str,
    combined_timing_uncertainty_s: float,
    condition_window: dict[str, str],
    source_log: str,
    source_canonical_markers: str,
) -> list[dict[str, Any]]:
    condition_start = float(condition_window["start_eeg_offset_s"])
    condition_end = float(condition_window["end_eeg_offset_s"])
    rows: list[dict[str, Any]] = []
    for phase, start, end in (
        (
            "pre",
            onset_eeg_offset_s - WINDOW_SECONDS,
            onset_eeg_offset_s,
        ),
        (
            "post",
            onset_eeg_offset_s,
            onset_eeg_offset_s + WINDOW_SECONDS,
        ),
    ):
        inside_condition = start >= condition_start and end <= condition_end
        source_eligible = (
            condition_window["primary_analysis_eligible"] == "yes"
        )
        eligible = inside_condition and source_eligible
        rows.append(
            {
                "subject_id": subject_id,
                "experiment_id": experiment_id,
                "window_id": f"{reference_id}__{phase}",
                "reference_id": reference_id,
                "reference_kind": reference_kind,
                "phase": phase,
                "condition": condition,
                "ad_mode": ad_mode,
                "matched_timing": matched_timing,
                "matched_ad_conditions": matched_ad_conditions,
                "reference_onset_eeg_offset_s": f"{onset_eeg_offset_s:.6f}",
                "reference_onset_xdf_timestamp_lsl": (
                    f"{onset_xdf_timestamp_lsl:.6f}"
                ),
                "reference_onset_log_unix": f"{onset_log_unix:.6f}",
                "onset_estimator": onset_estimator,
                "onset_status": onset_status,
                "combined_timing_uncertainty_s": (
                    f"{combined_timing_uncertainty_s:.6f}"
                ),
                "start_eeg_offset_s": f"{start:.6f}",
                "end_eeg_offset_s": f"{end:.6f}",
                "duration_s": f"{end - start:.6f}",
                "inside_condition": "yes" if inside_condition else "no",
                "primary_analysis_eligible": "yes" if eligible else "no",
                "exclusion_reason": (
                    ""
                    if eligible
                    else "outside_condition"
                    if not inside_condition
                    else "source_condition_ineligible"
                ),
                "source_log": source_log,
                "source_canonical_markers": source_canonical_markers,
                "source_xdf": condition_window["source_xdf"],
                "source_xdf_sha256": condition_window[
                    "source_xdf_sha256"
                ],
            }
        )
    return rows


def ad_rows(
    visibility: list[dict[str, str]],
    *,
    manifests: dict[str, dict[str, str]],
    conditions: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for event in visibility:
        if event["primary_analysis_eligible"] != "yes":
            continue
        subject_id = event["subject_id"]
        condition = event["condition"]
        source = manifests[subject_id]
        timing = "early" if condition.endswith("_early") else "late"
        rows.extend(
            window_pair(
                subject_id=subject_id,
                experiment_id=event["experiment_id"],
                reference_id=(
                    f"{subject_id}__ad_{int(event['condition_index']):02d}"
                ),
                reference_kind="advertisement",
                condition=condition,
                ad_mode=event["ad_mode"],
                matched_timing=timing,
                matched_ad_conditions=condition,
                onset_eeg_offset_s=float(
                    event["visual_onset_eeg_offset_s"]
                ),
                onset_xdf_timestamp_lsl=float(
                    event["visual_onset_xdf_timestamp_lsl"]
                ),
                onset_log_unix=float(event["visual_onset_log_unix"]),
                onset_estimator=event["estimator"],
                onset_status=event["visibility_status"],
                combined_timing_uncertainty_s=float(
                    event["combined_timing_uncertainty_s"]
                ),
                condition_window=conditions[(subject_id, condition)],
                source_log=event["source_log"],
                source_canonical_markers=source["canonical_table"],
            )
        )
    return rows


def no_ad_rows(
    manifest: list[dict[str, str]],
    *,
    conditions: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in manifest:
        if source["study_protocol_eligible"] != "yes":
            continue
        markers = read_csv(Path(source["canonical_table"]))
        blocks = condition_blocks(load_log(Path(source["source_log"])))
        no_ad_block = next(
            block
            for block in blocks
            if block[0].get("data", {}).get("condition") == "no_ads"
        )
        for turn, timing in ((2, "early"), (4, "late")):
            reply = next(
                event
                for event in no_ad_block
                if event["event"] == "assistant_reply"
                and int(event.get("turn", 0)) == turn
            )
            onset_log = unix_time(reply)
            onset_xdf, onset_eeg, alignment_uncertainty = xdf_projection(
                markers,
                onset_log,
            )
            rows.extend(
                window_pair(
                    subject_id=source["subject_id"],
                    experiment_id=source["experiment_id"],
                    reference_id=(
                        f"{source['subject_id']}__no_ad_{timing}"
                    ),
                    reference_kind="matched_no_ad_reply",
                    condition="no_ads",
                    ad_mode="none",
                    matched_timing=timing,
                    matched_ad_conditions=(
                        f"inline_{timing};block_{timing}"
                    ),
                    onset_eeg_offset_s=onset_eeg,
                    onset_xdf_timestamp_lsl=onset_xdf,
                    onset_log_unix=onset_log,
                    onset_estimator="log_projected_assistant_reply",
                    onset_status="derived_clock_aligned",
                    combined_timing_uncertainty_s=alignment_uncertainty,
                    condition_window=conditions[
                        (source["subject_id"], "no_ads")
                    ],
                    source_log=source["source_log"],
                    source_canonical_markers=source["canonical_table"],
                )
            )
    return rows


def run(
    manifest_path: Path,
    visibility_path: Path,
    conditions_path: Path,
    output_path: Path,
) -> None:
    manifest = read_csv(manifest_path)
    manifests = {row["subject_id"]: row for row in manifest}
    conditions = condition_lookup(read_csv(conditions_path))
    rows = ad_rows(
        read_csv(visibility_path),
        manifests=manifests,
        conditions=conditions,
    )
    rows.extend(no_ad_rows(manifest, conditions=conditions))
    write_csv(output_path, rows)
    eligible = sum(row["primary_analysis_eligible"] == "yes" for row in rows)
    print(f"Wrote {len(rows)} ad-analysis windows to {output_path}")
    print(f"Eligible windows: {eligible}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--visibility", type=Path, default=DEFAULT_VISIBILITY)
    parser.add_argument("--conditions", type=Path, default=DEFAULT_CONDITIONS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.manifest, args.visibility, args.conditions, args.output)


if __name__ == "__main__":
    main()
