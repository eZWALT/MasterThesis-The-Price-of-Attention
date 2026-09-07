#!/usr/bin/env python3
"""Fine-tune conversation transformers with a fused behavioural head.

5-fold by person (LOPO is too slow for backprop). Score = turn + mix * z(oof).
Models: ThradBERT (in-domain), DistilBERT-MNLI, Qwen3-0.6B last-token LoRA.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import GroupKFold
from torch.utils.data import DataLoader, Dataset

from features_behaviour import OUT, build_ads_frame, feat_matrix
from train_campaign import GOLD, eval_scores

HERE = Path(__file__).resolve().parent
SEED = 13
MAX_LEN = 256


class PrefixDS(Dataset):
    def __init__(self, texts, tabs, y, pairs_idx=None):
        self.texts = list(texts)
        self.tabs = np.asarray(tabs, np.float32)
        self.y = np.asarray(y, np.float32)

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, i):
        return i


class FusionHead(nn.Module):
    def __init__(self, hidden, tab_dim, n_out=8):
        super().__init__()
        self.tab = nn.Sequential(nn.Linear(tab_dim, 64), nn.ReLU(), nn.Dropout(0.2))
        self.head = nn.Sequential(
            nn.Linear(hidden + 64, 128), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(128, n_out),
        )

    def forward(self, h, tab):
        return self.head(torch.cat([h, self.tab(tab)], dim=-1))


def tokenize_batch(tok, texts, device):
    enc = tok(
        [str(t)[:2000] for t in texts],
        padding=True, truncation=True, max_length=MAX_LEN, return_tensors="pt",
    )
    return {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask")}


def pooled_hidden(model, enc, kind):
    if kind == "encoder":
        out = model(**enc)
        h = out.last_hidden_state
        cls = h[:, 0]
    else:
        out = model(**enc, output_hidden_states=True)
        h = out.hidden_states[-1]
        last = enc["attention_mask"].sum(1) - 1
        cls = h[torch.arange(h.size(0), device=h.device), last]
    return cls.float()


def run_encoder_fold(hub, kind, ads, tab, y, groups, device, epochs=6, lr=2e-5):
    from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(hub, trust_remote_code=True, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token or tok.unk_token
    gkf = GroupKFold(5)
    oof = np.full(len(y), np.nan)
    texts = ads.prefix_text.fillna("").tolist()
    # extra heads: U + 3 deltas
    Y = np.column_stack([
        y,
        ads.delta_credibility.to_numpy(float),
        ads.delta_trust.to_numpy(float),
        -ads.delta_manipulation.to_numpy(float),
        ads.delta_convincingness.to_numpy(float),
        ads.delta_helpfulness.to_numpy(float),
        ads.log_lat.to_numpy(float) * 0,  # placeholder alignment
        ads.good_moment_human.to_numpy(float),
    ]).astype(np.float32)

    for f, (tr, te) in enumerate(gkf.split(tab, y, groups=groups)):
        print(f"  fold {f} ntr={len(tr)}", flush=True)
        if kind == "encoder":
            enc_model = AutoModel.from_pretrained(hub, trust_remote_code=True).to(device)
        else:
            enc_model = AutoModelForCausalLM.from_pretrained(
                hub, torch_dtype=torch.bfloat16, trust_remote_code=True,
            ).to(device)
        hidden = enc_model.config.hidden_size
        head = FusionHead(hidden, tab.shape[1], n_out=Y.shape[1]).to(device)
        layers = None
        if hasattr(enc_model, "encoder") and hasattr(enc_model.encoder, "layer"):
            layers = list(enc_model.encoder.layer)
        elif hasattr(enc_model, "distilbert") and hasattr(enc_model.distilbert, "transformer"):
            layers = list(enc_model.distilbert.transformer.layer)
        if layers and len(layers) > 2:
            for p in layers[:-2]:
                for q in p.parameters():
                    q.requires_grad = False
        opt = torch.optim.AdamW(
            [p for p in list(enc_model.parameters()) + list(head.parameters()) if p.requires_grad],
            lr=lr, weight_decay=0.01,
        )
        enc_model.train(); head.train()
        idx = np.array(tr)
        rng = np.random.RandomState(SEED + f)
        for ep in range(epochs):
            rng.shuffle(idx)
            total = 0.0; n = 0
            for i0 in range(0, len(idx), 8):
                bi = idx[i0:i0 + 8]
                enc = tokenize_batch(tok, [texts[i] for i in bi], device)
                h = pooled_hidden(enc_model, enc, kind)
                pred = head(h, torch.as_tensor(tab[bi], device=device, dtype=torch.float32))
                tgt = torch.tensor(Y[bi], device=device)
                # z-score targets per batch-free: just MSE after centering train
                loss_mse = ((pred - tgt) ** 2).mean()
                # pairwise on U (col 0) within batch
                u = pred[:, 0]
                yu = tgt[:, 0]
                loss_p = torch.tensor(0.0, device=device)
                npair = 0
                for a in range(len(bi)):
                    for b in range(a + 1, len(bi)):
                        if yu[a] == yu[b]:
                            continue
                        # want u[better] > u[worse]
                        if yu[a] > yu[b]:
                            loss_p = loss_p + torch.nn.functional.softplus(u[b] - u[a])
                        else:
                            loss_p = loss_p + torch.nn.functional.softplus(u[a] - u[b])
                        npair += 1
                if npair:
                    loss_p = loss_p / npair
                loss = loss_mse + 0.5 * loss_p
                opt.zero_grad(); loss.backward()
                torch.nn.utils.clip_grad_norm_(list(enc_model.parameters()) + list(head.parameters()), 1.0)
                opt.step()
                total += float(loss.item()); n += 1
            print(f"    ep {ep} loss {total/max(n,1):.4f}", flush=True)

        enc_model.eval(); head.eval()
        with torch.no_grad():
            scores = []
            for i0 in range(0, len(te), 8):
                bi = te[i0:i0 + 8]
                enc = tokenize_batch(tok, [texts[i] for i in bi], device)
                h = pooled_hidden(enc_model, enc, kind)
                pred = head(h, torch.as_tensor(tab[bi], device=device, dtype=torch.float32))
                scores.extend(pred[:, 0].cpu().numpy().tolist())
            oof[te] = scores
        del enc_model, head
        torch.cuda.empty_cache()
    return oof


def run_qwen_lora(ads, tab, y, groups, device, epochs=4):
    """Proper pairwise+MSE LoRA on Qwen3-0.6B, all pairs in fold, turn+tab in head."""
    try:
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError:
        print("peft missing")
        return None
    from transformers import AutoModelForCausalLM, AutoTokenizer

    hub = "Qwen/Qwen3-0.6B"
    tok = AutoTokenizer.from_pretrained(hub, trust_remote_code=True, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    gkf = GroupKFold(5)
    oof = np.full(len(y), np.nan)
    texts = ads.prefix_text.fillna("").tolist()
    prompt = (
        "Score whether NOW is a good moment to mention one relevant product "
        "in this shopping chat. Higher = better for trust and usefulness.\n"
    )
    for f, (tr, te) in enumerate(gkf.split(tab, y, groups=groups)):
        print(f"  qwen06 fold {f}", flush=True)
        base = AutoModelForCausalLM.from_pretrained(
            hub, torch_dtype=torch.bfloat16, trust_remote_code=True,
        ).to(device)
        lora = LoraConfig(
            r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        )
        model = get_peft_model(base, lora)
        hidden = base.config.hidden_size
        head = FusionHead(hidden, tab.shape[1], n_out=1).to(device)
        opt = torch.optim.AdamW(
            list(model.parameters()) + list(head.parameters()), lr=1e-4, weight_decay=0.01,
        )
        tr_set = set(tr.tolist())
        # all pairs among train
        yu = y
        pairs = []
        # group train by person for pairs
        pk = ads.participant_key.to_numpy()
        for p in np.unique(pk[tr]):
            idx = [i for i in tr if pk[i] == p]
            for a in range(len(idx)):
                for b in range(a + 1, len(idx)):
                    i, j = idx[a], idx[b]
                    if yu[i] == yu[j]:
                        continue
                    pairs.append((i, j) if yu[i] > yu[j] else (j, i))
        rng = np.random.RandomState(SEED + f)
        model.train(); head.train()
        for ep in range(epochs):
            rng.shuffle(pairs)
            total = 0.0
            # use ALL pairs, plus a MSE pass over train rows
            for nseen, (i, j) in enumerate(pairs):
                def fwd(ix):
                    enc = tokenize_batch(tok, [prompt + texts[ix]], device)
                    h = pooled_hidden(model, enc, "causal")
                    return head(h, torch.as_tensor(tab[ix:ix + 1], device=device, dtype=torch.float32)).squeeze()
                sc = fwd(i); sr = fwd(j)
                loss = torch.nn.functional.softplus(sr - sc)
                # MSE on chosen
                loss = loss + 0.15 * (sc - float(yu[i])) ** 2
                opt.zero_grad(); loss.backward(); opt.step()
                total += float(loss.item())
            print(f"    ep {ep} pairloss {total/max(len(pairs),1):.4f} npairs={len(pairs)}", flush=True)
        model.eval(); head.eval()
        with torch.no_grad():
            for n, ix in enumerate(te):
                enc = tokenize_batch(tok, [prompt + texts[ix]], device)
                h = pooled_hidden(model, enc, "causal")
                oof[ix] = float(head(h, torch.as_tensor(tab[ix:ix + 1], device=device, dtype=torch.float32)).squeeze().cpu())
        del model, base, head
        torch.cuda.empty_cache()
    return oof


def main():
    t0 = time.time()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("device", device, flush=True)
    ads = build_ads_frame()
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    y = ads.ux_retention_resid.to_numpy(float)
    g = ads.participant_key.to_numpy()
    turn = ads.turn_feat.to_numpy(float)
    tab, cols = feat_matrix(ads, "no_ocean")
    # drop turn from tab so the head learns residual (we add turn back)
    # keep it actually — fusion can use it; we still lock turn at the end
    print("tab", tab.shape, cols[:8], flush=True)
    results = []

    specs = [
        ("thradbert", "Thrad/thrad-bert-conversation-classifier", "encoder", 3e-5, 8),
        ("distil_mnli", "typeform/distilbert-base-uncased-mnli", "encoder", 3e-5, 8),
        ("minilm", "sentence-transformers/all-MiniLM-L6-v2", "encoder", 3e-5, 8),
    ]
    for name, hub, kind, lr, ep in specs:
        print("====", name, flush=True)
        try:
            oof = run_encoder_fold(hub, kind, ads, tab, y, g, device, epochs=ep, lr=lr)
        except Exception as exc:
            import traceback
            print("FAIL", name, type(exc).__name__, exc, flush=True)
            traceback.print_exc()
            results.append({"name": name, "error": f"{type(exc).__name__}: {exc}"})
            json.dump(results, open(OUT / "tfm.json", "w"), indent=2)
            continue
        np.save(OUT / f"pred_tfm_{name}.npy", oof)
        for mix in (0.2, 0.35, 0.5, 1.0):
            # raw oof and locked-turn blend
            pack = eval_scores(f"tfm_{name}_raw", oof, anc, pairs)
            results.append(pack)
            z = (oof - np.nanmean(oof)) / (np.nanstd(oof) + 1e-8)
            s = turn + mix * z
            pack = eval_scores(f"tfm_{name}_turn_m{mix}", s, anc, pairs)
            results.append(pack)
        json.dump(results, open(OUT / "tfm.json", "w"), indent=2)

    print("==== qwen3-0.6B LoRA proper", flush=True)
    try:
        oof = run_qwen_lora(ads, tab, y, g, device, epochs=4)
        if oof is not None:
            np.save(OUT / "pred_tfm_qwen06_lora.npy", oof)
            pack = eval_scores("tfm_qwen06_lora_raw", oof, anc, pairs)
            results.append(pack)
            z = (oof - np.nanmean(oof)) / (np.nanstd(oof) + 1e-8)
            for mix in (0.2, 0.35, 0.5):
                results.append(eval_scores(f"tfm_qwen06_lora_turn_m{mix}", turn + mix * z, anc, pairs))
    except Exception as exc:
        print("FAIL qwen06", type(exc).__name__, exc, flush=True)
        results.append({"name": "tfm_qwen06_lora", "error": f"{type(exc).__name__}: {exc}"})

    json.dump(results, open(OUT / "tfm.json", "w"), indent=2)
    rows = [r for r in results if "spearman_U" in r]
    rows.sort(key=lambda r: -(r["spearman_U"] or -9))
    lines = ["# Transformer fusion (5-fold person)", "",
             "| model | Spearman | same-t | pair | AUROC |",
             "|---|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['spearman_U']} | {r.get('pairwise_same_timing')} | "
            f"{r.get('pairwise')} | {r.get('auroc_good')} |"
        )
    (OUT / "TFM.md").write_text("\n".join(lines) + "\n")
    print((OUT / "TFM.md").read_text())
    print(f"done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
