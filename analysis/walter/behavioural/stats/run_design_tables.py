"""Design-balance and by-arm headline cells from Walter Gold.

Reads only frozen Gold:

    outputs/gold/condition_features.csv

Writes under outputs/design/:

    task_by_condition.csv / .tex
    session_by_condition.csv / .tex
    design_summary.json
    arm_headline_cells.csv / .tex

    python analysis/walter/behavioural/stats/run_design_tables.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
BEH = HERE.parent
GOLD = BEH / "outputs" / "gold"
OUT = BEH / "outputs" / "design"

AD_CONDITIONS = ("inline_early", "inline_late", "block_early", "block_late")
NO_AD = "no_ads"
COND_ORDER = AD_CONDITIONS + (NO_AD,)
COND_TEX = (
    r"\(a^{\mathrm{imp}}_{2}\)",
    r"\(a^{\mathrm{imp}}_{4}\)",
    r"\(a^{\mathrm{exp}}_{2}\)",
    r"\(a^{\mathrm{exp}}_{4}\)",
    r"\(a^{\emptyset}\)",
    "Total",
)

TASK_ORDER = (
    "swt_laptop_budget",
    "swt_fitness_restart",
    "swt_gardening_birthday_gift",
    "swt_pet_decision_and_setup",
    "swt_study_environment",
)
TASK_LABEL = {
    "swt_laptop_budget": "Laptop on a budget",
    "swt_fitness_restart": "Fitness restart",
    "swt_gardening_birthday_gift": "Gardening gift",
    "swt_pet_decision_and_setup": "Pet decision",
    "swt_study_environment": "Study environment",
}

OUTCOMES = ("manipulation", "notice", "trust", "credibility")
OUTCOME_LABEL = {
    "manipulation": "Manipulation",
    "notice": "Notice",
    "trust": "Trust",
    "credibility": "Credibility",
}
ARMS = ("lab", "crowd", "pooled")

POOLED_CHECK = {"manipulation": 1.27, "notice": 2.07}
POOLED_CHECK_TOL = 0.02


def tex_num(x: float, digits: int) -> str:
    return rf"\({x:.{digits}f}\)"


def tex_ci(lo: float, hi: float, digits: int = 2) -> str:
    return rf"\([{lo:.{digits}f},\,{hi:.{digits}f}]\)"


def tex_p(p: float) -> str:
    if p < 0.001:
        return r"\(<.001\)"
    return rf"\({p:.3f}\)"


def count_table(frame: pd.DataFrame, row: str, row_order: list[str]) -> pd.DataFrame:
    tab = pd.crosstab(frame[row], frame["condition"])
    missing = [c for c in COND_ORDER if c not in tab.columns]
    extra = [c for c in tab.columns if c not in COND_ORDER]
    if missing or extra:
        raise SystemExit(f"unexpected condition values: missing={missing} extra={extra}")
    tab = tab.reindex(index=row_order, columns=list(COND_ORDER), fill_value=0)
    tab["Total"] = tab.sum(axis=1)
    total = tab.sum(axis=0).to_frame().T
    total.index = pd.Index(["Total"])
    return pd.concat([tab, total])


def chi_square(tab: pd.DataFrame) -> dict:
    observed = tab.loc[tab.index != "Total", list(COND_ORDER)].to_numpy(dtype=float)
    chi2, p, dof, _ = stats.chi2_contingency(observed, correction=False)
    return {"chi2": float(chi2), "df": int(dof), "p": float(p)}


def write_count_csv(tab: pd.DataFrame, path: Path, row_name: str, row_id_name: str, id_of) -> None:
    rows = []
    for idx, rec in tab.iterrows():
        if idx == "Total":
            rows.append(
                {
                    row_name: "Total",
                    row_id_name: "",
                    **{c: int(rec[c]) for c in COND_ORDER},
                    "Total": int(rec["Total"]),
                }
            )
            continue
        rows.append(
            {
                row_name: id_of(idx),
                row_id_name: idx,
                **{c: int(rec[c]) for c in COND_ORDER},
                "Total": int(rec["Total"]),
            }
        )
    pd.DataFrame(rows).to_csv(path, index=False)


def write_count_tex(tab: pd.DataFrame, path: Path, stub: str, label_of) -> None:
    lines = [
        r"\begin{tabular}{@{}l r r r r r r@{}}",
        r"\toprule",
        stub + " & " + " & ".join(COND_TEX) + r" \\",
        r"\midrule",
    ]
    for idx, rec in tab.iterrows():
        if idx == "Total":
            lines.append(r"\midrule")
            name = "Total"
        else:
            name = label_of(idx)
        cells = " & ".join(str(int(rec[c])) for c in list(COND_ORDER) + ["Total"])
        lines.append(f"{name} & {cells} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n")


def person_D(condition: pd.DataFrame, outcome: str) -> pd.DataFrame:
    wide = condition.pivot_table(
        index="experiment_id", columns="condition", values=outcome, aggfunc="first"
    )
    wide = wide.reindex(columns=list(COND_ORDER))
    if wide.isna().any().any():
        raise SystemExit(f"missing {outcome} cells in the person × condition table")
    arm = condition.groupby("experiment_id")["arm"].first()
    out = pd.DataFrame(
        {
            "D": wide[list(AD_CONDITIONS)].mean(axis=1) - wide[NO_AD],
            "arm": arm.reindex(wide.index),
        }
    )
    return out


def paired_t_summary(values: np.ndarray) -> dict:
    s = np.asarray(values, dtype=float)
    n = int(s.size)
    mean = float(s.mean())
    sd = float(s.std(ddof=1))
    se = sd / np.sqrt(n)
    t_stat, p = stats.ttest_1samp(s, 0.0)
    t_crit = float(stats.t.ppf(0.975, n - 1))
    return {
        "n": n,
        "mean_D": mean,
        "ci95_lo": mean - t_crit * se,
        "ci95_hi": mean + t_crit * se,
        "cohen_dz": mean / sd if sd > 0 else float("nan"),
        "t_statistic": float(t_stat),
        "df": n - 1,
        "p_raw": float(p),
    }


def welch_df(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = a.size, b.size
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    num = (va / na + vb / nb) ** 2
    den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
    return float(num / den)


def write_arm_tex(rows: list[dict], path: Path) -> None:
    lines = [
        r"\begin{tabular}{@{}l l r r r r r@{}}",
        r"\toprule",
        r"Outcome & Arm & \(n\) & \(D\) & 95\% CI & \(d_z\) & raw \(p\) \\",
        r"\midrule",
    ]
    last_outcome = None
    for rec in rows:
        if last_outcome is not None and rec["outcome"] != last_outcome:
            lines.append(r"\midrule")
        name = OUTCOME_LABEL[rec["outcome"]] if rec["outcome"] != last_outcome else ""
        last_outcome = rec["outcome"]
        lines.append(
            f"{name} & {rec['arm']} & {rec['n']} & "
            f"{tex_num(rec['mean_D'], 2)} & {tex_ci(rec['ci95_lo'], rec['ci95_hi'], 2)} & "
            f"{tex_num(rec['cohen_dz'], 2)} & {tex_p(rec['p_raw'])} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    condition = pd.read_csv(GOLD / "condition_features.csv")
    observed = set(condition["condition"].unique())
    if observed != set(COND_ORDER):
        raise SystemExit(f"unexpected condition values: {sorted(observed)}")
    tasks = list(condition["task_id"].unique())
    unknown = set(tasks) - set(TASK_ORDER)
    if unknown:
        raise SystemExit(f"unmapped task_id values: {sorted(unknown)}")

    task_tab = count_table(condition, "task_id", list(TASK_ORDER))
    session_order = [0, 1, 2, 3, 4]
    session_tab = count_table(condition, "session_position", session_order)

    write_count_csv(
        task_tab,
        OUT / "task_by_condition.csv",
        "task",
        "task_id",
        TASK_LABEL.__getitem__,
    )
    write_count_tex(
        task_tab,
        OUT / "task_by_condition.tex",
        "Task",
        TASK_LABEL.__getitem__,
    )
    write_count_csv(
        session_tab,
        OUT / "session_by_condition.csv",
        "session",
        "session_position",
        lambda pos: str(int(pos) + 1),
    )
    write_count_tex(
        session_tab,
        OUT / "session_by_condition.tex",
        "Session",
        lambda pos: str(int(pos) + 1),
    )
    summary = {
        "task_by_condition": chi_square(task_tab),
        "session_by_condition": chi_square(session_tab),
    }
    (OUT / "design_summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    person_rows: list[dict] = []
    welch_rows: list[dict] = []
    pooled_means: dict[str, float] = {}
    for outcome in OUTCOMES:
        d = person_D(condition, outcome)
        by_arm = {
            "lab": d.loc[d["arm"] == "lab", "D"].to_numpy(dtype=float),
            "crowd": d.loc[d["arm"] == "crowd", "D"].to_numpy(dtype=float),
            "pooled": d["D"].to_numpy(dtype=float),
        }
        for arm in ARMS:
            rec = paired_t_summary(by_arm[arm])
            rec.update({"block": "person_contrast", "outcome": outcome, "arm": arm})
            person_rows.append(rec)
        pooled_means[outcome] = float(by_arm["pooled"].mean())
        lab, crowd = by_arm["lab"], by_arm["crowd"]
        welch = stats.ttest_ind(crowd, lab, equal_var=False)
        welch_rows.append(
            {
                "block": "welch_between_arms",
                "outcome": outcome,
                "arm": "crowd_minus_lab",
                "n": "",
                "mean_D": float(crowd.mean() - lab.mean()),
                "ci95_lo": "",
                "ci95_hi": "",
                "cohen_dz": "",
                "t_statistic": float(welch.statistic),
                "df": welch_df(crowd, lab),
                "p_raw": float(welch.pvalue),
                "n_lab": int(lab.size),
                "n_crowd": int(crowd.size),
            }
        )

    mismatches = {
        name: pooled_means[name]
        for name, expected in POOLED_CHECK.items()
        if abs(pooled_means[name] - expected) > POOLED_CHECK_TOL
    }
    print(
        "pooled D: "
        + ", ".join(f"{k}={v:+.4f}" for k, v in pooled_means.items())
    )
    if mismatches:
        raise SystemExit(
            "pooled D mismatch (expected manipulation≈+1.27, notice≈+2.07): "
            + ", ".join(f"{k}={v:+.4f}" for k, v in mismatches.items())
        )

    for rec in person_rows:
        rec["n_lab"] = ""
        rec["n_crowd"] = ""
    cols = [
        "block",
        "outcome",
        "arm",
        "n",
        "mean_D",
        "ci95_lo",
        "ci95_hi",
        "cohen_dz",
        "t_statistic",
        "df",
        "p_raw",
        "n_lab",
        "n_crowd",
    ]
    pd.DataFrame(person_rows + welch_rows)[cols].to_csv(OUT / "arm_headline_cells.csv", index=False)
    write_arm_tex(person_rows, OUT / "arm_headline_cells.tex")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
