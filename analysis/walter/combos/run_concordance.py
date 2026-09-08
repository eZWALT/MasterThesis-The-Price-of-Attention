"""Block 6. Do the three modalities order the five conditions the same
way? Descriptive; no test is promoted from this figure.

For each headline variable the five condition means are computed on
within-person-centred scores (each person's mean over the five chats
removed) divided by the pooled within-person SD, so behaviour (n=54),
trajectory (n=54) and EEG (n=18, k=37 condition aggregation) share a
unit. 95% intervals are t-based on the person-centred values.

Concordance = Kendall tau between two variables' orderings of the five
conditions (10 condition pairs; tau is coarse at k=5 and is reported
as a description, not a test).

Writes outputs/concordance/.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st

import combokit as ck
from combokit import sk

OUT = ck.OUT / "concordance"
VARS = {
    "beh": ["trust", "credibility", "manipulation", "notice"],
    "traj": ["traj_n_shift", "traj_entropy_nats", "traj_mean_js_divergence", "traj_shifted_into_purchasable"],
    "eeg": ["eeg_fz_theta", "eeg_posterior_alpha", "eeg_theta", "eeg_beta"],
}
COLORS = ["k", "tab:blue", "tab:red", "tab:green"]


def profiles(C: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    rows = []
    for v in cols:
        w = sk.wide(C, v)
        wc = w.sub(w.mean(axis=1), axis=0)
        sd = float(wc.stack().std(ddof=1))
        z = wc / sd if sd > 0 else wc
        for cond in sk.CONDITIONS:
            s = z[cond]
            rows.append({"variable": v, "condition": cond, "n": len(s), "mean": float(s.mean()),
                         "ci": float(st.t.ppf(0.975, len(s) - 1) * s.std(ddof=1) / np.sqrt(len(s)))})
    return pd.DataFrame(rows)


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    C = ck.load_conditions()
    P = pd.concat([profiles(C, VARS["beh"]), profiles(C, VARS["traj"]), profiles(C[C.arm == "lab"], VARS["eeg"])], ignore_index=True)
    P.to_csv(OUT / "condition_profiles.csv", index=False)
    wide = P.pivot(index="variable", columns="condition", values="mean")[list(sk.CONDITIONS)]
    allv = VARS["beh"] + VARS["traj"] + VARS["eeg"]
    wide = wide.loc[allv]
    tau = pd.DataFrame(index=allv, columns=allv, dtype=float)
    for a in allv:
        for b in allv:
            tau.loc[a, b] = st.kendalltau(wide.loc[a], wide.loc[b])[0]
    tau.to_csv(OUT / "kendall_tau_profiles.csv")
    figure(P, tau)
    # cross-modal blocks of tau, summarised
    def block(m1, m2):
        vals = tau.loc[VARS[m1], VARS[m2]].to_numpy().ravel()
        return {"mean_tau": float(np.mean(vals)), "mean_abs_tau": float(np.mean(np.abs(vals))), "n_pairs": int(len(vals))}
    summary = {"blocks": {"beh_traj": block("beh", "traj"), "beh_eeg": block("beh", "eeg"), "traj_eeg": block("traj", "eeg")},
               "profiles": wide.round(3).to_dict(orient="index")}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def figure(P: pd.DataFrame, tau: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    x = np.arange(5)
    for ax, (mod, cols) in zip(axes, VARS.items()):
        for v, c in zip(cols, COLORS):
            s = P[P.variable == v].set_index("condition").loc[list(sk.CONDITIONS)]
            ax.errorbar(x + (cols.index(v) - 1.5) * 0.08, s["mean"], yerr=s["ci"], fmt="o-", color=c, ms=4, lw=1, capsize=2, label=v.replace("traj_", "").replace("eeg_", ""))
        ax.axhline(0, color="k", lw=0.6); ax.set_xticks(x, [sk.LABEL[c] for c in sk.CONDITIONS], rotation=20, fontsize=8)
        n = int(P[P.variable == cols[0]].n.iloc[0])
        ax.set_title(f"{ck.PRETTY[mod]} (n = {n})", fontsize=10); ax.legend(fontsize=7)
    axes[0].set_ylabel("within-person centred, pooled within-person SD units")
    fig.suptitle("Block 6: condition profiles per modality, within-person centred (95% CI); descriptive, no test is read from this figure", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "condition_profiles.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(tau.to_numpy(dtype=float), cmap="RdBu_r", vmin=-1, vmax=1)
    labels = [v.replace("traj_", "t:").replace("eeg_", "e:") for v in tau.index]
    ax.set_xticks(range(len(labels)), labels, rotation=90, fontsize=8); ax.set_yticks(range(len(labels)), labels, fontsize=8)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{tau.iat[i, j]:+.1f}", ha="center", va="center", fontsize=6)
    for k in (4, 8):
        ax.axhline(k - 0.5, color="k", lw=1); ax.axvline(k - 0.5, color="k", lw=1)
    ax.set_title("Kendall tau between condition orderings (5 conditions; descriptive)", fontsize=10)
    fig.colorbar(im, ax=ax, shrink=0.7); fig.tight_layout(); fig.savefig(OUT / "kendall_tau_profiles.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    s = run()
    print(json.dumps(s["blocks"], indent=1))
    print(pd.DataFrame(s["profiles"]).T.to_string())
    print(f"Wrote {OUT}")
