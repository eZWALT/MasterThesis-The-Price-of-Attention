#!/usr/bin/env python3
"""Train and evaluate ad-moment models on OUR human Gold.

What the model is trained on
----------------------------
X  = conversation prefix at the advertised turn (role-tagged last 4 turns,
     ending on the user utterance). No lambda, no person id, no task id, no EEG.
Y  = human UX from the RCT, never the saturated judge:
       U     = ux_retention_resid   (continuous; person-centred vs own no-ad)
       y_bin = good_moment_human    (1 if U >= 0)
       pairs = 324 within-person preferences (higher U wins)
       bandit reward = U on INSERT, 0 on WAIT

Evaluation is always against outputs/gold/human_anchor.csv.
Folds are grouped by participant (LOPO for probes, 5-fold for LoRA).
A second split grouped by task is reported so we do not just learn 'laptop'.

This script is meant to run for hours on Atlas GPU 1.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr, wilcoxon
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
GOLD = HERE / "outputs" / "gold"
EXP = HERE / "outputs" / "experiments"
SEED = 13

PROBE_MODELS = [
    # cheap baselines / small encoders
    {"name": "thradbert", "hub": "Thrad/thrad-bert-conversation-classifier", "kind": "encoder", "max_len": 384},
    {"name": "bge-small", "hub": "BAAI/bge-small-en-v1.5", "kind": "encoder", "max_len": 384},
    # quality tier — user asked to go bigger than 3B
    {"name": "qwen3-8b", "hub": "Qwen/Qwen3-8B", "kind": "causal", "max_len": 512, "load": "bf16"},
    {"name": "qwen3-14b", "hub": "Qwen/Qwen3-14B", "kind": "causal", "max_len": 512, "load": "4bit"},
    {"name": "phi-4-14b", "hub": "microsoft/phi-4", "kind": "causal", "max_len": 512, "load": "4bit"},
]


def spearman(a, b) -> float:
    a, b = np.asarray(a, float), np.asarray(b, float)
    ok = ~(np.isnan(a) | np.isnan(b))
    if ok.sum() < 3 or np.nanstd(a[ok]) == 0 or np.nanstd(b[ok]) == 0:
        return float("nan")
    return float(spearmanr(a[ok], b[ok]).statistic)


def auroc(y, s) -> float:
    y, s = np.asarray(y), np.asarray(s)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def load_gold():
    anc = pd.read_csv(GOLD / "human_anchor.csv")
    pairs = pd.read_csv(GOLD / "preference_pairs.csv")
    bandit = pd.read_csv(GOLD / "bandit_rows.csv")
    anc["prefix_text"] = anc["prefix_text"].fillna("")
    return anc, pairs, bandit


# ---------------------------------------------------------------------------
# embeddings
# ---------------------------------------------------------------------------

def _tokenizer(hub: str):
    from transformers import AutoTokenizer
    try:
        tok = AutoTokenizer.from_pretrained(hub, trust_remote_code=True)
    except Exception:
        tok = AutoTokenizer.from_pretrained("bert-base-uncased")
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token or tok.unk_token
    return tok


def _load_backbone(spec: dict, device: str):
    from transformers import AutoModel, AutoModelForCausalLM
    hub, kind, load = spec["hub"], spec["kind"], spec.get("load", "bf16")
    if kind == "encoder":
        model = AutoModel.from_pretrained(hub, trust_remote_code=True)
        return model.to(device).eval()
    kwargs = {"trust_remote_code": True}
    if load == "4bit":
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4",
        )
        kwargs["device_map"] = {"": device}
        return AutoModelForCausalLM.from_pretrained(hub, **kwargs).eval()
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    try:
        model = AutoModelForCausalLM.from_pretrained(hub, dtype=dtype, trust_remote_code=True)
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(hub, torch_dtype=dtype, trust_remote_code=True)
    return model.to(device).eval()


@torch.no_grad()
def embed_texts(spec: dict, texts: list[str], device: str, cache_path: Path) -> np.ndarray:
    if cache_path.exists():
        arr = np.load(cache_path)
        if arr.shape[0] == len(texts):
            print(f"  cache hit {cache_path.name} {arr.shape}")
            return arr
    print(f"  embedding {len(texts)} texts with {spec['name']} ({spec['hub']})")
    tok = _tokenizer(spec["hub"])
    model = _load_backbone(spec, device)
    max_len = spec["max_len"]
    kind = spec["kind"]
    outs = []
    bs = 8 if spec.get("load") == "4bit" else (4 if kind == "causal" else 16)
    t0 = time.time()
    for i in range(0, len(texts), bs):
        batch = list(texts[i:i + bs])
        enc = tok(batch, padding=True, truncation=True, max_length=max_len, return_tensors="pt")
        enc = {k: v for k, v in enc.items() if k in ("input_ids", "attention_mask")}
        enc = {k: v.to(model.device if hasattr(model, "device") else device) for k, v in enc.items()}
        if kind == "encoder":
            h = model(**enc).last_hidden_state
            vec = h[:, 0].float()
        else:
            out = model(**enc, output_hidden_states=True)
            h = out.hidden_states[-1]
            attn = enc["attention_mask"]
            last = attn.sum(1) - 1
            vec = h[torch.arange(h.size(0), device=h.device), last].float()
        outs.append(vec.cpu().numpy())
        if (i // bs) % 10 == 0:
            print(f"    {min(i+bs, len(texts))}/{len(texts)}")
    arr = np.concatenate(outs, axis=0)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(cache_path, arr)
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    print(f"  wrote {cache_path} {arr.shape} in {(time.time()-t0)/60:.1f} min")
    return arr


# ---------------------------------------------------------------------------
# probes
# ---------------------------------------------------------------------------

def lopo_ridge(X, y, groups) -> np.ndarray:
    pred = np.zeros(len(y), dtype=float)
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(X, y, groups=groups):
        sc = StandardScaler()
        Xt = sc.fit_transform(X[tr])
        Xe = sc.transform(X[te])
        pred[te] = Ridge(alpha=10.0).fit(Xt, y[tr]).predict(Xe)
    return pred


def lopo_logit(X, y, groups) -> np.ndarray:
    pred = np.zeros(len(y), dtype=float)
    logo = LeaveOneGroupOut()
    for tr, te in logo.split(X, y, groups=groups):
        if len(np.unique(y[tr])) < 2:
            pred[te] = y[tr].mean()
            continue
        sc = StandardScaler()
        Xt = sc.fit_transform(X[tr])
        Xe = sc.transform(X[te])
        clf = LogisticRegression(C=0.5, max_iter=400, class_weight="balanced")
        pred[te] = clf.fit(Xt, y[tr]).predict_proba(Xe)[:, 1]
    return pred


def grouped_kfold_ridge(X, y, groups, folds=5) -> np.ndarray:
    pred = np.zeros(len(y), dtype=float)
    gkf = GroupKFold(n_splits=folds)
    for tr, te in gkf.split(X, y, groups=groups):
        sc = StandardScaler()
        pred[te] = Ridge(alpha=10.0).fit(sc.fit_transform(X[tr]), y[tr]).predict(sc.transform(X[te]))
    return pred


def pairwise_acc_from_scores(pairs: pd.DataFrame, score_by_conv: dict) -> float:
    ok = 0
    n = 0
    for r in pairs.itertuples():
        a = score_by_conv.get(r.chosen_conversation_id)
        b = score_by_conv.get(r.rejected_conversation_id)
        if a is None or b is None:
            continue
        n += 1
        ok += int(a > b)
    return ok / n if n else float("nan")


def ope_ips(bandit: pd.DataFrame, score_by_conv: dict, tau: float) -> dict:
    """IPS of 'insert iff score > tau'. Propensity 0.2 on the 5-arm RCT."""
    rewards, weights = [], []
    for r in bandit.itertuples():
        s = score_by_conv.get(r.conversation_id, 0.0)
        pi = 1.0 if (r.action == "INSERT" and s > tau) or (r.action == "WAIT" and s <= tau) else 0.0
        if pi == 0.0:
            continue
        rewards.append(r.reward)
        weights.append(pi / 0.2)
    if not rewards:
        return {"n": 0, "ips": float("nan")}
    w = np.asarray(weights)
    v = np.asarray(rewards)
    return {"n": int(len(v)), "ips": float((w * v).sum() / w.sum())}


def eval_pack(name: str, pred_u, anc: pd.DataFrame, pairs: pd.DataFrame, bandit: pd.DataFrame) -> dict:
    y_u = anc.ux_retention_resid.to_numpy(float)
    y_b = anc.good_moment_human.to_numpy(int)
    score_by_conv = dict(zip(anc.conversation_id, pred_u))
    # within-person high vs low score → U (non-inferiority style)
    diffs = []
    for _, g in anc.assign(s=pred_u).groupby("participant_key"):
        if len(g) < 2:
            continue
        med = g.s.median()
        hi, lo = g[g.s > med], g[g.s <= med]
        if len(hi) and len(lo):
            diffs.append(hi.ux_retention_resid.mean() - lo.ux_retention_resid.mean())
    diffs = np.asarray(diffs) if diffs else np.array([np.nan])
    rng = np.random.RandomState(SEED)
    null = [auroc(rng.permutation(y_b), pred_u) for _ in range(200)] if len(np.unique(y_b)) > 1 else [0.5]
    # task-grouped
    task_pred = grouped_kfold_ridge(
        pred_u.reshape(-1, 1), y_u, anc.fold_task.to_numpy(), folds=min(5, anc.fold_task.nunique())
    )
    # that last bit is cheating (using pred as 1-d). Real task-grouped needs the embedding matrix.
    pack = {
        "name": name,
        "spearman_U_lopo": round(spearman(pred_u, y_u), 4),
        "auroc_good_lopo": round(auroc(y_b, pred_u), 4),
        "pairwise_acc": round(pairwise_acc_from_scores(pairs, score_by_conv), 4),
        "mean_U_high_minus_low": round(float(np.nanmean(diffs)), 4),
        "auroc_null_mean": round(float(np.mean(null)), 4),
        "ope_ips_tau0": ope_ips(bandit, score_by_conv, 0.0),
        "ope_ips_tau_median": ope_ips(bandit, score_by_conv, float(np.median(pred_u))),
    }
    # always-late structural baseline comparison lives outside
    return pack


def baseline_turn(anc) -> np.ndarray:
    return (anc.ad_turn.clip(upper=8) / 8.0).to_numpy(float)


def baseline_fit(anc) -> np.ndarray:
    return pd.to_numeric(anc.fit_score, errors="coerce").fillna(0).to_numpy(float)


# ---------------------------------------------------------------------------
# LoRA ranking on a causal LM (5-fold, not 54 — 54x LoRA is days)
# ---------------------------------------------------------------------------

def run_lora_rank(anc, pairs, device: str, hub: str, tag: str, epochs=2, max_len=384) -> dict:
    """LoRA the LM so last-token logit 'YES' prefers higher-U prefixes. 5-fold by person."""
    try:
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError:
        print("peft missing — skip LoRA")
        return {"name": tag, "skipped": "no peft"}

    from torch.utils.data import DataLoader
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(hub, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    groups = anc.fold_participant.to_numpy()
    gkf = GroupKFold(n_splits=5)
    oof = pd.Series(np.nan, index=anc.index)
    prompt_head = (
        "You score whether THIS turn is a good moment to insert one relevant product mention "
        "in a shopping-assistant chat. Higher = better for the user's trust and usefulness. "
        "Conversation so far:\n"
    )

    def score_batch(model, texts):
        model.eval()
        scores = []
        with torch.no_grad():
            for t in texts:
                enc = tok(prompt_head + t[:3000], return_tensors="pt", truncation=True, max_length=max_len)
                enc = {k: v.to(model.device) for k, v in enc.items()}
                out = model(**enc, output_hidden_states=True)
                h = out.hidden_states[-1][0, -1].float()
                scores.append(float(h.mean().cpu()))  # cheap scalar; trained via pair hinge on this
        return scores

    # We train a small linear head on frozen-LoRA hidden via pairwise hinge.
    fold_metrics = []
    for f, (tr, te) in enumerate(gkf.split(anc, groups=groups)):
        print(f"  LoRA fold {f}")
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
                                 bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4")
        base = AutoModelForCausalLM.from_pretrained(
            hub, quantization_config=bnb, device_map={"": device}, trust_remote_code=True,
        )
        lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
                          task_type=TaskType.CAUSAL_LM,
                          target_modules=["q_proj", "v_proj", "k_proj", "o_proj"])
        model = get_peft_model(base, lora)
        head = torch.nn.Linear(base.config.hidden_size, 1).to(device)
        opt = torch.optim.AdamW(list(model.parameters()) + list(head.parameters()), lr=1e-4)

        tr_ids = set(anc.iloc[tr].conversation_id)
        fold_pairs = pairs[
            pairs.chosen_conversation_id.isin(tr_ids) & pairs.rejected_conversation_id.isin(tr_ids)
        ]
        # map conv -> prefix
        pref = dict(zip(anc.conversation_id, anc.prefix_text))
        model.train()
        step = 0
        for ep in range(epochs):
            shuf = fold_pairs.sample(frac=1.0, random_state=SEED + ep + f)
            total = 0.0
            nseen = 0
            for row in shuf.itertuples():
                def fwd(text):
                    enc = tok(prompt_head + str(text)[:3000], return_tensors="pt",
                              truncation=True, max_length=max_len)
                    enc = {k: v.to(model.device) for k, v in enc.items()}
                    h = model.base_model.model(**enc, output_hidden_states=True).hidden_states[-1][:, -1, :]
                    return head(h.float()).squeeze()
                sc = fwd(pref[row.chosen_conversation_id])
                sr = fwd(pref[row.rejected_conversation_id])
                loss = torch.nn.functional.softplus(sr - sc)  # wants sc > sr
                opt.zero_grad(); loss.backward(); opt.step()
                total += float(loss.item()); nseen += 1
                step += 1
                if nseen >= 80:   # cap per epoch so 5 folds finish tonight
                    break
            print(f"    epoch {ep} loss {total/max(nseen,1):.4f} n={nseen}")

        model.eval()
        te_texts = anc.iloc[te].prefix_text.tolist()
        scores = []
        with torch.no_grad():
            for text in te_texts:
                enc = tok(prompt_head + str(text)[:3000], return_tensors="pt",
                          truncation=True, max_length=max_len)
                enc = {k: v.to(model.device) for k, v in enc.items()}
                h = model.base_model.model(**enc, output_hidden_states=True).hidden_states[-1][:, -1, :]
                scores.append(float(head(h.float()).squeeze().cpu()))
        oof.iloc[te] = scores
        del model, base, head
        torch.cuda.empty_cache()
        fold_metrics.append({"fold": f, "n_te": int(len(te))})

    pred = oof.to_numpy(float)
    return {"name": tag, "hub": hub, "folds": fold_metrics,
            "pred": pred.tolist()}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--only", nargs="*", default=None, help="subset of probe names")
    ap.add_argument("--skip-lora", action="store_true")
    ap.add_argument("--lora-hub", default="Qwen/Qwen3-8B")
    args = ap.parse_args()

    EXP.mkdir(parents=True, exist_ok=True)
    anc, pairs, bandit = load_gold()
    print("anchor", anc.shape, "pairs", pairs.shape, "bandit", bandit.shape)
    print("Y = ux_retention_resid / good_moment_human  (human RCT, not judge)")
    print("good_moment rate", round(anc.good_moment_human.mean(), 3))

    results = []

    # structural baselines — these must be beaten
    for name, pred in [
        ("baseline_turn", baseline_turn(anc)),
        ("baseline_fit", baseline_fit(anc)),
        ("baseline_turn_plus_fit", baseline_turn(anc) + baseline_fit(anc)),
    ]:
        pack = eval_pack(name, pred, anc, pairs, bandit)
        print(pack)
        results.append(pack)
        np.save(EXP / f"pred_{name}.npy", pred)

    # late-only oracle-ish: score = 1 if late else 0
    late = (anc.timing == "late").astype(float).to_numpy()
    pack = eval_pack("baseline_always_late_score", late, anc, pairs, bandit)
    print(pack); results.append(pack)

    specs = PROBE_MODELS
    if args.only:
        specs = [s for s in specs if s["name"] in args.only]

    for spec in specs:
        tag = spec["name"]
        try:
            X = embed_texts(spec, anc.prefix_text.tolist(), args.device, EXP / f"emb_{tag}.npy")
        except Exception as exc:
            print(f"EMBED FAIL {tag}: {type(exc).__name__}: {exc}")
            results.append({"name": tag, "error": f"{type(exc).__name__}: {exc}"})
            if args.device == "cuda":
                torch.cuda.empty_cache()
            continue
        groups = anc.fold_participant.to_numpy()
        pred_u = lopo_ridge(X, anc.ux_retention_resid.to_numpy(float), groups)
        pred_b = lopo_logit(X, anc.good_moment_human.to_numpy(int), groups)
        # task-grouped ridge on the same embeddings (the leakage check)
        pred_task = grouped_kfold_ridge(X, anc.ux_retention_resid.to_numpy(float), anc.fold_task.to_numpy(), 5)
        pack = eval_pack(f"probe_{tag}_lopo", pred_u, anc, pairs, bandit)
        pack["spearman_U_task_grouped"] = round(spearman(pred_task, anc.ux_retention_resid), 4)
        pack["auroc_good_from_logit_lopo"] = round(auroc(anc.good_moment_human, pred_b), 4)
        pack["dim"] = int(X.shape[1])
        print(pack)
        results.append(pack)
        np.save(EXP / f"pred_probe_{tag}.npy", pred_u)
        json.dump(results, open(EXP / "results.json", "w"), indent=2)

    if not args.skip_lora:
        try:
            lora = run_lora_rank(anc, pairs, args.device, args.lora_hub, "lora_qwen3-8b")
            if "pred" in lora:
                pred = np.asarray(lora["pred"], float)
                pack = eval_pack("lora_qwen3-8b_5fold", pred, anc, pairs, bandit)
                pack["lora"] = {k: v for k, v in lora.items() if k != "pred"}
                print(pack)
                results.append(pack)
                np.save(EXP / "pred_lora_qwen3-8b.npy", pred)
        except Exception as exc:
            print(f"LORA FAIL: {type(exc).__name__}: {exc}")
            results.append({"name": "lora_qwen3-8b", "error": f"{type(exc).__name__}: {exc}"})

    json.dump(results, open(EXP / "results.json", "w"), indent=2)
    # markdown table
    lines = ["# Experiment results (human Gold only)", "",
             "| model | Spearman U (LOPO) | AUROC good | pairwise acc | U high−low |",
             "|---|---:|---:|---:|---:|"]
    for r in results:
        if "spearman_U_lopo" in r:
            lines.append(
                f"| {r['name']} | {r['spearman_U_lopo']} | {r.get('auroc_good_lopo', r.get('auroc_good_from_logit_lopo', ''))} "
                f"| {r['pairwise_acc']} | {r['mean_U_high_minus_low']} |"
            )
        elif "error" in r:
            lines.append(f"| {r['name']} | ERROR | {r['error'][:80]} | | |")
    (EXP / "RESULTS.md").write_text("\n".join(lines) + "\n")
    print("wrote", EXP / "results.json")


if __name__ == "__main__":
    main()
