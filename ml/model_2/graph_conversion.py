from typing import Optional
import networkx as nx
import torch
from torch_geometric.data import Data
from torch_geometric.utils import from_networkx

def normalize_features(features: torch.Tensor) -> torch.Tensor:
    """
    Normalizes node features to have zero mean and unit variance.

    Args:
        features (torch.Tensor): The input feature tensor.

    Returns:
        torch.Tensor: The normalized feature tensor.
    """
    return (features - features.mean(dim=0)) / (features.std(dim=0) + 1e-9)

def preprocess_value(value, node, key):
    """
    Preprocesses a value to ensure it is numeric.

    Args:
        value: The value to preprocess.
        node: The node ID (for error reporting).
        key: The attribute key (for error reporting).

    Returns:
        float: The numeric value.

    Raises:
        ValueError: If the value cannot be converted to a numeric type.
    """
    if isinstance(value, str):
        try:
            # Attempt to convert string to float
            value = float(value)
        except ValueError:
            if value.upper() in ["NA", "N/A", "NULL", "NONE", ""]:
                # Handle common placeholders for missing values
                value = 0.0  # Default to 0.0 for missing values
            else:
                raise ValueError(f"Node {node} has a non-numeric value for '{key}': {value}")
    elif not isinstance(value, (int, float)):
        raise ValueError(f"Node {node} has a non-numeric value for '{key}': {value}")
    return float(value)

def graph_to_pyg_data(graph: nx.DiGraph, use_edge_types: bool = True) -> Data:
    """
    Converts a networkx.DiGraph to a PyTorch Geometric Data object.

    Args:
        graph (nx.DiGraph): The input directed graph.
        use_edge_types (bool): Whether to include edge types as one-hot encoded features.

    Returns:
        Data: A PyTorch Geometric Data object.

    Raises:
        ValueError: If any node is missing required features or has non-numeric values.
    """
    # Fixed node feature keys
    node_feature_keys = ["perc_academic", "perc_effort", "attendance"]

    # Validate and extract node features
    node_features = []
    for node, attrs in graph.nodes(data=True):
        feature_row = []
        for key in node_feature_keys:
            if key not in attrs:
                raise ValueError(f"Node {node} is missing the required feature '{key}'.")
            value = preprocess_value(attrs[key], node, key)
            feature_row.append(value)
        node_features.append(feature_row)
    node_features = torch.tensor(node_features, dtype=torch.float)
    node_features = normalize_features(node_features)

    # Add edge attributes if edge types are used
    if use_edge_types and "edge_type" in nx.get_edge_attributes(graph, "edge_type"):
        edge_types = nx.get_edge_attributes(graph, "edge_type")
        nx.set_edge_attributes(graph, {k: [v] for k, v in edge_types.items()}, "edge_attr")

    # Convert to PyTorch Geometric Data
    pyg_data = from_networkx(graph)

    # Add node features to PyG Data
    pyg_data.x = node_features

    # Add edge attributes if edge types are used
    if use_edge_types and "edge_attr" in pyg_data:
        edge_type_tensor = torch.tensor([attr[0] for attr in pyg_data.edge_attr], dtype=torch.long)
        pyg_data.edge_attr = torch.nn.functional.one_hot(edge_type_tensor).float()

    # Print summary
    print(f"PyG Data Summary: {pyg_data}")
    print(f"Number of nodes: {pyg_data.num_nodes}")
    print(f"Number of edges: {pyg_data.num_edges}")
    if pyg_data.x is not None:
        print(f"Node feature shape: {pyg_data.x.shape}")
    if pyg_data.edge_attr is not None:
        print(f"Edge attribute shape: {pyg_data.edge_attr.shape}")

    return pyg_data

def preprocessing(graph: nx.DiGraph, use_edge_types: bool = True) -> Data:
    """
    Preprocesses the graph by converting it to a PyTorch Geometric Data object.

    Args:
        graph (nx.DiGraph): The input directed graph.
        use_edge_types (bool): Whether to include edge types as one-hot encoded features.

    Returns:
        Data: A PyTorch Geometric Data object.
    """
    return graph_to_pyg_data(graph, use_edge_types=use_edge_types)