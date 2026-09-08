"""Equal-n Dataset A: median the 37 tiles nearest visual onset.

Conversation lengths in this cohort span 37–251 complete 4 s epochs
(median 95). The reported Dataset A cell is the median of the shortest
eligible window so every advertisement condition contributes the same
number of epochs and n=18 is retained.

Does not overwrite Gold ``condition_features.csv`` (whole-window
median). Does not touch ICA. Dataset B is unchanged.

Writes derived cells under
``statistics/outputs/sensitivity/ad_local_epochs/dataset_a/around/k37/``
and the confirmatory Dataset A contrast tables that Results reads.

    python analysis/eeg/statistics/run_equal_n_dataset_a.py
"""

from __future__ import annotations

import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_ad_local_epochs import (  # noqa: E402
    DEFAULT_AD_WINDOWS,
    DEFAULT_EPOCHS,
    index_epochs,
    unique_onsets,
    dataset_a_rows,
)
from build_condition_contrasts import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    ESTIMAND_MARKER,
    K37_ESTIMAND,
    descriptives,
    contrast_tables,
    read_csv,
    write_csv,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
K = 37
BRANCH = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/dataset_a/around/k37"
)
ARCHIVE = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/whole_window_dataset_a"
)
CONTRAST_FILES = (
    "eeg_condition_contrasts.csv",
    "eeg_condition_contrast_scores.csv",
    "eeg_condition_descriptives.csv",
)


def archive_whole_window() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    marker = ARCHIVE / "README.md"
    if not marker.exists():
        marker.write_text(
            "Whole-window Dataset A contrast tables (median over every "
            "retained 4 s tile in the condition). Copied before equal-n "
            "k=37 became the reported Dataset A summary. Gold "
            "`condition_features.csv` is still this aggregation.\n",
            encoding="utf-8",
        )
    for name in CONTRAST_FILES:
        source = DEFAULT_OUTPUT_DIR / name
        dest = ARCHIVE / name
        if source.exists() and not dest.exists():
            shutil.copy2(source, dest)
            print(f"archived {source} -> {dest}")


def run() -> None:
    archive_whole_window()
    epochs = read_csv(DEFAULT_EPOCHS)
    windows = read_csv(DEFAULT_AD_WINDOWS)
    epochs_by_cell = index_epochs(epochs)
    onsets_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for onset in unique_onsets(windows):
        onsets_by_subject[onset["subject_id"]].append(onset)
    rows, coverage = dataset_a_rows(
        epochs_by_cell=epochs_by_cell,
        onsets_by_subject=onsets_by_subject,
        k=K,
        side="around",
    )
    string_rows = [{key: str(value) for key, value in row.items()} for row in rows]
    n_ad = sum(
        1
        for row in coverage
        if row["condition"] != "no_ads" and int(row["n_epochs_selected"]) == K
    )
    n_cells = len(coverage)
    print(
        f"k={K} around: {n_cells} cells, "
        f"{n_ad} advertisement cells with exactly {K} tiles"
    )
    BRANCH.mkdir(parents=True, exist_ok=True)
    write_csv(BRANCH / "condition_features.csv", rows)
    write_csv(BRANCH / "coverage.csv", coverage)
    descriptive_rows = descriptives(string_rows)
    contrast_rows, score_rows = contrast_tables(string_rows)
    write_csv(BRANCH / "eeg_condition_descriptives.csv", descriptive_rows)
    write_csv(BRANCH / "eeg_condition_contrasts.csv", contrast_rows)
    write_csv(BRANCH / "eeg_condition_contrast_scores.csv", score_rows)
    write_csv(DEFAULT_OUTPUT_DIR / "eeg_condition_descriptives.csv", descriptive_rows)
    write_csv(DEFAULT_OUTPUT_DIR / "eeg_condition_contrasts.csv", contrast_rows)
    write_csv(DEFAULT_OUTPUT_DIR / "eeg_condition_contrast_scores.csv", score_rows)
    ESTIMAND_MARKER.write_text(K37_ESTIMAND + "\n", encoding="utf-8")
    print(f"Wrote {len(descriptive_rows)} descriptive rows")
    print(f"Wrote {len(contrast_rows)} contrast-test rows")
    print(f"Wrote {len(score_rows)} participant contrast scores")


if __name__ == "__main__":
    run()
