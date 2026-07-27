import os
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User

RES = os.path.join(os.path.dirname(__file__), "resources")

# Named so pango resolves the same face graphviz measures with; the built-in
# PostScript names are measured from hardcoded metrics but drawn in whatever
# pango substitutes, which mixes typefaces across the figure.
FONT = "Nimbus Sans"
FONT_BOLD = "Nimbus Sans Bold"


graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "dpi": "150",
    "pad": "0.5",
    "nodesep": "0.7",
    "ranksep": "1.2",
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
    "margin": "14",
    "labeljust": "l",
}

def cluster_attr(bg, border, dashed=False):
    style = "rounded,dashed" if dashed else "rounded"
    return dict(cluster_base, bgcolor=bg, pencolor=border, style=style)

edge_attr = {
    "fontsize": "10",
    "fontname": FONT,
    "fontcolor": "#444444",
    "color": "#6B7A8A",
    "penwidth": "1.2",
    "arrowsize": "0.8",
}

def edge(**kw):
    """Edge instances stamp library defaults over edge_attr, including the
    font, so every edge is built here instead."""
    return Edge(fontname=FONT, **kw)


IMG = {"imagescale": "false", "imagepos": "tc"}
# software components render as white "cards" so edges attach to a visible border
CARD = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "#FFFFFF",
    "color": "#B9C2CB",
    "penwidth": "1.0",
}
# networks use a dashed border so they read as a shared medium, not a host
NET = {
    "shape": "box",
    "style": "rounded,filled,dashed",
    "fillcolor": "#F6F9FD",
    "color": "#8FA8C8",
    "penwidth": "1.1",
}
# at dpi=150 a 90px icon renders ~0.6in tall; heights sized so icon + label
# fill the card snugly, keeping the icon/label group visually centered
S = {"width": "1.5", "height": "0.95"}
M = {"width": "1.9", "height": "0.95"}
L = {"width": "1.9", "height": "1.1"}

with Diagram(
    "Experiment Platform Architecture",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename=os.path.join(os.path.dirname(__file__), "architecture"),
    outformat=["png", "pdf"],
):

    # ── the two study arms, drawn symmetrically ──────────────────────────
    with Cluster("Laboratory Setup (in-person)", graph_attr=cluster_attr("#EAF4FB", "#8FB8D8")):
        lab_participant = User("Lab Participant", width="1.2")
        eeg = Custom("ActiCHamp Plus\n32-channels", os.path.join(RES, "eeg-headset.png"),
                     width="1.6", height="1.3", **IMG, **CARD)

    with Cluster("Crowdsourced Setup (remote)", graph_attr=cluster_attr("#FBEFF4", "#D3A0B8")):
        crowd_participant = User("Crowd Participant\n(Prolific / MTurk)", width="1.2")
        crowd_browser = Custom("Browser\n(own laptop)", os.path.join(RES, "firefox.png"),
                               width="1.6", height="1.1", **IMG, **CARD)

    inet = Custom("Internet\nresearch.ddns.net", os.path.join(RES, "globe.png"),
                  width="1.8", height="1.05", **IMG, **NET)

    # ── everything on the lab subnet, incl. the server itself ────────────
    with Cluster("Lab LAN (192.168.1.0/24)", graph_attr=cluster_attr("#FCFDFF", "#7F9DC0", dashed=True)):

        with Cluster("Lab Laptop", graph_attr=cluster_attr("#FDF6E3", "#D8C48F")):
            labrec = Custom("LabRecorder", os.path.join(RES, "recording.png"),
                            width="1.6", height="1.0", **IMG, **CARD)
            browser = Custom("Browser", os.path.join(RES, "firefox.png"), **S, **IMG, **CARD)

        with Cluster("Atlas Server (2x A100, 192.168.1.17)",
                     graph_attr=cluster_attr("#F2F0FA", "#9C93C8")):
            with Cluster("CPU (Docker)", graph_attr=cluster_attr("#F7F9FA", "#AAAAAA")):
                main = Custom("Main: Streamlit + RAG\n(:7777)", os.path.join(RES, "python.png"), **M, **IMG, **CARD)
                writer = Custom("Writer: Logger + LSL", os.path.join(RES, "python.png"), **M, **IMG, **CARD)
                click = Custom("HTTP: Ad Click (:7780)", os.path.join(RES, "python.png"), **M, **IMG, **CARD)
                faiss = Custom("FAISS Vector DB\n(ANN index)", os.path.join(RES, "meta.png"), **L, **IMG, **CARD)
                # grid layout (faiss/click left column, main/writer right) doubles
                # as the real data flow
                faiss >> edge(style="invis") >> main
                main >> edge(constraint="false") >> faiss
                click >> edge(style="invis") >> writer
                main >> edge(constraint="false") >> writer

            # the wrapper carries no information of its own, but it is what makes
            # dot keep GPU 0 above GPU 1 instead of packing them by size
            with Cluster("GPU Workers", graph_attr=cluster_attr("#F7FBF7", "#B9D4BA", dashed=True)):
                with Cluster("GPU 0 (LLM)", graph_attr=cluster_attr("#E8F5E9", "#8FBF92")):
                    ollama = Custom("Ollama\n(qwen3.6:35b)", os.path.join(RES, "ollama.png"),
                                    **L, **IMG, **CARD)

                with Cluster("GPU 1 (Retrieval)", graph_attr=cluster_attr("#E8F5E9", "#8FBF92")):
                    embed = Custom("Dense Embedding\n(Qwen3 0.6B)", os.path.join(RES, "neural.png"),
                                   **L, **IMG, **CARD)
                    rerank = Custom("Cross-Encoder\n(bge-reranker-v2-m3)", os.path.join(RES, "neural.png"),
                                    **L, **IMG, **CARD)

            # all three model services are called by Main, so the GPUs sit to its
            # right and the three requests leave as one parallel fan
            main >> ollama
            main >> embed
            main >> rerank

    # ── lab arm: EEG stays local to the laptop, app traffic on the LAN ───
    lab_participant >> edge(xlabel="wears") >> eeg
    eeg >> edge(style="dashed", color="#CC3333",
                taillabel="LSL EEG Stream", labelfontsize="10",
                labelfontcolor="#CC3333", labelfontname=FONT,
                labeldistance="3.2", labelangle="25") >> labrec
    lab_participant >> edge() >> browser
    # keep the whole server a rank right of the laptop so the LAN box reads
    # left-to-right instead of stacking the two hosts vertically. Docker is the
    # first thing right of the laptop, so no browser edge crosses a GPU box.
    browser >> edge(style="invis") >> click
    browser >> edge() >> main
    browser >> edge(constraint="false") >> click
    main >> edge(style="dashed", color="#CC3333",
                 taillabel="LSL Markers :16580", labelfontsize="10",
                 labelfontcolor="#CC3333", labelfontname=FONT,
                 labeldistance="5.5", labelangle="18",
                 constraint="false") >> labrec

    # ── crowd arm: never touches the lab laptop; enters via port-forward ─
    # invisible: pins the crowd arm to the same starting rank as the lab arm
    # so the two setups line up symmetrically on the left edge
    crowd_participant >> edge(style="invis") >> eeg
    crowd_participant >> edge() >> crowd_browser
    crowd_browser >> edge() >> inet
    inet >> edge(xlabel="DDNS port-forward") >> main
