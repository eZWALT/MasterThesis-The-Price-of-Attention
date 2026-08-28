"""Exhaustive post-hoc pairwise EEG contrasts.

EXPLORATORY ONLY. This script does not touch the confirmatory pipeline,
does not rebuild Gold, and does not refit ICA. It reads the same frozen
Gold tables as the planned analyses and writes to a separate directory.

Dataset A: 5 conditions, 10 unique pairs on person-level condition
medians.

Dataset B: 4 advertisement conditions, 6 unique pairs, computed twice.
In Delta space each cell is first differenced against its matched no-ad
reply; in raw space the post-minus-pre values are differenced directly.
Same-timing pairs are algebraically identical across the two spaces
because the shared control cancels; cross-timing pairs differ by the
control drift (N_early - N_late).

Bound and rationale:
    .agents/context/data-analysis/eeg/2026-08-28-posthoc-pairwise.md
Matched-control audit:
    .agents/context/data-analysis/eeg/2026-08-28-dataset-b-control-audit.md
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_ad_contrasts import cell_name  # noqa: E402
from build_condition_contrasts import (  # noqa: E402
    FEATURE_TIERS,
    confidence_interval,
    holm_adjust,
    mean,
    read_csv,
    write_csv,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONDITION_INPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/condition_features.csv"
)
DEFAULT_AD_INPUT = REPOSITORY_ROOT / (
    "src/project/logs/xdf/gold/features/ad_response_features.csv"
)
FROZEN_DIR = REPOSITORY_ROOT / "analysis/eeg/statistics/outputs"
DEFAULT_OUTPUT_DIR = FROZEN_DIR / "posthoc"

# Advertisement cells first so that an ad-versus-no-ad pair reads
# "ad minus no-ad", the same direction as the planned contrast.
DATASET_A_ORDER = (
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
    "no_ads",
)
DATASET_B_ORDER = ("inline_early", "inline_late", "block_early", "block_late")
MATCHED_CONTROL = {
    "inline_early": "no_ads_early",
    "block_early": "no_ads_early",
    "inline_late": "no_ads_late",
    "block_late": "no_ads_late",
}
TIMING_OF = {
    "inline_early": "early",
    "block_early": "early",
    "inline_late": "late",
    "block_late": "late",
}

# Weights on DATASET_A_ORDER. These reproduce contrast_functions() in
# build_condition_contrasts.py exactly; gate 2 checks that numerically.
PLANNED_A = {
    "any_ad_vs_no_ads": (0.25, 0.25, 0.25, 0.25, -1.0),
    "inline_vs_block": (0.5, 0.5, -0.5, -0.5, 0.0),
    "early_vs_late": (0.5, -0.5, 0.5, -0.5, 0.0),
    "format_x_timing": (1.0, -1.0, -1.0, 1.0, 0.0),
}
# Weights on DATASET_B_ORDER. The first two are identical in raw and
# Delta space. The timing row is space-dependent: the code's
# early_vs_late is the raw one, and the Delta one is tested nowhere.
BASIS_B = {
    "inline_vs_block": (0.5, 0.5, -0.5, -0.5),
    "early_vs_late": (0.5, -0.5, 0.5, -0.5),
    "format_x_timing": (1.0, -1.0, -1.0, 1.0),
}
TOLERANCE = 1e-9


class VerificationError(RuntimeError):
    """A gate failed, so no table is written."""


def bh_adjust(p_values: list[float]) -> list[float]:
    """Benjamini-Hochberg step-up, monotonicity enforced.

    Controls the false discovery rate rather than the family-wise error
    rate, so it is less conservative than Holm. Reported alongside Holm;
    it does not replace it, and it is not applied to the confirmatory
    pipeline, whose correction was pre-specified as Holm.
    """
    count = len(p_values)
    order = np.argsort(np.asarray(p_values, dtype=float))
    adjusted = np.empty(count, dtype=float)
    running_min = 1.0
    for rank in range(count - 1, -1, -1):
        index = int(order[rank])
        candidate = count / (rank + 1) * p_values[index]
        running_min = min(running_min, candidate)
        adjusted[index] = min(running_min, 1.0)
    return adjusted.tolist()


def harmonic(count: int) -> float:
    return float(sum(1.0 / i for i in range(1, count + 1)))


def by_adjust(p_values: list[float]) -> list[float]:
    """Benjamini-Yekutieli: FDR valid under arbitrary dependence.

    BH only controls FDR under independence or positive regression
    dependency. The 16 spectral measures violate that: the five relative
    powers sum to one by construction, so they are negatively dependent,
    and the engagement ratios reuse the same bands. BY restores the
    guarantee by inflating BH by the harmonic number of the family size
    (x2.45 at m=6, x2.93 at m=10), which on this data makes it stricter
    than Holm.
    """
    factor = harmonic(len(p_values))
    return [min(1.0, value * factor) for value in bh_adjust(p_values)]


def pair_label(first: str, second: str) -> str:
    return f"{first}__minus__{second}"


def test_row(
    *,
    scores: list[float],
    subjects: list[str],
) -> dict[str, Any]:
    array = np.asarray(scores, dtype=float)
    lower, upper = confidence_interval(scores)
    t_result = stats.ttest_1samp(array, popmean=0.0)
    try:
        wilcoxon = stats.wilcoxon(array, alternative="two-sided")
        wilcoxon_statistic = float(wilcoxon.statistic)
        wilcoxon_p = float(wilcoxon.pvalue)
    except ValueError:
        wilcoxon_statistic, wilcoxon_p = 0.0, 1.0
    sd = float(np.std(array, ddof=1))
    return {
        "n_participants": len(subjects),
        "mean_difference": mean(scores),
        "sd_difference": sd,
        "se_difference": float(stats.sem(array)),
        "ci_lower": lower,
        "ci_upper": upper,
        "cohen_dz": mean(scores) / sd if sd > 0 else math.nan,
        "t_statistic": float(t_result.statistic),
        "degrees_of_freedom": len(subjects) - 1,
        "p_t_raw": float(t_result.pvalue),
        "p_t_holm": "",
        "p_t_bh": "",
        "p_t_by": "",
        "wilcoxon_statistic": wilcoxon_statistic,
        "p_wilcoxon_raw": wilcoxon_p,
        "p_wilcoxon_holm": "",
        "p_wilcoxon_bh": "",
        "p_wilcoxon_by": "",
    }


def apply_corrections(
    rows: list[dict[str, Any]],
    family_keys: tuple[str, ...],
) -> None:
    """Adjust in place with Holm, BH and BY, within each family."""
    families: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        families[tuple(row[key] for key in family_keys)].append(row)
    for family in families.values():
        raw_t = [float(row["p_t_raw"]) for row in family]
        raw_w = [float(row["p_wilcoxon_raw"]) for row in family]
        for method, adjust in (
            ("holm", holm_adjust),
            ("bh", bh_adjust),
            ("by", by_adjust),
        ):
            for row, value_t, value_w in zip(
                family, adjust(raw_t), adjust(raw_w)
            ):
                row[f"p_t_{method}"] = value_t
                row[f"p_wilcoxon_{method}"] = value_w


def load_dataset_a(path: Path, *, feature_suffix: str) -> tuple[
    list[str],
    dict[str, dict[str, dict[str, float]]],
]:
    rows = [
        row
        for row in read_csv(path)
        if row["window_type"] == "condition"
        and row["primary_analysis_eligible"] == "yes"
    ]
    if len(rows) != 90:
        raise VerificationError(
            f"Gate 1: expected 90 eligible condition rows, found {len(rows)}"
        )
    by_subject: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for row in rows:
        by_subject[row["subject_id"]][row["condition"]] = {
            feature: float(row[f"{feature}{feature_suffix}"])
            for feature in FEATURE_TIERS
        }
    subjects = sorted(by_subject)
    for subject in subjects:
        if set(by_subject[subject]) != set(DATASET_A_ORDER):
            raise VerificationError(
                f"Gate 1: {subject} lacks complete condition cells"
            )
    if len(subjects) != 18:
        raise VerificationError(
            f"Gate 1: expected 18 complete subjects, found {len(subjects)}"
        )
    return subjects, by_subject


def load_dataset_b(path: Path) -> tuple[
    list[str],
    dict[str, dict[str, dict[str, float]]],
]:
    rows = [
        row
        for row in read_csv(path)
        if row["primary_analysis_eligible"] == "yes"
    ]
    by_subject: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    for row in rows:
        by_subject[row["subject_id"]][cell_name(row)] = {
            feature: float(row[f"{feature}_post_minus_pre"])
            for feature in FEATURE_TIERS
        }
    required = set(DATASET_B_ORDER) | {"no_ads_early", "no_ads_late"}
    subjects = sorted(
        subject
        for subject, cells in by_subject.items()
        if required.issubset(cells)
    )
    if not subjects:
        raise VerificationError("Gate 1: no subject has all six Dataset B cells")
    return subjects, by_subject


def dataset_a_tables(
    subjects: list[str],
    values: dict[str, dict[str, dict[str, float]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tests: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    for feature, feature_tier in FEATURE_TIERS.items():
        for first, second in combinations(DATASET_A_ORDER, 2):
            differences = [
                values[subject][first][feature]
                - values[subject][second][feature]
                for subject in subjects
            ]
            for subject, difference in zip(subjects, differences):
                scores.append(
                    {
                        "subject_id": subject,
                        "dataset": "dataset_a",
                        "contrast_space": "condition_median",
                        "pair_id": pair_label(first, second),
                        "condition_1": first,
                        "condition_2": second,
                        "feature": feature,
                        "feature_tier": feature_tier,
                        "difference": difference,
                    }
                )
            row = {
                "dataset": "dataset_a",
                "contrast_space": "condition_median",
                "pair_id": pair_label(first, second),
                "condition_1": first,
                "condition_2": second,
                "comparison_type": (
                    "ad_vs_no_ad" if second == "no_ads" else "ad_vs_ad"
                ),
                "feature": feature,
                "feature_tier": feature_tier,
                "contrast_tier": "posthoc_exploratory",
            }
            row.update(test_row(scores=differences, subjects=subjects))
            row["correction_family"] = (
                f"posthoc_pairwise_dataset_a__{feature}"
            )
            row["dataset_status"] = "analysis_ready_condition_v1"
            tests.append(row)
    apply_corrections(tests, ("feature",))
    return tests, scores


def dataset_b_tables(
    subjects: list[str],
    values: dict[str, dict[str, dict[str, float]]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tests: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    for feature, feature_tier in FEATURE_TIERS.items():
        for space in ("delta_matched_control", "raw_post_minus_pre"):
            for first, second in combinations(DATASET_B_ORDER, 2):
                differences = []
                for subject in subjects:
                    cells = values[subject]
                    left = cells[first][feature]
                    right = cells[second][feature]
                    if space == "delta_matched_control":
                        left -= cells[MATCHED_CONTROL[first]][feature]
                        right -= cells[MATCHED_CONTROL[second]][feature]
                    differences.append(left - right)
                same_timing = TIMING_OF[first] == TIMING_OF[second]
                for subject, difference in zip(subjects, differences):
                    scores.append(
                        {
                            "subject_id": subject,
                            "dataset": "dataset_b",
                            "contrast_space": space,
                            "pair_id": pair_label(first, second),
                            "condition_1": first,
                            "condition_2": second,
                            "feature": feature,
                            "feature_tier": feature_tier,
                            "difference": difference,
                        }
                    )
                row = {
                    "dataset": "dataset_b",
                    "contrast_space": space,
                    "pair_id": pair_label(first, second),
                    "condition_1": first,
                    "condition_2": second,
                    "comparison_type": (
                        "same_timing_control_cancels"
                        if same_timing
                        else "cross_timing_control_drift"
                    ),
                    "feature": feature,
                    "feature_tier": feature_tier,
                    "contrast_tier": "posthoc_exploratory",
                }
                row.update(test_row(scores=differences, subjects=subjects))
                row["correction_family"] = (
                    f"posthoc_pairwise_dataset_b__{space}__{feature}"
                )
                row["dataset_status"] = "analysis_ready_ad_v1"
                tests.append(row)
    apply_corrections(tests, ("feature", "contrast_space"))
    return tests, scores


def timing_discrepancy_table(
    subjects: list[str],
    values: dict[str, dict[str, dict[str, float]]],
) -> list[dict[str, Any]]:
    """Delta-space timing contrast beside the raw early_vs_late in code."""
    rows: list[dict[str, Any]] = []
    for feature, feature_tier in FEATURE_TIERS.items():
        raw_scores: list[float] = []
        delta_scores: list[float] = []
        drift_scores: list[float] = []
        for subject in subjects:
            cells = values[subject]
            early = mean(
                [
                    cells["inline_early"][feature],
                    cells["block_early"][feature],
                ]
            )
            late = mean(
                [cells["inline_late"][feature], cells["block_late"][feature]]
            )
            drift = (
                cells["no_ads_early"][feature]
                - cells["no_ads_late"][feature]
            )
            raw_scores.append(early - late)
            delta_scores.append(early - late - drift)
            drift_scores.append(drift)
        residual = float(
            np.max(
                np.abs(
                    np.asarray(raw_scores)
                    - np.asarray(delta_scores)
                    - np.asarray(drift_scores)
                )
            )
        )
        if residual > TOLERANCE:
            raise VerificationError(
                f"Gate 5: timing identity broken for {feature} "
                f"(residual {residual:.3e})"
            )
        for label, series in (
            ("raw_early_vs_late_in_code", raw_scores),
            ("delta_early_vs_late_not_in_code", delta_scores),
            ("control_drift_no_ad_early_minus_late", drift_scores),
        ):
            row = {
                "quantity": label,
                "feature": feature,
                "feature_tier": feature_tier,
                "identity": (
                    "raw = delta + control_drift (checked, residual < 1e-9)"
                ),
                "contrast_tier": "posthoc_exploratory",
            }
            row.update(test_row(scores=series, subjects=subjects))
            row["correction_family"] = "uncorrected_estimand_comparison"
            rows.append(row)
    return rows


def redundancy_map() -> list[dict[str, Any]]:
    """Express every pairwise contrast in the planned-contrast basis."""
    rows: list[dict[str, Any]] = []

    def solve(
        target: np.ndarray,
        basis: dict[str, tuple[float, ...]],
    ) -> dict[str, float]:
        matrix = np.array([basis[name] for name in basis], dtype=float).T
        coefficients, *_ = np.linalg.lstsq(matrix, target, rcond=None)
        residual = float(np.max(np.abs(matrix @ coefficients - target)))
        if residual > TOLERANCE:
            raise VerificationError(
                f"Gate 5: pairwise contrast {target} does not reconstruct "
                f"in the planned basis (residual {residual:.3e})"
            )
        return dict(zip(basis, (float(value) for value in coefficients)))

    for first, second in combinations(DATASET_A_ORDER, 2):
        target = np.zeros(len(DATASET_A_ORDER))
        target[DATASET_A_ORDER.index(first)] = 1.0
        target[DATASET_A_ORDER.index(second)] = -1.0
        coefficients = solve(target, PLANNED_A)
        rows.append(
            {
                "dataset": "dataset_a",
                "contrast_space": "condition_median",
                "pair_id": pair_label(first, second),
                "basis": "planned_dataset_a_contrasts",
                "all_basis_terms_exist_in_code": "yes",
                **{
                    f"coefficient__{name}": round(value, 12)
                    for name, value in coefficients.items()
                },
                "reconstructs_exactly": "yes",
            }
        )

    for first, second in combinations(DATASET_B_ORDER, 2):
        target = np.zeros(len(DATASET_B_ORDER))
        target[DATASET_B_ORDER.index(first)] = 1.0
        target[DATASET_B_ORDER.index(second)] = -1.0
        coefficients = solve(target, BASIS_B)
        cross_timing = TIMING_OF[first] != TIMING_OF[second]
        rows.append(
            {
                "dataset": "dataset_b",
                "contrast_space": "delta_and_raw",
                "pair_id": pair_label(first, second),
                "basis": "inline_vs_block, early_vs_late, format_x_timing",
                # In Delta space the timing basis vector is NOT the
                # early_vs_late in build_ad_contrasts.py; it is the
                # control-adjusted one, which the code does not test.
                "all_basis_terms_exist_in_code": (
                    "raw_yes__delta_no_timing_term"
                    if cross_timing
                    and abs(coefficients["early_vs_late"]) > TOLERANCE
                    else "yes"
                ),
                # any_ad_vs_no_ads is not in the Dataset B basis: the
                # control is already inside every Delta.
                "coefficient__any_ad_vs_no_ads": "not_in_basis",
                **{
                    f"coefficient__{name}": round(value, 12)
                    for name, value in coefficients.items()
                },
                "reconstructs_exactly": "yes",
            }
        )
    return rows


def verify_planned_a(
    subjects: list[str],
    values: dict[str, dict[str, dict[str, float]]],
) -> None:
    frozen = {
        (row["contrast_id"], row["feature"]): float(row["mean_difference"])
        for row in read_csv(FROZEN_DIR / "eeg_condition_contrasts.csv")
    }
    for feature in FEATURE_TIERS:
        for contrast_id, weights in PLANNED_A.items():
            recomputed = mean(
                [
                    sum(
                        weight * values[subject][condition][feature]
                        for weight, condition in zip(weights, DATASET_A_ORDER)
                    )
                    for subject in subjects
                ]
            )
            expected = frozen[(contrast_id, feature)]
            if abs(recomputed - expected) > TOLERANCE:
                raise VerificationError(
                    f"Gate 2: {contrast_id}/{feature} recomputed "
                    f"{recomputed:.12f} but frozen table says "
                    f"{expected:.12f}"
                )


def verify_planned_b(
    subjects: list[str],
    values: dict[str, dict[str, dict[str, float]]],
) -> None:
    frozen = {
        (row["contrast_id"], row["feature"]): float(row["mean_difference"])
        for row in read_csv(FROZEN_DIR / "eeg_ad_response_contrasts.csv")
    }
    planned = {
        "inline_early_vs_no_ad_early": "inline_early",
        "block_early_vs_no_ad_early": "block_early",
        "inline_late_vs_no_ad_late": "inline_late",
        "block_late_vs_no_ad_late": "block_late",
    }
    for feature in FEATURE_TIERS:
        for contrast_id, condition in planned.items():
            recomputed = mean(
                [
                    values[subject][condition][feature]
                    - values[subject][MATCHED_CONTROL[condition]][feature]
                    for subject in subjects
                ]
            )
            expected = frozen[(contrast_id, feature)]
            if abs(recomputed - expected) > TOLERANCE:
                raise VerificationError(
                    f"Gate 3: {contrast_id}/{feature} recomputed "
                    f"{recomputed:.12f} but frozen table says "
                    f"{expected:.12f}"
                )


def verify_same_timing_identity(tests: list[dict[str, Any]]) -> int:
    """Same-timing Dataset B pairs must match across the two spaces."""
    indexed = {
        (row["contrast_space"], row["pair_id"], row["feature"]): row
        for row in tests
    }
    checked = 0
    for (space, pair_id, feature), row in indexed.items():
        if space != "delta_matched_control":
            continue
        if row["comparison_type"] != "same_timing_control_cancels":
            continue
        other = indexed[("raw_post_minus_pre", pair_id, feature)]
        gap = abs(row["mean_difference"] - other["mean_difference"])
        if gap > TOLERANCE:
            raise VerificationError(
                f"Gate 4: {pair_id}/{feature} should cancel its control "
                f"but the two spaces differ by {gap:.3e}"
            )
        checked += 1
    return checked


def run(
    condition_input: Path,
    ad_input: Path,
    output_dir: Path,
    *,
    feature_suffix: str = "_median",
) -> None:
    subjects_a, values_a = load_dataset_a(
        condition_input, feature_suffix=feature_suffix
    )
    subjects_b, values_b = load_dataset_b(ad_input)
    print(f"Gate 1 passed: Dataset A n={len(subjects_a)}, "
          f"Dataset B n={len(subjects_b)}")

    verify_planned_a(subjects_a, values_a)
    print("Gate 2 passed: planned Dataset A contrasts reproduce to 1e-9")
    verify_planned_b(subjects_b, values_b)
    print("Gate 3 passed: planned Dataset B contrasts reproduce to 1e-9")

    tests_a, scores_a = dataset_a_tables(subjects_a, values_a)
    tests_b, scores_b = dataset_b_tables(subjects_b, values_b)

    checked = verify_same_timing_identity(tests_b)
    print(f"Gate 4 passed: {checked} same-timing Dataset B cells identical "
          "across spaces")

    timing_rows = timing_discrepancy_table(subjects_b, values_b)
    redundancy_rows = redundancy_map()
    print("Gate 5 passed: timing identity and basis reconstruction exact")

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "eeg_posthoc_pairwise_dataset_a.csv", tests_a)
    write_csv(output_dir / "eeg_posthoc_pairwise_dataset_b.csv", tests_b)
    write_csv(
        output_dir / "eeg_posthoc_pairwise_scores_dataset_a.csv", scores_a
    )
    write_csv(
        output_dir / "eeg_posthoc_pairwise_scores_dataset_b.csv", scores_b
    )
    write_csv(output_dir / "eeg_posthoc_timing_discrepancy.csv", timing_rows)
    write_csv(output_dir / "eeg_posthoc_redundancy_map.csv", redundancy_rows)

    print(f"Wrote {len(tests_a)} Dataset A pairwise tests")
    print(f"Wrote {len(tests_b)} Dataset B pairwise tests (both spaces)")
    print(f"Wrote {len(timing_rows)} timing-discrepancy rows")
    print(f"Wrote {len(redundancy_rows)} redundancy-map rows")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--condition-input", type=Path, default=DEFAULT_CONDITION_INPUT
    )
    parser.add_argument("--ad-input", type=Path, default=DEFAULT_AD_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--feature-suffix",
        default="_median",
        help="Dataset A window-summary suffix. Primary is _median.",
    )
    args = parser.parse_args()
    run(
        args.condition_input,
        args.ad_input,
        args.output_dir,
        feature_suffix=args.feature_suffix,
    )


if __name__ == "__main__":
    main()
