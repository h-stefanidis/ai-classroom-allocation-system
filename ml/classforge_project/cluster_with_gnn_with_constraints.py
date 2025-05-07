import os
import torch
import torch.nn.functional as F
import pandas as pd
import json
from sklearn.cluster import KMeans
from collections import defaultdict
from ortools.sat.python import cp_model
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv, GATConv, RGCNConv

# -------------------------
# GNN Definition
# -------------------------
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

# -------------------------
# Load Graph & Train GNN
# -------------------------
data = torch.load("data/student_graph.pt")

model = ImprovedClassForgeGNN(
    in_channels=data.num_node_features,
    hidden_channels=32,
    embedding_size=16,
    num_relations=len(set(data.edge_type.tolist()))
)

optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
model.train()

for epoch in range(200):
    optimizer.zero_grad()
    embeddings = model(data.x, data.edge_index, data.edge_type)
    loss = embeddings.norm(p=2).mean()
    loss.backward()
    optimizer.step()
    if epoch % 25 == 0:
        print(f"Epoch {epoch} | Loss: {loss.item():.4f}")

# -------------------------
# KMeans Clustering
# -------------------------
model.eval()
with torch.no_grad():
    embeddings = model(data.x, data.edge_index, data.edge_type).cpu().numpy()

num_students = embeddings.shape[0]
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
preferred_clusters = kmeans.fit_predict(embeddings)

# -------------------------
# Constraint-Based Allocation (CP-SAT)
# -------------------------
model_cp = cp_model.CpModel()
assignments = [model_cp.NewIntVar(0, num_clusters - 1, f"student_{i}") for i in range(num_students)]
target_per_class = num_students // num_clusters

# Balance class sizes
for c in range(num_clusters):
    class_members = []
    for i in range(num_students):
        is_in_class = model_cp.NewBoolVar(f"is_{i}_in_class_{c}")
        model_cp.Add(assignments[i] == c).OnlyEnforceIf(is_in_class)
        model_cp.Add(assignments[i] != c).OnlyEnforceIf(is_in_class.Not())
        class_members.append(is_in_class)
    model_cp.Add(sum(class_members) == target_per_class)

# Soft preference to match KMeans clusters
match_vars = []
for i in range(num_students):
    match = model_cp.NewBoolVar(f"match_{i}")
    model_cp.Add(assignments[i] == preferred_clusters[i]).OnlyEnforceIf(match)
    model_cp.Add(assignments[i] != preferred_clusters[i]).OnlyEnforceIf(match.Not())
    match_vars.append(match)

# Social constraints
friend_bonus = []
disrespect_penalty = []

for idx in range(data.edge_index.shape[1]):
    src, tgt = data.edge_index[:, idx].tolist()
    rel = int(data.edge_type[idx])
    same_class = model_cp.NewBoolVar(f"same_class_{src}_{tgt}")
    model_cp.Add(assignments[src] == assignments[tgt]).OnlyEnforceIf(same_class)
    model_cp.Add(assignments[src] != assignments[tgt]).OnlyEnforceIf(same_class.Not())
    if rel in [0, 1, 2, 3, 4]:
        friend_bonus.append(same_class)
    elif rel == 5:
        disrespect_penalty.append(same_class)

# Objective function
model_cp.Maximize(
    sum(match_vars) +
    2 * sum(friend_bonus) -
    5 * sum(disrespect_penalty)
)

# Solve
solver = cp_model.CpSolver()

# Optional: Set parameters for the solver (to handle timeout warning)
solver.parameters.max_time_in_seconds = 60
solver.parameters.log_search_progress = True  

status = solver.Solve(model_cp)

# -------------------------
# Save + Export
# -------------------------
if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    final_assignments = [solver.Value(assignments[i]) for i in range(num_students)]
    cluster_labels = torch.tensor(final_assignments, dtype=torch.long)

    clustered_data = Data(
        x=data.x,
        edge_index=data.edge_index,
        edge_type=data.edge_type,
        y=cluster_labels
    )
    if hasattr(data, "participant_ids"):
        clustered_data.participant_ids = data.participant_ids

    torch.save(clustered_data, "data/student_graph_clustered.pt")
    print("✅ GNN + CP-SAT allocation complete. Saved to: data/student_graph_clustered.pt")
    # exit()