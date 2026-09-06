"""Organised EEG-only Holm heatmaps at 2 / 4 / 8 s for Dataset A and Dataset B.

Writes PNG (300 dpi) and PDF under outputs/figures/eeg_only/heatmaps/.

    python analysis/eeg/analysis/plot_eeg_only_heatmaps.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

from condition_labels import DATASET_A_LABELS, DATASET_B_LABELS


ROOT = Path(__file__).resolve().parents[3]
STATS = ROOT / "analysis/eeg/statistics/outputs"
GRID = STATS / "sensitivity/epoch_length_grid_comparison.csv"
CONDITION_CONTRASTS = STATS / "eeg_condition_contrasts.csv"
AD_CONTRASTS = STATS / "eeg_ad_response_contrasts.csv"
OUT = Path(__file__).resolve().parent / "outputs" / "figures" / "eeg_only" / "heatmaps"

NAVY = "#1B3A4B"
CLAY = "#C45C26"
INK = "#12202A"
SLATE = "#5C6B73"
CMAP = LinearSegmentedColormap.from_list(
    "holm",
    ["#C45C26", "#F0D5B8", "#F4F6F7", "#9BB0BC"],
)

# Greek symbols, to match the manuscript prose (Fz θ, posterior α, ...).
FEATURES = [
    ("fz_theta_power_db_uv2", "Fz θ *"),
    ("posterior_alpha_power_db_uv2", "Posterior α *"),
    ("theta_power_db_uv2", "θ (global)"),
    ("alpha_power_db_uv2", "α (global)"),
    ("beta_power_db_uv2", "β (global)"),
    ("faa_log_f4_minus_f3", "FAA"),
    ("delta_power_db_uv2", "δ (global)"),
    ("gamma_power_db_uv2", "γ (global)"),
    ("delta_relative_power", "Relative δ"),
    ("theta_relative_power", "Relative θ"),
    ("alpha_relative_power", "Relative α"),
    ("beta_relative_power", "Relative β"),
    ("gamma_relative_power", "Relative γ"),
    ("engagement_beta_over_alpha_theta", "Pope"),
    ("engagement_pope_frontocentral_beta_over_alpha_theta", "Pope FC"),
    ("engagement_kislov_central_beta16_24_over_alpha8_12", "Kislov"),
]
DATASET_A = list(DATASET_A_LABELS.items())
DATASET_B = list(DATASET_B_LABELS.items())
WIDTHS = (2.0, 4.0, 8.0)
POLICY = "ica"


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 11,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save(figure: plt.Figure, stem: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf"):
        path = OUT / f"{stem}{suffix}"
        figure.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(figure)
    print(f"wrote {OUT / (stem + '.png')}")


def matrix(
    grid: pd.DataFrame,
    *,
    dataset: str,
    seconds: float,
    contrasts: list[tuple[str, str]],
) -> np.ndarray:
    values = np.full((len(FEATURES), len(contrasts)), np.nan)
    slice_ = grid[
        (grid["path"] == dataset)
        & (grid["policy"] == POLICY)
        & (grid["epoch_seconds"] == seconds)
    ]
    for i, (feature, _) in enumerate(FEATURES):
        for j, (contrast, _) in enumerate(contrasts):
            hit = slice_[
                (slice_["feature"] == feature)
                & (slice_["contrast_id"] == contrast)
            ]
            if hit.empty or pd.isna(hit.iloc[0]["p_t_holm"]):
                continue
            values[i, j] = float(hit.iloc[0]["p_t_holm"])
    return values


def draw(
    axis: plt.Axes,
    values: np.ndarray,
    contrasts: list[tuple[str, str]],
    *,
    title: str,
    show_ylabels: bool,
    annotate: bool = True,
) -> None:
    axis.imshow(values, aspect="auto", cmap=CMAP, vmin=0, vmax=1)
    axis.set_xticks(range(len(contrasts)), [label for _, label in contrasts], rotation=28, ha="right")
    if show_ylabels:
        axis.set_yticks(range(len(FEATURES)), [label for _, label in FEATURES])
    else:
        axis.set_yticks(range(len(FEATURES)), [""] * len(FEATURES))
    axis.tick_params(length=0)
    axis.set_title(title)
    axis.axhline(1.5, color=NAVY, linewidth=0.8)
    if annotate:
        fontsize = 7 if values.shape[1] <= 3 else 6.5
        for y in range(values.shape[0]):
            for x in range(values.shape[1]):
                value = values[y, x]
                if np.isnan(value):
                    continue
                axis.text(
                    x,
                    y,
                    apa_p(value),
                    ha="center",
                    va="center",
                    color="white" if value < 0.05 else INK,
                    fontsize=fontsize,
                    fontweight="semibold" if value < 0.05 else "normal",
                )


def apa_p(value: float) -> str:
    """APA-style p: no leading zero, two decimals above .10, three below."""
    text = f"{value:.2f}" if value >= 0.1 else f"{value:.3f}"
    return text[1:] if text.startswith("0.") else text


def plot_one(
    grid: pd.DataFrame,
    *,
    dataset: str,
    seconds: float,
    contrasts: list[tuple[str, str]],
    stem: str,
    title: str,
) -> None:
    style()
    values = matrix(grid, dataset=dataset, seconds=seconds, contrasts=contrasts)
    figure, axis = plt.subplots(figsize=(7.2 if dataset == "A" else 8.4, 8.6))
    draw(axis, values, contrasts, title=title, show_ylabels=True)
    figure.text(
        0.01,
        0.012,
        "Holm p within feature across the primary contrasts at this width, "
        "not across lengths. * = confirmatory features. Orange = Holm < 0.05. "
        f"ICA. n=18 except 8 s Dataset B early n=17. Source: {GRID.name}.",
        fontsize=8,
        color=SLATE,
    )
    figure.tight_layout(rect=(0, 0.04, 1, 0.98))
    save(figure, stem)


def plot_board(grid: pd.DataFrame) -> None:
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
            matrix(grid, dataset="A", seconds=seconds, contrasts=DATASET_A),
            DATASET_A,
            title=f"Dataset A · {seconds:g} s",
            show_ylabels=col == 0,
        )
        draw(
            axes[1, col],
            matrix(grid, dataset="B", seconds=seconds, contrasts=DATASET_B),
            DATASET_B,
            title=f"Dataset B · {seconds:g} s",
            show_ylabels=col == 0,
        )
    cbar = figure.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1)),
        ax=axes,
        fraction=0.02,
        pad=0.02,
    )
    cbar.set_label("Holm p")
    figure.suptitle(
        "EEG-only Holm p · ICA · 16 features × primary contrasts",
        y=0.995,
        color=INK,
    )
    figure.text(
        0.01,
        0.008,
        "Rows 1–2 (above the line) are confirmatory: Fz theta and posterior alpha. "
        "Holm is within feature at that width, not across 2/4/8 s. "
        "Primary remains 4 s. Orange = Holm < 0.05. "
        "Dataset B early at 8 s is n=17. Source: epoch_length_grid_comparison.csv · 19 Aug 2026.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "board_dataset_a_b_2_4_8s")


def matrix_from_contrasts(
    tests: pd.DataFrame,
    contrasts: list[tuple[str, str]],
) -> np.ndarray:
    values = np.full((len(FEATURES), len(contrasts)), np.nan)
    primary = tests[tests["contrast_tier"] == "primary"]
    for i, (feature, _) in enumerate(FEATURES):
        for j, (contrast, _) in enumerate(contrasts):
            hit = primary[
                (primary["feature"] == feature)
                & (primary["contrast_id"] == contrast)
            ]
            if hit.empty or pd.isna(hit.iloc[0]["p_t_holm"]):
                continue
            values[i, j] = float(hit.iloc[0]["p_t_holm"])
    return values


def plot_board_4s(grid: pd.DataFrame) -> None:
    """Reported 4 s ICA board: Dataset A equal-n k=37 + Dataset B onset-locked."""
    del grid
    style()
    condition = pd.read_csv(CONDITION_CONTRASTS)
    ad = pd.read_csv(AD_CONTRASTS)
    figure, axes = plt.subplots(
        1,
        2,
        figsize=(12.6, 8.8),
        gridspec_kw={"wspace": 0.28, "width_ratios": [3, 4]},
    )
    draw(
        axes[0],
        matrix_from_contrasts(condition, DATASET_A),
        DATASET_A,
        title="Dataset A: condition aggregation",
        show_ylabels=True,
    )
    draw(
        axes[1],
        matrix_from_contrasts(ad, DATASET_B),
        DATASET_B,
        title="Dataset B: onset-locked, versus matched no-ad",
        show_ylabels=False,
    )
    cbar = figure.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1)),
        ax=axes,
        fraction=0.03,
        pad=0.02,
    )
    cbar.set_label("Holm p")
    # No suptitle or in-figure footnote: the manuscript caption carries them.
    save(figure, "board_dataset_a_b_4s")


def main() -> None:
    grid = pd.read_csv(GRID)
    plot_board_4s(grid)
    plot_board(grid)
    for seconds in WIDTHS:
        plot_one(
            grid,
            dataset="A",
            seconds=seconds,
            contrasts=DATASET_A,
            stem=f"dataset_a_{seconds:g}s",
            title=f"Dataset A Holm p · {seconds:g} s · ICA",
        )
        plot_one(
            grid,
            dataset="B",
            seconds=seconds,
            contrasts=DATASET_B,
            stem=f"dataset_b_{seconds:g}s",
            title=f"Dataset B Holm p · {seconds:g} s · ICA",
        )


if __name__ == "__main__":
    main()
