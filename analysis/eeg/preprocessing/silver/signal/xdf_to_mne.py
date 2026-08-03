"""Convert one immutable XDF recording to an in-memory MNE Raw object.

The adapter reads the primary EEG stream and attaches the Silver canonical marker
table. It does not clean, resample, rereference, or modify the source XDF.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import mne
import numpy as np
import pyxdf


MICROVOLT_UNITS = {
    "microvolt",
    "microvolts",
    "microvolt(s)",
    "uv",
    "µv",
}
VOLT_UNITS = {"v", "volt", "volts"}


@dataclass(frozen=True)
class XdfMneReport:
    source_xdf: str
    eeg_stream_name: str
    manufacturer: str
    channel_count: int
    channel_names: tuple[str, ...]
    source_units: tuple[str, ...]
    mne_unit: str
    scale_to_volts: float
    sample_count: int
    nominal_srate_hz: float
    effective_srate_hz: float
    timestamp_median_step_s: float
    timestamp_p95_jitter_s: float
    duration_s: float
    eeg_start_lsl: float
    eeg_end_lsl: float
    montage: str
    montage_missing_channels: tuple[str, ...]
    canonical_annotation_count: int
    first_annotation_s: float | None
    last_annotation_s: float | None
    annotation_max_nearest_sample_error_s: float | None
    annotation_max_regularization_shift_s: float | None
    acquisition_reference: str


def _first(value: Any, default: Any = "") -> Any:
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def _stream_name(stream: dict[str, Any]) -> str:
    return str(_first((stream.get("info") or {}).get("name"), ""))


def _channel_metadata(stream: dict[str, Any]) -> list[dict[str, Any]]:
    info = stream.get("info") or {}
    desc = _first(info.get("desc"), {}) or {}
    channels = _first(desc.get("channels"), {}) or {}
    return list(channels.get("channel") or [])


def _unit_scale(units: list[str]) -> float:
    normalized = {unit.strip().lower() for unit in units}
    if normalized and normalized <= MICROVOLT_UNITS:
        return 1e-6
    if normalized and normalized <= VOLT_UNITS:
        return 1.0
    raise ValueError(
        "Unsupported or mixed EEG units: "
        f"{sorted(normalized)}. Scaling must never be guessed."
    )


def _select_primary_eeg(streams: list[dict[str, Any]]) -> dict[str, Any]:
    eeg_streams = [
        stream
        for stream in streams
        if str(_first((stream.get("info") or {}).get("type"), "")).lower()
        == "eeg"
    ]
    if not eeg_streams:
        raise ValueError("XDF contains no EEG stream")
    return max(
        eeg_streams,
        key=lambda stream: len(stream.get("time_stamps", [])),
    )


def _canonical_annotations(
    path: Path,
    *,
    eeg_timestamps: np.ndarray,
    nominal_srate_hz: float,
) -> tuple[mne.Annotations, list[float], list[float], list[float]]:
    onsets: list[float] = []
    descriptions: list[str] = []
    nearest_sample_errors: list[float] = []
    regularization_shifts: list[float] = []
    raw_duration_s = (len(eeg_timestamps) - 1) / nominal_srate_hz
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("event_timing_eligible") != "yes":
                continue
            timestamp_text = row.get("xdf_timestamp_lsl", "")
            if not timestamp_text:
                continue
            marker_timestamp = float(timestamp_text)
            insertion = int(np.searchsorted(eeg_timestamps, marker_timestamp))
            candidates = [
                index
                for index in (insertion - 1, insertion)
                if 0 <= index < len(eeg_timestamps)
            ]
            sample_index = min(
                candidates,
                key=lambda index: abs(
                    eeg_timestamps[index] - marker_timestamp
                ),
            )
            onset = sample_index / nominal_srate_hz
            if onset < 0 or onset > raw_duration_s:
                raise ValueError(
                    f"Canonical marker outside MNE span: {row.get('event')} "
                    f"at {onset:.6f}s, duration {raw_duration_s:.6f}s"
                )
            onsets.append(onset)
            descriptions.append(str(row.get("event", "")))
            nearest_sample_errors.append(
                float(eeg_timestamps[sample_index] - marker_timestamp)
            )
            regularization_shifts.append(
                float(
                    onset
                    - (marker_timestamp - float(eeg_timestamps[0]))
                )
            )
    annotations = mne.Annotations(
        onset=onsets,
        duration=[0.0] * len(onsets),
        description=descriptions,
    )
    return (
        annotations,
        onsets,
        nearest_sample_errors,
        regularization_shifts,
    )


def load_xdf_as_mne(
    xdf_path: Path,
    *,
    canonical_markers_path: Path | None = None,
    montage_name: str = "standard_1020",
    acquisition_reference: str = "unknown",
) -> tuple[mne.io.RawArray, XdfMneReport]:
    """Load XDF EEG samples as volts and attach eligible canonical annotations."""
    streams, _ = pyxdf.load_xdf(str(xdf_path), verbose=False)
    eeg = _select_primary_eeg(streams)
    info = eeg.get("info") or {}
    channel_count = int(_first(info.get("channel_count"), 0))
    nominal_srate = float(_first(info.get("nominal_srate"), 0.0))
    if channel_count <= 0 or nominal_srate <= 0:
        raise ValueError("EEG stream has invalid channel count or sampling rate")

    channels = _channel_metadata(eeg)
    if len(channels) != channel_count:
        raise ValueError(
            f"Expected {channel_count} channel metadata rows, found {len(channels)}"
        )
    names = [str(_first(channel.get("label"), "")) for channel in channels]
    units = [str(_first(channel.get("unit"), "")) for channel in channels]
    types = [
        str(_first(channel.get("type"), "EEG")).strip().lower()
        for channel in channels
    ]
    if not all(names) or len(set(names)) != len(names):
        raise ValueError("EEG channel names are blank or duplicated")
    if any(channel_type != "eeg" for channel_type in types):
        raise ValueError(f"Unexpected channel types in EEG stream: {sorted(set(types))}")

    timestamps = np.asarray(eeg.get("time_stamps", []), dtype=float)
    samples = np.asarray(eeg.get("time_series", []), dtype=float)
    if samples.ndim != 2:
        raise ValueError(f"Expected 2D EEG samples, got shape {samples.shape}")
    if samples.shape == (len(timestamps), channel_count):
        samples = samples.T
    elif samples.shape != (channel_count, len(timestamps)):
        raise ValueError(
            "EEG sample shape does not match timestamps/channels: "
            f"{samples.shape}, {len(timestamps)}, {channel_count}"
        )
    if len(timestamps) < 2 or not np.all(np.diff(timestamps) > 0):
        raise ValueError("EEG timestamps are missing or non-monotonic")

    scale = _unit_scale(units)
    samples_volts = samples * scale
    mne_info = mne.create_info(
        ch_names=names,
        sfreq=nominal_srate,
        ch_types=["eeg"] * channel_count,
    )
    raw = mne.io.RawArray(samples_volts, mne_info, verbose=False)

    montage = mne.channels.make_standard_montage(montage_name)
    montage_lookup = {name.lower() for name in montage.ch_names}
    missing_montage = tuple(name for name in names if name.lower() not in montage_lookup)
    if missing_montage:
        raise ValueError(
            f"{montage_name} lacks recorded channels: {missing_montage}"
        )
    raw.set_montage(montage, match_case=False, on_missing="raise", verbose=False)

    raw_duration = float(raw.times[-1])
    annotation_onsets: list[float] = []
    nearest_sample_errors: list[float] = []
    regularization_shifts: list[float] = []
    if canonical_markers_path is not None:
        (
            annotations,
            annotation_onsets,
            nearest_sample_errors,
            regularization_shifts,
        ) = _canonical_annotations(
            canonical_markers_path,
            eeg_timestamps=timestamps,
            nominal_srate_hz=nominal_srate,
        )
        raw.set_annotations(annotations, verbose=False)

    steps = np.diff(timestamps)
    median_step = float(np.median(steps))
    effective_srate = 1.0 / median_step
    jitter = np.abs(steps - median_step)
    desc = _first(info.get("desc"), {}) or {}
    acquisition = _first(desc.get("acquisition"), {}) or {}
    manufacturer = str(_first(acquisition.get("manufacturer"), ""))

    report = XdfMneReport(
        source_xdf=str(xdf_path),
        eeg_stream_name=_stream_name(eeg),
        manufacturer=manufacturer,
        channel_count=channel_count,
        channel_names=tuple(names),
        source_units=tuple(units),
        mne_unit="volts",
        scale_to_volts=scale,
        sample_count=samples.shape[1],
        nominal_srate_hz=nominal_srate,
        effective_srate_hz=effective_srate,
        timestamp_median_step_s=median_step,
        timestamp_p95_jitter_s=float(np.percentile(jitter, 95)),
        duration_s=float(timestamps[-1] - timestamps[0]),
        eeg_start_lsl=float(timestamps[0]),
        eeg_end_lsl=float(timestamps[-1]),
        montage=montage_name,
        montage_missing_channels=missing_montage,
        canonical_annotation_count=len(annotation_onsets),
        first_annotation_s=min(annotation_onsets) if annotation_onsets else None,
        last_annotation_s=max(annotation_onsets) if annotation_onsets else None,
        annotation_max_nearest_sample_error_s=(
            max(abs(value) for value in nearest_sample_errors)
            if nearest_sample_errors
            else None
        ),
        annotation_max_regularization_shift_s=(
            max(abs(value) for value in regularization_shifts)
            if regularization_shifts
            else None
        ),
        acquisition_reference=acquisition_reference,
    )
    return raw, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("xdf_path", type=Path)
    parser.add_argument("--canonical-markers", type=Path)
    parser.add_argument("--montage", default="standard_1020")
    parser.add_argument("--acquisition-reference", default="unknown")
    args = parser.parse_args()
    _, report = load_xdf_as_mne(
        args.xdf_path,
        canonical_markers_path=args.canonical_markers,
        montage_name=args.montage,
        acquisition_reference=args.acquisition_reference,
    )
    print(json.dumps(asdict(report), indent=2))


if __name__ == "__main__":
    main()
