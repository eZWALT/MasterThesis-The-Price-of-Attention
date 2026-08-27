"""Build a reviewable lab-log/XDF recording manifest.

The manifest separates objective evidence from initial guesses and leaves explicit
columns for supervisor corrections. It never treats folder numbering as proof of a
mapping.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pyxdf


LSL_EVENTS = {
    "baseline_start",
    "baseline_end",
    "warmup_start",
    "warmup_finish",
    "ad_injected",
    "condition_conclusion_submitted",
    "post_task_questionnaire_end",
    "experiment_end",
    "condition_start",
    "ad_displayed",
}
TURN_EVENT_RE = re.compile(r"^turn_\d+_(?:read|write)$")
SUBJECT_RE = re.compile(r"lab_subject_(\d+)")
XDF_SUBJECT_RE = re.compile(r"sub-P(\d+)", re.IGNORECASE)


@dataclass
class LogSession:
    subject_dir: str
    subject_number: int
    path: Path
    experiment_id: str
    study_type: str
    start_utc: datetime
    end_utc: datetime
    events: list[dict[str, Any]]

    @property
    def duration_s(self) -> float:
        return (self.end_utc - self.start_utc).total_seconds()

    @property
    def lsl_events(self) -> list[tuple[str, float]]:
        result: list[tuple[str, float]] = []
        for event in self.events:
            label = str(event.get("event", ""))
            if label not in LSL_EVENTS and not TURN_EVENT_RE.match(label):
                continue
            timestamp = event.get("timestamp")
            if not timestamp:
                continue
            result.append((label, parse_datetime(timestamp).timestamp()))
        return result


@dataclass
class XdfRecording:
    path: Path
    folder_subject_number: int | None
    filename_subject_number: int | None
    file_size_bytes: int
    header_datetime_utc: datetime | None
    stream_count: int
    eeg_stream_count: int
    marker_stream_count: int
    eeg_names: list[str]
    marker_names: list[str]
    eeg_channels: int | None
    nominal_srate_hz: float | None
    effective_srate_hz: float | None
    eeg_samples: int
    eeg_duration_s: float | None
    eeg_start_lsl: float | None
    eeg_end_lsl: float | None
    marker_samples: int
    marker_duration_s: float | None
    markers: list[tuple[str, float]]
    load_error: str


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def first(value: Any, default: Any = "") -> Any:
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def safe_float(value: Any) -> float | None:
    try:
        number = float(first(value))
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def safe_int(value: Any) -> int | None:
    try:
        return int(first(value))
    except (TypeError, ValueError):
        return None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return events


def discover_logs(log_root: Path) -> list[LogSession]:
    sessions: list[LogSession] = []
    for directory in sorted(log_root.glob("lab_subject*")):
        match = SUBJECT_RE.search(directory.name)
        if not match:
            continue
        candidates = sorted(directory.glob("*_export.jsonl"))
        if not candidates:
            candidates = sorted(directory.glob("*_events.jsonl"))
        if not candidates:
            continue
        path = candidates[0]
        events = load_jsonl(path)
        timestamps = [
            parse_datetime(str(event["timestamp"]))
            for event in events
            if event.get("timestamp")
        ]
        if not timestamps:
            continue
        session_started = next(
            (event for event in events if event.get("event") == "session_started"),
            {},
        )
        data = session_started.get("data") or {}
        sessions.append(
            LogSession(
                subject_dir=directory.name,
                subject_number=int(match.group(1)),
                path=path,
                experiment_id=str(
                    events[0].get("experiment_id", path.name.split("_events")[0])
                ),
                study_type=str(data.get("study_type", "")),
                start_utc=min(timestamps),
                end_utc=max(timestamps),
                events=events,
            )
        )
    return sessions


def marker_value(sample: Any) -> str:
    if isinstance(sample, np.ndarray):
        sample = sample.tolist()
    if isinstance(sample, (list, tuple)):
        sample = sample[0] if sample else ""
    if isinstance(sample, bytes):
        sample = sample.decode("utf-8", errors="replace")
    return str(sample)


def load_xdf(path: Path) -> XdfRecording:
    folder_match = SUBJECT_RE.search(path.parent.name)
    filename_match = XDF_SUBJECT_RE.search(path.name)
    folder_subject = int(folder_match.group(1)) if folder_match else None
    filename_subject = int(filename_match.group(1)) if filename_match else None

    try:
        streams, header = pyxdf.load_xdf(str(path), verbose=False)
        header_text = str(first((header.get("info") or {}).get("datetime"), ""))
        header_datetime = parse_datetime(header_text) if header_text else None

        eeg_streams = []
        marker_streams = []
        for stream in streams:
            info = stream.get("info") or {}
            stream_type = str(first(info.get("type"), "")).lower()
            stream_name = str(first(info.get("name"), ""))
            if stream_type == "eeg":
                eeg_streams.append(stream)
            if stream_type == "markers" or "marker" in stream_name.lower():
                marker_streams.append(stream)

        eeg_names = [str(first(stream["info"].get("name"), "")) for stream in eeg_streams]
        marker_names = [
            str(first(stream["info"].get("name"), "")) for stream in marker_streams
        ]

        primary_eeg = max(
            eeg_streams,
            key=lambda stream: len(stream.get("time_stamps", [])),
            default=None,
        )
        eeg_timestamps = (
            np.asarray(primary_eeg.get("time_stamps", []), dtype=float)
            if primary_eeg is not None
            else np.asarray([], dtype=float)
        )
        eeg_info = primary_eeg.get("info", {}) if primary_eeg is not None else {}

        markers: list[tuple[str, float]] = []
        for stream in marker_streams:
            timestamps = stream.get("time_stamps", [])
            values = stream.get("time_series", [])
            for timestamp, sample in zip(timestamps, values):
                label = marker_value(sample)
                if label:
                    markers.append((label, float(timestamp)))
        markers.sort(key=lambda item: item[1])
        non_dummy_markers = [
            item for item in markers if item[0] and item[0] != "dummy_start"
        ]

        marker_duration = None
        if len(non_dummy_markers) >= 2:
            marker_duration = non_dummy_markers[-1][1] - non_dummy_markers[0][1]

        eeg_duration = None
        if len(eeg_timestamps) >= 2:
            eeg_duration = float(eeg_timestamps[-1] - eeg_timestamps[0])

        return XdfRecording(
            path=path,
            folder_subject_number=folder_subject,
            filename_subject_number=filename_subject,
            file_size_bytes=path.stat().st_size,
            header_datetime_utc=header_datetime,
            stream_count=len(streams),
            eeg_stream_count=len(eeg_streams),
            marker_stream_count=len(marker_streams),
            eeg_names=eeg_names,
            marker_names=marker_names,
            eeg_channels=safe_int(eeg_info.get("channel_count")),
            nominal_srate_hz=safe_float(eeg_info.get("nominal_srate")),
            effective_srate_hz=safe_float(eeg_info.get("effective_srate")),
            eeg_samples=len(eeg_timestamps),
            eeg_duration_s=eeg_duration,
            eeg_start_lsl=float(eeg_timestamps[0]) if len(eeg_timestamps) else None,
            eeg_end_lsl=float(eeg_timestamps[-1]) if len(eeg_timestamps) else None,
            marker_samples=len(non_dummy_markers),
            marker_duration_s=marker_duration,
            markers=non_dummy_markers,
            load_error="",
        )
    except Exception as exc:  # Manifest must retain unreadable files for review.
        return XdfRecording(
            path=path,
            folder_subject_number=folder_subject,
            filename_subject_number=filename_subject,
            file_size_bytes=path.stat().st_size,
            header_datetime_utc=None,
            stream_count=0,
            eeg_stream_count=0,
            marker_stream_count=0,
            eeg_names=[],
            marker_names=[],
            eeg_channels=None,
            nominal_srate_hz=None,
            effective_srate_hz=None,
            eeg_samples=0,
            eeg_duration_s=None,
            eeg_start_lsl=None,
            eeg_end_lsl=None,
            marker_samples=0,
            marker_duration_s=None,
            markers=[],
            load_error=f"{type(exc).__name__}: {exc}",
        )


def ordinal_pairs(
    left: Iterable[tuple[str, float]],
    right: Iterable[tuple[str, float]],
) -> tuple[np.ndarray, np.ndarray]:
    left_by_label: dict[str, list[float]] = defaultdict(list)
    right_by_label: dict[str, list[float]] = defaultdict(list)
    for label, timestamp in left:
        left_by_label[label].append(timestamp)
    for label, timestamp in right:
        right_by_label[label].append(timestamp)

    left_values: list[float] = []
    right_values: list[float] = []
    for label in sorted(set(left_by_label) & set(right_by_label)):
        count = min(len(left_by_label[label]), len(right_by_label[label]))
        left_values.extend(left_by_label[label][:count])
        right_values.extend(right_by_label[label][:count])
    return np.asarray(left_values), np.asarray(right_values)


def fit_marker_match(
    recording: XdfRecording,
    session: LogSession,
) -> dict[str, float | int]:
    log_by_label: dict[str, list[float]] = defaultdict(list)
    xdf_by_label: dict[str, list[float]] = defaultdict(list)
    for label, timestamp in session.lsl_events:
        log_by_label[label].append(timestamp)
    for label, timestamp in recording.markers:
        xdf_by_label[label].append(timestamp)

    # Multiple recovered LSL outlets can duplicate or overlap marker sequences in
    # one XDF. Ordinal pairing therefore fails. The true log/XDF pairs instead
    # share an almost constant clock offset; find the densest offset cluster.
    offset_candidates: list[float] = []
    for label in set(log_by_label) & set(xdf_by_label):
        for log_timestamp in log_by_label[label]:
            for xdf_timestamp in xdf_by_label[label]:
                offset_candidates.append(xdf_timestamp - log_timestamp)
    if len(offset_candidates) < 3:
        return {
            "n": len(offset_candidates),
            "slope": math.nan,
            "median_abs_residual_s": math.nan,
            "max_abs_residual_s": math.nan,
        }

    offsets = np.sort(np.asarray(offset_candidates, dtype=float))
    tolerance_s = 0.25
    best_start = 0
    best_end = 1
    start = 0
    for end in range(len(offsets)):
        while offsets[end] - offsets[start] > tolerance_s:
            start += 1
        if end - start + 1 > best_end - best_start:
            best_start, best_end = start, end + 1
    offset = float(np.median(offsets[best_start:best_end]))

    paired_log: list[float] = []
    paired_xdf: list[float] = []
    used: dict[str, set[int]] = defaultdict(set)
    for label, log_timestamp in session.lsl_events:
        candidates = xdf_by_label.get(label, [])
        if not candidates:
            continue
        residuals = [
            abs((xdf_timestamp - log_timestamp) - offset)
            if index not in used[label]
            else math.inf
            for index, xdf_timestamp in enumerate(candidates)
        ]
        index = int(np.argmin(residuals))
        if residuals[index] <= 1.0:
            used[label].add(index)
            paired_log.append(log_timestamp)
            paired_xdf.append(candidates[index])

    n = len(paired_log)
    if n < 3:
        return {
            "n": n,
            "slope": math.nan,
            "median_abs_residual_s": math.nan,
            "max_abs_residual_s": math.nan,
        }

    log_times = np.asarray(paired_log)
    xdf_times = np.asarray(paired_xdf)
    centered_log = log_times - log_times[0]
    centered_xdf = xdf_times - xdf_times[0]
    slope, intercept = np.polyfit(centered_log, centered_xdf, deg=1)
    residuals = centered_xdf - (slope * centered_log + intercept)
    return {
        "n": n,
        "slope": float(slope),
        "median_abs_residual_s": float(np.median(np.abs(residuals))),
        "max_abs_residual_s": float(np.max(np.abs(residuals))),
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if not math.isfinite(value):
            return ""
        return f"{value:.{digits}f}"
    return str(value)


def classify_initial(
    recording: XdfRecording,
    folder_session: LogSession | None,
    best_session: LogSession | None,
    best_fit: dict[str, float | int] | None,
) -> tuple[str, str, str]:
    if recording.load_error:
        return "unreadable", "none", "XDF parser failed"
    if recording.eeg_duration_s is not None and recording.eeg_duration_s < 300:
        return "partial_recording", "low", "EEG duration is under 5 minutes"
    if folder_session and folder_session.study_type != "lab":
        return (
            "wrong_protocol",
            "high",
            "Folder-number candidate ran the crowd protocol and has no lab baseline",
        )
    if recording.marker_samples == 0:
        return "no_anchor", "low", "No non-dummy XDF markers"
    if best_session is None or best_fit is None:
        return "unmapped", "low", "No candidate log match"

    residual = float(best_fit["median_abs_residual_s"])
    n = int(best_fit["n"])
    slope = float(best_fit["slope"])
    same_folder = (
        recording.folder_subject_number is not None
        and recording.folder_subject_number == best_session.subject_number
    )
    if n >= 40 and residual <= 0.25 and abs(slope - 1.0) <= 0.001:
        confidence = "high" if same_folder else "medium"
        if not same_folder:
            return "folder_mismatch", confidence, "Strong markers match another log"
        expected = len(best_session.lsl_events)
        if n < expected:
            return (
                "partial_reconstructable",
                confidence,
                f"Strong timing match but {expected - n} expected markers are unmatched",
            )
        if recording.marker_samples > expected * 1.10:
            return (
                "healthy_with_duplicate_markers",
                confidence,
                "Complete timing match with additional duplicate XDF markers",
            )
        return "healthy", confidence, "Strong complete marker-timing match"
    if n >= 10 and residual <= 2.0 and abs(slope - 1.0) <= 0.01:
        return "partial_reconstructable", "medium", "Usable shared marker anchors"
    return "marker_mismatch", "low", "Marker timing does not cleanly match a log"


def build_rows(
    logs: list[LogSession],
    recordings: list[XdfRecording],
) -> list[dict[str, Any]]:
    logs_by_subject = {session.subject_number: session for session in logs}
    rows: list[dict[str, Any]] = []
    matched_log_subjects: set[int] = set()

    for recording in recordings:
        fits = [(session, fit_marker_match(recording, session)) for session in logs]
        fits.sort(
            key=lambda item: (
                -int(item[1]["n"]),
                float(item[1]["median_abs_residual_s"])
                if math.isfinite(float(item[1]["median_abs_residual_s"]))
                else math.inf,
            )
        )
        best_session, best_fit = fits[0] if fits else (None, None)
        second_session, second_fit = fits[1] if len(fits) > 1 else (None, None)
        folder_session = logs_by_subject.get(recording.folder_subject_number or -1)

        status, confidence, reason = classify_initial(
            recording, folder_session, best_session, best_fit
        )
        initial_session = best_session if confidence in {"high", "medium"} else folder_session
        if initial_session is not None:
            matched_log_subjects.add(initial_session.subject_number)

        marker_counts = Counter(label for label, _ in recording.markers)
        log_counts = Counter(
            label for label, _ in initial_session.lsl_events
        ) if initial_session else Counter()
        common_occurrences = sum(
            min(marker_counts[label], log_counts[label])
            for label in set(marker_counts) & set(log_counts)
        )
        expected_occurrences = sum(log_counts.values())
        coverage = (
            common_occurrences / expected_occurrences if expected_occurrences else None
        )
        markers_inside_eeg = 0
        if recording.eeg_start_lsl is not None and recording.eeg_end_lsl is not None:
            markers_inside_eeg = sum(
                recording.eeg_start_lsl <= timestamp <= recording.eeg_end_lsl
                for _, timestamp in recording.markers
            )
        first_marker_offset = None
        last_marker_margin = None
        if recording.markers and recording.eeg_start_lsl is not None:
            first_marker_offset = recording.markers[0][1] - recording.eeg_start_lsl
        if recording.markers and recording.eeg_end_lsl is not None:
            last_marker_margin = recording.eeg_end_lsl - recording.markers[-1][1]

        rows.append(
            {
                "manifest_row_type": "xdf",
                "xdf_path": str(recording.path),
                "xdf_file_size_bytes": recording.file_size_bytes,
                "xdf_folder_subject_guess": (
                    f"lab_subject_{recording.folder_subject_number}"
                    if recording.folder_subject_number is not None
                    else ""
                ),
                "xdf_filename_subject_guess": (
                    f"lab_subject_{recording.filename_subject_number}"
                    if recording.filename_subject_number is not None
                    else ""
                ),
                "initial_log_subject_guess": (
                    initial_session.subject_dir if initial_session else ""
                ),
                "initial_experiment_id_guess": (
                    initial_session.experiment_id if initial_session else ""
                ),
                "initial_mapping_confidence": confidence,
                "initial_health_guess": status,
                "initial_guess_reason": reason,
                "log_study_type": initial_session.study_type if initial_session else "",
                "log_path": str(initial_session.path) if initial_session else "",
                "log_start_utc": (
                    initial_session.start_utc.isoformat() if initial_session else ""
                ),
                "log_end_utc": (
                    initial_session.end_utc.isoformat() if initial_session else ""
                ),
                "log_duration_s": (
                    fmt(initial_session.duration_s) if initial_session else ""
                ),
                "log_event_count": (
                    len(initial_session.events) if initial_session else ""
                ),
                "log_lsl_event_count": (
                    len(initial_session.lsl_events) if initial_session else ""
                ),
                "log_baseline_start_count": log_counts["baseline_start"],
                "log_baseline_end_count": log_counts["baseline_end"],
                "log_condition_start_count": log_counts["condition_start"],
                "log_ad_injected_count": log_counts["ad_injected"],
                "log_ad_displayed_count": log_counts["ad_displayed"],
                "log_experiment_end_count": log_counts["experiment_end"],
                "xdf_header_datetime_utc": (
                    recording.header_datetime_utc.isoformat()
                    if recording.header_datetime_utc
                    else ""
                ),
                "xdf_stream_count": recording.stream_count,
                "xdf_eeg_stream_count": recording.eeg_stream_count,
                "xdf_marker_stream_count": recording.marker_stream_count,
                "xdf_eeg_stream_names": ";".join(recording.eeg_names),
                "xdf_marker_stream_names": ";".join(recording.marker_names),
                "xdf_eeg_channels": fmt(recording.eeg_channels),
                "xdf_nominal_srate_hz": fmt(recording.nominal_srate_hz),
                "xdf_effective_srate_hz": fmt(recording.effective_srate_hz),
                "xdf_eeg_samples": recording.eeg_samples,
                "xdf_eeg_duration_s": fmt(recording.eeg_duration_s),
                "xdf_marker_samples_non_dummy": recording.marker_samples,
                "xdf_markers_inside_eeg_span": markers_inside_eeg,
                "xdf_marker_fraction_inside_eeg_span": fmt(
                    (
                        markers_inside_eeg / recording.marker_samples
                        if recording.marker_samples
                        else None
                    ),
                    4,
                ),
                "xdf_first_marker_offset_from_eeg_start_s": fmt(
                    first_marker_offset
                ),
                "xdf_last_marker_margin_before_eeg_end_s": fmt(last_marker_margin),
                "xdf_marker_duration_s": fmt(recording.marker_duration_s),
                "xdf_unique_marker_labels": len(marker_counts),
                "xdf_baseline_start_count": marker_counts["baseline_start"],
                "xdf_baseline_end_count": marker_counts["baseline_end"],
                "xdf_condition_start_count": marker_counts["condition_start"],
                "xdf_ad_injected_count": marker_counts["ad_injected"],
                "xdf_ad_displayed_count": marker_counts["ad_displayed"],
                "xdf_experiment_end_count": marker_counts["experiment_end"],
                "marker_coverage_vs_initial_log": fmt(coverage, 4),
                "marker_best_log_match": best_session.subject_dir if best_session else "",
                "marker_best_common_count": best_fit["n"] if best_fit else "",
                "marker_best_slope": fmt(best_fit["slope"], 8) if best_fit else "",
                "marker_best_median_abs_residual_s": (
                    fmt(best_fit["median_abs_residual_s"], 6) if best_fit else ""
                ),
                "marker_best_max_abs_residual_s": (
                    fmt(best_fit["max_abs_residual_s"], 6) if best_fit else ""
                ),
                "marker_second_log_match": (
                    second_session.subject_dir if second_session else ""
                ),
                "marker_second_common_count": second_fit["n"] if second_fit else "",
                "marker_second_median_abs_residual_s": (
                    fmt(second_fit["median_abs_residual_s"], 6) if second_fit else ""
                ),
                "xdf_load_error": recording.load_error,
            }
        )

    xdf_folder_subjects = {
        recording.folder_subject_number
        for recording in recordings
        if recording.folder_subject_number is not None
    }
    for session in logs:
        if session.subject_number in xdf_folder_subjects:
            continue
        counts = Counter(label for label, _ in session.lsl_events)
        rows.append(
            {
                "manifest_row_type": "missing_xdf",
                "xdf_path": "",
                "xdf_file_size_bytes": "",
                "xdf_folder_subject_guess": "",
                "xdf_filename_subject_guess": "",
                "initial_log_subject_guess": session.subject_dir,
                "initial_experiment_id_guess": session.experiment_id,
                "initial_mapping_confidence": "high",
                "initial_health_guess": "missing_xdf",
                "initial_guess_reason": "Production lab log has no XDF folder/file",
                "log_study_type": session.study_type,
                "log_path": str(session.path),
                "log_start_utc": session.start_utc.isoformat(),
                "log_end_utc": session.end_utc.isoformat(),
                "log_duration_s": fmt(session.duration_s),
                "log_event_count": len(session.events),
                "log_lsl_event_count": len(session.lsl_events),
                "log_baseline_start_count": counts["baseline_start"],
                "log_baseline_end_count": counts["baseline_end"],
                "log_condition_start_count": counts["condition_start"],
                "log_ad_injected_count": counts["ad_injected"],
                "log_ad_displayed_count": counts["ad_displayed"],
                "log_experiment_end_count": counts["experiment_end"],
            }
        )
    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def subject_number_from_row(row: dict[str, Any]) -> int:
    for key in (
        "subject_and_xdf",
        "xdf_folder_subject_guess",
        "initial_log_subject_guess",
        "marker_best_log_match",
    ):
        match = SUBJECT_RE.search(str(row.get(key, "")))
        if match:
            return int(match.group(1))
    return 999


def concise_evidence(row: dict[str, Any]) -> str:
    log_minutes = ""
    eeg_minutes = ""
    try:
        log_minutes = f"{float(row.get('log_duration_s', '')) / 60:.1f}"
    except (TypeError, ValueError):
        pass
    try:
        eeg_minutes = f"{float(row.get('xdf_eeg_duration_s', '')) / 60:.1f}"
    except (TypeError, ValueError):
        pass

    if row.get("manifest_row_type") == "missing_xdf":
        return f"log {log_minutes} min; no XDF"

    matched = row.get("marker_best_common_count", "")
    expected = row.get("log_lsl_event_count", "")
    residual = row.get("marker_best_median_abs_residual_s", "")
    duration = (
        f"log/EEG {log_minutes}/{eeg_minutes} min"
        if log_minutes and eeg_minutes
        else f"EEG {eeg_minutes} min"
    )
    marker_text = f"markers {matched}/{expected}"
    if residual:
        marker_text += f"; residual {float(residual):.4f}s"
    return f"{duration}; {marker_text}"


def pipeline_disposition(row: dict[str, Any]) -> str:
    status = str(row.get("initial_health_guess", ""))
    dispositions = {
        "healthy": "Use mapped recording in Silver preprocessing",
        "healthy_with_duplicate_markers": (
            "Use Silver canonical markers; retain raw extras in Bronze"
        ),
        "folder_mismatch": "Resolve mapping before Silver preprocessing",
        "partial_reconstructable": (
            "Use governed Silver reconstruction and event eligibility"
        ),
        "marker_mismatch": "Resolve marker/timestamp mismatch before use",
        "partial_recording": "Locate full recording or exclude",
        "wrong_protocol": "Retain in Bronze; exclude from lab EEG arm",
        "missing_xdf": "Locate recording or record as unavailable",
        "unreadable": "Repair/re-export XDF or exclude",
        "unmapped": "Identify recording before use",
    }
    return dispositions.get(status, "Investigate before use")


def build_summary_rows(evidence_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []
    for row in evidence_rows:
        xdf_path = str(row.get("xdf_path", ""))
        if "_old" in Path(xdf_path).name:
            continue
        folder_subject = str(row.get("xdf_folder_subject_guess", ""))
        log_subject = str(row.get("initial_log_subject_guess", ""))
        subject_label = folder_subject or log_subject
        xdf_name = Path(xdf_path).name if xdf_path else "(missing)"
        summary_rows.append(
            {
                "subject_and_xdf": f"{subject_label} — {xdf_name}",
                "proposed_log_mapping": log_subject,
                "confidence": row.get("initial_mapping_confidence", ""),
                "initial_status": row.get("initial_health_guess", ""),
                "evidence": concise_evidence(row),
                "main_issue": row.get("initial_guess_reason", ""),
                "pipeline_disposition": pipeline_disposition(row),
            }
        )
    summary_rows.sort(key=subject_number_from_row)
    return summary_rows


def write_summary_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log-root",
        type=Path,
        default=Path("src/project/logs/production"),
    )
    parser.add_argument(
        "--xdf-root",
        type=Path,
        default=Path("src/project/logs/xdf/bronze"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "analysis/eeg/preprocessing/bronze/manifests/"
            "eeg_recording_manifest.csv"
        ),
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=Path(
            "analysis/eeg/preprocessing/bronze/manifests/"
            "eeg_recording_evidence.csv"
        ),
    )
    args = parser.parse_args()

    logs = discover_logs(args.log_root)
    xdf_paths = sorted(args.xdf_root.rglob("*.xdf"))
    recordings = [load_xdf(path) for path in xdf_paths]
    evidence_rows = build_rows(logs, recordings)
    summary_rows = build_summary_rows(evidence_rows)
    write_csv(evidence_rows, args.evidence_output)
    write_summary_csv(summary_rows, args.output)

    health_counts = Counter(row["initial_status"] for row in summary_rows)
    print(f"Wrote {len(summary_rows)} summary rows to {args.output}")
    print(f"Wrote {len(evidence_rows)} evidence rows to {args.evidence_output}")
    for status, count in sorted(health_counts.items()):
        print(f"  {status}: {count}")


if __name__ == "__main__":
    main()
