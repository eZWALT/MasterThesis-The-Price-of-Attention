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
OUT = os.path.dirname(__file__)

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "dpi": "150",
    "pad": "0.5",
    "nodesep": "0.5",
    "ranksep": "0.55",
    "fontname": "Helvetica",
    "splines": "ortho",
    "labelloc": "t",
}

node_attr = {"fontsize": "10", "fontname": "Helvetica", "labelloc": "b"}

cluster_base = {
    "fontsize": "12",
    "fontname": "Helvetica-Bold",
    "margin": "14",
    "labeljust": "l",
}

def cluster_attr(bg, border, dashed=False):
    style = "rounded,dashed" if dashed else "rounded"
    return dict(cluster_base, bgcolor=bg, pencolor=border, style=style)

edge_attr = {
    "fontsize": "10",
    "fontname": "Helvetica",
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
    "margin": "0.10,0.06",
    # the library defaults every node to 1.9in tall to fit an icon; text-only
    # notes must shrink back to their label
    "height": "0.1",
}


def screen(title, detail, icon, card=CARD):
    return Custom(f"{title}\n{detail}", os.path.join(RES, f"{icon}.png"),
                  **BOX, **IMG, **card)


def note(lines, mono=False):
    label = "".join(f"{l}\\l" for l in lines)
    attrs = dict(NOTE, width="2.3")
    if mono:
        attrs["fontname"] = "DejaVu Sans Mono"
    return Node(label, **attrs)


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
        outformat="png",
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
            survey = screen("Questionnaire", "20 items · 7-pt Likert", "survey")
            brief = screen("Task Briefing", "task prompt + warning", "brief")
            findings = screen("Findings", "free text ≤ 256 chars", "findings")
            chat = screen("Conversation", "4 turns · 1 ad at turn 2 or 4", "chat")

        with Cluster("Conditions (shuffled per participant)",
                     graph_attr=cluster_attr("#FBFAFE", "#9C93C8", dashed=True)):
            legend = note([
                "NO             no ads",
                "IN-EA / IN-LA  inline ad  · turn 2 / 4",
                "BL-EA / BL-LA  ad block   · turn 2 / 4",
            ], mono=True)

        with Cluster("Recording", graph_attr=cluster_attr(
                "#FAFCFE" if lab else "#FEFAFC",
                "#8FB8D8" if lab else "#D3A0B8", dashed=True)):
            rec = note(
                ["EEG 32 ch + event markers stream",
                 "over LSL to LabRecorder for the",
                 "whole session"] if lab else
                ["No physiological recording —",
                 "browser-only session on the",
                 "participant's own laptop"])

        with Cluster("3 · Wrap-Up", graph_attr=cluster_attr("#EEF6EE", "#8FBF92")):
            recall = screen("Ad Recall", "4 steps · 7 Likert + text", "recall")
            bfi = screen("BFI-10", "10 items · 5-pt", "bfi")
            demog = screen("Demographics", "all fields optional", "demog")
            validate = (screen("Validation", "pick 5 of 10 tasks", "validate", CROWD_CARD)
                        if not lab else None)
            debrief = screen("Debrief", "deception disclosure", "debrief")
            done = screen("Done",
                          "notify researcher" if lab else "Run ID → Prolific",
                          "done")

        for h in (consent, brief, recall):
            anchor >> Edge(style="invis") >> h

        consent >> gate >> warmup
        # phase transitions start a new column, so they must not add a rank
        warmup >> Edge(constraint="false") >> brief
        brief >> chat                                    # left column, downward
        survey >> Edge(style="invis") >> findings         # right column
        chat >> Edge(constraint="false") >> findings      # bottom row, rightward
        findings >> Edge(constraint="false") >> survey    # right column, upward
        survey >> Edge(xlabel="× 5", constraint="false") >> brief
        survey >> Edge(constraint="false") >> recall
        recall >> bfi >> demog
        tail = demog
        if validate is not None:
            tail >> validate
            tail = validate
        tail >> debrief >> done

        # park the two side notes in the space each phase leaves free
        chat >> Edge(style="invis") >> legend
        warmup >> Edge(style="invis") >> rec


build("lab", "flow_lab")
build("crowd", "flow_crowd")
