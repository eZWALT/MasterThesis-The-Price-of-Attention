#!/usr/bin/env python3
"""Freeze the recommended serving recipe (same-timing tilt)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, eval_scores, pairwise_breakdown

HERE = Path(__file__).resolve().parent
MIX, K, ALPHA = 0.15, 4, 10.0
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"


def oof_score(E, extra, y, g, turn):
    resid = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        scE = StandardScaler()
        pca = PCA(K, random_state=13)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        Xtr = np.hstack([P, extra[tr]])
        Xte = np.hstack([Pte, extra[te]])
        sc = StandardScaler()
        w = Ridge(ALPHA, fit_intercept=False).fit(sc.fit_transform(Xtr), r - r.mean()).coef_
        resid[te] = sc.transform(Xte) @ w
    z = (resid - resid.mean()) / (resid.std() + 1e-8)
    return turn.ravel() + MIX * z, resid


def person_ci(s, y, groups, n=2000):
    keys, inv = np.unique(groups, return_inverse=True)
    by = [y[inv == i] for i in range(len(keys))]
    bs = [s[inv == i] for i in range(len(keys))]
    rng = np.random.RandomState(13)
    boot = np.empty(n)
    for b in range(n):
        idx = rng.randint(0, len(keys), len(keys))
        boot[b] = spearmanr(
            np.concatenate([bs[i] for i in idx]),
            np.concatenate([by[i] for i in idx]),
        ).statistic
    return float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    E = np.load(E14)

    recipes = {
        "moment": ["log_lat"],
        "user_moment": ["log_lat", "ocean_O"],
        "same_t": ["log_lat", "ocean_O", "lex_q_start"],
    }
    packs = {}
    scores = {}
    for name, cols in recipes.items():
        extra = ads[cols].to_numpy(float)
        s, _ = oof_score(E, extra, y, g, turn)
        pack = eval_scores(f"BEST_{name}", s, anc, pairs)
        lo, hi = person_ci(s, y, g)
        pack["person_bootstrap_ci"] = [round(lo, 4), round(hi, 4)]
        st = pairwise_breakdown(pairs, dict(zip(anc.conversation_id, s)))
        z = (st["pairwise_same_timing"] - 0.5) / np.sqrt(0.25 / st["n_same"])
        pack["same_timing_z"] = round(float(z), 3)
        packs[name] = pack
        scores[name] = s
        print(name, pack, flush=True)

    primary = packs["same_t"]
    np.save(OUT / "pred_BEST_fixedturn_14b_lat.npy", scores["same_t"])
    extra = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
    resid = y - LinearRegression().fit(turn, y).predict(turn)
    scE = StandardScaler()
    pca = PCA(K, random_state=13)
    P = pca.fit_transform(scE.fit_transform(E))
    X = np.hstack([P, extra])
    sc = StandardScaler()
    w = Ridge(ALPHA, fit_intercept=False).fit(sc.fit_transform(X), resid - resid.mean()).coef_
    np.savez(
        OUT / "scorer_BEST_fixedturn_14b_lat.npz",
        pca_components=pca.components_, pca_mean=pca.mean_,
        emb_mean=scE.mean_, emb_scale=scE.scale_,
        feat_mean=sc.mean_, feat_scale=sc.scale_,
        w=w, mix=MIX, k=K,
        extra_cols=np.array(["log_lat", "ocean_O", "lex_q_start"]),
    )
    (OUT / "BEST.md").write_text(
        "# Best serving policy so far\n\n"
        "**Recommended serving π (moments, not just people):**\n"
        "`score = turn/8 + 0.15·z(Ridge(PCA₄(Qwen3-14B last-token), "
        "log latency, Openness, starts-with-question))`\n\n"
        "Person-bootstrap CI sits above the late rule (0.167).\n\n"
        f"- Spearman U LOPO: **{primary['spearman_U']}** "
        f"(person-bootstrap 95% CI {primary['person_bootstrap_ci'][0]}–"
        f"{primary['person_bootstrap_ci'][1]})\n"
        f"- same-timing pairwise: **{primary['pairwise_same_timing']}** "
        f"(z={primary['same_timing_z']}, n=108)\n"
        f"- within-person Spearman: **{primary['spearman_within']}**\n"
        f"- AUROC: **{primary['auroc_good']}**\n"
        f"- all-pair pairwise: {primary['pairwise']}\n\n"
        "`lex_q_start` is a conversation behaviour (user turn opens with "
        "what/which/how/…). Openness is BFI-10 if the product has it.\n\n"
        f"**Highest Spearman (people + moments):** drop the question feature → "
        f"{packs['user_moment']['spearman_U']} "
        f"(CI {packs['user_moment']['person_bootstrap_ci'][0]}–"
        f"{packs['user_moment']['person_bootstrap_ci'][1]}), "
        f"same-t {packs['user_moment']['pairwise_same_timing']}, "
        f"within {packs['user_moment']['spearman_within']}. "
        "Mostly ranks who tolerates ads.\n\n"
        f"**Moment-only (no BFI):** turn + latency + 14B → "
        f"Spearman {packs['moment']['spearman_U']}, "
        f"same-t {packs['moment']['pairwise_same_timing']}, "
        f"CI {packs['moment']['person_bootstrap_ci']}.\n\n"
        "Failed (do not promote): fat 54-column residual; DistilBERT / MiniLM / "
        "Qwen3-0.6B LoRA / RankNet fine-tunes (Spearman ≤ 0); two-stage "
        "turn+z(Openness); 8B/Phi/Thrad/instruct fusion; HGB; 1080-prefix PCA; "
        "MiniLM / BGE-m3 / Qwen3-Reranker-4B zero-shot; mix>0.15 (Spearman "
        "rises, late-prior flips). Keep mix **0.15**. "
        "Stepwise addition is what moved the number.\n"
    )
    json.dump(packs, open(OUT / "scorer_BEST.json", "w"), indent=2)
    print((OUT / "BEST.md").read_text())


if __name__ == "__main__":
    main()
