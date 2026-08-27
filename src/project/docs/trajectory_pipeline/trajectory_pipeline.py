"""Trajectory preprocessing pipeline, diagrams-as-code.

Bronze / Silver / Gold. Silver tables use the table icon; Gold uses the
database cylinder. Rebuild::

    python3 src/project/docs/trajectory_pipeline/make_icons.py
    python3 src/project/docs/trajectory_pipeline/trajectory_pipeline.py
"""

import os
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

RES = os.path.join(os.path.dirname(__file__), "resources")

FONT = "Nimbus Sans"
FONT_BOLD = "Nimbus Sans Bold"

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "dpi": "150",
    "pad": "0.5",
    "nodesep": "0.45",
    "ranksep": "0.9",
    "fontname": FONT,
    "splines": "ortho",
    "labelloc": "t",
}

node_attr = {
    "fontsize": "10",
    "fontname": FONT,
    "labelloc": "b",
}

cluster_base = {
    "fontsize": "12",
    "fontname": FONT_BOLD,
    "style": "rounded",
    "margin": "14",
    "labeljust": "l",
}


def cluster_attr(bg, border):
    return dict(cluster_base, bgcolor=bg, pencolor=border)


def edge(**kw):
    return Edge(fontname=FONT, **kw)


IMG = {"imagescale": "false", "imagepos": "tc"}
CARD = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "#FFFFFF",
    "color": "#B9C2CB",
    "penwidth": "1.0",
}
M = {"width": "2.15", "height": "1.10"}
G = {"width": "2.40", "height": "1.22"}
T = {"width": "2.30", "height": "1.10"}


def icon(label, name, size=None):
    box = size or M
    return Custom(label, os.path.join(RES, name), **box, **IMG, **CARD)


with Diagram(
    "Trajectory Preprocessing Pipeline",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr={
        "fontsize": "10",
        "fontname": FONT,
        "fontcolor": "#444444",
        "color": "#6B7A8A",
        "penwidth": "1.2",
        "arrowsize": "0.8",
    },
    filename=os.path.join(os.path.dirname(__file__), "trajectory_pipeline"),
    outformat=["png", "pdf"],
):

    with Cluster("Bronze", graph_attr=cluster_attr("#F3F1FA", "#8E86BE")):
        jsonl = icon("Tracked JSONL\nN = 54", "recording.png")

    with Cluster("Silver", graph_attr=cluster_attr("#EEF6EE", "#6FA574")):
        roster = icon("Filter\ncrowdfail out", "filter.png")
        parse = icon("Parse\n4 turns", "chat.png")
        infer = icon("Genre inference\n13-class", "neural.png")
        matrices = icon("transition_matrices.csv\n715", "table.png", T)
        inputs = icon("classifier_inputs.csv\n1,080", "table.png", T)
        roster >> edge() >> parse >> edge() >> infer
        infer >> edge(tailport="e", headport="w") >> matrices
        infer >> edge(tailport="e", headport="w") >> inputs

    with Cluster("Gold", graph_attr=cluster_attr("#FDF6E6", "#C4B07A")):
        turns = icon(
            "Turn grain\nutterances.csv   2,160\ntransitions.csv  1,620",
            "database.png",
            G,
        )
        convs = icon(
            "Conversation grain\nconversations.csv   540\nadvertisements.csv  216",
            "database.png",
            G,
        )

    jsonl >> edge() >> roster
    inputs >> edge(style="invis", penwidth="0") >> turns
    matrices >> edge(style="invis", penwidth="0") >> convs
    infer >> edge(tailport="e", headport="w", constraint="false") >> turns
    infer >> edge(tailport="e", headport="w", constraint="false") >> convs
