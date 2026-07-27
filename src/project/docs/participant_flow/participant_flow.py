"""Participant-facing screen flow, one figure per study arm.

Mirrors core/experiment/controller.py: the pre-condition screens, the
4-screen condition block repeated once per condition, and the post-condition
screens. Arm differences come from STUDY_SKIP_SCREENS in core/config.py:
lab skips prolific_id + validation, crowd skips baseline.

The post-condition screens are drawn as two phases rather than one so that no
column towers over the rest; the split is presentational, not a boundary in the
controller. Session-wide facts live in the titles, which leaves the conditions
legend as the only box that is not a screen.
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
    "ranksep": "0.45",
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

BOX = {"width": "2.0", "height": "1.05"}

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
    label = f"{title}\n{detail}" if detail else title
    return Custom(label, os.path.join(RES, f"{icon}.png"), **BOX, **IMG, **card)


def edge(**kw):
    # Edge instances stamp the library's own defaults over the graph-level
    # edge_attr, so the font has to be repeated here or labels fall back
    return Edge(fontname=FONT, **kw)


def note(lines, width="2.3", **kw):
    # \l left-justifies each line so the list starts under the cluster title
    # rather than drifting away from it
    return Node("".join(f"{l}\\l" for l in lines), **{**NOTE, **kw}, width=width)


def note_attr():
    # annotation, so: dashed, tight to its text, and a title one step below the
    # phase titles in the hierarchy
    return cluster_attr("#FBFAFE", "#9C93C8", dashed=True, margin="9", fontsize="10.5")


def build(study, filename):
    lab = study == "lab"
    # session-wide facts belong to the whole figure, so they sit in the title
    # rather than in a box that has to float somewhere
    title = ("Lab Participant Flow (in-person, 32-ch EEG + LSL markers)" if lab
             else "Crowd Participant Flow (remote, own browser)")

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
            consent = screen("Consent", "", "consent")
            if lab:
                gate = screen("Baseline", "30 s rest & EEG calibration", "eye", LAB_CARD)
            else:
                gate = screen("Prolific ID", "worker ID entry", "id", CROWD_CARD)
            warmup = screen("Warm-Up Chat", "2 turns · no ads", "warmup")

        with Cluster("2 · Condition Block (× 5 conditions · counterbalanced order)",
                     graph_attr=cluster_attr("#F2F0FA", "#9C93C8")):
            # Laid out as a 2x2 cycle: briefing and questionnaire share the top
            # row, so the repeat arrow closes the loop instead of running the
            # full height of the phase. Declared right-to-left because dot
            # orders same-rank siblings in reverse declaration order here.
            survey = screen("Questionnaire", "22 Likert · 3 sections", "survey")
            brief = screen("Task Briefing", "task prompt + warning", "brief")
            findings = screen("Findings", "free text ≤ 256 chars", "findings")
            chat = screen("Conversation", "4 turns · ≤ 1 ad (turn 2/4)", "chat")

            # the one annotation left, and it describes this phase, so it lives
            # inside it spanning both columns instead of floating beside them
            # the five names are compositional, so the box decodes the parts in
            # two columns rather than listing five near-identical strings
            with Cluster("Conditions", graph_attr=note_attr()):
                col = dict(width="1.8", labelloc="t", height="0.42")
                fmt = note(["NO: no ads (control)",
                            "IN: inline ad inside the reply",
                            "BL: ad block above the reply"], **col)
                when = note(["EA: ad early, at turn 2",
                             "LA: ad late, at turn 4"], **col)

        # split in two so no phase towers over the others: the post-condition
        # screens are measures first, then the close-out sequence
        with Cluster("3 · Measures", graph_attr=cluster_attr("#EEF6EE", "#8FBF92")):
            recall = screen("Ad Recall", "4 steps · 2 Likert + text", "recall")
            bfi = screen("BFI-10", "10 items · 5-pt", "bfi")
            demog = screen("Demographics", "", "demog")

        with Cluster("4 · Close-Out", graph_attr=cluster_attr("#EEF6EE", "#8FBF92")):
            validate = (screen("Validation", "pick 5 of 10 tasks", "validate", CROWD_CARD)
                        if not lab else None)
            debrief = screen("Debrief", "disclosure + opt-out", "debrief")
            done = screen("Done", "" if lab else "completion code for Prolific", "done")
            filler = (Node("", shape="box", style="invis", **BOX) if lab else None)

        head = validate if validate is not None else debrief
        for h in (consent, brief, recall, head):
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
        # same shape as every other phase transition: leave the bottom of one
        # column, enter the top of the next, without adding a rank
        demog >> edge(constraint="false") >> head
        if validate is not None:
            validate >> debrief
        debrief >> done
        if filler is not None:
            # lab has one screen fewer here; a card-sized invisible node keeps
            # this phase box the same height as the other three
            done >> edge(style="invis") >> filler

        # one legend column under each column of the cycle
        chat >> edge(style="invis") >> fmt
        findings >> edge(style="invis") >> when


build("lab", "flow_lab")
build("crowd", "flow_crowd")
