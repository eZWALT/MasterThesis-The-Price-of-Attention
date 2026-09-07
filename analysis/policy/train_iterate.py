#!/usr/bin/env python3
"""Iterate residual + multi-task models on the fat behavioural feature set.

Keeps the late-rule locked (score = turn + mix * z(residual)).
Updates BEST.md if something beats 0.274 Spearman AND 0.60 same-timing.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet, LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from features_behaviour import OUT, build_ads_frame, feat_matrix
from train_campaign import GOLD, eval_scores, pair_indices, lopo_ranknet

HERE = Path(__file__).resolve().parent
BEST_BAR = 0.2737
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"


def oof_resid(X, y, g, turn, kind="ridge", alpha=20.0):
    pred = np.zeros(len(y))
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(X, y, groups=g):
        resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        resid = resid - resid.mean()
        if kind == "ridge":
            sc = StandardScaler()
            Xs = sc.fit_transform(X[tr])
            m = Ridge(alpha, fit_intercept=False).fit(Xs, resid)
            pred[te] = sc.transform(X[te]) @ m.coef_
        elif kind == "enet":
            sc = StandardScaler()
            Xs = sc.fit_transform(X[tr])
            m = ElasticNet(0.08, l1_ratio=0.4, fit_intercept=False, max_iter=5000).fit(Xs, resid)
            pred[te] = sc.transform(X[te]) @ m.coef_
        elif kind == "hgb":
            m = HistGradientBoostingRegressor(
                max_depth=3, max_iter=60, min_samples_leaf=12,
                l2_regularization=1.0, random_state=13,
            )
            m.fit(X[tr], resid)
            pred[te] = m.predict(X[te])
        elif kind == "et":
            m = ExtraTreesRegressor(
                n_estimators=200, max_depth=4, min_samples_leaf=8, random_state=13,
            )
            m.fit(X[tr], resid)
            pred[te] = m.predict(X[te])
    return pred


def fixed_turn(turn, resid, mix):
    z = (resid - resid.mean()) / (resid.std() + 1e-8)
    return turn.ravel() + mix * z


def lopo_pca(E, k=4):
    """Return OOF PCA scores (k cols) — no, we need train-only PCA inside residual.
    Here we just return the raw E; caller PCA-inside-fold.
    """
    return E


def oof_resid_with_emb(Xtab, E, y, g, turn, k=4, alpha=15.0):
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(Xtab, y, groups=g):
        resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        resid = resid - resid.mean()
        scE = StandardScaler()
        pca = PCA(min(k, E[tr].shape[0] - 2, E[tr].shape[1]), random_state=13)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        Xtr = np.hstack([Xtab[tr], P])
        Xte = np.hstack([Xtab[te], Pte])
        sc = StandardScaler()
        m = Ridge(alpha, fit_intercept=False).fit(sc.fit_transform(Xtr), resid)
        pred[te] = sc.transform(Xte) @ m.coef_
    return pred


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    E = np.load(E14)
    assert E.shape[0] == 216

    results = []
    X_all, cols_all = feat_matrix(ads, "all")
    X_no, _ = feat_matrix(ads, "no_ocean")
    print("X_all", X_all.shape, flush=True)

    # screen residual
    resid_y = y - LinearRegression().fit(turn, y).predict(turn)
    screen = []
    for i, c in enumerate(cols_all):
        from scipy.stats import spearmanr
        rho = spearmanr(X_all[:, i], resid_y).statistic
        screen.append((c, float(rho)))
    screen.sort(key=lambda t: -abs(t[1]))
    print("top residual features:", flush=True)
    for c, r in screen[:15]:
        print(f"  {c:28} {r:+.3f}", flush=True)
    json.dump([{"f": c, "rho": r} for c, r in screen], open(OUT / "feat_screen.json", "w"), indent=2)

    recipes = []
    # tabular only
    for name, X, kind, a in [
        ("bhv_ridge", X_all, "ridge", 25),
        ("bhv_ridge_noocean", X_no, "ridge", 25),
        ("bhv_ridge_a80", X_all, "ridge", 80),
        ("bhv_enet", X_all, "enet", 0),
        ("bhv_hgb", X_all, "hgb", 0),
        ("bhv_et", X_all, "et", 0),
    ]:
        recipes.append((name, oof_resid(X, y, g, turn, kind, a)))

    # top-k features
    top = [c for c, r in screen if abs(r) >= 0.08]
    if top:
        Xt = ads[top].to_numpy(float)
        recipes.append(("bhv_top08_ridge", oof_resid(Xt, y, g, turn, "ridge", 15)))

    # 14B + behavioural
    for k, a, tag in [(4, 15, "k4"), (4, 10, "k4a10"), (8, 20, "k8")]:
        recipes.append((f"bhv+14b_{tag}", oof_resid_with_emb(X_no, E, y, g, turn, k, a)))
        recipes.append((f"bhv_all+14b_{tag}", oof_resid_with_emb(X_all, E, y, g, turn, k, a)))

    # latency + 14B (reproduce BEST) + extra lex/mnli only
    extra_cols = [c for c in cols_all if c.startswith("mnli_") or c.startswith("lex_") or c == "log_lat"]
    Xe = ads[extra_cols].to_numpy(float)
    recipes.append(("lat_lex_mnli+14b", oof_resid_with_emb(Xe, E, y, g, turn, 4, 12)))

    # multi-task: residual of each delta, then U-like combo
    heads = {}
    for col, sign in [
        ("delta_credibility", 1), ("delta_trust", 1), ("delta_manipulation", -1),
        ("delta_helpfulness", 1), ("delta_convincingness", 1),
        ("delta_relevance", 1), ("delta_notice_sponsored", -1),
    ]:
        yh = sign * ads[col].to_numpy(float)
        heads[col] = oof_resid_with_emb(X_no, E, y if False else yh, g, turn, 4, 15)
    # wait - residual of yh against turn, then combo
    uhat = (heads["delta_credibility"] + heads["delta_trust"] + heads["delta_manipulation"]) / 3.0
    recipes.append(("multitask_3_resid+14b", uhat))
    uwide = (
        heads["delta_credibility"] + heads["delta_trust"] + heads["delta_manipulation"]
        + 0.5 * heads["delta_helpfulness"] + 0.5 * heads["delta_convincingness"]
        + 0.25 * heads["delta_notice_sponsored"]
    ) / 3.5
    recipes.append(("multitask_wide_resid+14b", uwide))

    # RankNet on fat+14bpca globally leaky — skip raw; LOPO ranknet on tab
    pidx = pair_indices(anc)
    recipes.append(("ranknet_bhv", lopo_ranknet(X_no, y, g, pidx, 25)))

    best = None
    for name, resid in recipes:
        for mix in (0.12, 0.18, 0.25, 0.35):
            s = fixed_turn(turn, resid, mix)
            pack = eval_scores(f"{name}_m{mix}", s, anc, pairs)
            results.append(pack)
            if best is None or (pack["spearman_U"] or -9) > (best["spearman_U"] or -9):
                best = dict(pack)
                best["_score"] = s
                best["_resid"] = resid
        safe = [{k: v for k, v in r.items() if not hasattr(v, "shape")} for r in results]
        json.dump(safe, open(OUT / "iterate.json", "w"), indent=2)

    results.sort(key=lambda r: -(r.get("spearman_U") or -9))
    lines = [
        "# Behavioural + transformer-feature iteration",
        "",
        f"Bar to beat: Spearman {BEST_BAR} and same-timing ≥ 0.60.",
        "",
        "| model | Spearman | same-t | pair | AUROC | beats |",
        "|---|---:|---:|---:|---:|:---:|",
    ]
    for r in results[:40]:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('auroc_good')} | {'YES' if r.get('beats_turn') else ''} |"
        )
    (OUT / "ITERATE.md").write_text("\n".join(lines) + "\n")
    print((OUT / "ITERATE.md").read_text())
    print("BEST this pass", best["name"], best["spearman_U"], best.get("pairwise_same_timing"))

    if best and best["spearman_U"] > BEST_BAR and (best.get("pairwise_same_timing") or 0) >= 0.60:
        np.save(OUT / "pred_BEST_fixedturn_14b_lat.npy", best["_score"])
        (OUT / "BEST.md").write_text(
            "# Best serving policy so far\n\n"
            f"**{best['name']}**\n\n"
            f"- Spearman U: **{best['spearman_U']}**\n"
            f"- same-timing: **{best.get('pairwise_same_timing')}**\n"
            f"- pairwise: {best.get('pairwise')}\n"
            f"- AUROC: {best.get('auroc_good')}\n"
        )
        print("UPDATED BEST.md", flush=True)


if __name__ == "__main__":
    main()
