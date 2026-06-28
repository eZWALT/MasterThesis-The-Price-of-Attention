"""
Experiment: Chat response length across 3 ad conditions × 5 prompt variants.

Goal:  Find which system-prompt wording produces concise yet informative
       assistant replies — reducing overwhelm without losing helpfulness.

Design:
  3 conditions (baseline / inline / explicit) × 5 variants × 5 scenarios × N generations
  = 75 × N LLM calls (375 at N=5, 750 at N=10)

  Variant 1 in each condition is the CURRENT production prompt (control).

Metrics (from Ollama response metadata):
  - eval_count         (exact generation token count)
  - word_count
  - latency_ms

Usage:
  python -m experiments.chat_prompt_length.run --generations 10
  python -m experiments.chat_prompt_length.run --quick
  python -m experiments.chat_prompt_length.run --generations 5 --scenarios 3
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

# Ensure project root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
from experiments.shared import ExperimentCell, run_experiment, preflight
from experiments.chat_prompt_length.prompts import CONDITIONS
from experiments.chat_prompt_length.scenarios import SCENARIOS


def build_cells(n_scenarios: int) -> List[ExperimentCell]:
    """
    Build the full grid of experiment cells.
    Each cell = one (condition, variant, scenario) combination.
    """
    scenarios = SCENARIOS[:n_scenarios]
    cells: List[ExperimentCell] = []

    for cond in CONDITIONS:
        for variant in cond["variants"]:
            for scenario in scenarios:
                # Build the full message list for this cell
                system_parts = [variant.base_prompt]
                if scenario.task_system_extension:
                    system_parts.append(scenario.task_system_extension)
                system_content = " ".join(system_parts)

                messages = [{"role": "system", "content": system_content}]
                if variant.ad_prompt:
                    ad_content = variant.ad_prompt.format(
                        products_block=scenario.products_block
                    )
                    messages.append({"role": "system", "content": ad_content})
                messages.append({"role": "user", "content": scenario.user_message})

                cells.append(ExperimentCell(
                    variant_key=variant.key,
                    variant_label=variant.label,
                    cell_key=scenario.task_id,
                    cell_label=scenario.task_title,
                    messages=messages,
                    variant_note=variant.note,
                ))

    return cells


def main():
    parser = argparse.ArgumentParser(
        description="Chat response length experiment — 3 conditions × 5 variants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m experiments.chat_prompt_length.run --generations 10
  python -m experiments.chat_prompt_length.run --quick
  python -m experiments.chat_prompt_length.run --generations 5 --scenarios 3
        """,
    )
    parser.add_argument(
        "--generations", type=int, default=10,
        help="LLM generations per cell (default: 10)"
    )
    parser.add_argument(
        "--scenarios", type=int, default=5,
        help="Number of task scenarios to use (default: 5, max: 5)"
    )
    parser.add_argument(
        "--ollama-url", type=str, default="http://localhost:9999",
        help="Ollama API base URL"
    )
    parser.add_argument(
        "--model", type=str, default=DEFAULT_MODEL,
        help=f"Ollama model name (default: {DEFAULT_MODEL})"
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Smoke test: 2 scenarios × 1 generation"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Override output directory"
    )
    args = parser.parse_args()

    # ── Quick mode overrides ────────────────────────────────────────────────
    if args.quick:
        args.generations = 1
        args.scenarios = 2

    # ── Clamp scenarios ─────────────────────────────────────────────────────
    args.scenarios = min(args.scenarios, len(SCENARIOS))

    # ── Preflight ───────────────────────────────────────────────────────────
    preflight(args.ollama_url)

    # ── Build cells ─────────────────────────────────────────────────────────
    cells = build_cells(args.scenarios)

    n_variants = sum(len(c["variants"]) for c in CONDITIONS)
    total = len(cells) * args.generations
    print(f"\n  Conditions:  {len(CONDITIONS)}")
    print(f"  Variants:    {n_variants} ({[len(c['variants']) for c in CONDITIONS]} per condition)")
    print(f"  Scenarios:   {args.scenarios}")
    print(f"  Total cells: {len(cells)}")
    print(f"  Generations: {args.generations}")

    # ── Run ─────────────────────────────────────────────────────────────────
    output_dir = Path(args.output_dir) if args.output_dir else None
    run_experiment(
        experiment_name="chat_prompt_length",
        cells=cells,
        generations=args.generations,
        ollama_url=args.ollama_url,
        model=args.model,
        output_dir=output_dir,
        temperature=DEFAULT_TEMPERATURE,
        max_tokens=DEFAULT_MAX_TOKENS,
    )


if __name__ == "__main__":
    main()
