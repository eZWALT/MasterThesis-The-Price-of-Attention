"""Plot token distributions per condition × variant from existing experiment data."""

import json
import sys
from pathlib import Path
from collections import defaultdict
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

EXPERIMENT = "chat_prompt_length"
RUN_DIR = "20260628T134901Z"

script_dir = Path(__file__).resolve().parent
gen_file = script_dir / "output" / EXPERIMENT / RUN_DIR / "generations.jsonl"

records = []
with open(gen_file) as f:
    for line in f:
        records.append(json.loads(line))

# Group by condition prefix then variant
conditions = defaultdict(dict)  # {condition: {variant_key: [tokens]}}

for r in records:
    vk = r["variant_key"]
    group = vk.split("_")[0]  # base, inline, explicit
    toks = r.get("eval_count", 0)
    if toks > 0:
        conditions[group].setdefault(vk, []).append(toks)

condition_order = ["base", "inline", "explicit"]
condition_titles = {
    "base": "Baseline (no ads)",
    "inline": "Inline Persuasive",
    "explicit": "Explicit Ad Block",
}
condition_colors = {
    "base": ["#4e79a7", "#6ba0c8", "#8db8d8", "#a8c8e0", "#c0d8e8"],
    "inline": ["#f28e2b", "#f5a856", "#f8b878", "#fac89a", "#fcd8bc"],
    "explicit": ["#e15759", "#e87878", "#ec9292", "#f0acac", "#f4c6c6"],
}

fig, axes = plt.subplots(1, 3, figsize=(20, 7), sharey=True)

for col, cond in enumerate(condition_order):
    ax = axes[col]
    variants = conditions.get(cond, {})
    # Sort by variant number (v1, v2, ...)
    sorted_keys = sorted(variants.keys(), key=lambda k: int(k.split("_v")[1].split("_")[0]))
    data = [variants[k] for k in sorted_keys]
    labels = [k.replace(f"{cond}_", "") for k in sorted_keys]

    # Box plot
    bp = ax.boxplot(
        data,
        vert=True,
        patch_artist=True,
        showmeans=True,
        meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor="black", markersize=5),
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(linewidth=1),
        capprops=dict(linewidth=1),
    )

    for patch, color in zip(bp["boxes"], condition_colors[cond]):
        patch.set_facecolor(color)
        patch.set_alpha(0.8)

    # Overlay individual points (strip plot)
    for i, (vals, color) in enumerate(zip(data, condition_colors[cond])):
        x = [i + 1] * len(vals)
        ax.scatter(
            x, vals,
            alpha=0.25, s=12, color=color, edgecolors="none", zorder=3,
        )

    # Mean lines
    for i, vals in enumerate(data):
        mean_val = sum(vals) / len(vals)
        ax.scatter([i + 1], [mean_val], marker="D", color="white", edgecolors="black", s=40, zorder=5)

    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.set_title(condition_titles[cond], fontsize=12, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    if col == 0:
        ax.set_ylabel("Generation Tokens (eval_count)", fontsize=10)

    # Add mean annotations
    for i, vals in enumerate(data):
        mean_val = sum(vals) / len(vals)
        ax.annotate(
            f"μ={mean_val:.0f}",
            xy=(i + 1, mean_val),
            xytext=(8, 0),
            textcoords="offset points",
            fontsize=7,
            va="center",
            color="black",
        )

fig.suptitle(
    "Chat Response Length — Token Distributions by Condition × Prompt Variant\n"
    f"(50 generations per variant, qwen3.6:35b)",
    fontsize=13,
    fontweight="bold",
    y=1.02,
)
plt.tight_layout()

out_file = script_dir / "output" / EXPERIMENT / f"distributions_{RUN_DIR}.png"
plt.savefig(out_file, dpi=150, bbox_inches="tight")
print(f"Saved: {out_file}")
