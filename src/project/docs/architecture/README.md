# Architecture & Pipeline Diagrams

Two figures, both generated with the [diagrams](https://diagrams.mingrammer.com/) library
(a Graphviz wrapper) and sharing one visual language: rounded colored clusters, white
icon "cards", muted slate-gray arrows, orthogonal routing.

- **`architecture.png`** (from `arch.py`) — the experiment platform: participant/EEG
  setup, lab laptop (Browser + LabRecorder), and the Atlas server's GPU/CPU layout.
- **`catalog_pipeline.png`** (from `catalog_pipeline.py`) — the offline catalog
  preprocessing pipeline: HuggingFace source → filter/remap → dedup → merge → embed →
  FAISS index. Laid out left-to-right (`direction="LR"`) since it's a strictly
  sequential pipeline; each card names its operation plus the resulting artifact
  (file/size) instead of splitting every micro-step into its own node, which keeps a
  6-stage pipeline as one paper-friendly horizontal strip instead of a tall column.

## Regenerating

```bash
pip install diagrams
sudo apt-get install graphviz   # provides the `dot` binary diagrams depends on
python3 arch.py                 # writes architecture.png in this folder
python3 catalog_pipeline.py     # writes catalog_pipeline.png in this folder
```

## Layout

- `resources/` — icons used by both diagrams (Firefox, Ollama, neural network, EEG
  headset, LabRecorder, Meta/FAISS, Python, HuggingFace, funnel/filter, merge,
  dedup/stack). Each is pre-processed (cropped/centered/resized onto a square
  transparent canvas) so `imagepos=tc` + `labelloc=b` renders icon-on-top,
  label-below with no overlap, at a consistent visual size across both diagrams.
- `arch.py` / `catalog_pipeline.py` — each is the single source of truth for its
  diagram; edit the style dicts at the top (`graph_attr`, `node_attr`,
  `cluster_attr`, `IMG`/`CARD`/size presets) rather than per-node attributes, to
  keep the look consistent if new nodes are added.
