#!/usr/bin/env python3
"""Qwen3-14B last-token AND mean-pool on all 1,080 primary prefixes.

The 216 last-token PCA-8 probe is the only text model that beat the late
rule. This writes the same representation for every turn so we can train
on the extra views (LOPO by person).
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs" / "experiments" / "full"
HUB = "Qwen/Qwen3-14B"
MAX_LEN = 512
BS = 4


def main():
    df = pd.read_csv(HERE / "outputs/silver/turns.csv")
    df = df[df.source_set == "primary"].reset_index(drop=True)
    texts = df.prefix_text.fillna("").tolist()
    dest_last = OUT / "emb_qwen3-14b_last_1080.npy"
    dest_mean = OUT / "emb_qwen3-14b_mean_1080.npy"
    if dest_last.exists() and np.load(dest_last).shape[0] == len(texts) \
            and dest_mean.exists() and np.load(dest_mean).shape[0] == len(texts):
        print("already done")
        return

    device = "cuda"
    tok = AutoTokenizer.from_pretrained(HUB, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4",
    )
    model = AutoModelForCausalLM.from_pretrained(
        HUB, quantization_config=bnb, device_map={"": device}, trust_remote_code=True,
    ).eval()

    lasts, means = [], []
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(texts), BS):
            enc = tok(
                texts[i:i + BS], padding=True, truncation=True,
                max_length=MAX_LEN, return_tensors="pt",
            )
            enc = {k: v.to(device) for k, v in enc.items() if k in ("input_ids", "attention_mask")}
            h = model(**enc, output_hidden_states=True).hidden_states[-1].float()
            attn = enc["attention_mask"]
            last = attn.sum(1) - 1
            vec_last = h[torch.arange(h.size(0), device=device), last]
            mask = attn.unsqueeze(-1)
            vec_mean = (h * mask).sum(1) / mask.sum(1).clamp(min=1)
            lasts.append(vec_last.cpu().numpy())
            means.append(torch.nn.functional.normalize(vec_mean, dim=1).cpu().numpy())
            if i % 40 == 0:
                print(f"{i}/{len(texts)}", flush=True)
    last = np.concatenate(lasts)
    mean = np.concatenate(means)
    np.save(dest_last, last)
    np.save(dest_mean, mean)
    print(f"wrote {last.shape} {mean.shape} in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
