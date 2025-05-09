import torch
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv
from torch_geometric.data import Data

class GraphSAGE(torch.nn.Module):
    def __init__(self, in_channels: int, hidden_channels: int, out_channels: int, num_layers: int = 2, dropout: float = 0.5):
        """
        GraphSAGE model with configurable layers and dropout.

        Args:
            in_channels (int): Input feature dimension.
            hidden_channels (int): Hidden layer dimension.
            out_channels (int): Output embedding dimension.
            num_layers (int): Number of GraphSAGE layers.
            dropout (float): Dropout probability.
        """
        super(GraphSAGE, self).__init__()
        self.convs = torch.nn.ModuleList()
        self.convs.append(SAGEConv(in_channels, hidden_channels))
        for _ in range(num_layers - 2):
            self.convs.append(SAGEConv(hidden_channels, hidden_channels))
        self.convs.append(SAGEConv(hidden_channels, out_channels))
        self.dropout = dropout

    def forward(self, x, edge_index):
        """
        Forward pass for GraphSAGE.

        Args:
            x (torch.Tensor): Node features [num_nodes, in_channels].
            edge_index (torch.Tensor): Edge index [2, num_edges].

        Returns:
            torch.Tensor: Node embeddings [num_nodes, out_channels].
        """
        for conv in self.convs[:-1]:
            x = conv(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, p=self.dropout, training=self.training)
        x = self.convs[-1](x, edge_index)
        return x

def generate_embeddings(data: Data, hidden_channels: int = 32, out_channels: int = 16, num_layers: int = 3, dropout: float = 0.5) -> torch.Tensor:
    """
    Generates node embeddings using a GraphSAGE model.

    Args:
        data (Data): PyTorch Geometric Data object.
        hidden_channels (int): Hidden layer dimension.
        out_channels (int): Output embedding dimension.
        num_layers (int): Number of GraphSAGE layers.
        dropout (float): Dropout probability.

    Returns:
        torch.Tensor: Final node embeddings [num_nodes, embedding_dim].
    """
    # Initialize the GraphSAGE model
    model = GraphSAGE(
        in_channels=data.num_node_features,
        hidden_channels=hidden_channels,
        out_channels=out_channels,
        num_layers=num_layers,
        dropout=dropout
    )

    # Generate embeddings
    model.eval()
    with torch.no_grad():
        embeddings = model(data.x, data.edge_index)
    return embeddings