#!/usr/bin/env python3
"""Next iteration: two-stage person+moment, mix/α/k, new prefix features, emb fusion.

Bar: recommended same_t recipe Spearman 0.3088 / same-timing 0.6389.
Replace BEST only if Spearman stays ≥ 0.30 with CI above the late rule
AND same-timing does not collapse below 0.60, or both move up.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import ElasticNet, LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, ads_view, eval_scores

HERE = Path(__file__).resolve().parent
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"
EXP = HERE / "outputs/experiments"
FULL = HERE / "outputs/experiments/full"
SEED = 13


def oof_ridge_extra(E, extra, y, g, turn, k=4, alpha=10.0, y_is_resid=False):
    """LOPO residual of y after turn (unless y_is_resid), Ridge no intercept."""
    pred = np.zeros(len(y))
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(E, y, groups=g):
        if y_is_resid:
            resid = y[tr] - y[tr].mean()
        else:
            resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
            resid = resid - resid.mean()
        scE = StandardScaler()
        pca = PCA(k, random_state=SEED)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        Xtr = np.hstack([P, extra[tr]]) if extra.shape[1] else P
        Xte = np.hstack([Pte, extra[te]]) if extra.shape[1] else Pte
        sc = StandardScaler()
        m = Ridge(alpha, fit_intercept=False).fit(sc.fit_transform(Xtr), resid)
        pred[te] = sc.transform(Xte) @ m.coef_
    return pred


def oof_model_extra(E, extra, y, g, turn, kind="ridge", k=4, alpha=10.0):
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        resid = resid - resid.mean()
        scE = StandardScaler()
        pca = PCA(k, random_state=SEED)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        Xtr = np.hstack([P, extra[tr]])
        Xte = np.hstack([Pte, extra[te]])
        sc = StandardScaler()
        Ztr, Zte = sc.fit_transform(Xtr), sc.transform(Xte)
        if kind == "ridge":
            m = Ridge(alpha, fit_intercept=False).fit(Ztr, resid)
            pred[te] = Zte @ m.coef_
        elif kind == "enet":
            m = ElasticNet(alpha=0.05, l1_ratio=0.3, fit_intercept=False, max_iter=4000)
            m.fit(Ztr, resid)
            pred[te] = m.predict(Zte)
        elif kind == "kr_rbf":
            m = KernelRidge(alpha=2.0, kernel="rbf", gamma=0.05)
            m.fit(Ztr, resid)
            pred[te] = m.predict(Zte)
        elif kind == "hgb":
            m = HistGradientBoostingRegressor(
                max_depth=2, max_iter=40, min_samples_leaf=20,
                l2_regularization=1.0, random_state=SEED,
            )
            m.fit(Ztr, resid)
            pred[te] = m.predict(Zte)
        else:
            raise ValueError(kind)
    return pred


def blend(turn, *parts):
    """turn + sum_i mix_i * z(part_i). parts are (mix, array)."""
    s = turn.ravel().astype(float).copy()
    for mix, arr in parts:
        a = np.asarray(arr, float)
        z = (a - a.mean()) / (a.std() + 1e-8)
        s = s + mix * z
    return s


def rec(results, name, scores, anc, pairs):
    pack = eval_scores(name, scores, anc, pairs)
    results.append(pack)
    print(name, pack["spearman_U"], "same-t", pack.get("pairwise_same_timing"),
          "within", pack.get("spearman_within"), flush=True)
    return pack


def load_216(path, ads, prim, anc):
    arr = np.load(path)
    if arr.shape[0] == 216:
        return arr
    if arr.shape[0] == 1080:
        idx = ads_view(prim, anc)
        return arr[idx]
    raise ValueError(f"{path} shape {arr.shape}")


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    prim = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = prim[prim.source_set == "primary"].copy()
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    E = np.load(E14)
    results = []

    # --- locked recipes ---
    recipes = {
        "lat": ["log_lat"],
        "lat_O": ["log_lat", "ocean_O"],
        "same_t": ["log_lat", "ocean_O", "lex_q_start"],
        "lat_N": ["log_lat", "ocean_N"],
        "lat_O_ttr": ["log_lat", "ocean_O", "lex_ttr"],
        "lat_O_qmark": ["log_lat", "ocean_O", "lex_qmark"],
    }
    oof = {}
    for name, cols in recipes.items():
        extra = ads[cols].to_numpy(float)
        oof[name] = oof_ridge_extra(E, extra, y, g, turn)
        rec(results, f"lock_{name}_m0.15", blend(turn, (0.15, oof[name])), anc, pairs)

    # --- mix / alpha / k on same_t ---
    extra_st = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
    for k in (2, 4, 6, 8):
        for a in (3.0, 10.0, 30.0, 80.0):
            pred = oof_ridge_extra(E, extra_st, y, g, turn, k=k, alpha=a)
            for mix in (0.08, 0.12, 0.15, 0.20, 0.28):
                rec(results, f"st_k{k}_a{a:g}_m{mix}", blend(turn, (mix, pred)), anc, pairs)

    # --- two-stage: turn + a*z(O) + mix*z(moment without O) ---
    extra_m = ads[["log_lat", "lex_q_start"]].to_numpy(float)
    moment = oof_ridge_extra(E, extra_m, y, g, turn)
    O = ads.ocean_O.to_numpy(float)
    rec(results, "moment_lat_q_m0.15", blend(turn, (0.15, moment)), anc, pairs)
    for a_o in (0.05, 0.10, 0.15, 0.22, 0.30):
        for mix in (0.10, 0.15, 0.22):
            rec(
                results, f"2stage_O{a_o}_m{mix}",
                blend(turn, (a_o, O), (mix, moment)), anc, pairs,
            )

    # residualize y on turn+O first, then moment-only ridge
    y2 = np.zeros_like(y)
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        Xn = np.hstack([turn[tr], ads[["ocean_O"]].to_numpy(float)[tr]])
        Xe = np.hstack([turn[te], ads[["ocean_O"]].to_numpy(float)[te]])
        y2[te] = y[te] - LinearRegression().fit(Xn, y[tr]).predict(Xe)
    moment2 = oof_ridge_extra(E, extra_m, y2, g, turn, y_is_resid=True)
    rec(results, "residYO_moment_m0.15", blend(turn, (0.12, O), (0.15, moment2)), anc, pairs)
    rec(results, "residYO_moment_m0.20", blend(turn, (0.15, O), (0.20, moment2)), anc, pairs)

    # --- new conversation features stepwise on same_t ---
    ads["ix_lat_O"] = ads.log_lat * ads.ocean_O
    ads["ix_q_lat"] = ads.lex_q_start * ads.log_lat
    ads["ix_q_O"] = ads.lex_q_start * ads.ocean_O
    ads["ix_q_early"] = ads.lex_q_start * (1.0 - ads.turn_feat)
    new_cands = [
        "lex_ttr", "lex_qmark", "lex_hedge", "lex_i", "lex_product",
        "asst_qmark", "asst_rec", "asst_list", "user_asst_ratio", "log_asst",
        "pre_q_rate", "pre_qmark", "pre_hedge", "pre_prod",
        "run_entropy", "run_n_shift", "p_purch",
        "ocean_N", "ocean_C", "ocean_E", "ocean_A",
        "ix_lat_O", "ix_q_lat", "ix_q_O", "ix_q_early",
        "mnli_6", "mnli_0", "mnli_2",
    ]
    new_cands = [c for c in new_cands if c in ads.columns]
    base_cols = ["log_lat", "ocean_O", "lex_q_start"]
    base_pred = oof["same_t"]
    base_pack = rec(results, "base_same_t", blend(turn, (0.15, base_pred)), anc, pairs)
    best_sp, best_st = base_pack["spearman_U"], base_pack.get("pairwise_same_timing") or 0
    chosen = list(base_cols)
    improved = True
    while improved:
        improved = False
        trial = None
        for c in new_cands:
            if c in chosen:
                continue
            extra = ads[chosen + [c]].to_numpy(float)
            pred = oof_ridge_extra(E, extra, y, g, turn)
            pack = eval_scores(f"add_{'+'.join(chosen+[c])}", blend(turn, (0.15, pred)), anc, pairs)
            results.append(pack)
            sp, st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
            # keep if same-t not down more than 0.01 and spearman not down
            if sp >= best_sp - 0.002 and st >= best_st - 0.01 and (sp > best_sp or st > best_st + 0.005):
                key = (sp, st)
                if trial is None or key > trial[0]:
                    trial = (key, c, pack, pred)
        if trial:
            _, c, pack, pred = trial
            chosen.append(c)
            best_sp, best_st = pack["spearman_U"], pack.get("pairwise_same_timing") or 0
            print("KEEP", chosen, pack["spearman_U"], pack.get("pairwise_same_timing"), flush=True)
            improved = True

    # --- embedding fusion ---
    emb_specs = [
        ("8b", EXP / "emb_qwen3-8b.npy", 2),
        ("phi", EXP / "emb_phi-4-14b.npy", 2),
        ("thrad", EXP / "emb_thradbert.npy", 2),
        ("bge", EXP / "emb_bge-small.npy", 2),
        ("q4i", FULL / "emb_qwen4b_instruct_216.npy", 2),
        ("q8i", FULL / "emb_qwen8b_instruct_216.npy", 2),
        ("q06i", FULL / "emb_qwen06_instruct_216.npy", 2),
    ]
    extra = extra_st
    for name, path, k2 in emb_specs:
        if not path.exists():
            continue
        try:
            E2 = load_216(path, ads, prim, anc)
        except Exception as exc:
            print("skip", name, exc, flush=True)
            continue
        pred = np.zeros(len(y))
        for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
            resid = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
            resid = resid - resid.mean()
            sc1, sc2 = StandardScaler(), StandardScaler()
            p1 = PCA(4, random_state=SEED).fit(sc1.fit_transform(E[tr]))
            kk = min(k2, E2.shape[1], max(1, len(tr) - 2))
            p2 = PCA(kk, random_state=SEED).fit(sc2.fit_transform(E2[tr]))
            P = np.hstack([
                p1.transform(sc1.transform(E[tr])),
                p2.transform(sc2.transform(E2[tr])),
                extra[tr],
            ])
            Pe = np.hstack([
                p1.transform(sc1.transform(E[te])),
                p2.transform(sc2.transform(E2[te])),
                extra[te],
            ])
            sc = StandardScaler()
            m = Ridge(10.0, fit_intercept=False).fit(sc.fit_transform(P), resid)
            pred[te] = sc.transform(Pe) @ m.coef_
        rec(results, f"fuse14_{name}_st_m0.15", blend(turn, (0.15, pred)), anc, pairs)

    # --- nonlinear residual on same_t extras ---
    for kind in ("enet", "kr_rbf", "hgb"):
        pred = oof_model_extra(E, extra_st, y, g, turn, kind=kind)
        rec(results, f"{kind}_st_m0.15", blend(turn, (0.15, pred)), anc, pairs)

    # --- multi-task residual: mean of cred/trust/-manip ---
    y_mt = np.vstack([
        ads.delta_credibility.to_numpy(float),
        ads.delta_trust.to_numpy(float),
        -ads.delta_manipulation.to_numpy(float),
    ]).T
    y_mt = np.nanmean(y_mt, axis=1)
    pred = oof_ridge_extra(E, extra_st, y_mt, g, turn)
    rec(results, "multitask_Uparts_st_m0.15", blend(turn, (0.15, pred)), anc, pairs)

    # dump
    json.dump(results, open(OUT / "next.json", "w"), indent=2)
    rows = [r for r in results if "spearman_U" in r]
    rows.sort(key=lambda r: (
        -(r["spearman_U"] or -9),
        -(r.get("pairwise_same_timing") or 0),
    ))
    lines = [
        "# Next iteration (two-stage, mix grid, new prefix, emb fusion)",
        "",
        "Bar: same_t 0.3088 / 0.6389.",
        "",
        "| model | Spearman | same-t | pair | within | AUROC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows[:40]:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('spearman_within')} | {r.get('auroc_good')} |"
        )
    (OUT / "NEXT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "NEXT.md").read_text())
    print("chosen stepwise", chosen, "sp", best_sp, "st", best_st)
    print("n_models", len(rows))


if __name__ == "__main__":
    main()
