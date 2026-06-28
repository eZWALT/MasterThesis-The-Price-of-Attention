"""
Compare experiment runs side by side.

Loads one or more experiment runs from output/<experiment_name>/<run_label>/
and plots token-count distributions per variant, plus a summary table.

Usage:
  # Compare all runs of an experiment
  python -m experiments.compare chat_prompt_length

  # Compare specific runs
  python -m experiments.compare chat_prompt_length --runs v1_production v2_concise

  # Use a specific output dir
  python -m experiments.compare chat_prompt_length --output-dir experiments/output

Output:
  output/<experiment_name>/comparison_<timestamp>.png
  (also printed to terminal as a table)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _load_run(run_dir: Path) -> Dict:
    """Load generations.jsonl and summary.json from a run directory."""
    gen_file = run_dir / "generations.jsonl"
    summary_file = run_dir / "summary.json"

    records: List[dict] = []
    if gen_file.exists():
        with open(gen_file) as f:
            for line in f:
                records.append(json.loads(line))

    summary = {}
    if summary_file.exists():
        summary = json.loads(summary_file.read_text())

    return {
        "run_name": run_dir.name,
        "records": records,
        "summary": summary,
    }


def _discover_runs(base_dir: Path) -> List[str]:
    """Find all run subdirectories under base_dir/<experiment_name>/."""
    if not base_dir.exists():
        return []
    return sorted(
        d.name for d in base_dir.iterdir()
        if d.is_dir() and (d / "generations.jsonl").exists()
    )


def _variant_group_key(record: dict) -> str:
    """Group records by the part of variant_key before the first underscore-digit."""
    key = record.get("variant_key", "")
    parts = key.split("_")
    if len(parts) >= 2 and parts[0] in ("base", "inline", "explicit"):
        return parts[0]
    return "other"


CONDITION_COLORS = {
    "base": "#4e79a7",
    "inline": "#f28e2b",
    "explicit": "#e15759",
    "other": "#76b7b2",
}

CONDITION_LABELS = {
    "base": "Baseline",
    "inline": "Inline",
    "explicit": "Explicit",
    "other": "Other",
}


def plot_comparison(runs: List[Dict], output_file: Path) -> None:
    """Plot token-count box plots per variant, coloured by condition."""
    all_variants: List[str] = []
    for run in runs:
        for rec in run["records"]:
            vk = rec.get("variant_key", "")
            if vk not in all_variants:
                all_variants.append(vk)

    n_variants = len(all_variants)
    n_runs = len(runs)

    fig, ax = plt.subplots(figsize=(max(14, n_variants * 1.2), 7))

    bar_width = 0.8 / max(n_runs, 1)
    x_positions = range(n_variants)

    for run_idx, run in enumerate(runs):
        run_name = run["run_name"]
        run_records = run["records"]

        means = []
        stds = []
        for vk in all_variants:
            toks = [
                r["eval_count"] for r in run_records
                if r.get("variant_key") == vk and r.get("eval_count", 0) > 0
            ]
            if toks:
                means.append(sum(toks) / len(toks))
                import statistics
                stds.append(statistics.stdev(toks) if len(toks) > 1 else 0)
            else:
                means.append(0)
                stds.append(0)

        offset = (run_idx - n_runs / 2 + 0.5) * bar_width
        bars = ax.bar(
            [x + offset for x in x_positions],
            means,
            bar_width,
            yerr=stds,
            capsize=3,
            label=run_name,
            alpha=0.85,
        )

        # Color bars by condition group
        for i, vk in enumerate(all_variants):
            group = _variant_group_key({"variant_key": vk})
            color = CONDITION_COLORS.get(group, "#76b7b2")
            if i < len(bars):
                bars[i].set_facecolor(color)
                bars[i].set_alpha(0.7)

    # Legend for conditions
    legend_patches = [
        mpatches.Patch(color=CONDITION_COLORS[g], label=CONDITION_LABELS[g])
        for g in ["base", "inline", "explicit"]
    ]
    run_legend = ax.legend(
        loc="upper right",
        title="Runs",
        fontsize=9,
    )
    ax.add_artist(run_legend)
    ax.legend(
        handles=legend_patches,
        loc="upper left",
        title="Conditions",
        fontsize=9,
    )

    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(all_variants, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Generation Tokens (eval_count)")
    ax.set_title("Chat Prompt Length — Token Distribution by Variant")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    print(f"Plot saved to: {output_file}")


def plot_distributions(runs: List[Dict], output_file: Path) -> None:
    """Plot token-count violin/strip plots per variant for the first run."""
    if not runs:
        return
    run = runs[0]
    records = run["records"]

    variants: List[str] = []
    for rec in records:
        vk = rec.get("variant_key", "")
        if vk not in variants:
            variants.append(vk)

    fig, axes = plt.subplots(
        nrows=len(variants),
        ncols=1,
        figsize=(12, max(3, len(variants) * 0.8)),
        sharex=True,
    )
    if len(variants) == 1:
        axes = [axes]

    for i, vk in enumerate(variants):
        toks = [
            r["eval_count"] for r in records
            if r.get("variant_key") == vk and r.get("eval_count", 0) > 0
        ]
        group = _variant_group_key({"variant_key": vk})
        color = CONDITION_COLORS.get(group, "#76b7b2")
        label = run["run_name"]

        ax_i = axes[i]
        ax_i.hist(toks, bins=20, color=color, alpha=0.7, edgecolor="white", linewidth=0.5)
        ax_i.axvline(sum(toks) / len(toks), color="red", linestyle="--", linewidth=1, alpha=0.7)
        ax_i.set_ylabel(vk, fontsize=8, rotation=0, ha="right", va="center")
        ax_i.grid(axis="x", alpha=0.3)

    axes[-1].set_xlabel("Generation Tokens (eval_count)")
    fig.suptitle(f"Token Distributions — {run['run_name']}", fontsize=12, y=0.98)
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    print(f"Distribution plot saved to: {output_file}")


def print_comparison_table(runs: List[Dict]) -> None:
    """Print a text comparison table across runs."""
    for run in runs:
        print(f"\n{'=' * 78}")
        print(f"  Run: {run['run_name']}")
        print(f"{'=' * 78}")
        summary = run.get("summary", {})
        variants = summary.get("variants", [])
        if not variants:
            print("  (no summary data)")
            continue

        headers = [
            "Variant", "n", "Toks(μ)", "Toks(σ)", "p50", "p95",
            "Words(μ)", "Lat ms(μ)",
        ]
        rows: List[List[str]] = []
        for v in variants:
            rows.append([
                v.get("variant_label", v.get("variant_key", "?"))[:35],
                str(v.get("n_samples", 0)),
                f"{v.get('tokens', {}).get('mean', 0):.0f}",
                f"{v.get('tokens', {}).get('std', 0):.0f}",
                f"{v.get('tokens', {}).get('p50', 0):.0f}",
                f"{v.get('tokens', {}).get('p95', 0):.0f}",
                f"{v.get('words', {}).get('mean', 0):.0f}",
                f"{v.get('latency_ms', {}).get('mean', 0):.0f}",
            ])

        # Simple table print
        col_widths = [max(len(h), *(len(r[i]) for r in rows)) + 2 for i, h in enumerate(headers)]
        sep = "-" * (sum(col_widths) + len(headers) - 1)
        print(sep)
        print(" ".join(h.ljust(w) for h, w in zip(headers, col_widths)))
        print(sep)
        for row in rows:
            print(" ".join(c.ljust(w) for c, w in zip(row, col_widths)))
        print(sep)


def main():
    parser = argparse.ArgumentParser(
        description="Compare experiment runs side by side",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "experiment",
        type=str,
        help="Experiment name (folder under output/), e.g. 'chat_prompt_length'"
    )
    parser.add_argument(
        "--runs", nargs="*",
        help="Specific run labels to compare (default: all runs found)"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Base output directory (default: experiments/output)"
    )
    args = parser.parse_args()

    # ── Find base directory ─────────────────────────────────────────────────
    script_dir = Path(__file__).resolve().parent  # experiments/
    base_dir = Path(args.output_dir) if args.output_dir else script_dir / "output"
    exp_dir = base_dir / args.experiment

    # ── Discover runs ───────────────────────────────────────────────────────
    all_runs = _discover_runs(exp_dir)
    if not all_runs:
        print(f"No runs found in {exp_dir}")
        sys.exit(1)

    if args.runs:
        run_names = [r for r in args.runs if r in all_runs]
        missing = [r for r in args.runs if r not in all_runs]
        if missing:
            print(f"Warning: runs not found: {missing}")
    else:
        run_names = all_runs

    print(f"Comparing {len(run_names)} run(s): {run_names}")

    # ── Load ────────────────────────────────────────────────────────────────
    runs: List[Dict] = []
    for name in run_names:
        run = _load_run(exp_dir / name)
        runs.append(run)
        print(f"  Loaded {name}: {len(run['records'])} records")

    # ── Print table ────────────────────────────────────────────────────────
    print_comparison_table(runs)

    # ── Plot ─────────────────────────────────────────────────────────────────
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%dT%H%M%SZ")
    bar_file = exp_dir / f"comparison_bars_{timestamp}.png"
    dist_file = exp_dir / f"comparison_dists_{timestamp}.png"

    plot_comparison(runs, bar_file)
    plot_distributions(runs, dist_file)

    print(f"\nDone. Outputs in: {exp_dir}")


if __name__ == "__main__":
    main()
