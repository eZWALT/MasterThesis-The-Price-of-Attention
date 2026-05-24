#!/usr/bin/env python3
"""
Full Retrieval Pipeline — Diagnostic Test.

Run from project root:
    python tests/diagnostic.py

Shows detailed logs of every pipeline phase so you can follow what's happening.
"""

import time
import sys
import os
import logging

# Enable all logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def separator(title, char="─"):
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}")


def main():
    print()
    print("=" * 70)
    print("  FULL PIPELINE DIAGNOSTIC TEST")
    print("=" * 70)

    # ── PHASE 1: Environment & Configuration ──────────────────────────────────
    separator("PHASE 1: Environment & Configuration")

    import torch

    print(f"  Python:       {sys.version.split()[0]}")
    print(f"  PyTorch:      {torch.__version__}")
    print(f"  CUDA:         {torch.version.cuda if torch.cuda.is_available() else 'NOT AVAILABLE'}")
    print(f"  GPUs:         {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        free, total = torch.cuda.mem_get_info(i)
        name = torch.cuda.get_device_name(i)
        print(f"    GPU {i}: {name} -- {free/1024**3:.1f} GB free / {total/1024**3:.1f} GB total")

    import core.config as cfg

    print(f"\n  Config:")
    print(f"    LLM:            {cfg.DEFAULT_MODEL} ({cfg.LLM_BACKEND})")
    print(f"    Embedding:      {cfg.EMBEDDING_MODEL_NAME} on {cfg.EMBEDDING_DEVICE} ({cfg.EMBEDDING_DTYPE})")
    print(f"    Reranker:       {cfg.RERANKER_MODEL_NAME} on {cfg.RERANKER_DEVICE} ({cfg.RERANKER_DTYPE})")
    print(f"    Intent:         {cfg.INTENT_MODEL_NAME} on {cfg.INTENT_DEVICE}")
    print(f"    Catalog:        {cfg.CATALOG_PATH}")
    print(f"    FAISS index:    {cfg.FAISS_INDEX_PATH}")
    print(f"    Dense top-k:    {cfg.DENSE_TOP_K}")
    print(f"    Reranker top-k: {cfg.RERANKER_TOP_K}")
    print(f"    Hybrid:         {cfg.USE_HYBRID} (BM25={cfg.BM25_WEIGHT}, Dense={cfg.DENSE_WEIGHT})")

    # ── PHASE 2: Model Loading ────────────────────────────────────────────────
    separator("PHASE 2: Model Loading (cold start)")

    t0 = time.time()
    from core.retrieval import retrieve_ad

    # First call triggers full pipeline init
    ad = retrieve_ad("warmup query", [])
    load_time = time.time() - t0
    print(f"  [OK] Pipeline loaded in {load_time:.1f}s")

    print(f"\n  GPU memory after model loading:")
    for i in range(torch.cuda.device_count()):
        free, total = torch.cuda.mem_get_info(i)
        used = total - free
        print(f"    GPU {i}: {used/1024**3:.1f} GB used / {total/1024**3:.1f} GB total ({free/1024**3:.1f} GB free)")

    # ── PHASE 3: Single Query Trace ───────────────────────────────────────────
    separator("PHASE 3: Single Query Trace (detailed)")

    query = "I need a condenser microphone for recording vocals at home"
    print(f'  Query:   "{query}"')
    print(f"  Context: [] (empty)")
    print()

    t0 = time.time()
    ad = retrieve_ad(query, [])
    elapsed = time.time() - t0

    print(f"  Result ({elapsed:.3f}s):")
    print(f"    Title:    {ad.title}")
    text_display = ad.text[:120] + "..." if len(ad.text) > 120 else ad.text
    print(f"    Text:     {text_display}")
    print(f"    Score:    {ad.relevance_score:.4f}")
    print(f"    Item ID:  {ad.source_item_id}")
    print(f"    CTA:      {ad.cta}")

    # ── PHASE 4: Multi-turn Conversation Simulation ───────────────────────────
    separator("PHASE 4: Multi-turn Conversation Simulation")

    conversation = [
        {"role": "user", "content": "I want to set up a home recording studio"},
        {"role": "assistant", "content": "Great idea! What instruments or vocals will you be recording? And what is your budget?"},
        {"role": "user", "content": "Mainly vocals and acoustic guitar. Budget around 500 dollars total"},
        {"role": "assistant", "content": "For that budget I would suggest: an audio interface (~150), a condenser mic (~100-150), closed-back headphones (~80), and cables/stand."},
        {"role": "user", "content": "What microphone would you recommend for a beginner?"},
        {"role": "assistant", "content": "The Audio-Technica AT2020 is a popular choice. Large diaphragm condenser, great for vocals and acoustic instruments."},
        {"role": "user", "content": "And what about an audio interface with at least 2 inputs?"},
    ]

    print(f"  Simulating {len(conversation)} message conversation...\n")

    for msg in conversation:
        icon = "  USER" if msg["role"] == "user" else "  ASST"
        print(f"    {icon}: {msg['content'][:80]}")
    print()

    # Trigger retrieval at 3 points
    retrieval_points = [
        (2, "I want to set up a home recording studio"),
        (4, "What microphone would you recommend for a beginner?"),
        (6, "And what about an audio interface with at least 2 inputs?"),
    ]

    print(f"  Ad retrieval at {len(retrieval_points)} injection points:\n")
    for ctx_len, q in retrieval_points:
        context = conversation[:ctx_len]
        t0 = time.time()
        ad = retrieve_ad(q, context)
        elapsed = time.time() - t0
        print(f"    Turn {ctx_len // 2} | {elapsed:.2f}s | Query: \"{q[:55]}\"")
        print(f"             -> \"{ad.title[:60]}\" (score={ad.relevance_score:.3f})")
        print()

    # ── PHASE 5: Stress Test — Multiple Diverse Queries ───────────────────────
    separator("PHASE 5: Batch Query Stress Test (10 queries)")

    queries = [
        ("I need wireless headphones for running", []),
        ("Looking for a good acoustic guitar for beginners", []),
        ("What power tools do I need for basic woodworking?", []),
        ("I want to learn drums, what kit should I get?", []),
        ("Best dog food for a golden retriever puppy", []),
        ("I need a soldering iron for electronics projects", []),
        ("What skincare products help with dry skin?", []),
        ("Looking for a keyboard/piano for learning classical", []),
        ("I need storage containers for my garage", []),
        ("Recommend a good conditioner for curly hair", []),
    ]

    header = f"  {'#':<3} {'Latency':<9} {'Score':<9} {'Query':<45} Result"
    print(header)
    print(f"  {'---':<3} {'-------':<9} {'-------':<9} {'-' * 45} {'-' * 38}")

    latencies = []
    fallbacks = 0
    for i, (q, ctx) in enumerate(queries):
        t0 = time.time()
        ad = retrieve_ad(q, ctx)
        elapsed = time.time() - t0
        latencies.append(elapsed)
        status = "[!]" if ad.source_item_id == "fallback" else "[+]"
        fallbacks += 1 if ad.source_item_id == "fallback" else 0
        print(f"  {i+1:<3} {elapsed:<9.3f} {ad.relevance_score:<9.3f} {q[:45]:<45} {status} {ad.title[:36]}")

    # ── PHASE 6: Summary ──────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Pipeline load time:   {load_time:.1f}s")
    print(f"  Avg query latency:    {sum(latencies)/len(latencies):.3f}s")
    print(f"  Min / Max latency:    {min(latencies):.3f}s / {max(latencies):.3f}s")
    print(f"  P95 latency:          {sorted(latencies)[int(len(latencies) * 0.95)]:.3f}s")
    print(f"  Fallback ads:         {fallbacks}/{len(queries)}")

    vram_str = ""
    for i in range(torch.cuda.device_count()):
        free, total = torch.cuda.mem_get_info(i)
        vram_str += f"GPU{i}={(total - free) / 1024**3:.1f}GB  "
    print(f"  GPU VRAM used:        {vram_str}")
    print("=" * 70)

    if fallbacks == 0:
        print("  Status: ALL GOOD - no fallbacks")
    else:
        print(f"  Status: WARNING - {fallbacks} fallback(s)")
    print("=" * 70)
    print()

    return 0 if fallbacks == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
