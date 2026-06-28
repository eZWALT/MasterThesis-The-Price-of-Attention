"""
Experiment: HyDE token-length sweet spot.

Goal:  Find the optimal HYDE_TOKENS_PER_DOC that balances retrieval signal
       against generation latency.  Too short → weak semantic signal.
       Too long → wasted latency + LLM drift.

Method:
  1. Define 5 prompt variants (keyword → concise → moderate → detailed → comprehensive).
  2. Use realistic queries from the task catalog as input.
  3. Generate N samples per variant via the live LLM (Ollama).
  4. Tokenise each generation with the embedding tokenizer (Qwen3-Embedding-0.6B).
  5. Report mean / std / min / max / p50 / p95 token counts per variant.
  6. Save all raw generations + summary to JSONL.

Usage:
    # Full run (needs Ollama up on :9999)
    python -m experiments.hyde_token_length --generations 10

    # Quick smoke test (1 generation per variant, short queries)
    python -m experiments.hyde_token_length --generations 1 --quick

    # Custom Ollama URL
    python -m experiments.hyde_token_length --ollama-url http://localhost:9999

Output:
    experiments/output/hyde_token_length_<timestamp>/
        generations.jsonl    ← raw generation records
        summary.json         ← aggregated stats per variant
        summary.txt          ← human-readable table
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional

# ── Ensure project root is importable ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests

from core.config import DEFAULT_MODEL, HYDE_TEMPERATURE
from core.retrieval.hyde import count_embedding_tokens
from core.experiment.tasks import TASK_CATALOG


# ══════════════════════════════════════════════════════════════════════════════
# Prompt variants — each instructs the LLM to produce HyDE docs at a different
# length target.  The structure mirrors the production HYDE_PROMPT but varies
# the per-doc length constraint.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PromptVariant:
    key: str
    label: str
    target_tokens_per_doc: int
    prompt_template: str


PROMPT_VARIANTS: List[PromptVariant] = [
    PromptVariant(
        key="v1_keywords",
        label="Keywords only (≤20 tok/doc)",
        target_tokens_per_doc=20,
        prompt_template=(
            "You write hypothetical product listings for semantic search. "
            "Catalog items are short titles plus plain descriptions (materials, use case). "
            "Your text is embedded and matched against that index.\n\n"
            "Produce exactly {num_docs} listings. "
            "Each listing must be a keyword snippet of AT MOST 20 tokens — "
            "just nouns and adjectives, no full sentences.\n"
            "Each listing must be a DIFFERENT plausible product angle for the same need.\n\n"
            "Separate listings with a line containing only: ---\n\n"
            "User need: {query}\n"
            "Context:\n{context_block}\n\n"
            "Listing 1:"
        ),
    ),
    PromptVariant(
        key="v2_concise",
        label="Concise (≤50 tok/doc)",
        target_tokens_per_doc=50,
        prompt_template=(
            "You write hypothetical product listings for semantic search. "
            "Catalog items are short titles plus plain descriptions (materials, use case). "
            "Your text is embedded and matched against that index — write like a catalog entry, not an ad.\n\n"
            "Produce exactly {num_docs} listings. Keep each listing SHORT (under 50 tokens). "
            "Each listing must be a DIFFERENT plausible product angle for the same need. "
            "Use concrete nouns; avoid fluff, brands, prices, and CTAs.\n\n"
            "Separate listings with a line containing only: ---\n\n"
            "User need: {query}\n"
            "Context:\n{context_block}\n\n"
            "Listing 1:"
        ),
    ),
    PromptVariant(
        key="v3_moderate",
        label="Moderate (≤100 tok/doc) — current default",
        target_tokens_per_doc=100,
        prompt_template=(
            "You write hypothetical product listings for semantic search. "
            "Catalog items are short titles plus plain descriptions (materials, use case). "
            "Your text is embedded and matched against that index — write like a catalog entry, not an ad.\n\n"
            "Produce exactly {num_docs} listings. Keep each listing SHORT (well under "
            "{tokens_per_doc} tokens). "
            "Each listing must be a DIFFERENT plausible product angle for the same need. "
            "Use concrete nouns; avoid fluff, brands, prices, and CTAs. "
            "Stay on topic from the query, conversation, and task scenario.\n\n"
            "Separate listings with a line containing only: ---\n\n"
            "User need: {query}\n"
            "Context:\n{context_block}\n\n"
            "Listing 1:"
        ),
    ),
    PromptVariant(
        key="v4_detailed",
        label="Detailed (≤200 tok/doc)",
        target_tokens_per_doc=200,
        prompt_template=(
            "You write hypothetical product listings for semantic search. "
            "Catalog items are short titles plus plain descriptions (materials, use case). "
            "Your text is embedded and matched against that index — write like a catalog entry, not an ad.\n\n"
            "Produce exactly {num_docs} listings. "
            "Each listing should be a DETAILED product description of up to 200 tokens, "
            "covering materials, intended use, key features, and target audience. "
            "Each listing must be a DIFFERENT plausible product angle for the same need. "
            "Use concrete nouns; avoid fluff, brands, prices, and CTAs.\n\n"
            "Separate listings with a line containing only: ---\n\n"
            "User need: {query}\n"
            "Context:\n{context_block}\n\n"
            "Listing 1:"
        ),
    ),
    PromptVariant(
        key="v5_comprehensive",
        label="Comprehensive (≤350 tok/doc)",
        target_tokens_per_doc=350,
        prompt_template=(
            "You write hypothetical product listings for semantic search. "
            "Catalog items are short titles plus plain descriptions (materials, use case). "
            "Your text is embedded and matched against that index — write like a catalog entry, not an ad.\n\n"
            "Produce exactly {num_docs} listings. "
            "Each listing should be a COMPREHENSIVE product description of up to 350 tokens, "
            "covering materials, intended use, key features, target audience, technical "
            "specifications, and common use cases. "
            "Each listing must be a DIFFERENT plausible product angle for the same need. "
            "Use concrete nouns; avoid fluff, brands, prices, and CTAs.\n\n"
            "Separate listings with a line containing only: ---\n\n"
            "User need: {query}\n"
            "Context:\n{context_block}\n\n"
            "Listing 1:"
        ),
    ),
]


# ══════════════════════════════════════════════════════════════════════════════
# Sample queries — derived from the task catalog
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE_QUERIES: List[Dict[str, str]] = [
    {"query": "I need a thoughtful birthday gift for my friend who loves gardening", "task_id": "swt_gardening_birthday_gift"},
    {"query": "Looking for a laptop under 1200 euros for studying and coding", "task_id": "swt_laptop_budget"},
    {"query": "How can I improve my home study environment for better focus", "task_id": "swt_study_environment"},
    {"query": "I want to restart my fitness routine after a long break", "task_id": "swt_fitness_restart"},
    {"query": "I'm deciding what pet to get and need to set up its basic care", "task_id": "swt_pet_decision_and_setup"},
    {"query": "Starting a new hobby that fits my busy schedule and budget", "task_id": "swt_new_hobby_lifestyle"},
    {"query": "Need photography equipment for a community event", "task_id": "swt_photography_event"},
    {"query": "Planning a memorable 10-year anniversary surprise", "task_id": "swt_anniversary_surprise"},
]


# ══════════════════════════════════════════════════════════════════════════════
# LLM call — direct Ollama API (bypasses LLMClient to control num_predict precisely)
# ══════════════════════════════════════════════════════════════════════════════

def call_ollama(prompt: str, model: str, ollama_url: str, num_predict: int, temperature: float = HYDE_TEMPERATURE) -> str:
    """Single non-streaming Ollama /api/chat call. Returns the raw text or raises."""
    url = f"{ollama_url.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "think": False,
        "stream": False,
        "keep_alive": -1,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
            "num_ctx": 4096,
        },
    }
    resp = requests.post(url, json=payload, timeout=300)
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def ollama_is_up(ollama_url: str) -> bool:
    try:
        r = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=5)
        return r.ok
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Generation record
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class GenerationRecord:
    variant_key: str
    variant_label: str
    target_tokens_per_doc: int
    query: str
    task_id: str
    generation_idx: int
    raw_output: str
    token_count: int
    latency_ms: float
    model: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ══════════════════════════════════════════════════════════════════════════════
# Stats
# ══════════════════════════════════════════════════════════════════════════════

def _percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    s = sorted(data)
    k = (len(s) - 1) * p
    f = int(k)
    c = min(f + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


def compute_stats(token_counts: List[int], latencies: List[float]) -> Dict:
    return {
        "n_samples": len(token_counts),
        "token_mean": round(statistics.mean(token_counts), 1) if token_counts else 0,
        "token_std": round(statistics.stdev(token_counts), 1) if len(token_counts) > 1 else 0.0,
        "token_min": min(token_counts) if token_counts else 0,
        "token_max": max(token_counts) if token_counts else 0,
        "token_p50": round(_percentile(token_counts, 0.50), 1),
        "token_p95": round(_percentile(token_counts, 0.95), 1),
        "latency_mean_ms": round(statistics.mean(latencies), 1) if latencies else 0,
        "latency_p50_ms": round(_percentile(latencies, 0.50), 1),
        "latency_p95_ms": round(_percentile(latencies, 0.95), 1),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Main experiment loop
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment(
    generations: int,
    ollama_url: str,
    model: str,
    output_dir: Path,
    num_docs: int,
    quick: bool,
) -> None:
    queries = SAMPLE_QUERIES[:2] if quick else SAMPLE_QUERIES
    variants = PROMPT_VARIANTS[:2] if quick else PROMPT_VARIANTS

    total_calls = len(variants) * len(queries) * generations
    print(f"\n{'=' * 70}")
    print(f"  HyDE Token-Length Experiment")
    print(f"  Model:          {model}")
    print(f"  Ollama URL:     {ollama_url}")
    print(f"  Variants:       {len(variants)}")
    print(f"  Queries:        {len(queries)}")
    print(f"  Generations:    {generations}")
    print(f"  Total LLM calls: {total_calls}")
    print(f"  Output:         {output_dir}")
    print(f"{'=' * 70}\n")

    output_dir.mkdir(parents=True, exist_ok=True)
    generations_file = output_dir / "generations.jsonl"
    summary_file = output_dir / "summary.json"
    report_file = output_dir / "summary.txt"

    all_records: List[GenerationRecord] = []
    call_num = 0

    with open(generations_file, "w") as f:
        for variant in variants:
            print(f"\n── Variant: {variant.label} ──")

            for sample in queries:
                for gen_idx in range(generations):
                    call_num += 1
                    prompt = variant.prompt_template.format(
                        num_docs=num_docs,
                        tokens_per_doc=variant.target_tokens_per_doc,
                        query=sample["query"],
                        context_block=sample["task_id"],
                    )

                    # num_predict = enough headroom for all docs in one call
                    num_predict = min(2048, num_docs * variant.target_tokens_per_doc + 100)

                    print(f"  [{call_num}/{total_calls}] {variant.key} / {sample['task_id']} / gen#{gen_idx+1} ...", end=" ", flush=True)

                    try:
                        t0 = time.perf_counter()
                        raw = call_ollama(prompt, model, ollama_url, num_predict)
                        latency_ms = (time.perf_counter() - t0) * 1000
                        tok = count_embedding_tokens(raw)
                        print(f"{tok} tok, {latency_ms:.0f}ms")
                    except Exception as e:
                        print(f"FAILED: {e}")
                        raw = ""
                        tok = 0
                        latency_ms = 0.0

                    rec = GenerationRecord(
                        variant_key=variant.key,
                        variant_label=variant.label,
                        target_tokens_per_doc=variant.target_tokens_per_doc,
                        query=sample["query"],
                        task_id=sample["task_id"],
                        generation_idx=gen_idx,
                        raw_output=raw,
                        token_count=tok,
                        latency_ms=latency_ms,
                        model=model,
                    )
                    all_records.append(rec)
                    f.write(json.dumps(asdict(rec)) + "\n")
                    f.flush()

    # ── Aggregate ──────────────────────────────────────────────────────────
    summary: Dict = {"variants": [], "config": {
        "model": model,
        "ollama_url": ollama_url,
        "generations_per_query": generations,
        "num_docs": num_docs,
        "total_queries": len(queries),
        "total_calls": total_calls,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }}

    for variant in variants:
        recs = [r for r in all_records if r.variant_key == variant.key]
        tokens = [r.token_count for r in recs if r.token_count > 0]
        lats = [r.latency_ms for r in recs if r.latency_ms > 0]
        stats = compute_stats(tokens, lats)
        stats["variant_key"] = variant.key
        stats["variant_label"] = variant.label
        stats["target_tokens_per_doc"] = variant.target_tokens_per_doc
        summary["variants"].append(stats)

    summary_file.write_text(json.dumps(summary, indent=2))

    # ── Human-readable report ─────────────────────────────────────────────
    lines = [
        "HyDE Token-Length Experiment — Summary",
        "=" * 70,
        f"Model:       {model}",
        f"Generations: {generations} per query × {len(queries)} queries",
        f"Total calls: {total_calls}",
        "",
        f"{'Variant':<35} {'Target':>7} {'Mean':>7} {'Std':>7} {'Min':>6} {'Max':>6} {'p50':>7} {'p95':>7}  Latency(mean/p50/p95 ms)",
        "-" * 120,
    ]
    for v in summary["variants"]:
        lines.append(
            f"{v['variant_label']:<35} {v['target_tokens_per_doc']:>7} "
            f"{v['token_mean']:>7.0f} {v['token_std']:>7.0f} "
            f"{v['token_min']:>6} {v['token_max']:>6} "
            f"{v['token_p50']:>7.0f} {v['token_p95']:>7.0f}  "
            f"{v['latency_mean_ms']:>7.0f} / {v['latency_p50_ms']:>7.0f} / {v['latency_p95_ms']:>7.0f}"
        )
    report = "\n".join(lines) + "\n"
    report_file.write_text(report)
    print(f"\n{report}")
    print(f"\nResults saved to: {output_dir}")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="HyDE token-length sweet-spot experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m experiments.hyde_token_length --generations 10
  python -m experiments.hyde_token_length --generations 5 --quick
  python -m experiments.hyde_token_length --generations 20 --num-docs 3
        """,
    )
    parser.add_argument("--generations", type=int, default=10, help="Number of LLM generations per variant per query (default: 10)")
    parser.add_argument("--ollama-url", type=str, default="http://localhost:9999", help="Ollama API base URL")
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL, help=f"Ollama model name (default: {DEFAULT_MODEL})")
    parser.add_argument("--num-docs", type=int, default=2, help="Number of HyDE docs per generation (default: 2)")
    parser.add_argument("--quick", action="store_true", help="Smoke test: 2 variants × 2 queries × 1 generation")
    parser.add_argument("--output-dir", type=str, default=None, help="Override output directory")
    args = parser.parse_args()

    # ── Output directory ────────────────────────────────────────────────────
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        output_dir = Path(__file__).resolve().parent / "output" / f"hyde_token_length_{ts}"

    # ── Preflight ──────────────────────────────────────────────────────────
    print("Checking Ollama...", end=" ", flush=True)
    if not ollama_is_up(args.ollama_url):
        print("NOT RUNNING")
        print(f"\n  Start Ollama first:")
        print(f"    ./launch.sh --host   # or")
        print(f"    ollama serve &")
        print(f"\n  Then re-run this script.")
        sys.exit(1)
    print("OK")

    # ── Run ─────────────────────────────────────────────────────────────────
    run_experiment(
        generations=args.generations,
        ollama_url=args.ollama_url,
        model=args.model,
        output_dir=output_dir,
        num_docs=args.num_docs,
        quick=args.quick,
    )


if __name__ == "__main__":
    main()
