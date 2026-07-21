# System Architecture Diagram

`architecture.png` is generated from `arch.py` using the [diagrams](https://diagrams.mingrammer.com/)
library (a Graphviz wrapper). It documents the experiment platform: participant/EEG setup,
lab laptop (Browser + LabRecorder), and the Atlas server's GPU/CPU layout.

## Regenerating

```bash
pip install diagrams
sudo apt-get install graphviz   # provides the `dot` binary diagrams depends on
python3 arch.py                 # writes architecture.png in this folder
```

## Layout

- `resources/` — icons used by the diagram (Firefox, Ollama, neural network, EEG headset,
  LabRecorder, Meta/FAISS, Python). Each is pre-processed (cropped/centered/resized) so
  `imagepos=tc` + `labelloc=b` renders icon-on-top, label-below with no overlap.
- `arch.py` — single source of truth for the diagram; edit style dicts at the top
  (`graph_attr`, `node_attr`, `cluster_attr`, `IMG`/`CARD`/`S`/`M`/`L`) rather than
  per-node attributes, to keep the look consistent if new nodes are added.
