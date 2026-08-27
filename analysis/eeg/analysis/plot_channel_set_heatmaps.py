"""Holm heatmaps for primary vs George vs Wang vs AES-region channel sets.

4 s ICA only. Sensitivity, not a second confirmatory family.

    python analysis/eeg/analysis/plot_channel_set_heatmaps.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from condition_labels import DATASET_A_LABELS, DATASET_B_LABELS


ROOT = Path(__file__).resolve().parents[3]
STATS = ROOT / "analysis/eeg/statistics/outputs"
OUT = (
    Path(__file__).resolve().parent
    / "outputs"
    / "figures"
    / "channel_sets"
)
TABLE = STATS / "sensitivity" / "channel_sets" / "comparison"

NAVY = "#1B3A4B"
INK = "#12202A"
SLATE = "#5C6B73"
CMAP = LinearSegmentedColormap.from_list(
    "holm",
    ["#C45C26", "#F0D5B8", "#F4F6F7", "#9BB0BC"],
)
DIFF_CMAP = LinearSegmentedColormap.from_list(
    "diff",
    ["#1B3A4B", "#F4F6F7", "#C45C26"],
)

FEATURES = [
    ("fz_theta_power_db_uv2", "Fz theta *"),
    ("posterior_alpha_power_db_uv2", "Post. alpha *"),
    ("theta_power_db_uv2", "Theta"),
    ("alpha_power_db_uv2", "Alpha"),
    ("beta_power_db_uv2", "Beta"),
    ("faa_log_f4_minus_f3", "FAA"),
    ("delta_power_db_uv2", "Delta"),
    ("gamma_power_db_uv2", "Gamma"),
    ("delta_relative_power", "Rel. delta"),
    ("theta_relative_power", "Rel. theta"),
    ("alpha_relative_power", "Rel. alpha"),
    ("beta_relative_power", "Rel. beta"),
    ("gamma_relative_power", "Rel. gamma"),
    ("engagement_beta_over_alpha_theta", "Pope"),
    ("engagement_pope_frontocentral_beta_over_alpha_theta", "Pope FC"),
    ("engagement_kislov_central_beta16_24_over_alpha8_12", "Kislov"),
]
GLOBALS = [
    ("delta_power_db_uv2", "Delta"),
    ("theta_power_db_uv2", "Theta"),
    ("alpha_power_db_uv2", "Alpha"),
    ("beta_power_db_uv2", "Beta"),
    ("gamma_power_db_uv2", "Gamma"),
    ("delta_relative_power", "Rel. delta"),
    ("theta_relative_power", "Rel. theta"),
    ("alpha_relative_power", "Rel. alpha"),
    ("beta_relative_power", "Rel. beta"),
    ("gamma_relative_power", "Rel. gamma"),
]
DATASET_A = list(DATASET_A_LABELS.items())
DATASET_B = list(DATASET_B_LABELS.items())
BRANCHES = (
    (
        "primary",
        "Primary · 32-ch",
        STATS / "eeg_condition_contrasts.csv",
        STATS / "eeg_ad_response_contrasts.csv",
    ),
    (
        "literature_roi_v0",
        "George 2025 · 9-site",
        STATS / "sensitivity/channel_sets/literature_roi_v0/eeg_condition_contrasts.csv",
        STATS / "sensitivity/channel_sets/literature_roi_v0/eeg_ad_response_contrasts.csv",
    ),
    (
        "wang2022_v0",
        "Wang 2022 · zones",
        STATS / "sensitivity/channel_sets/wang2022_v0/eeg_condition_contrasts.csv",
        STATS / "sensitivity/channel_sets/wang2022_v0/eeg_ad_response_contrasts.csv",
    ),
    (
        "teaching_atlas_v0",
        "AES 2016 · regions",
        STATS / "sensitivity/channel_sets/teaching_atlas_v0/eeg_condition_contrasts.csv",
        STATS / "sensitivity/channel_sets/teaching_atlas_v0/eeg_ad_response_contrasts.csv",
    ),
)


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
        figure.savefig(OUT / f"{stem}{suffix}", bbox_inches="tight", facecolor="white")
    plt.close(figure)
    print(f"wrote {OUT / (stem + '.png')}")


def load_branch(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing channel-set contrasts: {path}. "
            "Run analysis/eeg/preprocessing/run_channel_set_sensitivity.py first."
        )
    return pd.read_csv(path)


def matrix(
    table: pd.DataFrame,
    contrasts: list[tuple[str, str]],
    features: list[tuple[str, str]],
    column: str,
) -> np.ndarray:
    values = np.full((len(features), len(contrasts)), np.nan)
    primary = table[table["contrast_tier"] == "primary"]
    for i, (feature, _) in enumerate(features):
        for j, (contrast, _) in enumerate(contrasts):
            hit = primary[
                (primary["feature"] == feature)
                & (primary["contrast_id"] == contrast)
            ]
            if hit.empty or pd.isna(hit.iloc[0][column]):
                continue
            values[i, j] = float(hit.iloc[0][column])
    return values


def draw_holm(
    axis: plt.Axes,
    values: np.ndarray,
    contrasts: list[tuple[str, str]],
    features: list[tuple[str, str]],
    *,
    title: str,
    show_ylabels: bool,
) -> None:
    axis.imshow(values, aspect="auto", cmap=CMAP, vmin=0, vmax=1)
    axis.set_xticks(
        range(len(contrasts)),
        [label for _, label in contrasts],
        rotation=28,
        ha="right",
    )
    if show_ylabels:
        axis.set_yticks(range(len(features)), [label for _, label in features])
    else:
        axis.set_yticks(range(len(features)), [""] * len(features))
    axis.tick_params(length=0)
    axis.set_title(title)
    axis.axhline(1.5, color=NAVY, linewidth=0.8)
    for y in range(values.shape[0]):
        for x in range(values.shape[1]):
            value = values[y, x]
            if np.isnan(value):
                continue
            axis.text(
                x,
                y,
                f"{value:.2f}" if value >= 0.1 else f"{value:.3f}",
                ha="center",
                va="center",
                color="white" if value < 0.05 else INK,
                fontsize=6.5,
                fontweight="semibold" if value < 0.05 else "normal",
            )


def draw_diff(
    axis: plt.Axes,
    values: np.ndarray,
    contrasts: list[tuple[str, str]],
    features: list[tuple[str, str]],
    *,
    title: str,
    show_ylabels: bool,
    vmax: float,
) -> None:
    norm = TwoSlopeNorm(vcenter=0.0, vmin=-vmax, vmax=vmax)
    axis.imshow(values, aspect="auto", cmap=DIFF_CMAP, norm=norm)
    axis.set_xticks(
        range(len(contrasts)),
        [label for _, label in contrasts],
        rotation=28,
        ha="right",
    )
    if show_ylabels:
        axis.set_yticks(range(len(features)), [label for _, label in features])
    else:
        axis.set_yticks(range(len(features)), [""] * len(features))
    axis.tick_params(length=0)
    axis.set_title(title)
    for y in range(values.shape[0]):
        for x in range(values.shape[1]):
            value = values[y, x]
            if np.isnan(value):
                continue
            axis.text(
                x,
                y,
                f"{value:+.2f}",
                ha="center",
                va="center",
                color="white" if abs(value) > 0.45 * vmax else INK,
                fontsize=6.5,
            )


def comparison_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for version, label, condition_path, ad_path in BRANCHES:
        condition = load_branch(condition_path)
        ad = load_branch(ad_path)
        for path_name, table, contrasts in (
            ("A", condition, DATASET_A),
            ("B", ad, DATASET_B),
        ):
            primary = table[table["contrast_tier"] == "primary"]
            for feature, feature_label in FEATURES:
                for contrast, contrast_label in contrasts:
                    hit = primary[
                        (primary["feature"] == feature)
                        & (primary["contrast_id"] == contrast)
                    ]
                    if hit.empty:
                        continue
                    row = hit.iloc[0]
                    rows.append(
                        {
                            "branch": version,
                            "branch_label": label,
                            "path": path_name,
                            "feature": feature,
                            "feature_label": feature_label,
                            "contrast_id": contrast,
                            "contrast_label": contrast_label,
                            "n_participants": int(row["n_participants"]),
                            "mean_difference": float(row["mean_difference"]),
                            "ci_lower": float(row["ci_lower"]),
                            "ci_upper": float(row["ci_upper"]),
                            "cohen_dz": float(row["cohen_dz"]),
                            "p_t_raw": float(row["p_t_raw"]),
                            "p_t_holm": (
                                float(row["p_t_holm"])
                                if pd.notna(row["p_t_holm"])
                                else np.nan
                            ),
                        }
                    )
    return rows


def plot_holm_board(path_name: str, contrasts: list, stem: str) -> None:
    style()
    n_branch = len(BRANCHES)
    figure, axes = plt.subplots(
        1,
        n_branch,
        figsize=(4.4 * n_branch, 8.8),
        gridspec_kw={"wspace": 0.16},
    )
    for axis, (version, label, condition_path, ad_path) in zip(axes, BRANCHES):
        table = load_branch(condition_path if path_name == "A" else ad_path)
        draw_holm(
            axis,
            matrix(table, contrasts, FEATURES, "p_t_holm"),
            contrasts,
            FEATURES,
            title=label,
            show_ylabels=axis is axes[0],
        )
    cbar = figure.colorbar(
        plt.cm.ScalarMappable(cmap=CMAP, norm=plt.Normalize(0, 1)),
        ax=axes,
        fraction=0.02,
        pad=0.02,
    )
    cbar.set_label("Holm p")
    figure.suptitle(
        f"Channel-set sensitivity · Dataset {path_name} Holm p · 4 s · ICA",
        y=0.995,
        color=INK,
    )
    figure.text(
        0.01,
        0.008,
        "Rows 1–2 (above the line) are confirmatory features and stay on current_v1, "
        "so they should match primary. Only the ten global band powers change. "
        "Orange = Holm < 0.05 within feature. Sensitivity, not a second confirmatory family. "
        "n=18.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, stem)


def plot_combined_board() -> None:
    style()
    n_branch = len(BRANCHES)
    figure, axes = plt.subplots(
        2,
        n_branch,
        figsize=(4.4 * n_branch, 13.2),
        gridspec_kw={"wspace": 0.16, "hspace": 0.22},
    )
    for col, (version, label, condition_path, ad_path) in enumerate(BRANCHES):
        draw_holm(
            axes[0, col],
            matrix(load_branch(condition_path), DATASET_A, FEATURES, "p_t_holm"),
            DATASET_A,
            FEATURES,
            title=f"Dataset A · {label}",
            show_ylabels=col == 0,
        )
        draw_holm(
            axes[1, col],
            matrix(load_branch(ad_path), DATASET_B, FEATURES, "p_t_holm"),
            DATASET_B,
            FEATURES,
            title=f"Dataset B · {label}",
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
        "Channel-set sensitivity · Holm p · 4 s · ICA · four montages",
        y=0.995,
        color=INK,
    )
    figure.text(
        0.01,
        0.006,
        "George: same nine Methods sites, every band. "
        "Wang and AES: region words mapped onto this cap; neither source published these electrode strings. "
        "Derived rows should match primary. Orange = Holm < 0.05. Not confirmatory. n=18.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, "board_holm_dataset_a_b")


def plot_mean_diff_board(path_name: str, contrasts: list, stem: str) -> None:
    style()
    matrices = []
    for _, _, condition_path, ad_path in BRANCHES:
        table = load_branch(condition_path if path_name == "A" else ad_path)
        matrices.append(matrix(table, contrasts, GLOBALS, "mean_difference"))
    finite = np.concatenate([block[np.isfinite(block)] for block in matrices])
    vmax = max(0.25, float(np.nanpercentile(np.abs(finite), 95)))
    n_branch = len(BRANCHES)
    figure, axes = plt.subplots(
        1,
        n_branch,
        figsize=(4.4 * n_branch, 6.6),
        gridspec_kw={"wspace": 0.16},
    )
    for axis, values, (_, label, _, _) in zip(axes, matrices, BRANCHES):
        draw_diff(
            axis,
            values,
            contrasts,
            GLOBALS,
            title=label,
            show_ylabels=axis is axes[0],
            vmax=vmax,
        )
    cbar = figure.colorbar(
        plt.cm.ScalarMappable(
            cmap=DIFF_CMAP,
            norm=TwoSlopeNorm(vcenter=0.0, vmin=-vmax, vmax=vmax),
        ),
        ax=axes,
        fraction=0.03,
        pad=0.02,
    )
    cbar.set_label("Mean difference")
    figure.suptitle(
        f"Channel-set sensitivity · Dataset {path_name} mean difference · globals · 4 s · ICA",
        y=0.995,
        color=INK,
    )
    figure.text(
        0.01,
        0.008,
        "Only the ten global powers change with the channel set. "
        "Absolute bands are dB; relative bands are proportions. "
        "Sensitivity, not confirmatory. n=18.",
        fontsize=8,
        color=SLATE,
    )
    save(figure, stem)


def main() -> None:
    rows = pd.DataFrame(comparison_rows())
    TABLE.mkdir(parents=True, exist_ok=True)
    table_path = TABLE / "channel_set_contrast_comparison.csv"
    rows.to_csv(table_path, index=False)
    print(f"wrote {table_path}")
    plot_holm_board("A", DATASET_A, "board_holm_dataset_a")
    plot_holm_board("B", DATASET_B, "board_holm_dataset_b")
    plot_combined_board()
    plot_mean_diff_board("A", DATASET_A, "board_mean_diff_globals_dataset_a")
    plot_mean_diff_board("B", DATASET_B, "board_mean_diff_globals_dataset_b")


if __name__ == "__main__":
    main()
