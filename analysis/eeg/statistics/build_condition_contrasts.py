"""Build participant-level EEG condition contrasts and summary statistics."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy import stats


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_features.csv"
)
DEFAULT_OUTPUT_DIR = REPOSITORY_ROOT / (
    "analysis/eeg/statistics/outputs"
)
K37_FEATURES = (
    DEFAULT_OUTPUT_DIR
    / "sensitivity/ad_local_epochs/dataset_a/around/k37/condition_features.csv"
)
ESTIMAND_MARKER = DEFAULT_OUTPUT_DIR / "eeg_condition_contrasts.estimand"
K37_ESTIMAND = "condition_aggregation_k37"
CONDITIONS = (
    "no_ads",
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
)
FEATURE_TIERS = {
    "fz_theta_power_db_uv2": "primary",
    "posterior_alpha_power_db_uv2": "primary",
    "theta_power_db_uv2": "secondary_global",
    "alpha_power_db_uv2": "secondary_global",
    "beta_power_db_uv2": "secondary",
    "faa_log_f4_minus_f3": "secondary",
    "delta_power_db_uv2": "exploratory",
    "gamma_power_db_uv2": "exploratory",
    "delta_relative_power": "exploratory",
    "theta_relative_power": "exploratory",
    "alpha_relative_power": "exploratory",
    "beta_relative_power": "exploratory",
    "gamma_relative_power": "exploratory",
    "engagement_beta_over_alpha_theta": "exploratory",
    "engagement_pope_frontocentral_beta_over_alpha_theta": "exploratory",
    "engagement_kislov_central_beta16_24_over_alpha8_12": "exploratory",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty analysis table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0]),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def mean(values: list[float]) -> float:
    return float(np.mean(np.asarray(values, dtype=float)))


def contrast_functions() -> dict[str, Callable[[dict[str, float]], float]]:
    return {
        "any_ad_vs_no_ads": lambda x: mean(
            [
                x["inline_early"],
                x["inline_late"],
                x["block_early"],
                x["block_late"],
            ]
        )
        - x["no_ads"],
        "inline_vs_block": lambda x: mean(
            [x["inline_early"], x["inline_late"]]
        )
        - mean([x["block_early"], x["block_late"]]),
        "early_vs_late": lambda x: mean(
            [x["inline_early"], x["block_early"]]
        )
        - mean([x["inline_late"], x["block_late"]]),
        "format_x_timing": lambda x: (
            x["inline_early"] - x["inline_late"]
        )
        - (x["block_early"] - x["block_late"]),
    }


def confidence_interval(values: list[float]) -> tuple[float, float]:
    array = np.asarray(values, dtype=float)
    average = float(np.mean(array))
    if len(array) < 2:
        return math.nan, math.nan
    standard_error = float(stats.sem(array))
    critical = float(stats.t.ppf(0.975, len(array) - 1))
    return average - critical * standard_error, average + critical * standard_error


def descriptives(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for feature, tier in FEATURE_TIERS.items():
        for metric, suffix in (
            ("condition_median", "_median"),
            ("condition_mean", "_mean"),
            ("baseline_delta", "_baseline_delta"),
        ):
            column = f"{feature}{suffix}"
            if not rows or column not in rows[0]:
                continue
            for condition in CONDITIONS:
                values = [
                    float(row[column])
                    for row in rows
                    if row["condition"] == condition
                    and row.get(column) not in ("", None)
                ]
                if len(values) < 2:
                    continue
                lower, upper = confidence_interval(values)
                output.append(
                    {
                        "condition": condition,
                        "feature": feature,
                        "feature_tier": tier,
                        "metric": metric,
                        "n_participants": len(values),
                        "mean": mean(values),
                        "sd": float(np.std(values, ddof=1)),
                        "median": float(np.median(values)),
                        "q25": float(np.quantile(values, 0.25)),
                        "q75": float(np.quantile(values, 0.75)),
                        "ci_lower": lower,
                        "ci_upper": upper,
                        "dataset_status": "analysis_ready_condition_v1",
                    }
                )
    return output


def holm_adjust(p_values: list[float]) -> list[float]:
    order = np.argsort(np.asarray(p_values))
    adjusted = np.empty(len(p_values), dtype=float)
    running_max = 0.0
    for rank, index in enumerate(order):
        candidate = (len(p_values) - rank) * p_values[int(index)]
        running_max = max(running_max, candidate)
        adjusted[int(index)] = min(running_max, 1.0)
    return adjusted.tolist()


def test_row(
    *,
    contrast_id: str,
    feature: str,
    tier: str,
    scores: list[float],
    metric: str,
) -> dict[str, Any]:
    array = np.asarray(scores, dtype=float)
    lower, upper = confidence_interval(scores)
    t_result = stats.ttest_1samp(array, popmean=0.0)
    try:
        wilcoxon = stats.wilcoxon(array, alternative="two-sided")
        wilcoxon_stat = float(wilcoxon.statistic)
        wilcoxon_p = float(wilcoxon.pvalue)
    except ValueError:
        wilcoxon_stat = 0.0
        wilcoxon_p = 1.0
    sd = float(np.std(array, ddof=1))
    return {
        "contrast_id": contrast_id,
        "contrast_tier": (
            "primary" if contrast_id != "format_x_timing" else "secondary"
        ),
        "feature": feature,
        "feature_tier": tier,
        "metric": metric,
        "n_participants": len(scores),
        "mean_difference": mean(scores),
        "sd_difference": sd,
        "se_difference": float(stats.sem(array)),
        "ci_lower": lower,
        "ci_upper": upper,
        "cohen_dz": mean(scores) / sd if sd > 0 else math.nan,
        "t_statistic": float(t_result.statistic),
        "degrees_of_freedom": len(scores) - 1,
        "p_t_raw": float(t_result.pvalue),
        "p_t_holm": "",
        "wilcoxon_statistic": wilcoxon_stat,
        "p_wilcoxon_raw": wilcoxon_p,
        "p_wilcoxon_holm": "",
        "correction_family": (
            f"primary_condition_contrasts__{feature}"
            if contrast_id != "format_x_timing"
            else "secondary_uncorrected"
        ),
        "dataset_status": "analysis_ready_condition_v1",
    }


def contrast_tables(
    rows: list[dict[str, str]],
    *,
    feature_suffix: str = "_median",
    metric: str = "condition_median",
    drop_incomplete_subjects: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_subject: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_subject[row["subject_id"]][row["condition"]] = row
    complete = {
        subject_id: subject
        for subject_id, subject in by_subject.items()
        if set(subject) == set(CONDITIONS)
    }
    incomplete = sorted(set(by_subject) - set(complete))
    if incomplete and not drop_incomplete_subjects:
        raise ValueError(
            f"{incomplete[0]} lacks complete condition cells: "
            f"{set(by_subject[incomplete[0]])}"
        )
    if not complete:
        raise ValueError("No participants have all five condition cells")
    if incomplete:
        print(
            "Dropping incomplete Dataset A subjects: " + ", ".join(incomplete),
            flush=True,
        )
    contrast_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    functions = contrast_functions()
    for feature, tier in FEATURE_TIERS.items():
        scores_by_contrast: dict[str, list[float]] = defaultdict(list)
        for subject_id in sorted(complete):
            subject = complete[subject_id]
            values = {
                condition: float(subject[condition][f"{feature}{feature_suffix}"])
                for condition in CONDITIONS
            }
            for contrast_id, function in functions.items():
                score = function(values)
                scores_by_contrast[contrast_id].append(score)
                score_rows.append(
                    {
                        "subject_id": subject_id,
                        "contrast_id": contrast_id,
                        "feature": feature,
                        "feature_tier": tier,
                        "difference": score,
                    }
                )
        for contrast_id in functions:
            contrast_rows.append(
                test_row(
                    contrast_id=contrast_id,
                    feature=feature,
                    tier=tier,
                    scores=scores_by_contrast[contrast_id],
                    metric=metric,
                )
            )

    for feature in FEATURE_TIERS:
        family = [
            row
            for row in contrast_rows
            if row["feature"] == feature
            and row["contrast_tier"] == "primary"
        ]
        adjusted_t = holm_adjust([float(row["p_t_raw"]) for row in family])
        adjusted_w = holm_adjust(
            [float(row["p_wilcoxon_raw"]) for row in family]
        )
        for row, p_t, p_w in zip(family, adjusted_t, adjusted_w):
            row["p_t_holm"] = p_t
            row["p_wilcoxon_holm"] = p_w
    return contrast_rows, score_rows


def refuse_confirmatory_clobber(
    input_path: Path,
    output_dir: Path,
    *,
    force: bool = False,
) -> None:
    """Block whole-window writes onto the reported Dataset A tables."""
    if force:
        return
    if output_dir.resolve() != DEFAULT_OUTPUT_DIR.resolve():
        return
    if not ESTIMAND_MARKER.exists():
        return
    if ESTIMAND_MARKER.read_text(encoding="utf-8").strip() != K37_ESTIMAND:
        return
    if input_path.resolve() == K37_FEATURES.resolve():
        return
    raise SystemExit(
        "Refusing to overwrite confirmatory Dataset A "
        f"({K37_ESTIMAND}) with {input_path}. "
        "Write to a sensitivity --output-dir, run "
        "run_equal_n_dataset_a.py, or pass "
        "--force-overwrite-confirmatory."
    )


def run(
    input_path: Path,
    output_dir: Path,
    *,
    feature_suffix: str = "_median",
    metric: str = "condition_median",
    expected_condition_rows: int | None = 90,
    drop_incomplete_subjects: bool = False,
    force_overwrite_confirmatory: bool = False,
) -> None:
    refuse_confirmatory_clobber(
        input_path,
        output_dir,
        force=force_overwrite_confirmatory,
    )
    rows = [
        row
        for row in read_csv(input_path)
        if row["window_type"] == "condition"
        and row["primary_analysis_eligible"] == "yes"
    ]
    if (
        expected_condition_rows is not None
        and len(rows) != expected_condition_rows
    ):
        raise ValueError(
            f"Expected {expected_condition_rows} eligible condition rows, "
            f"found {len(rows)}"
        )
    descriptive_rows = descriptives(rows)
    contrast_rows, score_rows = contrast_tables(
        rows,
        feature_suffix=feature_suffix,
        metric=metric,
        drop_incomplete_subjects=drop_incomplete_subjects,
    )
    write_csv(output_dir / "eeg_condition_descriptives.csv", descriptive_rows)
    write_csv(output_dir / "eeg_condition_contrasts.csv", contrast_rows)
    write_csv(output_dir / "eeg_condition_contrast_scores.csv", score_rows)
    print(f"Wrote {len(descriptive_rows)} descriptive rows")
    print(f"Wrote {len(contrast_rows)} contrast-test rows")
    print(f"Wrote {len(score_rows)} participant contrast scores")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--feature-suffix",
        default="_median",
        help="Window-summary suffix, e.g. _median or _mean.",
    )
    parser.add_argument(
        "--metric",
        default="condition_median",
        help="Label written to the metric column.",
    )
    parser.add_argument(
        "--allow-partial-cohort",
        action="store_true",
        help=(
            "Drop subjects missing a condition cell instead of requiring "
            "exactly 90 eligible condition rows."
        ),
    )
    parser.add_argument(
        "--force-overwrite-confirmatory",
        action="store_true",
        help=(
            "Allow writing whole-window Dataset A onto the default "
            "statistics/outputs tables. Off by default once k=37 is marked."
        ),
    )
    args = parser.parse_args()
    run(
        args.input,
        args.output_dir,
        feature_suffix=args.feature_suffix,
        metric=args.metric,
        expected_condition_rows=(
            None if args.allow_partial_cohort else 90
        ),
        drop_incomplete_subjects=args.allow_partial_cohort,
        force_overwrite_confirmatory=args.force_overwrite_confirmatory,
    )


if __name__ == "__main__":
    main()
