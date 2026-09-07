#!/usr/bin/env python3
"""Honest confirmation of anything that beat the late rule.

Nested LOPO (pick k, alpha on the 53, freeze, test the held-out person).
Bootstrap CI on the 216 scores. Timing-stripped check: does the text
score still rank same-timing pairs after we residualise it on turn?
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut, GroupKFold
from sklearn.preprocessing import StandardScaler

from train_campaign import (
    OUT, EXP, GOLD, eval_scores, pair_indices, pairwise_breakdown, spearman,
)

HERE = Path(__file__).resolve().parent
SEED = 13


def pca_ridge_once(Etr, ytr, Ete, k, alpha, extra_tr=None, extra_te=None):
    k = min(k, Etr.shape[0] - 2, Etr.shape[1])
    sc = StandardScaler()
    pca = PCA(k, random_state=SEED)
    Ptr = pca.fit_transform(sc.fit_transform(Etr))
    Pte = pca.transform(sc.transform(Ete))
    if extra_tr is not None:
        Ptr = np.hstack([Ptr, extra_tr])
        Pte = np.hstack([Pte, extra_te])
    sc2 = StandardScaler()
    Xs = sc2.fit_transform(Ptr)
    yc = ytr - ytr.mean()
    m = Ridge(alpha, fit_intercept=False).fit(Xs, yc)
    return sc2.transform(Pte) @ m.coef_


def nested_pca(E, y, groups, grid, extra=None):
    pred = np.full(len(y), np.nan)
    chosen = []
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(E, y, groups=groups):
        # inner 5-fold by person on train
        best, best_sc = None, -9
        inner_g = groups[tr]
        n_splits = min(5, len(np.unique(inner_g)))
        for k, a in grid:
            inner_pred = np.full(len(tr), np.nan)
            for itr, ite in GroupKFold(n_splits).split(E[tr], y[tr], groups=inner_g):
                extra_tr = extra[tr][itr] if extra is not None else None
                extra_te = extra[tr][ite] if extra is not None else None
                inner_pred[ite] = pca_ridge_once(
                    E[tr][itr], y[tr][itr], E[tr][ite], k, a, extra_tr, extra_te
                )
            sc = spearman(inner_pred, y[tr])
            if sc > best_sc:
                best_sc, best = sc, (k, a)
        k, a = best
        chosen.append({"k": k, "alpha": a, "inner": best_sc})
        extra_tr = extra[tr] if extra is not None else None
        extra_te = extra[te] if extra is not None else None
        pred[te] = pca_ridge_once(E[tr], y[tr], E[te], k, a, extra_tr, extra_te)
    return pred, chosen


def bootstrap_spearman(s, y, n=2000, seed=13):
    rng = np.random.RandomState(seed)
    s, y = np.asarray(s, float), np.asarray(y, float)
    vals = []
    for _ in range(n):
        i = rng.randint(0, len(s), len(s))
        vals.append(spearman(s[i], y[i]))
    vals = np.asarray(vals)
    return {
        "lo": round(float(np.nanpercentile(vals, 2.5)), 4),
        "hi": round(float(np.nanpercentile(vals, 97.5)), 4),
        "mean": round(float(np.nanmean(vals)), 4),
    }


def same_timing_p(pairs, score_by_conv):
    n = ok = 0
    for r in pairs.itertuples():
        if r.chosen_timing != r.rejected_timing:
            continue
        a = score_by_conv.get(r.chosen_conversation_id)
        b = score_by_conv.get(r.rejected_conversation_id)
        if a is None or b is None:
            continue
        n += 1
        ok += int(a > b)
    if not n:
        return {}
    p = ok / n
    # one-sided binomial vs 0.5, normal approx
    z = (p - 0.5) / np.sqrt(0.25 / n)
    return {"n": n, "acc": round(p, 4), "z": round(float(z), 3)}


def main():
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = anc.ux_retention_resid.to_numpy(float)
    g = anc.participant_key.to_numpy()
    turn = (anc.ad_turn.clip(upper=8) / 8.0).to_numpy()[:, None]
    results = []

    grid = [(4, 10), (8, 20), (8, 50), (16, 50), (16, 80), (32, 80)]
    targets = [
        EXP / "emb_qwen3-14b.npy",
        EXP / "emb_qwen3-8b.npy",
        EXP / "emb_phi-4-14b.npy",
        EXP / "emb_bge-small.npy",
        EXP / "emb_thradbert.npy",
        OUT / "emb_qwen3-emb-0.6b_1080.npy",
        OUT / "emb_qwen3-emb-4b_1080.npy",
        OUT / "emb_qwen3-emb-8b_1080.npy",
        OUT / "emb_bge_1080.npy",
    ]

    df1080 = None
    if (OUT / "turns_labelled.csv").exists():
        df1080 = pd.read_csv(OUT / "turns_labelled.csv")
        from train_campaign import ads_view
        ad_idx = ads_view(df1080, anc)

    for path in targets:
        if not path.exists():
            print("wait", path.name)
            continue
        E = np.load(path)
        if E.shape[0] == 1080:
            if df1080 is None:
                continue
            E = E[ad_idx]
        if E.shape[0] != 216:
            continue
        print("nested", path.name, E.shape, flush=True)
        pred, chosen = nested_pca(E, y, g, grid)
        pack = eval_scores(f"nested_{path.stem}", pred, anc, pairs)
        pack["bootstrap_spearman"] = bootstrap_spearman(pred, y)
        pack["same_timing"] = same_timing_p(pairs, dict(zip(anc.conversation_id, pred)))
        pack["k_chosen"] = pd.DataFrame(chosen).k.value_counts().to_dict()
        pack["alpha_chosen"] = pd.DataFrame(chosen).alpha.value_counts().to_dict()
        # timing-stripped score
        r = pred - LinearRegression().fit(turn, pred).predict(turn)
        pack["spearman_U_timing_stripped"] = round(spearman(r, y), 4)
        pack["same_timing_stripped"] = same_timing_p(pairs, dict(zip(anc.conversation_id, r)))
        # fixed turn + residual text
        resid = y - LinearRegression().fit(turn, y).predict(turn)
        pred_r, _ = nested_pca(E, resid, g, grid)
        for mix in (0.15, 0.3, 0.5):
            s = turn.ravel() + mix * (pred_r - np.nanmean(pred_r)) / (np.nanstd(pred_r) + 1e-8)
            p2 = eval_scores(f"fixedturn_m{mix}_{path.stem}", s, anc, pairs)
            p2["bootstrap_spearman"] = bootstrap_spearman(s, y)
            p2["same_timing"] = same_timing_p(pairs, dict(zip(anc.conversation_id, s)))
            results.append(p2)
        results.append(pack)
        json.dump(results, open(OUT / "confirm.json", "w"), indent=2)
        print(pack, flush=True)

    # latency + openness as a tiny locked residual (pre-specified from screen)
    if df1080 is not None:
        ads = df1080.iloc[ad_idx].reset_index(drop=True)
        lat = ads.log_lat.to_numpy()
        o = ads.ocean_O.to_numpy() if "ocean_O" in ads.columns else None
        # LOPO ridge on [lat, O] predicting residual U, then fixed turn
        from sklearn.model_selection import LeaveOneGroupOut
        extra = np.column_stack([lat] + ([o] if o is not None else []))
        pred = np.zeros(len(y))
        for tr, te in LeaveOneGroupOut().split(extra, y, groups=g):
            sc = StandardScaler()
            resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
            Xs = sc.fit_transform(extra[tr])
            m = Ridge(10, fit_intercept=False).fit(Xs, resid - resid.mean())
            pred[te] = sc.transform(extra[te]) @ m.coef_
        for mix in (0.2, 0.4):
            s = turn.ravel() + mix * (pred - pred.mean()) / (pred.std() + 1e-8)
            pack = eval_scores(f"fixedturn_m{mix}_lat_ocean", s, anc, pairs)
            pack["bootstrap_spearman"] = bootstrap_spearman(s, y)
            pack["same_timing"] = same_timing_p(pairs, dict(zip(anc.conversation_id, s)))
            results.append(pack)
            print(pack, flush=True)

    json.dump(results, open(OUT / "confirm.json", "w"), indent=2)
    lines = ["# Nested LOPO confirmation", ""]
    for r in sorted(results, key=lambda x: -(x.get("spearman_U") or -9)):
        ci = r.get("bootstrap_spearman", {})
        st = r.get("same_timing", {})
        lines.append(
            f"- **{r['name']}**: Spearman {r.get('spearman_U')} "
            f"(CI {ci.get('lo')}–{ci.get('hi')})  same-t {st.get('acc')} z={st.get('z')}"
        )
    (OUT / "CONFIRM.md").write_text("\n".join(lines) + "\n")
    print((OUT / "CONFIRM.md").read_text())


if __name__ == "__main__":
    main()
