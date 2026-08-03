"""Audit XDF-to-MNE conversion across the current recording manifest."""

from __future__ import annotations

import argparse
import csv
import gc
from pathlib import Path
from typing import Any

import numpy as np

from xdf_to_mne import load_xdf_as_mne


DEFAULT_MANIFEST = Path(
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
DEFAULT_OUTPUT = Path(
    "src/project/logs/xdf/silver/audits/xdf_mne_acquisition_audit.csv"
)


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


def run(manifest_path: Path, output_path: Path, subjects: set[str]) -> None:
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    if subjects:
        manifest = [row for row in manifest if row["subject_id"] in subjects]
    if not manifest:
        raise ValueError("No manifest rows selected")

    rows: list[dict[str, Any]] = []
    failures = 0
    for source in manifest:
        subject_id = source["subject_id"]
        print(f"Auditing {subject_id}")
        try:
            raw, report = load_xdf_as_mne(
                Path(source["source_xdf"]),
                canonical_markers_path=Path(source["canonical_table"]),
            )
            stride = max(1, report.sample_count // 100_000)
            sampled_data = raw._data[:, ::stride]
            channel_medians = np.median(sampled_data, axis=1, keepdims=True)
            absolute_dc_uv = np.abs(channel_medians) * 1e6
            centered_absolute_uv = (
                np.abs(sampled_data - channel_medians) * 1e6
            )
            expected_duration = (report.sample_count - 1) / report.nominal_srate_hz
            rows.append(
                {
                    "subject_id": subject_id,
                    "study_type": source["study_type"],
                    "study_protocol_eligible": source[
                        "study_protocol_eligible"
                    ],
                    "source_xdf": report.source_xdf,
                    "eeg_stream_name": report.eeg_stream_name,
                    "manufacturer": report.manufacturer,
                    "channel_count": report.channel_count,
                    "channel_names": ";".join(report.channel_names),
                    "source_units": ";".join(sorted(set(report.source_units))),
                    "scale_to_volts": f"{report.scale_to_volts:.9g}",
                    "nominal_srate_hz": f"{report.nominal_srate_hz:.6f}",
                    "effective_srate_hz": f"{report.effective_srate_hz:.6f}",
                    "timestamp_p95_jitter_s": (
                        f"{report.timestamp_p95_jitter_s:.9f}"
                    ),
                    "xdf_duration_s": f"{report.duration_s:.6f}",
                    "mne_regular_duration_s": f"{expected_duration:.6f}",
                    "duration_difference_s": (
                        f"{report.duration_s - expected_duration:.6f}"
                    ),
                    "montage": report.montage,
                    "montage_missing_channels": ";".join(
                        report.montage_missing_channels
                    ),
                    "montage_complete": (
                        "yes" if not report.montage_missing_channels else "no"
                    ),
                    "acquisition_reference": report.acquisition_reference,
                    "fcz_recorded": (
                        "yes"
                        if "fcz"
                        in {name.lower() for name in report.channel_names}
                        else "no"
                    ),
                    "canonical_annotation_count": (
                        report.canonical_annotation_count
                    ),
                    "first_annotation_s": (
                        f"{report.first_annotation_s:.6f}"
                        if report.first_annotation_s is not None
                        else ""
                    ),
                    "last_annotation_s": (
                        f"{report.last_annotation_s:.6f}"
                        if report.last_annotation_s is not None
                        else ""
                    ),
                    "annotation_max_nearest_sample_error_s": (
                        f"{report.annotation_max_nearest_sample_error_s:.9f}"
                        if report.annotation_max_nearest_sample_error_s
                        is not None
                        else ""
                    ),
                    "annotation_max_regularization_shift_s": (
                        f"{report.annotation_max_regularization_shift_s:.6f}"
                        if report.annotation_max_regularization_shift_s
                        is not None
                        else ""
                    ),
                    "median_abs_channel_dc_offset_uv": (
                        f"{np.median(absolute_dc_uv):.6f}"
                    ),
                    "max_abs_channel_dc_offset_uv": (
                        f"{np.max(absolute_dc_uv):.6f}"
                    ),
                    "p95_centered_abs_amplitude_uv": (
                        f"{np.percentile(centered_absolute_uv, 95):.6f}"
                    ),
                    "p99_centered_abs_amplitude_uv": (
                        f"{np.percentile(centered_absolute_uv, 99):.6f}"
                    ),
                    "conversion_status": "passed",
                    "error": "",
                }
            )
            del (
                sampled_data,
                channel_medians,
                absolute_dc_uv,
                centered_absolute_uv,
                raw,
            )
            gc.collect()
        except Exception as exc:
            failures += 1
            rows.append(
                {
                    "subject_id": subject_id,
                    "study_type": source.get("study_type", ""),
                    "study_protocol_eligible": source.get(
                        "study_protocol_eligible", ""
                    ),
                    "source_xdf": source.get("source_xdf", ""),
                    "eeg_stream_name": "",
                    "manufacturer": "",
                    "channel_count": "",
                    "channel_names": "",
                    "source_units": "",
                    "scale_to_volts": "",
                    "nominal_srate_hz": "",
                    "effective_srate_hz": "",
                    "timestamp_p95_jitter_s": "",
                    "xdf_duration_s": "",
                    "mne_regular_duration_s": "",
                    "duration_difference_s": "",
                    "montage": "",
                    "montage_missing_channels": "",
                    "montage_complete": "no",
                    "acquisition_reference": "unknown",
                    "fcz_recorded": "",
                    "canonical_annotation_count": "",
                    "first_annotation_s": "",
                    "last_annotation_s": "",
                    "annotation_max_nearest_sample_error_s": "",
                    "annotation_max_regularization_shift_s": "",
                    "median_abs_channel_dc_offset_uv": "",
                    "max_abs_channel_dc_offset_uv": "",
                    "p95_centered_abs_amplitude_uv": "",
                    "p99_centered_abs_amplitude_uv": "",
                    "conversion_status": "failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
    write_csv(output_path, rows)
    print(f"Wrote {len(rows)} rows to {output_path}; failures={failures}")
    if failures:
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--subjects", nargs="*", default=[])
    args = parser.parse_args()
    run(args.manifest, args.output, set(args.subjects))


if __name__ == "__main__":
    main()
