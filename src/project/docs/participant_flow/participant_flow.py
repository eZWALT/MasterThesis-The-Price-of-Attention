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
    title = ("Laboratory participant flow  ·  in-person, 32-ch EEG, LSL markers" if lab
             else "Crowd participant flow  ·  remote, own browser")

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
                gate = screen("Baseline", "30 s rest  ·  EEG calibration", "eye", LAB_CARD)
            else:
                gate = screen("Prolific ID", "worker ID entry", "id", CROWD_CARD)
            warmup = screen("Warm-Up Chat", "2 turns · no ads", "warmup")

        with Cluster("2 · Condition loop  (× 5 · randomised order)",
                     graph_attr=cluster_attr("#F2F0FA", "#9C93C8")):
            # 2×2 cycle. First-declared sibling sits on the left:
            #   1 briefing TL → 2 conversation BL → 3 findings BR → 4 survey TR
            # Entry hits briefing from the left; exit leaves the questionnaire
            # to the right. Compass ports keep every arrow on the perimeter.
            brief = screen("1  Task Briefing", "task prompt  ·  chats are independent", "brief")
            survey = screen("4  Questionnaire", "22 Likert  ·  3 sections", "survey")
            chat = screen("2  Conversation", "4 turns  ·  ≤1 ad (turn 2 or 4)", "chat")
            findings = screen("3  Findings", "free text  ·  ≤ 256 chars", "findings")

            # Two columns under the 2×2 cycle. Paper names; no IN/BL/EA/LA.
            with Cluster("Five conditions", graph_attr=note_attr()):
                col = dict(width="1.95", labelloc="t", height="0.42")
                fmt = note(["imp₂   implicit early",
                            "imp₄   implicit late",
                            "∅      no advertisement"], **col)
                when = note(["exp₂   explicit early",
                             "exp₄   explicit late"], **col)

        # split in two so no phase towers over the others: the post-condition
        # screens are measures first, then the close-out sequence
        with Cluster("3 · Measures", graph_attr=cluster_attr("#EEF6EE", "#6A9A6E")):
            recall = screen("Cued Recall", "4 ads only  ·  2 Likert + text", "recall")
            bfi = screen("BFI-10", "10 items  ·  5-pt", "bfi")
            demog = screen("Demographics", "", "demog")

        with Cluster("4 · Close-out", graph_attr=cluster_attr("#F7F1E8", "#C4A574")):
            validate = (screen("Validation", "pick 5 of 10 tasks", "validate", CROWD_CARD)
                        if not lab else None)
            debrief = screen("Debrief", "disclosure + opt-out", "debrief")
            done = screen("Done", "", "done")
            filler = (Node("", shape="box", style="invis", **BOX) if lab else None)

        head = validate if validate is not None else debrief
        for h in (consent, brief, recall, head):
            anchor >> edge(style="invis") >> h

        consent >> gate >> warmup
        # phase transitions start a new column, so they must not add a rank
        warmup >> edge(constraint="false", tailport="e", headport="w") >> brief
        brief >> edge(tailport="s", headport="n") >> chat
        survey >> edge(style="invis") >> findings
        chat >> edge(constraint="false", tailport="e", headport="w") >> findings
        findings >> edge(constraint="false", tailport="n", headport="s") >> survey
        survey >> edge(xlabel="× 5", constraint="false", tailport="w", headport="e") >> brief
        survey >> edge(constraint="false", tailport="e", headport="w") >> recall
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
