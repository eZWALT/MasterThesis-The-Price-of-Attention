"""Trust, looked at as data before any verdict.

Single item ``personality_trust`` (1-7), one answer per person per
condition. This script prints and plots what the 54 × 5 matrix looks
like, then runs Friedman and the ten pairwise Wilcoxon tests on it,
by arm and pooled, and checks the obvious confounds (session order,
task, ceiling, ties). Writes to outputs/exploratory/trust/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

HERE = Path(__file__).resolve().parent
WALTER = HERE.parents[1]
sys.path.insert(0, str(WALTER))
import statkit as sk  # noqa: E402

GOLD = WALTER / "behavioural" / "outputs" / "gold"
OUT = WALTER / "behavioural" / "outputs" / "exploratory" / "trust"
COND = list(sk.CONDITIONS)


def block(title: str) -> None:
    print("\n" + "=" * 88 + f"\n{title}\n" + "=" * 88)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c = pd.read_csv(GOLD / "condition_features.csv")
    person = pd.read_csv(GOLD / "person_features.csv")
    ads = pd.read_csv(GOLD / "advertisement_features.csv")
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", 40)

    # ------------------------------------------------------------------ 1
    block("1. The matrix: 54 people × 5 conditions, raw trust (1-7)")
    w = c.pivot_table(index=["arm", "experiment_id"], columns="condition", values="trust", aggfunc="first")[COND]
    w.columns = [sk.LABEL[x] for x in COND]
    w["any_ad_mean"] = w[[sk.LABEL[x] for x in sk.AD_CONDITIONS]].mean(axis=1)
    w["D_any_ad"] = w["any_ad_mean"] - w["no ad"]
    w["D_early_late"] = 0.5 * (w["implicit early"] + w["explicit early"]) - 0.5 * (w["implicit late"] + w["explicit late"])
    w["D_impl_expl"] = 0.5 * (w["implicit early"] + w["implicit late"]) - 0.5 * (w["explicit early"] + w["explicit late"])
    w["range"] = w[[sk.LABEL[x] for x in COND]].max(axis=1) - w[[sk.LABEL[x] for x in COND]].min(axis=1)
    w = w.reset_index()
    w["experiment_id"] = w["experiment_id"].str.slice(4, 20)
    print(w.round(2).to_string(index=False))
    w.to_csv(OUT / "trust_matrix.csv", index=False)

    # ------------------------------------------------------------------ 2
    block("2. Per-condition descriptives, pooled and by arm")
    def desc(df):
        g = df.groupby("condition")["trust"]
        d = pd.DataFrame({"n": g.count(), "mean": g.mean(), "sd": g.std(), "median": g.median(),
                          "q25": g.quantile(.25), "q75": g.quantile(.75), "min": g.min(), "max": g.max(),
                          "share_7": g.apply(lambda s: (s == 7).mean()), "share_le3": g.apply(lambda s: (s <= 3).mean())})
        return d.reindex(COND).round(2)
    print("pooled\n", desc(c).to_string())
    for arm in ("lab", "crowd"):
        print(f"\n{arm}\n", desc(c[c.arm == arm]).to_string())

    # ------------------------------------------------------------------ 3
    block("3. Likert histogram per condition (counts of 1..7)")
    hist = c.pivot_table(index="condition", columns="trust", values="experiment_id", aggfunc="count").reindex(COND).fillna(0).astype(int)
    print(hist.to_string())

    # ------------------------------------------------------------------ 4
    block("4. Sign of the within-person differences (who moved, and which way)")
    for col in ("D_any_ad", "D_early_late", "D_impl_expl"):
        d = w[col]
        print(f"{col:14s} negative {int((d < 0).sum()):2d}  zero {int((d == 0).sum()):2d}  positive {int((d > 0).sum()):2d}   "
              f"mean {d.mean():+.2f}  median {d.median():+.2f}  |d|>=1: {int((d.abs() >= 1).sum())}")
    print("people with identical trust in all 5 conditions:", int((w["range"] == 0).sum()))
    print("people with range >= 3:", int((w["range"] >= 3).sum()))
    for arm in ("lab", "crowd"):
        d = w.loc[w.arm == arm, "D_any_ad"]
        print(f"  {arm:5s} D_any_ad  neg {int((d < 0).sum()):2d} zero {int((d == 0).sum()):2d} pos {int((d > 0).sum()):2d}  mean {d.mean():+.2f}")

    # ------------------------------------------------------------------ 5
    block("5. Friedman (5 conditions and 4 ad conditions), pooled and by arm")
    rows = []
    for arm, df in (("pooled", c), ("lab", c[c.arm == "lab"]), ("crowd", c[c.arm == "crowd"])):
        ww = sk.wide(df, "trust")
        for name, cols in (("friedman_5", sk.CONDITIONS), ("friedman_4ad", sk.AD_CONDITIONS)):
            r = sk.friedman(ww, cols)
            r.update({"arm": arm, "test": name})
            rows.append(r)
    fr = pd.DataFrame(rows)[["arm", "test", "n", "k", "stat", "p_raw", "kendall_w"]]
    print(fr.round(4).to_string(index=False))
    fr.to_csv(OUT / "trust_friedman.csv", index=False)

    # ------------------------------------------------------------------ 6
    block("6. Ten pairwise Wilcoxon (pooled n=54), Holm within the 10, plus arm split")
    pw_rows = []
    for arm, df in (("pooled", c), ("lab", c[c.arm == "lab"]), ("crowd", c[c.arm == "crowd"])):
        ww = sk.wide(df, "trust")
        pw = pd.DataFrame(sk.pairwise_wilcoxon(ww))
        pw["arm"] = arm
        pw["family"] = arm
        pw_rows.append(pw)
    pw = pd.concat(pw_rows, ignore_index=True)
    pw = sk.add_corrections(pw, family_col="family", p_col="p_raw")
    show = pw[["arm", "pair_label", "n", "mean", "sd", "rank_biserial", "p_raw", "p_holm_family"]]
    print(show.loc[show.arm == "pooled"].sort_values("p_raw").round(3).to_string(index=False))
    print("\nlab / crowd, raw p < .10 only")
    print(show.loc[(show.arm != "pooled") & (show.p_raw < .10)].sort_values("p_raw").round(3).to_string(index=False))
    pw.to_csv(OUT / "trust_pairwise_wilcoxon.csv", index=False)

    # ------------------------------------------------------------------ 7
    block("7. Planned D: paired t and Wilcoxon, pooled and by arm")
    rows = []
    for arm, df in (("pooled", c), ("lab", c[c.arm == "lab"]), ("crowd", c[c.arm == "crowd"])):
        ww = sk.wide(df, "trust")
        for cid in sk.CONTRASTS:
            r = sk.paired_d(sk.contrast_scores(ww, cid))
            r.update({"arm": arm, "contrast": sk.CONTRAST_LABEL[cid]})
            rows.append(r)
    pdt = pd.DataFrame(rows)[["arm", "contrast", "n", "mean", "ci95_lo", "ci95_hi", "dz", "p_raw", "p_wilcoxon"]]
    print(pdt.round(3).to_string(index=False))
    pdt.to_csv(OUT / "trust_planned_D_by_arm.csv", index=False)

    # ------------------------------------------------------------------ 8
    block("8. Confounds: session order and task, independent of condition")
    pos = c.groupby("session_position")["trust"].agg(["count", "mean", "std"]).round(2)
    print("by session position (0 first .. 4 last)\n", pos.to_string())
    # Friedman on position instead of condition
    wp = c.pivot_table(index="experiment_id", columns="session_position", values="trust", aggfunc="first").dropna()
    chi, p = stats.friedmanchisquare(*[wp[k].to_numpy() for k in wp.columns])
    print(f"Friedman over position: chi2={chi:.2f} p={p:.4f}   (n={len(wp)})")
    last_minus_first = (wp[wp.columns.max()] - wp[wp.columns.min()])
    print(f"last − first position: mean {last_minus_first.mean():+.2f}, Wilcoxon p={stats.wilcoxon(last_minus_first).pvalue:.4f}")
    task = c.groupby("task_genre")["trust"].agg(["count", "mean", "std"]).round(2).sort_values("mean")
    print("\nby task genre\n", task.to_string())
    xt = pd.crosstab(c["condition"], c["session_position"]).reindex(COND)
    print("\ncondition × position counts (is the design balanced?)\n", xt.to_string())

    # ------------------------------------------------------------------ 9
    block("9. Trust vs the other outcomes, within person (D vs D) and level")
    dcols = {}
    for o in ("trust", "notice", "manipulation", "credibility", "helpfulness", "relevance", "neutrality"):
        ww = sk.wide(c, o)
        dcols[o] = sk.contrast_scores(ww, "any_ad_vs_no_ads")
    dd = pd.DataFrame(dcols)
    rho = dd.corr(method="spearman").round(2)
    print("Spearman among any-ad D_i (n=54)\n", rho.to_string())
    for o in ("notice", "manipulation", "credibility"):
        r = sk.spearman(dd["trust"], dd[o])
        print(f"  D_trust ~ D_{o}: rho={r['rho']:+.2f} p={r['p_raw']:.4f}")
    # does noticing predict distrust? split by whether notice rose under ads
    noticed = dd["notice"] > 0
    print(f"\nD_trust among people whose notice rose under ads (n={int(noticed.sum())}): mean {dd.loc[noticed,'trust'].mean():+.2f}")
    print(f"D_trust among people whose notice did not rise (n={int((~noticed).sum())}): mean {dd.loc[~noticed,'trust'].mean():+.2f}")
    print("Mann-Whitney on D_trust between the two groups: p=%.4f" % stats.mannwhitneyu(dd.loc[noticed, "trust"], dd.loc[~noticed, "trust"]).pvalue)

    # ------------------------------------------------------------------ 10
    block("10. Trust vs personality, level and D (n=54)")
    lvl = c.groupby("experiment_id")["trust"].mean().rename("trust_level")
    pm = person.set_index("experiment_id").join(lvl).join(dd["trust"].rename("D_trust_any_ad"))
    for trait in ("bfi_e", "bfi_a", "bfi_c", "bfi_n", "bfi_o"):
        a = sk.spearman(pm["trust_level"], pm[trait]); b = sk.spearman(pm["D_trust_any_ad"], pm[trait])
        print(f"  {trait}: level rho={a['rho']:+.2f} p={a['p_raw']:.3f}   D_any_ad rho={b['rho']:+.2f} p={b['p_raw']:.3f}")
    print("\nlab vs crowd trust level: lab %.2f  crowd %.2f  Mann-Whitney p=%.4f" % (
        pm.loc[pm.arm == "lab", "trust_level"].mean(), pm.loc[pm.arm == "crowd", "trust_level"].mean(),
        stats.mannwhitneyu(pm.loc[pm.arm == "lab", "trust_level"], pm.loc[pm.arm == "crowd", "trust_level"]).pvalue))

    # ------------------------------------------------------------------ 11
    block("11. Cued-recall trust shift (ad grain, 216): the other trust question")
    rs = ads.groupby("condition")["recall_trust_shift"].agg(["count", "mean", "std", "median"]).reindex(list(sk.AD_CONDITIONS)).round(2)
    print(rs.to_string())
    hist2 = ads.pivot_table(index="condition", columns="recall_trust_shift", values="experiment_id", aggfunc="count").reindex(list(sk.AD_CONDITIONS)).fillna(0).astype(int)
    print("\nhistogram\n", hist2.to_string())

    # ------------------------------------------------------------------ figures
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    ax = axes[0]
    mat = w[[sk.LABEL[x] for x in COND]].to_numpy(dtype=float)
    order = np.argsort(w["D_any_ad"].to_numpy())
    im = ax.imshow(mat[order], aspect="auto", cmap="RdYlGn", vmin=1, vmax=7)
    ax.set_xticks(range(5), [sk.LABEL[x] for x in COND], rotation=30, ha="right")
    ax.set_ylabel("person (sorted by any-ad − no-ad)")
    ax.set_title("raw trust 1–7, 54 × 5")
    fig.colorbar(im, ax=ax, fraction=0.04)
    ax = axes[1]
    for i, cond in enumerate(COND):
        vals = c.loc[c.condition == cond, "trust"]
        ax.plot(np.full(len(vals), i) + np.random.uniform(-0.18, 0.18, len(vals)), vals, "o", ms=3, alpha=0.4, color="0.3")
        ax.plot([i - 0.3, i + 0.3], [vals.mean()] * 2, color="crimson", lw=2)
        ax.plot([i - 0.2, i + 0.2], [vals.median()] * 2, color="navy", lw=2)
    ax.set_xticks(range(5), [sk.LABEL[x] for x in COND], rotation=30, ha="right")
    ax.set_ylim(0.5, 7.5); ax.set_title("trust by condition (red mean, blue median)")
    ax = axes[2]
    for arm, colr in (("lab", "tab:blue"), ("crowd", "tab:orange")):
        sub = c[c.arm == arm].groupby("condition")["trust"].agg(["mean", "sem"]).reindex(COND)
        ax.errorbar(range(5), sub["mean"], yerr=1.96 * sub["sem"], marker="o", capsize=3, label=f"{arm} (n={c[c.arm == arm].experiment_id.nunique()})", color=colr)
    ax.set_xticks(range(5), [sk.LABEL[x] for x in COND], rotation=30, ha="right")
    ax.set_title("mean ± 95% CI by arm"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "trust_overview.png", dpi=150); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, col in zip(axes, ("D_any_ad", "D_impl_expl", "D_early_late")):
        d = w[col]
        ax.hist(d, bins=np.arange(-4.125, 4.25, 0.25), color="0.4")
        ax.axvline(0, color="k"); ax.axvline(d.mean(), color="crimson", label=f"mean {d.mean():+.2f}")
        ax.set_title(col); ax.legend()
    fig.suptitle("Within-person trust differences, n = 54")
    fig.tight_layout(); fig.savefig(OUT / "trust_D_hist.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    for _, r in w.iterrows():
        ax.plot(range(5), r[[sk.LABEL[x] for x in COND]].to_numpy(dtype=float) + np.random.uniform(-0.08, 0.08), color="tab:blue" if r.arm == "lab" else "tab:orange", alpha=0.25, lw=1)
    m = c.groupby("condition")["trust"].mean().reindex(COND)
    ax.plot(range(5), m, color="k", lw=3, marker="o", label="mean")
    ax.set_xticks(range(5), [sk.LABEL[x] for x in COND], rotation=20)
    ax.set_title("Every person's trust profile (blue lab, orange crowd)"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "trust_spaghetti.png", dpi=150); plt.close(fig)
    print(f"\nfigures + csv in {OUT}")


if __name__ == "__main__":
    np.random.seed(0)
    run()
