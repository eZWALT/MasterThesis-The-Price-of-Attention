"""Descriptive / relational pass on Walter's behavioural Gold.

Not an item hunt. Planned composites stay frozen. The two manipulation
items and the two notice items are shown next to their means.

Person is the inferential unit. Condition-row correlations are not
tested as if n=270.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
GOLD = HERE / "outputs" / "gold"
OUT = HERE / "outputs" / "eda"

CONDITION_ORDER = (
    "no_ads",
    "inline_early",
    "inline_late",
    "block_early",
    "block_late",
)
CONDITION_LABELS = {
    "no_ads": "no ad",
    "inline_early": "implicit early",
    "inline_late": "implicit late",
    "block_early": "explicit early",
    "block_late": "explicit late",
}
PRIMARY = ("trust", "credibility", "manipulation", "notice")
ITEM_PAIR = (
    "behaviour_pushing",
    "behaviour_manipulate",
    "notice_brands",
    "notice_sponsored",
)
SECONDARY = ("helpfulness", "convincingness", "relevance", "neutrality")
PROCESS = (
    "duration_sec",
    "reply_latency_ms_median",
    "user_msg_len_median",
    "time_to_first_user_sec",
)
CONTRASTS = ("any_ad_vs_no_ads", "inline_vs_block", "early_vs_late")
CONTRAST_LABELS = {
    "any_ad_vs_no_ads": "any ad − no ad",
    "inline_vs_block": "implicit − explicit",
    "early_vs_late": "early − late",
}
BFI = ("bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o")


def load() -> dict[str, pd.DataFrame]:
    return {
        "id_map": pd.read_csv(GOLD / "id_map.csv"),
        "person": pd.read_csv(GOLD / "person_features.csv"),
        "condition": pd.read_csv(GOLD / "condition_features.csv"),
        "ads": pd.read_csv(GOLD / "advertisement_features.csv"),
        "contrast": pd.read_csv(GOLD / "contrast_scores.csv"),
        "combo_lab": pd.read_csv(GOLD / "combo_condition_lab.csv"),
        "contrast_lab": pd.read_csv(GOLD / "combo_contrast_lab.csv"),
    }


def condition_descriptives(condition: pd.DataFrame) -> pd.DataFrame:
    cols = [*PRIMARY, *ITEM_PAIR, *SECONDARY, *PROCESS]
    rows = []
    for cond in CONDITION_ORDER:
        block = condition.loc[condition["condition"] == cond]
        row = {
            "condition": cond,
            "label": CONDITION_LABELS[cond],
            "n": int(len(block)),
        }
        for col in cols:
            row[f"{col}_mean"] = float(block[col].mean())
            row[f"{col}_sd"] = float(block[col].std(ddof=1))
        rows.append(row)
    return pd.DataFrame(rows)


def interaction_cells(condition: pd.DataFrame) -> pd.DataFrame:
    ads = condition.loc[condition["presentation"] != "none"].copy()
    rows = []
    for (pres, timing), block in ads.groupby(["presentation", "timing"]):
        row = {"presentation": pres, "timing": timing, "n": int(len(block))}
        for col in (*PRIMARY, *ITEM_PAIR, *PROCESS):
            row[f"{col}_mean"] = float(block[col].mean())
            row[f"{col}_sd"] = float(block[col].std(ddof=1))
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["presentation", "timing"])


def arm_cells(condition: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (arm, cond), block in condition.groupby(["arm", "condition"]):
        row = {
            "arm": arm,
            "condition": cond,
            "label": CONDITION_LABELS[cond],
            "n": int(len(block)),
        }
        for col in PRIMARY:
            row[f"{col}_mean"] = float(block[col].mean())
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["arm", "condition"])


def person_means(condition: pd.DataFrame) -> pd.DataFrame:
    cols = [*PRIMARY, *ITEM_PAIR, *SECONDARY, *PROCESS]
    return (
        condition.groupby(
            ["experiment_id", "participant_id", "subject_id", "arm"], sort=False
        )[list(cols)]
        .mean()
        .reset_index()
    )


def spearman_matrix(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rho = pd.DataFrame(index=cols, columns=cols, dtype=float)
    pval = pd.DataFrame(index=cols, columns=cols, dtype=float)
    for a in cols:
        for b in cols:
            pair = frame[[a, b]].dropna()
            if len(pair) < 5:
                rho.loc[a, b] = np.nan
                pval.loc[a, b] = np.nan
                continue
            r, p = stats.spearmanr(pair[a].to_numpy(), pair[b].to_numpy())
            rho.loc[a, b] = float(np.asarray(r).reshape(-1)[0])
            pval.loc[a, b] = float(np.asarray(p).reshape(-1)[0])
    return rho, pval


def contrast_tests(contrast: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in (*PRIMARY, *ITEM_PAIR, *SECONDARY):
        raw_p = []
        block_rows = []
        for contrast_id in CONTRASTS:
            col = f"{outcome}__{contrast_id}"
            series = contrast[col].dropna().astype(float)
            n = int(len(series))
            mean = float(series.mean())
            sd = float(series.std(ddof=1))
            se = sd / np.sqrt(n)
            t_stat, p_t = stats.ttest_1samp(series, 0.0)
            w_stat, p_w = stats.wilcoxon(series, alternative="two-sided", zero_method="wilcox")
            dz = mean / sd if sd else np.nan
            rec = {
                "outcome": outcome,
                "contrast": contrast_id,
                "contrast_label": CONTRAST_LABELS[contrast_id],
                "n": n,
                "mean": mean,
                "sd": sd,
                "ci95_lo": mean - 1.96 * se,
                "ci95_hi": mean + 1.96 * se,
                "t": float(t_stat),
                "p_t": float(p_t),
                "wilcoxon_w": float(w_stat),
                "p_wilcoxon": float(p_w),
                "dz": float(dz),
            }
            block_rows.append(rec)
            raw_p.append(float(p_t))
        reject, p_holm, _, _ = multipletests(raw_p, method="holm")
        for rec, adj, hit in zip(block_rows, p_holm, reject):
            rec["p_holm"] = float(adj)
            rec["holm_sig"] = bool(hit)
            rows.append(rec)
    return pd.DataFrame(rows)


def recall_descriptives(ads: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, block in (
        ("condition", ads.groupby("condition")),
        ("presentation", ads.groupby("presentation")),
        ("timing", ads.groupby("timing")),
    ):
        for name, sub in block:
            rows.append(
                {
                    "split": key,
                    "level": name,
                    "n": int(len(sub)),
                    "recall_memory_mean": float(sub["recall_memory"].mean()),
                    "recall_memory_sd": float(sub["recall_memory"].std(ddof=1)),
                    "recall_trust_shift_mean": float(sub["recall_trust_shift"].mean()),
                    "recall_trust_shift_sd": float(sub["recall_trust_shift"].std(ddof=1)),
                }
            )
    return pd.DataFrame(rows)


def combo_associations(contrast_lab: pd.DataFrame) -> pd.DataFrame:
    rows = []
    eeg_cols = [
        c
        for c in contrast_lab.columns
        if c.startswith("eeg_") and "__" in c
    ]
    beh_cols = [
        f"{outcome}__{contrast}"
        for outcome in PRIMARY
        for contrast in CONTRASTS
    ]
    for beh in beh_cols:
        for eeg in eeg_cols:
            pair = contrast_lab[[beh, eeg]].dropna()
            if len(pair) < 8:
                continue
            r, p = stats.spearmanr(pair[beh], pair[eeg])
            rows.append(
                {
                    "behaviour": beh,
                    "eeg": eeg,
                    "n": int(len(pair)),
                    "spearman_rho": float(r),
                    "p": float(p),
                }
            )
    return pd.DataFrame(rows)


def _boxes(condition: pd.DataFrame, cols: tuple[str, ...], title: str, path: Path) -> None:
    fig, axes = plt.subplots(1, len(cols), figsize=(3.2 * len(cols), 4.2), sharex=True)
    if len(cols) == 1:
        axes = [axes]
    data = [condition.loc[condition["condition"] == c] for c in CONDITION_ORDER]
    labels = [CONDITION_LABELS[c] for c in CONDITION_ORDER]
    for ax, col in zip(axes, cols):
        ax.boxplot([d[col].to_numpy() for d in data], tick_labels=labels, showfliers=False)
        ax.set_title(col.replace("_", " "))
        ax.tick_params(axis="x", rotation=45)
        ax.set_ylim(1, 7)
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _heatmap(matrix: pd.DataFrame, title: str, path: Path, vmin=-1, vmax=1) -> None:
    fig, ax = plt.subplots(figsize=(0.55 * len(matrix.columns) + 2, 0.55 * len(matrix) + 2))
    im = ax.imshow(matrix.to_numpy(dtype=float), cmap="coolwarm", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(matrix.columns)), matrix.columns, rotation=60, ha="right")
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    fig.colorbar(im, ax=ax, fraction=0.046)
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _forest(tests: pd.DataFrame, path: Path) -> None:
    prim = tests.loc[tests["outcome"].isin(PRIMARY)].copy()
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    axes = axes.ravel()
    for ax, outcome in zip(axes, PRIMARY):
        block = prim.loc[prim["outcome"] == outcome]
        y = np.arange(len(block))
        ax.axvline(0, color="0.5", lw=1)
        ax.errorbar(
            block["mean"],
            y,
            xerr=[block["mean"] - block["ci95_lo"], block["ci95_hi"] - block["mean"]],
            fmt="o",
            color="black",
        )
        ax.set_yticks(y, block["contrast_label"])
        ax.set_title(outcome)
        ax.invert_yaxis()
    fig.suptitle("Planned D (mean, 95% CI). Holm is on the paired t, within outcome.")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def run() -> dict[str, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    data = load()
    condition = data["condition"]
    person = data["person"]
    ads = data["ads"]
    contrast = data["contrast"]
    contrast_lab = data["contrast_lab"]

    desc = condition_descriptives(condition)
    inter = interaction_cells(condition)
    arms = arm_cells(condition)
    means = person_means(condition)
    means = means.merge(
        person[["experiment_id", *BFI, "demo_sex", "demo_familiarity", "demo_frequency"]],
        on="experiment_id",
        how="left",
    )
    tests = contrast_tests(contrast)
    recall = recall_descriptives(ads)
    combos = combo_associations(contrast_lab)

    outcome_cols = [*PRIMARY, *ITEM_PAIR, *SECONDARY]
    rho_out, p_out = spearman_matrix(means, outcome_cols)
    rho_proc, p_proc = spearman_matrix(means, [*PRIMARY, *PROCESS])
    rho_bfi, p_bfi = spearman_matrix(means, [*PRIMARY, *BFI])

    d_any = contrast[
        ["experiment_id", *[f"{o}__any_ad_vs_no_ads" for o in PRIMARY]]
    ].merge(person[["experiment_id", *BFI]], on="experiment_id")
    d_any = d_any.rename(columns={f"{o}__any_ad_vs_no_ads": f"D_{o}" for o in PRIMARY})
    rho_dbfi, p_dbfi = spearman_matrix(d_any, [f"D_{o}" for o in PRIMARY] + list(BFI))

    desc.to_csv(OUT / "condition_descriptives.csv", index=False)
    inter.to_csv(OUT / "format_timing_cells.csv", index=False)
    arms.to_csv(OUT / "arm_condition_means.csv", index=False)
    means.to_csv(OUT / "person_means.csv", index=False)
    tests.to_csv(OUT / "planned_contrasts.csv", index=False)
    recall.to_csv(OUT / "recall_descriptives.csv", index=False)
    combos.to_csv(OUT / "combo_spearman_lab.csv", index=False)
    rho_out.to_csv(OUT / "spearman_outcomes.csv")
    p_out.to_csv(OUT / "spearman_outcomes_p.csv")
    rho_proc.to_csv(OUT / "spearman_process.csv")
    p_proc.to_csv(OUT / "spearman_process_p.csv")
    rho_bfi.to_csv(OUT / "spearman_bfi.csv")
    p_bfi.to_csv(OUT / "spearman_bfi_p.csv")
    rho_dbfi.to_csv(OUT / "spearman_D_any_ad_bfi.csv")
    p_dbfi.to_csv(OUT / "spearman_D_any_ad_bfi_p.csv")

    _boxes(condition, PRIMARY, "Primary composites by condition (N=54)", OUT / "box_primary.png")
    _boxes(
        condition,
        ITEM_PAIR,
        "Item pairs kept beside the composites",
        OUT / "box_items.png",
    )
    _heatmap(rho_out, "Spearman among person-mean outcomes (n=54)", OUT / "heatmap_outcomes.png")
    _heatmap(rho_proc, "Spearman: outcomes × process (person means)", OUT / "heatmap_process.png")
    _heatmap(rho_bfi, "Spearman: outcomes × BFI (person means)", OUT / "heatmap_bfi.png")
    _forest(tests, OUT / "forest_planned_D.png")

    holm_hits = tests.loc[tests["holm_sig"] & tests["outcome"].isin(PRIMARY)]
    summary = {
        "n_people": 54,
        "holm_hits_primary": holm_hits[["outcome", "contrast", "mean", "p_t", "p_holm"]].to_dict(
            orient="records"
        ),
    }
    (OUT / "eda_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"out": OUT, "gold": GOLD}


if __name__ == "__main__":
    paths = run()
    print(f"Gold: {paths['gold']}")
    print(f"EDA:  {paths['out']}")
