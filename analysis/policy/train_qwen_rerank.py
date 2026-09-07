#!/usr/bin/env python3
"""Qwen3-Reranker-4B yes/no scores as serve-time features, then residual add.

GPU 1 only. Run after train_tfm_fusion releases the card.
Also scores the finished Qwen3-0.6B LoRA OOF if the npy exists.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler
from transformers import AutoModelForCausalLM, AutoTokenizer

from features_behaviour import OUT, build_ads_frame
from train_campaign import GOLD, eval_scores

HERE = Path(__file__).resolve().parent
E14 = HERE / "outputs/experiments/emb_qwen3-14b.npy"
CACHE = OUT / "feat_qwen_rerank4b_216.npy"
HUB = "Qwen/Qwen3-Reranker-4B"
MIX, K, ALPHA = 0.15, 4, 10.0
SEED = 13
MAX_LEN = 1024

TASKS = [
    (
        "qwrr_good",
        "Judge whether NOW is a good moment to mention one relevant product "
        "in this shopping conversation. Yes means the user would find it "
        "helpful and not manipulative.",
        "Is this a good advertising moment?",
    ),
    (
        "qwrr_ready",
        "Judge whether the user is ready for a concrete product recommendation.",
        "Is the user ready for a recommendation?",
    ),
    (
        "qwrr_intrusive",
        "Judge whether mentioning a product now would feel intrusive or pushy.",
        "Would an ad feel intrusive here?",
    ),
]


def format_pair(instruction: str, query: str, doc: str) -> str:
    return (
        f"<Instruct>: {instruction}\n"
        f"<Query>: {query}\n"
        f"<Document>: {doc}"
    )


@torch.no_grad()
def score_reranker(texts: list[str]) -> np.ndarray:
    tok = AutoTokenizer.from_pretrained(HUB, trust_remote_code=True, padding_side="left")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        HUB, torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="cuda:0",
    ).eval()
    yes_id = tok.convert_tokens_to_ids("yes")
    no_id = tok.convert_tokens_to_ids("no")
    prefix = (
        "<|im_start|>system\n"
        "Judge whether the Document meets the requirements based on the Query "
        'and the Instruct provided. Note that the answer can only be "yes" or "no".'
        "<|im_end|>\n<|im_start|>user\n"
    )
    suffix = "<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"
    pre = tok.encode(prefix, add_special_tokens=False)
    suf = tok.encode(suffix, add_special_tokens=False)
    room = MAX_LEN - len(pre) - len(suf)
    out = np.zeros((len(texts), len(TASKS)), dtype=np.float32)
    for j, (_, inst, query) in enumerate(TASKS):
        for i in range(0, len(texts), 2):
            batch = []
            for t in texts[i:i + 2]:
                body = format_pair(inst, query, str(t)[:1800])
                ids = tok.encode(body, add_special_tokens=False, truncation=True, max_length=room)
                batch.append(pre + ids + suf)
            maxlen = max(len(x) for x in batch)
            pad_id = tok.pad_token_id
            input_ids = torch.full((len(batch), maxlen), pad_id, dtype=torch.long, device=model.device)
            attn = torch.zeros_like(input_ids)
            for r, ids in enumerate(batch):
                input_ids[r, -len(ids):] = torch.tensor(ids, device=model.device)
                attn[r, -len(ids):] = 1
            logits = model(input_ids=input_ids, attention_mask=attn).logits[:, -1, :]
            yes = logits[:, yes_id]
            no = logits[:, no_id]
            p_yes = torch.softmax(torch.stack([no, yes], dim=1), dim=1)[:, 1]
            out[i:i + len(batch), j] = p_yes.float().cpu().numpy()
        print(f"  rerank task {j+1}/{len(TASKS)}", flush=True)
    del model
    torch.cuda.empty_cache()
    return out


def oof_blend(E, extra, y, g, turn, mix=MIX):
    pred = np.zeros(len(y))
    for tr, te in LeaveOneGroupOut().split(E, y, groups=g):
        r = y[tr] - LinearRegression().fit(turn[tr], y[tr]).predict(turn[tr])
        scE = StandardScaler()
        pca = PCA(K, random_state=SEED)
        P = pca.fit_transform(scE.fit_transform(E[tr]))
        Pte = pca.transform(scE.transform(E[te]))
        sc = StandardScaler()
        Xtr = sc.fit_transform(np.hstack([P, extra[tr]]))
        Xte = sc.transform(np.hstack([Pte, extra[te]]))
        w = Ridge(ALPHA, fit_intercept=False).fit(Xtr, r - r.mean()).coef_
        pred[te] = Xte @ w
    z = (pred - pred.mean()) / (pred.std() + 1e-8)
    return turn.ravel() + mix * z


def main():
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads[["turn_feat"]].to_numpy(float)
    E = np.load(E14)
    results = []

    def rec(name, s):
        pack = eval_scores(name, s, anc, pairs)
        results.append(pack)
        print(name, pack["spearman_U"], "same-t", pack.get("pairwise_same_timing"),
              "within", pack.get("spearman_within"), flush=True)

    # LoRA OOF if present
    lora_path = OUT / "pred_tfm_qwen06_lora.npy"
    if lora_path.exists():
        oof = np.load(lora_path)
        rec("tfm_qwen06_lora_raw", oof)
        z = (oof - np.nanmean(oof)) / (np.nanstd(oof) + 1e-8)
        for mix in (0.15, 0.25, 0.35):
            rec(f"tfm_qwen06_lora_m{mix}", turn.ravel() + mix * z)
        extra = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
        extra2 = np.hstack([extra, z.reshape(-1, 1)])
        rec("same_t+lora_m0.15", oof_blend(E, extra2, y, g, turn))

    texts = ads.prefix_text.fillna("").tolist()
    if CACHE.exists() and np.load(CACHE).shape == (len(texts), len(TASKS)):
        Z = np.load(CACHE)
        print("loaded", CACHE, flush=True)
    else:
        print("scoring Qwen3-Reranker-4B…", flush=True)
        Z = score_reranker(texts)
        np.save(CACHE, Z)
        print("saved", CACHE, Z.shape, flush=True)

    names = [t[0] for t in TASKS]
    for j, n in enumerate(names):
        ads[n] = Z[:, j]
    ads["qwrr_net"] = ads.qwrr_good - ads.qwrr_intrusive

    extra0 = ads[["log_lat", "ocean_O", "lex_q_start"]].to_numpy(float)
    rec("base_same_t", oof_blend(E, extra0, y, g, turn))
    from scipy.stats import spearmanr
    rU = y - LinearRegression().fit(turn, y).predict(turn)
    for n in names + ["qwrr_net"]:
        print(f"  resid ρ {n} {spearmanr(ads[n], rU).statistic:+.3f}", flush=True)
        extra = np.hstack([extra0, ads[[n]].to_numpy(float)])
        rec(f"same_t+{n}", oof_blend(E, extra, y, g, turn))
    extra = np.hstack([extra0, Z])
    rec("same_t+qwrr_all3", oof_blend(E, extra, y, g, turn))

    json.dump(results, open(OUT / "qwen_rerank.json", "w"), indent=2)
    rows = sorted(results, key=lambda r: (-(r["spearman_U"] or -9), -(r.get("pairwise_same_timing") or 0)))
    lines = [
        "# Qwen3-Reranker-4B features + LoRA OOF",
        "",
        "| model | Spearman | same-t | pair | within | AUROC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('spearman_within')} | {r.get('auroc_good')} |"
        )
    (OUT / "QWEN_RERANK.md").write_text("\n".join(lines) + "\n")
    print((OUT / "QWEN_RERANK.md").read_text())


if __name__ == "__main__":
    main()
