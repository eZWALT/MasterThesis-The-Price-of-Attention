"""Create the XDF bronze/silver/gold layout without changing raw bytes."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from marker_pipeline import write_csv


DEFAULT_ROOT = Path("src/project/logs/xdf")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def organize(root: Path, *, apply: bool, include_hashes: bool) -> None:
    bronze = root / "bronze"
    silver = root / "silver"
    gold = root / "gold"
    source_directories = sorted(
        path
        for path in root.glob("lab_subject_*")
        if path.is_dir()
    )

    planned = [(source, bronze / source.name) for source in source_directories]
    for source, destination in planned:
        if destination.exists():
            raise FileExistsError(
                f"Refusing to overwrite existing bronze directory: {destination}"
            )
        print(f"{source} -> {destination}")

    if not apply:
        print("Dry run only. Re-run with --apply to move directories safely.")
        return

    bronze.mkdir(parents=True, exist_ok=True)
    (silver / "audits").mkdir(parents=True, exist_ok=True)
    (silver / "canonical_markers").mkdir(parents=True, exist_ok=True)
    (silver / "validation").mkdir(parents=True, exist_ok=True)
    gold.mkdir(parents=True, exist_ok=True)

    moved: list[tuple[Path, Path]] = []
    try:
        for source, destination in planned:
            source.rename(destination)
            moved.append((source, destination))
    except Exception:
        for source, destination in reversed(moved):
            if destination.exists() and not source.exists():
                destination.rename(source)
        raise

    inventory: list[dict[str, object]] = []
    for path in sorted(bronze.rglob("*.xdf")):
        stat = path.stat()
        inventory.append(
            {
                "relative_path": str(path.relative_to(root)),
                "size_bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(
                    stat.st_mtime, tz=timezone.utc
                ).isoformat(),
                "sha256": sha256(path) if include_hashes else "",
            }
        )
    write_csv(silver / "audits" / "bronze_inventory.csv", inventory)
    print(f"Moved {len(planned)} subject directories into {bronze}")
    print(f"Inventoried {len(inventory)} immutable XDF files")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the displayed moves. Without this flag the command is a dry run.",
    )
    parser.add_argument(
        "--skip-hash",
        action="store_true",
        help="Skip SHA-256 calculation (faster but weaker provenance).",
    )
    args = parser.parse_args()
    organize(args.root, apply=args.apply, include_hashes=not args.skip_hash)


if __name__ == "__main__":
    main()
