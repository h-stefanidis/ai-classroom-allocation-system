from typing import Optional
import networkx as nx
import torch
from torch_geometric.data import Data
from torch_geometric.utils import from_networkx

def normalize_features(features: torch.Tensor) -> torch.Tensor:
    """
    Normalizes node features to have zero mean and unit variance.
    """
    return (features - features.mean(dim=0)) / (features.std(dim=0) + 1e-9)

def preprocess_value(value, node, key):
    """
    Preprocesses a value to ensure it is numeric.
    """
    if isinstance(value, str):
        try:
            value = value.strip().replace('%', '')  # Remove percentage sign if present
            value = float(value)
        except ValueError:
            if value.upper() in ["NA", "N/A", "NULL", "NONE", ""]:
                value = 0.0  # Default to 0.0 for missing values
            else:
                raise ValueError(f"Node {node} has a non-numeric value for '{key}': {value}")
    elif not isinstance(value, (int, float)):
        raise ValueError(f"Node {node} has a non-numeric value for '{key}': {value}")
    return float(value)

def graph_to_pyg_data(graph: nx.DiGraph, use_edge_types: bool = True) -> Data:
    """
    Converts a networkx.DiGraph to a PyTorch Geometric Data object.
    Preserves real student IDs in the `student_ids` field.
    """
    node_feature_keys = ["perc_academic", "perc_effort", "attendance"]

    for node, attrs in graph.nodes(data=True):
        for key in node_feature_keys:
            if key not in attrs:
                attrs[key] = 0.0  # Default value
        if "student_id" not in attrs:
            attrs["student_id"] = node  # Fallback to node index

    node_features = []
    real_ids = []
    for node, attrs in graph.nodes(data=True):
        feature_row = [preprocess_value(attrs[key], node, key) for key in node_feature_keys]
        node_features.append(feature_row)
        real_ids.append(attrs["student_id"])

    node_features = torch.tensor(node_features, dtype=torch.float)
    node_features = normalize_features(node_features)

    if use_edge_types and "edge_type" in nx.get_edge_attributes(graph, "edge_type"):
        edge_types = nx.get_edge_attributes(graph, "edge_type")
        nx.set_edge_attributes(graph, {k: [v] for k, v in edge_types.items()}, "edge_attr")

    pyg_data = from_networkx(graph)
    pyg_data.x = node_features
    pyg_data.student_ids = real_ids  # <-- Include real IDs here

    return pyg_data

def preprocessing(graph: nx.DiGraph, use_edge_types: bool = True) -> Data:
    """
    Preprocesses the graph by converting it to a PyTorch Geometric Data object.
    """
    return graph_to_pyg_data(graph, use_edge_types=use_edge_types)
