"""Generate objective and visual evidence for the EEG cleaning policy."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from scipy.signal import welch  # noqa: E402

from clean_eeg import (  # noqa: E402
    DEFAULT_POLICY,
    clean_recording,
    load_policy,
    reviewed_bad_channels,
)
from xdf_to_mne import load_xdf_as_mne  # noqa: E402


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
DEFAULT_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
DEFAULT_CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
DEFAULT_OUTPUT_DIR = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/validation/cleaning_visual"
)
REPRESENTATIVE_SUBJECTS = (
    "lab_subject_2",
    "lab_subject_5",
    "lab_subject_13",
    "lab_subject_19",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def subject_windows(path: Path) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(path):
        if row["primary_analysis_eligible"] != "yes":
            continue
        grouped.setdefault(row["subject_id"], []).append(row)
    return grouped


def bad_channels_for_subject(
    subject_id: str,
    *,
    policy: dict[str, Any],
    channel_qc_path: Path,
) -> list[str]:
    return sorted(
        set(reviewed_bad_channels(channel_qc_path, subject_id))
        | set(
            policy["bad_channel_review"]["subject_specific_interpolation"].get(
                subject_id,
                [],
            )
        )
    )


def prepare_pre_interpolation(
    subject_id: str,
    source: dict[str, str],
    *,
    policy: dict[str, Any],
    channel_qc_path: Path,
):
    raw, _ = load_xdf_as_mne(
        REPOSITORY_ROOT / source["source_xdf"],
        canonical_markers_path=(
            REPOSITORY_ROOT / source["source_canonical_markers"]
        ),
        montage_name=policy["input"]["montage"],
        acquisition_reference=policy["input"]["online_reference"],
    )
    bads = bad_channels_for_subject(
        subject_id,
        policy=policy,
        channel_qc_path=channel_qc_path,
    )
    raw.info["bads"] = bads
    filtering = policy["filtering"]
    raw.notch_filter(filtering["notch_hz"], picks="eeg", verbose=False)
    raw.filter(
        filtering["highpass_hz"],
        filtering["lowpass_hz"],
        picks="eeg",
        verbose=False,
    )
    raw.set_eeg_reference(
        policy["rereferencing"]["method"],
        projection=False,
        verbose=False,
    )
    return raw


def nearest_neighbors(raw, channel: str, count: int = 4) -> list[str]:
    index = raw.ch_names.index(channel)
    positions = np.asarray([item["loc"][:3] for item in raw.info["chs"]])
    distances = np.linalg.norm(positions - positions[index], axis=1)
    ordered = np.argsort(distances)
    return [
        raw.ch_names[candidate]
        for candidate in ordered
        if candidate != index
    ][:count]


def worst_segment(
    raw,
    windows: list[dict[str, str]],
    channel: str,
    seconds: float = 10.0,
) -> tuple[int, int, str]:
    sfreq = float(raw.info["sfreq"])
    length = int(round(seconds * sfreq))
    best: tuple[float, int, int, str] | None = None
    for window in windows:
        start = int(math.ceil(float(window["start_eeg_offset_s"]) * sfreq))
        stop = min(
            int(math.floor(float(window["end_eeg_offset_s"]) * sfreq)),
            int(raw.n_times),
        )
        for segment_start in range(start, stop - length + 1, length):
            segment_stop = segment_start + length
            data = raw.get_data(
                picks=[channel],
                start=segment_start,
                stop=segment_stop,
            )[0]
            score = float(np.ptp(data))
            candidate = (
                score,
                segment_start,
                segment_stop,
                window["window_id"],
            )
            if best is None or candidate[0] > best[0]:
                best = candidate
    if best is None:
        raise ValueError(f"No complete validation segment for {channel}")
    return best[1], best[2], best[3]


def psd_db_uv2_per_hz(data_v: np.ndarray, sfreq: float):
    frequencies, density = welch(
        data_v,
        fs=sfreq,
        nperseg=min(int(2 * sfreq), data_v.shape[-1]),
        noverlap=min(int(sfreq), data_v.shape[-1] // 2),
        axis=-1,
        detrend="constant",
    )
    mean_density = np.mean(density, axis=0)
    return frequencies, 10 * np.log10(
        np.maximum(mean_density * 1e12, np.finfo(float).tiny)
    )


def line_noise_power(data_v: np.ndarray, sfreq: float) -> float:
    frequencies, density = welch(
        data_v,
        fs=sfreq,
        nperseg=min(int(4 * sfreq), data_v.shape[-1]),
        axis=-1,
        detrend="constant",
    )
    mean_density = np.mean(density, axis=0)
    line = (frequencies >= 49.0) & (frequencies <= 51.0)
    reference = (frequencies >= 45.0) & (frequencies <= 55.0) & ~line
    return float(np.mean(mean_density[line]) / np.mean(mean_density[reference]))


def filtering_evidence(
    windows_by_subject: dict[str, list[dict[str, str]]],
    *,
    policy: dict[str, Any],
    channel_qc_path: Path,
    output_dir: Path,
) -> list[dict[str, Any]]:
    figure, axes = plt.subplots(
        len(REPRESENTATIVE_SUBJECTS),
        1,
        figsize=(10, 10),
        sharex=True,
    )
    results: list[dict[str, Any]] = []
    for axis, subject_id in zip(axes, REPRESENTATIVE_SUBJECTS):
        source = windows_by_subject[subject_id][0]
        raw, _ = load_xdf_as_mne(
            REPOSITORY_ROOT / source["source_xdf"],
            canonical_markers_path=(
                REPOSITORY_ROOT / source["source_canonical_markers"]
            ),
        )
        clean, _ = clean_recording(
            subject_id=subject_id,
            xdf_path=REPOSITORY_ROOT / source["source_xdf"],
            canonical_markers_path=(
                REPOSITORY_ROOT / source["source_canonical_markers"]
            ),
            channel_qc_path=channel_qc_path,
        )
        condition = next(
            row
            for row in windows_by_subject[subject_id]
            if row["window_type"] == "condition"
        )
        sfreq = float(raw.info["sfreq"])
        start = int(float(condition["start_eeg_offset_s"]) * sfreq)
        stop = min(start + int(30 * sfreq), int(raw.n_times))
        raw_data = raw.get_data(start=start, stop=stop, picks="eeg")
        clean_data = clean.get_data(start=start, stop=stop, picks="eeg")
        raw_freq, raw_psd = psd_db_uv2_per_hz(raw_data, sfreq)
        clean_freq, clean_psd = psd_db_uv2_per_hz(clean_data, sfreq)
        axis.plot(raw_freq, raw_psd, color="#A45A52", alpha=0.8, label="Raw")
        axis.plot(
            clean_freq,
            clean_psd,
            color="#2A7F62",
            linewidth=1.5,
            label="Cleaned",
        )
        axis.axvline(50, color="#C2872B", linestyle="--", linewidth=1)
        axis.set_xlim(0.5, 80)
        axis.set_ylabel(subject_id.replace("lab_subject_", "S"))
        raw_line = line_noise_power(raw_data, sfreq)
        clean_line = line_noise_power(clean_data, sfreq)
        average_rms_uv = float(
            np.sqrt(np.mean(np.mean(clean_data, axis=0) ** 2)) * 1e6
        )
        results.append(
            {
                "subject_id": subject_id,
                "raw_line_noise_ratio": raw_line,
                "clean_line_noise_ratio": clean_line,
                "line_noise_reduction_fraction": 1.0 - clean_line / raw_line,
                "average_reference_mean_rms_uv": average_rms_uv,
                "line_noise_pass": clean_line < raw_line * 0.25,
                "average_reference_pass": average_rms_uv < 5.0,
            }
        )
    axes[0].legend(frameon=False, ncol=2, loc="upper right")
    axes[-1].set_xlabel("Frequency (Hz)")
    figure.supylabel("PSD (dB µV²/Hz)")
    figure.suptitle("Filtering and rereferencing validation", fontweight="bold")
    figure.tight_layout()
    figure.savefig(output_dir / "filtering_validation.png", dpi=180)
    plt.close(figure)
    return results


def interpolation_evidence(
    windows_by_subject: dict[str, list[dict[str, str]]],
    *,
    policy: dict[str, Any],
    channel_qc_path: Path,
    output_dir: Path,
) -> list[dict[str, Any]]:
    repairs = []
    for subject_id in sorted(windows_by_subject):
        for channel in bad_channels_for_subject(
            subject_id,
            policy=policy,
            channel_qc_path=channel_qc_path,
        ):
            repairs.append((subject_id, channel))
    figure, axes = plt.subplots(
        len(repairs),
        2,
        figsize=(13, 3.2 * len(repairs)),
        squeeze=False,
    )
    results: list[dict[str, Any]] = []
    for row_index, (subject_id, channel) in enumerate(repairs):
        source = windows_by_subject[subject_id][0]
        pre = prepare_pre_interpolation(
            subject_id,
            source,
            policy=policy,
            channel_qc_path=channel_qc_path,
        )
        post, _ = clean_recording(
            subject_id=subject_id,
            xdf_path=REPOSITORY_ROOT / source["source_xdf"],
            canonical_markers_path=(
                REPOSITORY_ROOT / source["source_canonical_markers"]
            ),
            channel_qc_path=channel_qc_path,
        )
        start, stop, window_id = worst_segment(
            pre,
            windows_by_subject[subject_id],
            channel,
        )
        neighbors = nearest_neighbors(pre, channel)
        pre_channel = pre.get_data(
            picks=[channel], start=start, stop=stop
        )[0] * 1e6
        post_channel = post.get_data(
            picks=[channel], start=start, stop=stop
        )[0] * 1e6
        neighbor_data = post.get_data(
            picks=neighbors, start=start, stop=stop
        ) * 1e6
        neighbor_median = np.median(neighbor_data, axis=0)
        sfreq = float(pre.info["sfreq"])
        times = np.arange(stop - start) / sfreq

        trace_axis = axes[row_index, 0]
        trace_axis.plot(times, pre_channel, color="#A45A52", alpha=0.7, label="Before")
        trace_axis.plot(times, post_channel, color="#2A7F62", label="Interpolated")
        trace_axis.plot(
            times,
            neighbor_median,
            color="#355C7D",
            alpha=0.8,
            linewidth=1,
            label="Neighbor median",
        )
        trace_axis.set_title(f"{subject_id} {channel} · {window_id}")
        trace_axis.set_xlabel("Seconds")
        trace_axis.set_ylabel("Amplitude (µV)")
        trace_axis.legend(frameon=False, ncol=3, fontsize=8)

        psd_axis = axes[row_index, 1]
        pre_freq, pre_psd = psd_db_uv2_per_hz(pre_channel[None, :] * 1e-6, sfreq)
        post_freq, post_psd = psd_db_uv2_per_hz(
            post_channel[None, :] * 1e-6,
            sfreq,
        )
        psd_axis.plot(pre_freq, pre_psd, color="#A45A52", label="Before")
        psd_axis.plot(post_freq, post_psd, color="#2A7F62", label="Interpolated")
        psd_axis.set_xlim(0.5, 40)
        psd_axis.set_xlabel("Frequency (Hz)")
        psd_axis.set_ylabel("PSD (dB µV²/Hz)")
        psd_axis.legend(frameon=False, fontsize=8)

        correlation = float(np.corrcoef(post_channel, neighbor_median)[0, 1])
        pre_ptp = float(np.ptp(pre_channel))
        post_ptp = float(np.ptp(post_channel))
        results.append(
            {
                "subject_id": subject_id,
                "channel": channel,
                "validation_window": window_id,
                "neighbors": neighbors,
                "pre_interpolation_peak_to_peak_uv": pre_ptp,
                "post_interpolation_peak_to_peak_uv": post_ptp,
                "post_neighbor_correlation": correlation,
                "amplitude_pass": post_ptp < 1000.0,
                "spatial_consistency_pass": correlation > 0.4,
            }
        )
    figure.suptitle("Recording-specific channel interpolation", fontweight="bold")
    figure.tight_layout()
    figure.savefig(output_dir / "interpolation_validation.png", dpi=180)
    plt.close(figure)
    return results


def run(
    *,
    windows_path: Path,
    channel_qc_path: Path,
    policy_path: Path,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    policy = load_policy(policy_path)
    windows_by_subject = subject_windows(windows_path)
    filtering = filtering_evidence(
        windows_by_subject,
        policy=policy,
        channel_qc_path=channel_qc_path,
        output_dir=output_dir,
    )
    interpolation = interpolation_evidence(
        windows_by_subject,
        policy=policy,
        channel_qc_path=channel_qc_path,
        output_dir=output_dir,
    )
    objective_pass = all(
        row["line_noise_pass"] and row["average_reference_pass"]
        for row in filtering
    ) and all(
        row["amplitude_pass"] and row["spatial_consistency_pass"]
        for row in interpolation
    )
    report = {
        "policy_version": policy["policy_version"],
        "policy_status": policy["status"],
        "objective_status": "passed" if objective_pass else "failed",
        "human_visual_signoff": "pending",
        "filtering_checks": filtering,
        "interpolation_checks": interpolation,
        "figures": [
            str(output_dir / "filtering_validation.png"),
            str(output_dir / "interpolation_validation.png"),
        ],
    }
    report_path = output_dir / "cleaning_visual_validation.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps(report, indent=2))
    print(f"Wrote visual validation pack to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument("--channel-qc", type=Path, default=DEFAULT_CHANNEL_QC)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    run(
        windows_path=args.windows,
        channel_qc_path=args.channel_qc,
        policy_path=args.policy,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
