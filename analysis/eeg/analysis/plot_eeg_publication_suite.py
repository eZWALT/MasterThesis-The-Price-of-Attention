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


ROOT = Path(__file__).resolve().parents[3]
STATS = ROOT / "analysis/eeg/statistics/outputs"
GOLD = ROOT / "src/project/logs/xdf/gold/features"
OUT = Path(__file__).resolve().parent / "outputs" / "figures" / "suite"

NAVY = "#1B3A4B"
CLAY = "#C45C26"
TEAL = "#2A6F6F"
SLATE = "#5C6B73"
MIST = "#D5DDE3"
INK = "#12202A"
PRIMARY = {
    "fz_theta_power_db_uv2": "Fz theta (dB µV²)",
    "posterior_alpha_power_db_uv2": "Posterior alpha (dB µV²)",
}
CONDITIONS = [
    "no_ads",
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
]
CONDITION_LABELS = {
    "no_ads": "No ads",
    "inline_early": "Inline early",
    "inline_late": "Inline late",
    "block_early": "Block early",
    "block_late": "Block late",
}
PATH_A_LABELS = {
    "any_ad_vs_no_ads": "Any ad − no ads",
    "inline_vs_block": "Inline − block",
    "early_vs_late": "Early − late",
}
PATH_B_LABELS = {
    "inline_early_vs_no_ad_early": "Inline early",
    "block_early_vs_no_ad_early": "Block early",
    "inline_late_vs_no_ad_late": "Inline late",
    "block_late_vs_no_ad_late": "Block late",
}
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
        figure.savefig(path, bbox_inches="tight", facecolor="white")
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
    figure.suptitle("Condition medians by participant (Path A, 4 s, ICA)", y=1.02)
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
                & (condition["contrast_id"].isin(PATH_A_LABELS))
            ],
            PATH_A_LABELS,
            "Path A · sustained condition",
        ),
        (
            axes[1],
            ad[
                (ad["feature"].isin(PRIMARY))
                & (ad["contrast_id"].isin(PATH_B_LABELS))
            ],
            PATH_B_LABELS,
            "Path B · ad-locked post−pre vs matched no-ad",
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
            star = holm_star(float(row["p_t_holm"]) if row["p_t_holm"] != "" else math.nan)
            if star:
                axis.text(
                    row["ci_upper"] + 0.04 * max(abs(frame["ci_upper"]).max(), 1),
                    positions[index],
                    star,
                    va="center",
                    color=CLAY,
                    fontsize=11,
                )
        axis.axvline(0, color=INK, linewidth=0.8)
        axis.set_yticks(
            positions,
            [
                f"{labels[row.contrast_id]}\n{PRIMARY[row.feature]}"
                for row in frame.itertuples()
            ],
        )
        axis.invert_yaxis()
        axis.set_xlabel("Mean within-person difference (95% t CI)")
        axis.set_title(title)
    figure.suptitle("Confirmatory EEG contrasts at the pre-specified 4 s width", y=1.02)
    caption(
        figure,
        "Navy = Fz theta; teal = posterior alpha. Asterisks mark Holm p < 0.05 "
        "within each feature’s primary family. Primary is 4 s + median + ICA.",
    )
    save(figure, "figure_08_confirmatory_forests")


def plot_ad_paired_slopes(ad_responses: pd.DataFrame) -> None:
    cells = [
        ("inline_early", "no_ads_early", "Inline early"),
        ("block_early", "no_ads_early", "Block early"),
        ("inline_late", "no_ads_late", "Inline late"),
        ("block_late", "no_ads_late", "Block late"),
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
    contrasts = list(PATH_B_LABELS)
    features = list(PRIMARY)
    lengths = [2.0, 4.0, 8.0, 16.0, 32.0]
    matrix = np.full((len(features) * len(contrasts), len(lengths)), np.nan)
    labels = []
    for i, feature in enumerate(features):
        for j, contrast in enumerate(contrasts):
            labels.append(f"{PRIMARY[feature]} · {PATH_B_LABELS[contrast]}")
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
    axis.set_title("Path B confirmatory Holm p across epoch lengths (ICA)")
    figure.colorbar(image, ax=axis, fraction=0.03, pad=0.02, label="Holm p")
    caption(
        figure,
        "Orange cells are Holm < 0.05. Holm is within feature at each length, "
        "not across the grid. Primary remains 4 s.",
    )
    save(figure, "figure_10_epoch_grid_heatmap")


def plot_epoch_traces(grid: pd.DataFrame) -> None:
    figure, axes = plt.subplots(1, 2, figsize=(11.4, 4.8), sharey=True)
    traces = (
        (
            axes[0],
            "fz_theta_power_db_uv2",
            "block_early_vs_no_ad_early",
            "Fz theta · block early − no-ad",
        ),
        (
            axes[1],
            "posterior_alpha_power_db_uv2",
            "block_late_vs_no_ad_late",
            "Posterior alpha · block late − no-ad",
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
        "Five global bands from Path A window medians. Overlapping lines are "
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
    for path, color, label in (("A", NAVY, "Path A"), ("B", CLAY, "Path B")):
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
