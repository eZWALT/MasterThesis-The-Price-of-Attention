#!/usr/bin/env python3
"""Proper modelling pass: use ALL primary data, LOPO by person.

What was wrong before
---------------------
216 last-token vectors (4096–5120 dim) + ridge, and turn was *not* in X.
That overfits and throws away the only reliable signal (late > early).

What this does
--------------
X rows = all 1,080 primary user turns (54 people × 5 conditions × 4 turns).
Y is the conversation-level human UX, copied onto every turn of that chat
(leave-one-person-out so this is extra views, not leakage).
No-ad chats have U = 0 by construction.

Features (never presentation/lambda):
  turn, latency, length, ThradBERT posteriors, trajectory stats, fit,
  optional task_genre, PCA of a real sentence embedding (bge).

Eval is still the 216 advertised conversations of held-out people
(score = the ad-turn row). Beat baseline_turn (Spearman ~0.17) or fail.

Runs on CPU. Safe to run while GPU LoRA is going.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "experiments" / "full"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 13


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3 or np.nanstd(a[ok]) == 0 or np.nanstd(b[ok]) == 0:
        return float("nan")
    return float(spearmanr(a[ok], b[ok]).statistic)


def auroc(y, s) -> float:
    y, s = np.asarray(y), np.asarray(s)
    if len(np.unique(y[~np.isnan(s)])) < 2:
        return float("nan")
    m = ~np.isnan(s)
    return float(roc_auc_score(y[m], s[m]))


def pairwise_acc(anc_eval: pd.DataFrame, scores: np.ndarray) -> float:
    s = pd.Series(scores, index=anc_eval.index)
    ok = n = 0
    for pid, g in anc_eval.assign(_s=s.values).groupby("participant_key"):
        rows = g.to_dict("records")
        for i in range(len(rows)):
            for j in range(i + 1, len(rows)):
                a, b = rows[i], rows[j]
                if a["ux_retention_resid"] == b["ux_retention_resid"]:
                    continue
                n += 1
                chosen = a if a["ux_retention_resid"] > b["ux_retention_resid"] else b
                rejected = b if chosen is a else a
                ok += int(chosen["_s"] > rejected["_s"])
    return ok / n if n else float("nan")


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

def build_frame() -> tuple[pd.DataFrame, pd.DataFrame]:
    turns = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = turns[turns.source_set == "primary"].copy()
    anc = pd.read_csv(HERE / "outputs/gold/human_anchor.csv")

    # conversation-level Y
    ycols = [
        "ux_retention", "ux_retention_resid", "good_moment_human",
        "delta_credibility", "delta_trust", "delta_manipulation",
        "delta_helpfulness", "recall_memory", "recall_trust_shift",
        "credibility", "trust", "manipulation",
    ]
    ytab = anc[["conversation_id"] + ycols].copy()

    # no-ad: U = 0, good = 1 (definition of the control)
    noad_ids = prim.loc[prim.condition == "no_ads", "conversation_id"].unique()
    noad = pd.DataFrame({"conversation_id": noad_ids})
    for c in ycols:
        noad[c] = 0.0
    noad["good_moment_human"] = 1
    ytab = pd.concat([ytab, noad], ignore_index=True)

    df = prim.merge(ytab, on="conversation_id", how="left")
    assert df.ux_retention_resid.notna().all(), "turns without Y"

    # trajectory conversation stats (utterance source)
    traj = pd.read_csv(HERE.parents[1] / "analysis/trajectories/outputs/conversations.csv")
    traj = traj[traj.genre_source == "utterance"][
        ["conversation_id", "n_shift", "diversity", "entropy_nats",
         "mean_js_divergence", "max_persistence"]
    ]
    df = df.merge(traj, on="conversation_id", how="left")

    # 13-way posteriors from utterance Gold
    utt = pd.read_csv(HERE.parents[1] / "analysis/trajectories/outputs/utterances.csv")
    utt = utt[utt.genre_source == "utterance"]
    pcols = [c for c in utt.columns if c.startswith("p_")]
    df = df.merge(
        utt[["conversation_id", "turn"] + pcols],
        on=["conversation_id", "turn"], how="left",
    )

    df["turn_feat"] = df.turn.clip(upper=8) / 8.0
    df["log_len"] = np.log1p(pd.to_numeric(df.msg_len, errors="coerce").fillna(0))
    df["log_lat"] = np.log1p(pd.to_numeric(df.time_to_reply_ms, errors="coerce").fillna(0))
    df["fit"] = pd.to_numeric(df.fit_score, errors="coerce").fillna(0.0)
    df["p_purch"] = pd.to_numeric(df.p_purchasable, errors="coerce").fillna(0.0)
    for c in ["n_shift", "diversity", "entropy_nats", "mean_js_divergence", "max_persistence"] + pcols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)
    df["task_g"] = df.task_genre.fillna("unk")
    df["genre"] = df.genre_utterance.fillna("unk")
    df.to_csv(OUT / "turns_labelled.csv", index=False)
    print("labelled turns", df.shape, "people", df.participant_key.nunique(),
          "ad-turn rows", int(df.is_ad_turn.sum()))
    return df, anc


def make_X(df: pd.DataFrame, which: str, pca_mat: np.ndarray | None = None) -> np.ndarray:
    tab = [
        "turn_feat", "is_ad_turn", "ad_already_shown", "log_len", "log_lat",
        "fit", "p_purch", "n_shift", "diversity", "entropy_nats",
        "mean_js_divergence", "max_persistence",
    ]
    pcols = [c for c in df.columns if c.startswith("p_") and c != "p_purchasable"]
    parts = [df[tab + pcols].to_numpy(float)]
    if "task" in which:
        parts.append(pd.get_dummies(df.task_g, prefix="tg").to_numpy(float))
    if "genre" in which:
        parts.append(pd.get_dummies(df.genre, prefix="g").to_numpy(float))
    if pca_mat is not None and "pca" in which:
        parts.append(pca_mat)
    return np.hstack(parts)


def lopo_reg(X, y, groups, model="ridge"):
    pred = np.full(len(y), np.nan)
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(X, y, groups=groups):
        if model == "ridge":
            sc = StandardScaler()
            m = Ridge(alpha=50.0)
            m.fit(sc.fit_transform(X[tr]), y[tr])
            pred[te] = m.predict(sc.transform(X[te]))
        else:
            m = HistGradientBoostingRegressor(
                max_depth=3, max_iter=80, min_samples_leaf=20,
                l2_regularization=1.0, random_state=SEED,
            )
            m.fit(X[tr], y[tr])
            pred[te] = m.predict(X[te])
    return pred


def lopo_clf(X, y, groups):
    pred = np.full(len(y), np.nan)
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(X, y, groups=groups):
        if len(np.unique(y[tr])) < 2:
            pred[te] = y[tr].mean()
            continue
        m = HistGradientBoostingClassifier(
            max_depth=3, max_iter=80, min_samples_leaf=20,
            l2_regularization=1.0, random_state=SEED,
        )
        m.fit(X[tr], y[tr])
        pred[te] = m.predict_proba(X[te])[:, 1]
    return pred


def eval_on_ads(df: pd.DataFrame, anc: pd.DataFrame, pred_turn: np.ndarray, name: str) -> dict:
    """Collapse to the 216 ad turns of the same conversations as the anchor."""
    tmp = df.assign(_pred=pred_turn)
    ad = tmp[tmp.is_ad_turn == 1][["conversation_id", "_pred"]]
    ev = anc.merge(ad, on="conversation_id", how="left")
    s = ev._pred.to_numpy(float)
    y = ev.ux_retention_resid.to_numpy(float)
    yb = ev.good_moment_human.to_numpy(int)
    pack = {
        "name": name,
        "n": int(ev._pred.notna().sum()),
        "spearman_U": round(spearman(s, y), 4),
        "auroc_good": round(auroc(yb, s), 4),
        "pairwise_acc": round(pairwise_acc(ev, s), 4),
    }
    print(pack)
    return pack


def embed_bge(texts: list[str], cache: Path) -> np.ndarray:
    if cache.exists():
        arr = np.load(cache)
        if arr.shape[0] == len(texts):
            print("bge cache", arr.shape)
            return arr
    from transformers import AutoModel, AutoTokenizer
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
    model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5").to(device).eval()
    outs = []
    with torch.no_grad():
        for i in range(0, len(texts), 32):
            enc = tok(list(texts[i:i + 32]), padding=True, truncation=True,
                      max_length=384, return_tensors="pt")
            enc = {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask")}
            h = model(**enc).last_hidden_state
            mask = enc["attention_mask"].unsqueeze(-1)
            vec = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
            outs.append(vec.cpu().numpy())
    arr = np.concatenate(outs)
    np.save(cache, arr)
    print("bge wrote", arr.shape)
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    return arr


def main():
    t0 = time.time()
    df, anc = build_frame()
    groups = df.participant_key.to_numpy()
    y = df.ux_retention_resid.to_numpy(float)
    yb = df.good_moment_human.to_numpy(int)
    results = []

    # sanity: turn-only on the 216 ads (must recover ~0.17)
    turn_only = df.turn_feat.to_numpy()
    results.append(eval_on_ads(df, anc, turn_only, "baseline_turn_on_1080_rows"))

    print("embedding 1080 prefixes with bge-small (mean pool)…")
    E = embed_bge(df.prefix_text.fillna("").tolist(), OUT / "emb_bge_1080.npy")
    pca = PCA(n_components=32, random_state=SEED).fit_transform(StandardScaler().fit_transform(E))

    setups = [
        ("ridge_tab", "ridge", "tab"),
        ("ridge_tab_genre", "ridge", "tab+genre"),
        ("ridge_tab_task_genre", "ridge", "tab+task+genre"),
        ("ridge_pca32", "ridge", "pca"),
        ("ridge_tab_pca", "ridge", "tab+pca"),
        ("ridge_tab_genre_pca", "ridge", "tab+genre+pca"),
        ("hgb_tab", "hgb", "tab"),
        ("hgb_tab_genre", "hgb", "tab+genre"),
        ("hgb_tab_pca", "hgb", "tab+pca"),
        ("hgb_tab_genre_pca", "hgb", "tab+genre+pca"),
    ]
    cache_X = {}
    for name, algo, which in setups:
        key = which
        if key not in cache_X:
            cache_X[key] = make_X(df, which, pca)
            print(f"X[{which}] {cache_X[key].shape}")
        X = cache_X[key]
        print("train", name)
        pred = lopo_reg(X, y, groups, model=algo)
        pack = eval_on_ads(df, anc, pred, name)
        pack["X_dim"] = int(X.shape[1])
        pack["algo"] = algo
        results.append(pack)
        json.dump(results, open(OUT / "results.json", "w"), indent=2)

    # classifier on good_moment with best-looking feature set
    print("HGB classifier tab+genre+pca")
    X = cache_X["tab+genre+pca"]
    pred_c = lopo_clf(X, yb, groups)
    pack = eval_on_ads(df, anc, pred_c, "hgbclf_tab_genre_pca")
    results.append(pack)

    # multi-task ridge: predict 3 deltas, score = (cred + trust - manip)/3
    print("multitask ridge on 3 deltas")
    X = cache_X["tab+genre+pca"]
    d1 = lopo_reg(X, df.delta_credibility.to_numpy(float), groups, "ridge")
    d2 = lopo_reg(X, df.delta_trust.to_numpy(float), groups, "ridge")
    d3 = lopo_reg(X, df.delta_manipulation.to_numpy(float), groups, "ridge")
    uhat = (d1 + d2 - d3) / 3.0
    results.append(eval_on_ads(df, anc, uhat, "multitask_ridge_tab_genre_pca"))

    # train on ad-turns only (216) with tab — should be close to turn baseline
    ad_mask = df.is_ad_turn == 1
    print("ridge tab, train on 216 ad-turns only")
    Xad = cache_X["tab"][ad_mask.to_numpy()]
    yad = y[ad_mask.to_numpy()]
    gad = groups[ad_mask.to_numpy()]
    pred_ad = lopo_reg(Xad, yad, gad, "ridge")
    # map back
    full = np.full(len(df), np.nan)
    full[ad_mask.to_numpy()] = pred_ad
    results.append(eval_on_ads(df, anc, full, "ridge_tab_adturns_only"))

    json.dump(results, open(OUT / "results.json", "w"), indent=2)
    # table
    lines = ["# Full-data LOPO results (eval = 216 ad conversations)", "",
             "| model | Spearman U | AUROC | pairwise |",
             "|---|---:|---:|---:|"]
    for r in results:
        lines.append(f"| {r['name']} | {r.get('spearman_U','')} | {r.get('auroc_good','')} | {r.get('pairwise_acc','')} |")
    (OUT / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print(f"done in {(time.time()-t0)/60:.1f} min")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
