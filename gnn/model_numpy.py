"""
NumPy-based GNN Implementation

Pure Python/NumPy implementation of Graph Convolutional Network.
CPU-safe, no GPU dependencies required.
"""

import numpy as np
import json
import pickle
from typing import Dict, Tuple, Optional, List


def glorot_init(shape: Tuple[int, int]) -> np.ndarray:
    """Xavier/Glorot initialization"""
    limit = np.sqrt(6.0 / (shape[0] + shape[1]))
    return np.random.uniform(-limit, limit, shape).astype(np.float32)


def relu(x: np.ndarray) -> np.ndarray:
    """ReLU activation"""
    return np.maximum(0, x)


def relu_derivative(x: np.ndarray) -> np.ndarray:
    """Derivative of ReLU"""
    return (x > 0).astype(np.float32)


def softmax(x: np.ndarray) -> np.ndarray:
    """Softmax activation"""
    # Numerical stability
    exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
    return exp_x / np.sum(exp_x, axis=1, keepdims=True)


def cross_entropy_loss(y_pred: np.ndarray, y_true: np.ndarray) -> float:
    """Cross-entropy loss"""
    n = y_true.shape[0]
    log_probs = -np.log(y_pred[np.arange(n), y_true] + 1e-8)
    return np.mean(log_probs)


class GCNLayerNumPy:
    """Graph Convolutional Layer (NumPy implementation)"""

    def __init__(self, in_features: int, out_features: int):
        self.in_features = in_features
        self.out_features = out_features

        # Initialize weights
        self.W = glorot_init((in_features, out_features))
        self.b = np.zeros(out_features, dtype=np.float32)

        # For backpropagation
        self.cache = {}

    def normalize_adjacency(self, edge_index: np.ndarray, num_nodes: int) -> np.ndarray:
        """Create normalized adjacency matrix"""
        # Create adjacency matrix
        adj = np.zeros((num_nodes, num_nodes), dtype=np.float32)
        adj[edge_index[0], edge_index[1]] = 1.0

        # Add self-loops
        adj = adj + np.eye(num_nodes, dtype=np.float32)

        # Normalize: D^{-1/2} A D^{-1/2}
        degree = np.sum(adj, axis=1)
        degree_inv_sqrt = np.power(degree, -0.5)
        degree_inv_sqrt[np.isinf(degree_inv_sqrt)] = 0.0

        D_inv_sqrt = np.diag(degree_inv_sqrt)
        adj_normalized = D_inv_sqrt @ adj @ D_inv_sqrt

        return adj_normalized

    def forward(self, x: np.ndarray, adj_norm: np.ndarray) -> np.ndarray:
        """Forward pass"""
        # Aggregate neighbors: H' = A_norm @ X @ W + b
        h = adj_norm @ x @ self.W + self.b

        # Cache for backprop
        self.cache['x'] = x
        self.cache['adj_norm'] = adj_norm
        self.cache['h'] = h

        return h

    def backward(self, grad_output: np.ndarray, learning_rate: float) -> np.ndarray:
        """Backward pass"""
        x = self.cache['x']
        adj_norm = self.cache['adj_norm']

        # Gradients
        # Forward: h = adj_norm @ x @ W + b
        # Backward: grad_x = adj_norm @ (grad_output @ W.T)
        grad_W = (adj_norm @ x).T @ grad_output
        grad_b = np.sum(grad_output, axis=0)
        grad_x = adj_norm @ (grad_output @ self.W.T)

        # Update weights
        self.W -= learning_rate * grad_W
        self.b -= learning_rate * grad_b

        return grad_x


class GCNNumPy:
    """Graph Convolutional Network (NumPy implementation)"""

    def __init__(
        self,
        num_features: int,
        num_classes: int,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.5,
        learning_rate: float = 0.01
    ):
        self.num_features = num_features
        self.num_classes = num_classes
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.learning_rate = learning_rate

        # Build layers
        self.layers = []

        # Input layer
        self.layers.append(GCNLayerNumPy(num_features, hidden_dim))

        # Hidden layers
        for _ in range(num_layers - 2):
            self.layers.append(GCNLayerNumPy(hidden_dim, hidden_dim))

        # Output layer
        self.layers.append(GCNLayerNumPy(hidden_dim, num_classes))

        # Cache for backprop
        self.cache = {}
        self.adj_norm = None

    def forward(self, x: np.ndarray, edge_index: np.ndarray, training: bool = False) -> np.ndarray:
        """Forward pass"""
        # Normalize adjacency once
        if self.adj_norm is None:
            self.adj_norm = self.layers[0].normalize_adjacency(edge_index, x.shape[0])

        h = x
        activations = [h]

        # Apply layers
        for i, layer in enumerate(self.layers[:-1]):
            h = layer.forward(h, self.adj_norm)
            h = relu(h)

            # Dropout during training
            if training and self.dropout > 0:
                mask = (np.random.rand(*h.shape) > self.dropout).astype(np.float32)
                h = h * mask / (1 - self.dropout)

            activations.append(h)

        # Output layer (no activation, no dropout)
        h = self.layers[-1].forward(h, self.adj_norm)
        activations.append(h)

        # Cache for backprop
        self.cache['activations'] = activations

        return h

    def predict(self, x: np.ndarray, edge_index: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict classes with confidence scores

        Returns:
            predicted_classes: Predicted class indices [num_nodes]
            confidence_scores: Confidence scores [num_nodes]
        """
        logits = self.forward(x, edge_index, training=False)
        probs = softmax(logits)

        predicted_classes = np.argmax(probs, axis=1)
        confidence_scores = np.max(probs, axis=1)

        return predicted_classes, confidence_scores

    def compute_loss(self, logits: np.ndarray, y: np.ndarray) -> float:
        """Compute cross-entropy loss"""
        probs = softmax(logits)
        return cross_entropy_loss(probs, y)

    def compute_accuracy(self, logits: np.ndarray, y: np.ndarray) -> float:
        """Compute classification accuracy"""
        preds = np.argmax(logits, axis=1)
        return np.mean(preds == y)

    def get_model_summary(self) -> str:
        """Get model architecture summary"""
        total_params = sum(
            layer.W.size + layer.b.size
            for layer in self.layers
        )

        summary = f"""
GNN Model Summary (NumPy Implementation):
------------------------------------------
Architecture: Graph Convolutional Network (GCN)
Layers: {self.num_layers}
Hidden dimensions: {self.hidden_dim}
Input features: {self.num_features}
Output classes: {self.num_classes}
Dropout: {self.dropout}
Learning rate: {self.learning_rate}

Parameters:
  Total: {total_params:,}
  Trainable: {total_params:,}

Device: CPU (NumPy)
"""
        return summary

    def save(self, filepath: str, metadata: Optional[Dict] = None):
        """Save model"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        checkpoint = {
            'num_features': self.num_features,
            'num_classes': self.num_classes,
            'hidden_dim': self.hidden_dim,
            'num_layers': self.num_layers,
            'dropout': self.dropout,
            'learning_rate': self.learning_rate,
            'layers': [(layer.W, layer.b) for layer in self.layers],
            'metadata': metadata
        }

        with open(filepath, 'wb') as f:
            pickle.dump(checkpoint, f)

        print(f"✓ Model saved to {filepath}")

    def load(self, filepath: str) -> Optional[Dict]:
        """Load model"""
        with open(filepath, 'rb') as f:
            checkpoint = pickle.load(f)

        self.num_features = checkpoint['num_features']
        self.num_classes = checkpoint['num_classes']
        self.hidden_dim = checkpoint['hidden_dim']
        self.num_layers = checkpoint['num_layers']
        self.dropout = checkpoint['dropout']
        self.learning_rate = checkpoint['learning_rate']

        # Rebuild layers
        self.layers = []
        self.layers.append(GCNLayerNumPy(self.num_features, self.hidden_dim))
        for _ in range(self.num_layers - 2):
            self.layers.append(GCNLayerNumPy(self.hidden_dim, self.hidden_dim))
        self.layers.append(GCNLayerNumPy(self.hidden_dim, self.num_classes))

        # Load weights
        for layer, (W, b) in zip(self.layers, checkpoint['layers']):
            layer.W = W
            layer.b = b

        self.adj_norm = None  # Will be recomputed on first forward pass

        print(f"✓ Model loaded from {filepath}")

        return checkpoint.get('metadata')


if __name__ == '__main__':
    print("=== NumPy GNN Model Test ===\n")

    # Load graph
    print("Loading graph...")
    graph_data = np.load('gnn/output/schema_graph.npz')

    x = graph_data['x']
    edge_index = graph_data['edge_index']
    y = graph_data['y']

    print(f"✓ Graph loaded: {x.shape[0]} nodes, {edge_index.shape[1]} edges")

    # Create model
    print("\nCreating model...")
    model = GCNNumPy(
        num_features=x.shape[1],
        num_classes=int(graph_data['num_classes'][0]),
        hidden_dim=64,
        num_layers=2,
        dropout=0.5,
        learning_rate=0.01
    )

    print(model.get_model_summary())

    # Test forward pass
    print("Testing forward pass...")
    logits = model.forward(x, edge_index, training=False)
    print(f"✓ Output shape: {logits.shape}")

    # Test prediction
    preds, confidence = model.predict(x, edge_index)
    print(f"✓ Predictions shape: {preds.shape}")
    print(f"✓ Confidence shape: {confidence.shape}")
    print(f"✓ Confidence range: [{confidence.min():.4f}, {confidence.max():.4f}]")

    # Test loss and accuracy
    loss = model.compute_loss(logits, y)
    accuracy = model.compute_accuracy(logits, y)
    print(f"✓ Initial loss: {loss:.4f}")
    print(f"✓ Initial accuracy: {accuracy:.4f}")

    print("\n✓ Model test complete!")
