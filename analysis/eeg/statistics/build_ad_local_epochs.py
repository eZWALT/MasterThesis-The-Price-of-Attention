"""Ad-local epoch averaging. Exploratory only.

Dataset A currently medians every retained 4 s tile in a condition
(median 95 tiles, about six minutes). If an advertisement only perturbs
a few tens of seconds, that median is mostly non-ad conversation.

This script does not rebuild Gold, does not touch ICA, and does not
change the confirmatory 4 s / median pipeline. It reads the frozen
condition-epoch table and the frozen visual-onset contracts, keeps the
k nearest retained tiles to each onset, re-medians those tiles, and
re-runs the same person-level contrasts.

Three Dataset A selections, each with a matched-time no-ad control
(tiles around the turn-2 and turn-4 replies of the no-ad conversation):

- around: k tiles nearest the onset (pre and post mixed)
- pre:    k tiles immediately before the onset
- post:   k tiles immediately after the onset

Dataset B companion: at each k, Delta = median(k post) - median(k pre),
then the same eight advertisement contrasts. k=1 is not identical to
confirmatory Dataset B: those windows are locked to visual onset, these
tiles are locked to condition start.

k grid: 1, 3, 5, 10, 20. k=all reproduces Dataset A as a gate.

    python analysis/eeg/statistics/build_ad_local_epochs.py
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_ad_contrasts import cell_name  # noqa: E402
from build_ad_contrasts import run as run_ad_contrasts
from build_condition_contrasts import (  # noqa: E402
    CONDITIONS,
    FEATURE_TIERS,
    contrast_tables,
    holm_adjust,
    read_csv,
    write_csv,
)
from build_posthoc_pairwise import bh_adjust, by_adjust  # noqa: E402


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
GOLD_FEATURES = REPOSITORY_ROOT / "src/project/logs/xdf/gold/features"
GOLD_WINDOWS = REPOSITORY_ROOT / "src/project/logs/xdf/gold/windows"
DEFAULT_EPOCHS = GOLD_FEATURES / "condition_epoch_features.csv"
DEFAULT_CONDITION_FEATURES = GOLD_FEATURES / "condition_features.csv"
DEFAULT_AD_RESPONSES = GOLD_FEATURES / "ad_response_features.csv"
DEFAULT_AD_WINDOWS = GOLD_WINDOWS / "ad_analysis_windows.csv"
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs"
)
CONFIRMATORY_A = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/eeg_condition_contrasts.csv"
)
CONFIRMATORY_B = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv"
)

K_GRID = (1, 3, 5, 10, 20)
SELECTIONS = ("around", "pre", "post")
FEATURES = tuple(FEATURE_TIERS)
AD_CONDITIONS = (
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
)


def epoch_mid(row: dict[str, str]) -> float:
    return 0.5 * (
        float(row["epoch_start_eeg_offset_s"])
        + float(row["epoch_end_eeg_offset_s"])
    )


def unique_onsets(windows: list[dict[str, str]]) -> list[dict[str, str]]:
    by_id: dict[str, dict[str, str]] = {}
    for row in windows:
        if row["primary_analysis_eligible"] != "yes":
            continue
        by_id.setdefault(row["reference_id"], row)
    return list(by_id.values())


def index_epochs(
    epochs: list[dict[str, str]],
) -> dict[tuple[str, str], list[dict[str, str]]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in epochs:
        if row["window_type"] != "condition":
            continue
        if row["retained_by_policy"] != "yes":
            continue
        grouped[(row["subject_id"], row["condition"])].append(row)
    return grouped


def select_tiles(
    tiles: list[dict[str, str]],
    onset_s: float,
    *,
    k: int,
    side: str,
) -> list[dict[str, str]]:
    scored: list[tuple[float, float, dict[str, str]]] = []
    for row in tiles:
        mid = epoch_mid(row)
        if side == "pre" and not mid < onset_s:
            continue
        if side == "post" and not mid >= onset_s:
            continue
        scored.append((abs(mid - onset_s), mid, row))
    scored.sort(key=lambda item: item[0])
    chosen = scored[:k]
    return [row for _, _, row in chosen]


def unique_tiles(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    by_key: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in rows:
        key = (row["subject_id"], row["window_id"], row["epoch_index"])
        by_key[key] = row
    return list(by_key.values())


def median_features(rows: list[dict[str, str]]) -> dict[str, float]:
    if not rows:
        raise ValueError("Cannot median an empty epoch list")
    summary: dict[str, float] = {}
    for feature in FEATURES:
        values = np.asarray([float(row[feature]) for row in rows], dtype=float)
        summary[f"{feature}_median"] = float(np.median(values))
        summary[f"{feature}_mean"] = float(np.mean(values))
    return summary


def distance_stats(
    rows: list[dict[str, str]], onset_times: list[float]
) -> dict[str, float]:
    if not rows or not onset_times:
        return {
            "mean_abs_distance_s": math.nan,
            "max_abs_distance_s": math.nan,
            "span_s": math.nan,
        }
    distances: list[float] = []
    mids = [epoch_mid(row) for row in rows]
    for mid in mids:
        distances.append(min(abs(mid - onset) for onset in onset_times))
    return {
        "mean_abs_distance_s": float(np.mean(distances)),
        "max_abs_distance_s": float(np.max(distances)),
        "span_s": float(max(mids) - min(mids)),
    }


def template_cell(rows: list[dict[str, str]]) -> dict[str, Any]:
    first = rows[0]
    return {
        "subject_id": first["subject_id"],
        "experiment_id": first["experiment_id"],
        "window_id": first["window_id"],
        "window_type": "condition",
        "condition": first["condition"],
        "ad_mode": first["ad_mode"],
        "trial_index": first["trial_index"],
        "primary_analysis_eligible": "yes",
        "ica_applied": first["ica_applied"],
        "source_xdf": first["source_xdf"],
    }


def local_condition_cell(
    *,
    tiles: list[dict[str, str]],
    onsets: list[dict[str, str]],
    k: int | None,
    side: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    selected: list[dict[str, str]] = []
    onset_times = [
        float(onset["reference_onset_eeg_offset_s"]) for onset in onsets
    ]
    if k is None:
        selected = list(tiles)
    else:
        for onset in onsets:
            selected.extend(
                select_tiles(
                    tiles,
                    float(onset["reference_onset_eeg_offset_s"]),
                    k=k,
                    side=side,
                )
            )
        selected = unique_tiles(selected)
    if not selected:
        raise ValueError(
            f"{tiles[0]['subject_id']} {tiles[0]['condition']} "
            f"has no {side} tiles at k={k}"
        )
    cell = template_cell(tiles)
    if onsets:
        cell["condition"] = (
            "no_ads"
            if onsets[0]["condition"] == "no_ads"
            else onsets[0]["condition"]
        )
    cell.update(median_features(selected))
    cell["complete_epoch_count"] = len(selected)
    cell["retained_epoch_count"] = len(selected)
    coverage = {
        "subject_id": cell["subject_id"],
        "condition": cell["condition"],
        "selection": "all" if k is None else side,
        "k_epochs": "" if k is None else k,
        "k_label": "all" if k is None else str(k),
        "n_onsets": len(onsets),
        "n_epochs_available": len(tiles),
        "n_epochs_selected": len(selected),
        "requested_per_onset": "" if k is None else k,
        **distance_stats(selected, onset_times if k is not None else []),
    }
    return cell, coverage


def dataset_a_rows(
    *,
    epochs_by_cell: dict[tuple[str, str], list[dict[str, str]]],
    onsets_by_subject: dict[str, list[dict[str, str]]],
    k: int | None,
    side: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for subject_id, onsets in sorted(onsets_by_subject.items()):
        by_condition: dict[str, list[dict[str, str]]] = defaultdict(list)
        for onset in onsets:
            by_condition[onset["condition"]].append(onset)
        if k is None:
            for condition in CONDITIONS:
                tiles = epochs_by_cell[(subject_id, condition)]
                cell, cov = local_condition_cell(
                    tiles=tiles,
                    onsets=[],
                    k=None,
                    side="around",
                )
                cell["condition"] = condition
                cov["condition"] = condition
                rows.append(cell)
                coverage.append(cov)
            continue
        for condition in AD_CONDITIONS:
            tiles = epochs_by_cell[(subject_id, condition)]
            cell, cov = local_condition_cell(
                tiles=tiles,
                onsets=by_condition[condition],
                k=k,
                side=side,
            )
            rows.append(cell)
            coverage.append(cov)
        no_ad_onsets = by_condition["no_ads"]
        tiles = epochs_by_cell[(subject_id, "no_ads")]
        cell, cov = local_condition_cell(
            tiles=tiles,
            onsets=no_ad_onsets,
            k=k,
            side=side,
        )
        cell["condition"] = "no_ads"
        rows.append(cell)
        coverage.append(cov)
    return rows, coverage


def dataset_b_rows(
    *,
    epochs_by_cell: dict[tuple[str, str], list[dict[str, str]]],
    onsets: list[dict[str, str]],
    k: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    for onset in onsets:
        tiles = epochs_by_cell[(onset["subject_id"], onset["condition"])]
        t0 = float(onset["reference_onset_eeg_offset_s"])
        pre = select_tiles(tiles, t0, k=k, side="pre")
        post = select_tiles(tiles, t0, k=k, side="post")
        if not pre or not post:
            raise ValueError(
                f"{onset['reference_id']} lacks pre/post tiles at k={k}"
            )
        pre_med = median_features(pre)
        post_med = median_features(post)
        row: dict[str, Any] = {
            "subject_id": onset["subject_id"],
            "experiment_id": onset["experiment_id"],
            "reference_id": onset["reference_id"],
            "reference_kind": onset["reference_kind"],
            "condition": onset["condition"],
            "ad_mode": onset["ad_mode"],
            "matched_timing": onset["matched_timing"],
            "matched_ad_conditions": onset["matched_ad_conditions"],
            "primary_analysis_eligible": "yes",
            "k_epochs": k,
            "n_pre": len(pre),
            "n_post": len(post),
        }
        for feature in FEATURES:
            pre_value = pre_med[f"{feature}_median"]
            post_value = post_med[f"{feature}_median"]
            row[f"{feature}_pre"] = pre_value
            row[f"{feature}_post"] = post_value
            row[f"{feature}_post_minus_pre"] = post_value - pre_value
        rows.append(row)
        coverage.append(
            {
                "subject_id": onset["subject_id"],
                "reference_id": onset["reference_id"],
                "condition": cell_name(onset),
                "selection": "prepost",
                "k_epochs": k,
                "k_label": str(k),
                "n_pre": len(pre),
                "n_post": len(post),
                "mean_abs_distance_s_pre": distance_stats(pre, [t0])[
                    "mean_abs_distance_s"
                ],
                "mean_abs_distance_s_post": distance_stats(post, [t0])[
                    "mean_abs_distance_s"
                ],
            }
        )
    return rows, coverage


def attach_fdr(rows: list[dict[str, Any]]) -> None:
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["contrast_tier"] != "primary":
            row["p_t_bh"] = ""
            row["p_t_by"] = ""
            row["holm_significant"] = "no"
            row["bh_significant"] = "no"
            continue
        by_family[row["feature"]].append(row)
    for family in by_family.values():
        raw = [float(row["p_t_raw"]) for row in family]
        bh = bh_adjust(raw)
        by = by_adjust(raw)
        for row, q_bh, q_by in zip(family, bh, by):
            row["p_t_bh"] = q_bh
            row["p_t_by"] = q_by
            holm = row.get("p_t_holm")
            row["holm_significant"] = (
                "yes"
                if holm not in ("", None) and float(holm) < 0.05
                else "no"
            )
            row["bh_significant"] = "yes" if q_bh < 0.05 else "no"


COMPARISON_FIELDS = (
    "dataset",
    "selection",
    "k_epochs",
    "k_label",
    "contrast_id",
    "contrast_tier",
    "feature",
    "feature_tier",
    "n_participants",
    "mean_difference",
    "sd_difference",
    "se_difference",
    "ci_lower",
    "ci_upper",
    "cohen_dz",
    "t_statistic",
    "degrees_of_freedom",
    "p_t_raw",
    "p_t_holm",
    "p_t_bh",
    "p_t_by",
    "wilcoxon_statistic",
    "p_wilcoxon_raw",
    "p_wilcoxon_holm",
    "holm_significant",
    "bh_significant",
    "correction_family",
)


def flatten_contrasts(
    rows: list[dict[str, Any]],
    *,
    dataset: str,
    selection: str,
    k: int | None,
) -> list[dict[str, Any]]:
    attach_fdr(rows)
    flat: list[dict[str, Any]] = []
    for row in rows:
        item = {field: row.get(field, "") for field in COMPARISON_FIELDS}
        item["dataset"] = dataset
        item["selection"] = selection
        item["k_epochs"] = "" if k is None else k
        item["k_label"] = "all" if k is None else str(k)
        flat.append(item)
    return flat


def verify_dataset_a_all(
    local_rows: list[dict[str, Any]],
    gold_rows: list[dict[str, str]],
) -> dict[str, Any]:
    gold = {
        (row["subject_id"], row["condition"]): row
        for row in gold_rows
        if row["window_type"] == "condition"
        and row["primary_analysis_eligible"] == "yes"
    }
    diffs: list[float] = []
    for row in local_rows:
        key = (row["subject_id"], row["condition"])
        gold_row = gold[key]
        for feature in FEATURES:
            diffs.append(
                abs(
                    float(row[f"{feature}_median"])
                    - float(gold_row[f"{feature}_median"])
                )
            )
    return {
        "n_cells": len(local_rows),
        "n_feature_comparisons": len(diffs),
        "max_abs_median_diff": max(diffs) if diffs else math.nan,
        "mean_abs_median_diff": float(np.mean(diffs)) if diffs else math.nan,
        "gate_passed": bool(diffs) and max(diffs) < 1e-9,
    }


def confirm_contrast_match(
    local_rows: list[dict[str, Any]],
    confirmatory_path: Path,
    *,
    p_column: str = "p_t_raw",
) -> dict[str, Any]:
    gold = read_csv(confirmatory_path)
    lookup = {
        (row["feature"], row["contrast_id"]): row
        for row in gold
    }
    diffs: list[float] = []
    mismatches: list[dict[str, Any]] = []
    for row in local_rows:
        key = (row["feature"], row["contrast_id"])
        if key not in lookup:
            continue
        if row.get("metric") and lookup[key].get("metric"):
            if row["metric"] != lookup[key]["metric"]:
                continue
        delta = abs(float(row[p_column]) - float(lookup[key][p_column]))
        diffs.append(delta)
        if delta > 1e-9:
            mismatches.append(
                {
                    "feature": row["feature"],
                    "contrast_id": row["contrast_id"],
                    "local": float(row[p_column]),
                    "confirmatory": float(lookup[key][p_column]),
                }
            )
    return {
        "n_compared": len(diffs),
        "max_abs_p_diff": max(diffs) if diffs else math.nan,
        "n_mismatches": len(mismatches),
        "gate_passed": bool(diffs) and max(diffs) < 1e-9,
        "mismatches": mismatches[:8],
    }


def dataset_b_k1_correlation(
    local_rows: list[dict[str, Any]],
    gold_rows: list[dict[str, str]],
) -> dict[str, Any]:
    gold = {row["reference_id"]: row for row in gold_rows}
    by_feature: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: {"local": [], "gold": []}
    )
    for row in local_rows:
        gold_row = gold.get(row["reference_id"])
        if gold_row is None:
            continue
        for feature in FEATURES:
            local_value = float(row[f"{feature}_post_minus_pre"])
            gold_value = float(gold_row[f"{feature}_post_minus_pre"])
            by_feature[feature]["local"].append(local_value)
            by_feature[feature]["gold"].append(gold_value)
    summary: dict[str, Any] = {}
    correlations: list[float] = []
    for feature, values in by_feature.items():
        local = np.asarray(values["local"], dtype=float)
        gold_arr = np.asarray(values["gold"], dtype=float)
        if local.std() == 0 or gold_arr.std() == 0:
            corr = math.nan
        else:
            corr = float(np.corrcoef(local, gold_arr)[0, 1])
        correlations.append(corr)
        summary[feature] = {
            "n": len(local),
            "pearson_r": corr,
            "mean_abs_diff": float(np.mean(np.abs(local - gold_arr))),
        }
    finite = [value for value in correlations if not math.isnan(value)]
    summary["_overall"] = {
        "median_pearson_r": float(np.median(finite)) if finite else math.nan,
        "min_pearson_r": float(min(finite)) if finite else math.nan,
    }
    return summary


def hit_rows(comparison: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for row in comparison:
        holm = row.get("p_t_holm")
        bh = row.get("p_t_bh")
        holm_hit = holm not in ("", None) and float(holm) < 0.05
        bh_hit = bh not in ("", None) and float(bh) < 0.05
        raw_lt = float(row["p_t_raw"]) < 0.05
        if not (holm_hit or bh_hit or raw_lt):
            continue
        hits.append(
            {
                "dataset": row["dataset"],
                "selection": row["selection"],
                "k_label": row["k_label"],
                "contrast_id": row["contrast_id"],
                "feature": row["feature"],
                "feature_tier": row["feature_tier"],
                "contrast_tier": row["contrast_tier"],
                "mean_difference": row["mean_difference"],
                "cohen_dz": row["cohen_dz"],
                "p_t_raw": row["p_t_raw"],
                "p_t_holm": holm,
                "p_t_bh": bh,
                "holm_significant": "yes" if holm_hit else "no",
                "bh_significant": "yes" if bh_hit else "no",
            }
        )
    hits.sort(
        key=lambda item: (
            0 if item["holm_significant"] == "yes" else 1,
            0 if item["bh_significant"] == "yes" else 1,
            float(item["p_t_raw"]),
        )
    )
    return hits


def run(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    epochs = read_csv(DEFAULT_EPOCHS)
    windows = read_csv(DEFAULT_AD_WINDOWS)
    gold_condition = read_csv(DEFAULT_CONDITION_FEATURES)
    gold_ad = read_csv(DEFAULT_AD_RESPONSES)
    epochs_by_cell = index_epochs(epochs)
    onsets = unique_onsets(windows)
    onsets_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for onset in onsets:
        onsets_by_subject[onset["subject_id"]].append(onset)

    comparison: list[dict[str, Any]] = []
    coverage_a: list[dict[str, Any]] = []
    coverage_b: list[dict[str, Any]] = []

    all_rows, all_cov = dataset_a_rows(
        epochs_by_cell=epochs_by_cell,
        onsets_by_subject=onsets_by_subject,
        k=None,
        side="around",
    )
    coverage_a.extend(all_cov)
    verification = verify_dataset_a_all(all_rows, gold_condition)
    all_contrasts, _ = contrast_tables(
        [{key: str(value) for key, value in row.items()} for row in all_rows]
    )
    contrast_gate = confirm_contrast_match(all_contrasts, CONFIRMATORY_A)
    comparison.extend(
        flatten_contrasts(
            [dict(row) for row in all_contrasts],
            dataset="A",
            selection="all",
            k=None,
        )
    )
    write_csv(output_dir / "dataset_a_k_all_features.csv", all_rows)

    for side in SELECTIONS:
        for k in K_GRID:
            rows, cov = dataset_a_rows(
                epochs_by_cell=epochs_by_cell,
                onsets_by_subject=onsets_by_subject,
                k=k,
                side=side,
            )
            coverage_a.extend(cov)
            contrasts, _ = contrast_tables(
                [{key: str(value) for key, value in row.items()} for row in rows]
            )
            branch = output_dir / "dataset_a" / side / f"k{k}"
            write_csv(branch / "condition_features.csv", rows)
            write_csv(branch / "eeg_condition_contrasts.csv", contrasts)
            comparison.extend(
                flatten_contrasts(
                    [dict(row) for row in contrasts],
                    dataset="A",
                    selection=side,
                    k=k,
                )
            )

    k1_ad_rows: list[dict[str, Any]] | None = None
    for k in K_GRID:
        rows, cov = dataset_b_rows(
            epochs_by_cell=epochs_by_cell,
            onsets=onsets,
            k=k,
        )
        coverage_b.extend(cov)
        branch = output_dir / "dataset_b" / f"k{k}"
        write_csv(branch / "ad_response_features.csv", rows)
        run_ad_contrasts(branch / "ad_response_features.csv", branch)
        contrasts = read_csv(branch / "eeg_ad_response_contrasts.csv")
        comparison.extend(
            flatten_contrasts(
                [dict(row) for row in contrasts],
                dataset="B",
                selection="prepost",
                k=k,
            )
        )
        if k == 1:
            k1_ad_rows = rows

    assert k1_ad_rows is not None
    k1_corr = dataset_b_k1_correlation(k1_ad_rows, gold_ad)

    write_csv(output_dir / "coverage_dataset_a.csv", coverage_a)
    write_csv(output_dir / "coverage_dataset_b.csv", coverage_b)
    write_csv(output_dir / "comparison.csv", comparison)
    hits = hit_rows(comparison)
    if hits:
        write_csv(output_dir / "hits_raw_or_corrected.csv", hits)

    holm_hits = [row for row in hits if row["holm_significant"] == "yes"]
    bh_hits = [row for row in hits if row["bh_significant"] == "yes"]
    manifest = {
        "exploratory": True,
        "confirmatory_untouched": True,
        "k_grid": list(K_GRID),
        "selections_dataset_a": list(SELECTIONS),
        "n_onsets": len(onsets),
        "n_comparison_rows": len(comparison),
        "verification_dataset_a_all": verification,
        "verification_dataset_a_contrasts": contrast_gate,
        "dataset_b_k1_vs_onset_locked": k1_corr["_overall"],
        "n_holm_hits": len(holm_hits),
        "n_bh_hits": len(bh_hits),
        "n_nominal_raw_p_lt_05": sum(
            1 for row in comparison if float(row["p_t_raw"]) < 0.05
        ),
        "holm_hits": holm_hits[:40],
        "bh_hits": bh_hits[:40],
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    print(json.dumps({key: manifest[key] for key in (
        "n_holm_hits",
        "n_bh_hits",
        "n_nominal_raw_p_lt_05",
        "verification_dataset_a_all",
        "verification_dataset_a_contrasts",
        "dataset_b_k1_vs_onset_locked",
    )}, indent=2))
    if holm_hits:
        print("Holm hits:")
        for row in holm_hits[:20]:
            print(
                f"  {row['dataset']}/{row['selection']}/k={row['k_label']} "
                f"{row['contrast_id']} {row['feature']} "
                f"dz={float(row['cohen_dz']):.3f} "
                f"pHolm={float(row['p_t_holm']):.4f}"
            )
    else:
        print("No Holm hits at any k or selection.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == "__main__":
    main()
