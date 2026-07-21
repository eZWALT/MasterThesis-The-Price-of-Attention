import os
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.onprem.client import User

RES = os.path.join(os.path.dirname(__file__), "resources")

graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "dpi": "150",
    "pad": "0.5",
    "nodesep": "0.6",
    "ranksep": "1.2",
    "fontname": "Helvetica",
    "splines": "ortho",
    "labelloc": "t",
}

node_attr = {
    "fontsize": "10",
    "fontname": "Helvetica",
    "labelloc": "b",
}

cluster_base = {
    "fontsize": "12",
    "fontname": "Helvetica-Bold",
    "style": "rounded",
    "margin": "14",
    "labeljust": "l",
}

def cluster_attr(bg, border):
    return dict(cluster_base, bgcolor=bg, pencolor=border)

edge_attr = {
    "fontsize": "10",
    "fontname": "Helvetica",
    "fontcolor": "#444444",
    "color": "#6B7A8A",
    "penwidth": "1.2",
    "arrowsize": "0.8",
}

IMG = {"imagescale": "false", "imagepos": "tc"}
# software components render as white "cards" so edges attach to a visible border
CARD = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "#FFFFFF",
    "color": "#B9C2CB",
    "penwidth": "1.0",
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
    outformat="png",
):

    with Cluster("Participant Setup", graph_attr=cluster_attr("#EAF4FB", "#8FB8D8")):
        participant = User("Participant", width="1.2")
        eeg = Custom("ActiCHamp Plus\n32-channels", os.path.join(RES, "eeg-headset.png"),
                     width="1.6", height="1.3", **IMG, **CARD)

    with Cluster("Lab Laptop", graph_attr=cluster_attr("#FDF6E3", "#D8C48F")):
        labrec = Custom("LabRecorder", os.path.join(RES, "recording.png"),
                        width="1.6", height="1.0", **IMG, **CARD)
        browser = Custom("Browser", os.path.join(RES, "firefox.png"), **S, **IMG, **CARD)

    with Cluster("Atlas Server (2x A100)", graph_attr=cluster_attr("#F2F0FA", "#9C93C8")):
        with Cluster("GPU 0 — LLM", graph_attr=cluster_attr("#E8F5E9", "#8FBF92")):
            ollama = Custom("Ollama\n(qwen3.6:35b)", os.path.join(RES, "ollama.png"), **L, **IMG, **CARD)

        with Cluster("CPU — Docker", graph_attr=cluster_attr("#F7F9FA", "#AAAAAA")):
            main = Custom("Main: Streamlit + RAG", os.path.join(RES, "python.png"), **M, **IMG, **CARD)
            writer = Custom("Writer: Logger + LSL", os.path.join(RES, "python.png"), **M, **IMG, **CARD)
            click = Custom("HTTP: Ad Click (:7780)", os.path.join(RES, "python.png"), **M, **IMG, **CARD)
            faiss = Custom("FAISS Vector DB\n(ANN index)", os.path.join(RES, "meta.png"), **L, **IMG, **CARD)
            # grid layout (faiss/click left column, main/writer right) doubles
            # as the real data flow: dir="back" renders the arrow as main->faiss
            faiss >> Edge(style="invis") >> main
            main >> Edge(constraint="false") >> faiss
            click >> Edge(style="invis") >> writer
            main >> Edge(constraint="false") >> writer

        with Cluster("GPU 1 — Retrieval", graph_attr=cluster_attr("#E8F5E9", "#8FBF92")):
            rerank = Custom("Cross-Encoder\n(bge-reranker-v2-m3)", os.path.join(RES, "neural.png"), **L, **IMG, **CARD)
            embed = Custom("Dense Embedding\n(Qwen3 0.6B)", os.path.join(RES, "neural.png"), **L, **IMG, **CARD)

        # keep GPU 0 fully left of the Docker cluster, vertically centered
        ollama >> Edge(style="invis") >> faiss
        ollama >> Edge(style="invis") >> click
        ollama >> Edge(style="invis") >> writer
        ollama >> Edge() >> main
        main >> embed
        main >> rerank

    participant >> Edge(xlabel="wears") >> eeg
    eeg >> Edge(style="dashed", color="#CC3333",
                taillabel="LSL EEG Stream", labelfontsize="10",
                labelfontcolor="#CC3333", labelfontname="Helvetica",
                labeldistance="3.2", labelangle="25") >> labrec
    participant >> Edge() >> browser
    browser >> Edge() >> main
    main >> Edge(style="dashed", color="#CC3333", fontcolor="#CC3333",
                 xlabel="LSL Marker Stream", constraint="false") >> labrec
