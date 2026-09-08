"""Block 2. Redraw the 2,560-cell combo map as CI forests.

A heatmap of rho hides the interval. At n = 18 a Spearman rho of .45
has a 95% interval of about [-.05, .77]; the reader needs to see that
width. Three panels of the a priori headline cells (behaviour
primaries x EEG primaries, behaviour primaries x trajectory headline,
trajectory headline x EEG primaries), one dot per planned contrast,
Bonett-Wright intervals; plus a fourth panel with the twelve smallest
raw p in the whole map, so the largest effects are visible with their
intervals and their Holm/BH verdicts.

Reads outputs/combos_all_tests.csv (run_combos.py); writes
outputs/forest/.
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st

import combokit as ck
from combokit import sk

OUT = ck.OUT / "forest"
COLORS = {"any_ad_vs_no_ads": "k", "inline_vs_block": "tab:blue", "early_vs_late": "tab:red"}
MARKERS = {"any_ad_vs_no_ads": "o", "inline_vs_block": "s", "early_vs_late": "^"}


def ci(rho: float, n: float) -> tuple[float, float]:
    se = math.sqrt((1 + rho * rho / 2) / (n - 3))
    z = np.arctanh(np.clip(rho, -0.9999, 0.9999)); zc = st.norm.ppf(0.975)
    return float(np.tanh(z - zc * se)), float(np.tanh(z + zc * se))


def forest_panel(ax, sub: pd.DataFrame, title: str) -> None:
    pairs = sub[["left", "right"]].drop_duplicates().apply(tuple, axis=1).tolist()
    pairs = sorted(pairs, key=lambda p: (p[0], p[1]))
    y0 = {p: i for i, p in enumerate(pairs)}
    n = int(sub["n"].dropna().iloc[0])
    for _, r in sub.iterrows():
        if pd.isna(r.effect):
            continue
        lo, hi = ci(r.effect, r.n)
        off = {"any_ad_vs_no_ads": -0.25, "inline_vs_block": 0.0, "early_vs_late": 0.25}[r.contrast]
        y = y0[(r.left, r.right)] + off
        ax.plot([lo, hi], [y, y], color=COLORS[r.contrast], lw=1)
        ax.plot(r.effect, y, MARKERS[r.contrast], color=COLORS[r.contrast], ms=4, mfc="white" if r.p_raw >= 0.05 else COLORS[r.contrast])
    ax.set_yticks(range(len(pairs)), [f"{a} × {b.replace('traj_', '').replace('eeg_', '')}" for a, b in pairs], fontsize=7)
    ax.invert_yaxis(); ax.set_xlim(-1, 1); ax.axvline(0, color="k", lw=0.8)
    thr_raw = st.t.ppf(0.975, n - 2) / math.sqrt(st.t.ppf(0.975, n - 2) ** 2 + n - 2)
    k = int(sub["n_tests_in_family"].iloc[0])
    thr_holm = st.t.ppf(1 - 0.025 / k, n - 2) / math.sqrt(st.t.ppf(1 - 0.025 / k, n - 2) ** 2 + n - 2)
    for t_, ls in ((thr_raw, ":"), (thr_holm, "--")):
        ax.axvline(t_, color="0.5", ls=ls, lw=0.8); ax.axvline(-t_, color="0.5", ls=ls, lw=0.8)
    ax.set_title(f"{title}\nn = {n}; dotted = raw .05\ndashed = Holm within family of {k}", fontsize=9)
    ax.set_xlabel("Spearman rho of person-level D (95% CI)", fontsize=8)
    for i in range(len(pairs)):
        if i % 2 == 0:
            ax.axhspan(i - 0.5, i + 0.5, color="0.95", zorder=0)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    T = pd.read_csv(ck.OUT / "combos_all_tests.csv")
    D = T[(T.grain == "D") & (T.headline == True) & (T.combo != "threeway")]  # noqa: E712
    fig, axes = plt.subplots(1, 3, figsize=(18, 8), gridspec_kw={"width_ratios": [1, 2.2, 1.2]})
    for ax, combo, title in zip(axes, ("beh_eeg", "beh_traj", "traj_eeg"),
                                ("behaviour × EEG (primaries)", "behaviour × trajectory (headline)", "trajectory × EEG (headline)")):
        forest_panel(ax, D[D.combo == combo], title)
    handles = [plt.Line2D([], [], color=COLORS[c], marker=MARKERS[c], ls="-", label=ck.PRETTY[c]) for c in sk.PLANNED]
    axes[0].legend(handles=handles, fontsize=7, loc="lower left")
    fig.suptitle("Block 2: the a priori cross-modal cells with their intervals (person-level D_i; filled = raw p < .05; none survive Holm or BH)", fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / "forest_headline.png", dpi=150); plt.close(fig)

    # top-12 raw p across the entire map, with CI and verdicts
    top = T[T.grain == "D"].sort_values("p_raw").head(12).copy()
    top[["ci_lo", "ci_hi"]] = [ci(r, n) for r, n in zip(top.effect, top.n)]
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, (_, r) in enumerate(top.iterrows()):
        ax.plot([r.ci_lo, r.ci_hi], [i, i], color=COLORS.get(r.contrast, "0.4"), lw=1.2)
        ax.plot(r.effect, i, MARKERS.get(r.contrast, "o"), color=COLORS.get(r.contrast, "0.4"), ms=5)
        ax.text(1.02, i, f"n={int(r.n)}  raw {r.p_raw:.4f}  Holm {r.p_holm_family:.2f}  BH {r.p_bh_global:.2f}", va="center", fontsize=7, transform=ax.get_yaxis_transform())
    ax.set_yticks(range(len(top)), [f"{r.combo} | {ck.PRETTY.get(r.contrast, r.contrast)} | {r.left} × {r.right}" for _, r in top.iterrows()], fontsize=7)
    ax.invert_yaxis(); ax.set_xlim(-1, 1); ax.axvline(0, color="k", lw=0.8)
    ax.set_title("Twelve smallest raw p of 2,560 combo tests, with 95% CI. Every Holm and BH verdict is null.", fontsize=9)
    ax.set_xlabel("Spearman rho (D grain)")
    fig.tight_layout(); fig.savefig(OUT / "forest_top12.png", dpi=150, bbox_inches="tight"); plt.close(fig)
    top.to_csv(OUT / "top12_raw.csv", index=False)

    # cluster check: process x engagement at the format contrast
    clus = T[(T.grain == "D") & (T.combo == "beh_eeg") & (T.contrast == "inline_vs_block")
             & (T.left.isin(ck.BEH_PROCESS)) & (T.right.isin(["eeg_engagement", "eeg_pope", "eeg_kislov", "eeg_beta", "eeg_gamma", "eeg_rel_beta", "eeg_rel_gamma"]))]
    clus.to_csv(OUT / "cluster_process_x_engagement_format.csv", index=False)
    print(top[["combo", "contrast", "left", "right", "n", "effect", "ci_lo", "ci_hi", "p_raw", "p_holm_family", "p_bh_global"]].round(3).to_string(index=False))
    print(clus[["left", "right", "effect", "p_raw"]].round(3).to_string(index=False))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    run()
