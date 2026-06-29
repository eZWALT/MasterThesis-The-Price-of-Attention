"""
Experiment v2: Chat response length across current prompt types × 5 variants.

Tests the 3 CURRENT prompt types (baseline, inline injection, awareness)
instead of the old 3 conditions (baseline, inline, explicit).

Output goes to a separate directory so v1 results are never overwritten.

Usage:
  python -m experiments.chat_prompt_length.run_v2 --generations 10 --label v2_prompts
  python -m experiments.chat_prompt_length.run_v2 --quick --label smoke
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
from experiments.shared import ExperimentCell, run_experiment, preflight
from experiments.chat_prompt_length.prompts_v2 import CONDITIONS
from experiments.chat_prompt_length.scenarios import SCENARIOS


def build_cells(n_scenarios: int) -> List[ExperimentCell]:
    """
    Build the full grid of experiment cells.
    Each cell = one (prompt_type, variant, scenario) combination.
    """
    scenarios = SCENARIOS[:n_scenarios]
    cells: List[ExperimentCell] = []

    for cond in CONDITIONS:
        for variant in cond["variants"]:
            for scenario in scenarios:
                system_content = variant.base_prompt

                messages = [{"role": "system", "content": system_content}]

                if variant.ad_prompt:
                    if cond["key"] == "awareness":
                        # Awareness uses only the FIRST product (the one that was shown)
                        first_product = scenario.products_block.split("\n\n")[0]
                        ad_content = variant.ad_prompt.format(
                            products_block=first_product
                        )
                    else:
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
        description="Chat response length v2 — 3 prompt types × 5 variants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m experiments.chat_prompt_length.run_v2 --generations 10
  python -m experiments.chat_prompt_length.run_v2 --quick
  python -m experiments.chat_prompt_length.run_v2 --generations 5 --scenarios 3
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
    parser.add_argument(
        "--label", type=str, default=None,
        help="Short name for this run (e.g. 'v2_prompts')."
    )
    args = parser.parse_args()

    if args.quick:
        args.generations = 1
        args.scenarios = 2

    args.scenarios = min(args.scenarios, len(SCENARIOS))

    preflight(args.ollama_url)

    cells = build_cells(args.scenarios)

    n_variants = sum(len(c["variants"]) for c in CONDITIONS)
    total = len(cells) * args.generations
    print(f"\n  Prompt types: {len(CONDITIONS)}")
    print(f"  Variants:     {n_variants} ({[len(c['variants']) for c in CONDITIONS]} per type)")
    print(f"  Scenarios:    {args.scenarios}")
    print(f"  Total cells:  {len(cells)}")
    print(f"  Generations:  {args.generations}")

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
        run_label=args.label,
    )


if __name__ == "__main__":
    main()
