"""Compute condition-blind channel and recording EEG quality metrics.

The audit samples evenly spaced windows from the complete recording. Filtering is
used only to measure quality; no cleaned EEG is written.
"""

from __future__ import annotations

import argparse
import csv
import gc
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.signal import butter, sosfiltfilt, welch

from xdf_to_mne import load_xdf_as_mne


DEFAULT_MANIFEST = Path(
    "src/project/logs/xdf/silver/canonical_marker_manifest.csv"
)
DEFAULT_CHANNEL_OUTPUT = Path(
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
DEFAULT_RECORDING_OUTPUT = Path(
    "src/project/logs/xdf/silver/audits/eeg_recording_quality.csv"
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


def window_starts(
    sample_count: int,
    window_samples: int,
    requested_windows: int,
) -> list[int]:
    if sample_count <= window_samples:
        return [0]
    return sorted(
        {
            int(value)
            for value in np.linspace(
                0,
                sample_count - window_samples,
                requested_windows,
            )
        }
    )


def safe_correlations(data: np.ndarray) -> np.ndarray:
    reference = np.median(data, axis=0)
    reference_std = float(np.std(reference))
    correlations = np.full(data.shape[0], np.nan)
    if reference_std == 0:
        return correlations
    for index, channel in enumerate(data):
        if float(np.std(channel)) == 0:
            continue
        correlations[index] = float(np.corrcoef(channel, reference)[0, 1])
    return correlations


def spectral_ratios(
    data: np.ndarray,
    sfreq: float,
) -> tuple[np.ndarray, np.ndarray]:
    frequencies, psd = welch(
        data,
        fs=sfreq,
        nperseg=min(int(sfreq * 2), data.shape[1]),
        axis=1,
    )
    total_mask = (frequencies >= 1.0) & (frequencies <= 80.0)
    line_mask = (frequencies >= 49.0) & (frequencies <= 51.0)
    low_mask = (frequencies >= 1.0) & (frequencies <= 40.0)
    high_mask = (frequencies >= 30.0) & (frequencies <= 40.0)
    total = np.trapezoid(psd[:, total_mask], frequencies[total_mask], axis=1)
    line = np.trapezoid(psd[:, line_mask], frequencies[line_mask], axis=1)
    low = np.trapezoid(psd[:, low_mask], frequencies[low_mask], axis=1)
    high = np.trapezoid(psd[:, high_mask], frequencies[high_mask], axis=1)
    return (
        np.divide(line, total, out=np.zeros_like(line), where=total > 0),
        np.divide(high, low, out=np.zeros_like(high), where=low > 0),
    )


def provisional_reasons(
    *,
    channel_name: str,
    robust_std_uv: float,
    correlation: float,
    flat_fraction: float,
) -> list[str]:
    reasons: list[str] = []
    if robust_std_uv < 0.5:
        reasons.append("near_flat")
    if (
        robust_std_uv > 150.0
        and np.isfinite(correlation)
        and correlation < 0.40
    ):
        reasons.append("extreme_amplitude")
    if (
        channel_name.lower() not in {"fp1", "fp2"}
        and np.isfinite(correlation)
        and correlation < 0.40
    ):
        reasons.append("low_correlation")
    if flat_fraction > 0.01:
        reasons.append("flatline")
    return reasons


def audit_recording(
    source: dict[str, str],
    *,
    window_seconds: float,
    requested_windows: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw, report = load_xdf_as_mne(
        Path(source["source_xdf"]),
        canonical_markers_path=Path(source["canonical_table"]),
    )
    sfreq = float(raw.info["sfreq"])
    window_samples = max(int(round(window_seconds * sfreq)), int(sfreq * 4))
    starts = window_starts(
        report.sample_count,
        window_samples,
        requested_windows,
    )
    sos = butter(
        4,
        [0.5, 40.0],
        btype="bandpass",
        fs=sfreq,
        output="sos",
    )
    metrics: dict[str, list[np.ndarray]] = {
        "robust_std_uv": [],
        "robust_peak_to_peak_uv": [],
        "correlation": [],
        "flat_fraction": [],
        "line_noise_ratio": [],
        "high_frequency_ratio": [],
    }
    for start in starts:
        stop = min(start + window_samples, report.sample_count)
        segment = raw.get_data(start=start, stop=stop)
        filtered = sosfiltfilt(sos, segment, axis=1)
        channel_median = np.median(filtered, axis=1, keepdims=True)
        mad = np.median(np.abs(filtered - channel_median), axis=1)
        metrics["robust_std_uv"].append(1.4826 * mad * 1e6)
        metrics["robust_peak_to_peak_uv"].append(
            (
                np.percentile(filtered, 99.5, axis=1)
                - np.percentile(filtered, 0.5, axis=1)
            )
            * 1e6
        )
        metrics["correlation"].append(safe_correlations(filtered))
        metrics["flat_fraction"].append(
            np.mean(np.diff(segment, axis=1) == 0, axis=1)
        )
        line_ratio, high_ratio = spectral_ratios(segment, sfreq)
        metrics["line_noise_ratio"].append(line_ratio)
        metrics["high_frequency_ratio"].append(high_ratio)

    aggregated = {
        name: np.nanmedian(np.stack(values), axis=0)
        for name, values in metrics.items()
    }
    channel_rows: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    flagged_count = 0
    for index, channel_name in enumerate(report.channel_names):
        values = {
            name: float(result[index])
            for name, result in aggregated.items()
        }
        reasons = provisional_reasons(
            channel_name=channel_name,
            robust_std_uv=values["robust_std_uv"],
            correlation=values["correlation"],
            flat_fraction=values["flat_fraction"],
        )
        reason_counts.update(reasons)
        flagged_count += bool(reasons)
        channel_rows.append(
            {
                "subject_id": source["subject_id"],
                "study_protocol_eligible": source[
                    "study_protocol_eligible"
                ],
                "channel": channel_name,
                "windows_sampled": len(starts),
                "sampled_seconds": f"{len(starts) * window_seconds:.1f}",
                "robust_std_uv": f"{values['robust_std_uv']:.6f}",
                "robust_peak_to_peak_uv": (
                    f"{values['robust_peak_to_peak_uv']:.6f}"
                ),
                "correlation_with_median": (
                    f"{values['correlation']:.6f}"
                ),
                "flat_fraction": f"{values['flat_fraction']:.9f}",
                "line_noise_ratio": f"{values['line_noise_ratio']:.6f}",
                "high_frequency_ratio": (
                    f"{values['high_frequency_ratio']:.6f}"
                ),
                "ocular_proxy_low_correlation": (
                    "yes"
                    if channel_name.lower() in {"fp1", "fp2"}
                    and np.isfinite(values["correlation"])
                    and values["correlation"] < 0.40
                    else "no"
                ),
                "provisional_flag": "yes" if reasons else "no",
                "provisional_reasons": ";".join(reasons),
            }
        )

    summary = {
        "subject_id": source["subject_id"],
        "study_type": source["study_type"],
        "study_protocol_eligible": source["study_protocol_eligible"],
        "channel_count": report.channel_count,
        "windows_sampled": len(starts),
        "sampled_seconds": f"{len(starts) * window_seconds:.1f}",
        "flagged_channel_count": flagged_count,
        "flagged_channel_fraction": f"{flagged_count / report.channel_count:.4f}",
        "near_flat_channel_count": reason_counts["near_flat"],
        "extreme_amplitude_channel_count": reason_counts[
            "extreme_amplitude"
        ],
        "low_correlation_channel_count": reason_counts["low_correlation"],
        "ocular_proxy_low_correlation_count": sum(
            row["ocular_proxy_low_correlation"] == "yes"
            for row in channel_rows
        ),
        "flatline_channel_count": reason_counts["flatline"],
        "channels_above_20pct_line_noise": int(
            np.sum(aggregated["line_noise_ratio"] > 0.20)
        ),
        "median_channel_robust_std_uv": (
            f"{np.nanmedian(aggregated['robust_std_uv']):.6f}"
        ),
        "median_channel_correlation": (
            f"{np.nanmedian(aggregated['correlation']):.6f}"
        ),
        "median_line_noise_ratio": (
            f"{np.nanmedian(aggregated['line_noise_ratio']):.6f}"
        ),
        "notch_50hz_required": (
            "yes"
            if np.nanmedian(aggregated["line_noise_ratio"]) > 0.20
            else "no"
        ),
        "automatic_recording_exclusion": "no",
        "review_status": "pending",
    }
    del raw
    gc.collect()
    return channel_rows, summary


def run(
    manifest_path: Path,
    channel_output: Path,
    recording_output: Path,
    *,
    subjects: set[str],
    window_seconds: float,
    requested_windows: int,
) -> None:
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest = list(csv.DictReader(handle))
    if subjects:
        manifest = [row for row in manifest if row["subject_id"] in subjects]
    if not manifest:
        raise ValueError("No manifest rows selected")

    channel_rows: list[dict[str, Any]] = []
    recording_rows: list[dict[str, Any]] = []
    for source in manifest:
        print(f"Signal QC {source['subject_id']}")
        channels, recording = audit_recording(
            source,
            window_seconds=window_seconds,
            requested_windows=requested_windows,
        )
        channel_rows.extend(channels)
        recording_rows.append(recording)
    write_csv(channel_output, channel_rows)
    write_csv(recording_output, recording_rows)
    print(
        f"Wrote {len(channel_rows)} channel rows and "
        f"{len(recording_rows)} recording rows"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--channel-output",
        type=Path,
        default=DEFAULT_CHANNEL_OUTPUT,
    )
    parser.add_argument(
        "--recording-output",
        type=Path,
        default=DEFAULT_RECORDING_OUTPUT,
    )
    parser.add_argument("--subjects", nargs="*", default=[])
    parser.add_argument("--window-seconds", type=float, default=30.0)
    parser.add_argument("--windows", type=int, default=12)
    args = parser.parse_args()
    run(
        args.manifest,
        args.channel_output,
        args.recording_output,
        subjects=set(args.subjects),
        window_seconds=args.window_seconds,
        requested_windows=args.windows,
    )


if __name__ == "__main__":
    main()
