"""Apply the deterministic portion of the Silver EEG cleaning policy."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import mne

from xdf_to_mne import load_xdf_as_mne


HERE = Path(__file__).resolve().parent
DEFAULT_POLICY = HERE / "cleaning_policy.json"


@dataclass(frozen=True)
class CleaningReport:
    subject_id: str
    policy_version: str
    source_xdf: str
    bad_channels: tuple[str, ...]
    notch_hz: tuple[float, ...]
    highpass_hz: float
    lowpass_hz: float
    rereference: str
    interpolated_channels: tuple[str, ...]
    ica_applied: bool
    output_channel_count: int
    output_sample_count: int


def load_policy(path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        policy = json.load(handle)
    if policy.get("status") not in {
        "requires_visual_validation",
        "frozen",
    }:
        raise ValueError(f"Unsupported cleaning policy status: {policy.get('status')}")
    return policy


def reviewed_bad_channels(
    channel_qc_path: Path,
    subject_id: str,
) -> list[str]:
    with channel_qc_path.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["subject_id"] == subject_id
        ]
    if not rows:
        raise ValueError(f"No channel QC rows for {subject_id}")
    return sorted(
        row["channel"]
        for row in rows
        if row["provisional_flag"] == "yes"
    )


def clean_recording(
    *,
    subject_id: str,
    xdf_path: Path,
    canonical_markers_path: Path,
    channel_qc_path: Path,
    policy_path: Path = DEFAULT_POLICY,
) -> tuple[mne.io.BaseRaw, CleaningReport]:
    policy = load_policy(policy_path)
    raw, _ = load_xdf_as_mne(
        xdf_path,
        canonical_markers_path=canonical_markers_path,
        montage_name=policy["input"]["montage"],
        acquisition_reference=policy["input"]["online_reference"],
    )
    audited_bad_channels = reviewed_bad_channels(channel_qc_path, subject_id)
    subject_specific = policy["bad_channel_review"].get(
        "subject_specific_interpolation",
        {},
    )
    bad_channels = sorted(
        set(audited_bad_channels)
        | set(subject_specific.get(subject_id, []))
    )
    unknown = sorted(set(bad_channels) - set(raw.ch_names))
    if unknown:
        raise ValueError(f"QC contains unknown channels for {subject_id}: {unknown}")
    raw.info["bads"] = bad_channels

    filtering = policy["filtering"]
    notch_hz = tuple(float(value) for value in filtering["notch_hz"])
    raw.notch_filter(notch_hz, picks="eeg", verbose=False)
    raw.filter(
        l_freq=float(filtering["highpass_hz"]),
        h_freq=float(filtering["lowpass_hz"]),
        picks="eeg",
        verbose=False,
    )
    raw.set_eeg_reference(
        ref_channels=policy["rereferencing"]["method"],
        projection=False,
        verbose=False,
    )
    if bad_channels:
        raw.interpolate_bads(
            reset_bads=bool(policy["interpolation"]["reset_bad_labels"]),
            method={"eeg": policy["interpolation"]["method"]},
            verbose=False,
        )

    report = CleaningReport(
        subject_id=subject_id,
        policy_version=str(policy["policy_version"]),
        source_xdf=str(xdf_path),
        bad_channels=tuple(bad_channels),
        notch_hz=notch_hz,
        highpass_hz=float(filtering["highpass_hz"]),
        lowpass_hz=float(filtering["lowpass_hz"]),
        rereference=str(policy["rereferencing"]["method"]),
        interpolated_channels=tuple(bad_channels),
        ica_applied=False,
        output_channel_count=int(len(raw.ch_names)),
        output_sample_count=int(raw.n_times),
    )
    return raw, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject-id", required=True)
    parser.add_argument("--xdf", type=Path, required=True)
    parser.add_argument("--canonical-markers", type=Path, required=True)
    parser.add_argument("--channel-qc", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    args = parser.parse_args()
    _, report = clean_recording(
        subject_id=args.subject_id,
        xdf_path=args.xdf,
        canonical_markers_path=args.canonical_markers,
        channel_qc_path=args.channel_qc,
        policy_path=args.policy,
    )
    print(json.dumps(asdict(report), indent=2))


if __name__ == "__main__":
    main()
