import json
from collections import defaultdict
import networkx as nx
import random;
import pandas as pd

import random

# Fixed color palettes
CLASSROOM_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"  # 6 colors
]

EDGE_TYPE_COLOR_MAP = {
    0: "#1f77b4",  # friends - blue
    1: "#ff7f0e",  # advice - orange
    2: "#d62728",  # disrespect - red
    3: "#2ca02c",  # feedback - green
    4: "#9467bd",  # influential - purple
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
    edge_type_map = {0: 'friends', 1: 'advice', 2: 'disrespect', 3: 'feedback', 4: 'influential'}
    data = {}
    positions_by_classroom = {}

    classroom_allocs = allocations["Allocations"]
    details_lookup = allocations.get("Details", {})

    for i, (classroom, student_ids) in enumerate(classroom_allocs.items()):
        color = CLASSROOM_COLORS[i % len(CLASSROOM_COLORS)]

        # Assign fixed random positions
        positions = {
            sid: {"x": random.randint(0, 800), "y": random.randint(0, 600)}
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





def nx_to_cytoscape(graph: nx.DiGraph, positions: dict) -> list:
    elements = []

    #for node, attrs in graph.nodes(data=True):
    #    elements.append({
    #        "data": {"id": str(node), "label": str(node), **attrs},
    #        "position": positions.get(node, {"x": 0, "y": 0})  # fallback just in case
    #    })

    for node, attrs in graph.nodes(data=True):
        label = f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}".strip()
        elements.append({
            "data": {
                "id": str(node),
                "label": label if label else str(node),
                **attrs
            },
            "position": positions.get(node, {"x": 0, "y": 0})  # fallback just in case
        })

    for u, v, attrs in graph.edges(data=True):
        elements.append({
            "data": {"source": str(u), "target": str(v), **attrs}
        })


    return elements
