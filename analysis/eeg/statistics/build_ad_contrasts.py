"""Build participant-level pre/post advertisement EEG response contrasts."""

from __future__ import annotations

import argparse
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np
from scipy import stats

from build_condition_contrasts import (
    FEATURE_TIERS,
    confidence_interval,
    holm_adjust,
    mean,
    read_csv,
    write_csv,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_response_features.csv"
)
DEFAULT_OUTPUT_DIR = REPOSITORY_ROOT / "analysis/eeg/statistics/outputs"


def cell_name(row: dict[str, str]) -> str:
    if row["reference_kind"] == "matched_no_ad_reply":
        return f"no_ads_{row['matched_timing']}"
    return row["condition"]


def contrast_functions() -> dict[
    str,
    tuple[str, Callable[[dict[str, float]], float]],
]:
    return {
        "inline_early_vs_no_ad_early": (
            "primary",
            lambda x: x["inline_early"] - x["no_ads_early"],
        ),
        "block_early_vs_no_ad_early": (
            "primary",
            lambda x: x["block_early"] - x["no_ads_early"],
        ),
        "inline_late_vs_no_ad_late": (
            "primary",
            lambda x: x["inline_late"] - x["no_ads_late"],
        ),
        "block_late_vs_no_ad_late": (
            "primary",
            lambda x: x["block_late"] - x["no_ads_late"],
        ),
        "any_ad_vs_matched_no_ad": (
            "secondary",
            lambda x: mean(
                [
                    x["inline_early"],
                    x["block_early"],
                    x["inline_late"],
                    x["block_late"],
                ]
            )
            - mean([x["no_ads_early"], x["no_ads_late"]]),
        ),
        "inline_vs_block": (
            "secondary",
            lambda x: mean([x["inline_early"], x["inline_late"]])
            - mean([x["block_early"], x["block_late"]]),
        ),
        "early_vs_late": (
            "secondary",
            lambda x: mean([x["inline_early"], x["block_early"]])
            - mean([x["inline_late"], x["block_late"]]),
        ),
        "format_x_timing": (
            "secondary",
            lambda x: (x["inline_early"] - x["inline_late"])
            - (x["block_early"] - x["block_late"]),
        ),
    }


def test_row(
    *,
    contrast_id: str,
    contrast_tier: str,
    feature: str,
    feature_tier: str,
    values: list[float],
) -> dict[str, Any]:
    array = np.asarray(values, dtype=float)
    lower, upper = confidence_interval(values)
    t_result = stats.ttest_1samp(array, 0.0)
    try:
        wilcoxon = stats.wilcoxon(array)
        w_stat = float(wilcoxon.statistic)
        w_p = float(wilcoxon.pvalue)
    except ValueError:
        w_stat, w_p = 0.0, 1.0
    sd = float(np.std(array, ddof=1))
    return {
        "contrast_id": contrast_id,
        "contrast_tier": contrast_tier,
        "feature": feature,
        "feature_tier": feature_tier,
        "response_metric": "post_minus_pre",
        "n_participants": len(values),
        "mean_difference": mean(values),
        "sd_difference": sd,
        "se_difference": float(stats.sem(array)),
        "ci_lower": lower,
        "ci_upper": upper,
        "cohen_dz": mean(values) / sd if sd > 0 else math.nan,
        "t_statistic": float(t_result.statistic),
        "degrees_of_freedom": len(values) - 1,
        "p_t_raw": float(t_result.pvalue),
        "p_t_holm": "",
        "wilcoxon_statistic": w_stat,
        "p_wilcoxon_raw": w_p,
        "p_wilcoxon_holm": "",
        "correction_family": (
            f"primary_ad_responses__{feature}"
            if contrast_tier == "primary"
            else "secondary_uncorrected"
        ),
        "dataset_status": "analysis_ready_ad_v1",
    }


def run(input_path: Path, output_dir: Path) -> None:
    rows = [
        row
        for row in read_csv(input_path)
        if row["primary_analysis_eligible"] == "yes"
    ]
    by_subject: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_subject[row["subject_id"]][cell_name(row)] = row

    tests: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    functions = contrast_functions()
    for feature, feature_tier in FEATURE_TIERS.items():
        for contrast_id, (contrast_tier, function) in functions.items():
            required_scores: list[float] = []
            for subject_id in sorted(by_subject):
                subject_rows = by_subject[subject_id]
                values = {
                    cell: float(
                        row[f"{feature}_post_minus_pre"]
                    )
                    for cell, row in subject_rows.items()
                }
                try:
                    score = function(values)
                except KeyError:
                    continue
                required_scores.append(score)
                scores.append(
                    {
                        "subject_id": subject_id,
                        "contrast_id": contrast_id,
                        "feature": feature,
                        "feature_tier": feature_tier,
                        "difference": score,
                    }
                )
            if len(required_scores) < 15:
                raise ValueError(
                    f"{contrast_id}/{feature} has only "
                    f"{len(required_scores)} complete participants"
                )
            tests.append(
                test_row(
                    contrast_id=contrast_id,
                    contrast_tier=contrast_tier,
                    feature=feature,
                    feature_tier=feature_tier,
                    values=required_scores,
                )
            )

    for feature in FEATURE_TIERS:
        family = [
            row
            for row in tests
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

    write_csv(output_dir / "eeg_ad_response_contrasts.csv", tests)
    write_csv(output_dir / "eeg_ad_response_contrast_scores.csv", scores)
    print(f"Wrote {len(tests)} ad response tests")
    print(f"Wrote {len(scores)} participant ad response scores")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    run(args.input, args.output_dir)


if __name__ == "__main__":
    main()
