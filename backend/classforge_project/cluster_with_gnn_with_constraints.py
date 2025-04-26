import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, GATConv, RGCNConv
from sklearn.cluster import KMeans
from ortools.sat.python import cp_model
import pandas as pd

# -------------------------
# GNN Model Definition
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
# Load Graph & Student Data
# -------------------------
graph = torch.load("data/student_graph.pt")
df = pd.read_csv("SNA_GNN_Grouped_Students.csv")
num_students = graph.num_nodes
num_groups = 6
target_group_size = num_students // num_groups

# -------------------------
# Train GNN
# -------------------------
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

model.eval()
with torch.no_grad():
    embeddings = model(graph.x, graph.edge_index, graph.edge_type).cpu().numpy()

# -------------------------
# Cluster GNN Embeddings
# -------------------------
kmeans = KMeans(n_clusters=num_groups, random_state=42)
gnn_clusters = kmeans.fit_predict(embeddings)
df["GNN_Cluster"] = gnn_clusters

# -------------------------
# CP-SAT Optimization
# -------------------------
model_cp = cp_model.CpModel()
assignments = [model_cp.NewIntVar(0, num_groups - 1, f"student_{i}") for i in range(num_students)]

# Group size constraint
for g in range(num_groups):
    model_cp.Add(sum(assignments[i] == g for i in range(num_students)) == target_group_size)

# Encourage matching GNN cluster
match_vars = []
for i in range(num_students):
    match = model_cp.NewBoolVar(f"match_cluster_{i}")
    model_cp.Add(assignments[i] == gnn_clusters[i]).OnlyEnforceIf(match)
    model_cp.Add(assignments[i] != gnn_clusters[i]).OnlyEnforceIf(match.Not())
    match_vars.append(match)

# -------------------------
# Social Edge Constraints
# -------------------------
edge_index = graph.edge_index.t().tolist()
edge_type = graph.edge_type.tolist()

positive_types = {0, 1, 2, 3, 4}  # Friend, Influence, Feedback, MoreTime, Advice
disrespect_type = 5
positive_penalties = []
disrespect_penalties = []

for (i, j), t in zip(edge_index, edge_type):
    same_group = model_cp.NewBoolVar(f"same_group_{i}_{j}")
    model_cp.Add(assignments[i] == assignments[j]).OnlyEnforceIf(same_group)
    model_cp.Add(assignments[i] != assignments[j]).OnlyEnforceIf(same_group.Not())
    penalty = model_cp.NewIntVar(0, 1, f"penalty_{i}_{j}")
    if t in positive_types:
        model_cp.Add(penalty == 1 - same_group)
        positive_penalties.append(penalty)
    elif t == disrespect_type:
        model_cp.Add(penalty == same_group)
        disrespect_penalties.append(penalty)

# -------------------------
# Objective: Maximize alignment & social harmony
# -------------------------
model_cp.Maximize(
    sum(match_vars) -
    5 * sum(positive_penalties) -
    10 * sum(disrespect_penalties)
)

# -------------------------
# Solve
# -------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model_cp)

if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
    df["Optimized_Group"] = [solver.Value(assignments[i]) for i in range(num_students)]
    df[["Participant-ID", "GNN_Cluster", "Optimized_Group"]].to_csv("optimized_allocation_with_gnn_social.csv", index=False)
    print("✅ Allocation complete. Saved to optimized_allocation_with_gnn_social.csv")
else:
    print("❌ No feasible solution found.")
