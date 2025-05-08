import torch
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx
from matplotlib.lines import Line2D
import matplotlib.cm as cm

# Load clustered graph
data = torch.load("data/student_graph_clustered.pt")

# Load participant IDs from Excel (or use saved .participant_ids if present)
participants = pd.read_excel("SchoolData/Student Survey - Jan.xlsx", sheet_name="participants")
participants = participants.dropna(subset=["Participant-ID"]).reset_index(drop=True)
participants["Participant-ID"] = participants["Participant-ID"].astype(int)
participant_ids = participants["Participant-ID"].tolist()
labels = {i: pid for i, pid in enumerate(participant_ids)}

# Convert to NetworkX graph
G = to_networkx(data, edge_attrs=["edge_type"], to_undirected=True)

# Edge color by relationship
edge_color_map = {
    0: "green", 1: "blue", 2: "orange", 3: "purple", 4: "teal", 5: "red"
}
edge_colors = [edge_color_map.get(attr["edge_type"], "gray") for _, _, attr in G.edges(data=True)]

# Node color by cluster label (data.y)
num_clusters = len(set(data.y.tolist()))
cluster_colors = cm.get_cmap("Set3", num_clusters)
node_color_map = [cluster_colors(int(c)) for c in data.y]

# Plot
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G, pos,
    node_color=node_color_map,
    edge_color=edge_colors,
    labels=labels,
    node_size=600,
    font_size=8
)

# Legends
edge_legend = [
    Line2D([0], [0], color=color, lw=2, label=label)
    for label, color in zip(
        ["Friend", "Influence", "Feedback", "More Time", "Advice", "Disrespect"],
        ["green", "blue", "orange", "purple", "teal", "red"]
    )
]

cluster_legend = [
    Line2D([0], [0], marker='o', color='w', label=f"Classroom {i}",
           markerfacecolor=cluster_colors(i), markersize=12)
    for i in range(num_clusters)
]

plt.legend(handles=cluster_legend + edge_legend, loc="upper left")
plt.title("ClassForge Clustered Classroom Graph")
plt.axis("off")
plt.tight_layout()
plt.show()
