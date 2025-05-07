
import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv, GATConv, RGCNConv

class ClassForgeEnsembleGNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, embedding_size, num_relations):
        super().__init__()
        self.sage = SAGEConv(in_channels, hidden_channels)
        self.gat = GATConv(hidden_channels, hidden_channels, heads=2, concat=False)
        self.rgcn = RGCNConv(hidden_channels, embedding_size, num_relations=num_relations)

    def forward(self, x, edge_index, edge_type):
        x1 = F.relu(self.sage(x, edge_index))
        x2 = F.relu(self.gat(x1, edge_index))
        x3 = self.rgcn(x2, edge_index, edge_type)
        return torch.cat([x1, x2, x3], dim=1)
