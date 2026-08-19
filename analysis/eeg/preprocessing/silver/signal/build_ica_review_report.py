"""Build one human-readable HTML index for all ICA component evidence."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPOSITORY_ROOT = HERE.parents[4]
DEFAULT_REPORT_DIRECTORY = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/ica/candidate_v1/reports"
)
DEFAULT_OUTPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/silver/ica/candidate_v1/ica_review.html"
)


def image_uri(output_path: Path, repository_path: str) -> str:
    target = REPOSITORY_ROOT / repository_path
    return target.relative_to(output_path.parent).as_posix()


def build(report_directory: Path, output_path: Path) -> None:
    reports = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(report_directory.glob("lab_subject_*.json"))
    ]
    if not reports:
        raise ValueError(f"No ICA reports found in {report_directory}")
    sections: list[str] = []
    for report in reports:
        excluded = ", ".join(
            str(value) for value in report["excluded_components"]
        ) or "none"
        images = []
        for label, key in (
            ("Selection evidence", "selection_figure"),
            ("Component topographies", "topography_figure"),
            ("Source and proxy traces", "timecourse_figure"),
            ("Component spectra", "spectrum_figure"),
        ):
            path = report["figures"].get(key)
            if path is None:
                continue
            images.append(
                "<figure>"
                f'<img src="{html.escape(image_uri(output_path, path))}" '
                f'alt="{html.escape(label)}">'
                f"<figcaption>{html.escape(label)}</figcaption>"
                "</figure>"
            )
        sections.append(
            "<section>"
            f"<h2>{html.escape(report['subject_id'])}</h2>"
            "<p>"
            f"Fitted components: {report['fitted_component_count']} · "
            f"Excluded: {html.escape(excluded)} · "
            f"Human signoff: {html.escape(report['human_visual_signoff'])}"
            "</p>"
            '<div class="evidence">'
            + "".join(images)
            + "</div></section>"
        )
    document = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ICA candidate review</title>
<style>
body { font-family: sans-serif; margin: 2rem; color: #202124; }
.notice { max-width: 80rem; padding: 1rem; background: #fff4d6; }
section { border-top: 1px solid #bbb; margin-top: 2rem; padding-top: 1rem; }
.evidence { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }
figure { margin: 0; }
img { width: 100%; border: 1px solid #ddd; }
figcaption { font-size: .9rem; color: #555; }
@media (max-width: 900px) { .evidence { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<h1>ICA candidate component review</h1>
<p class="notice">Human signoff 2026-08-19: all automatic exclusions
approved. ICA is the primary Gold branch. No-ICA remains a mandatory
sensitivity. Do not add exclusions, and do not reverse the primary branch
because some ad tests are significant only under ICA.</p>
""" + "".join(sections) + """
</body>
</html>
"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(f"Wrote {len(reports)} participant sections to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-directory",
        type=Path,
        default=DEFAULT_REPORT_DIRECTORY,
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.report_directory, args.output)


if __name__ == "__main__":
    main()
