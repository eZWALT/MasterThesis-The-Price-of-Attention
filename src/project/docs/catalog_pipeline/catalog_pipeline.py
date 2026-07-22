import os
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

RES = os.path.join(os.path.dirname(__file__), "resources")

# Same visual language as the main architecture diagram (arch.py), so the two
# figures read as one consistent visual system in the thesis.
graph_attr = {
    "fontsize": "22",
    "bgcolor": "white",
    "dpi": "150",
    "pad": "0.5",
    "nodesep": "0.5",
    "ranksep": "0.8",
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
CARD = {
    "shape": "box",
    "style": "rounded,filled",
    "fillcolor": "#FFFFFF",
    "color": "#B9C2CB",
    "penwidth": "1.0",
}
# title + 1–2 detail lines: enough for thesis clarity without the old wall of text
M = {"width": "2.0", "height": "1.15"}

with Diagram(
    "Offline Catalog Preprocessing Pipeline",
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename=os.path.join(os.path.dirname(__file__), "catalog_pipeline"),
    outformat="png",
):

    with Cluster("Source Dataset", graph_attr=cluster_attr("#E8F0FE", "#A5B8D6")):
        hf = Custom("HuggingFace\nmilistu/AMAZON-Products-2023\n117,243 products",
                     os.path.join(RES, "hf.png"), **M, **IMG, **CARD)

    with Cluster("Catalog Construction", graph_attr=cluster_attr("#F0F4E8", "#B8C8A0")):
        filt = Custom("Filter & Remap\nmeta_* categories",
                       os.path.join(RES, "filter.png"), **M, **IMG, **CARD)
        dedup = Custom("Deduplicate\nby item_id",
                        os.path.join(RES, "dedup.png"), **M, **IMG, **CARD)
        filt >> Edge() >> dedup

    with Cluster("Catalog Serialization", graph_attr=cluster_attr("#FDF6E3", "#D8C48F")):
        merge = Custom("Merge Catalogs\n+ synthetic sources",
                        os.path.join(RES, "merge.png"), **M, **IMG, **CARD)

    with Cluster("Embedding Pipeline", graph_attr=cluster_attr("#E8F5E9", "#8FBF92")):
        embed = Custom("Qwen3 Embedding\n0.6B · 1536-d",
                        os.path.join(RES, "neural.png"), **M, **IMG, **CARD)

    with Cluster("Vector Database", graph_attr=cluster_attr("#F3EEF9", "#B0A4CC")):
        faiss = Custom("FAISS Index\nFlatIP · 459 MB",
                        os.path.join(RES, "meta.png"), **M, **IMG, **CARD)

    hf >> Edge() >> filt
    dedup >> Edge() >> merge
    merge >> Edge() >> embed
    embed >> Edge() >> faiss
