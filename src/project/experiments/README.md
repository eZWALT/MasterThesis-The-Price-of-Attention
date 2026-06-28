# Experiments

Controlled experiments for tuning prompts, model parameters, and pipeline behaviour.

## Structure

```
experiments/
├── shared/                    # Reusable utilities (import, don't modify)
│   ├── ollama.py               # Health check + LLM call with metadata
│   ├── stats.py                # Mean/std/p50/p95 + table formatting
│   └── runner.py               # ExperimentCell, run_experiment(), preflight()
├── chat_prompt_length/         # Experiment: chat response length
│   ├── prompts.py              # 3 conditions × 5 prompt variants
│   ├── scenarios.py            # 5 task-catalog user messages
│   └── run.py                  # CLI entrypoint
├── output/                     # All results (gitignored)
│   └── .gitignore
└── README.md                   # This file
```

## Adding a new experiment

1. Create a new folder: `experiments/<your_experiment>/`
2. Add `__init__.py` + your experiment files (prompts, data, `run.py`)
3. In `run.py`, import from `experiments.shared` and call `run_experiment()`
4. Define your cells as a list of `ExperimentCell` objects
5. Run: `python -m experiments.<your_experiment>.run --generations N`

### Template

```python
from experiments.shared import ExperimentCell, run_experiment, preflight

cells = [
    ExperimentCell(
        variant_key="my_variant",
        variant_label="My Variant",
        cell_key="scenario_1",
        cell_label="Scenario 1",
        messages=[{"role": "user", "content": "..."}],
    ),
]

run_experiment(
    experiment_name="my_experiment",
    cells=cells,
    generations=10,
    ollama_url="http://localhost:9999",
    model="qwen3.6:35b",
)
```

## Running in tmux (survives SSH disconnects)

```bash
# Start
tmux new-session -d -s my-exp "cd ~/MasterThesis-RAG-RecSys/src/project && \
  python -m experiments.chat_prompt_length.run --generations 10 2>&1 | \
  tee experiments/output/chat_run.log"

# Watch live
tmux attach -t my-exp          # Ctrl+B D to detach

# Check progress
wc -l experiments/output/chat_prompt_length/*/generations.jsonl

# Kill when done
tmux kill-session -t my-exp
```

## Output format

Every experiment run produces:

```
output/<experiment_name>/<timestamp>/
├── generations.jsonl   # One JSON record per LLM call
├── summary.json         # Aggregated stats per variant
└── summary.txt          # Human-readable comparison table
```

## Current experiments

### `chat_prompt_length`

Tests 15 prompt variants (3 ad conditions × 5 conciseness levels) to find
which wording produces the most concise-but-informative assistant responses.
Variant 1 in each condition is the current production prompt (control).

```bash
# Quick smoke test (2 scenarios × 1 generation)
python -m experiments.chat_prompt_length.run --quick

# Full run (5 scenarios × 5 variants × 3 conditions × 10 generations = 750 calls)
python -m experiments.chat_prompt_length.run --generations 10
```
