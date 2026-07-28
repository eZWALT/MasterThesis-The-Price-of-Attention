# Offline Experiments

A small harness for tuning prompts and model parameters against a live Ollama
endpoint. This is **not** the participant study — it never touches the protocol,
the participant UI, or `logs/`. Use it to decide what the study should ship.

## Layout

```text
experiments/
├── shared/                 reusable pieces — import, don't fork
│   ├── ollama.py             health check + call with metadata
│   ├── stats.py              mean/std/p50/p95 and table formatting
│   └── runner.py             ExperimentCell, run_experiment(), preflight()
├── chat_prompt_length/     response-length study
│   ├── prompts.py            v1: 3 ad conditions × 5 variants
│   ├── prompts_v2.py         v2: baseline / inline / awareness × 5 variants
│   ├── scenarios.py          5 task-catalog user messages
│   └── run.py, run_v2.py     CLI entrypoints
├── compare.py              plot and tabulate several runs side by side
├── plot_dists.py           token distributions for a single run
└── output/                 results (git-ignored)
```

## Running

Start Ollama first — the runner pre-flights the endpoint and exits early if it
is unreachable.

```bash
cd src/project

# smoke test: 2 scenarios × 1 generation
python -m experiments.chat_prompt_length.run_v2 --quick

# full run, labelled so it can be compared later
python -m experiments.chat_prompt_length.run_v2 --generations 10 --label v2_prompts

# compare labelled runs
python -m experiments.compare chat_prompt_length --runs v1_production v2_prompts
```

Common flags: `--generations N`, `--scenarios N`, `--model NAME`,
`--ollama-url URL`, `--label NAME`, `--output-dir PATH`. The model defaults to
`DEFAULT_MODEL` from `core/config.py`.

Long runs survive SSH drops under tmux:

```bash
tmux new-session -d -s prompt-exp \
  'cd ~/MasterThesis-RAG-RecSys/src/project && \
   python -m experiments.chat_prompt_length.run_v2 --generations 10 --label v2_prompts'
tmux attach -t prompt-exp        # Ctrl+B then D to detach
```

## Output

```text
output/<experiment>/<label-or-timestamp>/
├── generations.jsonl    one record per LLM call
├── summary.json         aggregated stats per variant
└── summary.txt          human-readable comparison table
```

Labelling runs is what makes them comparable — without `--label` the folder is a
timestamp and `compare.py` has nothing meaningful to key on.

## Adding an experiment

1. Create `experiments/<name>/` with an `__init__.py`.
2. Describe the grid as a list of `ExperimentCell` objects.
3. Call `run_experiment()` from a `run.py` with an argparse CLI.

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
)
```

## Current experiments

### `chat_prompt_length`

Assistant replies that ramble hurt both the reading time and the ad's
visibility, so this grid searches for the shortest wording that stays helpful.
It crosses three prompt types with five conciseness variants; variant 1 of each
is the current production prompt, acting as control. `run_v2.py` targets the
prompt types actually in use today (base, inline injection, post-injection
awareness) and writes to its own output folder, so v1 results stay intact.
