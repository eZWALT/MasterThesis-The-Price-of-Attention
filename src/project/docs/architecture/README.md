# Architecture & Pipeline Diagrams

Two figures, both generated with the [diagrams](https://diagrams.mingrammer.com/) library
(a Graphviz wrapper) and sharing one visual language: rounded colored clusters, white
icon "cards", muted slate-gray arrows, orthogonal routing.

- **`architecture.png`** (from `arch.py`) shows the experiment platform: the two study arms
  (in-person lab, remote crowdsourced), the `192.168.1.0/24` lab subnet as a dashed
  boundary, and the Atlas server's CPU/GPU layout. Reading order is left-to-right along
  the request path: browser → Docker (Streamlit) → GPU model services. Docker sits
  immediately right of the laptop so no HTTP edge has to cross a GPU cluster, and ports
  live in node labels (`:7777`, `:7780`, `:16580`) rather than on the arrows, which keeps
  the two parallel browser edges label-free and unambiguous.
- **`flow_lab.png` / `flow_crowd.png`** (both from `participant_flow.py`) show the screens a
  participant walks through, one figure per study arm. Three phase columns instead of one
  tall strip; the repeated condition block is drawn as a 2×2 cycle so the repeat arrow is a
  short hop rather than a full-height return sweep. Screens that exist in only one arm are
  outlined in that arm's colour (lab blue, crowd pink), matching `architecture.png`.
- **`catalog_pipeline.png`** (from `catalog_pipeline.py`) shows the offline catalog
  preprocessing pipeline: HuggingFace source → filter/remap → dedup → merge → embed →
  FAISS index. Laid out left-to-right (`direction="LR"`) since it's a strictly
  sequential pipeline; each card names its operation plus the resulting artifact
  (file/size) instead of splitting every micro-step into its own node, which keeps a
  6-stage pipeline as one paper-friendly horizontal strip instead of a tall column.

## Regenerating

```bash
pip install diagrams
sudo apt-get install graphviz           # provides the `dot` binary diagrams depends on
sudo apt-get install fonts-urw-base35   # provides Nimbus Sans (see below)
python3 arch.py                 # architecture.png + .pdf
python3 participant_flow.py     # flow_lab.png/.pdf + flow_crowd.png/.pdf
python3 catalog_pipeline.py     # catalog_pipeline.png + .pdf
```

Each script writes a PNG and a PDF. Use the PDF in LaTeX so the figures stay sharp at any
scale; the PNG is for previewing.

## Fonts

All three scripts set `FONT = "Nimbus Sans"` rather than `"Helvetica"`. Graphviz measures
the built-in PostScript families (Helvetica, Courier) from hardcoded metrics but *draws*
whatever pango substitutes, so labels were being laid out to Helvetica widths and rendered
in DejaVu Sans, which made left-justified text spill past its box. Naming an installed
family makes measurement and rendering agree. Two related traps, both worked around in the
scripts and worth knowing before editing them:

- `Edge` and `Node` instances stamp the library's own defaults (`fontname="Sans-Serif"`,
  `fixedsize="true"`, `height="1.9"`) *over* the graph-level `edge_attr`/`node_attr`. Edges
  are therefore built through a local `edge()` helper that re-applies the font, and
  text-only note boxes set `fixedsize="false"` so they size to their label.
- Cards are fixed-size on purpose (uniform boxes), so a label longer than the card width
  will overflow silently rather than growing the box. Check any new label visually.

To match a thesis body font instead, change `FONT`/`FONT_BOLD` to any installed family
(`fc-list : family`); nothing else needs touching.

## Flow figures ↔ code

The flow figures are generated from what `core/experiment/controller.py` actually does:
`_PRE_CONDITION_SCREENS`, the `_CONDITION_SCREENS` block repeated once per entry in
`condition_plan`, then `_POST_CONDITION_SCREENS`. Arm differences are exactly
`STUDY_SKIP_SCREENS` in `core/config.py` (lab skips `prolific_id` + `validation`, crowd
skips `baseline`). The four phase panels are the code's three stages with the post-condition
screens split in two, `Measures` (recall, BFI-10, demographics) and `Close-Out` (validation,
debrief, done), because six screens in one column tower over the other phases. The split is
presentational only; the controller has no such boundary.

Everything that holds for the whole session is in the figure title (EEG/LSL recording for the
lab arm, own-browser for crowd) or in a phase title (`counterbalanced order`), so the only
box that is not a screen is the conditions legend, which sits inside the phase it describes.
The lab `Close-Out` panel carries a card-sized invisible node so its box matches the other
three despite holding one screen fewer.

Figure labels are shortened, so the mapping is:

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

Counts in the detail lines were read off the code, not the docstrings:

| Figure label | Source | Note |
| --- | --- | --- |
| 4 turns, at most 1 ad | `MIN/MAX_TURNS_PER_TRIAL`, `CONDITION_TIMING` | `no_ads` shows none, hence "≤ 1" |
| 22 Likert · 3 sections | `POST_CONDITION_LLM_ITEMS` (15) + `_PERSONALITY_LIKERT` (3) + `_PERSONALITY_OPEN` (2) + `_BEHAVIOUR_ITEMS` (2) | all 7-pt; the open items are rated *and* elaborated |
| 4 steps · 2 Likert + text | `RECALL_ITEMS` (2) + `RECALL_OPEN_ENDED` (1), one step per ad condition | the `render_ads_recall` docstring still claims 7 Likert, which is stale |
| 10 items · 5-pt | `BFI10_ITEMS`, `OCEAN_SCALE_MIN/MAX` | `bfi_version` defaults to `"10"` |
| pick 5 of 10 tasks | `render_validation_questions` | 5 real + 5 distractors |

## Layout

- `resources/` holds the icons used by both diagrams (Firefox, Ollama, neural network, EEG
  headset, LabRecorder, Meta/FAISS, Python, HuggingFace, funnel/filter, merge,
  dedup/stack). Each is pre-processed (cropped/centered/resized onto a square
  transparent canvas) so `imagepos=tc` + `labelloc=b` renders icon-on-top,
  label-below with no overlap, at a consistent visual size across both diagrams.
- `arch.py` / `catalog_pipeline.py`: each is the single source of truth for its
  diagram; edit the style dicts at the top (`graph_attr`, `node_attr`,
  `cluster_attr`, `IMG`/`CARD`/size presets) rather than per-node attributes, to
  keep the look consistent if new nodes are added.
