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
from channel_sets import (  # noqa: E402
    ChannelSetPolicy,
    assert_output_allowed,
    channel_indices,
    lookup_names,
    mean_over,
    rejection_channel_spec,
    require_ready,
    reroute_if_default,
    resolve_channel_set,
    suggested_sensitivity_dir,
)


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
    channel_set: ChannelSetPolicy | Path | None = None,
) -> dict[str, float]:
    policy = resolve_channel_set(channel_set)
    require_ready(policy)
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
        name: band_integral(psd, frequencies, band.low_hz, band.high_hz)
        for name, band in policy.bands.items()
    }
    total_per_channel = band_integral(psd, frequencies, 0.5, 40.0)
    lookup = lookup_names(channel_names)

    features: dict[str, float] = {}
    for name, band in policy.bands.items():
        regional_power = mean_over(
            powers[name],
            band.channels,
            lookup,
            field=f"{name} power",
        )
        regional_total = mean_over(
            total_per_channel,
            band.channels,
            lookup,
            field=f"{name} relative total",
        )
        features[f"{name}_power_db_uv2"] = safe_db_uv2(regional_power)
        features[f"{name}_relative_power"] = (
            regional_power / regional_total if regional_total > 0 else math.nan
        )

    features["fz_theta_power_db_uv2"] = safe_db_uv2(
        mean_over(
            powers["theta"],
            policy.fz_theta_channels,
            lookup,
            field="Fz theta",
        )
    )
    features["posterior_alpha_power_db_uv2"] = safe_db_uv2(
        mean_over(
            powers["alpha"],
            policy.posterior_alpha_channels,
            lookup,
            field="posterior alpha",
        )
    )
    left_alpha = mean_over(
        powers["alpha"],
        policy.faa_left,
        lookup,
        field="FAA left",
    )
    right_alpha = mean_over(
        powers["alpha"],
        policy.faa_right,
        lookup,
        field="FAA right",
    )
    features["faa_log_f4_minus_f3"] = math.log(
        max(right_alpha, np.finfo(float).tiny)
    ) - math.log(max(left_alpha, np.finfo(float).tiny))

    alpha = mean_over(
        powers["alpha"],
        policy.pope_global_channels,
        lookup,
        field="Pope global alpha",
    )
    theta = mean_over(
        powers["theta"],
        policy.pope_global_channels,
        lookup,
        field="Pope global theta",
    )
    beta = mean_over(
        powers["beta"],
        policy.pope_global_channels,
        lookup,
        field="Pope global beta",
    )
    denominator = alpha + theta
    features["engagement_beta_over_alpha_theta"] = (
        beta / denominator if denominator > 0 else math.nan
    )
    frontocentral_alpha = mean_over(
        powers["alpha"],
        policy.pope_frontocentral_channels,
        lookup,
        field="Pope frontocentral alpha",
    )
    frontocentral_theta = mean_over(
        powers["theta"],
        policy.pope_frontocentral_channels,
        lookup,
        field="Pope frontocentral theta",
    )
    frontocentral_beta = mean_over(
        powers["beta"],
        policy.pope_frontocentral_channels,
        lookup,
        field="Pope frontocentral beta",
    )
    features["engagement_pope_frontocentral_beta_over_alpha_theta"] = (
        frontocentral_beta / (frontocentral_alpha + frontocentral_theta)
    )

    alpha_8_12 = band_integral(
        psd,
        frequencies,
        policy.kislov_alpha_hz[0],
        policy.kislov_alpha_hz[1],
    )
    beta_16_24 = band_integral(
        psd,
        frequencies,
        policy.kislov_beta_hz[0],
        policy.kislov_beta_hz[1],
    )
    central_alpha = mean_over(
        alpha_8_12,
        policy.kislov_channels,
        lookup,
        field="Kislov alpha",
    )
    central_beta = mean_over(
        beta_16_24,
        policy.kislov_channels,
        lookup,
        field="Kislov beta",
    )
    features["engagement_kislov_central_beta16_24_over_alpha8_12"] = (
        central_beta / central_alpha
    )
    return features


def quality_features(
    data_v: np.ndarray,
    channel_names: list[str],
    rejection_channels: str | tuple[str, ...] | None = None,
) -> dict[str, float | int | str]:
    data_uv = data_v * 1e6
    peak_to_peak = np.ptp(data_uv, axis=1)
    channel_std = np.std(data_uv, axis=1)
    max_abs_by_channel = np.max(np.abs(data_uv), axis=1)
    channel_lookup = lookup_names(channel_names)
    spec = "all" if rejection_channels is None else rejection_channels
    reject_index = channel_indices_or_all(spec, channel_lookup)
    rejected_ptp = peak_to_peak[reject_index]
    rejected_std = channel_std[reject_index]
    rejected_abs = max_abs_by_channel[reject_index]
    rejected_names = [channel_names[int(index)] for index in reject_index]
    frontal_peak_to_peak = {
        f"{channel.lower()}_peak_to_peak_uv": (
            float(peak_to_peak[channel_lookup[channel.lower()]])
            if channel.lower() in channel_lookup
            else math.nan
        )
        for channel in ("Fp1", "Fp2", "F3", "F4")
    }
    return {
        "max_abs_amplitude_uv": float(np.max(rejected_abs)),
        "max_abs_amplitude_channel": rejected_names[
            int(np.argmax(rejected_abs))
        ],
        "max_peak_to_peak_uv": float(np.max(rejected_ptp)),
        "max_peak_to_peak_channel": rejected_names[int(np.argmax(rejected_ptp))],
        "median_peak_to_peak_uv": float(np.median(rejected_ptp)),
        "max_channel_std_uv": float(np.max(rejected_std)),
        "median_channel_std_uv": float(np.median(rejected_std)),
        "near_flat_channel_count": int(np.count_nonzero(rejected_std < 0.5)),
        **frontal_peak_to_peak,
    }


def channel_indices_or_all(
    spec: str | tuple[str, ...],
    lookup: dict[str, int],
) -> np.ndarray:
    return channel_indices(spec, lookup, field="epoch rejection")


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
    channel_set: ChannelSetPolicy | Path | None = None,
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
    policy = resolve_channel_set(channel_set)
    quality = quality_features(
        data_v,
        channel_names,
        rejection_channels=rejection_channel_spec(policy),
    )
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
    row.update(
        spectral_features(
            data_v,
            sfreq=sfreq,
            channel_names=channel_names,
            channel_set=policy,
        )
    )
    if not policy.is_primary:
        row["channel_set_policy_version"] = policy.policy_version
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
        **(
            {"channel_set_policy_version": first["channel_set_policy_version"]}
            if first.get("channel_set_policy_version")
            else {}
        ),
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
        summary[f"{feature}_mean"] = float(np.mean(np.asarray(values, dtype=float)))
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
                row[f"{feature}_mean_baseline_delta"] = ""
                continue
            row[output_name] = (
                float(row[f"{feature}_median"])
                - float(baseline[f"{feature}_median"])
            )
            row[f"{feature}_mean_baseline_delta"] = (
                float(row[f"{feature}_mean"])
                - float(baseline[f"{feature}_mean"])
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
    from_epochs: Path | None = None,
    channel_set_path: Path | None = None,
) -> None:
    if epoch_seconds < 2.0:
        raise ValueError("Epoch duration must be at least 2 seconds")
    channel_set = resolve_channel_set(channel_set_path)
    require_ready(channel_set)
    target = REPOSITORY_ROOT / suggested_sensitivity_dir(channel_set)
    epochs_output = reroute_if_default(
        channel_set,
        epochs_output,
        DEFAULT_EPOCHS,
        target / "condition_epoch_features.csv",
    )
    summary_output = reroute_if_default(
        channel_set,
        summary_output,
        DEFAULT_SUMMARY,
        target / "condition_features.csv",
    )
    assert_output_allowed(channel_set, epochs_output, summary_output)
    policy = load_policy(policy_path)
    epoch_rejection = policy["epoch_rejection"]
    if not str(epoch_rejection.get("status", "")).startswith("frozen_"):
        raise ValueError("Condition features require frozen epoch rejection")
    if from_epochs is not None:
        epoch_rows = read_csv(from_epochs)
        if subjects is not None:
            epoch_rows = [
                row for row in epoch_rows if row["subject_id"] in subjects
            ]
        if not epoch_rows:
            raise ValueError("No epoch rows selected")
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in epoch_rows:
            grouped[str(row["window_id"])].append(row)
        summaries = [
            summarize_window(grouped[key], epoch_rejection)
            for key in sorted(grouped)
        ]
        add_baseline_deltas(summaries)
        write_csv(summary_output, summaries)
        print(f"Reused {len(epoch_rows)} epochs from {from_epochs}")
        print(f"Wrote {len(summaries)} window summaries to {summary_output}")
        return
    windows = [
        row
        for row in read_csv(windows_path)
        if row["primary_analysis_eligible"] == "yes"
        and row["window_type"] in {"baseline", "condition"}
        and (subjects is None or row["subject_id"] in subjects)
    ]
    if not windows:
        raise ValueError("No eligible windows selected")

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
                        channel_set=channel_set,
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
    parser.add_argument(
        "--from-epochs",
        type=Path,
        help="Re-summarize an existing epoch table without recleaning EEG.",
    )
    parser.add_argument(
        "--channel-set-policy",
        type=Path,
        default=None,
        help=(
            "Optional channel-set JSON. Default is the frozen current_v1 "
            "contract. Non-primary policies cannot write primary Gold."
        ),
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
        from_epochs=args.from_epochs,
        channel_set_path=args.channel_set_policy,
    )


if __name__ == "__main__":
    main()
