"""Paper-depth EEG audit from frozen person-level scores.

Reads existing contrast tables only. Does not rebuild Gold, fit ICA, or
change the confirmatory contract. Writes MDE, compatibility, LOO people,
sign counts, bootstrap-vs-t disagreements, and the exploratory Holm
inventory so those cells cannot leak into the abstract.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
STATS = REPOSITORY_ROOT / "analysis/eeg/statistics/outputs"
ANALYSIS = REPOSITORY_ROOT / "analysis/eeg/analysis/outputs"
OUT = ANALYSIS / "paper_depth"

PRIMARY_FEATURES = ("fz_theta_power_db_uv2", "posterior_alpha_power_db_uv2")
DATASET_A_PRIMARY = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")
DATASET_B_PRIMARY = (
    "inline_early_vs_no_ad_early",
    "block_early_vs_no_ad_early",
    "inline_late_vs_no_ad_late",
    "block_late_vs_no_ad_late",
)
LABELS = {
    "any_ad_vs_no_ads": "any-ad − no-ads",
    "inline_vs_block": "implicit − explicit",
    "early_vs_late": "early − late",
    "inline_early_vs_no_ad_early": "implicit early − no-ad",
    "block_early_vs_no_ad_early": "explicit early − no-ad",
    "inline_late_vs_no_ad_late": "implicit late − no-ad",
    "block_late_vs_no_ad_late": "explicit late − no-ad",
    "fz_theta_power_db_uv2": "Fz theta",
    "posterior_alpha_power_db_uv2": "posterior alpha",
}
FEATURE_SHORT = {
    "fz_theta_power_db_uv2": "Fz theta",
    "posterior_alpha_power_db_uv2": "posterior alpha",
    "theta_power_db_uv2": "global theta",
    "alpha_power_db_uv2": "global alpha",
    "beta_power_db_uv2": "global beta",
    "delta_power_db_uv2": "global delta",
    "gamma_power_db_uv2": "global gamma",
    "delta_relative_power": "relative delta",
    "theta_relative_power": "relative theta",
    "alpha_relative_power": "relative alpha",
    "beta_relative_power": "relative beta",
    "gamma_relative_power": "relative gamma",
    "faa_log_f4_minus_f3": "FAA",
    "engagement_beta_over_alpha_theta": "Pope global",
    "engagement_pope_frontocentral_beta_over_alpha_theta": "Pope FC",
    "engagement_kislov_central_beta16_24_over_alpha8_12": "Kislov",
}


def mde_dz(n: int, alpha: float, power: float = 0.80) -> float:
    df = n - 1
    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
    t_beta = float(stats.t.ppf(power, df))
    return (t_crit + t_beta) / np.sqrt(n)


def observed_power(dz: float, n: int, alpha: float) -> float:
    df = n - 1
    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
    nc = abs(dz) * np.sqrt(n)
    return float(
        stats.nct.sf(t_crit, df, nc) + stats.nct.cdf(-t_crit, df, nc)
    )


def tost_p(mean: float, se: float, df: int, bound: float) -> float:
    t_lo = (mean - (-bound)) / se
    t_hi = (bound - mean) / se
    p_lo = float(stats.t.sf(t_lo, df))
    p_hi = float(stats.t.sf(t_hi, df))
    return max(p_lo, p_hi)


def n_for_power(sd: float, delta: float, alpha: float, power: float = 0.80) -> int:
    for n in range(4, 400):
        if mde_dz(n, alpha, power) * sd <= delta:
            return n
    return 400


def loo_people(scores: pd.DataFrame, contrast_id: str, feature: str) -> dict:
    block = scores[
        (scores["contrast_id"] == contrast_id) & (scores["feature"] == feature)
    ].copy()
    values = {
        str(row.subject_id): float(row.difference) for row in block.itertuples()
    }
    subjects = list(values)
    diffs = np.array([values[s] for s in subjects], dtype=float)
    full_mean = float(np.mean(diffs))
    full_sign = np.sign(full_mean) if full_mean != 0 else 0.0
    rows = []
    for i, subject in enumerate(subjects):
        left = np.delete(diffs, i)
        mean_i = float(np.mean(left))
        rows.append(
            {
                "subject_id": subject,
                "left_out_value": float(diffs[i]),
                "loo_mean": mean_i,
                "mean_shift": mean_i - full_mean,
                "sign_flipped": bool(np.sign(mean_i) != full_sign and full_sign != 0),
            }
        )
    frame = pd.DataFrame(rows)
    worst = frame.iloc[frame["mean_shift"].abs().idxmax()]
    sign_stable = float((~frame["sign_flipped"]).mean())
    return {
        "n": int(len(subjects)),
        "full_mean": full_mean,
        "n_positive": int((diffs > 0).sum()),
        "n_negative": int((diffs < 0).sum()),
        "n_zero": int((diffs == 0).sum()),
        "sign_stability": sign_stable,
        "max_influencer": str(worst["subject_id"]),
        "max_influencer_value": float(worst["left_out_value"]),
        "max_mean_shift": float(worst["mean_shift"]),
        "people": frame,
    }


def verify_t(diffs: np.ndarray, stored: pd.Series) -> dict:
    n = len(diffs)
    mean = float(np.mean(diffs))
    sd = float(np.std(diffs, ddof=1))
    se = sd / np.sqrt(n)
    t_stat, p_raw = stats.ttest_1samp(diffs, 0.0)
    t_crit = float(stats.t.ppf(0.975, n - 1))
    lo = mean - t_crit * se
    hi = mean + t_crit * se
    dz = mean / sd if sd else float("nan")
    return {
        "recomputed_mean": mean,
        "recomputed_sd": sd,
        "recomputed_t": float(t_stat),
        "recomputed_p": float(p_raw),
        "recomputed_ci_lower": lo,
        "recomputed_ci_upper": hi,
        "recomputed_dz": float(dz),
        "mean_match": abs(mean - float(stored["mean_difference"])) < 1e-9,
        "p_match": abs(float(p_raw) - float(stored["p_t_raw"])) < 1e-12,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    condition_tests = pd.read_csv(STATS / "eeg_condition_contrasts.csv")
    ad_tests = pd.read_csv(STATS / "eeg_ad_response_contrasts.csv")
    condition_scores = pd.read_csv(STATS / "eeg_condition_contrast_scores.csv")
    ad_scores = pd.read_csv(STATS / "eeg_ad_response_contrast_scores.csv")
    diagnostics = pd.read_csv(ANALYSIS / "tables/assumption_influence_diagnostics.csv")
    ica = json.loads((STATS / "ica_sensitivity_comparison.json").read_text())

    confirmatory_rows = []
    loo_frames = []
    n = 18
    for path, tests, scores, contrasts, family in (
        ("A", condition_tests, condition_scores, DATASET_A_PRIMARY, 3),
        ("B", ad_tests, ad_scores, DATASET_B_PRIMARY, 4),
    ):
        alpha_holm = 0.05 / family
        alpha_raw = 0.05
        for contrast_id in contrasts:
            for feature in PRIMARY_FEATURES:
                stored = tests[
                    (tests["contrast_id"] == contrast_id)
                    & (tests["feature"] == feature)
                    & (tests["contrast_tier"] == "primary")
                ].iloc[0]
                block = scores[
                    (scores["contrast_id"] == contrast_id)
                    & (scores["feature"] == feature)
                ]
                diffs = block["difference"].to_numpy(dtype=float)
                check = verify_t(diffs, stored)
                people = loo_people(scores, contrast_id, feature)
                people["people"] = people["people"].assign(
                    dataset=dataset,
                    contrast_id=contrast_id,
                    feature=feature,
                )
                loo_frames.append(people["people"])
                diag = diagnostics[
                    (diagnostics["analysis"] == ("condition" if dataset == "A" else "ad"))
                    & (diagnostics["contrast_id"] == contrast_id)
                    & (diagnostics["feature"] == feature)
                ]
                boot_lo = (
                    float(diag["bootstrap_mean_ci_lower"].iloc[0]) if len(diag) else float("nan")
                )
                boot_hi = (
                    float(diag["bootstrap_mean_ci_upper"].iloc[0]) if len(diag) else float("nan")
                )
                t_excludes = not (
                    float(stored["ci_lower"]) <= 0 <= float(stored["ci_upper"])
                )
                boot_excludes = not (boot_lo <= 0 <= boot_hi)
                sd = float(stored["sd_difference"])
                se = float(stored["se_difference"])
                mean = float(stored["mean_difference"])
                dz = float(stored["cohen_dz"])
                confirmatory_rows.append(
                    {
                        "path": path,
                        "contrast_id": contrast_id,
                        "contrast": LABELS[contrast_id],
                        "feature": LABELS[feature],
                        "n": int(stored["n_participants"]),
                        "mean_db": mean,
                        "sd_db": sd,
                        "se_db": se,
                        "ci_lower": float(stored["ci_lower"]),
                        "ci_upper": float(stored["ci_upper"]),
                        "ci_halfwidth": 0.5
                        * (float(stored["ci_upper"]) - float(stored["ci_lower"])),
                        "cohen_dz": dz,
                        "p_t_raw": float(stored["p_t_raw"]),
                        "p_t_holm": float(stored["p_t_holm"]),
                        "p_wilcoxon_holm": float(stored["p_wilcoxon_holm"]),
                        "t_excludes_zero": t_excludes,
                        "bootstrap_ci_lower": boot_lo,
                        "bootstrap_ci_upper": boot_hi,
                        "bootstrap_excludes_zero": boot_excludes,
                        "bootstrap_t_disagree_on_zero": bool(
                            t_excludes != boot_excludes
                        ),
                        "n_positive": people["n_positive"],
                        "n_negative": people["n_negative"],
                        "sign_stability_loo": people["sign_stability"],
                        "max_influencer": people["max_influencer"],
                        "max_influencer_value": people["max_influencer_value"],
                        "max_mean_shift": people["max_mean_shift"],
                        "compatible_abs_db": max(
                            abs(float(stored["ci_lower"])),
                            abs(float(stored["ci_upper"])),
                        ),
                        "inside_pm_0p3": bool(
                            float(stored["ci_lower"]) >= -0.3
                            and float(stored["ci_upper"]) <= 0.3
                        ),
                        "inside_pm_0p5": bool(
                            float(stored["ci_lower"]) >= -0.5
                            and float(stored["ci_upper"]) <= 0.5
                        ),
                        "inside_pm_1p0": bool(
                            float(stored["ci_lower"]) >= -1.0
                            and float(stored["ci_upper"]) <= 1.0
                        ),
                        "tost_p_0p3": tost_p(mean, se, n - 1, 0.3),
                        "tost_p_0p5": tost_p(mean, se, n - 1, 0.5),
                        "tost_p_1p0": tost_p(mean, se, n - 1, 1.0),
                        "tost_p_2p0": tost_p(mean, se, n - 1, 2.0),
                        "mde_db_holm80": mde_dz(n, alpha_holm) * sd,
                        "mde_db_raw80": mde_dz(n, alpha_raw) * sd,
                        "mde_dz_holm80": mde_dz(n, alpha_holm),
                        "observed_power_holm": observed_power(dz, n, alpha_holm),
                        "observed_power_raw": observed_power(dz, n, alpha_raw),
                        "n80_for_0p5db": n_for_power(sd, 0.5, alpha_holm),
                        "n80_for_1p0db": n_for_power(sd, 1.0, alpha_holm),
                        "recomputed_mean_match": check["mean_match"],
                        "recomputed_p_match": check["p_match"],
                    }
                )

    confirmatory = pd.DataFrame(confirmatory_rows)
    loo_all = pd.concat(loo_frames, ignore_index=True)

    expl = ad_tests[
        (ad_tests["contrast_tier"] == "primary")
        & (ad_tests["p_t_holm"] != "")
        & (ad_tests["p_t_holm"].astype(float) < 0.05)
        & (~ad_tests["feature"].isin(PRIMARY_FEATURES))
    ].copy()
    expl["feature_label"] = expl["feature"].map(FEATURE_SHORT)
    expl["contrast"] = expl["contrast_id"].map(LABELS)
    ica_changes = {
        (row["contrast_id"], row["feature"]): row
        for row in ica["ad_contrasts"]["corrected_significance_changes"]
    }
    expl_rows = []
    for row in expl.itertuples():
        change = ica_changes.get((row.contrast_id, row.feature), {})
        expl_rows.append(
            {
                "contrast": LABELS[row.contrast_id],
                "feature": FEATURE_SHORT.get(row.feature, row.feature),
                "tier": row.feature_tier,
                "mean_db": float(row.mean_difference),
                "ci_lower": float(row.ci_lower),
                "ci_upper": float(row.ci_upper),
                "cohen_dz": float(row.cohen_dz),
                "p_t_raw": float(row.p_t_raw),
                "p_t_holm": float(row.p_t_holm),
                "p_wilcoxon_holm": float(row.p_wilcoxon_holm),
                "ica_only": bool(change.get("ica_significant") and not change.get("no_ica_significant")),
                "no_ica_holm": change.get("no_ica_p_t_holm"),
                "paper_status": "exploratory ICA-only; do not abstract",
            }
        )
    exploratory = pd.DataFrame(expl_rows)

    dataset_a_holm_hits = int(
        (
            (condition_tests["contrast_tier"] == "primary")
            & (condition_tests["p_t_holm"] != "")
            & (condition_tests["p_t_holm"].astype(float) < 0.05)
        ).sum()
    )
    dataset_b_conf_hits = int(
        (
            (ad_tests["contrast_tier"] == "primary")
            & (ad_tests["feature"].isin(PRIMARY_FEATURES))
            & (ad_tests["p_t_holm"].astype(float) < 0.05)
        ).sum()
    )

    summary = {
        "n": 18,
        "recomputed_all_means_match": bool(confirmatory["recomputed_mean_match"].all()),
        "recomputed_all_p_match": bool(confirmatory["recomputed_p_match"].all()),
        "dataset_a_primary_holm_hits": 0
        if int(
            (
                (confirmatory["path"] == "A")
                & (confirmatory["p_t_holm"] < 0.05)
            ).sum()
        )
        == 0
        else int(
            (
                (confirmatory["path"] == "A")
                & (confirmatory["p_t_holm"] < 0.05)
            ).sum()
        ),
        "dataset_a_all_feature_primary_holm_hits": dataset_a_holm_hits,
        "dataset_b_confirmatory_holm_hits": dataset_b_conf_hits,
        "dataset_a_all_cis_inside_0p3db": bool(
            confirmatory.loc[confirmatory["path"] == "A", "inside_pm_0p3"].all()
        ),
        "dataset_b_any_ci_inside_1db": bool(
            confirmatory.loc[confirmatory["path"] == "B", "inside_pm_1p0"].any()
        ),
        "bootstrap_t_zero_disagreements": confirmatory.loc[
            confirmatory["bootstrap_t_disagree_on_zero"],
            ["path", "contrast", "feature", "ci_lower", "ci_upper", "bootstrap_ci_lower", "bootstrap_ci_upper"],
        ].to_dict(orient="records"),
        "exploratory_ica_only_holm_hits": expl_rows,
        "mde_dataset_a_theta_anyad_holm80": float(
            confirmatory[
                (confirmatory["path"] == "A")
                & (confirmatory["contrast_id"] == "any_ad_vs_no_ads")
                & (confirmatory["feature"] == "Fz theta")
            ]["mde_db_holm80"].iloc[0]
        ),
        "mde_dataset_b_explicit_early_theta_holm80": float(
            confirmatory[
                (confirmatory["path"] == "B")
                & (confirmatory["contrast_id"] == "block_early_vs_no_ad_early")
                & (confirmatory["feature"] == "Fz theta")
            ]["mde_db_holm80"].iloc[0]
        ),
        "tost_note": (
            "TOST bounds 0.3/0.5/1.0/2.0 dB are post-hoc illustrations, "
            "not a pre-registered equivalence margin."
        ),
        "stale_docs": [
            "analysis/eeg/analysis/README.md still says read-vs-write is unimplemented",
            "outputs/reports/initial_results_summary.md still says the same",
        ],
    }

    confirmatory.to_csv(OUT / "confirmatory_depth.csv", index=False)
    exploratory.to_csv(OUT / "exploratory_holm_hits.csv", index=False)
    loo_all.to_csv(OUT / "loo_people.csv", index=False)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
