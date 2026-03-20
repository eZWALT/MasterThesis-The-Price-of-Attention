"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   HUGGINGFACE LOCAL BACKEND  (recsys_hf_backend.py)                        ║
║   Drop-in patch for recsys_llm.LLMBackend                                  ║
║                                                                             ║
║   Adds four factory methods to LLMBackend:                                 ║
║     .huggingface()   — transformers pipeline, any HF model, CPU/GPU        ║
║     .vllm()          — vLLM server (fast batched inference, GPU only)       ║
║     .tgi()           — Text Generation Inference docker (HuggingFace)       ║
║     .llamacpp()      — llama.cpp GGUF models (CPU-optimised quantisation)   ║
║                                                                             ║
║   All four return a standard LLMBackend with the same .call() interface    ║
║   as Anthropic/OpenAI — everything in recsys_llm and recsys_rag_peft       ║
║   works unchanged.                                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

HARDWARE GUIDE
══════════════

  ┌──────────────────┬──────────────┬──────────────┬────────────────────────┐
  │ Backend          │ VRAM needed  │ Speed        │ Best for               │
  ├──────────────────┼──────────────┼──────────────┼────────────────────────┤
  │ llamacpp (GGUF)  │ 0  (CPU ok)  │ ~1-5 tok/s   │ laptop, no GPU         │
  │ transformers     │ 4-8 GB       │ ~10-30 tok/s │ single GPU dev machine │
  │ transformers 4bit│ 2-4 GB       │ ~8-20 tok/s  │ consumer GPU (RTX 3060)│
  │ TGI (docker)     │ 8-80 GB      │ ~80-300 tok/s│ multi-GPU server       │
  │ vLLM             │ 8-80 GB      │ ~200-500 tok/s│ A100/H100 cluster     │
  └──────────────────┴──────────────┴──────────────┴────────────────────────┘

RECOMMENDED MODELS (free, HuggingFace Hub)
══════════════════════════════════════════

  Tier 1 — laptop / CPU (≤ 8 GB RAM)
    LLMBackend.llamacpp("Qwen/Qwen2.5-1.5B-Instruct-GGUF")
    LLMBackend.llamacpp("microsoft/Phi-3-mini-4k-instruct-gguf")

  Tier 2 — consumer GPU (8-16 GB VRAM)
    LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")       # best 7B overall
    LLMBackend.huggingface("mistralai/Mistral-7B-Instruct-v0.3")
    LLMBackend.huggingface("meta-llama/Llama-3.2-3B-Instruct")  # tiny + good
    LLMBackend.huggingface("google/gemma-2-9b-it")

  Tier 2b — same GPU, quantised (fits in 4-6 GB VRAM)
    LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct", load_in_4bit=True)
    LLMBackend.huggingface("mistralai/Mistral-7B-Instruct-v0.3", load_in_4bit=True)

  Tier 3 — multi-GPU / cloud A100 (40-80 GB VRAM)
    LLMBackend.vllm("meta-llama/Llama-3.1-70B-Instruct")
    LLMBackend.vllm("Qwen/Qwen2.5-72B-Instruct")
    LLMBackend.tgi("meta-llama/Llama-3.1-70B-Instruct")

INSTALL
═══════

  # Tier 1 (CPU / laptop)
  pip install llama-cpp-python           # CPU build
  CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python  # CUDA build

  # Tier 2 (single GPU)
  pip install transformers accelerate
  pip install bitsandbytes              # for load_in_4bit / load_in_8bit

  # Tier 3 (multi-GPU server)
  pip install vllm                      # also serves OpenAI-compatible API
  docker pull ghcr.io/huggingface/text-generation-inference  # TGI

USAGE
═════

  from recsys_llm           import LLMBackend
  from recsys_hf_backend    import patch_llm_backend
  patch_llm_backend()       # injects .huggingface() / .vllm() / .tgi() / .llamacpp()

  # Then use exactly like Anthropic/OpenAI:
  llm  = LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")
  resp = llm.call("Recommend 5 sci-fi movies for a user who loved Dune.")
  print(resp.text, f"({resp.latency_ms:.0f}ms, {resp.output_tokens} tokens)")

  # Or import the extended class directly (no patching needed):
  from recsys_hf_backend import HFLLMBackend
  llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct", load_in_4bit=True)
"""

# ─────────────────────────────────────────────────────────────────────────────
# 0. IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import os, time, json, re
from typing import Any, Optional

# Soft imports — each backend only needs its own dep
try:
    import torch
    HAS_TORCH = True
    _DEFAULT_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:
    HAS_TORCH = False
    _DEFAULT_DEVICE = "cpu"

try:
    import transformers
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Import LLMResponse from our module — or define a minimal stub
try:
    from recsys_llm import LLMResponse, LLMBackend
    HAS_LLM = True
except ImportError:
    HAS_LLM = False

    # Minimal stubs so the file is importable standalone
    from dataclasses import dataclass, field
    from typing import Callable

    @dataclass
    class LLMResponse:
        text: str
        model: str
        input_tokens: int  = 0
        output_tokens: int = 0
        latency_ms: float  = 0.0
        raw: Any           = None

    class LLMBackend:
        """Minimal stub — replace with the real class from recsys_llm."""
        def __init__(self, provider, model, call_fn):
            self.provider = provider; self.model = model
            self._call_fn = call_fn; self.total_calls = 0
            self.total_tokens_in = 0; self.total_tokens_out = 0
            self.total_cost_usd  = 0.0

        def call(self, prompt, system="", max_tokens=512, temperature=0.0):
            t0 = time.time()
            resp = self._call_fn(prompt, system, max_tokens, temperature)
            resp.latency_ms = (time.time() - t0) * 1000
            self.total_calls += 1
            self.total_tokens_in  += resp.input_tokens
            self.total_tokens_out += resp.output_tokens
            return resp

        def stats(self):
            return {"provider": self.provider, "model": self.model,
                    "total_calls": self.total_calls,
                    "tokens_in": self.total_tokens_in,
                    "tokens_out": self.total_tokens_out,
                    "est_cost_usd": 0.0}

        def __repr__(self):
            return f"LLMBackend({self.provider}/{self.model})"


# ─────────────────────────────────────────────────────────────────────────────
# 1. HUGGINGFACE TRANSFORMERS BACKEND
# ─────────────────────────────────────────────────────────────────────────────

def _make_hf_backend(
    model_id: str,
    device: Optional[str]  = None,
    load_in_4bit: bool     = False,
    load_in_8bit: bool     = False,
    torch_dtype: str       = "auto",
    max_new_tokens_limit: int = 1024,
    trust_remote_code: bool   = False,
) -> LLMBackend:
    """
    Build a transformers-based LLMBackend.

    Parameters
    ----------
    model_id        HuggingFace Hub ID, e.g. "Qwen/Qwen2.5-7B-Instruct"
    device          "cuda" | "cpu" | "mps" | None (auto)
    load_in_4bit    4-bit NF4 quantisation via bitsandbytes (~½ VRAM)
    load_in_8bit    8-bit LLM.int8 quantisation via bitsandbytes (~¾ VRAM)
    torch_dtype     "auto" | "float16" | "bfloat16" | "float32"
                    auto → bfloat16 on Ampere+ GPU, float32 on CPU
    max_new_tokens_limit   Hard cap on generation length (safety valve)
    trust_remote_code      Required for some models (Phi-3, etc.)

    How quantisation works
    ──────────────────────
    load_in_4bit uses QLoRA's NF4 format (bitsandbytes):
        - Weights stored in 4 bits, dequantised to bf16 for compute
        - ~25% of original VRAM: 7B model fits in ~4 GB instead of 14 GB
        - Slight quality loss (~1-3% on most benchmarks)
        - Requires bitsandbytes: pip install bitsandbytes

    load_in_8bit uses LLM.int8:
        - ~50% of original VRAM
        - Less quality loss than 4bit
        - Slower than 4bit on some hardware

    Chat template handling
    ──────────────────────
    Modern instruction-tuned models (Qwen, Llama-3, Mistral-Instruct)
    require messages to be formatted with the model's chat template.
    We use tokenizer.apply_chat_template() which handles this automatically.
    If the tokenizer has no chat template, we fall back to a simple
    <system>...<user>...<assistant> format.
    """
    if not HAS_TRANSFORMERS:
        print("⚠  pip install transformers accelerate  →  falling back to mock")
        return _make_mock_backend()

    device = device or _DEFAULT_DEVICE

    # ── Load model ────────────────────────────────────────────────────────
    print(f"  Loading {model_id} (device={device}"
          f"{', 4bit' if load_in_4bit else ''}"
          f"{', 8bit' if load_in_8bit else ''}) …")

    import transformers as _tf

    tokenizer = _tf.AutoTokenizer.from_pretrained(
        model_id, trust_remote_code=trust_remote_code)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Quantisation config
    bnb_cfg = None
    if load_in_4bit or load_in_8bit:
        try:
            import bitsandbytes  # noqa: F401
            from transformers import BitsAndBytesConfig
            bnb_cfg = BitsAndBytesConfig(
                load_in_4bit        = load_in_4bit,
                load_in_8bit        = load_in_8bit,
                bnb_4bit_use_double_quant = True,
                bnb_4bit_quant_type       = "nf4",
                bnb_4bit_compute_dtype    = torch.bfloat16 if HAS_TORCH else None,
            )
        except ImportError:
            print("  ⚠  bitsandbytes not installed — running full precision")
            bnb_cfg = None

    # dtype
    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16,
                 "float32": torch.float32, "auto": "auto"} if HAS_TORCH else {}
    t_dtype   = dtype_map.get(torch_dtype, "auto") if HAS_TORCH else None

    model_kwargs = dict(
        trust_remote_code  = trust_remote_code,
        device_map         = "auto" if device == "cuda" else None,
        quantization_config= bnb_cfg,
    )
    if t_dtype and t_dtype != "auto":
        model_kwargs["torch_dtype"] = t_dtype

    model = _tf.AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
    if device == "cpu" and not model_kwargs.get("device_map"):
        model = model.to(device)
    model.eval()

    n_params = sum(p.numel() for p in model.parameters()) / 1e9
    print(f"  Loaded {model_id} — {n_params:.1f}B params on {device} ✓")

    # ── Call function ─────────────────────────────────────────────────────

    def _call(prompt: str, system: str, max_tokens: int, temperature: float) -> LLMResponse:
        # Build chat messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # Apply model's chat template if available
        if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
            input_text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        else:
            # Fallback: simple concatenation
            sys_str = f"System: {system}\n\n" if system else ""
            input_text = f"{sys_str}User: {prompt}\nAssistant:"

        # Tokenise
        inputs = tokenizer(
            input_text, return_tensors="pt", truncation=True, max_length=2048
        ).to(device if not model_kwargs.get("device_map") else "cuda")

        n_input_tokens = inputs.input_ids.shape[-1]

        # Generation kwargs
        gen_kwargs = dict(
            max_new_tokens = min(max_tokens, max_new_tokens_limit),
            do_sample      = temperature > 0,
            pad_token_id   = tokenizer.eos_token_id,
        )
        if temperature > 0:
            gen_kwargs["temperature"] = temperature
            gen_kwargs["top_p"]       = 0.9

        # Generate
        with torch.no_grad() if HAS_TORCH else _noop_ctx():
            output_ids = model.generate(**inputs, **gen_kwargs)

        # Decode only new tokens (skip the prompt)
        new_ids    = output_ids[0][n_input_tokens:]
        output_txt = tokenizer.decode(new_ids, skip_special_tokens=True).strip()

        return LLMResponse(
            text          = output_txt,
            model         = model_id,
            input_tokens  = n_input_tokens,
            output_tokens = len(new_ids),
        )

    return LLMBackend("huggingface", model_id, _call)


class _noop_ctx:
    """Context manager no-op (used when torch is absent)."""
    def __enter__(self): return self
    def __exit__(self, *_): pass


# ─────────────────────────────────────────────────────────────────────────────
# 2. vLLM BACKEND  (OpenAI-compatible server)
# ─────────────────────────────────────────────────────────────────────────────

def _make_vllm_backend(
    model_id: str,
    base_url: str  = "http://localhost:8000",
    api_key: str   = "not-needed",
    temperature: float = 0.0,
) -> LLMBackend:
    """
    Build a vLLM backend (OpenAI-compatible server).

    vLLM exposes an OpenAI-compatible REST API, so we reuse the same
    HTTP call pattern as the OpenAI backend but point to localhost.

    START vLLM SERVER:
        pip install vllm
        python -m vllm.entrypoints.openai.api_server \\
            --model meta-llama/Llama-3.1-70B-Instruct \\
            --tensor-parallel-size 4   # number of GPUs
            --port 8000

    Why vLLM?
      - PagedAttention: batches requests sharing KV cache → ~10-20× throughput
        vs naive HuggingFace generate() for concurrent users.
      - Continuous batching: idle GPU cycles are never wasted.
      - Same model quality as HF transformers (same weights, no quantisation
        by default, though AWQ/GPTQ quantised models work too).
      - Scales from a single A100 to a multi-node cluster with --tensor-parallel.

    Cost profile:
      A100 80GB on AWS (~$3.50/hr) → ~500 tok/s throughput for 70B models.
      For benchmark eval (100 users × 30 candidates ≈ 15K tokens/user):
        100 users at 500 tok/s ≈ 3 seconds total for the entire eval set.
      Compare: Anthropic haiku at $0.001/call × 100 calls = $0.10.
      Cloud GPU pays off after ~30-50 benchmark runs.
    """
    if not HAS_REQUESTS:
        print("⚠  pip install requests  →  falling back to mock")
        return _make_mock_backend()

    def _call(prompt: str, system: str, max_tokens: int, temperature_: float) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model":       model_id,
            "messages":    messages,
            "max_tokens":  max_tokens,
            "temperature": temperature_,
        }
        headers = {"Authorization": f"Bearer {api_key}",
                   "Content-Type": "application/json"}
        r = _requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload, headers=headers, timeout=120)
        r.raise_for_status()
        data = r.json()

        choice = data["choices"][0]["message"]["content"]
        usage  = data.get("usage", {})
        return LLMResponse(
            text          = choice,
            model         = model_id,
            input_tokens  = usage.get("prompt_tokens", 0),
            output_tokens = usage.get("completion_tokens", 0),
            raw           = data,
        )

    return LLMBackend("vllm", model_id, _call)


# ─────────────────────────────────────────────────────────────────────────────
# 3. TEXT GENERATION INFERENCE (TGI) BACKEND
# ─────────────────────────────────────────────────────────────────────────────

def _make_tgi_backend(
    model_id: str,
    base_url: str = "http://localhost:8080",
) -> LLMBackend:
    """
    Build a HuggingFace TGI backend.

    TGI is HuggingFace's production inference server — it powers the
    HuggingFace Inference API and is available as a Docker image.

    START TGI SERVER:
        docker run --gpus all --shm-size 64g -p 8080:80 \\
            ghcr.io/huggingface/text-generation-inference:latest \\
            --model-id meta-llama/Llama-3.1-70B-Instruct \\
            --num-shard 4

    TGI vs vLLM:
      - TGI is HF's official server; broader model compatibility.
      - vLLM has higher raw throughput for concurrent requests.
      - TGI has built-in support for speculative decoding and GPTQ.
      - For RecSys benchmarks with sequential (not concurrent) calls,
        both are equivalent — use whichever you have running.

    TGI also exposes an OpenAI-compatible endpoint at /v1/chat/completions
    (since TGI 2.0), so the vLLM backend also works with TGI servers.
    This native TGI backend uses the /generate endpoint directly for
    slightly lower latency (skips the OpenAI-compat translation layer).
    """
    if not HAS_REQUESTS:
        print("⚠  pip install requests  →  falling back to mock")
        return _make_mock_backend()

    def _call(prompt: str, system: str, max_tokens: int, temperature: float) -> LLMResponse:
        # TGI /generate endpoint (direct, slightly faster than /v1/chat)
        sys_str  = f"{system}\n\n" if system else ""
        full_prompt = f"{sys_str}{prompt}"

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens":  max_tokens,
                "temperature":     max(temperature, 0.01),  # TGI requires > 0
                "do_sample":       temperature > 0,
                "return_full_text": False,
            },
        }
        r = _requests.post(f"{base_url}/generate",
                            json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        text = data.get("generated_text", "")

        # Token counts from TGI response
        details = data.get("details", {})
        n_out   = details.get("generated_tokens", len(text.split()))

        return LLMResponse(
            text          = text.strip(),
            model         = model_id,
            input_tokens  = len(full_prompt.split()),  # TGI doesn't always return this
            output_tokens = n_out,
            raw           = data,
        )

    return LLMBackend("tgi", model_id, _call)


# ─────────────────────────────────────────────────────────────────────────────
# 4. LLAMA.CPP BACKEND  (GGUF, CPU-optimised)
# ─────────────────────────────────────────────────────────────────────────────

def _make_llamacpp_backend(
    model_path_or_repo: str,
    filename_pattern:   str   = "*Q4_K_M.gguf",
    n_gpu_layers:       int   = 0,
    n_ctx:              int   = 4096,
    n_threads:          Optional[int] = None,
) -> LLMBackend:
    """
    Build a llama.cpp backend using llama-cpp-python.

    llama.cpp runs GGUF-quantised models efficiently on CPU (and GPU
    with n_gpu_layers > 0 for CUDA/Metal offloading).

    INSTALL:
        pip install llama-cpp-python                 # CPU only
        CMAKE_ARGS="-DLLAMA_CUDA=on" \\
            pip install llama-cpp-python             # CUDA GPU offload
        CMAKE_ARGS="-DLLAMA_METAL=on" \\
            pip install llama-cpp-python             # Apple Metal (M1/M2/M3)

    Parameters
    ----------
    model_path_or_repo   Either:
                           - a local path: "/models/qwen2.5-7b-q4.gguf"
                           - a HF repo ID: "Qwen/Qwen2.5-7B-Instruct-GGUF"
                             (auto-downloads the matching GGUF file)
    filename_pattern     GGUF file to download when using HF repo.
                         Q4_K_M is the recommended quantisation level:
                           Q2_K   — smallest, noticeable quality loss
                           Q4_K_M — good balance of size and quality  ← recommended
                           Q5_K_M — slightly better quality, larger
                           Q8_0   — near-lossless, ~2× size of Q4
    n_gpu_layers         Number of transformer layers to offload to GPU.
                         0 = CPU only.  -1 = all layers on GPU.
                         Partial offload is useful when VRAM < full model:
                           7B Q4 ≈ 4 GB; if you have 6 GB VRAM, try n_gpu_layers=28
    n_ctx                Context window size in tokens.
    n_threads            CPU threads (None = auto = physical cores)

    RECOMMENDED GGUF MODELS:
        Qwen/Qwen2.5-3B-Instruct-GGUF        — 2 GB, great quality/size
        Qwen/Qwen2.5-7B-Instruct-GGUF        — 4.5 GB, strong instruction following
        microsoft/Phi-3-mini-4k-instruct-gguf — 2.2 GB, very fast on CPU
        bartowski/Meta-Llama-3.2-3B-Instruct-GGUF — 2 GB, good for rec tasks
        bartowski/Mistral-7B-Instruct-v0.3-GGUF   — 4.5 GB, structured JSON output

    CPU PERFORMANCE TIPS:
        - Use Q4_K_M (not Q2 — too much quality loss for ranking tasks)
        - Set n_threads to physical core count (not hyperthreads)
        - On M1/M2 Mac: use Metal build → effectively "free" GPU offload
        - 7B Q4 on M2 MacBook Pro: ~25-35 tok/s
        - 7B Q4 on Intel i9 (16 threads): ~8-12 tok/s
    """
    try:
        from llama_cpp import Llama
    except ImportError:
        print("⚠  pip install llama-cpp-python  →  falling back to mock")
        return _make_mock_backend()

    # If model_path_or_repo looks like a HF repo, download GGUF
    if "/" in model_path_or_repo and not os.path.exists(model_path_or_repo):
        try:
            from huggingface_hub import hf_hub_download
            import glob
            local_dir = os.path.expanduser(f"~/.cache/llama_cpp/{model_path_or_repo.replace('/', '_')}")
            os.makedirs(local_dir, exist_ok=True)

            # List files and find matching GGUF
            from huggingface_hub import list_repo_files
            repo_files  = list(list_repo_files(model_path_or_repo))
            gguf_files  = [f for f in repo_files if f.endswith(".gguf")]
            import fnmatch
            matching    = [f for f in gguf_files
                           if fnmatch.fnmatch(os.path.basename(f), filename_pattern)]
            target_file = matching[0] if matching else (gguf_files[0] if gguf_files else None)

            if target_file is None:
                raise FileNotFoundError(f"No GGUF files in {model_path_or_repo}")

            print(f"  Downloading {target_file} from {model_path_or_repo} …")
            model_path = hf_hub_download(
                repo_id  = model_path_or_repo,
                filename = target_file,
                local_dir= local_dir,
            )
            print(f"  Downloaded → {model_path}")
        except Exception as e:
            print(f"  ⚠  GGUF download failed: {e}")
            return _make_mock_backend()
    else:
        model_path = model_path_or_repo

    print(f"  Loading GGUF: {os.path.basename(model_path)}"
          f"  (n_gpu_layers={n_gpu_layers}, n_ctx={n_ctx}) …")

    llm_cpp = Llama(
        model_path   = model_path,
        n_gpu_layers = n_gpu_layers,
        n_ctx        = n_ctx,
        n_threads    = n_threads,
        verbose      = False,
    )
    print(f"  llama.cpp model loaded ✓")

    def _call(prompt: str, system: str, max_tokens: int, temperature: float) -> LLMResponse:
        # Use OpenAI-compatible chat format (llama.cpp supports this natively)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = llm_cpp.create_chat_completion(
            messages    = messages,
            max_tokens  = max_tokens,
            temperature = max(temperature, 0.01),
        )
        text   = response["choices"][0]["message"]["content"]
        usage  = response.get("usage", {})
        return LLMResponse(
            text          = text.strip(),
            model         = os.path.basename(model_path),
            input_tokens  = usage.get("prompt_tokens", 0),
            output_tokens = usage.get("completion_tokens", 0),
            raw           = response,
        )

    return LLMBackend("llamacpp", os.path.basename(model_path), _call)


# ─────────────────────────────────────────────────────────────────────────────
# 5. MOCK FALLBACK
# ─────────────────────────────────────────────────────────────────────────────

def _make_mock_backend() -> LLMBackend:
    """Deterministic mock — used when any dep is missing."""
    import random

    def _call(prompt, system, max_tokens, temperature):
        time.sleep(0.05)
        ids    = re.findall(r'\b(\d{2,6})\b', prompt)
        ids    = list(dict.fromkeys(ids))[:20]
        random.shuffle(ids)
        text   = json.dumps({"ranked_ids": ids, "explanation": "Mock."})
        return LLMResponse(text=text, model="mock",
                            input_tokens=len(prompt)//4,
                            output_tokens=len(text)//4)

    return LLMBackend("mock", "mock", _call)


# ─────────────────────────────────────────────────────────────────────────────
# 6. HFLLMBackend — subclass with all four methods as classmethods
# ─────────────────────────────────────────────────────────────────────────────

class HFLLMBackend(LLMBackend):
    """
    LLMBackend subclass with HuggingFace factory methods.

    Usage (no patching needed):
        from recsys_hf_backend import HFLLMBackend
        llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")
        llm = HFLLMBackend.vllm("meta-llama/Llama-3.1-70B-Instruct")
        llm = HFLLMBackend.tgi("meta-llama/Llama-3.1-70B-Instruct")
        llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF")
    """

    @classmethod
    def huggingface(cls,
                    model_id: str,
                    device: Optional[str]  = None,
                    load_in_4bit: bool     = False,
                    load_in_8bit: bool     = False,
                    torch_dtype: str       = "auto",
                    trust_remote_code: bool = False) -> LLMBackend:
        """
        Load any HuggingFace instruction-tuned model locally.

        Quick examples:
            # Best 7B model for instruction following (mid-range GPU)
            llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")

            # Same model quantised to 4-bit (fits in 4 GB VRAM)
            llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct",
                                            load_in_4bit=True)

            # Tiny 1.5B model, runs on CPU in < 2 GB RAM
            llm = HFLLMBackend.huggingface("Qwen/Qwen2.5-1.5B-Instruct")

            # Llama 3.2 3B — very good quality/size ratio
            llm = HFLLMBackend.huggingface("meta-llama/Llama-3.2-3B-Instruct")
        """
        return _make_hf_backend(
            model_id, device=device,
            load_in_4bit=load_in_4bit, load_in_8bit=load_in_8bit,
            torch_dtype=torch_dtype, trust_remote_code=trust_remote_code,
        )

    @classmethod
    def vllm(cls,
             model_id: str,
             base_url: str = "http://localhost:8000",
             api_key: str  = "not-needed") -> LLMBackend:
        """
        Connect to a running vLLM server.

        Start the server:
            pip install vllm
            python -m vllm.entrypoints.openai.api_server \\
                --model Qwen/Qwen2.5-72B-Instruct \\
                --tensor-parallel-size 4

        Also works with any OpenAI-compatible server
        (LM Studio, TabbyAPI, etc.).
        """
        return _make_vllm_backend(model_id, base_url=base_url, api_key=api_key)

    @classmethod
    def tgi(cls,
            model_id: str,
            base_url: str = "http://localhost:8080") -> LLMBackend:
        """
        Connect to a HuggingFace TGI server.

        Start the server:
            docker run --gpus all --shm-size 64g -p 8080:80 \\
                ghcr.io/huggingface/text-generation-inference:latest \\
                --model-id meta-llama/Llama-3.1-70B-Instruct \\
                --num-shard 4
        """
        return _make_tgi_backend(model_id, base_url=base_url)

    @classmethod
    def llamacpp(cls,
                 model_path_or_repo: str,
                 filename_pattern: str = "*Q4_K_M.gguf",
                 n_gpu_layers: int     = 0,
                 n_ctx: int            = 4096,
                 n_threads: Optional[int] = None) -> LLMBackend:
        """
        Load a GGUF model via llama.cpp — runs on CPU, no GPU needed.

        Quick examples:
            # Download Q4_K_M GGUF from HF Hub (auto)
            llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF")

            # Load from local file
            llm = HFLLMBackend.llamacpp("/models/mistral-7b-q4.gguf")

            # Offload 20 layers to GPU (partial offload for small VRAM)
            llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF",
                                         n_gpu_layers=20)

            # Apple Silicon — offload everything to Metal (fast)
            llm = HFLLMBackend.llamacpp("Qwen/Qwen2.5-7B-Instruct-GGUF",
                                         n_gpu_layers=-1)   # -1 = all layers
        """
        return _make_llamacpp_backend(
            model_path_or_repo,
            filename_pattern=filename_pattern,
            n_gpu_layers=n_gpu_layers,
            n_ctx=n_ctx, n_threads=n_threads,
        )


# ─────────────────────────────────────────────────────────────────────────────
# 7. PATCH FUNCTION — injects methods into existing LLMBackend class
# ─────────────────────────────────────────────────────────────────────────────

def patch_llm_backend():
    """
    Monkey-patch the four HF factory methods into recsys_llm.LLMBackend.

    Call once at startup — after that, LLMBackend.huggingface() etc. work
    exactly like LLMBackend.anthropic().

    Usage:
        from recsys_llm      import LLMBackend
        from recsys_hf_backend import patch_llm_backend
        patch_llm_backend()

        llm = LLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")
    """
    if not HAS_LLM:
        print("⚠  recsys_llm not found — patch skipped. Use HFLLMBackend directly.")
        return

    from recsys_llm import LLMBackend as _Base

    _Base.huggingface = classmethod(
        lambda cls, model_id, device=None, load_in_4bit=False,
               load_in_8bit=False, torch_dtype="auto",
               trust_remote_code=False:
        _make_hf_backend(model_id, device=device,
                         load_in_4bit=load_in_4bit,
                         load_in_8bit=load_in_8bit,
                         torch_dtype=torch_dtype,
                         trust_remote_code=trust_remote_code)
    )
    _Base.vllm = classmethod(
        lambda cls, model_id, base_url="http://localhost:8000", api_key="not-needed":
        _make_vllm_backend(model_id, base_url=base_url, api_key=api_key)
    )
    _Base.tgi = classmethod(
        lambda cls, model_id, base_url="http://localhost:8080":
        _make_tgi_backend(model_id, base_url=base_url)
    )
    _Base.llamacpp = classmethod(
        lambda cls, model_path_or_repo, filename_pattern="*Q4_K_M.gguf",
               n_gpu_layers=0, n_ctx=4096, n_threads=None:
        _make_llamacpp_backend(model_path_or_repo,
                               filename_pattern=filename_pattern,
                               n_gpu_layers=n_gpu_layers,
                               n_ctx=n_ctx, n_threads=n_threads)
    )
    print("  LLMBackend patched: .huggingface() / .vllm() / .tgi() / .llamacpp() ✓")


# ─────────────────────────────────────────────────────────────────────────────
# 8. QUICK BENCHMARK — measures tok/s and JSON-parse rate per backend
# ─────────────────────────────────────────────────────────────────────────────

def benchmark_backend(llm: LLMBackend, n_calls: int = 5) -> dict:
    """
    Run a quick quality + speed benchmark on any LLMBackend.

    Tests:
      1. Raw generation speed (tok/s)
      2. JSON parse rate on a structured ranking prompt
      3. Consistency — same prompt, same top result across calls?

    Useful for comparing backends before running the full RecSys eval.

    Usage:
        llm   = HFLLMBackend.huggingface("Qwen/Qwen2.5-7B-Instruct")
        stats = benchmark_backend(llm, n_calls=10)
        print(stats)
    """
    TEST_PROMPT = textwrap.dedent("""
        USER HISTORY: Inception, The Matrix, Interstellar, Blade Runner 2049

        CANDIDATES:
          {"id": 1, "title": "Dune"}
          {"id": 2, "title": "Arrival"}
          {"id": 3, "title": "Everything Everywhere All at Once"}
          {"id": 4, "title": "Happy Gilmore"}
          {"id": 5, "title": "The Notebook"}

        Rank all 5 candidates for this user. Output JSON only:
        {"ranked_ids": [<id>, ...], "explanation": "<one sentence>"}
    """).strip()

    TEST_SYSTEM = (
        "You are an expert recommender. "
        "Output ONLY valid JSON, no preamble, no markdown."
    )

    results = []
    for i in range(n_calls):
        t0   = time.time()
        resp = llm.call(TEST_PROMPT, system=TEST_SYSTEM,
                        max_tokens=128, temperature=0.0)
        lat  = time.time() - t0

        # Try to parse JSON
        try:
            clean   = re.sub(r"```json|```", "", resp.text).strip()
            parsed  = json.loads(clean)
            top_id  = parsed.get("ranked_ids", [None])[0]
            parseable = True
        except Exception:
            top_id    = None
            parseable = False

        results.append({
            "latency_s":   round(lat, 3),
            "tok_per_s":   round(resp.output_tokens / max(lat, 0.001), 1),
            "output_tokens": resp.output_tokens,
            "json_ok":     parseable,
            "top_id":      top_id,
        })
        print(f"  call {i+1}/{n_calls}  {lat:.2f}s  "
              f"{resp.output_tokens} tok  "
              f"json={'ok' if parseable else 'fail'}  top={top_id}")

    avg_lat  = float(sum(r["latency_s"]  for r in results) / n_calls)
    avg_tps  = float(sum(r["tok_per_s"]  for r in results) / n_calls)
    json_rate = sum(1 for r in results if r["json_ok"]) / n_calls
    top_ids   = [r["top_id"] for r in results if r["top_id"] is not None]
    consistency = max(top_ids.count(x) for x in set(top_ids)) / len(top_ids) if top_ids else 0

    summary = {
        "backend":      str(llm),
        "n_calls":      n_calls,
        "avg_latency_s": round(avg_lat, 3),
        "avg_tok_per_s": round(avg_tps, 1),
        "json_parse_rate": round(json_rate, 2),
        "top1_consistency": round(consistency, 2),
        "llm_stats":    llm.stats(),
    }
    print(f"\n  avg latency: {avg_lat:.2f}s | tok/s: {avg_tps:.0f} | "
          f"json rate: {json_rate:.0%} | consistency: {consistency:.0%}")
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# 9. CLI
# ─────────────────────────────────────────────────────────────────────────────

import textwrap as _textwrap  # already imported above but make explicit for __main__

if __name__ == "__main__":
    import argparse, sys

    parser = argparse.ArgumentParser(description="HF Backend for RecSys suite")
    sub    = parser.add_subparsers(dest="cmd")

    # bench sub-command
    bench_p = sub.add_parser("bench", help="Quick speed + quality benchmark")
    bench_p.add_argument("--backend",  required=True,
                          choices=["hf", "vllm", "tgi", "llamacpp"])
    bench_p.add_argument("--model",    required=True,
                          help="Model ID or path")
    bench_p.add_argument("--4bit",     dest="quant4", action="store_true")
    bench_p.add_argument("--8bit",     dest="quant8", action="store_true")
    bench_p.add_argument("--gpu-layers", type=int, default=0)
    bench_p.add_argument("--base-url", default="http://localhost:8000")
    bench_p.add_argument("--n-calls",  type=int, default=5)

    # demo sub-command
    demo_p = sub.add_parser("demo", help="Single rec prompt demo")
    demo_p.add_argument("--backend",  required=True,
                         choices=["hf", "vllm", "tgi", "llamacpp"])
    demo_p.add_argument("--model",    required=True)
    demo_p.add_argument("--4bit",     dest="quant4", action="store_true")
    demo_p.add_argument("--gpu-layers", type=int, default=0)

    args = parser.parse_args()

    if args.cmd is None:
        parser.print_help(); sys.exit(0)

    # Build backend
    if args.backend == "hf":
        llm = HFLLMBackend.huggingface(
            args.model, load_in_4bit=args.quant4, load_in_8bit=args.quant8)
    elif args.backend == "vllm":
        llm = HFLLMBackend.vllm(args.model, base_url=args.base_url)
    elif args.backend == "tgi":
        llm = HFLLMBackend.tgi(args.model, base_url=args.base_url)
    elif args.backend == "llamacpp":
        llm = HFLLMBackend.llamacpp(args.model, n_gpu_layers=args.gpu_layers)

    if args.cmd == "bench":
        benchmark_backend(llm, n_calls=args.n_calls)

    elif args.cmd == "demo":
        resp = llm.call(
            "Given a user who liked Inception, The Matrix, and Interstellar, "
            "recommend 3 movies and explain why each fits. "
            'Output JSON: {"recommendations": [{"title": "...", "reason": "..."}]}',
            system="You are an expert movie recommender. Output JSON only.",
            max_tokens=256, temperature=0.0,
        )
        print(f"\nResponse:\n{resp.text}")
        print(f"\nStats: {llm.stats()}")
