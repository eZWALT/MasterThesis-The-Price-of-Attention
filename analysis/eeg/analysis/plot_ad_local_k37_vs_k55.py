"""Holm and dz heatmaps: Dataset A around-onset, k=37 vs k=55.

    python analysis/eeg/analysis/plot_ad_local_k37_vs_k55.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[3]
TABLE = (
    ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/balanced_k/comparison.csv"
)
OUT = Path(__file__).resolve().parent / "outputs" / "figures" / "ad_local_epochs" / "balanced_k"

INK = "#12202A"
SLATE = "#5C6B73"
HOLM_CMAP = LinearSegmentedColormap.from_list(
    "holm",
    ["#C45C26", "#F0D5B8", "#F4F6F7", "#9BB0BC"],
)
DZ_CMAP = LinearSegmentedColormap.from_list(
    "dz",
    ["#1B3A4B", "#F4F6F7", "#C45C26"],
)
FEATURES = (
    "fz_theta_power_db_uv2",
    "posterior_alpha_power_db_uv2",
    "theta_power_db_uv2",
    "alpha_power_db_uv2",
    "beta_power_db_uv2",
    "faa_log_f4_minus_f3",
    "delta_power_db_uv2",
    "gamma_power_db_uv2",
    "delta_relative_power",
    "theta_relative_power",
    "alpha_relative_power",
    "beta_relative_power",
    "gamma_relative_power",
    "engagement_beta_over_alpha_theta",
    "engagement_pope_frontocentral_beta_over_alpha_theta",
    "engagement_kislov_central_beta16_24_over_alpha8_12",
)
FEATURE_LABELS = (
    "Fz theta",
    "Posterior alpha",
    "Global theta",
    "Global alpha",
    "Global beta",
    "FAA",
    "Global delta",
    "Global gamma",
    "Rel. delta",
    "Rel. theta",
    "Rel. alpha",
    "Rel. beta",
    "Rel. gamma",
    "Pope",
    "Pope FC",
    "Kislov",
)
CONTRASTS = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")
CONTRAST_LABELS = ("Any ad", "Format", "Timing")
PANELS = (
    (37, "saturate", "k = 37 · n = 18\nequal n_tiles"),
    (55, "saturate", "k = 55 · n = 18\nshort chats still in"),
    (55, "complete", "k = 55 · n = 13\nshort chats dropped"),
)


def matrix(frame: pd.DataFrame, k: int, rule: str, column: str) -> np.ndarray:
    slice_ = frame[
        (frame["k_epochs"] == k)
        & (frame["rule"] == rule)
        & (frame["contrast_id"].isin(CONTRASTS))
    ]
    values = np.full((len(FEATURES), len(CONTRASTS)), np.nan)
    for i, feature in enumerate(FEATURES):
        for j, contrast in enumerate(CONTRASTS):
            hit = slice_[
                (slice_["feature"] == feature) & (slice_["contrast_id"] == contrast)
            ]
            if not hit.empty:
                values[i, j] = float(hit.iloc[0][column])
    return values


def holm_hits(frame: pd.DataFrame, k: int, rule: str) -> np.ndarray:
    slice_ = frame[
        (frame["k_epochs"] == k)
        & (frame["rule"] == rule)
        & (frame["contrast_id"].isin(CONTRASTS))
    ]
    hits = np.zeros((len(FEATURES), len(CONTRASTS)), dtype=bool)
    for i, feature in enumerate(FEATURES):
        for j, contrast in enumerate(CONTRASTS):
            hit = slice_[
                (slice_["feature"] == feature) & (slice_["contrast_id"] == contrast)
            ]
            if not hit.empty:
                hits[i, j] = hit.iloc[0]["holm_significant"] == "yes"
    return hits


def annotate_holm(axis: plt.Axes, values: np.ndarray) -> None:
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if np.isnan(value):
                continue
            axis.text(
                j,
                i,
                f"{value:.3f}" if value < 0.10 else f"{value:.2f}",
                ha="center",
                va="center",
                fontsize=7,
                color="white" if value < 0.05 else INK,
                fontweight="bold" if value < 0.05 else "normal",
            )


def annotate_dz(axis: plt.Axes, values: np.ndarray, hits: np.ndarray) -> None:
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            value = values[i, j]
            if np.isnan(value):
                continue
            axis.text(
                j,
                i,
                f"{value:+.2f}",
                ha="center",
                va="center",
                fontsize=6.5,
                color="white" if hits[i, j] else INK,
                fontweight="bold" if hits[i, j] else "normal",
            )


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "pdf.fonttype": 42,
            "savefig.dpi": 180,
        }
    )
    frame = pd.read_csv(TABLE)
    OUT.mkdir(parents=True, exist_ok=True)

    holm = [matrix(frame, k, rule, "p_t_holm") for k, rule, _ in PANELS]
    dz = [matrix(frame, k, rule, "cohen_dz") for k, rule, _ in PANELS]
    hits = [holm_hits(frame, k, rule) for k, rule, _ in PANELS]

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 7.6), constrained_layout=True)
    image = None
    for axis, values, title in zip(axes, holm, (p[2] for p in PANELS)):
        image = axis.imshow(values, cmap=HOLM_CMAP, vmin=0, vmax=1, aspect="auto")
        axis.set_xticks(range(3), CONTRAST_LABELS, color=INK)
        axis.set_title(title, color=INK, loc="left", fontsize=10)
        annotate_holm(axis, values)
        axis.tick_params(length=0)
        for spine in axis.spines.values():
            spine.set_visible(False)
    axes[0].set_yticks(range(len(FEATURES)), FEATURE_LABELS, color=INK, fontsize=8)
    for axis in axes[1:]:
        axis.set_yticks([])
    cbar = fig.colorbar(image, ax=axes, fraction=0.03, pad=0.02)
    cbar.set_label("Holm p (within feature, 3 contrasts)", color=INK)
    fig.suptitle(
        "Dataset A · tiles nearest the onset · Holm p",
        color=INK,
        fontsize=13,
        x=0.01,
        ha="left",
    )
    fig.savefig(OUT / "holm_k37_vs_k55.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / "holm_k37_vs_k55.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 7.6), constrained_layout=True)
    norm = TwoSlopeNorm(vmin=-1.1, vcenter=0, vmax=1.1)
    image = None
    for axis, values, hit, title in zip(
        axes, dz, hits, (p[2] for p in PANELS)
    ):
        image = axis.imshow(values, cmap=DZ_CMAP, norm=norm, aspect="auto")
        axis.set_xticks(range(3), CONTRAST_LABELS, color=INK)
        axis.set_title(title, color=INK, loc="left", fontsize=10)
        annotate_dz(axis, values, hit)
        axis.tick_params(length=0)
        for spine in axis.spines.values():
            spine.set_visible(False)
    axes[0].set_yticks(range(len(FEATURES)), FEATURE_LABELS, color=INK, fontsize=8)
    for axis in axes[1:]:
        axis.set_yticks([])
    cbar = fig.colorbar(image, ax=axes, fraction=0.03, pad=0.02)
    cbar.set_label("Cohen dz  (white text = Holm < .05)", color=INK)
    fig.suptitle(
        "Dataset A · tiles nearest the onset · effect size",
        color=INK,
        fontsize=13,
        x=0.01,
        ha="left",
    )
    fig.savefig(OUT / "dz_k37_vs_k55.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT / "dz_k37_vs_k55.pdf", bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT / 'holm_k37_vs_k55.png'}")
    print(f"wrote {OUT / 'dz_k37_vs_k55.png'}")


if __name__ == "__main__":
    main()
