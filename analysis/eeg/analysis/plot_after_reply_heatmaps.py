"""After-reply Path B heatmaps. Writes only under heatmaps/after_reply/."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from plot_eeg_only_heatmaps import (  # noqa: E402
    CMAP,
    FEATURES,
    INK,
    PATH_A,
    PATH_B,
    SLATE,
    WIDTHS,
    draw,
    matrix,
    style,
)


ROOT = Path(__file__).resolve().parents[3]
GOLDEN_GRID = ROOT / (
    "analysis/eeg/statistics/outputs/sensitivity/epoch_length_grid_comparison.csv"
)
AFTER_GRID = ROOT / (
    "analysis/eeg/statistics/outputs/sensitivity/after_reply/"
    "after_reply_grid_comparison.csv"
)
OUT = HERE / "outputs/figures/eeg_only/heatmaps/after_reply"


def save(figure: plt.Figure, stem: str) -> None:
    if "after_reply" not in str(OUT.resolve()):
        raise RuntimeError(f"refusing to write outside after_reply/: {OUT}")
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf"):
        path = OUT / f"{stem}{suffix}"
        figure.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    print(f"wrote {OUT / (stem + '.png')}")


def plot_one(grid: pd.DataFrame, seconds: float) -> None:
    style()
    values = matrix(grid, path="B", seconds=seconds, contrasts=PATH_B)
    figure, axis = plt.subplots(figsize=(8.4, 8.6))
    draw(
        axis,
        values,
        PATH_B,
        title=f"Path B after-reply Holm p · {seconds:g} s · ICA",
        show_ylabels=True,
    )
    figure.text(
        0.01,
        0.012,
        "Lock = assistant_reply + 0.49 s banner lag, ads and matched no-ad. "
        "Holm within feature at this width. * = confirmatory. Orange = Holm < 0.05. "
        "Parallel sensitivity; golden visual-onset lock is unchanged.",
        fontsize=8,
        color=SLATE,
    )
    figure.tight_layout(rect=(0, 0.04, 1, 0.98))
    save(figure, f"path_b_{seconds:g}s")


def plot_after_board(after: pd.DataFrame) -> None:
    style()
    figure, axes = plt.subplots(1, 3, figsize=(14.8, 8.4))
    for col, seconds in enumerate(WIDTHS):
        draw(
            axes[col],
            matrix(after, path="B", seconds=seconds, contrasts=PATH_B),
            PATH_B,
            title=f"After-reply Path B · {seconds:g} s",
            show_ylabels=col == 0,
        )
    figure.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1)),
        ax=axes,
        fraction=0.02,
        pad=0.02,
    ).set_label("Holm p")
    figure.suptitle(
        "After-reply Path B Holm p · ICA · 16 features",
        y=0.98,
        color=INK,
    )
    figure.text(
        0.01,
        0.01,
        "t=0 is the finished reply plus the explicit banner lag. "
        "Not the confirmatory visual-onset lock. Orange = Holm < 0.05.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "board_path_b_2_4_8s")


def plot_vs_golden(golden: pd.DataFrame, after: pd.DataFrame) -> None:
    style()
    figure, axes = plt.subplots(
        2,
        3,
        figsize=(14.8, 12.4),
        gridspec_kw={"wspace": 0.18, "hspace": 0.22},
    )
    for col, seconds in enumerate(WIDTHS):
        draw(
            axes[0, col],
            matrix(golden, path="B", seconds=seconds, contrasts=PATH_B),
            PATH_B,
            title=f"Golden visual onset · {seconds:g} s",
            show_ylabels=col == 0,
        )
        draw(
            axes[1, col],
            matrix(after, path="B", seconds=seconds, contrasts=PATH_B),
            PATH_B,
            title=f"After-reply lock · {seconds:g} s",
            show_ylabels=col == 0,
        )
    figure.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1)),
        ax=axes,
        fraction=0.02,
        pad=0.02,
    ).set_label("Holm p")
    figure.suptitle(
        "Path B Holm p · golden visual onset vs after-reply lock",
        y=0.995,
        color=INK,
    )
    figure.text(
        0.01,
        0.008,
        "Top = confirmatory lock (ad becomes visible). Bottom = finished reply + 0.49 s. "
        "Same ICA, same 18 people, same Holm rule. Path A is unchanged and not shown.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "board_path_b_golden_vs_after_reply")


def plot_familiar_board(golden: pd.DataFrame, after: pd.DataFrame) -> None:
    style()
    figure, axes = plt.subplots(
        2,
        3,
        figsize=(14.8, 12.4),
        gridspec_kw={"wspace": 0.18, "hspace": 0.22},
    )
    for col, seconds in enumerate(WIDTHS):
        draw(
            axes[0, col],
            matrix(golden, path="A", seconds=seconds, contrasts=PATH_A),
            PATH_A,
            title=f"Path A golden · {seconds:g} s",
            show_ylabels=col == 0,
        )
        draw(
            axes[1, col],
            matrix(after, path="B", seconds=seconds, contrasts=PATH_B),
            PATH_B,
            title=f"Path B after-reply · {seconds:g} s",
            show_ylabels=col == 0,
        )
    figure.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1)),
        ax=axes,
        fraction=0.02,
        pad=0.02,
    ).set_label("Holm p")
    figure.suptitle(
        "Path A unchanged · Path B after-reply lock",
        y=0.995,
        color=INK,
    )
    figure.text(
        0.01,
        0.008,
        "Path A is the golden tiled-condition tests. Path B uses the after-reply lock. "
        "Do not treat this as a replacement for the confirmatory board.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "board_path_a_golden_path_b_after_reply")


def main() -> None:
    after = pd.read_csv(AFTER_GRID)
    golden = pd.read_csv(GOLDEN_GRID)
    plot_after_board(after)
    plot_vs_golden(golden, after)
    plot_familiar_board(golden, after)
    for seconds in WIDTHS:
        plot_one(after, seconds)


if __name__ == "__main__":
    main()
