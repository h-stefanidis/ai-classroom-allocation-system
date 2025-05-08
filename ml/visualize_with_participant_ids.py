import torch
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx
from matplotlib.lines import Line2D

# Load graph
data = torch.load("data/student_graph.pt")

# Load Excel again to get Participant-ID
participants = pd.read_excel("SchoolData/Student Survey - Jan.xlsx", sheet_name="participants")
participants = participants.dropna(subset=["Participant-ID"]).reset_index(drop=True)
participants["Participant-ID"] = participants["Participant-ID"].astype(int)

# Build mapping from node index to Participant-ID
participant_ids = participants["Participant-ID"].tolist()
labels = {i: pid for i, pid in enumerate(participant_ids)}

# Convert to NetworkX
G = to_networkx(data, edge_attrs=["edge_type"], to_undirected=True)

# Assign edge colors
edge_color_map = {
    0: "green", 1: "blue", 2: "orange", 3: "purple", 4: "teal", 5: "red"
}
edge_colors = [
    edge_color_map.get(attr["edge_type"], "gray")
    for _, _, attr in G.edges(data=True)
]

# Draw nodes in neutral color
node_colors = ["skyblue"] * data.num_nodes

# Draw graph with Participant-ID labels
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G, pos,
    node_color=node_colors,
    edge_color=edge_colors,
    labels=labels,
    node_size=600,
    font_size=8
)

# Add edge legend
legend_elements = [
    Line2D([0], [0], color=color, lw=2, label=label)
    for label, color in zip(
        ["Friend", "Influence", "Feedback", "More Time", "Advice", "Disrespect"],
        ["green", "blue", "orange", "purple", "teal", "red"]
    )
]
plt.legend(handles=legend_elements, loc="upper left")
plt.title("Student Social Network Graph")
plt.axis("off")
plt.tight_layout()
plt.show()