"""Goal 5 combos — exploratory map (2,560 tests). Not Results.

Thesis entry is ``run_thesis_families.py``. Reduced blocks 0–7 are
Discussion-only. Association, not mediation.

Four families, the four rows of the goal-list table:

  beh_eeg    behaviour × EEG          lab n = 18
  beh_traj   behaviour × trajectory   n = 54
  traj_eeg   trajectory × EEG         lab n = 18
  threeway   partial Spearman, behaviour ~ EEG | trajectory and behaviour ~ trajectory | EEG, n = 18

Two grains per pairwise family:

  D    person-level planned D_i, same contrast on both sides, Spearman
  RM   condition-state, repeated-measures correlation with the person
       centred out (Bakdash & Marusich), 90 or 270 rows, df = N - k - 1

EEG: all 16 Dataset A k=37 features are swept; Fz theta and posterior
alpha are the headline pair. Trajectory: utterance source only.
Everything reads combo_threeway*.csv; nothing is re-joined here.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
WALTER = HERE.parent
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = HERE / "outputs"

BEH_PRIMARY = ("trust", "credibility", "manipulation", "notice")
BEH_ALL = BEH_PRIMARY + (
    "helpfulness", "convincingness", "relevance", "neutrality",
    "behaviour_pushing", "behaviour_manipulate", "notice_brands", "notice_sponsored",
    "duration_sec", "reply_latency_ms_median", "user_msg_len_median",
)
EEG_HEADLINE = ("eeg_fz_theta", "eeg_posterior_alpha")
EEG_ALL = (
    "eeg_fz_theta", "eeg_posterior_alpha", "eeg_theta", "eeg_alpha", "eeg_beta",
    "eeg_delta", "eeg_gamma", "eeg_faa", "eeg_rel_delta", "eeg_rel_theta",
    "eeg_rel_alpha", "eeg_rel_beta", "eeg_rel_gamma", "eeg_engagement",
    "eeg_pope", "eeg_kislov",
)
TRAJ_PRIMARY = ("traj_n_shift", "traj_shift_rate", "traj_diversity", "traj_entropy_nats", "traj_max_persistence")
TRAJ_ALL = TRAJ_PRIMARY + (
    "traj_entropy_normalised", "traj_mean_js_divergence", "traj_max_js_divergence",
    "traj_mean_total_variation", "traj_shifted_into_purchasable",
)


def d_family(dtab: pd.DataFrame, left: tuple, right: tuple, family: str, headline_right: tuple) -> list[dict]:
    rows = []
    for cid in sk.PLANNED:
        for a in left:
            for b in right:
                ca, cb = f"{a}__{cid}", f"{b}__{cid}"
                if ca not in dtab.columns or cb not in dtab.columns:
                    continue
                rec = sk.spearman(dtab[ca], dtab[cb])
                if "rho" not in rec:
                    continue
                rec.update({
                    "family": f"{family}|D|{cid}", "combo": family, "grain": "D",
                    "contrast": cid, "contrast_label": sk.CONTRAST_LABEL[cid],
                    "left": a, "right": b,
                    "headline": (a in BEH_PRIMARY or a in TRAJ_PRIMARY) and (b in headline_right),
                    "effect": rec["rho"], "effect_name": "Spearman rho",
                })
                rows.append(rec)
    return rows


def rm_family(state: pd.DataFrame, left: tuple, right: tuple, family: str, headline_right: tuple) -> list[dict]:
    rows = []
    for a in left:
        for b in right:
            if a not in state.columns or b not in state.columns:
                continue
            rec = sk.rmcorr(state, "experiment_id", a, b)
            if "rrm" not in rec:
                continue
            rec.update({
                "family": f"{family}|RM", "combo": family, "grain": "RM",
                "contrast": "state", "contrast_label": "person x condition rows, person centred",
                "left": a, "right": b,
                "headline": (a in BEH_PRIMARY or a in TRAJ_PRIMARY) and (b in headline_right),
                "effect": rec["rrm"], "effect_name": "r_rm",
            })
            rows.append(rec)
    return rows


def threeway_family(dlab: pd.DataFrame) -> list[dict]:
    rows = []
    for cid in sk.PLANNED:
        for beh in BEH_PRIMARY:
            for eeg in EEG_HEADLINE:
                for traj in TRAJ_PRIMARY:
                    cb, ce, ct = f"{beh}__{cid}", f"{eeg}__{cid}", f"{traj}__{cid}"
                    if not {cb, ce, ct} <= set(dlab.columns):
                        continue
                    for x, y, z, kind in ((cb, ce, ct, "beh~eeg|traj"), (cb, ct, ce, "beh~traj|eeg"), (ct, ce, cb, "traj~eeg|beh")):
                        rec = sk.partial_spearman(dlab, x, y, z)
                        if "rho_partial" not in rec:
                            continue
                        rec.update({
                            "family": f"threeway|{kind}|{cid}", "combo": "threeway", "grain": "D",
                            "contrast": cid, "contrast_label": sk.CONTRAST_LABEL[cid],
                            "kind": kind, "beh": beh, "eeg": eeg, "traj": traj,
                            "left": x, "right": y, "given": z, "headline": True,
                            "effect": rec["rho_partial"], "effect_name": "partial Spearman rho",
                        })
                        rows.append(rec)
    return rows


def heat_D(table: pd.DataFrame, combo: str, right_cols: tuple, path: Path, title: str) -> None:
    sub = table.loc[(table["combo"] == combo) & (table["grain"] == "D")]
    fig, axes = plt.subplots(1, 3, figsize=(4.4 * 3, 0.32 * sub["left"].nunique() + 2.2), sharey=True)
    for ax, cid in zip(axes, sk.PLANNED):
        blk = sub.loc[sub["contrast"] == cid]
        piv = blk.pivot_table(index="left", columns="right", values="effect").reindex(columns=[c for c in right_cols if c in blk["right"].unique()])
        pp = blk.pivot_table(index="left", columns="right", values="p_raw").reindex(index=piv.index, columns=piv.columns)
        im = ax.imshow(piv.to_numpy(dtype=float), cmap="coolwarm", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(piv.columns)), [c.replace("eeg_", "").replace("traj_", "") for c in piv.columns], rotation=60, ha="right", fontsize=7)
        ax.set_yticks(range(len(piv.index)), piv.index, fontsize=7)
        ax.set_title(sk.CONTRAST_LABEL[cid])
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                p = pp.iat[i, j]
                if pd.notna(p) and p < 0.05:
                    ax.text(j, i, "\u2022", ha="center", va="center", color="black", fontsize=9)
    fig.colorbar(im, ax=axes, fraction=0.02, label="Spearman rho on D_i")
    fig.suptitle(f"{title}   (\u2022 = raw p < .05; see hit tables for Holm / BH)")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    state = pd.read_csv(GOLD / "combo_threeway.csv")
    state_lab = pd.read_csv(GOLD / "combo_threeway_lab.csv")
    dall = pd.read_csv(GOLD / "combo_threeway_D.csv")
    dlab = pd.read_csv(GOLD / "combo_threeway_lab_D.csv")

    rows: list[dict] = []
    rows += d_family(dlab, BEH_ALL, EEG_ALL, "beh_eeg", EEG_HEADLINE)
    rows += rm_family(state_lab, BEH_ALL, EEG_ALL, "beh_eeg", EEG_HEADLINE)
    rows += d_family(dall, BEH_ALL, TRAJ_ALL, "beh_traj", TRAJ_PRIMARY)
    rows += rm_family(state, BEH_ALL, TRAJ_ALL, "beh_traj", TRAJ_PRIMARY)
    rows += d_family(dlab, TRAJ_ALL, EEG_ALL, "traj_eeg", EEG_HEADLINE)
    rows += rm_family(state_lab, TRAJ_ALL, EEG_ALL, "traj_eeg", EEG_HEADLINE)
    rows += threeway_family(dlab)

    table = pd.DataFrame(rows)
    table = table.loc[table["p_raw"].notna()].copy()
    table = sk.add_corrections(table, family_col="family", p_col="p_raw")
    lead = ["combo", "grain", "contrast", "contrast_label", "kind", "beh", "eeg", "traj", "left", "right", "given", "headline",
            "n", "n_obs", "n_persons", "dof", "effect", "effect_name", "p_raw", "p_holm_family", "p_bh_global",
            "sig_raw", "sig_holm_family", "sig_bh_global", "n_tests_in_family", "n_tests_global", "family"]
    lead = [c for c in lead if c in table.columns]
    table = table[lead].sort_values(["combo", "grain", "p_raw"])
    table.to_csv(OUT / "combos_all_tests.csv", index=False)

    summary = {"overall": sk.summarise(table), "by_combo": {}}
    for combo in ("beh_eeg", "beh_traj", "traj_eeg", "threeway"):
        sub = table.loc[table["combo"] == combo]
        folder = OUT / combo
        folder.mkdir(exist_ok=True)
        sub.to_csv(folder / "tests.csv", index=False)
        sub.loc[sub["headline"]].to_csv(folder / "tests_headline.csv", index=False)
        sub.loc[sub["sig_raw"]].sort_values("p_raw").to_csv(folder / "hits_raw.csv", index=False)
        sub.loc[sub["sig_holm_family"]].sort_values("p_raw").to_csv(folder / "hits_holm_family.csv", index=False)
        sub.loc[sub["sig_bh_global"]].sort_values("p_raw").to_csv(folder / "hits_bh_global.csv", index=False)
        summary["by_combo"][combo] = {
            **sk.summarise(sub),
            "headline_tests": int(sub["headline"].sum()),
            "headline_raw_hits": int((sub["headline"] & sub["sig_raw"]).sum()),
            "top_raw": sub.sort_values("p_raw").head(8)[
                [c for c in ("grain", "contrast_label", "kind", "left", "right", "given", "n", "n_persons", "effect", "p_raw", "p_holm_family", "p_bh_global") if c in sub.columns]
            ].round(4).to_dict(orient="records"),
        }

    heat_D(table, "beh_eeg", EEG_ALL, OUT / "beh_eeg" / "heat_D.png", "behaviour \u00d7 EEG, D grain, lab n=18")
    heat_D(table, "beh_traj", TRAJ_ALL, OUT / "beh_traj" / "heat_D.png", "behaviour \u00d7 trajectory, D grain, n=54")
    heat_D(table, "traj_eeg", EEG_ALL, OUT / "traj_eeg" / "heat_D.png", "trajectory \u00d7 EEG, D grain, lab n=18")

    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    s = run()
    print(json.dumps({"overall": s["overall"], "by_combo": {k: {kk: vv for kk, vv in v.items() if kk != "top_raw"} for k, v in s["by_combo"].items()}}, indent=2))
    print(f"Wrote {OUT}")
