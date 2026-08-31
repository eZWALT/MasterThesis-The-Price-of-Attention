"""Exhaustive k = 1..K neighbourhood search for ad-local EEG averaging.

Exploratory only. Does not touch Gold or ICA. Reads the frozen 4 s
condition-epoch table, medians the k nearest retained tiles to each
visual onset for every k in 1..90 (three Dataset A selections plus
Dataset B pre/post Δ), then sign-flips person-level contrast scores
jointly across k until a wall-clock deadline.

The permutation answers: if you search every neighbourhood, how often
does a Holm cell appear by chance? Holm inside each k is the same
family as confirmatory; it is not a correction for searching 90 k.

    python -u analysis/eeg/statistics/run_ad_local_k_exhaustive.py --hours 2
    python -u analysis/eeg/statistics/run_ad_local_k_exhaustive.py --status
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_ad_contrasts import cell_name  # noqa: E402
from build_ad_local_epochs import (  # noqa: E402
    epoch_mid,
    index_epochs,
    unique_onsets,
)
from build_condition_contrasts import (  # noqa: E402
    FEATURE_TIERS,
    CONDITIONS,
    holm_adjust,
    read_csv,
    write_csv,
)
from build_posthoc_pairwise import bh_adjust, by_adjust  # noqa: E402


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
GOLD_FEATURES = REPOSITORY_ROOT / "src/project/logs/xdf/gold/features"
GOLD_WINDOWS = REPOSITORY_ROOT / "src/project/logs/xdf/gold/windows"
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "analysis/eeg/statistics/outputs/sensitivity/ad_local_epochs/exhaustive"
)
FEATURES = tuple(FEATURE_TIERS)
N_FEAT = len(FEATURES)
A_CONDITIONS = list(CONDITIONS)
A_CONTRASTS = (
    "any_ad_vs_no_ads",
    "inline_vs_block",
    "early_vs_late",
    "format_x_timing",
)
A_PRIMARY = 3
A_WEIGHTS = np.asarray(
    [
        [-1.0, 0.25, 0.25, 0.25, 0.25],
        [0.0, 0.5, 0.5, -0.5, -0.5],
        [0.0, 0.5, -0.5, 0.5, -0.5],
        [0.0, 1.0, -1.0, -1.0, 1.0],
    ],
    dtype=np.float64,
)
B_CELLS = (
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
    "no_ads_early",
    "no_ads_late",
)
B_CONTRASTS = (
    "inline_early_vs_no_ad_early",
    "block_early_vs_no_ad_early",
    "inline_late_vs_no_ad_late",
    "block_late_vs_no_ad_late",
    "any_ad_vs_matched_no_ad",
    "inline_vs_block",
    "early_vs_late",
    "format_x_timing",
)
B_PRIMARY = 4
B_WEIGHTS = np.asarray(
    [
        [1, 0, 0, 0, -1, 0],
        [0, 0, 1, 0, -1, 0],
        [0, 1, 0, 0, 0, -1],
        [0, 0, 0, 1, 0, -1],
        [0.25, 0.25, 0.25, 0.25, -0.5, -0.5],
        [0.5, 0.5, -0.5, -0.5, 0, 0],
        [0.5, -0.5, 0.5, -0.5, 0, 0],
        [1, -1, -1, 1, 0, 0],
    ],
    dtype=np.float64,
)
SELECTIONS = ("around", "pre", "post")
GATES = (
    ("A", "around", 5, "any_ad_vs_no_ads", "fz_theta_power_db_uv2", -0.11781617953958755),
    ("A", "around", 10, "any_ad_vs_no_ads", "fz_theta_power_db_uv2", -0.2323535800662929),
    ("B", "prepost", 3, "inline_late_vs_no_ad_late", "posterior_alpha_power_db_uv2", -0.8062828480512715),
)


def log(output: Path, payload: dict[str, Any]) -> None:
    payload = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), **payload}
    line = "PROGRESS " + json.dumps(payload, default=str)
    print(line, flush=True)
    (output / "progress.json").write_text(json.dumps(payload, indent=2, default=str))
    with (output / "progress.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, default=str) + "\n")


def ttest_last_axis(scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = scores.shape[-1]
    mean = scores.mean(axis=-1)
    sd = scores.std(axis=-1, ddof=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        dz = mean / sd
        t_stat = dz * math.sqrt(n)
    p_val = 2.0 * stats.t.sf(np.abs(t_stat), n - 1)
    return t_stat, p_val, dz


def holm_last_axis(p_val: np.ndarray) -> np.ndarray:
    m = p_val.shape[-1]
    order = np.argsort(p_val, axis=-1)
    sorted_p = np.take_along_axis(p_val, order, axis=-1)
    factors = np.arange(m, 0, -1, dtype=np.float64)
    adjusted_sorted = np.minimum(1.0, np.maximum.accumulate(sorted_p * factors, axis=-1))
    inverse = np.argsort(order, axis=-1)
    return np.take_along_axis(adjusted_sorted, inverse, axis=-1)


def holm_axis(p_val: np.ndarray, axis: int) -> np.ndarray:
    moved = np.moveaxis(p_val, axis, -1)
    adjusted = holm_last_axis(moved)
    return np.moveaxis(adjusted, -1, axis)


def tile_features(rows: list[dict[str, str]]) -> np.ndarray:
    if not rows:
        return np.zeros((0, N_FEAT), dtype=np.float64)
    return np.asarray(
        [[float(row[feature]) for feature in FEATURES] for row in rows],
        dtype=np.float64,
    )


def sorted_sides(
    tiles: list[dict[str, str]], onset_s: float
) -> dict[str, tuple[np.ndarray, list[tuple[str, str]]]]:
    buckets: dict[str, list[tuple[float, dict[str, str]]]] = {
        "around": [],
        "pre": [],
        "post": [],
    }
    for row in tiles:
        mid = epoch_mid(row)
        dist = abs(mid - onset_s)
        buckets["around"].append((dist, row))
        if mid < onset_s:
            buckets["pre"].append((dist, row))
        else:
            buckets["post"].append((dist, row))
    out: dict[str, tuple[np.ndarray, list[tuple[str, str]]]] = {}
    for side, items in buckets.items():
        items.sort(key=lambda item: item[0])
        rows = [item[1] for item in items]
        keys = [(row["window_id"], row["epoch_index"]) for row in rows]
        out[side] = (tile_features(rows), keys)
    return out


def union_median(
    matrices: list[np.ndarray],
    keys: list[list[tuple[str, str]]],
    k: int,
) -> tuple[np.ndarray, int]:
    collected: dict[tuple[str, str], np.ndarray] = {}
    for matrix, key_list in zip(matrices, keys):
        take = min(k, len(key_list))
        for index in range(take):
            collected[key_list[index]] = matrix[index]
    if not collected:
        return np.full(N_FEAT, np.nan), 0
    stacked = np.stack(list(collected.values()), axis=0)
    return np.median(stacked, axis=0), stacked.shape[0]


def prefix_median(matrix: np.ndarray, k: int) -> tuple[np.ndarray, int]:
    take = min(k, matrix.shape[0])
    if take == 0:
        return np.full(N_FEAT, np.nan), 0
    return np.median(matrix[:take], axis=0), take


def build_arrays(
    *,
    epochs_by_cell: dict[tuple[str, str], list[dict[str, str]]],
    onsets: list[dict[str, str]],
    k_max: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]]:
    onsets_by_subject: dict[str, list[dict[str, str]]] = defaultdict(list)
    for onset in onsets:
        onsets_by_subject[onset["subject_id"]].append(onset)
    subjects = sorted(onsets_by_subject)
    n_subj = len(subjects)
    n_k = k_max
    a_values = np.full((3, n_k, n_subj, 5, N_FEAT), np.nan)
    a_count = np.zeros((3, n_k, n_subj, 5), dtype=np.int16)
    b_delta = np.full((n_k, n_subj, 6, N_FEAT), np.nan)
    b_count = np.zeros((n_k, n_subj, 6, 2), dtype=np.int16)
    packed: dict[str, dict[str, dict[str, tuple[np.ndarray, list[tuple[str, str]]]]]] = (
        defaultdict(dict)
    )
    for onset in onsets:
        tiles = epochs_by_cell[(onset["subject_id"], onset["condition"])]
        packed[onset["subject_id"]][onset["reference_id"]] = sorted_sides(
            tiles, float(onset["reference_onset_eeg_offset_s"])
        )

    for s_i, subject in enumerate(subjects):
        by_condition: dict[str, list[str]] = defaultdict(list)
        cell_of: dict[str, str] = {}
        for onset in onsets_by_subject[subject]:
            by_condition[onset["condition"]].append(onset["reference_id"])
            cell_of[onset["reference_id"]] = cell_name(onset)
        for k in range(1, k_max + 1):
            k_i = k - 1
            for condition in A_CONDITIONS:
                c_i = A_CONDITIONS.index(condition)
                refs = by_condition[condition]
                for sel_i, side in enumerate(SELECTIONS):
                    matrices = [packed[subject][ref][side][0] for ref in refs]
                    keys = [packed[subject][ref][side][1] for ref in refs]
                    median, count = union_median(matrices, keys, k)
                    a_values[sel_i, k_i, s_i, c_i] = median
                    a_count[sel_i, k_i, s_i, c_i] = count
            for ref, cell in cell_of.items():
                b_i = B_CELLS.index(cell)
                pre_m, pre_n = prefix_median(packed[subject][ref]["pre"][0], k)
                post_m, post_n = prefix_median(packed[subject][ref]["post"][0], k)
                b_delta[k_i, s_i, b_i] = post_m - pre_m
                b_count[k_i, s_i, b_i] = (pre_n, post_n)
    return a_values, a_count, b_delta, b_count, subjects, packed


def scores_from_values(values: np.ndarray, weights: np.ndarray) -> np.ndarray:
    # values: (..., n_cell, n_feat) ; weights: (n_contrast, n_cell)
    return np.einsum("cC, ...Cf -> ...cf", weights, values)


def point_table(
    scores: np.ndarray,
    *,
    dataset: str,
    selection: str,
    contrasts: tuple[str, ...],
    n_primary: int,
) -> list[dict[str, Any]]:
    # scores: (n_k, n_contrast, n_feat, n_subj)
    t_stat, p_raw, dz = ttest_last_axis(scores)
    mean = scores.mean(axis=-1)
    sd = scores.std(axis=-1, ddof=1)
    n = scores.shape[-1]
    se = sd / math.sqrt(n)
    critical = float(stats.t.ppf(0.975, n - 1))
    rows: list[dict[str, Any]] = []
    n_k, n_contrast, n_feat = t_stat.shape
    for k_i in range(n_k):
        holm = np.zeros((n_contrast, n_feat), dtype=np.float64)
        bh = np.full((n_contrast, n_feat), np.nan)
        by = np.full((n_contrast, n_feat), np.nan)
        for f_i in range(n_feat):
            family = p_raw[k_i, :n_primary, f_i]
            holm[:n_primary, f_i] = holm_adjust(family.tolist())
            bh[:n_primary, f_i] = bh_adjust(family.tolist())
            by[:n_primary, f_i] = by_adjust(family.tolist())
        for c_i, contrast in enumerate(contrasts):
            primary = c_i < n_primary
            for f_i, feature in enumerate(FEATURES):
                p_h = holm[c_i, f_i] if primary else math.nan
                p_bh = bh[c_i, f_i] if primary else math.nan
                rows.append(
                    {
                        "dataset": dataset,
                        "selection": selection,
                        "k_epochs": k_i + 1,
                        "k_label": str(k_i + 1),
                        "contrast_id": contrast,
                        "contrast_tier": "primary" if primary else "secondary",
                        "feature": feature,
                        "feature_tier": FEATURE_TIERS[feature],
                        "n_participants": n,
                        "mean_difference": float(mean[k_i, c_i, f_i]),
                        "sd_difference": float(sd[k_i, c_i, f_i]),
                        "se_difference": float(se[k_i, c_i, f_i]),
                        "ci_lower": float(mean[k_i, c_i, f_i] - critical * se[k_i, c_i, f_i]),
                        "ci_upper": float(mean[k_i, c_i, f_i] + critical * se[k_i, c_i, f_i]),
                        "cohen_dz": float(dz[k_i, c_i, f_i]),
                        "t_statistic": float(t_stat[k_i, c_i, f_i]),
                        "degrees_of_freedom": n - 1,
                        "p_t_raw": float(p_raw[k_i, c_i, f_i]),
                        "p_t_holm": "" if not primary else float(p_h),
                        "p_t_bh": "" if not primary else float(p_bh),
                        "p_t_by": "" if not primary else float(by[c_i, f_i]),
                        "holm_significant": (
                            "yes" if primary and p_h < 0.05 else "no"
                        ),
                        "bh_significant": (
                            "yes" if primary and p_bh < 0.05 else "no"
                        ),
                    }
                )
    return rows


def check_gates(rows: list[dict[str, Any]]) -> None:
    lookup = {
        (
            row["dataset"],
            row["selection"],
            int(row["k_epochs"]),
            row["contrast_id"],
            row["feature"],
        ): float(row["cohen_dz"])
        for row in rows
    }
    for dataset, selection, k, contrast, feature, expected in GATES:
        got = lookup[(dataset, selection, k, contrast, feature)]
        if abs(got - expected) > 1e-9:
            raise RuntimeError(
                f"Gate failed {dataset}/{selection}/k={k}/{contrast}/{feature}: "
                f"{got} != {expected}"
            )


def signflip_min_holm(
    person_scores: np.ndarray,
    *,
    n_primary: int,
    n_perm: int,
    chunk: int,
    rng: np.random.Generator,
    deadline: float,
    output: Path,
    label: str,
) -> dict[str, Any]:
    """person_scores: (n_k, n_contrast, n_feat, n_subj)."""
    n_k, n_contrast, n_feat, n_subj = person_scores.shape
    _, p_obs, _ = ttest_last_axis(person_scores)
    holm_obs = np.full_like(p_obs, np.nan)
    for k_i in range(n_k):
        for f_i in range(n_feat):
            holm_obs[k_i, :n_primary, f_i] = holm_adjust(
                p_obs[k_i, :n_primary, f_i].tolist()
            )
    min_obs = np.nanmin(holm_obs[:, :n_primary, :], axis=0)
    hit_obs = np.nanmin(holm_obs[:, :n_primary, :], axis=0) < 0.05
    n_hit_obs = int(np.nansum(holm_obs[:, :n_primary, :] < 0.05))
    extreme_min = np.zeros((n_primary, n_feat), dtype=np.int64)
    extreme_hits = np.zeros((n_primary, n_feat), dtype=np.int64)
    extreme_count = 0
    done = 0
    started = time.monotonic()
    while done < n_perm and time.monotonic() < deadline:
        take = min(chunk, n_perm - done)
        signs = rng.choice(np.array([-1.0, 1.0]), size=(take, n_subj))
        # flipped: (take, n_k, n_contrast, n_feat, n_subj)
        flipped = person_scores[None, ...] * signs[:, None, None, None, :]
        _, p_perm, _ = ttest_last_axis(flipped)
        # Holm along contrast axis for primary only, vectorized over take × k × feat
        holm_perm = holm_axis(p_perm[:, :, :n_primary, :], axis=2)
        min_perm = holm_perm.min(axis=1)
        n_hit_perm = np.sum(holm_perm < 0.05, axis=(1, 2))
        extreme_min += np.sum(min_perm <= min_obs[None, :, :], axis=0)
        extreme_hits += np.sum(min_perm < 0.05, axis=0)
        extreme_count += int(np.sum(n_hit_perm >= n_hit_obs))
        done += take
        elapsed = time.monotonic() - started
        rate = done / max(elapsed, 1e-6)
        log(
            output,
            {
                "phase": "perm",
                "label": label,
                "n_perm_done": done,
                "n_perm_target": n_perm,
                "perms_per_s": round(rate, 2),
                "eta_s": round((n_perm - done) / max(rate, 1e-6), 1),
                "deadline_remaining_s": round(deadline - time.monotonic(), 1),
                "n_holm_hits_obs": n_hit_obs,
            },
        )
    p_search = (extreme_min + 1) / (done + 1)
    p_any = (extreme_hits + 1) / (done + 1)
    return {
        "n_perm": done,
        "n_holm_hits_obs": n_hit_obs,
        "p_at_least_this_many_hits": (extreme_count + 1) / (done + 1),
        "min_holm_obs": min_obs.tolist(),
        "p_search_min_holm": p_search.tolist(),
        "p_any_k_holm": p_any.tolist(),
        "contrasts": list(A_CONTRASTS[:n_primary] if n_primary == 3 else B_CONTRASTS[:n_primary]),
        "features": list(FEATURES),
    }


def jackknife_stability(
    person_scores: np.ndarray, n_primary: int
) -> list[dict[str, Any]]:
    n_k, n_contrast, n_feat, n_subj = person_scores.shape
    rows: list[dict[str, Any]] = []
    for drop in range(n_subj):
        keep = [index for index in range(n_subj) if index != drop]
        subset = person_scores[..., keep]
        _, p_raw, _ = ttest_last_axis(subset)
        for k_i in range(n_k):
            for f_i in range(n_feat):
                holm = holm_adjust(p_raw[k_i, :n_primary, f_i].tolist())
                for c_i in range(n_primary):
                    if holm[c_i] < 0.05:
                        rows.append(
                            {
                                "dropped_index": drop,
                                "k_epochs": k_i + 1,
                                "contrast_index": c_i,
                                "feature": FEATURES[f_i],
                                "p_t_holm": holm[c_i],
                            }
                        )
    return rows


def write_plots(rows: list[dict[str, Any]], output: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    ink = "#12202A"
    plt.rcParams.update({"pdf.fonttype": 42, "font.family": "DejaVu Sans"})
    frame = { }
    # lazy: rebuild lookups
    by: dict[tuple, dict[str, Any]] = {}
    for row in rows:
        by[
            (
                row["dataset"],
                row["selection"],
                int(row["k_epochs"]),
                row["contrast_id"],
                row["feature"],
            )
        ] = row
    k_vals = list(range(1, 1 + max(int(row["k_epochs"]) for row in rows)))

    def series(dataset: str, selection: str, contrast: str, feature: str, column: str) -> list[float]:
        return [
            float(by[(dataset, selection, k, contrast, feature)][column])
            for k in k_vals
        ]

    fig_a, axes = plt.subplots(2, 3, figsize=(12, 7), constrained_layout=True)
    for col, selection in enumerate(SELECTIONS):
        for row_i, feature in enumerate(
            ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
        ):
            axis = axes[row_i, col]
            for contrast, name in (
                ("any_ad_vs_no_ads", "Any ad"),
                ("inline_vs_block", "Format"),
                ("early_vs_late", "Timing"),
            ):
                p_vals = series("A", selection, contrast, feature, "p_t_holm")
                axis.plot(k_vals, p_vals, lw=1.2, label=name)
            axis.axhline(0.05, color="#C45C26", lw=0.8, ls="--")
            axis.set_ylim(0, 1)
            axis.set_title(f"{selection} · {feature.replace('_power_db_uv2','')}", loc="left", color=ink, fontsize=9)
            axis.set_xlabel("k tiles")
            axis.set_ylabel("Holm p")
    axes[0, 2].legend(frameon=False, fontsize=8)
    fig_a.suptitle("Dataset A Holm p vs neighbourhood size (k = 1..90)", color=ink, x=0.01, ha="left")
    fig_a.savefig(output / "dataset_a_holm_vs_k.png", dpi=160, facecolor="white")
    fig_a.savefig(output / "dataset_a_holm_vs_k.pdf", facecolor="white")

    fig_b, axes_b = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    for contrast, name in (
        ("inline_early_vs_no_ad_early", "Imp early"),
        ("block_early_vs_no_ad_early", "Exp early"),
        ("inline_late_vs_no_ad_late", "Imp late"),
        ("block_late_vs_no_ad_late", "Exp late"),
    ):
        axes_b[0].plot(
            k_vals,
            series("B", "prepost", contrast, "posterior_alpha_power_db_uv2", "cohen_dz"),
            label=name,
        )
        axes_b[1].plot(
            k_vals,
            series("B", "prepost", contrast, "posterior_alpha_power_db_uv2", "p_t_holm"),
            label=name,
        )
    axes_b[0].axhline(0, color="#5C6B73", lw=0.8)
    axes_b[1].axhline(0.05, color="#C45C26", lw=0.8, ls="--")
    axes_b[0].set_title("Dataset B posterior alpha dz", loc="left", color=ink)
    axes_b[1].set_title("Dataset B posterior alpha Holm p", loc="left", color=ink)
    axes_b[0].set_xlabel("k tiles")
    axes_b[1].set_xlabel("k tiles")
    axes_b[0].set_ylabel("Cohen dz")
    axes_b[1].set_ylabel("Holm p")
    axes_b[1].set_ylim(0, 1)
    axes_b[0].legend(frameon=False, fontsize=8)
    fig_b.savefig(output / "dataset_b_posterior_alpha_vs_k.png", dpi=160, facecolor="white")
    fig_b.savefig(output / "dataset_b_posterior_alpha_vs_k.pdf", facecolor="white")

    with PdfPages(output / "exhaustive_k_report.pdf") as pdf:
        pdf.savefig(fig_a, facecolor="white")
        pdf.savefig(fig_b, facecolor="white")
        hits = [
            row
            for row in rows
            if row["holm_significant"] == "yes"
        ]
        fig = plt.figure(figsize=(11, 8.5))
        fig.text(0.08, 0.92, f"Holm hits across k = 1..{max(k_vals)}: {len(hits)}", fontsize=16, color=ink)
        lines = [
            f"{row['dataset']}/{row['selection']}/k={row['k_label']:>3}  "
            f"{row['contrast_id'][:28]:28}  {row['feature'][:28]:28}  "
            f"dz={float(row['cohen_dz']):+.2f}  Holm={float(row['p_t_holm']):.4f}"
            for row in sorted(hits, key=lambda item: float(item["p_t_holm"]))[:40]
        ]
        fig.text(0.08, 0.86, "\n".join(lines) or "none", fontsize=8, family="DejaVu Sans Mono", va="top", color=ink)
        pdf.savefig(fig, facecolor="white")
        plt.close(fig)
    plt.close(fig_a)
    plt.close(fig_b)


def random_ranking_dataset_a(
    *,
    packed: dict[str, dict[str, dict[str, tuple[np.ndarray, list]]]],
    onsets: list[dict[str, str]],
    subjects: list[str],
    k_max: int,
    n_hit_obs: int,
    rng: np.random.Generator,
    deadline: float,
    output: Path,
) -> dict[str, Any]:
    """Break distance ranking: random tile order, then the same k-prefix medians."""
    refs_by: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for onset in onsets:
        refs_by[onset["subject_id"]][onset["condition"]].append(onset["reference_id"])
    n_subj = len(subjects)
    done = 0
    extreme = 0
    started = time.monotonic()
    while time.monotonic() < deadline:
        values = np.full((k_max, n_subj, 5, N_FEAT), np.nan)
        for s_i, subject in enumerate(subjects):
            for c_i, condition in enumerate(A_CONDITIONS):
                refs = refs_by[subject][condition]
                matrix = packed[subject][refs[0]]["around"][0]
                order = rng.permutation(matrix.shape[0])
                shuffled = matrix[order]
                n_tiles = shuffled.shape[0]
                for k in range(1, k_max + 1):
                    take = min(k, n_tiles)
                    values[k - 1, s_i, c_i] = np.median(shuffled[:take], axis=0)
        person = np.moveaxis(scores_from_values(values, A_WEIGHTS), [1, 2, 3], [3, 1, 2])
        _, p_raw, _ = ttest_last_axis(person)
        n_hit = 0
        for k_i in range(k_max):
            for f_i in range(N_FEAT):
                holm = holm_adjust(p_raw[k_i, :A_PRIMARY, f_i].tolist())
                n_hit += int(np.sum(np.asarray(holm) < 0.05))
        if n_hit >= n_hit_obs:
            extreme += 1
        done += 1
        if done % 25 == 0:
            elapsed = time.monotonic() - started
            rate = done / max(elapsed, 1e-6)
            log(
                output,
                {
                    "phase": "random_ranking",
                    "label": "A/around",
                    "n_perm_done": done,
                    "perms_per_s": round(rate, 2),
                    "deadline_remaining_s": round(deadline - time.monotonic(), 1),
                    "n_holm_hits_obs": n_hit_obs,
                },
            )
    return {
        "n_perm": done,
        "n_holm_hits_obs": n_hit_obs,
        "p_at_least_this_many_hits": (extreme + 1) / (done + 1) if done else math.nan,
        "kind": "random_tile_ranking",
    }


def random_ranking_dataset_b(
    *,
    packed: dict[str, dict[str, dict[str, tuple[np.ndarray, list]]]],
    onsets: list[dict[str, str]],
    subjects: list[str],
    k_max: int,
    n_hit_obs: int,
    rng: np.random.Generator,
    deadline: float,
    output: Path,
) -> dict[str, Any]:
    cell_of: dict[str, dict[str, str]] = defaultdict(dict)
    for onset in onsets:
        cell_of[onset["subject_id"]][onset["reference_id"]] = cell_name(onset)
    n_subj = len(subjects)
    done = 0
    extreme = 0
    started = time.monotonic()
    while time.monotonic() < deadline:
        delta = np.full((k_max, n_subj, 6, N_FEAT), np.nan)
        for s_i, subject in enumerate(subjects):
            for ref, cell in cell_of[subject].items():
                b_i = B_CELLS.index(cell)
                pre = packed[subject][ref]["pre"][0]
                post = packed[subject][ref]["post"][0]
                pre_s = pre[rng.permutation(pre.shape[0])]
                post_s = post[rng.permutation(post.shape[0])]
                for k in range(1, k_max + 1):
                    pre_m = np.median(pre_s[: min(k, pre_s.shape[0])], axis=0)
                    post_m = np.median(post_s[: min(k, post_s.shape[0])], axis=0)
                    delta[k - 1, s_i, b_i] = post_m - pre_m
        person = np.moveaxis(scores_from_values(delta, B_WEIGHTS), [1, 2, 3], [3, 1, 2])
        _, p_raw, _ = ttest_last_axis(person)
        n_hit = 0
        for k_i in range(k_max):
            for f_i in range(N_FEAT):
                holm = holm_adjust(p_raw[k_i, :B_PRIMARY, f_i].tolist())
                n_hit += int(np.sum(np.asarray(holm) < 0.05))
        if n_hit >= n_hit_obs:
            extreme += 1
        done += 1
        if done % 10 == 0:
            elapsed = time.monotonic() - started
            rate = done / max(elapsed, 1e-6)
            log(
                output,
                {
                    "phase": "random_ranking",
                    "label": "B/prepost",
                    "n_perm_done": done,
                    "perms_per_s": round(rate, 2),
                    "deadline_remaining_s": round(deadline - time.monotonic(), 1),
                    "n_holm_hits_obs": n_hit_obs,
                },
            )
    return {
        "n_perm": done,
        "n_holm_hits_obs": n_hit_obs,
        "p_at_least_this_many_hits": (extreme + 1) / (done + 1) if done else math.nan,
        "kind": "random_tile_ranking",
    }


def run(*, output: Path, k_max: int, hours: float, n_perm: int, chunk: int, seed: int) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "progress.jsonl").write_text("")
    started = time.monotonic()
    deadline = started + hours * 3600.0
    log(output, {"phase": "start", "k_max": k_max, "hours": hours, "n_perm": n_perm, "seed": seed})
    epochs = read_csv(GOLD_FEATURES / "condition_epoch_features.csv")
    windows = read_csv(GOLD_WINDOWS / "ad_analysis_windows.csv")
    epochs_by_cell = index_epochs(epochs)
    onsets = unique_onsets(windows)
    log(output, {"phase": "precompute", "n_onsets": len(onsets), "n_epochs": len(epochs)})
    a_values, a_count, b_delta, b_count, subjects, packed = build_arrays(
        epochs_by_cell=epochs_by_cell,
        onsets=onsets,
        k_max=k_max,
    )
    np.savez_compressed(
        output / "arrays.npz",
        a_values=a_values,
        a_count=a_count,
        b_delta=b_delta,
        b_count=b_count,
        subjects=np.asarray(subjects),
        features=np.asarray(FEATURES),
    )
    a_person = {
        side: np.moveaxis(scores_from_values(a_values[sel_i], A_WEIGHTS), [1, 2, 3], [3, 1, 2])
        for sel_i, side in enumerate(SELECTIONS)
    }
    b_person = np.moveaxis(scores_from_values(b_delta, B_WEIGHTS), [1, 2, 3], [3, 1, 2])
    rows: list[dict[str, Any]] = []
    for side in SELECTIONS:
        rows.extend(
            point_table(
                a_person[side],
                dataset="A",
                selection=side,
                contrasts=A_CONTRASTS,
                n_primary=A_PRIMARY,
            )
        )
    rows.extend(
        point_table(
            b_person,
            dataset="B",
            selection="prepost",
            contrasts=B_CONTRASTS,
            n_primary=B_PRIMARY,
        )
    )
    check_gates(rows)
    write_csv(output / "comparison.csv", rows)
    hits = [row for row in rows if row["holm_significant"] == "yes"]
    write_csv(output / "holm_hits.csv", hits) if hits else None
    planned_a = [
        row
        for row in hits
        if row["dataset"] == "A"
        and row["feature"] in ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
    ]
    coverage = []
    for sel_i, side in enumerate(SELECTIONS):
        for k_i in range(k_max):
            coverage.append(
                {
                    "selection": side,
                    "k_epochs": k_i + 1,
                    "median_n_selected": float(np.median(a_count[sel_i, k_i])),
                    "min_n_selected": int(np.min(a_count[sel_i, k_i])),
                    "n_cells_saturated": int(np.sum(a_count[sel_i, k_i] < k_i + 1)),
                }
            )
    write_csv(output / "coverage.csv", coverage)
    log(
        output,
        {
            "phase": "point_estimates",
            "n_rows": len(rows),
            "n_holm_hits": len(hits),
            "n_planned_feature_dataset_a_holm": len(planned_a),
            "elapsed_s": round(time.monotonic() - started, 1),
        },
    )

    rng = np.random.default_rng(seed)
    n_slots = 6
    remaining = max(30.0, deadline - time.monotonic() - 180.0)
    slot = remaining / n_slots
    perm_results: dict[str, Any] = {}
    for side in SELECTIONS:
        perm_results[f"A_{side}"] = signflip_min_holm(
            a_person[side],
            n_primary=A_PRIMARY,
            n_perm=n_perm,
            chunk=chunk,
            rng=rng,
            deadline=time.monotonic() + slot,
            output=output,
            label=f"A/{side}",
        )
    perm_results["B_prepost"] = signflip_min_holm(
        b_person,
        n_primary=B_PRIMARY,
        n_perm=n_perm,
        chunk=chunk,
        rng=rng,
        deadline=time.monotonic() + slot,
        output=output,
        label="B/prepost",
    )
    perm_results["A_around_random_ranking"] = random_ranking_dataset_a(
        packed=packed,
        onsets=onsets,
        subjects=subjects,
        k_max=k_max,
        n_hit_obs=perm_results["A_around"]["n_holm_hits_obs"],
        rng=rng,
        deadline=time.monotonic() + slot,
        output=output,
    )
    perm_results["B_prepost_random_ranking"] = random_ranking_dataset_b(
        packed=packed,
        onsets=onsets,
        subjects=subjects,
        k_max=k_max,
        n_hit_obs=perm_results["B_prepost"]["n_holm_hits_obs"],
        rng=rng,
        deadline=time.monotonic() + slot,
        output=output,
    )
    (output / "permutation.json").write_text(json.dumps(perm_results, indent=2))
    log(output, {"phase": "jackknife", "elapsed_s": round(time.monotonic() - started, 1)})
    jack_b = jackknife_stability(b_person, B_PRIMARY)
    if jack_b:
        write_csv(output / "jackknife_b_holm_hits.csv", jack_b)
    log(output, {"phase": "plots"})
    write_plots(rows, output)
    findings = {
        "k_max": k_max,
        "n_holm_hits": len(hits),
        "n_planned_feature_dataset_a_holm": len(planned_a),
        "planned_a_hits": planned_a[:30],
        "n_subjects": len(subjects),
        "permutation": {
            key: {
                "n_perm": value["n_perm"],
                "n_holm_hits_obs": value["n_holm_hits_obs"],
                "p_at_least_this_many_hits": value["p_at_least_this_many_hits"],
            }
            for key, value in perm_results.items()
        },
        "elapsed_s": round(time.monotonic() - started, 1),
        "gate_passed": True,
    }
    (output / "findings.json").write_text(json.dumps(findings, indent=2, default=str))
    log(output, {"phase": "done", **findings})
    print("EXHAUSTIVE_COMPLETE", flush=True)


def show_status(output: Path) -> None:
    path = output / "progress.json"
    if not path.exists():
        print("No progress.json yet.")
        return
    print(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--k-max", type=int, default=90)
    parser.add_argument("--hours", type=float, default=2.0)
    parser.add_argument("--n-perm", type=int, default=5_000_000)
    parser.add_argument("--chunk", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20260829)
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    if args.status:
        show_status(args.output_dir)
        return
    run(
        output=args.output_dir,
        k_max=args.k_max,
        hours=args.hours,
        n_perm=args.n_perm,
        chunk=args.chunk,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
