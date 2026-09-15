"""Exploratory Holm-surviving EEG cells (feature_tier != primary).

Reads only frozen confirmatory contrast tables:

    analysis/eeg/statistics/outputs/eeg_condition_contrasts.csv
    analysis/eeg/statistics/outputs/eeg_ad_response_contrasts.csv

Writes:

    analysis/eeg/analysis/outputs/tables/exploratory_holm_cells.csv
    analysis/eeg/analysis/outputs/tables/exploratory_holm_cells.tex

    python analysis/eeg/analysis/make_exploratory_cells_table.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
STATS = ROOT / "analysis" / "eeg" / "statistics" / "outputs"
OUT = HERE / "outputs" / "tables"

EXPECTED_N = 7

DATASET_LABEL = {
    "A": "Condition aggregation",
    "B": "Onset-locked",
}
CONTRAST_TEX = {
    "early_vs_late": r"early \(-\) late",
    "block_early_vs_no_ad_early": r"explicit early \(-\) \(a^{\emptyset}\)",
    "inline_late_vs_no_ad_late": r"implicit late \(-\) \(a^{\emptyset}\)",
    "block_late_vs_no_ad_late": r"explicit late \(-\) \(a^{\emptyset}\)",
    "inline_early_vs_no_ad_early": r"implicit early \(-\) \(a^{\emptyset}\)",
}
CONTRAST_CSV = {
    "early_vs_late": "early - late",
    "block_early_vs_no_ad_early": "explicit early - a_empty",
    "inline_late_vs_no_ad_late": "implicit late - a_empty",
    "block_late_vs_no_ad_late": "explicit late - a_empty",
    "inline_early_vs_no_ad_early": "implicit early - a_empty",
}
MEASURE_TEX = {
    "theta_power_db_uv2": r"global \(\theta\) (dB)",
    "delta_power_db_uv2": r"global \(\delta\) (dB)",
    "delta_relative_power": r"relative \(\delta\)",
    "theta_relative_power": r"relative \(\theta\)",
    "alpha_relative_power": r"relative \(\alpha\)",
    "beta_relative_power": r"relative \(\beta\)",
    "gamma_relative_power": r"relative \(\gamma\)",
}
MEASURE_CSV = {
    "theta_power_db_uv2": "global theta (dB)",
    "delta_power_db_uv2": "global delta (dB)",
    "delta_relative_power": "relative delta",
    "theta_relative_power": "relative theta",
    "alpha_relative_power": "relative alpha",
    "beta_relative_power": "relative beta",
    "gamma_relative_power": "relative gamma",
}


def tex_num(x: float, digits: int) -> str:
    return rf"\({x:.{digits}f}\)"


def tex_ci(lo: float, hi: float, digits: int) -> str:
    return rf"\([{lo:.{digits}f},\,{hi:.{digits}f}]\)"


def tex_p(p: float) -> str:
    if p < 0.001:
        return r"\(<.001\)"
    return rf"\({p:.3f}\)"


def is_relative(feature: str) -> bool:
    return feature.endswith("_relative_power")


def digits_for(feature: str) -> int:
    return 3 if is_relative(feature) else 2


def select_hits(frame: pd.DataFrame, dataset: str) -> pd.DataFrame:
    out = frame.copy()
    out["p_t_holm"] = pd.to_numeric(out["p_t_holm"], errors="coerce")
    out["p_t_raw"] = pd.to_numeric(out["p_t_raw"], errors="coerce")
    hit = out[(out["p_t_holm"] < 0.05) & (out["feature_tier"] != "primary")].copy()
    hit["dataset"] = dataset
    hit["dataset_label"] = DATASET_LABEL[dataset]
    return hit


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a = pd.read_csv(STATS / "eeg_condition_contrasts.csv")
    b = pd.read_csv(STATS / "eeg_ad_response_contrasts.csv")
    hits = pd.concat([select_hits(a, "A"), select_hits(b, "B")], ignore_index=True)
    n = int(len(hits))
    if n != EXPECTED_N:
        print(
            f"WARNING: expected {EXPECTED_N} exploratory Holm cells "
            f"(1 from A, 6 from B); found {n} "
            f"(A={(hits['dataset']=='A').sum()}, B={(hits['dataset']=='B').sum()})"
        )
    else:
        print(f"exploratory Holm cells: {n} (A=1, B=6)")

    hits["dataset_order"] = hits["dataset"].map({"A": 0, "B": 1})
    hits = hits.sort_values(
        ["dataset_order", "p_t_holm"], kind="mergesort"
    ).reset_index(drop=True)
    hits["contrast"] = hits["contrast_id"].map(CONTRAST_CSV).fillna(hits["contrast_id"])
    hits["contrast_tex"] = hits["contrast_id"].map(CONTRAST_TEX).fillna(hits["contrast_id"])
    hits["measure"] = hits["feature"].map(MEASURE_CSV).fillna(hits["feature"])
    hits["measure_tex"] = hits["feature"].map(MEASURE_TEX).fillna(hits["feature"])

    csv_cols = [
        "dataset",
        "dataset_label",
        "contrast_id",
        "contrast",
        "feature",
        "measure",
        "feature_tier",
        "n_participants",
        "mean_difference",
        "ci_lower",
        "ci_upper",
        "cohen_dz",
        "p_t_raw",
        "p_t_holm",
    ]
    hits[csv_cols].to_csv(OUT / "exploratory_holm_cells.csv", index=False)

    lines = [
        r"\begin{tabular}{@{}l l l r r r r r@{}}",
        r"\toprule",
        r"Dataset & Contrast & Measure & \(M\) & 95\% CI & \(d_z\) & raw \(p\) & Holm \(p\) \\",
        r"\midrule",
    ]
    last_dataset = None
    for rec in hits.itertuples(index=False):
        if last_dataset is not None and rec.dataset != last_dataset:
            lines.append(r"\midrule")
        last_dataset = rec.dataset
        d = digits_for(rec.feature)
        lines.append(
            f"{rec.dataset_label} & {rec.contrast_tex} & {rec.measure_tex} & "
            f"{tex_num(rec.mean_difference, d)} & "
            f"{tex_ci(rec.ci_lower, rec.ci_upper, d)} & "
            f"{tex_num(rec.cohen_dz, 2)} & "
            f"{tex_p(rec.p_t_raw)} & {tex_p(rec.p_t_holm)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "exploratory_holm_cells.tex").write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT / 'exploratory_holm_cells.csv'}")
    print(f"wrote {OUT / 'exploratory_holm_cells.tex'}")


if __name__ == "__main__":
    main()
