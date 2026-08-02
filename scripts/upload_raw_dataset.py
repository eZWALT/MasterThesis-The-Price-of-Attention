#!/usr/bin/env python3
"""Upload tracked subject exports and lab XDF recordings to Hugging Face."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from huggingface_hub import CommitOperationAdd, HfApi
from huggingface_hub.errors import HfHubHTTPError


DEFAULT_REPO_ID = "eZWALT/Price-of-Attention-RAW"
DEFAULT_TRACKED_DIR = (
    Path(__file__).resolve().parent.parent / "src" / "project" / "logs" / "tracked"
)
STUDY_TYPES = ("beta", "crowd", "lab")


class UploadValidationError(ValueError):
    """Raised when local inputs are not safe to upload."""


@dataclass(frozen=True)
class UploadFile:
    source: Path
    destination: str
    study_type: str
    subject: str
    kind: str

    @property
    def size(self) -> int:
        return self.source.stat().st_size


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Upload tracked subject export JSONL files and lab XDF recordings "
            "to a private Hugging Face dataset repository. The default mode is "
            "a local-only dry run."
        )
    )
    parser.add_argument(
        "--tracked-dir",
        type=Path,
        default=DEFAULT_TRACKED_DIR,
        help=f"Tracked logs root (default: {DEFAULT_TRACKED_DIR})",
    )
    parser.add_argument(
        "--xdf-dir",
        type=Path,
        help=(
            "XDF root containing one directory per exact lab subject name, "
            "for example <xdf-dir>/lab_subject_18/*.xdf"
        ),
    )
    parser.add_argument(
        "--study-type",
        action="append",
        choices=STUDY_TYPES,
        dest="study_types",
        help=(
            "Upload only this study type; repeat the option to select multiple "
            "(default: beta, crowd, and lab)"
        ),
    )
    parser.add_argument(
        "--repo-id",
        default=DEFAULT_REPO_ID,
        help=f"Destination Hugging Face dataset repository (default: {DEFAULT_REPO_ID})",
    )
    parser.add_argument(
        "--commit-message",
        default="Upload raw subject logs and lab recordings",
        help="Commit message used with --exec",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_false",
        dest="execute",
        help="Validate inputs and preview every upload without network writes (default)",
    )
    mode.add_argument(
        "--exec",
        action="store_true",
        dest="execute",
        help="Perform the upload after showing the same preview",
    )
    parser.set_defaults(execute=False)
    return parser.parse_args()


def find_exports(subject_dir: Path) -> list[Path]:
    exports = set(subject_dir.glob("*_export.jsonl"))
    legacy_export = subject_dir / "export.jsonl"
    if legacy_export.is_file():
        exports.add(legacy_export)
    return sorted(path for path in exports if path.is_file())


def find_xdf_files(subject_xdf_dir: Path) -> list[Path]:
    if not subject_xdf_dir.is_dir():
        return []
    return sorted(
        path
        for path in subject_xdf_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".xdf"
    )


def validate_jsonl(path: Path) -> None:
    records = 0
    line_number = 0
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                records += 1
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise UploadValidationError(
                        f"{path}:{line_number} is not a JSON object"
                    )
    except (OSError, UnicodeError) as exc:
        raise UploadValidationError(f"Cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise UploadValidationError(
            f"{path}:{line_number} contains invalid JSON: {exc.msg}"
        ) from exc

    if records == 0:
        raise UploadValidationError(f"{path} contains no JSON records")


def discover_uploads(
    tracked_dir: Path,
    xdf_dir: Path | None,
    study_types: Iterable[str] = STUDY_TYPES,
) -> tuple[list[UploadFile], list[str]]:
    tracked_dir = tracked_dir.expanduser().resolve()
    if not tracked_dir.is_dir():
        raise UploadValidationError(f"Tracked logs directory does not exist: {tracked_dir}")

    xdf_root = xdf_dir.expanduser().resolve() if xdf_dir else None
    uploads: list[UploadFile] = []
    warnings: list[str] = []
    subjects_found = 0

    selected_study_types = tuple(dict.fromkeys(study_types))
    if not selected_study_types:
        raise UploadValidationError("At least one study type must be selected")

    for study_type in selected_study_types:
        study_dir = tracked_dir / study_type
        if not study_dir.is_dir():
            warnings.append(f"Study directory is absent and will be skipped: {study_dir}")
            continue

        for subject_dir in sorted(path for path in study_dir.iterdir() if path.is_dir()):
            subjects_found += 1
            subject = subject_dir.name
            exports = find_exports(subject_dir)

            if not exports:
                message = f"No export JSONL found for {study_type}/{subject}"
                if study_type == "lab":
                    raise UploadValidationError(message)
                warnings.append(f"{message}; subject will be skipped")
                continue

            for export in exports:
                validate_jsonl(export)
                uploads.append(
                    UploadFile(
                        source=export,
                        destination=f"data/{study_type}/{subject}/{export.name}",
                        study_type=study_type,
                        subject=subject,
                        kind="jsonl",
                    )
                )

            if study_type == "lab":
                if xdf_root is None:
                    raise UploadValidationError(
                        "Lab subjects were found, so --xdf-dir is required"
                    )
                subject_xdf_dir = xdf_root / subject
                xdf_files = find_xdf_files(subject_xdf_dir)
                if not xdf_files:
                    raise UploadValidationError(
                        f"No XDF recording found for {subject} in {subject_xdf_dir}"
                    )
                for xdf_file in xdf_files:
                    uploads.append(
                        UploadFile(
                            source=xdf_file,
                            destination=(
                                f"data/lab/{subject}/xdf/{xdf_file.name}"
                            ),
                            study_type=study_type,
                            subject=subject,
                            kind="xdf",
                        )
                    )

    if subjects_found == 0:
        raise UploadValidationError(f"No subject directories found under {tracked_dir}")
    if not uploads:
        raise UploadValidationError("No files are eligible for upload")

    ensure_unique_destinations(uploads)
    return uploads, warnings


def ensure_unique_destinations(uploads: Iterable[UploadFile]) -> None:
    destinations: dict[str, Path] = {}
    for upload in uploads:
        previous = destinations.get(upload.destination)
        if previous is not None:
            raise UploadValidationError(
                f"Destination collision for {upload.destination}: "
                f"{previous} and {upload.source}"
            )
        destinations[upload.destination] = upload.source


def print_preview(
    uploads: list[UploadFile], warnings: list[str], repo_id: str, execute: bool
) -> None:
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    subjects = {(item.study_type, item.subject) for item in uploads}
    jsonl_count = sum(item.kind == "jsonl" for item in uploads)
    xdf_count = sum(item.kind == "xdf" for item in uploads)
    total_bytes = sum(item.size for item in uploads)

    print("=== Hugging Face RAW Dataset Upload ===")
    print(f"Repository: {repo_id}")
    print(f"Mode:       {'exec' if execute else 'dry-run'}")
    print("")
    for item in uploads:
        print(f"  {item.source} -> {item.destination}")
    print("")
    print(
        f"Summary: {len(subjects)} subjects, {jsonl_count} JSONL files, "
        f"{xdf_count} XDF files, {format_bytes(total_bytes)} total"
    )


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.2f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def upload(
    uploads: list[UploadFile], repo_id: str, commit_message: str
) -> str:
    token = os.environ.get("HF_TOKEN") or None
    api = HfApi(token=token)

    try:
        api.whoami()
        repo_info = api.repo_info(repo_id=repo_id, repo_type="dataset")
    except HfHubHTTPError as exc:
        raise RuntimeError(
            "Hugging Face authentication or repository lookup failed. Set HF_TOKEN "
            "or run `hf auth login`, and confirm access to "
            f"https://huggingface.co/datasets/{repo_id}."
        ) from exc

    if repo_info.private is not True:
        raise RuntimeError(
            f"Refusing to upload because dataset repository {repo_id} is not private"
        )

    operations = [
        CommitOperationAdd(
            path_in_repo=item.destination,
            path_or_fileobj=item.source,
        )
        for item in uploads
    ]
    try:
        commit_info = api.create_commit(
            repo_id=repo_id,
            repo_type="dataset",
            operations=operations,
            commit_message=commit_message,
        )
        remote_files = set(
            api.list_repo_files(
                repo_id=repo_id,
                repo_type="dataset",
                revision=commit_info.oid,
            )
        )
    except HfHubHTTPError as exc:
        raise RuntimeError(f"Hugging Face upload failed: {exc}") from exc

    missing = sorted(
        item.destination for item in uploads if item.destination not in remote_files
    )
    if missing:
        preview = ", ".join(missing[:5])
        remainder = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
        raise RuntimeError(
            f"Post-upload verification could not find: {preview}{remainder}"
        )

    return str(commit_info.commit_url)


def main() -> int:
    args = parse_args()
    try:
        uploads, warnings = discover_uploads(
            args.tracked_dir,
            args.xdf_dir,
            args.study_types or STUDY_TYPES,
        )
        print_preview(uploads, warnings, args.repo_id, args.execute)
        if not args.execute:
            print("")
            print("Dry run complete. Add --exec to upload.")
            return 0

        commit_url = upload(uploads, args.repo_id, args.commit_message)
    except (UploadValidationError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("")
    print(f"Upload verified: {commit_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
