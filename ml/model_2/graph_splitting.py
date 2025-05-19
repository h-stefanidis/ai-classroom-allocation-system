import json
from collections import defaultdict
import networkx as nx
import random
import pandas as pd

# Fixed color palettes
CLASSROOM_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"  # 6 colors
]

EDGE_TYPE_COLOR_MAP = {
    0: "#1f77b4",  # friends - blue
    1: "#ff7f0e",  # influential - orange
    2: "#2ca02c",  # feedback - green
    3: "#d62728",  # more_time - red
    4: "#9467bd",  # advice - purple
    5: "#8c564b",  # disrespect - brown
}

def attach_names_to_graph(graph: nx.DiGraph, df: pd.DataFrame) -> None:
    """
    Attaches 'first_name' and 'last_name' to nodes in the graph based on participant_id.

    Assumes:
      - df has columns: participant_id, first_name, last_name
      - participant_id values match node IDs in the graph
    """
    for _, row in df.iterrows():
        pid = row["participant_id"]
        if graph.has_node(pid):
            graph.nodes[pid]["first_name"] = row["first_name"]
            graph.nodes[pid]["last_name"] = row["last_name"]

def get_split_graphs(graph: nx.DiGraph, allocations: dict) -> dict:
    edge_type_map = {0: 'friends', 1: 'influential', 2: 'feedback', 3: 'more_time', 4: 'advice', 5: 'disrespect'}
    data = {}
    positions_by_classroom = {}

    classroom_allocs = allocations["Allocations"]
    details_lookup = allocations.get("Details", {})

    for i, (classroom, student_ids) in enumerate(classroom_allocs.items()):
        color = CLASSROOM_COLORS[i % len(CLASSROOM_COLORS)]

        # Assign fixed random positions (keys as str for consistency)
        positions = {
            str(sid): {"x": random.randint(0, 800), "y": random.randint(0, 600)}
            for sid in student_ids
        }
        positions_by_classroom[classroom] = positions

        # Subgraph and annotate with classroom + optional names
        classroom_subgraph = graph.subgraph(student_ids).copy()

        for node in classroom_subgraph.nodes:
            classroom_subgraph.nodes[node]["classroom"] = classroom
            classroom_subgraph.nodes[node]["color"] = color

            # Attach names if available
            if node in details_lookup:
                classroom_subgraph.nodes[node]["first_name"] = details_lookup[node].get("first_name", "")
                classroom_subgraph.nodes[node]["last_name"] = details_lookup[node].get("last_name", "")

        # Style the edges
        for u, v, d in classroom_subgraph.edges(data=True):
            edge_type = d.get("edge_type")
            d["connection_type"] = edge_type_map.get(edge_type)
            d["color"] = EDGE_TYPE_COLOR_MAP.get(edge_type, "#ccc")

        data[classroom] = nx_to_cytoscape(classroom_subgraph, positions)

        for edge_type_val, edge_type_name in edge_type_map.items():
            edges_of_type = [
                (u, v, d)
                for u, v, d in classroom_subgraph.edges(data=True)
                if d.get("edge_type") == edge_type_val
            ]
            sg = nx.DiGraph()
            sg.add_nodes_from(classroom_subgraph.nodes(data=True))
            sg.add_edges_from(edges_of_type)
            data[f"{classroom}__{edge_type_name}"] = nx_to_cytoscape(sg, positions)

    return {"subgraphs": data}

def nx_to_cytoscape(graph, positions=None):
    """
    Converts a NetworkX graph to Cytoscape.js compatible elements.
    Ensures all node and edge IDs are strings (no floats).
    Also ensures all positions are JSON serializable (lists, not numpy arrays).
    """
    elements = []
    for node, attrs in graph.nodes(data=True):
        node_id = str(int(node)) if isinstance(node, float) and node.is_integer() else str(node)
        data = {"id": node_id, "label": attrs.get("label", node_id)}
        data.update({k: v for k, v in attrs.items() if k != "label"})
        element = {"data": data}
        if positions and str(node) in positions:
            pos = positions[str(node)]
            if isinstance(pos, dict) and "x" in pos and "y" in pos:
                element["position"] = {"x": float(pos["x"]), "y": float(pos["y"])}
            else:
                if hasattr(pos, "tolist"):
                    pos = pos.tolist()
                elif isinstance(pos, tuple):
                    pos = list(pos)
                element["position"] = {"x": float(pos[0]), "y": float(pos[1])}
        elements.append(element)

    for u, v, attrs in graph.edges(data=True):
        source_id = str(int(u)) if isinstance(u, float) and u.is_integer() else str(u)
        target_id = str(int(v)) if isinstance(v, float) and v.is_integer() else str(v)
        data = {"source": source_id, "target": target_id}
        data.update(attrs)
        element = {"data": data}
        elements.append(element)

    return elements