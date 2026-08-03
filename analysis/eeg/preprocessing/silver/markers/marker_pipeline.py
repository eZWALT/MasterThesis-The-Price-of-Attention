"""Shared marker alignment and canonicalization logic.

Raw XDF files are read-only inputs. Every derivative is written as a sidecar
table in the silver layer; this module never modifies an XDF.
"""

from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

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


@dataclass(frozen=True)
class LogEvent:
    index: int
    label: str
    timestamp_unix: float
    timestamp_utc: str
    trial_index: int | None
    turn: int | None
    ad_mode: str
    condition: str


@dataclass(frozen=True)
class LogSession:
    subject_id: str
    subject_number: int
    experiment_id: str
    path: Path
    study_type: str
    events: tuple[LogEvent, ...]


@dataclass(frozen=True)
class RawMarker:
    stream_index: int
    stream_name: str
    stream_source_id: str
    sample_index: int
    label: str
    timestamp_lsl: float

    @property
    def marker_id(self) -> tuple[int, int]:
        return (self.stream_index, self.sample_index)


@dataclass(frozen=True)
class XdfMarkerData:
    subject_id: str
    subject_number: int
    path: Path
    markers: tuple[RawMarker, ...]
    marker_stream_count: int
    eeg_start_lsl: float | None
    eeg_end_lsl: float | None


@dataclass(frozen=True)
class ClockFit:
    log_origin: float
    xdf_origin: float
    slope: float
    anchor_count: int
    residuals_s: tuple[float, ...]

    def predict(self, log_timestamp_unix: float) -> float:
        return self.xdf_origin + self.slope * (
            log_timestamp_unix - self.log_origin
        )

    @property
    def rmse_s(self) -> float:
        if not self.residuals_s:
            return math.nan
        residuals = np.asarray(self.residuals_s, dtype=float)
        return float(np.sqrt(np.mean(np.square(residuals))))

    @property
    def median_abs_residual_s(self) -> float:
        if not self.residuals_s:
            return math.nan
        return float(np.median(np.abs(self.residuals_s)))

    @property
    def p95_abs_residual_s(self) -> float:
        if not self.residuals_s:
            return math.nan
        return float(np.percentile(np.abs(self.residuals_s), 95))

    @property
    def max_abs_residual_s(self) -> float:
        if not self.residuals_s:
            return math.nan
        return float(np.max(np.abs(self.residuals_s)))


@dataclass(frozen=True)
class Alignment:
    fit: ClockFit | None
    matches: dict[int, RawMarker]


def first(value: Any, default: Any = "") -> Any:
    if isinstance(value, list):
        return value[0] if value else default
    return value if value is not None else default


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def marker_value(sample: Any) -> str:
    if isinstance(sample, np.ndarray):
        sample = sample.tolist()
    if isinstance(sample, (list, tuple)):
        sample = sample[0] if sample else ""
    if isinstance(sample, bytes):
        sample = sample.decode("utf-8", errors="replace")
    return str(sample)


def is_lsl_event(label: str) -> bool:
    return label in LSL_EVENTS or bool(TURN_EVENT_RE.match(label))


def subject_sort_key(value: str) -> int:
    match = SUBJECT_RE.search(value)
    return int(match.group(1)) if match else 9999


def discover_logs(log_root: Path) -> dict[int, LogSession]:
    if not log_root.is_dir():
        raise FileNotFoundError(f"Log root does not exist: {log_root}")
    sessions: dict[int, LogSession] = {}
    for directory in sorted(log_root.glob("lab_subject*")):
        match = SUBJECT_RE.search(directory.name)
        if not match:
            continue
        candidates = sorted(directory.glob("*_export.jsonl"))
        if not candidates:
            candidates = sorted(directory.glob("*_events.jsonl"))
        if not candidates:
            continue

        source_path = candidates[0]
        raw_events: list[dict[str, Any]] = []
        with source_path.open(encoding="utf-8", errors="replace") as handle:
            for line_number, line in enumerate(handle, start=1):
                try:
                    raw_events.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"{source_path}:{line_number}: invalid JSON: {exc}"
                    ) from exc

        marker_events: list[LogEvent] = []
        for raw in raw_events:
            label = str(raw.get("event", ""))
            timestamp = raw.get("timestamp")
            if not timestamp or not is_lsl_event(label):
                continue
            data = raw.get("data") or {}
            marker_events.append(
                LogEvent(
                    index=len(marker_events),
                    label=label,
                    timestamp_unix=parse_datetime(str(timestamp)).timestamp(),
                    timestamp_utc=parse_datetime(str(timestamp)).isoformat(),
                    trial_index=_optional_int(raw.get("trial_index")),
                    turn=_optional_int(raw.get("turn")),
                    ad_mode=str(raw.get("ad_mode", "")),
                    condition=str(
                        data.get("condition")
                        or raw.get("condition")
                        or raw.get("ad_mode")
                        or ""
                    ),
                )
            )

        started = next(
            (item for item in raw_events if item.get("event") == "session_started"),
            {},
        )
        subject_number = int(match.group(1))
        sessions[subject_number] = LogSession(
            subject_id=directory.name,
            subject_number=subject_number,
            experiment_id=str(
                raw_events[0].get("experiment_id", source_path.stem)
                if raw_events
                else source_path.stem
            ),
            path=source_path,
            study_type=str((started.get("data") or {}).get("study_type", "")),
            events=tuple(marker_events),
        )
    if not sessions:
        raise ValueError(f"No production log sessions found under {log_root}")
    return sessions


def discover_xdfs(bronze_root: Path) -> dict[int, Path]:
    if not bronze_root.is_dir():
        raise FileNotFoundError(f"Bronze root does not exist: {bronze_root}")
    recordings: dict[int, Path] = {}
    for path in sorted(bronze_root.rglob("*.xdf")):
        if "_old" in path.name:
            continue
        folder_match = SUBJECT_RE.search(path.parent.name)
        filename_match = XDF_SUBJECT_RE.search(path.name)
        number = (
            int(folder_match.group(1))
            if folder_match
            else int(filename_match.group(1))
            if filename_match
            else None
        )
        if number is None:
            continue
        if number in recordings:
            raise ValueError(
                f"Multiple current XDF files for lab_subject_{number}: "
                f"{recordings[number]} and {path}"
            )
        recordings[number] = path
    if not recordings:
        raise ValueError(f"No current XDF recordings found under {bronze_root}")
    return recordings


def load_xdf_markers(path: Path) -> XdfMarkerData:
    folder_match = SUBJECT_RE.search(path.parent.name)
    filename_match = XDF_SUBJECT_RE.search(path.name)
    number = (
        int(folder_match.group(1))
        if folder_match
        else int(filename_match.group(1))
        if filename_match
        else None
    )
    if number is None:
        raise ValueError(f"Cannot infer subject from {path}")

    streams, _ = pyxdf.load_xdf(str(path), verbose=False)
    eeg_streams: list[dict[str, Any]] = []
    marker_streams: list[tuple[int, dict[str, Any]]] = []
    for stream_index, stream in enumerate(streams):
        info = stream.get("info") or {}
        stream_type = str(first(info.get("type"), "")).lower()
        stream_name = str(first(info.get("name"), ""))
        if stream_type == "eeg":
            eeg_streams.append(stream)
        if stream_type == "markers" or "marker" in stream_name.lower():
            marker_streams.append((stream_index, stream))

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

    markers: list[RawMarker] = []
    for stream_index, stream in marker_streams:
        info = stream.get("info") or {}
        name = str(first(info.get("name"), ""))
        source_id = str(first(info.get("source_id"), ""))
        timestamps = stream.get("time_stamps", [])
        values = stream.get("time_series", [])
        for sample_index, (timestamp, sample) in enumerate(zip(timestamps, values)):
            label = marker_value(sample)
            if not label or label == "dummy_start":
                continue
            markers.append(
                RawMarker(
                    stream_index=stream_index,
                    stream_name=name,
                    stream_source_id=source_id,
                    sample_index=sample_index,
                    label=label,
                    timestamp_lsl=float(timestamp),
                )
            )
    markers.sort(key=lambda item: item.timestamp_lsl)

    return XdfMarkerData(
        subject_id=f"lab_subject_{number}",
        subject_number=number,
        path=path,
        markers=tuple(markers),
        marker_stream_count=len(marker_streams),
        eeg_start_lsl=float(eeg_timestamps[0]) if len(eeg_timestamps) else None,
        eeg_end_lsl=float(eeg_timestamps[-1]) if len(eeg_timestamps) else None,
    )


def fit_alignment(
    log_events: Sequence[LogEvent],
    raw_markers: Sequence[RawMarker],
    *,
    offset_cluster_tolerance_s: float = 0.25,
    initial_match_tolerance_s: float = 1.0,
    final_match_tolerance_s: float = 0.25,
) -> Alignment:
    if len(log_events) < 3 or len(raw_markers) < 3:
        return Alignment(fit=None, matches={})

    log_by_label: dict[str, list[LogEvent]] = defaultdict(list)
    raw_by_label: dict[str, list[RawMarker]] = defaultdict(list)
    for event in log_events:
        log_by_label[event.label].append(event)
    for marker in raw_markers:
        raw_by_label[marker.label].append(marker)

    offset_candidates = [
        marker.timestamp_lsl - event.timestamp_unix
        for label in set(log_by_label) & set(raw_by_label)
        for event in log_by_label[label]
        for marker in raw_by_label[label]
    ]
    if len(offset_candidates) < 3:
        return Alignment(fit=None, matches={})
    offset = _densest_offset(offset_candidates, offset_cluster_tolerance_s)

    initial_matches = _greedy_matches(
        log_events,
        raw_by_label,
        lambda event: event.timestamp_unix + offset,
        initial_match_tolerance_s,
    )
    initial_fit = fit_from_matches(log_events, initial_matches)
    if initial_fit is None:
        return Alignment(fit=None, matches=initial_matches)

    final_matches = _greedy_matches(
        log_events,
        raw_by_label,
        lambda event: initial_fit.predict(event.timestamp_unix),
        final_match_tolerance_s,
    )
    final_fit = fit_from_matches(log_events, final_matches)
    return Alignment(fit=final_fit or initial_fit, matches=final_matches)


def best_session_alignment(
    xdf: XdfMarkerData,
    sessions: Iterable[LogSession],
) -> tuple[LogSession, Alignment]:
    candidates: list[tuple[tuple[float, int, float], LogSession, Alignment]] = []
    for session in sessions:
        alignment = fit_alignment(session.events, xdf.markers)
        fit = alignment.fit
        if fit is None or not session.events:
            continue
        matched_fraction = fit.anchor_count / len(session.events)
        score = (
            matched_fraction,
            fit.anchor_count,
            -fit.p95_abs_residual_s,
        )
        candidates.append((score, session, alignment))
    if not candidates:
        raise ValueError(f"No log session can be aligned to {xdf.path}")
    _, session, alignment = max(candidates, key=lambda item: item[0])
    return session, alignment


def fit_from_matches(
    log_events: Sequence[LogEvent],
    matches: dict[int, RawMarker],
) -> ClockFit | None:
    event_by_index = {event.index: event for event in log_events}
    pairs = [
        (event_by_index[index].timestamp_unix, marker.timestamp_lsl)
        for index, marker in matches.items()
        if index in event_by_index
    ]
    return fit_from_pairs(pairs)


def fit_from_pairs(pairs: Sequence[tuple[float, float]]) -> ClockFit | None:
    if len(pairs) < 3:
        return None
    ordered = sorted(pairs)
    log_times = np.asarray([pair[0] for pair in ordered], dtype=float)
    xdf_times = np.asarray([pair[1] for pair in ordered], dtype=float)
    log_origin = float(log_times[0])
    centered_log = log_times - log_origin
    slope, xdf_origin = np.polyfit(centered_log, xdf_times, deg=1)
    predicted = xdf_origin + slope * centered_log
    residuals = xdf_times - predicted
    return ClockFit(
        log_origin=log_origin,
        xdf_origin=float(xdf_origin),
        slope=float(slope),
        anchor_count=len(ordered),
        residuals_s=tuple(float(item) for item in residuals),
    )


def canonical_rows(
    session: LogSession,
    xdf: XdfMarkerData,
    alignment: Alignment,
    *,
    duplicate_tolerance_s: float = 0.25,
    maximum_eeg_extrapolation_s: float = 30.0,
    extrapolation_uncertainty_rate: float = 0.0001,
) -> list[dict[str, Any]]:
    fit = alignment.fit
    markers_by_label: dict[str, list[RawMarker]] = defaultdict(list)
    for marker in xdf.markers:
        markers_by_label[marker.label].append(marker)
    matched_log_times = [
        event.timestamp_unix
        for event in session.events
        if event.index in alignment.matches
    ]

    rows: list[dict[str, Any]] = []
    for event in session.events:
        selected = alignment.matches.get(event.index)
        predicted = (
            fit.predict(event.timestamp_unix)
            if fit is not None
            else selected.timestamp_lsl
            if selected is not None
            else math.nan
        )
        nearby = (
            [
                marker
                for marker in markers_by_label[event.label]
                if abs(marker.timestamp_lsl - predicted) <= duplicate_tolerance_s
            ]
            if math.isfinite(predicted)
            else []
        )
        timestamp = (
            selected.timestamp_lsl
            if selected is not None
            else predicted
            if fit is not None
            else math.nan
        )
        provenance = "observed" if selected is not None else "derived"
        method = (
            "direct_xdf_marker"
            if selected is not None
            else "participant_affine_projection"
            if fit is not None
            else "unavailable"
        )
        inside_eeg = (
            math.isfinite(timestamp)
            and xdf.eeg_start_lsl is not None
            and xdf.eeg_end_lsl is not None
            and xdf.eeg_start_lsl <= timestamp <= xdf.eeg_end_lsl
        )
        extrapolation_s = (
            max(
                0.0,
                min(matched_log_times) - event.timestamp_unix,
                event.timestamp_unix - max(matched_log_times),
            )
            if matched_log_times and selected is None
            else 0.0
        )
        derived_timing_eligible = (
            fit is not None
            and inside_eeg
            and extrapolation_s <= maximum_eeg_extrapolation_s
        )
        timing_eligible = inside_eeg and (
            selected is not None or derived_timing_eligible
        )
        reconstruction_scope = (
            "observed"
            if selected is not None
            else "eeg_timing"
            if derived_timing_eligible
            else "metadata_only"
            if fit is not None
            else "unavailable"
        )
        rows.append(
            {
                "subject_id": session.subject_id,
                "experiment_id": session.experiment_id,
                "event_index": event.index,
                "event": event.label,
                "trial_index": _blank_none(event.trial_index),
                "turn": _blank_none(event.turn),
                "ad_mode": event.ad_mode,
                "condition": event.condition,
                "log_timestamp_utc": event.timestamp_utc,
                "log_timestamp_unix": _fmt(event.timestamp_unix, 6),
                "xdf_timestamp_lsl": _fmt(timestamp, 6),
                "eeg_offset_s": _fmt(
                    timestamp - xdf.eeg_start_lsl
                    if inside_eeg and xdf.eeg_start_lsl is not None
                    else math.nan,
                    6,
                ),
                "provenance": provenance,
                "reconstruction_method": method,
                "reconstruction_scope": reconstruction_scope,
                "extrapolation_from_observed_span_s": _fmt(
                    extrapolation_s, 6
                ),
                "timing_uncertainty_s": _fmt(
                    0.0
                    if selected is not None
                    else fit.p95_abs_residual_s
                    + extrapolation_s * extrapolation_uncertainty_rate
                    if fit is not None
                    else math.nan,
                    6,
                ),
                "raw_match_count": len(nearby),
                "duplicate_raw_count": max(0, len(nearby) - 1),
                "selected_stream_index": (
                    selected.stream_index if selected is not None else ""
                ),
                "selected_stream_name": (
                    selected.stream_name if selected is not None else ""
                ),
                "selected_stream_source_id": (
                    selected.stream_source_id if selected is not None else ""
                ),
                "selected_sample_index": (
                    selected.sample_index if selected is not None else ""
                ),
                "anchor_count": fit.anchor_count if fit is not None else 0,
                "fit_slope": _fmt(fit.slope if fit is not None else math.nan, 9),
                "fit_rmse_s": _fmt(
                    fit.rmse_s if fit is not None else math.nan, 6
                ),
                "fit_p95_abs_residual_s": _fmt(
                    fit.p95_abs_residual_s if fit is not None else math.nan, 6
                ),
                "fit_max_abs_residual_s": _fmt(
                    fit.max_abs_residual_s if fit is not None else math.nan, 6
                ),
                "inside_eeg_span": "yes" if inside_eeg else "no",
                "event_timing_eligible": (
                    "yes" if timing_eligible else "no"
                ),
                "study_protocol_eligible": (
                    "yes" if session.study_type == "lab" else "no"
                ),
                "primary_analysis_eligible": (
                    "yes"
                    if timing_eligible
                    and session.study_type == "lab"
                    else "no"
                ),
                "source_log": str(session.path),
                "source_xdf": str(xdf.path),
            }
        )
    return rows


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _densest_offset(values: Iterable[float], tolerance_s: float) -> float:
    offsets = np.sort(np.asarray(list(values), dtype=float))
    best_start = 0
    best_end = 1
    start = 0
    for end in range(len(offsets)):
        while offsets[end] - offsets[start] > tolerance_s:
            start += 1
        if end - start + 1 > best_end - best_start:
            best_start, best_end = start, end + 1
    return float(np.median(offsets[best_start:best_end]))


def _greedy_matches(
    log_events: Sequence[LogEvent],
    raw_by_label: dict[str, list[RawMarker]],
    predict: Any,
    tolerance_s: float,
) -> dict[int, RawMarker]:
    used: set[tuple[int, int]] = set()
    matches: dict[int, RawMarker] = {}
    for event in log_events:
        target = float(predict(event))
        candidates = [
            marker
            for marker in raw_by_label.get(event.label, [])
            if marker.marker_id not in used
        ]
        if not candidates:
            continue
        selected = min(
            candidates, key=lambda marker: abs(marker.timestamp_lsl - target)
        )
        if abs(selected.timestamp_lsl - target) <= tolerance_s:
            matches[event.index] = selected
            used.add(selected.marker_id)
    return matches


def _optional_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _blank_none(value: Any) -> Any:
    return "" if value is None else value


def _fmt(value: float, digits: int) -> str:
    if not math.isfinite(float(value)):
        return ""
    return f"{float(value):.{digits}f}"
