#!/usr/bin/env python3
"""Serve-time behavioural features from the conversation itself.

Nothing post-treatment (no Likert, no recall, no λ). Everything here is
observable at the user turn where π decides.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
GOLD = HERE / "outputs" / "gold"
OUT = HERE / "outputs" / "experiments" / "full"

PRODUCT = re.compile(
    r"\b(buy|bought|price|cheap|budget|recommend|recommendat|option|options|"
    r"product|laptop|chair|desk|gift|order|brand|model|vs|versus|compare|"
    r"which one|should i get|looking for|need a|want a)\b",
    re.I,
)
MONEY = re.compile(r"(\$|€|£|\b\d+\s?(usd|eur|gbp|dollars?|euros?)\b|\bunder\s+\d+)", re.I)
FIRST = re.compile(r"\b(i|i'm|i've|me|my|mine)\b", re.I)
SECOND = re.compile(r"\b(you|your|you're)\b", re.I)
HEDGE = re.compile(r"\b(maybe|not sure|idk|don't know|confused|stuck|help|unsure|kinda|perhaps)\b", re.I)
READY = re.compile(r"\b(let's|go with|i'll take|decide|decided|final|get this|buy this)\b", re.I)

MNLI_HYP = [
    "The user is ready to choose or buy a product.",
    "The user is frustrated, confused, or stuck.",
    "The user is asking for concrete product recommendations.",
    "The conversation is only just getting started.",
    "The user is thinking out loud and not ready to decide.",
    "The user already got a useful answer and is following up.",
    "This would be a natural moment to mention a relevant product.",
]


def lexical(text: str) -> dict:
    t = str(text or "")
    words = re.findall(r"[A-Za-z']+", t)
    n = max(len(words), 1)
    return {
        "lex_chars": len(t),
        "lex_words": len(words),
        "lex_qmark": t.count("?"),
        "lex_excl": t.count("!"),
        "lex_q_start": float(t.lstrip().startswith(("what", "which", "how", "why", "should", "can", "is ", "are "))),
        "lex_product": len(PRODUCT.findall(t)),
        "lex_money": len(MONEY.findall(t)),
        "lex_i": len(FIRST.findall(t)) / n,
        "lex_you": len(SECOND.findall(t)) / n,
        "lex_hedge": len(HEDGE.findall(t)) / n,
        "lex_ready": len(READY.findall(t)),
        "lex_ttr": len(set(w.lower() for w in words)) / n,
        "lex_avg_word": float(np.mean([len(w) for w in words])) if words else 0.0,
    }


def mnli_entail(texts: list[str], cache: Path) -> np.ndarray:
    """(n, n_hyp) entailment probabilities. Cached."""
    if cache.exists():
        arr = np.load(cache)
        if arr.shape == (len(texts), len(MNLI_HYP)):
            return arr
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    hub = "typeform/distilbert-base-uncased-mnli"
    tok = AutoTokenizer.from_pretrained(hub)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModelForSequenceClassification.from_pretrained(hub).to(device).eval()
    # entailment index
    id2 = {int(k) if str(k).isdigit() else k: v for k, v in model.config.id2label.items()}
    # config may be {0: 'CONTRADICTION', ...}
    ent_idx = None
    for i, lab in model.config.id2label.items():
        if str(lab).lower().startswith("entail"):
            ent_idx = int(i)
    if ent_idx is None:
        ent_idx = 2
    outs = np.zeros((len(texts), len(MNLI_HYP)), dtype=np.float32)
    with torch.no_grad():
        for j, hyp in enumerate(MNLI_HYP):
            for i in range(0, len(texts), 16):
                batch = [str(t)[:1200] for t in texts[i:i + 16]]
                enc = tok(batch, [hyp] * len(batch), padding=True, truncation=True,
                          max_length=256, return_tensors="pt")
                enc = {k: v.to(device) for k, v in enc.items()}
                prob = model(**enc).logits.softmax(-1)[:, ent_idx].cpu().numpy()
                outs[i:i + len(batch), j] = prob
            print(f"  mnli {j+1}/{len(MNLI_HYP)}", flush=True)
    np.save(cache, outs)
    del model
    if device == "cuda":
        import torch
        torch.cuda.empty_cache()
    return outs


ASST_REC = re.compile(
    r"\b(recommend|consider|try|option|here are|you could|you might|i suggest)\b",
    re.I,
)


def last_assistant_features(prim: pd.DataFrame) -> pd.DataFrame:
    """Features of the assistant message the user just read (serve-time)."""
    recs = []
    for cid, g in prim.sort_values("turn").groupby("conversation_id", sort=False):
        prev = ""
        for r in g.itertuples():
            t = str(prev or "")
            words = re.findall(r"[A-Za-z']+", t)
            recs.append({
                "conversation_id": cid,
                "turn": int(r.turn),
                "asst_chars": float(len(t)),
                "asst_qmark": float(t.count("?")),
                "asst_list": float(bool(re.search(r"(^|\n)\s*([-*]|\d+\.)\s", t))),
                "asst_rec": float(len(ASST_REC.findall(t))),
                "user_asst_ratio": float(len(str(getattr(r, "user_text", "") or ""))) / (len(t) + 1.0),
            })
            prev = getattr(r, "reply_after", "") or ""
    return pd.DataFrame(recs)


def prefix_user_agg(prim: pd.DataFrame) -> pd.DataFrame:
    """Running lexical stats over user turns ≤ current (no future)."""
    recs = []
    for cid, g in prim.sort_values("turn").groupby("conversation_id", sort=False):
        q_start, qmark, hedge, prod, chars = [], [], [], [], []
        for r in g.itertuples():
            lex = lexical(getattr(r, "user_text", "") or "")
            q_start.append(lex["lex_q_start"])
            qmark.append(lex["lex_qmark"])
            hedge.append(lex["lex_hedge"])
            prod.append(lex["lex_product"])
            chars.append(lex["lex_chars"])
            recs.append({
                "conversation_id": cid,
                "turn": int(r.turn),
                "pre_q_rate": float(np.mean(q_start)),
                "pre_qmark": float(np.sum(qmark)),
                "pre_hedge": float(np.mean(hedge)),
                "pre_prod": float(np.sum(prod)),
                "pre_chars": float(np.mean(chars)),
            })
    return pd.DataFrame(recs)


def running_from_turns(prim: pd.DataFrame) -> pd.DataFrame:
    recs = []
    for cid, g in prim.sort_values("turn").groupby("conversation_id", sort=False):
        lats, lens = [], []
        for r in g.itertuples():
            lat = float(getattr(r, "time_to_reply_ms", 0) or 0)
            ln = float(getattr(r, "msg_len", 0) or 0)
            lats.append(lat)
            lens.append(ln)
            slope_lat = float(np.polyfit(range(len(lats)), lats, 1)[0]) if len(lats) >= 2 else 0.0
            slope_len = float(np.polyfit(range(len(lens)), lens, 1)[0]) if len(lens) >= 2 else 0.0
            recs.append({
                "conversation_id": cid,
                "turn": int(r.turn),
                "bhv_mean_len": float(np.mean(lens)),
                "run_lat_slope": slope_lat,
                "run_len_slope": slope_len,
                "lat_vs_run": lat / (np.mean(lats) + 1.0),
            })
    return pd.DataFrame(recs)


def build_ads_frame() -> pd.DataFrame:
    from train_campaign import ads_view, collect_ocean, prefix_features

    turns = pd.read_csv(HERE / "outputs/silver/turns.csv")
    prim = turns[turns.source_set == "primary"].copy()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    ad_idx = ads_view(prim, anc)
    ads = prim.iloc[ad_idx].reset_index(drop=True)
    assert list(ads.conversation_id) == list(anc.conversation_id)

    utt = pd.read_csv(HERE.parents[1] / "analysis/trajectories/outputs/utterances.csv")
    utt = utt[utt.genre_source == "utterance"]
    pref = prefix_features(utt)
    ads = ads.merge(pref, on=["conversation_id", "turn"], how="left")
    ads = ads.merge(running_from_turns(prim), on=["conversation_id", "turn"], how="left")
    ads = ads.merge(last_assistant_features(prim), on=["conversation_id", "turn"], how="left")
    ads = ads.merge(prefix_user_agg(prim), on=["conversation_id", "turn"], how="left")
    ocean = collect_ocean()
    ads = ads.merge(ocean, on="experiment_id", how="left")

    lex = pd.DataFrame([lexical(t) for t in ads.user_text.fillna("")])
    ads = pd.concat([ads.reset_index(drop=True), lex], axis=1)

    # MNLI conversation-state scores on the prefix
    print("MNLI conversation-state features…", flush=True)
    M = mnli_entail(ads.prefix_text.fillna("").tolist(), OUT / "feat_mnli_216.npy")
    for j, _ in enumerate(MNLI_HYP):
        ads[f"mnli_{j}"] = M[:, j]

    ads["turn_feat"] = ads.turn.clip(upper=8) / 8.0
    ads["log_lat"] = np.log1p(pd.to_numeric(ads.time_to_reply_ms, errors="coerce").fillna(0))
    ads["log_len"] = np.log1p(pd.to_numeric(ads.msg_len, errors="coerce").fillna(0))
    ads["fit"] = pd.to_numeric(ads.fit_score, errors="coerce").fillna(0.0)
    ads["n_cand"] = pd.to_numeric(ads.candidate_count, errors="coerce").fillna(0.0)
    ads["sess"] = pd.to_numeric(anc.session_position, errors="coerce").fillna(0).to_numpy()

    ads["log_asst"] = np.log1p(pd.to_numeric(ads.get("asst_chars"), errors="coerce").fillna(0))
    num_cols = [
        "turn_feat", "log_lat", "log_len", "fit", "n_cand", "sess",
        "bhv_mean_len", "run_lat_slope", "run_len_slope", "lat_vs_run",
        "run_mean_lat", "run_n_shift", "run_entropy", "run_last_js", "run_mean_js",
        "p_purch",
        "asst_chars", "asst_qmark", "asst_list", "asst_rec", "user_asst_ratio", "log_asst",
        "pre_q_rate", "pre_qmark", "pre_hedge", "pre_prod", "pre_chars",
    ]
    if "p_purchasable" in ads.columns:
        ads["p_purch"] = pd.to_numeric(ads.p_purchasable, errors="coerce").fillna(0)
    pcols = [c for c in ads.columns if c.startswith("p_") and c not in ("p_purchasable", "p_purch")]
    ocols = [c for c in ads.columns if c.startswith("ocean_")]
    lcols = [c for c in ads.columns if c.startswith("lex_")]
    mcols = [c for c in ads.columns if c.startswith("mnli_")]
    keep = num_cols + pcols + ocols + lcols + mcols
    for c in keep:
        if c in ads.columns:
            ads[c] = pd.to_numeric(ads[c], errors="coerce").fillna(0.0)
    # attach labels
    for c in ["ux_retention_resid", "ux_retention", "good_moment_human",
              "delta_credibility", "delta_trust", "delta_manipulation",
              "delta_helpfulness", "delta_relevance", "delta_neutrality",
              "delta_convincingness", "delta_notice_sponsored",
              "participant_key", "conversation_id", "timing"]:
        if c in anc.columns:
            ads[c] = anc[c].to_numpy()
    feat_cols = [c for c in keep if c in ads.columns]
    ads.attrs["feat_cols"] = feat_cols
    ads.to_csv(OUT / "ads_behaviour.csv", index=False)
    print("ads", ads.shape, "feat", len(feat_cols), flush=True)
    return ads


def feat_matrix(ads: pd.DataFrame, which: str = "all") -> np.ndarray:
    cols = list(ads.attrs.get("feat_cols") or [
        c for c in ads.columns
        if c.startswith(("lex_", "mnli_", "ocean_", "p_", "run_", "log_", "turn_feat", "fit", "n_cand", "sess", "lat_"))
    ])
    if which == "no_ocean":
        cols = [c for c in cols if not c.startswith("ocean_")]
    if which == "core":
        cols = [c for c in cols if c in (
            "turn_feat", "log_lat", "log_len", "fit", "lex_product", "lex_hedge",
            "lex_ready", "lex_qmark", "mnli_0", "mnli_1", "mnli_2", "mnli_6",
            "run_lat_slope", "lat_vs_run", "p_purch",
        ) or c.startswith("mnli_")]
    return ads[cols].to_numpy(float), cols


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ads = build_ads_frame()
    X, cols = feat_matrix(ads)
    print("X", X.shape)
    print("cols", cols)
