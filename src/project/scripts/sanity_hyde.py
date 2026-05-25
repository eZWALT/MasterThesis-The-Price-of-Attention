#!/usr/bin/env python3
"""
HyDE / query-expansion sanity check (optional LLM cost).

Usage (from src/project):
  QUERY_EXPANSION_MODE=hyde python scripts/sanity_hyde.py
  python scripts/sanity_hyde.py --mode expand

Requires a running LLM at core.config.API_URL (same as the chat backend).
Does not load FAISS or embedding models — only times the expansion stage.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# project root on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.retrieval.stages.query_preprocessor import QueryExpansionStage
from core.retrieval.stages.state import PipelineState


def main() -> None:
    parser = argparse.ArgumentParser(description="Time HyDE / query expansion stage")
    parser.add_argument("--mode", choices=("hyde", "expand"), default="hyde")
    parser.add_argument(
        "--query",
        default="Why do people say Peruvians eat pigeons? I'm curious about Peruvian food.",
    )
    args = parser.parse_args()

    context = [
        {"role": "user", "content": "Tell me about Peruvian cuisine"},
        {"role": "assistant", "content": "Peruvian food includes ceviche and cuy..."},
        {"role": "user", "content": args.query},
    ]

    state = PipelineState(query=args.query, context=context)
    stage = QueryExpansionStage(mode=args.mode)

    t0 = time.perf_counter()
    out = stage.run(state)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    print(f"Mode: {args.mode}")
    print(f"Latency: {elapsed_ms:.0f} ms")
    print(f"Input query ({len(args.query)} chars): {args.query[:120]}...")
    if out.expanded_query:
        print(f"Expanded ({len(out.expanded_query)} chars):\n{out.expanded_query}")
    else:
        print("No expanded_query set (LLM failed or mode=none).")


if __name__ == "__main__":
    main()
