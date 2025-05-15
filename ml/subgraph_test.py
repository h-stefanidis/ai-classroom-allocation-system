import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx
from torch_geometric.data import Data

from db.db_manager import get_db  # Assumes your db manager has get_db context
from build_graph import build_graph_from_db  # Adjust this if in same file or module
from classroom_split import split_graph_by_classroom  # The subgraph-splitting function

# Define edge type labels for visualization
EDGE_TYPE_LABELS = {
    0: "friend",
    1: "influence",
    2: "feedback",
    3: "more_time",
    4: "advice",
    5: "disrespect"
}

def visualize_subgraph(graph: Data, classroom_name: str, edge_type_labels: dict[int, str] = None):
    """
    Visualizes a PyTorch Geometric Data graph using NetworkX and matplotlib.
    """
    G = to_networkx(graph, edge_attrs=["edge_type"])
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(8, 6))
    plt.title(f"Classroom: {classroom_name}", fontsize=14)

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500)

    # Draw edges with edge type colors
    edge_colors = []
    for _, _, d in G.edges(data=True):
        etype = d.get("edge_type", -1)
        edge_colors.append(etype)

    cmap = plt.cm.get_cmap('tab10')  # Up to 10 edge types
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, edge_cmap=cmap, edge_vmin=0, edge_vmax=9)

    # Node labels (participant_ids)
    pid_labels = {i: pid.item() for i, pid in enumerate(graph.participant_ids)}
    nx.draw_networkx_labels(G, pos, labels=pid_labels, font_size=10)

    # Optional legend for edge types
    if edge_type_labels:
        handles = [plt.Line2D([0], [0], color=cmap(i), lw=2, label=label)
                   for i, label in edge_type_labels.items()]
        plt.legend(handles=handles, title="Edge Types", fontsize=9)

    plt.axis('off')
    plt.tight_layout()
    plt.show()


def main():
    with get_db() as db:
        print("Loading full graph from database...")
        full_graph = build_graph_from_db(db)
        print("Splitting graph by classroom...")
        subgraphs = split_graph_by_classroom(full_graph, db)

        print(f"Visualizing {len(subgraphs)} classroom subgraphs...")
        for classroom, subgraph in subgraphs.items():
            visualize_subgraph(subgraph, classroom, EDGE_TYPE_LABELS)


if __name__ == "__main__":
    main()
