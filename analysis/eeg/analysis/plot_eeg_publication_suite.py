"""Publication-quality EEG figures beyond the initial forest suite.

Writes PNG (300 dpi) and PDF under outputs/figures/suite/.

    python analysis/eeg/analysis/plot_eeg_publication_suite.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

from condition_labels import (
    CONDITION_LABELS,
    DATASET_A_LABELS,
    DATASET_B_LABELS,
    DATASET_B_SLOPE_PANELS,
)


ROOT = Path(__file__).resolve().parents[3]
STATS = ROOT / "analysis/eeg/statistics/outputs"
GOLD = ROOT / "src/project/logs/xdf/gold/features"
OUT = Path(__file__).resolve().parent / "outputs" / "figures" / "suite"

NAVY = "#1B3A4B"
CLAY = "#C45C26"
HOLM_ORANGE = CLAY
HOLM_STAR_SIZE = 16
HOLM_LEGEND = "Holm p < .05"
TEAL = "#2A6F6F"
SLATE = "#5C6B73"
MIST = "#D5DDE3"
INK = "#12202A"
PRIMARY = {
    "fz_theta_power_db_uv2": "Fz θ (dB µV²)",
    "posterior_alpha_power_db_uv2": "Posterior α (dB µV²)",
}
CONDITIONS = [
    "no_ads",
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
]
BANDS = [
    ("delta_power_db_uv2", "Delta"),
    ("theta_power_db_uv2", "Theta"),
    ("alpha_power_db_uv2", "Alpha"),
    ("beta_power_db_uv2", "Beta"),
    ("gamma_power_db_uv2", "Gamma"),
]


def style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "text.color": INK,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save(figure: plt.Figure, stem: str) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    figure.tight_layout(rect=(0, 0.06, 1, 0.98))
    paths = []
    for suffix in (".png", ".pdf"):
        path = OUT / f"{stem}{suffix}"
        figure.savefig(path, format=suffix[1:], bbox_inches="tight", facecolor="white")
        paths.append(path)
    plt.close(figure)
    print(f"wrote {paths[0]}")
    return paths


def caption(figure: plt.Figure, text: str) -> None:
    figure.text(0.01, 0.012, text, fontsize=8, color=SLATE)


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def holm_star(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def plot_condition_rainclouds(features: pd.DataFrame) -> None:
    eligible = features[
        (features["window_type"] == "condition")
        & (features["primary_analysis_eligible"] == "yes")
    ]
    figure, axes = plt.subplots(1, 2, figsize=(11.2, 5.1), sharex=True)
    rng = np.random.default_rng(20260819)
    for axis, (feature, label) in zip(axes, PRIMARY.items()):
        column = f"{feature}_median"
        for index, condition in enumerate(CONDITIONS):
            values = eligible.loc[
                eligible["condition"] == condition, column
            ].to_numpy(dtype=float)
            parts = axis.violinplot(
                values,
                positions=[index],
                widths=0.72,
                showextrema=False,
                showmedians=False,
            )
            for body in parts["bodies"]:
                body.set_facecolor(TEAL if index == 0 else NAVY)
                body.set_alpha(0.22)
                body.set_edgecolor("none")
            axis.boxplot(
                values,
                positions=[index],
                widths=0.16,
                showfliers=False,
                medianprops={"color": CLAY, "linewidth": 1.8},
                boxprops={"color": NAVY, "linewidth": 1.1},
                whiskerprops={"color": NAVY},
                capprops={"color": NAVY},
            )
            jitter = rng.normal(0, 0.055, size=len(values))
            axis.scatter(
                np.full(len(values), index) + jitter,
                values,
                s=18,
                color=NAVY,
                alpha=0.55,
                zorder=3,
            )
        axis.set_xticks(range(len(CONDITIONS)))
        axis.set_xticklabels(
            [CONDITION_LABELS[c] for c in CONDITIONS],
            rotation=28,
            ha="right",
        )
        axis.set_ylabel(label)
        axis.set_title(label)
    figure.suptitle("Condition medians by participant (Dataset A, 4 s, ICA)", y=1.02)
    caption(
        figure,
        "Each point is one participant (n=18). Violin = distribution; "
        "box = quartiles; orange = median. Source: condition_features.csv.",
    )
    save(figure, "figure_07_condition_rainclouds")


def plot_confirmatory_forests(
    condition: pd.DataFrame,
    ad: pd.DataFrame,
) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(12.4, 6.2))
    panels = (
        (
            axes[0],
            condition[
                (condition["feature"].isin(PRIMARY))
                & (condition["contrast_id"].isin(DATASET_A_LABELS))
            ],
            DATASET_A_LABELS,
            "Dataset A: condition aggregation",
        ),
        (
            axes[1],
            ad[
                (ad["feature"].isin(PRIMARY))
                & (ad["contrast_id"].isin(DATASET_B_LABELS))
            ],
            DATASET_B_LABELS,
            "Dataset B: onset-locked, versus matched no-ad",
        ),
    )
    for axis, frame, labels, title in panels:
        frame = frame.copy()
        frame["order"] = frame["contrast_id"].map(
            {key: index for index, key in enumerate(labels)}
        )
        frame["feat_order"] = frame["feature"].map(
            {key: index for index, key in enumerate(PRIMARY)}
        )
        frame = frame.sort_values(["order", "feat_order"]).reset_index(drop=True)
        colors = [NAVY if row.feature.startswith("fz_") else TEAL for row in frame.itertuples()]
        positions = np.arange(len(frame))
        xmax = float(frame["ci_upper"].max()); xmin = float(frame["ci_lower"].min()); span = xmax - xmin
        for index, row in frame.iterrows():
            axis.errorbar(
                row["mean_difference"],
                positions[index],
                xerr=[[row["mean_difference"] - row["ci_lower"]],
                      [row["ci_upper"] - row["mean_difference"]]],
                fmt="o",
                color=colors[index],
                capsize=3.5,
                markersize=6,
                elinewidth=1.4,
            )
            p_holm = float(row["p_t_holm"]) if row["p_t_holm"] != "" else math.nan
            if pd.notna(p_holm) and p_holm < 0.05:
                axis.text(
                    xmax + 0.06 * span,
                    positions[index],
                    "*",
                    va="center",
                    ha="center",
                    color=HOLM_ORANGE,
                    fontsize=HOLM_STAR_SIZE,
                    fontweight="bold",
                )
        axis.axvline(0, color=INK, linewidth=0.8)
        axis.set_xlim(xmin - 0.05 * span, xmax + 0.14 * span)
        axis.set_yticks(
            positions,
            [
                f"{labels[row.contrast_id]}\n{PRIMARY[row.feature]}"
                for row in frame.itertuples()
            ],
        )
        axis.invert_yaxis()
        axis.set_xlabel("Mean within-person difference, dB (95% t CI)")
        axis.set_title(title)
    handle = Line2D(
        [0], [0], marker="*", color="none", markeredgecolor=HOLM_ORANGE,
        markerfacecolor=HOLM_ORANGE, markersize=14, linestyle="none", label=HOLM_LEGEND,
    )
    figure.legend(handles=[handle], loc="lower center", bbox_to_anchor=(0.5, -0.02), frameon=False, fontsize=9)
    # No suptitle or in-figure footnote: the manuscript caption carries them.
    save(figure, "figure_08_confirmatory_forests")


def plot_ad_paired_slopes(ad_responses: pd.DataFrame) -> None:
    cells = [
        *DATASET_B_SLOPE_PANELS,
    ]
    figure, axes = plt.subplots(2, 4, figsize=(13.2, 6.8), sharey="row")
    for row_index, (feature, ylabel) in enumerate(PRIMARY.items()):
        column = f"{feature}_post_minus_pre"
        for col_index, (ad_cond, ctrl, title) in enumerate(cells):
            axis = axes[row_index, col_index]
            ad = ad_responses[
                (ad_responses["condition"] == ad_cond)
                & (ad_responses["primary_analysis_eligible"] == "yes")
            ].set_index("subject_id")
            if ctrl.endswith("early"):
                control = ad_responses[
                    (ad_responses["reference_kind"] == "matched_no_ad_reply")
                    & (ad_responses["matched_timing"] == "early")
                    & (ad_responses["primary_analysis_eligible"] == "yes")
                ].set_index("subject_id")
            else:
                control = ad_responses[
                    (ad_responses["reference_kind"] == "matched_no_ad_reply")
                    & (ad_responses["matched_timing"] == "late")
                    & (ad_responses["primary_analysis_eligible"] == "yes")
                ].set_index("subject_id")
            subjects = ad.index.intersection(control.index)
            left = control.loc[subjects, column].to_numpy(dtype=float)
            right = ad.loc[subjects, column].to_numpy(dtype=float)
            for a, b in zip(left, right):
                axis.plot([0, 1], [a, b], color=MIST, linewidth=0.9)
            axis.scatter(np.zeros(len(left)), left, color=SLATE, s=16, zorder=3)
            axis.scatter(np.ones(len(right)), right, color=NAVY, s=16, zorder=3)
            axis.plot(
                [0, 1],
                [left.mean(), right.mean()],
                color=CLAY,
                linewidth=2.2,
                zorder=4,
            )
            axis.set_xticks([0, 1], ["No-ad", "Ad"])
            if row_index == 0:
                axis.set_title(title)
            if col_index == 0:
                axis.set_ylabel(ylabel)
            axis.axhline(0, color=INK, linewidth=0.6, alpha=0.45)
    figure.suptitle(
        "Ad vs matched no-ad post−pre change, paired within participant",
        y=1.02,
    )
    caption(
        figure,
        "Grey lines = participants. Orange = mean. Values are post−pre dB in "
        "the 4 s ad-locked window. Source: ad_response_features.csv.",
    )
    save(figure, "figure_09_ad_paired_slopes")


def plot_epoch_grid_heatmap(grid: pd.DataFrame) -> None:
    conf = grid[
        (grid["confirmatory"] == True)  # noqa: E712
        & (grid["path"] == "B")
        & (grid["policy"] == "ica")
    ].copy()
    contrasts = list(DATASET_B_LABELS)
    features = list(PRIMARY)
    lengths = [2.0, 4.0, 8.0, 16.0, 32.0]
    matrix = np.full((len(features) * len(contrasts), len(lengths)), np.nan)
    labels = []
    for i, feature in enumerate(features):
        for j, contrast in enumerate(contrasts):
            labels.append(f"{PRIMARY[feature]} · {DATASET_B_LABELS[contrast]}")
            for k, seconds in enumerate(lengths):
                hit = conf[
                    (conf["feature"] == feature)
                    & (conf["contrast_id"] == contrast)
                    & (conf["epoch_seconds"] == seconds)
                ]
                if not hit.empty:
                    matrix[i * len(contrasts) + j, k] = float(hit.iloc[0]["p_t_holm"])
    cmap = LinearSegmentedColormap.from_list(
        "holm",
        ["#C45C26", "#F0D5B8", "#F4F6F7", "#9BB0BC"],
    )
    figure, axis = plt.subplots(figsize=(10.6, 6.4))
    image = axis.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    axis.set_xticks(range(len(lengths)), [f"{s:g} s" for s in lengths])
    axis.set_yticks(range(len(labels)), labels)
    for y in range(matrix.shape[0]):
        for x in range(matrix.shape[1]):
            value = matrix[y, x]
            if np.isnan(value):
                continue
            axis.text(
                x,
                y,
                f"{value:.3f}",
                ha="center",
                va="center",
                color="white" if value < 0.05 else INK,
                fontsize=8,
                fontweight="semibold" if value < 0.05 else "normal",
            )
    axis.set_title("Dataset B confirmatory Holm p across epoch lengths (ICA)")
    figure.colorbar(image, ax=axis, fraction=0.03, pad=0.02, label="Holm p")
    caption(
        figure,
        "Orange cells are Holm < 0.05. Holm is within feature at each length, "
        "not across the grid. Primary remains 4 s.",
    )
    save(figure, "figure_10_epoch_grid_heatmap")


def plot_epoch_grid_heatmap_ica_noica(grid: pd.DataFrame) -> None:
    contrasts = list(DATASET_B_LABELS)
    features = list(PRIMARY)
    lengths = [2.0, 4.0, 8.0, 16.0, 32.0]
    cmap = LinearSegmentedColormap.from_list(
        "holm",
        ["#C45C26", "#F0D5B8", "#F4F6F7", "#9BB0BC"],
    )
    figure, axes = plt.subplots(1, 2, figsize=(13.2, 6.6), sharey=True)
    labels = [
        f"{PRIMARY[feature]} · {DATASET_B_LABELS[contrast]}"
        for feature in features
        for contrast in contrasts
    ]
    for axis, policy, title in (
        (axes[0], "ica", "Dataset B confirmatory Holm p · ICA"),
        (axes[1], "no_ica", "Dataset B confirmatory Holm p · No-ICA"),
    ):
        conf = grid[
            (grid["confirmatory"] == True)  # noqa: E712
            & (grid["path"] == "B")
            & (grid["policy"] == policy)
        ]
        matrix = np.full((len(labels), len(lengths)), np.nan)
        for i, feature in enumerate(features):
            for j, contrast in enumerate(contrasts):
                for k, seconds in enumerate(lengths):
                    hit = conf[
                        (conf["feature"] == feature)
                        & (conf["contrast_id"] == contrast)
                        & (conf["epoch_seconds"] == seconds)
                    ]
                    if not hit.empty:
                        matrix[i * len(contrasts) + j, k] = float(
                            hit.iloc[0]["p_t_holm"]
                        )
        image = axis.imshow(matrix, aspect="auto", cmap=cmap, vmin=0, vmax=1)
        axis.set_xticks(range(len(lengths)), [f"{s:g} s" for s in lengths])
        axis.set_yticks(range(len(labels)), labels)
        for y in range(matrix.shape[0]):
            for x in range(matrix.shape[1]):
                value = matrix[y, x]
                if np.isnan(value):
                    continue
                axis.text(
                    x,
                    y,
                    f"{value:.3f}",
                    ha="center",
                    va="center",
                    color="white" if value < 0.05 else INK,
                    fontsize=7.5,
                    fontweight="semibold" if value < 0.05 else "normal",
                )
        for x, seconds in enumerate(lengths):
            if seconds in (4.0, 8.0):
                axis.add_patch(
                    plt.Rectangle(
                        (x - 0.5, -0.5),
                        1,
                        matrix.shape[0],
                        fill=False,
                        edgecolor=NAVY,
                        linewidth=1.6,
                    )
                )
        axis.set_title(title)
    figure.colorbar(image, ax=axes, fraction=0.03, pad=0.02, label="Holm p")
    caption(
        figure,
        "Navy boxes = 4 s (primary) and 8 s. Orange = Holm p < 0.05 within "
        "feature at that length, not across the grid. Source: "
        "epoch_length_grid_comparison.csv.",
    )
    save(figure, "figure_10b_epoch_grid_heatmap_ica_noica")


def plot_epoch_timeline() -> None:
    explicit_inject = -3.3
    explicit_reply = -0.49
    implicit_inject = -1.57
    implicit_reply = 1.6
    early_next = 52.7
    late_next = 79.4
    widths = (2, 4, 8)
    colors = {2: "#C45C26", 4: "#5C6B73", 8: "#2A6F6F"}
    pre_colors = {2: "#D5DDE3", 4: "#9BB0BC", 8: "#1B3A4B"}

    figure, axes = plt.subplots(
        3,
        1,
        figsize=(11.4, 8.4),
        gridspec_kw={"height_ratios": [1.15, 1.15, 0.85]},
    )

    def draw_zoom(axis, title, inject, reply) -> None:
        t0, t1 = -8.6, 10.2
        axis.set_xlim(t0, t1)
        axis.set_ylim(0, 4.2)
        axis.axvline(0, color=CLAY, linestyle="--", linewidth=1.2)
        axis.axvline(inject, color=SLATE, linestyle="--", linewidth=1.0)
        axis.axvline(reply, color=NAVY, linestyle="--", linewidth=1.0)
        axis.text(inject, 4.05, "inject", ha="center", va="top", fontsize=8, color=SLATE)
        axis.text(reply, 4.05, "reply", ha="center", va="top", fontsize=8, color=NAVY)
        axis.text(0, 4.05, "ad onset", ha="center", va="top", fontsize=8, color=CLAY)
        for index, width in enumerate(widths):
            y = 0.55 + index * 1.05
            axis.barh(
                y,
                width,
                left=-width,
                height=0.62,
                color=pre_colors[width],
                edgecolor="none",
            )
            axis.barh(
                y,
                width,
                left=0,
                height=0.62,
                color=colors[width],
                alpha=0.72 if width != 2 else 0.9,
                edgecolor="none",
            )
            axis.text(
                -width - 0.15,
                y,
                f"{width}s pre",
                ha="right",
                va="center",
                fontsize=7.5,
                color=INK,
            )
            axis.text(
                width + 0.15,
                y,
                f"{width}s post",
                ha="left",
                va="center",
                fontsize=7.5,
                color=INK,
            )
        axis.set_yticks([])
        axis.set_xlabel("seconds from visual ad onset")
        axis.set_title(title, loc="left")
        axis.text(
            t1,
            0.15,
            "median n=19",
            ha="right",
            va="bottom",
            fontsize=7.5,
            color=SLATE,
        )
        for spine in ("left", "top", "right"):
            axis.spines[spine].set_visible(False)

    draw_zoom(
        axes[0],
        "Explicit ads (ICA hits live here) · reply already up ~0.5 s",
        explicit_inject,
        explicit_reply,
    )
    draw_zoom(
        axes[1],
        "Implicit ads · reply follows display by ~1.6 s",
        implicit_inject,
        implicit_reply,
    )

    axis = axes[2]
    axis.set_xlim(0, 120)
    axis.set_ylim(0, 2.4)
    for y, _label in ((0.7, "early / late post windows"), (1.55, "")):
        axis.barh(y, 120, left=0, height=0.38, color=MIST, edgecolor="none")
        for width in (8, 4, 2):
            axis.barh(
                y,
                width,
                left=0,
                height=0.38,
                color=colors[width],
                edgecolor="none",
            )
    axis.axvline(early_next, color=INK, linewidth=1.3)
    axis.axvline(late_next, color=CLAY, linewidth=1.3)
    axis.text(
        early_next,
        2.2,
        "early · next user_message +53 s",
        ha="center",
        fontsize=8,
        color=INK,
    )
    axis.text(
        late_next,
        2.2,
        "late · conclusion +79 s",
        ha="center",
        fontsize=8,
        color=CLAY,
    )
    axis.set_yticks([])
    axis.set_xlabel("seconds from visual ad onset")
    axis.set_title(
        "Same post windows on a 2-minute scale · next act differs by timing",
        loc="left",
    )
    axis.text(
        1,
        0.12,
        "clay=2s  slate=4s  teal=8s",
        fontsize=7.5,
        color=SLATE,
    )
    for spine in ("left", "top", "right"):
        axis.spines[spine].set_visible(False)

    caption(
        figure,
        "Dataset B lock = visual ad onset. 2/4/8 post never reach writing or "
        "conclusion. 4 s is the width that usually contains the reply and not "
        "the next act. Source: ad_visibility_events.csv + canonical markers.",
    )
    save(figure, "figure_17_epoch_timeline")


def plot_epoch_traces(grid: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11.4, 4.8), sharey=True)
    traces = (
        (
            axes[0],
            "fz_theta_power_db_uv2",
            "block_early_vs_no_ad_early",
            "Fz theta · explicit early − no-ad",
        ),
        (
            axes[1],
            "posterior_alpha_power_db_uv2",
            "block_late_vs_no_ad_late",
            "Posterior alpha · explicit late − no-ad",
        ),
    )
    lengths = [2.0, 4.0, 8.0, 16.0, 32.0]
    for axis, feature, contrast, title in traces:
        for policy, color, label in (
            ("ica", NAVY, "ICA"),
            ("no_ica", CLAY, "No-ICA"),
        ):
            subset = grid[
                (grid["feature"] == feature)
                & (grid["contrast_id"] == contrast)
                & (grid["path"] == "B")
                & (grid["policy"] == policy)
            ].set_index("epoch_seconds")
            ys = [float(subset.loc[s, "p_t_holm"]) for s in lengths]
            axis.plot(lengths, ys, marker="o", color=color, linewidth=2, label=label)
        axis.axhline(0.05, color=CLAY, linestyle="--", linewidth=1, alpha=0.8)
        axis.set_xticks(lengths, [f"{s:g}" for s in lengths])
        axis.set_xlabel("Window length (s)")
        axis.set_title(title)
        axis.set_ylim(-0.02, 1.05)
        axis.legend(frameon=False)
    axes[0].set_ylabel("Holm p")
    figure.suptitle("The two confirmatory grid cells do not hold at 4 s", y=1.03)
    caption(
        figure,
        "Dashed line = 0.05. Left hit is ICA-only at 2 s. Right hit is 8 s "
        "under both cleanings. Source: epoch_length_grid_comparison.csv.",
    )
    save(figure, "figure_11_epoch_grid_traces")


def plot_band_profiles(features: pd.DataFrame) -> None:
    eligible = features[
        (features["window_type"] == "condition")
        & (features["primary_analysis_eligible"] == "yes")
    ]
    figure, axis = plt.subplots(figsize=(10.8, 5.0))
    x = np.arange(len(BANDS))
    width = 0.15
    palette = ["#5C6B73", "#355C7D", "#2A6F6F", "#C45C26", "#8C4A32"]
    for offset, (condition, color) in enumerate(zip(CONDITIONS, palette)):
        means = []
        sems = []
        for band, _ in BANDS:
            values = eligible.loc[
                eligible["condition"] == condition, f"{band}_median"
            ].to_numpy(dtype=float)
            means.append(float(np.mean(values)))
            sems.append(float(np.std(values, ddof=1) / math.sqrt(len(values))))
        axis.errorbar(
            x + (offset - 2) * width,
            means,
            yerr=sems,
            fmt="o-",
            color=color,
            linewidth=1.6,
            markersize=5,
            capsize=2.5,
            label=CONDITION_LABELS[condition],
        )
    axis.set_xticks(x, [label for _, label in BANDS])
    axis.set_ylabel("Global band power (dB µV²)")
    axis.set_title("Condition spectral profiles (mean ± SEM, n=18)")
    axis.legend(ncols=5, frameon=False, loc="upper right")
    caption(
        figure,
        "Five global bands from Dataset A window medians. Overlapping lines are "
        "the visual form of the Holm-null condition tests.",
    )
    save(figure, "figure_12_band_profiles")


def plot_ica_agreement(grid: pd.DataFrame) -> None:
    four = grid[(grid["epoch_seconds"] == 4.0) & (grid["path"].isin(["A", "B"]))]
    ica = four[four["policy"] == "ica"].set_index(
        ["path", "contrast_id", "feature"]
    )
    no_ica = four[four["policy"] == "no_ica"].set_index(
        ["path", "contrast_id", "feature"]
    )
    shared = ica.index.intersection(no_ica.index)
    figure, axis = plt.subplots(figsize=(6.6, 6.2))
    for path, color, label in (("A", NAVY, "Dataset A"), ("B", CLAY, "Dataset B")):
        keys = [key for key in shared if key[0] == path]
        xs = [float(no_ica.loc[key, "mean_difference"]) for key in keys]
        ys = [float(ica.loc[key, "mean_difference"]) for key in keys]
        axis.scatter(xs, ys, color=color, s=28, alpha=0.8, label=label)
    lims = np.array(axis.get_xlim() + axis.get_ylim())
    lo, hi = float(lims.min()), float(lims.max())
    axis.plot([lo, hi], [lo, hi], color=MIST, linewidth=1)
    axis.axhline(0, color=INK, linewidth=0.5, alpha=0.4)
    axis.axvline(0, color=INK, linewidth=0.5, alpha=0.4)
    axis.set_xlabel("No-ICA mean difference")
    axis.set_ylabel("ICA mean difference")
    axis.set_title("4 s effects agree in direction more than in magnitude")
    axis.legend(frameon=False)
    caption(
        figure,
        "Each point is one contrast × feature at 4 s. ICA is primary. "
        "Source: epoch_length_grid_comparison.csv.",
    )
    save(figure, "figure_13_ica_vs_noica")


def plot_task_state(scores: pd.DataFrame, tests: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.8))
    rng = np.random.default_rng(7)
    for axis, feature, label in zip(axes, PRIMARY, PRIMARY.values()):
        values = scores.loc[
            scores["feature"] == feature, "difference"
        ].to_numpy(dtype=float)
        axis.axhline(0, color=INK, linewidth=0.8)
        jitter = rng.normal(0, 0.04, size=len(values))
        axis.scatter(
            jitter,
            values,
            s=36,
            color=NAVY,
            alpha=0.75,
            zorder=3,
        )
        axis.plot(
            [-0.18, 0.18],
            [values.mean(), values.mean()],
            color=CLAY,
            linewidth=2.4,
        )
        test = tests[tests["feature"] == feature].iloc[0]
        holm = test["p_t_holm"]
        holm_s = f"{float(holm):.3f}" if holm != "" else "—"
        axis.set_title(
            f"{label}\nHolm p = {holm_s}{holm_star(float(holm) if holm != '' else math.nan)}"
        )
        axis.set_xticks([])
        axis.set_ylabel("Writing − reading (person median, dB)")
        axis.set_xlim(-0.45, 0.45)
    figure.suptitle("Positive control: writing minus reading (4 s, ICA)", y=1.03)
    caption(
        figure,
        "Each point is one participant’s median of turn-level writing−reading "
        "differences. Orange bar = mean. Not a Q1/Q2 confirmatory test.",
    )
    save(figure, "figure_14_task_state")


def plot_task_state_slopes(pairs: pd.DataFrame, tests: pd.DataFrame) -> None:
    eligible = pairs[pairs["primary_analysis_eligible"] == "yes"]
    figure, axes = plt.subplots(1, 2, figsize=(10.4, 4.9))
    for axis, feature, label in zip(axes, PRIMARY, PRIMARY.values()):
        reading = eligible.groupby("subject_id")[f"{feature}_reading"].median()
        writing = eligible.groupby("subject_id")[f"{feature}_writing"].median()
        subjects = reading.index.intersection(writing.index)
        left = reading.loc[subjects].to_numpy(dtype=float)
        right = writing.loc[subjects].to_numpy(dtype=float)
        for a, b in zip(left, right):
            axis.plot([0, 1], [a, b], color=MIST, linewidth=0.95)
        axis.scatter(np.zeros(len(left)), left, color=SLATE, s=20, zorder=3)
        axis.scatter(np.ones(len(right)), right, color=NAVY, s=20, zorder=3)
        axis.plot(
            [0, 1],
            [left.mean(), right.mean()],
            color=CLAY,
            linewidth=2.3,
            zorder=4,
        )
        test = tests[tests["feature"] == feature].iloc[0]
        holm = test["p_t_holm"]
        holm_s = f"{float(holm):.3f}" if holm != "" else "—"
        axis.set_xticks([0, 1], ["Reading", "Writing"])
        axis.set_ylabel(label)
        axis.set_title(f"{label} · Holm p = {holm_s}")
    figure.suptitle(
        "Same 4 s chain recovers writing > reading Fz theta",
        y=1.03,
    )
    caption(
        figure,
        "Each grey line is one participant (median of 13–15 turns). Orange = "
        "mean. Positive control, not a Q1/Q2 test.",
    )
    save(figure, "figure_15_task_state_slopes")


def plot_session_order(scores: pd.DataFrame, tests: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(10.4, 4.8))
    rng = np.random.default_rng(3)
    for axis, feature, label in zip(axes, PRIMARY, PRIMARY.values()):
        frame = scores[scores["feature"] == feature]
        first = frame["first_median"].to_numpy(dtype=float)
        last = frame["last_median"].to_numpy(dtype=float)
        for a, b in zip(first, last):
            axis.plot([0, 1], [a, b], color=MIST, linewidth=0.95)
        axis.scatter(np.zeros(len(first)), first, color=SLATE, s=20, zorder=3)
        axis.scatter(np.ones(len(last)), last, color=NAVY, s=20, zorder=3)
        axis.plot(
            [0, 1],
            [first.mean(), last.mean()],
            color=CLAY,
            linewidth=2.3,
            zorder=4,
        )
        test = tests[tests["feature"] == feature].iloc[0]
        axis.set_xticks([0, 1], ["First condition", "Last condition"])
        axis.set_ylabel(label)
        axis.set_title(f"{label} · p = {float(test['p_t_raw']):.2f}")
        jitter = rng.normal(0, 0.0, size=1)
        _ = jitter
    figure.suptitle("No session-order drift in confirmatory features", y=1.03)
    caption(
        figure,
        "Last minus first condition median within each participant. "
        "Exploratory time-on-task check, not confirmatory.",
    )
    save(figure, "figure_16_session_order")


def main() -> None:
    style()
    condition_features = read_table(GOLD / "condition_features.csv")
    ad_responses = read_table(GOLD / "ad_response_features.csv")
    condition_tests = read_table(STATS / "eeg_condition_contrasts.csv")
    ad_tests = read_table(STATS / "eeg_ad_response_contrasts.csv")
    grid = read_table(STATS / "sensitivity/epoch_length_grid_comparison.csv")
    plot_condition_rainclouds(condition_features)
    plot_confirmatory_forests(condition_tests, ad_tests)
    plot_ad_paired_slopes(ad_responses)
    plot_epoch_grid_heatmap(grid)
    plot_epoch_grid_heatmap_ica_noica(grid)
    plot_epoch_timeline()
    plot_epoch_traces(grid)
    plot_band_profiles(condition_features)
    plot_ica_agreement(grid)
    task_scores = STATS / "task_state/eeg_task_state_contrast_scores.csv"
    task_tests = STATS / "task_state/eeg_task_state_contrasts.csv"
    task_pairs = GOLD / "task_state/task_state_pair_features.csv"
    if task_scores.exists() and task_tests.exists():
        plot_task_state(read_table(task_scores), read_table(task_tests))
        if task_pairs.exists():
            plot_task_state_slopes(read_table(task_pairs), read_table(task_tests))
    else:
        print("task-state plots skipped; run the positive-control pipeline first")
    session = STATS / "task_state/eeg_session_order_contrasts.csv"
    session_scores = STATS / "task_state/eeg_session_order_scores.csv"
    if session.exists() and session_scores.exists():
        plot_session_order(read_table(session_scores), read_table(session))


if __name__ == "__main__":
    main()
