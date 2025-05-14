import os
import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
from ortools.sat.python import cp_model
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv, GATConv, RGCNConv
from .preserved_relationship import compute_preserved_relationships
 
class ImprovedClassForgeGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, embedding_size, num_relations):
        super().__init__()
        self.sage1 = SAGEConv(in_channels, hidden_channels)
        self.sage2 = SAGEConv(hidden_channels, hidden_channels)
        self.gat1 = GATConv(hidden_channels, hidden_channels, heads=2, concat=False)
        self.rgcn = RGCNConv(hidden_channels, embedding_size, num_relations=num_relations)
        self.fusion = torch.nn.Linear(hidden_channels + hidden_channels + embedding_size, embedding_size)
 
    def forward(self, x, edge_index, edge_type):
        x_sage = F.relu(self.sage1(x, edge_index))
        x_sage = F.dropout(F.relu(self.sage2(x_sage, edge_index)), p=0.2, training=self.training)
        x_gat = F.dropout(F.relu(self.gat1(x_sage, edge_index)), p=0.2, training=self.training)
        x_rgcn = self.rgcn(x_gat, edge_index, edge_type)
        x_all = torch.cat([x_sage, x_gat, x_rgcn], dim=1)
        return F.normalize(self.fusion(x_all), p=2, dim=1)
 
def cluster_students_with_gnn(graph, num_clusters):
    """
    Function to perform GNN-based clustering with constraints.
    Args:
        graph (torch_geometric.data.Data): Input graph data.
        num_clusters (int): Number of clusters (classrooms) to assign.
    Returns:
        torch_geometric.data.Data: Clustered graph data with assignments.
    """
    model = ImprovedClassForgeGNN(
        in_channels=graph.num_node_features,
        hidden_channels=32,
        embedding_size=16,
        num_relations=len(set(graph.edge_type.tolist()))
    )

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    model.train()

    for epoch in range(200):
        optimizer.zero_grad()
        embeddings = model(graph.x, graph.edge_index, graph.edge_type)
        loss = embeddings.norm(p=2).mean()
        loss.backward()
        optimizer.step()
        if epoch % 25 == 0:
            print(f"Epoch {epoch} | Loss: {loss.item():.4f}")

    model.eval()
    with torch.no_grad():
        embeddings = model(graph.x, graph.edge_index, graph.edge_type).cpu().numpy()

    num_students = embeddings.shape[0]
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    preferred_clusters = kmeans.fit_predict(embeddings)

    model_cp = cp_model.CpModel()
    # Assign classroom IDs starting from 1
    assignments = [model_cp.NewIntVar(1, num_clusters, f"student_{i}") for i in range(num_students)]

    # Balanced size constraints
    base = num_students // num_clusters
    remainder = num_students % num_clusters
    min_per_class = base
    max_per_class = base + 1 if remainder > 0 else base

    for c in range(1, num_clusters + 1):
        class_members = []
        for i in range(num_students):
            is_in_class = model_cp.NewBoolVar(f"is_{i}_in_class_{c}")
            model_cp.Add(assignments[i] == c).OnlyEnforceIf(is_in_class)
            model_cp.Add(assignments[i] != c).OnlyEnforceIf(is_in_class.Not())
            class_members.append(is_in_class)
        model_cp.Add(sum(class_members) >= min_per_class)
        model_cp.Add(sum(class_members) <= max_per_class)

    # Match preferred k-means cluster (adjusted for 1-indexed cluster IDs)
    match_vars = []
    for i in range(num_students):
        match = model_cp.NewBoolVar(f"match_{i}")
        model_cp.Add(assignments[i] == (preferred_clusters[i] + 1)).OnlyEnforceIf(match)
        model_cp.Add(assignments[i] != (preferred_clusters[i] + 1)).OnlyEnforceIf(match.Not())
        match_vars.append(match)

    # Handle relationship-based bonuses/penalties
    friend_rels = {0, 1, 2, 3, 4}  # example: friends, advice, influence, etc.
    disrespect_rels = {5}         # example: disrespect relation

    friend_bonus = []
    disrespect_penalty = []

    for idx in range(graph.edge_index.shape[1]):
        src, tgt = graph.edge_index[:, idx].tolist()
        rel = int(graph.edge_type[idx])
        same_class = model_cp.NewBoolVar(f"same_class_{src}_{tgt}")
        model_cp.Add(assignments[src] == assignments[tgt]).OnlyEnforceIf(same_class)
        model_cp.Add(assignments[src] != assignments[tgt]).OnlyEnforceIf(same_class.Not())
        if rel in friend_rels:
            friend_bonus.append(same_class)
        elif rel in disrespect_rels:
            disrespect_penalty.append(same_class)

    # Objective: maximize match + friendships, minimize disrespect
    model_cp.Maximize(
        sum(match_vars) +
        2 * sum(friend_bonus) -
        5 * sum(disrespect_penalty)
    )

    # Solve the constraint model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    solver.parameters.log_search_progress = True
    status = solver.Solve(model_cp)

    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        final_assignments = [solver.Value(assignments[i]) for i in range(num_students)]
        cluster_labels = torch.tensor(final_assignments, dtype=torch.long)

        clustered_data = Data(
            x=graph.x,
            edge_index=graph.edge_index,
            edge_type=graph.edge_type,
            y=cluster_labels
        )
        if hasattr(graph, "participant_ids"):
            clustered_data.participant_ids = graph.participant_ids
        print("---------------")
        return clustered_data, graph

    raise RuntimeError("Clustering failed: No feasible solution found.")
