"""Generate reproducible publication-oriented EEG analysis artifacts.

This module reads immutable Gold feature tables and versioned statistical
outputs. It never rewrites preprocessing data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from condition_labels import (
    AD_CONTRAST_LABELS,
    CONDITION_CONTRAST_LABELS,
    CONDITION_LABELS,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ANALYSIS_ROOT / "analysis_config.json"
DEFAULT_OUTPUT = ANALYSIS_ROOT / "outputs"
AUDITED_RECORDING_COUNT = 19
PROTOCOL_EXCLUSION_COUNT = 1

GOLD_ROOT = REPOSITORY_ROOT / "src/project/logs/xdf/gold/features"
STATISTICS_ROOT = REPOSITORY_ROOT / "analysis/eeg/statistics/outputs"
VALIDATION_ROOT = REPOSITORY_ROOT / "src/project/logs/xdf/gold/validation"

INPUTS = {
    "condition_features": GOLD_ROOT / "condition_features.csv",
    "condition_epochs": GOLD_ROOT / "condition_epoch_features.csv",
    "ad_responses": GOLD_ROOT / "ad_response_features.csv",
    "condition_validation": GOLD_ROOT / "condition_feature_validation.json",
    "ad_validation": GOLD_ROOT / "ad_feature_validation.json",
    "engagement_validation": GOLD_ROOT / "engagement_feature_validation.json",
    "soundness_validation": (
        VALIDATION_ROOT / "preprocessing_soundness.json"
    ),
    "condition_tests": STATISTICS_ROOT / "eeg_condition_contrasts.csv",
    "condition_scores": (
        STATISTICS_ROOT / "eeg_condition_contrast_scores.csv"
    ),
    "ad_tests": STATISTICS_ROOT / "eeg_ad_response_contrasts.csv",
    "ad_scores": STATISTICS_ROOT / "eeg_ad_response_contrast_scores.csv",
    "threshold_comparison": (
        STATISTICS_ROOT / "threshold_sensitivity_comparison.json"
    ),
    "condition_tests_1000": (
        STATISTICS_ROOT
        / "sensitivity/frozen_v1/eeg_condition_contrasts.csv"
    ),
    "condition_tests_1500": (
        STATISTICS_ROOT
        / "sensitivity/frozen_v2/eeg_condition_contrasts.csv"
    ),
    "ad_tests_1000": (
        STATISTICS_ROOT
        / "sensitivity/frozen_v1/eeg_ad_response_contrasts.csv"
    ),
    "ad_tests_1500": (
        STATISTICS_ROOT
        / "sensitivity/frozen_v2/eeg_ad_response_contrasts.csv"
    ),
}

POLICY_PATHS = {
    "frozen_v1_1000_uv": (
        REPOSITORY_ROOT
        / "analysis/eeg/preprocessing/silver/signal/"
        "cleaning_policy_frozen_v1.json"
    ),
    "frozen_v3_1050_uv": (
        REPOSITORY_ROOT
        / "analysis/eeg/preprocessing/silver/signal/cleaning_policy.json"
    ),
    "frozen_v2_1500_uv": (
        REPOSITORY_ROOT
        / "analysis/eeg/preprocessing/silver/signal/"
        "cleaning_policy_frozen_v2.json"
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.18,
            "grid.linewidth": 0.6,
            "legend.frameon": False,
            "figure.constrained_layout.use": False,
        }
    )


def save_figure(
    figure: plt.Figure,
    output_stem: Path,
) -> list[Path]:
    paths = []
    figure.tight_layout(rect=(0, 0.07, 1, 0.98))
    for suffix in (".png", ".pdf"):
        path = output_stem.with_suffix(suffix)
        figure.savefig(path, bbox_inches="tight")
        paths.append(path)
    plt.close(figure)
    return paths


def feature_label(feature: str, config: dict[str, Any]) -> str:
    for group in (
        "primary_features",
        "secondary_features",
        "exploratory_features",
    ):
        if feature in config[group]:
            return str(config[group][feature])
    return feature


def holm_adjust(p_values: np.ndarray) -> np.ndarray:
    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)
    running_max = 0.0
    for rank, index in enumerate(order):
        candidate = (len(p_values) - rank) * p_values[index]
        running_max = max(running_max, candidate)
        adjusted[index] = min(running_max, 1.0)
    return adjusted


def add_global_primary_holm(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["p_t_holm_global_primary_family"] = holm_adjust(
        output["p_t_raw"].to_numpy(dtype=float)
    )
    output["global_family_significant"] = (
        output["p_t_holm_global_primary_family"] < 0.05
    )
    return output


def enrich_results(
    frame: pd.DataFrame,
    *,
    analysis: str,
    config: dict[str, Any],
) -> pd.DataFrame:
    labels = config[
        "condition_contrast_labels"
        if analysis == "condition"
        else "ad_contrast_labels"
    ]
    output = frame.copy()
    output.insert(0, "analysis", analysis)
    output.insert(
        2,
        "contrast_label",
        output["contrast_id"].map(labels).fillna(output["contrast_id"]),
    )
    output.insert(
        5,
        "feature_label",
        output["feature"].map(
            lambda value: feature_label(str(value), config)
        ),
    )
    output["holm_significant"] = (
        pd.to_numeric(output["p_t_holm"], errors="coerce")
        < float(config["alpha"])
    )
    return output


def bootstrap_mean_ci(
    values: np.ndarray,
    *,
    iterations: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    draws = rng.choice(
        values,
        size=(iterations, len(values)),
        replace=True,
    )
    means = draws.mean(axis=1)
    return (
        float(np.quantile(means, 0.025)),
        float(np.quantile(means, 0.975)),
    )


def rank_biserial(values: np.ndarray) -> float:
    nonzero = values[~np.isclose(values, 0.0)]
    if len(nonzero) == 0:
        return 0.0
    ranks = stats.rankdata(np.abs(nonzero))
    positive = float(ranks[nonzero > 0].sum())
    negative = float(ranks[nonzero < 0].sum())
    return (positive - negative) / (positive + negative)


def diagnostic_rows(
    scores: pd.DataFrame,
    *,
    analysis: str,
    config: dict[str, Any],
    rng: np.random.Generator,
) -> pd.DataFrame:
    primary_features = set(config["primary_features"])
    rows: list[dict[str, Any]] = []
    selected = scores[scores["feature"].isin(primary_features)]
    for (contrast_id, feature), group in selected.groupby(
        ["contrast_id", "feature"],
        sort=True,
    ):
        values = group["difference"].to_numpy(dtype=float)
        shapiro = stats.shapiro(values)
        q1, q3 = np.quantile(values, [0.25, 0.75])
        iqr = q3 - q1
        outlier_count = int(
            np.sum((values < q1 - 1.5 * iqr) | (values > q3 + 1.5 * iqr))
        )
        bootstrap_low, bootstrap_high = bootstrap_mean_ci(
            values,
            iterations=int(config["bootstrap_iterations"]),
            rng=rng,
        )
        full_mean = float(values.mean())
        leave_one_out = np.array(
            [np.delete(values, index).mean() for index in range(len(values))]
        )
        if math.isclose(full_mean, 0.0):
            sign_stability = float(np.mean(np.isclose(leave_one_out, 0.0)))
        else:
            sign_stability = float(
                np.mean(np.sign(leave_one_out) == np.sign(full_mean))
            )
        rows.append(
            {
                "analysis": analysis,
                "contrast_id": contrast_id,
                "feature": feature,
                "feature_label": feature_label(str(feature), config),
                "n_participants": len(values),
                "mean_difference": full_mean,
                "median_difference": float(np.median(values)),
                "skewness": float(stats.skew(values, bias=False)),
                "shapiro_w": float(shapiro.statistic),
                "shapiro_p": float(shapiro.pvalue),
                "rank_biserial": rank_biserial(values),
                "iqr_outlier_count": outlier_count,
                "bootstrap_mean_ci_lower": bootstrap_low,
                "bootstrap_mean_ci_upper": bootstrap_high,
                "leave_one_out_sign_stability": sign_stability,
                "maximum_leave_one_out_mean_shift": float(
                    np.max(np.abs(leave_one_out - full_mean))
                ),
            }
        )
    return pd.DataFrame(rows)


def subject14_influence_rows(
    scores: pd.DataFrame,
    *,
    analysis: str,
    config: dict[str, Any],
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    selected = scores[scores["feature"].isin(config["primary_features"])]
    for (contrast_id, feature), group in selected.groupby(
        ["contrast_id", "feature"],
        sort=True,
    ):
        full = group["difference"].to_numpy(dtype=float)
        without = group.loc[
            ~group["subject_id"].eq("lab_subject_14"),
            "difference",
        ].to_numpy(dtype=float)
        full_mean = float(full.mean())
        without_mean = float(without.mean())
        full_sd = float(full.std(ddof=1))
        without_sd = float(without.std(ddof=1))
        rows.append(
            {
                "analysis": analysis,
                "contrast_id": contrast_id,
                "feature": feature,
                "feature_label": feature_label(str(feature), config),
                "full_n": len(full),
                "without_subject14_n": len(without),
                "full_mean_difference": full_mean,
                "without_subject14_mean_difference": without_mean,
                "mean_shift": without_mean - full_mean,
                "full_cohen_dz": (
                    full_mean / full_sd if full_sd > 0 else math.nan
                ),
                "without_subject14_cohen_dz": (
                    without_mean / without_sd
                    if without_sd > 0
                    else math.nan
                ),
                "direction_changed": (
                    np.sign(full_mean) != np.sign(without_mean)
                ),
            }
        )
    return pd.DataFrame(rows)


def plot_data_flow(
    condition_validation: dict[str, Any],
    ad_validation: dict[str, Any],
    output_stem: Path,
) -> list[Path]:
    labels = [
        "Audited recordings",
        "Analyzed participants",
        "Condition windows",
        "Condition epochs",
        "Retained condition epochs",
        "Ad/no-ad pairs",
        "Eligible ad/no-ad pairs",
    ]
    values = [
        AUDITED_RECORDING_COUNT,
        condition_validation["subject_count"],
        condition_validation["window_count"],
        condition_validation["epoch_count"],
        condition_validation["retained_epoch_count"],
        ad_validation["response_pair_count"],
        ad_validation["eligible_response_pair_count"],
    ]
    colors = [
        "#9AA6B2",
        "#355C7D",
        "#6C8EAD",
        "#9AA6B2",
        "#4C956C",
        "#B07D62",
        "#4C956C",
    ]
    figure, axis = plt.subplots(figsize=(8.2, 4.4))
    positions = np.arange(len(labels))
    bars = axis.barh(positions, values, color=colors)
    axis.set_yticks(positions, labels)
    axis.invert_yaxis()
    axis.set_xlabel("Count")
    axis.set_title("EEG analysis cohort and retained observations")
    maximum = max(values)
    for bar, value in zip(bars, values):
        axis.text(
            bar.get_width() + maximum * 0.012,
            bar.get_y() + bar.get_height() / 2,
            f"{value:,}",
            va="center",
        )
    axis.set_xlim(0, maximum * 1.13)
    figure.text(
        0.01,
        0.01,
        "Source: frozen_v3 Gold validation; counts use participants, windows, "
        "four-second epochs, and response pairs.",
        fontsize=8,
    )
    return save_figure(figure, output_stem)


def plot_forest(
    frame: pd.DataFrame,
    *,
    title: str,
    label_column: str,
    output_stem: Path,
) -> list[Path]:
    plot_frame = frame.copy().reset_index(drop=True)
    plot_frame["display"] = (
        plot_frame[label_column] + "\n" + plot_frame["feature_label"]
    )
    positions = np.arange(len(plot_frame))
    palette = {
        feature: color
        for feature, color in zip(
            plot_frame["feature"].drop_duplicates(),
            ("#355C7D", "#B07D62", "#4C956C", "#8C6BB1"),
        )
    }
    figure_height = max(4.2, len(plot_frame) * 0.48)
    figure, axis = plt.subplots(figsize=(9.2, figure_height))
    for index, row in plot_frame.iterrows():
        axis.errorbar(
            row["mean_difference"],
            positions[index],
            xerr=np.array(
                [
                    [row["mean_difference"] - row["ci_lower"]],
                    [row["ci_upper"] - row["mean_difference"]],
                ]
            ),
            fmt="o",
            color=palette[row["feature"]],
            capsize=3,
            markersize=5,
        )
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_yticks(positions, plot_frame["display"])
    axis.invert_yaxis()
    axis.set_xlabel("Mean within-participant difference (95% t CI)")
    axis.set_title(title)
    figure.text(
        0.01,
        0.01,
        "Points are participant-level mean contrasts; intervals are "
        "two-sided 95% t confidence intervals. Holm correction is reported "
        "in the companion table.",
        fontsize=8,
    )
    return save_figure(figure, output_stem)


def plot_condition_profiles(
    condition_features: pd.DataFrame,
    config: dict[str, Any],
    output_stem: Path,
) -> list[Path]:
    conditions = list(config["condition_labels"])
    figure, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), sharex=True)
    for axis, (feature, label) in zip(
        axes,
        config["primary_features"].items(),
    ):
        column = f"{feature}_median"
        pivot = condition_features.pivot(
            index="subject_id",
            columns="condition",
            values=column,
        )[conditions]
        x = np.arange(len(conditions))
        for _, participant in pivot.iterrows():
            axis.plot(
                x,
                participant.to_numpy(dtype=float),
                color="#AAB2B8",
                alpha=0.45,
                linewidth=0.7,
            )
        mean_values = pivot.mean(axis=0).to_numpy(dtype=float)
        sem_values = pivot.sem(axis=0).to_numpy(dtype=float)
        axis.errorbar(
            x,
            mean_values,
            yerr=sem_values,
            color="#19324A",
            marker="o",
            linewidth=2.2,
            capsize=3,
            label="Mean ± SEM",
        )
        axis.set_title(label)
        axis.set_xticks(
            x,
            [config["condition_labels"][value] for value in conditions],
            rotation=28,
            ha="right",
        )
        axis.set_ylabel("Window median (dB µV²)")
        axis.legend(loc="best")
    figure.suptitle("Participant-level EEG profiles across experimental conditions")
    figure.text(
        0.01,
        0.01,
        "Grey lines represent participants (n=18); dark line is the "
        "participant mean. Baseline is excluded from confirmatory profiles.",
        fontsize=8,
    )
    return save_figure(figure, output_stem)


def plot_score_distributions(
    condition_scores: pd.DataFrame,
    ad_scores: pd.DataFrame,
    config: dict[str, Any],
    output_stem: Path,
) -> list[Path]:
    feature = "fz_theta_power_db_uv2"
    panels = [
        (
            condition_scores[
                (condition_scores["feature"] == feature)
                & (
                    condition_scores["contrast_id"].isin(
                        [
                            "any_ad_vs_no_ads",
                            "inline_vs_block",
                            "early_vs_late",
                        ]
                    )
                )
            ],
            config["condition_contrast_labels"],
            "Sustained-condition contrasts",
        ),
        (
            ad_scores[
                (ad_scores["feature"] == feature)
                & (
                    ad_scores["contrast_id"].isin(
                        [
                            "inline_early_vs_no_ad_early",
                            "block_early_vs_no_ad_early",
                            "inline_late_vs_no_ad_late",
                            "block_late_vs_no_ad_late",
                        ]
                    )
                )
            ],
            config["ad_contrast_labels"],
            "Ad-locked post − pre contrasts",
        ),
    ]
    figure, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    rng = np.random.default_rng(int(config["random_seed"]))
    for axis, (frame, labels, title) in zip(axes, panels):
        contrast_ids = list(frame["contrast_id"].drop_duplicates())
        for index, contrast_id in enumerate(contrast_ids):
            values = frame.loc[
                frame["contrast_id"] == contrast_id,
                "difference",
            ].to_numpy(dtype=float)
            jitter = rng.normal(0, 0.045, size=len(values))
            axis.scatter(
                np.full(len(values), index) + jitter,
                values,
                color="#6C8EAD",
                alpha=0.72,
                s=22,
            )
            axis.plot(
                [index - 0.2, index + 0.2],
                [values.mean(), values.mean()],
                color="#8A2D2D",
                linewidth=2.2,
            )
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_xticks(
            np.arange(len(contrast_ids)),
            [labels[value] for value in contrast_ids],
            rotation=32,
            ha="right",
        )
        axis.set_ylabel("Participant contrast (dB µV²)")
        axis.set_title(title)
    figure.suptitle("Fz theta participant-level contrast distributions")
    figure.text(
        0.01,
        0.01,
        "Each point is one participant; red segments show arithmetic means. "
        "Source: frozen_v3 participant contrast tables.",
        fontsize=8,
    )
    return save_figure(figure, output_stem)


def sensitivity_frame(
    primary: pd.DataFrame,
    sensitivity_1000: pd.DataFrame,
    sensitivity_1500: pd.DataFrame,
    *,
    analysis: str,
    config: dict[str, Any],
) -> pd.DataFrame:
    frames = []
    for policy, frame in (
        ("frozen_v1_1000_uv", sensitivity_1000),
        ("frozen_v3_1050_uv", primary),
        ("frozen_v2_1500_uv", sensitivity_1500),
    ):
        selected = frame[
            (frame["feature"].isin(config["primary_features"]))
            & (frame["contrast_tier"] == "primary")
        ].copy()
        selected.insert(0, "analysis", analysis)
        selected.insert(1, "policy", policy)
        selected.insert(
            2,
            "policy_label",
            config["policy_labels"][policy],
        )
        frames.append(selected)
    return pd.concat(frames, ignore_index=True)


def plot_sensitivity(
    condition: pd.DataFrame,
    ad: pd.DataFrame,
    config: dict[str, Any],
    output_stem: Path,
) -> list[Path]:
    figure, axes = plt.subplots(1, 2, figsize=(12.5, 7.0))
    for axis, frame, title, labels in (
        (
            axes[0],
            condition,
            "Condition contrasts",
            config["condition_contrast_labels"],
        ),
        (
            axes[1],
            ad,
            "Ad-response contrasts",
            config["ad_contrast_labels"],
        ),
    ):
        combinations = list(
            frame[["contrast_id", "feature"]]
            .drop_duplicates()
            .itertuples(index=False, name=None)
        )
        policy_offsets = {
            "frozen_v1_1000_uv": -0.18,
            "frozen_v3_1050_uv": 0.0,
            "frozen_v2_1500_uv": 0.18,
        }
        colors = {
            "frozen_v1_1000_uv": "#8C6BB1",
            "frozen_v3_1050_uv": "#19324A",
            "frozen_v2_1500_uv": "#B07D62",
        }
        for policy, policy_frame in frame.groupby("policy", sort=False):
            for index, (contrast_id, feature) in enumerate(combinations):
                row = policy_frame[
                    (policy_frame["contrast_id"] == contrast_id)
                    & (policy_frame["feature"] == feature)
                ].iloc[0]
                axis.plot(
                    row["mean_difference"],
                    index + policy_offsets[policy],
                    "o",
                    color=colors[policy],
                    label=(
                        config["policy_labels"][policy]
                        if index == 0
                        else None
                    ),
                )
        axis.axvline(0, color="black", linewidth=0.8)
        axis.set_yticks(
            np.arange(len(combinations)),
            [
                f"{labels[contrast]}\n{feature_label(feature, config)}"
                for contrast, feature in combinations
            ],
        )
        axis.invert_yaxis()
        axis.set_xlabel("Mean within-participant difference")
        axis.set_title(title)
        axis.legend(loc="best")
    figure.suptitle("Primary EEG estimates across artifact thresholds")
    figure.text(
        0.01,
        0.01,
        "Sensitivity policies: 1,000, 1,050, and 1,500 µV peak-to-peak. "
        "Intervals are omitted to emphasize estimate displacement.",
        fontsize=8,
    )
    return save_figure(figure, output_stem)


def quality_gates(
    *,
    condition_features: pd.DataFrame,
    condition_epochs: pd.DataFrame,
    ad_responses: pd.DataFrame,
    condition_tests: pd.DataFrame,
    ad_tests: pd.DataFrame,
    publication_primary_condition: pd.DataFrame,
    publication_primary_ad: pd.DataFrame,
    condition_scores: pd.DataFrame,
    ad_scores: pd.DataFrame,
    condition_validation: dict[str, Any],
    ad_validation: dict[str, Any],
    engagement_validation: dict[str, Any],
    soundness_validation: dict[str, Any],
    threshold_comparison: dict[str, Any],
    expected_outputs: list[Path],
    config: dict[str, Any],
) -> dict[str, Any]:
    primary_features = set(config["primary_features"])
    primary_condition = condition_tests[
        (condition_tests["feature"].isin(primary_features))
        & (condition_tests["contrast_tier"] == "primary")
    ]
    primary_ad = ad_tests[
        (ad_tests["feature"].isin(primary_features))
        & (ad_tests["contrast_tier"] == "primary")
    ]
    condition_rows = condition_features[
        condition_features["window_type"] == "condition"
    ]
    checks = {
        "01_soundness_machine_checks_pass": bool(
            soundness_validation["all_machine_checks_pass"]
        ),
        "02_condition_validation_passes": (
            condition_validation["status"] == "passed"
        ),
        "03_ad_validation_passes": ad_validation["status"] == "passed",
        "04_engagement_validation_passes": (
            engagement_validation["validation_status"] == "pass"
        ),
        "05_expected_18_participants": (
            condition_features["subject_id"].nunique() == 18
            and ad_responses["subject_id"].nunique() == 18
        ),
        "06_complete_condition_cells": (
            len(condition_rows) == 90
            and condition_rows.groupby("subject_id")["condition"].nunique().eq(5).all()
        ),
        "07_complete_ad_reference_cells": (
            len(ad_responses) == 108
            and ad_responses["primary_analysis_eligible"].eq("yes").all()
        ),
        "08_no_duplicate_condition_keys": (
            not condition_features.duplicated(["subject_id", "window_id"]).any()
        ),
        "09_no_duplicate_ad_keys": (
            not ad_responses.duplicated(["subject_id", "reference_id"]).any()
        ),
        "10_primary_policy_is_frozen_v3": (
            condition_features["artifact_policy_status"].eq("frozen_v3").all()
            and ad_responses["artifact_policy_status"].eq("frozen_v3").all()
        ),
        "11_ica_is_primary": (
            condition_features["ica_applied"].eq("yes").all()
            and ad_responses["ica_applied"].eq("yes").all()
        ),
        "12_primary_features_are_complete": (
            not primary_condition[
                ["mean_difference", "ci_lower", "ci_upper", "p_t_holm"]
            ].isna().any().any()
            and not primary_ad[
                ["mean_difference", "ci_lower", "ci_upper", "p_t_holm"]
            ].isna().any().any()
        ),
        "13_primary_participant_scores_are_complete": (
            condition_scores[
                condition_scores["feature"].isin(primary_features)
            ].groupby(["contrast_id", "feature"]).size().eq(18).all()
            and ad_scores[
                ad_scores["feature"].isin(primary_features)
            ].groupby(["contrast_id", "feature"]).size().eq(18).all()
        ),
        "14_holm_values_are_valid": (
            primary_condition["p_t_holm"].between(0, 1).all()
            and primary_ad["p_t_holm"].between(0, 1).all()
            and publication_primary_condition[
                "p_t_holm_global_primary_family"
            ].between(0, 1).all()
            and publication_primary_ad[
                "p_t_holm_global_primary_family"
            ].between(0, 1).all()
        ),
        "15_confidence_intervals_contain_estimates": (
            primary_condition["mean_difference"].between(
                primary_condition["ci_lower"],
                primary_condition["ci_upper"],
            ).all()
            and primary_ad["mean_difference"].between(
                primary_ad["ci_lower"],
                primary_ad["ci_upper"],
            ).all()
        ),
        "16_threshold_sensitivity_passes": (
            threshold_comparison["status"] == "pass"
        ),
        "17_confirmatory_directions_are_threshold_stable": bool(
            threshold_comparison["checks"][
                "all_sensitivities_preserve_confirmatory_directions"
            ]
        ),
        "18_no_baseline_rows_in_confirmatory_condition_tests": (
            condition_tests["metric"].eq("condition_median").all()
        ),
        "19_epoch_keys_are_unique": (
            not condition_epochs.duplicated(
                ["subject_id", "window_id", "epoch_index"]
            ).any()
        ),
        "20_expected_artifacts_exist_and_are_nonempty": all(
            path.exists() and path.stat().st_size > 0
            for path in expected_outputs
        ),
    }
    return {
        "status": "pass" if all(checks.values()) else "failed",
        "passed": sum(checks.values()),
        "total": len(checks),
        "checks": checks,
    }


def write_narrative(
    path: Path,
    *,
    primary_condition: pd.DataFrame,
    primary_ad: pd.DataFrame,
    diagnostics: pd.DataFrame,
    quality: dict[str, Any],
) -> None:
    best_condition = primary_condition.sort_values("p_t_holm").iloc[0]
    best_ad = primary_ad.sort_values("p_t_holm").iloc[0]
    minimum_stability = diagnostics["leave_one_out_sign_stability"].min()
    text = f"""# Initial publication analysis summary

## Scope

This report summarizes the frozen `frozen_v3` EEG datasets for 18 laboratory
participants. It is an initial analysis scaffold, not a final claim of
neurophysiological or causal evidence.

## Confirmatory results

No primary sustained-condition or ad-response contrast survives its
feature-specific Holm family at α=0.05.

The smallest corrected sustained-condition result is
`{best_condition['contrast_id']}` for `{best_condition['feature']}`
(`mean={best_condition['mean_difference']:.3f}`,
`95% CI [{best_condition['ci_lower']:.3f}, {best_condition['ci_upper']:.3f}]`,
`dz={best_condition['cohen_dz']:.3f}`,
`p_Holm={best_condition['p_t_holm']:.3f}`,
`p_global_Holm={best_condition['p_t_holm_global_primary_family']:.3f}`).

The smallest corrected ad-response result is
`{best_ad['contrast_id']}` for `{best_ad['feature']}`
(`mean={best_ad['mean_difference']:.3f}`,
`95% CI [{best_ad['ci_lower']:.3f}, {best_ad['ci_upper']:.3f}]`,
`dz={best_ad['cohen_dz']:.3f}`,
`p_Holm={best_ad['p_t_holm']:.3f}`,
`p_global_Holm={best_ad['p_t_holm_global_primary_family']:.3f}`).

## Robustness

The 1,000 and 1,500 µV sensitivity branches preserve all confirmatory effect
directions and corrected conclusions relative to the 1,050 µV primary policy.
The minimum leave-one-participant-out sign stability across primary-feature
diagnostics is {minimum_stability:.1%}.

## Interpretation boundaries

- The sample is small (`n=18`), so confidence intervals and participant-level
  distributions should lead interpretation.
- Laboratory feedback identifies `Cz` as the online reference and `Fpz` as
  ground; the XDF does not encode those physical roles directly.
- Current feature tables apply the approved 99%-variance ICA branch
  (`Fp1/Fp2` ocular proxies, at most three components). No-ICA remains a
  mandatory sensitivity. Artifact-threshold 1,000/1,500 µV branches were
  computed on the no-ICA 1,050 µV tables and have not been rebuilt under ICA.
- Baseline eye state was uncontrolled and is excluded from confirmatory tests.
- Engagement ratios, FAA, global bands, and uncorrected interactions are
  secondary or exploratory.
- The era-aware read-versus-write positive control is not yet implemented;
  null condition results therefore do not establish universal pipeline
  sensitivity.
- A non-significant result is not evidence of absence; report compatible effect
  ranges and study power limitations.

## Automated quality review

{quality['passed']} of {quality['total']} analysis gates pass.
"""
    path.write_text(text, encoding="utf-8")


def run(config_path: Path, output_root: Path) -> dict[str, Any]:
    config = load_json(config_path)
    config["condition_labels"] = {
        **config.get("condition_labels", {}),
        **CONDITION_LABELS,
    }
    config["condition_contrast_labels"] = {
        **config.get("condition_contrast_labels", {}),
        **CONDITION_CONTRAST_LABELS,
    }
    config["ad_contrast_labels"] = {
        **config.get("ad_contrast_labels", {}),
        **AD_CONTRAST_LABELS,
    }
    configure_style()
    tables = output_root / "tables"
    figures = output_root / "figures"
    reports = output_root / "reports"
    for directory in (tables, figures, reports):
        directory.mkdir(parents=True, exist_ok=True)

    condition_features = pd.read_csv(INPUTS["condition_features"])
    condition_epochs = pd.read_csv(INPUTS["condition_epochs"])
    ad_responses = pd.read_csv(INPUTS["ad_responses"])
    condition_tests = pd.read_csv(INPUTS["condition_tests"])
    condition_scores = pd.read_csv(INPUTS["condition_scores"])
    ad_tests = pd.read_csv(INPUTS["ad_tests"])
    ad_scores = pd.read_csv(INPUTS["ad_scores"])
    condition_validation = load_json(INPUTS["condition_validation"])
    ad_validation = load_json(INPUTS["ad_validation"])
    engagement_validation = load_json(INPUTS["engagement_validation"])
    soundness_validation = load_json(INPUTS["soundness_validation"])
    threshold_comparison = load_json(INPUTS["threshold_comparison"])

    condition_enriched = enrich_results(
        condition_tests,
        analysis="condition",
        config=config,
    )
    ad_enriched = enrich_results(ad_tests, analysis="ad", config=config)
    primary_condition = add_global_primary_holm(
        condition_enriched[
            (condition_enriched["feature_tier"] == "primary")
            & (condition_enriched["contrast_tier"] == "primary")
        ]
    )
    primary_ad = add_global_primary_holm(
        ad_enriched[
            (ad_enriched["feature_tier"] == "primary")
            & (ad_enriched["contrast_tier"] == "primary")
        ]
    )
    exploratory = pd.concat(
        [
            condition_enriched[
                condition_enriched["feature"].isin(
                    config["exploratory_features"]
                )
            ],
            ad_enriched[
                ad_enriched["feature"].isin(
                    config["exploratory_features"]
                )
            ],
        ],
        ignore_index=True,
    )

    rng = np.random.default_rng(int(config["random_seed"]))
    diagnostics = pd.concat(
        [
            diagnostic_rows(
                condition_scores,
                analysis="condition",
                config=config,
                rng=rng,
            ),
            diagnostic_rows(
                ad_scores,
                analysis="ad",
                config=config,
                rng=rng,
            ),
        ],
        ignore_index=True,
    )
    subject14_influence = pd.concat(
        [
            subject14_influence_rows(
                condition_scores,
                analysis="condition",
                config=config,
            ),
            subject14_influence_rows(
                ad_scores,
                analysis="ad",
                config=config,
            ),
        ],
        ignore_index=True,
    )
    onset_provenance = (
        ad_responses.groupby(
            [
                "reference_kind",
                "onset_estimator",
                "onset_status",
            ],
            dropna=False,
        )
        .agg(
            event_count=("reference_id", "size"),
            participant_count=("subject_id", "nunique"),
            maximum_timing_uncertainty_s=(
                "combined_timing_uncertainty_s",
                "max",
            ),
            median_timing_uncertainty_s=(
                "combined_timing_uncertainty_s",
                "median",
            ),
        )
        .reset_index()
    )
    diagnostic_columns = [
        "analysis",
        "contrast_id",
        "feature",
        "shapiro_p",
        "rank_biserial",
        "iqr_outlier_count",
        "bootstrap_mean_ci_lower",
        "bootstrap_mean_ci_upper",
        "leave_one_out_sign_stability",
        "maximum_leave_one_out_mean_shift",
    ]
    primary_condition = primary_condition.merge(
        diagnostics[diagnostic_columns],
        on=["analysis", "contrast_id", "feature"],
        how="left",
        validate="one_to_one",
    )
    primary_ad = primary_ad.merge(
        diagnostics[diagnostic_columns],
        on=["analysis", "contrast_id", "feature"],
        how="left",
        validate="one_to_one",
    )

    condition_sensitivity = sensitivity_frame(
        condition_tests,
        pd.read_csv(INPUTS["condition_tests_1000"]),
        pd.read_csv(INPUTS["condition_tests_1500"]),
        analysis="condition",
        config=config,
    )
    ad_sensitivity = sensitivity_frame(
        ad_tests,
        pd.read_csv(INPUTS["ad_tests_1000"]),
        pd.read_csv(INPUTS["ad_tests_1500"]),
        analysis="ad",
        config=config,
    )
    sensitivity = pd.concat(
        [condition_sensitivity, ad_sensitivity],
        ignore_index=True,
    )

    qc_summary = pd.DataFrame(
        [
            {"metric": "audited_recordings", "value": AUDITED_RECORDING_COUNT},
            {
                "metric": "wrong_protocol_exclusions",
                "value": PROTOCOL_EXCLUSION_COUNT,
            },
            {"metric": "participants", "value": condition_validation["subject_count"]},
            {"metric": "condition_windows", "value": condition_validation["window_count"]},
            {"metric": "condition_epochs", "value": condition_validation["epoch_count"]},
            {
                "metric": "retained_condition_epochs",
                "value": condition_validation["retained_epoch_count"],
            },
            {
                "metric": "retained_condition_fraction",
                "value": condition_validation["retained_epoch_fraction"],
            },
            {"metric": "ad_response_pairs", "value": ad_validation["response_pair_count"]},
            {
                "metric": "eligible_ad_response_pairs",
                "value": ad_validation["eligible_response_pair_count"],
            },
            {
                "metric": "maximum_ad_timing_uncertainty_s",
                "value": ad_validation["maximum_combined_timing_uncertainty_s"],
            },
            {"metric": "artifact_policy", "value": "frozen_v3_1050_uv"},
            {"metric": "ica_applied", "value": "yes"},
        ]
    )

    table_outputs = {
        "cohort_qc_summary": tables / "cohort_qc_summary.csv",
        "primary_condition_results": tables / "primary_condition_results.csv",
        "primary_ad_results": tables / "primary_ad_results.csv",
        "exploratory_engagement_results": (
            tables / "exploratory_engagement_results.csv"
        ),
        "assumption_influence_diagnostics": (
            tables / "assumption_influence_diagnostics.csv"
        ),
        "threshold_sensitivity_results": (
            tables / "threshold_sensitivity_results.csv"
        ),
        "subject14_influence": tables / "subject14_influence.csv",
        "ad_onset_provenance": tables / "ad_onset_provenance.csv",
    }
    for frame, path in (
        (qc_summary, table_outputs["cohort_qc_summary"]),
        (primary_condition, table_outputs["primary_condition_results"]),
        (primary_ad, table_outputs["primary_ad_results"]),
        (exploratory, table_outputs["exploratory_engagement_results"]),
        (diagnostics, table_outputs["assumption_influence_diagnostics"]),
        (sensitivity, table_outputs["threshold_sensitivity_results"]),
        (subject14_influence, table_outputs["subject14_influence"]),
        (onset_provenance, table_outputs["ad_onset_provenance"]),
    ):
        frame.to_csv(path, index=False)

    figure_outputs: list[Path] = []
    figure_outputs += plot_data_flow(
        condition_validation,
        ad_validation,
        figures / "figure_01_data_flow",
    )
    figure_outputs += plot_forest(
        primary_condition,
        title="Primary sustained-condition EEG contrasts",
        label_column="contrast_label",
        output_stem=figures / "figure_02_condition_primary_forest",
    )
    figure_outputs += plot_forest(
        primary_ad,
        title="Primary ad-response EEG contrasts",
        label_column="contrast_label",
        output_stem=figures / "figure_03_ad_primary_forest",
    )
    figure_outputs += plot_condition_profiles(
        condition_features[
            condition_features["window_type"].eq("condition")
        ],
        config,
        figures / "figure_04_condition_profiles",
    )
    figure_outputs += plot_score_distributions(
        condition_scores,
        ad_scores,
        config,
        figures / "figure_05_participant_distributions",
    )
    figure_outputs += plot_sensitivity(
        condition_sensitivity,
        ad_sensitivity,
        config,
        figures / "figure_06_threshold_sensitivity",
    )

    expected_outputs = [*table_outputs.values(), *figure_outputs]
    quality = quality_gates(
        condition_features=condition_features,
        condition_epochs=condition_epochs,
        ad_responses=ad_responses,
        condition_tests=condition_tests,
        ad_tests=ad_tests,
        publication_primary_condition=primary_condition,
        publication_primary_ad=primary_ad,
        condition_scores=condition_scores,
        ad_scores=ad_scores,
        condition_validation=condition_validation,
        ad_validation=ad_validation,
        engagement_validation=engagement_validation,
        soundness_validation=soundness_validation,
        threshold_comparison=threshold_comparison,
        expected_outputs=expected_outputs,
        config=config,
    )
    quality_path = reports / "quality_gates.json"
    quality_path.write_text(
        json.dumps(quality, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )

    narrative_path = reports / "initial_results_summary.md"
    write_narrative(
        narrative_path,
        primary_condition=primary_condition,
        primary_ad=primary_ad,
        diagnostics=diagnostics,
        quality=quality,
    )

    manifest = {
        "analysis_version": config["analysis_version"],
        "status": (
            "initial_publication_scaffold_ready_human_gates_pending"
            if quality["status"] == "pass"
            else "quality_review_required"
        ),
        "analysis_unit": "participant",
        "primary_policy": "frozen_v3_1050_uv",
        "alpha": config["alpha"],
        "multiplicity": {
            "condition": (
                "Holm across three primary contrasts separately per feature"
            ),
            "ad_response": (
                "Holm across four primary ad-versus-control contrasts "
                "separately per feature"
            ),
            "global_primary_sensitivity": (
                "Additional Holm sensitivity across all primary-feature "
                "tests within each analysis"
            ),
        },
        "inputs": {
            name: {
                "path": str(path.relative_to(REPOSITORY_ROOT)),
                "sha256": sha256(path),
            }
            for name, path in {**INPUTS, **POLICY_PATHS}.items()
        },
        "outputs": [
            str(path.relative_to(ANALYSIS_ROOT))
            for path in [
                *expected_outputs,
                quality_path,
                narrative_path,
            ]
        ],
        "quality_gates": quality,
        "human_gates": [
            "Filtering and interpolation figures approved 2026-08-19.",
            "If available, verify Cz/Fpz handling against the acquisition "
            "workspace because Cz is also exported as a dynamic data channel.",
            "ICA is the approved primary branch (2026-08-19). Keep the "
            "no-ICA frozen_v3 tables as a mandatory sensitivity.",
            "Confirm engagement indices remain exploratory.",
            "Implement and interpret the read-versus-write positive control "
            "before treating null condition effects as evidence of pipeline "
            "insensitivity.",
            "Integrate behavioral covariates only after their data contract is frozen.",
        ],
    }
    manifest_path = reports / "analysis_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, default=json_default) + "\n",
        encoding="utf-8",
    )
    if quality["status"] != "pass":
        failed = [key for key, value in quality["checks"].items() if not value]
        raise ValueError(f"Publication analysis quality gates failed: {failed}")
    print(
        f"Generated publication analysis with {quality['passed']}/"
        f"{quality['total']} quality gates passing under {output_root}"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.config.resolve(), args.output_root.resolve())


if __name__ == "__main__":
    main()
