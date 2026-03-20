# RecSys Benchmark Suite — Usage Guide

Three files, three layers. Each builds on the previous and can be used independently.

```
recsys_v2.py      — 20 classic/neural models, full metric suite, charts
recsys_llm.py     — LLM/RAG rerankers, conversational system, prompt benchmarks
USAGE.md          — this file
```

---

## Quick install

```bash
pip install pandas numpy scipy scikit-learn implicit torch matplotlib pyyaml requests

# For LLM features (pick what you need)
pip install anthropic openai         # cloud backends
# or: brew install ollama && ollama pull llama3.2   # local, free
```

---

## 1. Classic benchmark (recsys_v2.py)

```bash
# Fast run — MovieLens 100K, 300 eval users, all 20 models
python recsys_v2.py

# Production dataset
python recsys_v2.py --dataset ml-1m --eval-users 1000 --k 10

# Skip PyTorch (faster on CPU-only machines)
python recsys_v2.py --no-neural

# Change negative sampling strategy (affects training quality)
python recsys_v2.py --neg pop_biased
# options: uniform | pop_biased | hard
```

**What you get:**
- `recsys_output/results.csv` — full metric table
- `recsys_output/config.json` — reproducible config
- Five charts: accuracy bars, radar, accuracy-vs-diversity scatter, heatmap, timing

---

## 2. LLM reranker benchmark (recsys_llm.py)

```bash
# Offline mode — no API key, uses deterministic mock backend
python recsys_llm.py --demo

# With Anthropic (cheapest: haiku, ~$0.001 per eval user)
python recsys_llm.py --demo --provider anthropic --api-key sk-ant-...

# With OpenAI
python recsys_llm.py --demo --provider openai --api-key sk-...

# With local Ollama (free, ~2× slower than cloud)
ollama serve && ollama pull llama3.2
python recsys_llm.py --demo --provider ollama --model llama3.2

# Full benchmark — LLM rerankers vs all v2 models (adds ~3 extra rows to table)
python recsys_llm.py --benchmark --provider anthropic --api-key sk-ant-... --eval-users 100

# Prompt strategy comparison (zero-shot vs few-shot vs CoT vs multi-objective)
python recsys_llm.py --prompt-bench --provider anthropic --api-key sk-ant-...
```

---

## 3. Programmatic usage

### 3a. Classic models only

```python
from recsys_v2 import RecConfig, download_movielens_100k, build_dataset
from recsys_v2 import EASERecommender, ALSRecommender, run_experiment

cfg     = RecConfig(dataset="ml-100k", k=10, n_eval_users=300)
results = run_experiment(cfg)
# → prints accuracy + beyond-accuracy table, saves charts
```

### 3b. LLM backend (pluggable)

```python
from recsys_llm import LLMBackend

# Cloud
llm = LLMBackend.anthropic("sk-ant-...")       # claude-haiku-4-5-20251001 default
llm = LLMBackend.openai("sk-...")              # gpt-4o-mini default
llm = LLMBackend.ollama("llama3.2")            # local, no key

# Mock — for testing, no API calls
llm = LLMBackend.mock()

resp = llm.call("Recommend 3 movies for a sci-fi fan.")
print(resp.text, resp.latency_ms, "ms")
print(llm.stats())  # total calls, tokens, estimated cost
```

### 3c. RAG reranker drop-in

```python
from recsys_v2  import build_dataset, EASERecommender, RecConfig, evaluate_model
from recsys_llm import ZeroShotLLMReranker, FewShotLLMReranker, LLMBackend

cfg     = RecConfig()
dataset = build_dataset(ratings, items, cfg)
recall  = EASERecommender(); recall.fit(dataset)
llm     = LLMBackend.anthropic()

# Zero-shot: CF recall → LLM rerank
reranker = ZeroShotLLMReranker(recall, llm, item_meta, n_candidates=30)
reranker.fit(dataset)

# Evaluate with same protocol as all v2 models → directly comparable
metrics = evaluate_model(reranker.score, dataset, cfg)
print(metrics)  # hr, ndcg, mrr, ild, novelty, gini ...
```

### 3d. Conversational system

```python
from recsys_llm import ConversationalRecSys, LLMBackend

crs = ConversationalRecSys(
    recall_model    = recall,          # any fitted v2 model
    llm             = llm,
    dataset         = dataset,
    item_meta       = item_meta,       # {item_id: "Title (genres)"}
    rerank_strategy = "zero_shot",     # "zero_shot" | "few_shot" | "multi_objective"
    k               = 5,
    epsilon_greedy  = 0.05,            # 5% random exploration
)

session = crs.new_session(user_id=42)
result  = crs.turn(session, "I want a dark thriller set in space")
print(result["response"])   # natural language reply
print(result["ranked_ids"]) # item ids

result2 = crs.turn(session, "Something shorter please")
print(result2["response"])

print(session.preference_summary())
# → "genres: thriller | constraints: shorter"
```

### 3e. Multi-objective reranking (ad strategy research)

```python
from recsys_llm import MultiObjectiveLLMReranker

# Retention-optimised (diversity/novelty over raw CTR)
reranker = MultiObjectiveLLMReranker(
    recall_model     = recall,
    llm              = llm,
    item_meta        = item_meta,
    relevance_weight = 0.4,   # lower → less filter bubble
    diversity_weight = 0.3,
    novelty_weight   = 0.2,
    freshness_weight = 0.1,
)

# Native ad injection (sponsored item gets natural placement)
reranker = MultiObjectiveLLMReranker(
    recall_model   = recall,
    llm            = llm,
    item_meta      = item_meta,
    sponsored_item = {"id": 99, "title": "Sponsored Movie Title"},
)
```

### 3f. Prompt strategy comparison

```python
from recsys_llm import PromptStrategyBenchmark

bench   = PromptStrategyBenchmark(recall, llm, dataset, cfg, item_meta)
results = bench.run(n_users=50)
PromptStrategyBenchmark.print_table(results)
# Compares: zero_shot | few_shot | chain_of_thought | multi_objective
```

### 3g. LLM-as-Judge evaluation

```python
from recsys_llm import LLMAsJudge

judge  = LLMAsJudge(llm)
scores = judge.evaluate(
    user_history    = ["Inception", "The Matrix", "Interstellar"],
    recommendations = ["Dune", "Arrival", "Blade Runner 2049"],
    explanation     = "You love sci-fi with complex narratives.",
    user_query      = "thoughtful sci-fi",
)
print(scores)
# → {"relevance": 4.5, "diversity": 3.0, "naturalness": 4.0, ...}
```

---

## 4. Extending with Amazon data

```python
from recsys_v2 import get_amazon_sample_url, build_dataset, RecConfig

url  = get_amazon_sample_url("Video_Games")   # or "Electronics", "Books", ...
df   = pd.read_csv(url, compression="gzip",
                   names=["item_id","user_id","rating","timestamp"])
cfg  = RecConfig(dataset="amazon_video_games")
# No item metadata for Amazon → content-based model will skip TF-IDF gracefully
dataset = build_dataset(df, items=None, cfg=cfg)
```

---

## 5. Research recipes

### Accuracy vs diversity frontier
```python
results = {}
for eps in [0.0, 0.05, 0.1, 0.2, 0.3]:
    cfg.epsilon = eps  # used by epsilon_greedy_rerank in ConversationalRecSys
    r = run_experiment(cfg)
    results[f"eps={eps}"] = r["ALS"]
# Plot NDCG vs Gini across epsilon values → filter-bubble curve
```

### Negative sampling ablation
```python
for strat in ["uniform", "pop_biased", "hard"]:
    cfg.neg_strategy = strat
    r = run_experiment(cfg)
    print(strat, r["BPR"]["ndcg"])
```

### LLM cost vs quality
```python
for n_cand in [10, 20, 50, 100]:
    reranker = ZeroShotLLMReranker(recall, llm, item_meta, n_candidates=n_cand)
    reranker.fit(dataset)
    m = evaluate_model(reranker.score, dataset, cfg)
    print(f"n_cand={n_cand}  NDCG={m['ndcg']:.4f}  cost=${llm.stats()['est_cost_usd']:.4f}")
```

---

## 6. File structure

```
recsys_v2.py
  RecConfig               — serialisable experiment config
  RecDataset              — standard data container
  NegativeSampler         — uniform / pop_biased / hard negatives
  RandomRecommender       — lower bound baseline
  PopularityRecommender   — strong non-personalised baseline
  ItemKNNRecommender      — memory-based CF
  EASERecommender         — closed-form item autoencoder (★ often beats deep)
  SLIMRecommender         — sparse item-item regression
  SVDRecommender          — Funk-SVD latent factors
  SVDPlusPlusRecommender  — SVD + implicit feedback vectors
  ALSRecommender          — weighted ALS (via `implicit`)
  BPRRecommender          — pairwise ranking ALS (via `implicit`)
  ContentBasedRecommender — TF-IDF genre profiles
  FMRecommender           — factorization machines (BPR loss)
  AutoRecRecommender      — item autoencoder (PyTorch)
  NeuMFRecommender        — GMF + MLP two-tower (PyTorch)
  GRU4RecRecommender      — GRU sequential (PyTorch)
  SASRecRecommender       — self-attention sequential (PyTorch)
  WeightedHybridRecommender
  CascadeHybridRecommender
  SwitchingHybridRecommender
  ColdStartHandler
  Explainer
  ThompsonSamplingBandit
  NegativeSampler
  evaluate_model()        — LOO + 100-way neg sampling eval
  plot_results()          — 5 matplotlib charts

recsys_llm.py  (imports recsys_v2 softly — works standalone too)
  LLMBackend              — Anthropic / OpenAI / Ollama / Mock
  P5PromptLibrary         — 5 task prompt templates
  RecQuery                — structured intent slots
  IntentParser            — NL → RecQuery (LLM or rule-based)
  ZeroShotLLMReranker     — CF recall + LLM rerank
  FewShotLLMReranker      — + in-context user history examples
  MultiObjectiveLLMReranker — CTR / diversity / novelty / freshness / ads
  ConversationalSession   — multi-turn state, slots, critiques, seen-items
  ConversationalRecSys    — full chat loop
  LLMAsJudge              — LLM evaluation of rec quality
  PromptStrategyBenchmark — zero-shot vs few-shot vs CoT vs multi-obj
  run_llm_benchmark()     — drops into v2 evaluate_model() protocol
```

---

## 7. Key papers

| Model | Paper |
|---|---|
| ItemKNN | Sarwar et al., *Item-Based Collaborative Filtering* (WWW 2001) |
| SVD++ | Koren, *Factorization Meets the Neighborhood* (KDD 2008) |
| ALS | Hu, Koren & Volinsky, *Collaborative Filtering for Implicit Feedback* (ICDM 2008) |
| BPR | Rendle et al., *BPR: Bayesian Personalized Ranking* (UAI 2009) |
| FM | Rendle, *Factorization Machines* (ICDM 2010) |
| EASE^R | Steck, *Embarrassingly Shallow Autoencoders* (WWW 2019) |
| SLIM | Ning & Karypis, *SLIM: Sparse Linear Methods* (ICDM 2011) |
| AutoRec | Sedhain et al., *AutoRec: Autoencoders Meet Collaborative Filtering* (WWW 2015) |
| NeuMF | He et al., *Neural Collaborative Filtering* (WWW 2017) |
| GRU4Rec | Hidasi et al., *Session-Based Recommendations with RNNs* (ICLR 2016) |
| SASRec | Kang & McAuley, *Self-Attentive Sequential Recommendation* (ICDM 2018) |
| P5 | Geng et al., *Recommendation as Language Processing* (RecSys 2022) |
| LLMRank | Hou et al., *LLMs are Zero-Shot Rankers for RecSys* (ECIR 2024) |
| LLM-as-Judge | Zheng et al., *Judging LLM-as-a-Judge with MT-Bench* (NeurIPS 2023) |

---

## 8. RAG + PEFT extension (recsys_rag_peft.py)

```bash
pip install scipy                          # statistical tests (already in v2)
pip install sentence-transformers          # dense retrieval (optional)
pip install transformers peft accelerate   # PEFT per user (optional)

# BM25 + dense + hybrid — no API key needed
python recsys_rag_peft.py

# With LLM rerankers
python recsys_rag_peft.py --provider anthropic --api-key sk-ant-...

# Include per-user LoRA adapters
python recsys_rag_peft.py --provider anthropic --api-key sk-ant-... \
    --include-peft --peft-users 50

# Full suite: hybrid RAG + prompt benchmark + LLM judge
python recsys_rag_peft.py --provider anthropic --api-key sk-ant-... \
    --include-peft --prompt-bench --eval-users 200
```

### Programmatic — one-call builder

```python
from recsys_v2       import RecConfig, build_dataset, EASERecommender
from recsys_llm      import LLMBackend
from recsys_rag_peft import build_rag_pipeline

llm      = LLMBackend.anthropic("sk-ant-...")
recall   = EASERecommender(); recall.fit(dataset)
pipeline = build_rag_pipeline(dataset, cfg, llm, item_meta, recall,
                               include_peft=True, peft_train_users=50)

results = pipeline["benchmark"].run(n_eval_users=200)
pipeline["benchmark"].print_report(results)
```

### Individual components

```python
from recsys_rag_peft import (BM25RecommenderAdapter, DenseRetriever,
                               HybridRAGRetriever, LLMUserProfiler,
                               EnhancedLLMAsJudge, EnhancedPromptStrategyBenchmark,
                               PerUserPEFTReranker, RAGvsPEFTBenchmark)

# BM25 standalone
bm25 = BM25RecommenderAdapter(item_texts)
bm25.fit(dataset)
scores = bm25.score(user_id=42, item_ids=[1, 2, 3])

# Hybrid RAG
hybrid = HybridRAGRetriever(bm25, dense, bm25_weight=1.0, dense_weight=1.0)
hybrid.fit(dataset)
ablation = hybrid.ablation(uid=42, item_ids=[1, 2, 3])
# → {"bm25": {...}, "dense": {...}, "hybrid": {...}}

# LLM user profiler
profiler = LLMUserProfiler(llm, item_meta)
profile  = profiler.get_or_create(user_id=42, history=[1, 7, 23, 99])
print(profile.summary)           # "User enjoys cerebral sci-fi..."
print(profile.genre_preferences) # ["Sci-Fi", "Thriller"]
print(profile.to_query_string()) # BM25 query from profile

# Enhanced LLM-as-judge
judge   = EnhancedLLMAsJudge(llm)
scores  = judge.evaluate(user_history, recommendations,
                          traditional_metrics={"hr": 0.6, "ndcg": 0.4})
results = judge.batch_evaluate_and_correlate(cases, trad_results)
judge.print_correlation_table(results["correlations"])

# Enhanced prompt benchmark (with stats)
bench   = EnhancedPromptStrategyBenchmark(recall, llm, dataset, cfg, item_meta)
results = bench.run(n_users=100)
bench.print_full_report(results)
# Shows: NDCG, cold/warm split, Cohen's d, Wilcoxon p-values, token efficiency

# PEFT per user
peft = PerUserPEFTReranker(item_meta, base_model_name="gpt2", train_steps=30)
peft.fit(dataset, fit_users=list(dataset.ground_truth.keys())[:50])
print(peft.adapter_stats())  # {"adapters": 50, "avg_size_mb": 0.31, ...}
```

### File structure (recsys_rag_peft.py)

```
BM25Retriever               — Robertson BM25, pure Python, no deps
BM25RecommenderAdapter      — wraps BM25 in v2 .score() interface
DenseRetriever              — cosine ANN; SBERT or TF-IDF fallback
HybridRAGRetriever          — RRF fusion of BM25 + dense
  .ablation()               — returns all three score dicts for analysis
UserProfile                 — structured NL taste profile dataclass
LLMUserProfiler             — history → UserProfile via LLM
  .batch_profile()          — bulk profile generation
  .profile_diversity()      — measure personalisation depth
ProfileAwareLLMReranker     — ZeroShot + profile injection (better prompts)
EnhancedLLMAsJudge          — judge + Spearman corr + disagreement analysis
  .batch_evaluate_and_correlate()
  .print_correlation_table()
EnhancedPromptStrategyBenchmark — zero/few/CoT/multi-obj + Wilcoxon + Cohen's d
  .run()                    — returns per-user scores for statistical analysis
  .print_full_report()      — cold/warm split, effect sizes, token efficiency
PerUserPEFTReranker         — LoRA adapter per user (GPT-2 base)
  .fit()                    — trains N user adapters
  .adapter_stats()          — storage and coverage report
RAGvsPEFTBenchmark          — head-to-head eval on v2 protocol
  .register()               — plug in any model
  .run()                    — returns full metric dict
  .print_report()           — cold/warm + timing breakdown
build_rag_pipeline()        — one-call builder for everything above
```

---

## 9. HuggingFace local backends (recsys_hf_backend.py)

Four backends, zero API cost. Every downstream model in `recsys_llm` and
`recsys_rag_peft` works unchanged — just swap the `llm=` argument.

```
Hardware tier       | Backend          | Install
────────────────────┼──────────────────┼──────────────────────────────────
laptop / no GPU     | .llamacpp()      | pip install llama-cpp-python
consumer GPU 8-16GB | .huggingface()   | pip install transformers accelerate
consumer GPU 4-6GB  | .huggingface(    | pip install transformers bitsandbytes
                    |   load_in_4bit)  |
multi-GPU server    | .vllm()          | pip install vllm  (then start server)
HF TGI docker       | .tgi()           | docker pull ghcr.io/huggingface/tgi
```

### Option A — patch existing LLMBackend (cleanest)

```python
from recsys_llm        import LLMBackend
from recsys_hf_backend import patch_llm_backend

patch_llm_backend()   # one call; adds .huggingface() etc. to LLMBackend

# Now everything works exactly like Anthropic/OpenAI
llm = LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")
llm = LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct", load_in_4bit=True)
llm = LLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF")
llm = LLMBackend.vllm("meta-llama/Llama-3.1-70B-Instruct")
```

### Option B — use HFLLMBackend directly

```python
from recsys_hf_backend import HFLLMBackend

llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")
```

### Laptop / CPU — llama.cpp

```python
# Auto-downloads Q4_K_M GGUF from HF Hub (~4.5 GB)
llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF")

# Tiny 1.5B — runs in 1 GB RAM, ~8 tok/s on any laptop
llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-1.5B-Instruct-GGUF")

# Apple Silicon — offload everything to Metal (fast)
llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF", n_gpu_layers=-1)

# Load from local file
llm = HFLLMBackend.llamacpp("/models/mistral-7b-q4.gguf")
```

### Consumer GPU — transformers

```python
# Full precision (needs ~14 GB VRAM for 7B)
llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")

# 4-bit NF4 quantisation — fits in 4 GB VRAM, ~2% quality loss
llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct", load_in_4bit=True)

# 8-bit quantisation — fits in 7 GB VRAM, ~1% quality loss
llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct", load_in_8bit=True)

# Tiny 3B model — good for quick iteration
llm = HFLLMBackend.huggingface("meta-llama/Llama-3.2-3B-Instruct")
```

### Multi-GPU server — vLLM

```bash
# Start the server (one-time)
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct \
    --tensor-parallel-size 4          # number of GPUs
```

```python
llm = HFLLMBackend.vllm("Qwen/Qwen2.5-72B-Instruct",
                          base_url="http://localhost:8000")
```

### Speed + quality benchmark

```bash
# Test any backend before running the full eval
python recsys_hf_backend.py bench --backend hf --model Qwen/Qwen2.5-7B-Instruct
python recsys_hf_backend.py bench --backend hf --model Qwen/Qwen2.5-7B-Instruct --4bit
python recsys_hf_backend.py bench --backend llamacpp --model Qwen/Qwen2.5-7B-Instruct-GGUF
python recsys_hf_backend.py bench --backend vllm --model Qwen/Qwen2.5-72B-Instruct

# Or in Python
from recsys_hf_backend import benchmark_backend
stats = benchmark_backend(llm, n_calls=10)
# → avg_latency_s, avg_tok_per_s, json_parse_rate, top1_consistency
```

### Plug into the full pipeline — zero changes

```python
from recsys_hf_backend import HFLLMBackend, patch_llm_backend
from recsys_rag_peft    import build_rag_pipeline

patch_llm_backend()
llm = LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct", load_in_4bit=True)

# Everything downstream is identical
pipeline = build_rag_pipeline(dataset, cfg, llm, item_meta, recall)
results  = pipeline["benchmark"].run(n_eval_users=200)
```

### Recommended models

| Model | Size | VRAM | Notes |
|---|---|---|---|
| `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | 3 GB | best tiny model, runs on CPU |
| `Qwen/Qwen2.5-7B-Instruct` | 7B | 14 GB / 4 GB (4bit) | best 7B overall |
| `meta-llama/Llama-3.2-3B-Instruct` | 3B | 6 GB | fast, good JSON output |
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | 14 GB / 4 GB (4bit) | strong structured output |
| `google/gemma-2-9b-it` | 9B | 18 GB | high quality |
| `meta-llama/Llama-3.1-70B-Instruct` | 70B | 4× A100 | near-frontier quality |
| `Qwen/Qwen2.5-72B-Instruct` | 72B | 4× A100 | best open model currently |
