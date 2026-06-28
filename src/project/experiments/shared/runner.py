"""
Shared experiment runner.

Every experiment follows the same pattern:
  1. Define a set of "cells" (variant × scenario combinations).
  2. For each cell, call the LLM N times.
  3. Collect records → write JSONL.
  4. Aggregate stats → write summary.json + summary.txt.

Experiments call run_experiment() with their own cells and metadata.
This module handles I/O, progress output, and result aggregation.

Output layout (per experiment run):
  output/<experiment_name>/<run_label>/    ← label or timestamp
    generations.jsonl   — one JSON record per LLM call
    summary.json        — aggregated stats per variant
    summary.txt         — human-readable comparison table

Multiple runs of the same experiment are stored side by side:
  output/chat_prompt_length/
    v1_production/          ← --label v1_production
    v2_concise_rewording/   ← --label v2_concise_rewording
    20260628T134901Z/       ← auto-timestamp when no label given
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Ensure project root is importable when run as module
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experiments.shared.ollama import call_ollama, ollama_is_up
from experiments.shared.stats import compute_stats, format_table


@dataclass
class GenerationRecord:
    """One row per LLM call — written to generations.jsonl."""
    experiment: str                # e.g. "chat_prompt_length"
    variant_key: str               # e.g. "base_v1_current"
    variant_label: str             # human-readable
    cell_key: str                  # e.g. scenario/task id
    cell_label: str               # human-readable
    generation_idx: int
    user_input: str                # what was sent to the LLM (prompt or user message)
    assistant_reply: str          # raw LLM output
    eval_count: int               # Ollama generation tokens
    prompt_eval_count: int        # Ollama input tokens
    word_count: int
    char_count: int
    latency_ms: float
    eval_duration_ns: int
    model: str
    variant_note: str = ""        # optional researcher note
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ExperimentCell:
    """
    One cell in the experiment grid.
    An experiment is a list of cells, each run N times.
    """
    variant_key: str
    variant_label: str
    cell_key: str            # e.g. "swt_gardening_birthday_gift"
    cell_label: str          # e.g. "Gardening birthday gift"
    messages: List[Dict[str, str]]  # the full message list to send to the LLM
    variant_note: str = ""


def run_experiment(
    experiment_name: str,
    cells: List[ExperimentCell],
    generations: int,
    ollama_url: str,
    model: str,
    output_dir: Optional[Path] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    num_ctx: int = 16384,
    run_label: Optional[str] = None,
) -> Path:
    """
    Run the experiment and return the output directory path.

    Parameters
    ----------
    experiment_name : used for output folder naming, e.g. "chat_prompt_length"
    cells            : list of ExperimentCell, each run `generations` times
    generations      : number of LLM calls per cell
    ollama_url       : Ollama base URL
    model            : model name
    output_dir       : override output directory (otherwise auto-generated)
    temperature      : LLM sampling temperature
    max_tokens       : max tokens to generate per call
    num_ctx          : context window size
    run_label        : short name for this run (e.g. "v1_production").
                       Replaces timestamp in the output folder name so
                       multiple runs of the same experiment (with different
                       prompts, for example) are stored side by side and
                       can be compared by the analysis scripts.
    """
    total_calls = len(cells) * generations

    # ── Output directory ────────────────────────────────────────────────────
    if output_dir is None:
        folder = run_label if run_label else datetime.now().strftime("%Y%m%dT%H%M%SZ")
        output_dir = Path(__file__).resolve().parent.parent / "output" / experiment_name / folder
    output_dir.mkdir(parents=True, exist_ok=True)

    generations_file = output_dir / "generations.jsonl"
    summary_file = output_dir / "summary.json"
    report_file = output_dir / "summary.txt"

    print(f"\n{'=' * 78}")
    print(f"  Experiment: {experiment_name}")
    print(f"  Model:        {model}")
    print(f"  Ollama URL:   {ollama_url}")
    print(f"  Cells:        {len(cells)}")
    print(f"  Generations:  {generations}")
    print(f"  Total calls:  {total_calls}")
    print(f"  Output:       {output_dir}")
    print(f"{'=' * 78}\n")

    all_records: List[GenerationRecord] = []
    call_num = 0

    with open(generations_file, "w") as f:
        for cell in cells:
            for gen_idx in range(generations):
                call_num += 1

                label = f"[{call_num}/{total_calls}] {cell.variant_key}/{cell.cell_key}#{gen_idx + 1}"
                print(f"  {label} ...", end=" ", flush=True)

                try:
                    t0 = time.perf_counter()
                    result = call_ollama(
                        messages=cell.messages,
                        model=model,
                        ollama_url=ollama_url,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        num_ctx=num_ctx,
                    )
                    latency_ms = (time.perf_counter() - t0) * 1000
                    words = len(result["content"].split())
                    chars = len(result["content"])
                    print(f"{result['eval_count']} tok, {words} words, {latency_ms:.0f}ms")
                except Exception as e:
                    print(f"FAILED: {e}")
                    result = {
                        "content": "",
                        "eval_count": 0,
                        "prompt_eval_count": 0,
                        "eval_duration_ns": 0,
                        "done_reason": f"error: {e}",
                    }
                    latency_ms = 0.0
                    words = 0
                    chars = 0

                rec = GenerationRecord(
                    experiment=experiment_name,
                    variant_key=cell.variant_key,
                    variant_label=cell.variant_label,
                    cell_key=cell.cell_key,
                    cell_label=cell.cell_label,
                    generation_idx=gen_idx,
                    user_input=json.dumps(cell.messages),
                    assistant_reply=result["content"],
                    eval_count=result["eval_count"],
                    prompt_eval_count=result["prompt_eval_count"],
                    word_count=words,
                    char_count=chars,
                    latency_ms=latency_ms,
                    eval_duration_ns=result["eval_duration_ns"],
                    model=model,
                    variant_note=cell.variant_note,
                )
                all_records.append(rec)
                f.write(json.dumps(asdict(rec)) + "\n")
                f.flush()

    # ── Aggregate per variant ───────────────────────────────────────────────
    variants_seen: Dict[str, Dict] = {}
    for rec in all_records:
        if rec.variant_key not in variants_seen:
            variants_seen[rec.variant_key] = {
                "variant_key": rec.variant_key,
                "variant_label": rec.variant_label,
                "variant_note": rec.variant_note,
                "records": [],
            }
        variants_seen[rec.variant_key]["records"].append(rec)

    summary: Dict = {
        "experiment": experiment_name,
        "run_label": run_label or "",
        "config": {
            "model": model,
            "ollama_url": ollama_url,
            "generations": generations,
            "n_cells": len(cells),
            "total_calls": total_calls,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "variants": [],
    }

    table_rows: List[List[str]] = []

    for vkey in sorted(variants_seen.keys()):
        vdata = variants_seen[vkey]
        recs = vdata["records"]
        tokens = [r.eval_count for r in recs if r.eval_count > 0]
        words = [r.word_count for r in recs if r.word_count > 0]
        chars = [r.char_count for r in recs if r.char_count > 0]
        lats = [r.latency_ms for r in recs if r.latency_ms > 0]

        v_stats = {
            "variant_key": vkey,
            "variant_label": vdata["variant_label"],
            "variant_note": vdata["variant_note"],
            "n_samples": len(recs),
            "tokens": compute_stats(tokens),
            "words": compute_stats(words),
            "chars": compute_stats(chars),
            "latency_ms": compute_stats(lats),
        }
        summary["variants"].append(v_stats)

        table_rows.append([
            vdata["variant_label"][:35],
            f"{v_stats['tokens']['mean']:.0f}",
            f"{v_stats['tokens']['std']:.0f}",
            f"{v_stats['tokens']['p50']:.0f}",
            f"{v_stats['words']['mean']:.0f}",
            f"{v_stats['latency_ms']['mean']:.0f}",
        ])

    summary_file.write_text(json.dumps(summary, indent=2))

    # ── Report ──────────────────────────────────────────────────────────────
    headers = ["Variant", "Toks(μ)", "Toks(σ)", "Toks p50", "Words(μ)", "Lat ms(μ)"]
    report = (
        f"{experiment_name} — Summary\n"
        f"{'=' * 78}\n"
        f"Model: {model}  •  Generations: {generations}  •  Cells: {len(cells)}  •  Total calls: {total_calls}\n\n"
        f"{format_table(headers, table_rows)}\n"
    )
    report_file.write_text(report)
    print(f"\n{report}")
    print(f"Results saved to: {output_dir}")
    return output_dir


def preflight(ollama_url: str) -> None:
    """Check Ollama is running, exit with help message if not."""
    print("Checking Ollama...", end=" ", flush=True)
    if not ollama_is_up(ollama_url):
        print("NOT RUNNING")
        print(f"\n  Start Ollama first:")
        print(f"    ./launch.sh --host   # or")
        print(f"    ollama serve &")
        print(f"\n  Then re-run this script.")
        sys.exit(1)
    print("OK")
