"""Block 1. Nine headline cross-modal tests instead of 2,560.

For each planned contrast, reduce each modality's person-level D_i
block to one score (PC1 of the z-scored D's), then correlate the three
scores pairwise:

    behaviour PC1 x trajectory PC1   n = 54
    behaviour PC1 x EEG PC1          n = 18 (lab)
    trajectory PC1 x EEG PC1         n = 18 (lab)

3 contrasts x 3 pairs = 9 tests, Holm within the nine. This is the
family a reviewer would accept as "the cross-modal question", and it
is the one the 2,560-cell map cannot answer because Holm-2560 needs
|rho| > .83 at n = 18.

Secondary (planned-primary) family: behaviour PC1 and trajectory PC1
against the two a priori EEG primaries (Fz theta, posterior alpha),
12 tests, Holm within twelve.

Process family: PC1 of the three process D's (duration, reply
latency, message length) against each of the other three scores,
9 tests, Holm within nine. Declared because the largest raw cells of
the 2,560-cell map were process x engagement at the format contrast.

Sensitivity: a unit-weighted z-mean composite in place of PC1 (PC1
from 18 rows and 16 columns is not stable), behaviour x trajectory on
the laboratory arm alone, partial Spearman given arm, and the EEG side
rebuilt from the whole-window Gold medians (~95 tiles) instead of the
k=37 condition aggregation (21 tests; block 0 shows k=37 costs
reliability on Fz theta).

Writes outputs/headline/.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import combokit as ck
from combokit import sk

OUT = ck.OUT / "headline"
ORIENT = {"beh": "manipulation", "traj": "traj_n_shift", "eeg": "eeg_theta", "proc": "duration_sec"}
BLOCKS = {"beh": ck.BEH_SURVEY, "traj": ck.TRAJ, "eeg": ck.EEG, "proc": ck.BEH_PROCESS}


def scores_for(D: pd.DataFrame, contrast: str) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    """PC1 and z-mean per modality for one contrast. Returns a frame
    indexed like D with columns pc1_<mod>, zmean_<mod>, plus loadings
    and variance-explained records."""
    out = pd.DataFrame(index=D.index)
    load_rows, var_rows = [], []
    for mod, block in BLOCKS.items():
        cols = ck.dcols(block, contrast)
        sub = D[cols].copy()
        sub.columns = block
        sc, load, ve = ck.pc1(sub, orient_on=ORIENT[mod])
        out[f"pc1_{mod}"] = sc
        out[f"zmean_{mod}"] = ck.zmean(sub, signs=np.sign(load))
        var_rows.append({"contrast": contrast, "modality": mod, "n": int(sub.dropna().shape[0]), "k_vars": len(block),
                         "pc1_var_explained": ve, "pc1_zmean_spearman": float(pd.concat([sc, out[f"zmean_{mod}"]], axis=1).dropna().corr(method="spearman").iloc[0, 1]),
                         **ck.pc1_loo_stability(sub, orient_on=ORIENT[mod])})
        for v, l in load.items():
            load_rows.append({"contrast": contrast, "modality": mod, "variable": v, "loading": float(l)})
    return out, load_rows, var_rows


def wholewindow_eeg_D(D: pd.DataFrame, cid: str) -> pd.DataFrame:
    """EEG D_i from the whole-window Gold medians (~95 tiles per
    condition) instead of the k=37 condition aggregation; block 0 shows
    the single-channel Fz theta D is more reliable there (.35-.61 vs
    ~0). Sensitivity only: Gold is not overwritten and the confirmatory
    EEG cell stays k=37."""
    G = pd.read_csv(ck.EEG_GOLD / "condition_features.csv")
    G = G[(G.primary_analysis_eligible == "yes") & (G.condition.isin(sk.CONDITIONS))]
    out = pd.DataFrame(index=D.index)
    for short, long in ck.EEG_LONG.items():
        w = G.pivot_table(index="experiment_id", columns="condition", values=f"{long}_median", aggfunc="first").reindex(columns=list(sk.CONDITIONS))
        d = sk.contrast_scores(w.dropna(), cid)
        out[short] = D["experiment_id"].map(d)
    return out


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    D = ck.load_D()
    tests, loads, vars_ = [], [], []
    all_scores = []
    for cid in sk.PLANNED:
        S, lr, vr = scores_for(D, cid)
        loads += lr; vars_ += vr
        S["experiment_id"] = D["experiment_id"]; S["arm"] = D["arm"]; S["contrast"] = cid
        # whole-window EEG sensitivity
        WW = wholewindow_eeg_D(D, cid)
        sc_ww, load_ww, ve_ww = ck.pc1(WW, orient_on="eeg_theta")
        S["pc1_eeg_wholewindow"] = sc_ww
        vars_.append({"contrast": cid, "modality": "eeg_wholewindow", "n": int(WW.dropna().shape[0]), "k_vars": WW.shape[1], "pc1_var_explained": ve_ww,
                      "pc1_zmean_spearman": np.nan,
                      "spearman_with_k37_pc1": float(pd.concat([sc_ww, S["pc1_eeg"]], axis=1).dropna().corr(method="spearman").iloc[0, 1]),
                      **ck.pc1_loo_stability(WW, orient_on="eeg_theta")})
        for mod in ("beh", "traj", "proc"):
            r = ck.spearman_ci(S[f"pc1_{mod}"], S["pc1_eeg_wholewindow"])
            tests.append({"family": "sensitivity_wholewindow_eeg", "contrast": cid, "left": f"pc1_{mod}", "right": "pc1_eeg_wholewindow", "arm": "lab", **r})
        for mod in ("beh", "traj"):
            for e in ck.EEG_PRIMARY:
                r = ck.spearman_ci(S[f"pc1_{mod}"], WW[e])
                tests.append({"family": "sensitivity_wholewindow_eeg", "contrast": cid, "left": f"pc1_{mod}", "right": f"{e}_wholewindow", "arm": "lab", **r})
        all_scores.append(S)
        for a, b in (("beh", "traj"), ("beh", "eeg"), ("traj", "eeg")):
            for score, fam in (("pc1", "headline_PC1"), ("zmean", "sensitivity_zmean")):
                r = ck.spearman_ci(S[f"{score}_{a}"], S[f"{score}_{b}"])
                tests.append({"family": fam, "contrast": cid, "left": f"{score}_{a}", "right": f"{score}_{b}", "arm": "all", **r})
            # lab-only behaviour x trajectory, for comparability with the EEG pairs; and partial given arm
            if (a, b) == ("beh", "traj"):
                lab = S[S.arm == "lab"]
                r = ck.spearman_ci(lab["pc1_beh"], lab["pc1_traj"])
                tests.append({"family": "sensitivity_lab_only", "contrast": cid, "left": "pc1_beh", "right": "pc1_traj", "arm": "lab", **r})
                S["_arm"] = (S.arm == "lab").astype(float)
                rp = sk.partial_spearman(S, "pc1_beh", "pc1_traj", "_arm")
                tests.append({"family": "sensitivity_partial_arm", "contrast": cid, "left": "pc1_beh", "right": "pc1_traj", "arm": "all|arm",
                              "n": rp.get("n"), "rho": rp.get("rho_partial"), "p_raw": rp.get("p_raw")})
        # process (duration, reply latency, message length) as its own block: the largest raw cells of the
        # 2,560-cell map were process x engagement at the format contrast, so this family is declared here
        for b in ("beh", "traj", "eeg"):
            r = ck.spearman_ci(S["pc1_proc"], S[f"pc1_{b}"])
            tests.append({"family": "process_PC1", "contrast": cid, "left": "pc1_proc", "right": f"pc1_{b}", "arm": "all" if b != "eeg" else "lab", **r})
        # planned primaries
        for mod in ("beh", "traj"):
            for e in ck.EEG_PRIMARY:
                r = ck.spearman_ci(S[f"pc1_{mod}"], D[f"{e}__{cid}"])
                tests.append({"family": "planned_primaries", "contrast": cid, "left": f"pc1_{mod}", "right": e, "arm": "lab", **r})
    T = pd.DataFrame(tests)
    T = ck.holm_bh(T)
    T.to_csv(OUT / "headline_tests.csv", index=False)
    L = pd.DataFrame(loads); L.to_csv(OUT / "pc1_loadings.csv", index=False)
    V = pd.DataFrame(vars_); V.to_csv(OUT / "pc1_variance.csv", index=False)
    pd.concat(all_scores).to_csv(OUT / "pc1_scores.csv", index=False)
    figure(pd.concat(all_scores), T[T.family == "headline_PC1"])
    loadings_figure(L)
    summary = {
        "headline_PC1": T[T.family == "headline_PC1"][["contrast", "left", "right", "n", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm_family", "rho_loo_min", "rho_loo_max"]].round(3).to_dict(orient="records"),
        "planned_primaries": T[T.family == "planned_primaries"][["contrast", "left", "right", "n", "rho", "p_raw", "p_holm_family"]].round(3).to_dict(orient="records"),
        "process_PC1": T[T.family == "process_PC1"][["contrast", "left", "right", "n", "rho", "ci_lo", "ci_hi", "p_raw", "p_holm_family"]].round(3).to_dict(orient="records"),
        "hits": {f: int(T[T.family == f]["sig_holm_family"].sum()) for f in T.family.unique()},
        "min_p_raw": {f: float(T[T.family == f]["p_raw"].min()) for f in T.family.unique()},
        "pc1_variance": V.round(3).to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def figure(S: pd.DataFrame, T: pd.DataFrame) -> None:
    pairs = (("beh", "traj"), ("beh", "eeg"), ("traj", "eeg"))
    fig, axes = plt.subplots(3, 3, figsize=(12, 11))
    for i, cid in enumerate(sk.PLANNED):
        sub = S[S.contrast == cid]
        for j, (a, b) in enumerate(pairs):
            ax = axes[i, j]
            row = T[(T.contrast == cid) & (T.left == f"pc1_{a}") & (T.right == f"pc1_{b}")].iloc[0]
            for arm, m, c in (("lab", "o", "tab:blue"), ("crowd", "s", "0.6")):
                q = sub[sub.arm == arm].dropna(subset=[f"pc1_{a}", f"pc1_{b}"])
                if len(q):
                    ax.scatter(q[f"pc1_{a}"], q[f"pc1_{b}"], marker=m, color=c, s=28, label=f"{arm} (n={len(q)})", alpha=0.85)
            ax.axhline(0, color="k", lw=0.5); ax.axvline(0, color="k", lw=0.5)
            ax.set_title(f"{ck.PRETTY[cid]}\nrho = {row.rho:+.2f} [{row.ci_lo:+.2f}, {row.ci_hi:+.2f}]  p = {row.p_raw:.2f}  Holm = {row.p_holm_family:.2f}", fontsize=9)
            ax.set_xlabel(f"{ck.PRETTY[a]} PC1 of D", fontsize=8); ax.set_ylabel(f"{ck.PRETTY[b]} PC1 of D", fontsize=8)
            if i == 0 and j == 0:
                ax.legend(fontsize=7)
    fig.suptitle("Block 1: one score per modality per contrast; 9 tests, Holm within nine", fontsize=11)
    fig.tight_layout(); fig.savefig(OUT / "headline_scatter.png", dpi=150); plt.close(fig)


def loadings_figure(L: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 4, figsize=(20, 5.5), gridspec_kw={"wspace": 0.8, "width_ratios": [1, 1, 1, 0.8]})
    for ax, mod in zip(axes, BLOCKS):
        piv = L[L.modality == mod].pivot(index="variable", columns="contrast", values="loading")[list(sk.PLANNED)]
        piv = piv.loc[BLOCKS[mod]]
        im = ax.imshow(piv.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        ax.set_yticks(range(len(piv)), piv.index, fontsize=8)
        ax.set_xticks(range(3), [ck.PRETTY[c] for c in piv.columns], fontsize=8, rotation=20)
        for r in range(piv.shape[0]):
            for c in range(piv.shape[1]):
                ax.text(c, r, f"{piv.iat[r, c]:+.2f}", ha="center", va="center", fontsize=7)
        ax.set_title(f"{ck.PRETTY[mod]} PC1 loadings (corr with score)", fontsize=10)
    axes[0].text(-0.6, -1.2, "behaviour PC1 = negative evaluation (manipulation up, trust/credibility/helpfulness down)", fontsize=7, transform=axes[0].transData)
    fig.colorbar(im, ax=axes, shrink=0.6, pad=0.02)
    fig.savefig(OUT / "pc1_loadings.png", dpi=150, bbox_inches="tight"); plt.close(fig)


if __name__ == "__main__":
    s = run()
    pd.set_option("display.width", 220)
    print(pd.DataFrame(s["headline_PC1"]).to_string(index=False))
    print(pd.DataFrame(s["planned_primaries"]).to_string(index=False))
    print(pd.DataFrame(s["process_PC1"]).to_string(index=False))
    print(pd.DataFrame(s["pc1_variance"]).to_string(index=False))
    print(s["hits"], s["min_p_raw"])
