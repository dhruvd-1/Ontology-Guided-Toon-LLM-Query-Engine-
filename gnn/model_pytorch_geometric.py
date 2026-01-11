"""
PyTorch Geometric GNN Implementation

Replaces NumPy GNN with proper PyTorch Geometric model.
Supports both GAT (Graph Attention Network) and GCN (Graph Convolutional Network).

Requirements:
- PyTorch 2.0+
- PyTorch Geometric
- CPU-safe with GPU support
"""

import os
import json
import numpy as np
from typing import Dict, Optional, Tuple

# Try importing PyTorch
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("WARNING: PyTorch not available")

# Try importing PyTorch Geometric
try:
    import torch_geometric
    from torch_geometric.nn import GATConv, GCNConv, LayerNorm
    from torch_geometric.data import Data
    PYTORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    PYTORCH_GEOMETRIC_AVAILABLE = False
    if TORCH_AVAILABLE:
        print("WARNING: PyTorch Geometric not available")


class GATModel(nn.Module):
    """
    Graph Attention Network for schema-to-ontology mapping

    Architecture:
    - Multi-head attention (8 heads)
    - 2+ message-passing layers
    - LayerNorm + Dropout
    - Residual connections
    """

    def __init__(
        self,
        num_features: int,
        num_classes: int,
        hidden_dim: int = 256,
        num_layers: int = 3,
        num_heads: int = 8,
        dropout: float = 0.6,
    ):
        super(GATModel, self).__init__()

        self.num_features = num_features
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.dropout = dropout

        # Input projection
        self.input_proj = nn.Linear(num_features, hidden_dim)

        # GAT layers
        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()

        # First layer
        self.convs.append(
            GATConv(
                hidden_dim,
                hidden_dim // num_heads,
                heads=num_heads,
                dropout=dropout,
                concat=True
            )
        )
        self.norms.append(LayerNorm(hidden_dim))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(
                GATConv(
                    hidden_dim,
                    hidden_dim // num_heads,
                    heads=num_heads,
                    dropout=dropout,
                    concat=True
                )
            )
            self.norms.append(LayerNorm(hidden_dim))

        # Output layer (no concatenation)
        self.convs.append(
            GATConv(
                hidden_dim,
                num_classes,
                heads=num_heads,
                dropout=0.0,
                concat=False
            )
        )

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
        # Input projection
        x = self.input_proj(x)
        x = F.elu(x)
        x = self.dropout_layer(x)

        # GAT layers with residual connections
        for i, (conv, norm) in enumerate(zip(self.convs[:-1], self.norms)):
            identity = x
            x = conv(x, edge_index)
            x = norm(x)
            x = F.elu(x)
            x = self.dropout_layer(x)

            # Residual connection
            if identity.size(-1) == x.size(-1):
                x = x + identity

        # Output layer
        x = self.convs[-1](x, edge_index)

        return x

    def predict(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Predict with confidence scores

        Returns:
            predicted_classes: [num_nodes]
            confidence_scores: [num_nodes]
        """
        self.eval()
        with torch.no_grad():
            logits = self.forward(x, edge_index)
            probs = F.softmax(logits, dim=1)
            confidence_scores, predicted_classes = torch.max(probs, dim=1)

        return predicted_classes, confidence_scores


class GCNModel(nn.Module):
    """
    Graph Convolutional Network for schema-to-ontology mapping

    Simpler alternative to GAT.
    """

    def __init__(
        self,
        num_features: int,
        num_classes: int,
        hidden_dim: int = 256,
        num_layers: int = 3,
        dropout: float = 0.5,
    ):
        super(GCNModel, self).__init__()

        self.num_features = num_features
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout

        # Layers
        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()

        # Input layer
        self.convs.append(GCNConv(num_features, hidden_dim))
        self.norms.append(LayerNorm(hidden_dim))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.convs.append(GCNConv(hidden_dim, hidden_dim))
            self.norms.append(LayerNorm(hidden_dim))

        # Output layer
        self.convs.append(GCNConv(hidden_dim, num_classes))

        self.dropout_layer = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        for i, (conv, norm) in enumerate(zip(self.convs[:-1], self.norms)):
            x = conv(x, edge_index)
            x = norm(x)
            x = F.relu(x)
            x = self.dropout_layer(x)

        # Output
        x = self.convs[-1](x, edge_index)
        return x

    def predict(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Predict with confidence scores"""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x, edge_index)
            probs = F.softmax(logits, dim=1)
            confidence_scores, predicted_classes = torch.max(probs, dim=1)

        return predicted_classes, confidence_scores


def create_model(
    num_features: int,
    num_classes: int,
    model_type: str = 'gat',
    hidden_dim: int = 256,
    num_layers: int = 3,
    device: str = 'cpu'
) -> nn.Module:
    """
    Create GNN model

    Args:
        num_features: Number of input features
        num_classes: Number of output classes
        model_type: 'gat' or 'gcn'
        hidden_dim: Hidden dimension size
        num_layers: Number of message-passing layers
        device: 'cpu' or 'cuda'

    Returns:
        Model instance
    """
    if not TORCH_AVAILABLE or not PYTORCH_GEOMETRIC_AVAILABLE:
        raise RuntimeError("PyTorch and PyTorch Geometric are required")

    if model_type.lower() == 'gat':
        model = GATModel(
            num_features=num_features,
            num_classes=num_classes,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            num_heads=8,
            dropout=0.6
        )
    elif model_type.lower() == 'gcn':
        model = GCNModel(
            num_features=num_features,
            num_classes=num_classes,
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            dropout=0.5
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    model = model.to(device)

    return model


def get_model_summary(model: nn.Module) -> str:
    """Get model architecture summary"""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    summary = f"""
Model Architecture:
-------------------
Type: {model.__class__.__name__}
Layers: {getattr(model, 'num_layers', 'N/A')}
Hidden dim: {getattr(model, 'hidden_dim', 'N/A')}
Input features: {getattr(model, 'num_features', 'N/A')}
Output classes: {getattr(model, 'num_classes', 'N/A')}

Parameters:
  Total: {total_params:,}
  Trainable: {trainable_params:,}
"""

    return summary


if __name__ == '__main__':
    print("=== PyTorch Geometric GNN Test ===\n")

    if not TORCH_AVAILABLE:
        print("✗ PyTorch not available")
        print("  Install with: pip install torch")
        exit(1)

    if not PYTORCH_GEOMETRIC_AVAILABLE:
        print("✗ PyTorch Geometric not available")
        print("  Install with: pip install torch-geometric")
        exit(1)

    print("✓ PyTorch available:", torch.__version__)
    print("✓ PyTorch Geometric available:", torch_geometric.__version__)

    # Test model creation
    print("\nTesting model creation...")

    # GAT model
    gat_model = create_model(
        num_features=96,
        num_classes=50,
        model_type='gat',
        hidden_dim=256,
        num_layers=3
    )
    print("\n✓ GAT Model created:")
    print(get_model_summary(gat_model))

    # Test forward pass
    print("Testing forward pass...")
    x = torch.randn(100, 96)
    edge_index = torch.randint(0, 100, (2, 500))

    logits = gat_model(x, edge_index)
    print(f"✓ Output shape: {logits.shape}")

    preds, conf = gat_model.predict(x, edge_index)
    print(f"✓ Predictions shape: {preds.shape}")
    print(f"✓ Confidence range: [{conf.min():.4f}, {conf.max():.4f}]")

    print("\n✓ PyTorch Geometric GNN test complete!")
