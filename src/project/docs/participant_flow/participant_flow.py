"""Participant-facing screen flow, one figure per study arm.

Mirrors core/experiment/controller.py: the pre-condition screens, the
4-screen condition block repeated once per condition, and the post-condition
screens. Arm differences come from STUDY_SKIP_SCREENS in core/config.py:
lab skips prolific_id + validation, crowd skips baseline.
"""

import os
from diagrams import Diagram, Cluster, Edge, Node
from diagrams.custom import Custom

RES = os.path.join(os.path.dirname(__file__), "resources")

# Named so pango resolves the same face graphviz measures with: the built-in
# PostScript names (Helvetica, Courier) are measured from hardcoded metrics but
# drawn in whatever pango substitutes, which shifts every label slightly.
FONT = "Nimbus Sans"
FONT_BOLD = "Nimbus Sans Bold"
OUT = os.path.dirname(__file__)

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "dpi": "150",
    "pad": "0.5",
    "nodesep": "0.5",
    "ranksep": "0.55",
    "fontname": FONT,
    "splines": "ortho",
    "labelloc": "t",
}

node_attr = {"fontsize": "10", "fontname": FONT, "labelloc": "b"}

cluster_base = {
    "fontsize": "12",
    "fontname": FONT_BOLD,
    "margin": "14",
    "labeljust": "l",
}

def cluster_attr(bg, border, dashed=False, margin="14", fontsize="12"):
    style = "rounded,dashed" if dashed else "rounded"
    return dict(cluster_base, bgcolor=bg, pencolor=border, style=style,
                margin=margin, fontsize=fontsize)

edge_attr = {
    "fontsize": "10",
    "fontname": FONT,
    "fontcolor": "#444444",
    "color": "#6B7A8A",
    "penwidth": "1.2",
    "arrowsize": "0.8",
}

IMG = {"imagescale": "false", "imagepos": "tc"}
CARD = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "#FFFFFF",
    "color": "#B9C2CB",
    "penwidth": "1.0",
}
# arm-specific screens keep the colour their setup has in architecture.png
LAB_CARD = dict(CARD, color="#8FB8D8", penwidth="1.6")
CROWD_CARD = dict(CARD, color="#D3A0B8", penwidth="1.6")

BOX = {"width": "2.3", "height": "1.05"}

# text-only note: no icon, so the label is centred rather than bottom-aligned.
# Borderless, since the dashed cluster around it already frames the text.
NOTE = {
    "shape": "box",
    "style": "filled",
    "fillcolor": "#FFFFFF00",
    "penwidth": "0",
    "labelloc": "c",
    "fontsize": "9",
    "margin": "0.12,0.09",
    # the library fixes every node at 1.9in square to hold an icon; text-only
    # notes must instead be sized by their own label, or the text overflows
    # both the node and the cluster drawn around it
    "fixedsize": "false",
    "height": "0.1",
}


def screen(title, detail, icon, card=CARD):
    return Custom(f"{title}\n{detail}", os.path.join(RES, f"{icon}.png"),
                  **BOX, **IMG, **card)


def edge(**kw):
    # Edge instances stamp the library's own defaults over the graph-level
    # edge_attr, so the font has to be repeated here or labels fall back
    return Edge(fontname=FONT, **kw)


def note(lines):
    # Helvetica only: graphviz sizes labels from built-in Helvetica metrics, so
    # any other family (Courier, DejaVu Sans Mono) lays out at the wrong width
    # and left-justified text spills over the cluster border.
    return Node("".join(f"{l}\\l" for l in lines), **NOTE, width="2.3")


def build(study, filename):
    lab = study == "lab"
    title = ("Lab Participant Flow (in-person, EEG)" if lab
             else "Crowd Participant Flow (remote, Prolific)")

    with Diagram(
        title,
        show=False,
        direction="TB",
        graph_attr=graph_attr,
        node_attr=node_attr,
        edge_attr=edge_attr,
        filename=os.path.join(OUT, filename),
        outformat=["png", "pdf"],
    ):
        # ranks the first screen of each phase together, so each phase becomes a
        # column instead of one 12-screen vertical strip
        anchor = Node("", shape="point", style="invis", width="0.01", height="0.01")

        with Cluster("1 · Onboarding", graph_attr=cluster_attr("#EAF4FB", "#8FB8D8")):
            consent = screen("Consent", "ethics + data notice", "consent")
            if lab:
                gate = screen("Baseline", "30 s rest · webcam + EEG", "eye", LAB_CARD)
            else:
                gate = screen("Prolific ID", "worker ID entry", "id", CROWD_CARD)
            warmup = screen("Warm-Up Chat", "2 turns · no ads", "warmup")

        with Cluster("2 · Condition Block (× 5 conditions)",
                     graph_attr=cluster_attr("#F2F0FA", "#9C93C8")):
            # Laid out as a 2x2 cycle: briefing and questionnaire share the top
            # row, so the repeat arrow closes the loop instead of running the
            # full height of the phase. Declared right-to-left because dot
            # orders same-rank siblings in reverse declaration order here.
            survey = screen("Questionnaire", "22 Likert items · 3 sections", "survey")
            brief = screen("Task Briefing", "task prompt + warning", "brief")
            findings = screen("Findings", "free text ≤ 256 chars", "findings")
            chat = screen("Conversation", "4 turns · ≤ 1 ad (turn 2 or 4)", "chat")

        # the three phase columns have very different heights; these notes carry
        # the design facts a methods reader needs and fill the space that leaves
        with Cluster("Conditions",
                     graph_attr=cluster_attr("#FBFAFE", "#9C93C8", dashed=True, margin="9", fontsize="10.5")):
            legend = note([
                "NO — no ads",
                "IN-EA — inline ad · turn 2",
                "IN-LA — inline ad · turn 4",
                "BL-EA — ad block · turn 2",
                "BL-LA — ad block · turn 4",
            ])

        with Cluster("Counterbalancing",
                     graph_attr=cluster_attr("#FBFAFE", "#9C93C8", dashed=True, margin="9", fontsize="10.5")):
            counter = note([
                "Tasks: Latin-square rotation by",
                "cb_group (or participant-id hash)",
                "Conditions: shuffled independently,",
                "then zipped with the task order",
            ])

        # neutral, unlike the two purple notes: logging is session-wide, not
        # a property of the condition block
        with Cluster("Logging",
                     graph_attr=cluster_attr("#FAFBFC", "#A9B4BF", dashed=True, margin="9", fontsize="10.5")):
            logging_note = note([
                "One JSON line per event, append-",
                "only and crash-safe, written to",
                "logs/<run>/<run>_events.jsonl",
            ])

        with Cluster("Recording", graph_attr=cluster_attr(
                "#FAFCFE" if lab else "#FEFAFC",
                "#8FB8D8" if lab else "#D3A0B8", dashed=True, margin="9", fontsize="10.5")):
            rec = note(
                ["32-ch EEG and event markers",
                 "stream over LSL to LabRecorder",
                 "for the whole session"] if lab else
                ["No physiological recording —",
                 "browser-only session on the",
                 "participant's own laptop"])

        with Cluster("3 · Wrap-Up", graph_attr=cluster_attr("#EEF6EE", "#8FBF92")):
            recall = screen("Ad Recall", "4 steps · 2 Likert + open text", "recall")
            bfi = screen("BFI-10", "10 items · 5-pt", "bfi")
            demog = screen("Demographics", "all fields optional", "demog")
            validate = (screen("Validation", "pick 5 of 10 tasks", "validate", CROWD_CARD)
                        if not lab else None)
            debrief = screen("Debrief", "disclosure + withdraw option", "debrief")
            done = screen("Done",
                          "notify researcher" if lab else "Run ID → Prolific",
                          "done")

        for h in (consent, brief, recall):
            anchor >> edge(style="invis") >> h

        consent >> gate >> warmup
        # phase transitions start a new column, so they must not add a rank
        warmup >> edge(constraint="false") >> brief
        brief >> chat                                    # left column, downward
        survey >> edge(style="invis") >> findings         # right column
        chat >> edge(constraint="false") >> findings      # bottom row, rightward
        findings >> edge(constraint="false") >> survey    # right column, upward
        survey >> edge(xlabel="× 5", constraint="false") >> brief
        survey >> edge(constraint="false") >> recall
        recall >> bfi >> demog
        tail = demog
        if validate is not None:
            tail >> validate
            tail = validate
        tail >> debrief >> done

        # park the side notes in the space the two shorter phases leave free,
        # filling down to the depth of the wrap-up column
        chat >> edge(style="invis") >> legend
        legend >> edge(style="invis") >> counter
        warmup >> edge(style="invis") >> rec
        rec >> edge(style="invis") >> logging_note


build("lab", "flow_lab")
build("crowd", "flow_crowd")
