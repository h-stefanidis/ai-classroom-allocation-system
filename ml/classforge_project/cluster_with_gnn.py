import torch
import torch.nn.functional as F
from sklearn.cluster import KMeans
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv, GATConv, RGCNConv

# -------------------------
# Improved GNN Definition
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
        out = self.fusion(x_all)
        return F.normalize(out, p=2, dim=1)

# -------------------------
# Load Data & Setup
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

# -------------------------
# Train GNN
# -------------------------
for epoch in range(200):
    optimizer.zero_grad()
    embeddings = model(data.x, data.edge_index, data.edge_type)
    loss = embeddings.norm(p=2).mean()  # Simple unsupervised loss
    loss.backward()
    optimizer.step()
    if epoch % 25 == 0:
        print(f"Epoch {epoch} | Loss: {loss.item():.4f}")

# -------------------------
# Inference & Clustering
# -------------------------
model.eval()
with torch.no_grad():
    embeddings = model(data.x, data.edge_index, data.edge_type).cpu().numpy()

# KMeans
no_of_classrooms  = 5
num_clusters = no_of_classrooms
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
cluster_labels = torch.tensor(kmeans.fit_predict(embeddings), dtype=torch.long)

# Save graph with cluster labels
clustered_data = Data(
    x=data.x,
    edge_index=data.edge_index,
    edge_type=data.edge_type,
    y=cluster_labels
)
if hasattr(data, "participant_ids"):
    clustered_data.participant_ids = data.participant_ids

torch.save(clustered_data, "data/student_graph_clustered.pt")
print("✅ Improved GNN trained and graph clustered. Saved to: data/student_graph_clustered.pt")
