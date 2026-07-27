# Architecture & Pipeline Diagrams

Two figures, both generated with the [diagrams](https://diagrams.mingrammer.com/) library
(a Graphviz wrapper) and sharing one visual language: rounded colored clusters, white
icon "cards", muted slate-gray arrows, orthogonal routing.

- **`architecture.png`** (from `arch.py`) — the experiment platform: the two study arms
  (in-person lab, remote crowdsourced), the `192.168.1.0/24` lab subnet as a dashed
  boundary, and the Atlas server's CPU/GPU layout. Reading order is left-to-right along
  the request path: browser → Docker (Streamlit) → GPU model services. Docker sits
  immediately right of the laptop so no HTTP edge has to cross a GPU cluster, and ports
  live in node labels (`:7777`, `:7780`, `:16580`) rather than on the arrows, which keeps
  the two parallel browser edges label-free and unambiguous.
- **`flow_lab.png` / `flow_crowd.png`** (both from `participant_flow.py`) — the screens a
  participant walks through, one figure per study arm. Three phase columns instead of one
  tall strip; the repeated condition block is drawn as a 2×2 cycle so the repeat arrow is a
  short hop rather than a full-height return sweep. Screens that exist in only one arm are
  outlined in that arm's colour (lab blue, crowd pink), matching `architecture.png`.
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
python3 participant_flow.py     # writes flow_lab.png + flow_crowd.png
python3 catalog_pipeline.py     # writes catalog_pipeline.png in this folder
```

## Flow figures ↔ code

The flow figures are generated from what `core/experiment/controller.py` actually does:
`_PRE_CONDITION_SCREENS`, the `_CONDITION_SCREENS` block repeated once per entry in
`condition_plan`, then `_POST_CONDITION_SCREENS`. Arm differences are exactly
`STUDY_SKIP_SCREENS` in `core/config.py` (lab skips `prolific_id` + `validation`, crowd
skips `baseline`). Figure labels are shortened, so the mapping is:

| Figure label | `SCREEN_*` id | Arm |
| --- | --- | --- |
| Consent | `consent` | both |
| Baseline | `baseline` | lab only |
| Prolific ID | `prolific_id` | crowd only |
| Warm-Up Chat | `warmup_chat` | both |
| Task Briefing | `condition_intro` | both |
| Conversation | `condition_chat` | both |
| Findings | `condition_conclusion` | both |
| Questionnaire | `post_condition_survey` | both |
| Ad Recall | `ads_recall_interpretation` | both |
| BFI-10 | `ocean` | both |
| Demographics | `demographics` | both |
| Validation | `validation` | crowd only |
| Debrief | `deception_disclosure` | both |
| Done | `done` | both |

Counts in the detail lines come from the same sources: 4 turns per conversation
(`MIN/MAX_TURNS_PER_TRIAL`), one ad at turn 2 or 4 (`CONDITION_TIMING`), 20 post-condition
items (`POST_CONDITION_*` lists), 4 recall steps (one per ad condition), BFI-10
(`OCEAN_ITEMS`), and 5-of-10 task recognition (`render_validation_questions`).

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
