"""Build analysis-ready condition-level EEG spectral feature tables."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy.signal import welch


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
SIGNAL_DIR = REPOSITORY_ROOT / "analysis/eeg/preprocessing/silver/signal"
sys.path.insert(0, str(SIGNAL_DIR))

from clean_eeg import clean_recording, load_policy  # noqa: E402


DEFAULT_WINDOWS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/windows/condition_windows.csv"
)
DEFAULT_CHANNEL_QC = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/audits/eeg_channel_quality.csv"
)
DEFAULT_EPOCHS = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_epoch_features.csv"
)
DEFAULT_SUMMARY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_features.csv"
)

BANDS = {
    "delta": (0.5, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 13.0),
    "beta": (13.0, 30.0),
    "gamma": (30.0, 40.0),
}
POWER_FEATURES = tuple(f"{band}_power_db_uv2" for band in BANDS)
RELATIVE_FEATURES = tuple(f"{band}_relative_power" for band in BANDS)
DERIVED_FEATURES = (
    "fz_theta_power_db_uv2",
    "posterior_alpha_power_db_uv2",
    "faa_log_f4_minus_f3",
    "engagement_beta_over_alpha_theta",
    "engagement_pope_frontocentral_beta_over_alpha_theta",
    "engagement_kislov_central_beta16_24_over_alpha8_12",
)
SUMMARY_FEATURES = POWER_FEATURES + RELATIVE_FEATURES + DERIVED_FEATURES


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def band_integral(
    psd: np.ndarray,
    frequencies: np.ndarray,
    low_hz: float,
    high_hz: float,
) -> np.ndarray:
    mask = (frequencies >= low_hz) & (frequencies <= high_hz)
    if np.count_nonzero(mask) < 2:
        raise ValueError(
            f"Insufficient frequency bins for {low_hz:g}-{high_hz:g} Hz"
        )
    return np.trapezoid(psd[:, mask], frequencies[mask], axis=1)


def safe_db_uv2(power_v2: float) -> float:
    return 10.0 * math.log10(max(power_v2 * 1e12, np.finfo(float).tiny))


def spectral_features(
    data_v: np.ndarray,
    *,
    sfreq: float,
    channel_names: list[str],
) -> dict[str, float]:
    nperseg = min(int(round(2.0 * sfreq)), data_v.shape[1])
    frequencies, psd = welch(
        data_v,
        fs=sfreq,
        nperseg=nperseg,
        noverlap=nperseg // 2,
        axis=1,
        detrend="constant",
        scaling="density",
    )
    powers = {
        band: band_integral(psd, frequencies, low_hz, high_hz)
        for band, (low_hz, high_hz) in BANDS.items()
    }
    total_per_channel = band_integral(psd, frequencies, 0.5, 40.0)
    total_power = float(np.mean(total_per_channel))

    features: dict[str, float] = {}
    for band, channel_powers in powers.items():
        global_power = float(np.mean(channel_powers))
        features[f"{band}_power_db_uv2"] = safe_db_uv2(global_power)
        features[f"{band}_relative_power"] = (
            global_power / total_power if total_power > 0 else math.nan
        )

    lookup = {name.lower(): index for index, name in enumerate(channel_names)}
    if "f3" not in lookup or "f4" not in lookup:
        raise ValueError("FAA requires F3 and F4 channels")
    f3_alpha = float(powers["alpha"][lookup["f3"]])
    f4_alpha = float(powers["alpha"][lookup["f4"]])
    if "fz" not in lookup:
        raise ValueError("Frontal-midline theta requires Fz")
    features["fz_theta_power_db_uv2"] = safe_db_uv2(
        float(powers["theta"][lookup["fz"]])
    )
    posterior_channels = ("o1", "oz", "o2", "p3", "pz", "p4")
    missing_posterior = [
        channel for channel in posterior_channels if channel not in lookup
    ]
    if missing_posterior:
        raise ValueError(
            f"Posterior alpha requires channels: {missing_posterior}"
        )
    features["posterior_alpha_power_db_uv2"] = safe_db_uv2(
        float(
            np.mean(
                [
                    powers["alpha"][lookup[channel]]
                    for channel in posterior_channels
                ]
            )
        )
    )
    features["faa_log_f4_minus_f3"] = math.log(
        max(f4_alpha, np.finfo(float).tiny)
    ) - math.log(max(f3_alpha, np.finfo(float).tiny))

    alpha = float(np.mean(powers["alpha"]))
    theta = float(np.mean(powers["theta"]))
    beta = float(np.mean(powers["beta"]))
    denominator = alpha + theta
    features["engagement_beta_over_alpha_theta"] = (
        beta / denominator if denominator > 0 else math.nan
    )
    frontocentral_channels = (
        "f3",
        "f4",
        "fz",
        "fc1",
        "fc2",
        "c3",
        "c4",
        "cz",
    )
    missing_frontocentral = [
        channel for channel in frontocentral_channels if channel not in lookup
    ]
    if missing_frontocentral:
        raise ValueError(
            "Frontocentral engagement requires channels: "
            f"{missing_frontocentral}"
        )
    frontocentral_alpha = float(
        np.mean(
            [
                powers["alpha"][lookup[channel]]
                for channel in frontocentral_channels
            ]
        )
    )
    frontocentral_theta = float(
        np.mean(
            [
                powers["theta"][lookup[channel]]
                for channel in frontocentral_channels
            ]
        )
    )
    frontocentral_beta = float(
        np.mean(
            [
                powers["beta"][lookup[channel]]
                for channel in frontocentral_channels
            ]
        )
    )
    features["engagement_pope_frontocentral_beta_over_alpha_theta"] = (
        frontocentral_beta / (frontocentral_alpha + frontocentral_theta)
    )

    central_channels = ("cz", "pz", "p3", "p4")
    missing_central = [
        channel for channel in central_channels if channel not in lookup
    ]
    if missing_central:
        raise ValueError(
            f"Central engagement requires channels: {missing_central}"
        )
    alpha_8_12 = band_integral(psd, frequencies, 8.0, 12.0)
    beta_16_24 = band_integral(psd, frequencies, 16.0, 24.0)
    central_alpha = float(
        np.mean([alpha_8_12[lookup[channel]] for channel in central_channels])
    )
    central_beta = float(
        np.mean([beta_16_24[lookup[channel]] for channel in central_channels])
    )
    features["engagement_kislov_central_beta16_24_over_alpha8_12"] = (
        central_beta / central_alpha
    )
    return features


def quality_features(
    data_v: np.ndarray,
    channel_names: list[str],
) -> dict[str, float | int | str]:
    data_uv = data_v * 1e6
    peak_to_peak = np.ptp(data_uv, axis=1)
    channel_std = np.std(data_uv, axis=1)
    max_abs_by_channel = np.max(np.abs(data_uv), axis=1)
    channel_lookup = {
        name.lower(): index for index, name in enumerate(channel_names)
    }
    frontal_peak_to_peak = {
        f"{channel.lower()}_peak_to_peak_uv": (
            float(peak_to_peak[channel_lookup[channel.lower()]])
            if channel.lower() in channel_lookup
            else math.nan
        )
        for channel in ("Fp1", "Fp2", "F3", "F4")
    }
    return {
        "max_abs_amplitude_uv": float(np.max(max_abs_by_channel)),
        "max_abs_amplitude_channel": channel_names[
            int(np.argmax(max_abs_by_channel))
        ],
        "max_peak_to_peak_uv": float(np.max(peak_to_peak)),
        "max_peak_to_peak_channel": channel_names[int(np.argmax(peak_to_peak))],
        "median_peak_to_peak_uv": float(np.median(peak_to_peak)),
        "max_channel_std_uv": float(np.max(channel_std)),
        "median_channel_std_uv": float(np.median(channel_std)),
        "near_flat_channel_count": int(np.count_nonzero(channel_std < 0.5)),
        **frontal_peak_to_peak,
    }


def complete_epoch_bounds(
    *,
    start_s: float,
    end_s: float,
    sfreq: float,
    epoch_seconds: float,
    raw_sample_count: int,
) -> Iterable[tuple[int, int, int]]:
    epoch_samples = int(round(epoch_seconds * sfreq))
    start_sample = max(0, int(math.ceil(start_s * sfreq)))
    stop_sample = min(raw_sample_count, int(math.floor(end_s * sfreq)))
    epoch_count = max(0, (stop_sample - start_sample) // epoch_samples)
    for epoch_index in range(epoch_count):
        epoch_start = start_sample + epoch_index * epoch_samples
        yield epoch_index, epoch_start, epoch_start + epoch_samples


def epoch_row(
    window: dict[str, str],
    *,
    epoch_index: int,
    start_sample: int,
    stop_sample: int,
    sfreq: float,
    data_v: np.ndarray,
    channel_names: list[str],
    epoch_rejection: dict[str, Any],
    ica_applied: bool,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "subject_id": window["subject_id"],
        "experiment_id": window["experiment_id"],
        "window_id": window["window_id"],
        "window_type": window["window_type"],
        "condition": window["condition"],
        "ad_mode": window["ad_mode"],
        "trial_index": window["trial_index"],
        "epoch_index": epoch_index,
        "epoch_start_eeg_offset_s": f"{start_sample / sfreq:.6f}",
        "epoch_end_eeg_offset_s": f"{stop_sample / sfreq:.6f}",
        "epoch_duration_s": f"{(stop_sample - start_sample) / sfreq:.6f}",
        "sampling_rate_hz": f"{sfreq:.6f}",
        "channel_count": len(channel_names),
        "baseline_eye_state": (
            "uncontrolled_mostly_open"
            if window["window_type"] == "baseline"
            else "not_applicable"
        ),
        "ica_applied": "yes" if ica_applied else "no",
        "artifact_policy_status": epoch_rejection["status"],
        "max_peak_to_peak_threshold_uv": epoch_rejection[
            "max_peak_to_peak_uv"
        ],
    }
    quality = quality_features(data_v, channel_names)
    row.update(quality)
    rejection_reasons: list[str] = []
    if float(quality["max_peak_to_peak_uv"]) > float(
        epoch_rejection["max_peak_to_peak_uv"]
    ):
        rejection_reasons.append("gross_peak_to_peak")
    if (
        epoch_rejection["reject_near_flat_channels"]
        and int(quality["near_flat_channel_count"]) > 0
    ):
        rejection_reasons.append("near_flat_channel")
    row["retained_by_policy"] = "no" if rejection_reasons else "yes"
    row["artifact_rejection_reason"] = ";".join(rejection_reasons)
    row.update(spectral_features(data_v, sfreq=sfreq, channel_names=channel_names))
    row["source_xdf"] = window["source_xdf"]
    row["source_xdf_sha256"] = window["source_xdf_sha256"]
    row["source_canonical_markers"] = window["source_canonical_markers"]
    return row


def percentile(values: list[float], quantile: float) -> float:
    return float(np.quantile(np.asarray(values, dtype=float), quantile))


def summarize_window(
    rows: list[dict[str, Any]],
    epoch_rejection: dict[str, Any],
) -> dict[str, Any]:
    first = rows[0]
    retained_rows = [
        row for row in rows if row["retained_by_policy"] == "yes"
    ]
    if not retained_rows:
        raise ValueError(f"{first['window_id']} has no retained epochs")
    retained_fraction = len(retained_rows) / len(rows)
    window_eligible = (
        len(retained_rows) >= int(epoch_rejection["minimum_retained_epochs"])
        and retained_fraction
        >= float(epoch_rejection["minimum_retained_fraction"])
    )
    summary: dict[str, Any] = {
        "subject_id": first["subject_id"],
        "experiment_id": first["experiment_id"],
        "window_id": first["window_id"],
        "window_type": first["window_type"],
        "condition": first["condition"],
        "ad_mode": first["ad_mode"],
        "trial_index": first["trial_index"],
        "baseline_eye_state": first["baseline_eye_state"],
        "epoch_duration_s": first["epoch_duration_s"],
        "complete_epoch_count": len(rows),
        "retained_epoch_count": len(retained_rows),
        "retained_epoch_fraction": retained_fraction,
        "retained_duration_s": (
            len(retained_rows) * float(first["epoch_duration_s"])
        ),
        "minimum_retained_fraction": epoch_rejection[
            "minimum_retained_fraction"
        ],
        "minimum_retained_epochs": epoch_rejection[
            "minimum_retained_epochs"
        ],
        "primary_analysis_eligible": "yes" if window_eligible else "no",
        "exclusion_reason": "" if window_eligible else "insufficient_clean_epochs",
        "artifact_policy_status": epoch_rejection["status"],
        "ica_applied": first["ica_applied"],
        "max_peak_to_peak_uv_p50": percentile(
            [float(row["max_peak_to_peak_uv"]) for row in rows], 0.5
        ),
        "max_peak_to_peak_uv_p95": percentile(
            [float(row["max_peak_to_peak_uv"]) for row in rows], 0.95
        ),
        "max_abs_amplitude_uv_p95": percentile(
            [float(row["max_abs_amplitude_uv"]) for row in rows], 0.95
        ),
        "epochs_with_near_flat_channel": sum(
            int(row["near_flat_channel_count"]) > 0 for row in rows
        ),
    }
    for feature in SUMMARY_FEATURES:
        values = [float(row[feature]) for row in retained_rows]
        summary[f"{feature}_median"] = percentile(values, 0.5)
        summary[f"{feature}_iqr"] = percentile(values, 0.75) - percentile(
            values, 0.25
        )
    summary["source_xdf"] = first["source_xdf"]
    summary["source_xdf_sha256"] = first["source_xdf_sha256"]
    return summary


def add_baseline_deltas(summaries: list[dict[str, Any]]) -> None:
    baselines = {
        row["subject_id"]: row
        for row in summaries
        if row["window_type"] == "baseline"
    }
    for row in summaries:
        baseline = baselines.get(row["subject_id"])
        for feature in SUMMARY_FEATURES:
            output_name = f"{feature}_baseline_delta"
            if baseline is None:
                row[output_name] = ""
                continue
            row[output_name] = (
                float(row[f"{feature}_median"])
                - float(baseline[f"{feature}_median"])
            )


def build(
    *,
    windows_path: Path,
    channel_qc_path: Path,
    epochs_output: Path,
    summary_output: Path,
    epoch_seconds: float,
    subjects: set[str] | None,
    policy_path: Path,
) -> None:
    if epoch_seconds < 2.0:
        raise ValueError("Epoch duration must be at least 2 seconds")
    windows = [
        row
        for row in read_csv(windows_path)
        if row["primary_analysis_eligible"] == "yes"
        and row["window_type"] in {"baseline", "condition"}
        and (subjects is None or row["subject_id"] in subjects)
    ]
    if not windows:
        raise ValueError("No eligible windows selected")
    policy = load_policy(policy_path)
    epoch_rejection = policy["epoch_rejection"]
    if not str(epoch_rejection.get("status", "")).startswith("frozen_"):
        raise ValueError("Condition features require frozen epoch rejection")

    windows_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for window in windows:
        windows_by_subject[window["subject_id"]].append(window)

    epoch_rows: list[dict[str, Any]] = []
    for subject_id in sorted(windows_by_subject):
        subject_windows = windows_by_subject[subject_id]
        first = subject_windows[0]
        print(f"{subject_id}: loading and cleaning", flush=True)
        raw, cleaning_report = clean_recording(
            subject_id=subject_id,
            xdf_path=REPOSITORY_ROOT / first["source_xdf"],
            canonical_markers_path=(
                REPOSITORY_ROOT / first["source_canonical_markers"]
            ),
            channel_qc_path=channel_qc_path,
            policy_path=policy_path,
        )
        sfreq = float(raw.info["sfreq"])
        for window in subject_windows:
            before = len(epoch_rows)
            for epoch_index, start_sample, stop_sample in complete_epoch_bounds(
                start_s=float(window["start_eeg_offset_s"]),
                end_s=float(window["end_eeg_offset_s"]),
                sfreq=sfreq,
                epoch_seconds=epoch_seconds,
                raw_sample_count=int(raw.n_times),
            ):
                data_v = raw.get_data(
                    start=start_sample,
                    stop=stop_sample,
                    picks="eeg",
                )
                epoch_rows.append(
                    epoch_row(
                        window,
                        epoch_index=epoch_index,
                        start_sample=start_sample,
                        stop_sample=stop_sample,
                        sfreq=sfreq,
                        data_v=data_v,
                        channel_names=raw.ch_names,
                        epoch_rejection=epoch_rejection,
                        ica_applied=cleaning_report.ica_applied,
                    )
                )
            print(
                f"  {window['window_id']}: {len(epoch_rows) - before} epochs",
                flush=True,
            )

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in epoch_rows:
        grouped[str(row["window_id"])].append(row)
    summaries = [
        summarize_window(grouped[key], epoch_rejection)
        for key in sorted(grouped)
    ]
    add_baseline_deltas(summaries)
    write_csv(epochs_output, epoch_rows)
    write_csv(summary_output, summaries)
    print(f"Wrote {len(epoch_rows)} epochs to {epochs_output}")
    print(f"Wrote {len(summaries)} window summaries to {summary_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument("--channel-qc", type=Path, default=DEFAULT_CHANNEL_QC)
    parser.add_argument("--epochs-output", type=Path, default=DEFAULT_EPOCHS)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--epoch-seconds", type=float, default=4.0)
    parser.add_argument(
        "--policy",
        type=Path,
        default=SIGNAL_DIR / "cleaning_policy.json",
    )
    parser.add_argument(
        "--subjects",
        nargs="+",
        help="Optional subject IDs, for example: lab_subject_1 lab_subject_8",
    )
    args = parser.parse_args()
    build(
        windows_path=args.windows,
        channel_qc_path=args.channel_qc,
        epochs_output=args.epochs_output,
        summary_output=args.summary_output,
        epoch_seconds=args.epoch_seconds,
        subjects=set(args.subjects) if args.subjects else None,
        policy_path=args.policy,
    )


if __name__ == "__main__":
    main()
