import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx

def visualize_subgraph(graph: Data, classroom_name: str, edge_type_labels: dict[int, str] = None):
    """
    Visualizes a PyTorch Geometric Data graph using NetworkX and matplotlib.

    Args:
        graph (Data): The subgraph to visualize.
        classroom_name (str): Title for the plot.
        edge_type_labels (dict): Optional mapping of edge_type values to string labels.
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

    cmap = plt.cm.get_cmap('tab10')  # Up to 10 types
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, edge_cmap=cmap, edge_vmin=0, edge_vmax=9)

    # Node labels (participant_ids)
    pid_labels = {i: pid.item() for i, pid in enumerate(graph.participant_ids)}
    nx.draw_networkx_labels(G, pos, labels=pid_labels, font_size=10)

    # Optional: Legend for edge types
    if edge_type_labels:
        handles = [plt.Line2D([0], [0], color=cmap(i), lw=2, label=label)
                   for i, label in edge_type_labels.items()]
        plt.legend(handles=handles, title="Edge Types", fontsize=9)

    plt.axis('off')
    plt.tight_layout()
    plt.show()



import matplotlib.pyplot as plt
import networkx as nx
from torch_geometric.utils import to_networkx

def visualize_subgraph(graph: Data, classroom_name: str, edge_type_labels: dict[int, str] = None):
    """
    Visualizes a PyTorch Geometric Data graph using NetworkX and matplotlib.

    Args:
        graph (Data): The subgraph to visualize.
        classroom_name (str): Title for the plot.
        edge_type_labels (dict): Optional mapping of edge_type values to string labels.
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

    cmap = plt.cm.get_cmap('tab10')  # Up to 10 types
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, edge_cmap=cmap, edge_vmin=0, edge_vmax=9)

    # Node labels (participant_ids)
    pid_labels = {i: pid.item() for i, pid in enumerate(graph.participant_ids)}
    nx.draw_networkx_labels(G, pos, labels=pid_labels, font_size=10)

    # Optional: Legend for edge types
    if edge_type_labels:
        handles = [plt.Line2D([0], [0], color=cmap(i), lw=2, label=label)
                   for i, label in edge_type_labels.items()]
        plt.legend(handles=handles, title="Edge Types", fontsize=9)

    plt.axis('off')
    plt.tight_layout()
    plt.show()
