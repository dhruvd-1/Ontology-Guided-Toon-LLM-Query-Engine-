"""
GNN Model for Schema-to-Ontology Mapping

Implements Graph Convolutional Network (GCN) for node classification.
"""

import os
os.environ['CUDA_VISIBLE_DEVICES'] = ''  # Force CPU only

import numpy as np
import json
from typing import Dict, Tuple, Optional

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch not available")


class GCNLayer(nn.Module):
    """Graph Convolutional Layer"""

    def __init__(self, in_features: int, out_features: int):
        super(GCNLayer, self).__init__()
        self.linear = nn.Linear(in_features, out_features)
        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.linear.weight)
        if self.linear.bias is not None:
            nn.init.zeros_(self.linear.bias)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of GCN layer

        Args:
            x: Node features [num_nodes, in_features]
            edge_index: Edge indices [2, num_edges]

        Returns:
            Updated node features [num_nodes, out_features]
        """
        # Linear transformation
        x = self.linear(x)

        # Aggregate neighbors
        num_nodes = x.size(0)

        # Create adjacency matrix (simplified, not optimized)
        adj = torch.zeros(num_nodes, num_nodes, device=x.device)
        adj[edge_index[0], edge_index[1]] = 1.0

        # Add self-loops
        adj = adj + torch.eye(num_nodes, device=x.device)

        # Normalize adjacency matrix (D^{-1/2} A D^{-1/2})
        degree = adj.sum(dim=1)
        degree_inv_sqrt = torch.pow(degree, -0.5)
        degree_inv_sqrt[torch.isinf(degree_inv_sqrt)] = 0.0

        norm = degree_inv_sqrt.view(-1, 1) * adj * degree_inv_sqrt.view(1, -1)

        # Aggregate
        x = torch.matmul(norm, x)

        return x


class GCN(nn.Module):
    """Graph Convolutional Network for node classification"""

    def __init__(
        self,
        num_features: int,
        num_classes: int,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.5
    ):
        super(GCN, self).__init__()

        self.num_features = num_features
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout

        # Build layers
        self.layers = nn.ModuleList()

        # Input layer
        self.layers.append(GCNLayer(num_features, hidden_dim))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(GCNLayer(hidden_dim, hidden_dim))

        # Output layer
        self.layers.append(GCNLayer(hidden_dim, num_classes))

        self.dropout_layer = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """
        Forward pass

        Args:
            x: Node features [num_nodes, num_features]
            edge_index: Edge indices [2, num_edges]

        Returns:
            Logits [num_nodes, num_classes]
        """
        # Apply GCN layers
        for i, layer in enumerate(self.layers[:-1]):
            x = layer(x, edge_index)
            x = F.relu(x)
            x = self.dropout_layer(x)

        # Output layer (no activation, no dropout)
        x = self.layers[-1](x, edge_index)

        return x

    def predict(self, x: torch.Tensor, edge_index: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict classes with confidence scores

        Args:
            x: Node features [num_nodes, num_features]
            edge_index: Edge indices [2, num_edges]

        Returns:
            predicted_classes: Predicted class indices [num_nodes]
            confidence_scores: Confidence scores [num_nodes]
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x, edge_index)
            probs = F.softmax(logits, dim=1)
            confidence_scores, predicted_classes = torch.max(probs, dim=1)

        return predicted_classes, confidence_scores


class SimpleGNNWrapper:
    """Wrapper for GNN model with simplified interface"""

    def __init__(
        self,
        num_features: int,
        num_classes: int,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.5,
        device: str = 'cpu'
    ):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch is required for GNN model")

        self.device = torch.device(device)
        self.model = GCN(
            num_features=num_features,
            num_classes=num_classes,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=dropout
        ).to(self.device)

        self.num_features = num_features
        self.num_classes = num_classes

    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        summary = f"""
GNN Model Summary:
------------------
Architecture: Graph Convolutional Network (GCN)
Layers: {self.model.num_layers}
Hidden dimensions: {self.model.hidden_dim}
Input features: {self.num_features}
Output classes: {self.num_classes}
Dropout: {self.model.dropout}

Parameters:
  Total: {total_params:,}
  Trainable: {trainable_params:,}

Device: {self.device}
"""
        return summary

    def save(self, filepath: str, metadata: Optional[Dict] = None):
        """Save model checkpoint"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'num_features': self.num_features,
            'num_classes': self.num_classes,
            'hidden_dim': self.model.hidden_dim,
            'num_layers': self.model.num_layers,
            'dropout': self.model.dropout,
        }

        if metadata:
            checkpoint['metadata'] = metadata

        torch.save(checkpoint, filepath)
        print(f"✓ Model saved to {filepath}")

    def load(self, filepath: str):
        """Load model checkpoint"""
        checkpoint = torch.load(filepath, map_location=self.device)

        self.model = GCN(
            num_features=checkpoint['num_features'],
            num_classes=checkpoint['num_classes'],
            hidden_dim=checkpoint['hidden_dim'],
            num_layers=checkpoint['num_layers'],
            dropout=checkpoint['dropout']
        ).to(self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.num_features = checkpoint['num_features']
        self.num_classes = checkpoint['num_classes']

        print(f"✓ Model loaded from {filepath}")

        return checkpoint.get('metadata')


def create_model(graph: Dict, hidden_dim: int = 128, num_layers: int = 2) -> SimpleGNNWrapper:
    """Create GNN model from graph"""
    model = SimpleGNNWrapper(
        num_features=graph['num_features'],
        num_classes=graph['num_classes'],
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        device='cpu'
    )

    print(model.get_model_summary())

    return model


if __name__ == '__main__':
    print("=== GNN Model Test ===\n")

    if not TORCH_AVAILABLE:
        print("PyTorch not available, skipping test")
        exit(1)

    # Load graph
    print("Loading graph...")
    graph_data = np.load('gnn/output/schema_graph.npz')
    with open('gnn/output/schema_graph_meta.json', 'r') as f:
        metadata = json.load(f)

    # Convert to torch tensors
    x = torch.from_numpy(graph_data['x']).float()
    edge_index = torch.from_numpy(graph_data['edge_index']).long()
    y = torch.from_numpy(graph_data['y']).long()

    print(f"✓ Graph loaded: {x.shape[0]} nodes, {edge_index.shape[1]} edges")

    # Create model
    print("\nCreating model...")
    model = SimpleGNNWrapper(
        num_features=x.shape[1],
        num_classes=int(graph_data['num_classes'][0]),
        hidden_dim=64,
        num_layers=2
    )

    print(model.get_model_summary())

    # Test forward pass
    print("Testing forward pass...")
    model.model.eval()
    with torch.no_grad():
        output = model.model(x, edge_index)
        print(f"✓ Output shape: {output.shape}")

        # Test prediction
        preds, confidence = model.model.predict(x, edge_index)
        print(f"✓ Predictions shape: {preds.shape}")
        print(f"✓ Confidence shape: {confidence.shape}")
        print(f"✓ Confidence range: [{confidence.min():.4f}, {confidence.max():.4f}]")

    print("\n✓ Model test complete!")
