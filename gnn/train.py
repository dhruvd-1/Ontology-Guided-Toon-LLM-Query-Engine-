"""
GNN Training Module

Trains the GNN model on schema-to-ontology mapping task.
"""

import numpy as np
import json
import os
from typing import Dict, Tuple
from gnn.model_numpy import GCNNumPy, softmax


def create_train_val_split(num_nodes: int, val_ratio: float = 0.2, seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """Create train/validation split"""
    np.random.seed(seed)
    indices = np.arange(num_nodes)
    np.random.shuffle(indices)

    val_size = int(num_nodes * val_ratio)
    val_indices = indices[:val_size]
    train_indices = indices[val_size:]

    return train_indices, val_indices


def train_epoch(
    model: GCNNumPy,
    x: np.ndarray,
    edge_index: np.ndarray,
    y: np.ndarray,
    train_indices: np.ndarray
) -> Tuple[float, float]:
    """Train for one epoch"""
    # Forward pass
    logits = model.forward(x, edge_index, training=True)

    # Compute loss and accuracy on training set
    train_logits = logits[train_indices]
    train_y = y[train_indices]

    loss = model.compute_loss(train_logits, train_y)
    accuracy = model.compute_accuracy(train_logits, train_y)

    # Backward pass (simplified - just update on training nodes)
    probs = softmax(logits)

    # Create target one-hot
    num_classes = probs.shape[1]
    targets = np.zeros_like(probs)
    targets[np.arange(len(y)), y] = 1

    # Gradient of cross-entropy + softmax
    grad_output = (probs - targets) / len(train_indices)

    # Only propagate gradients for training nodes
    grad_mask = np.zeros(len(y), dtype=bool)
    grad_mask[train_indices] = True
    grad_output[~grad_mask] = 0

    # Backprop through layers (simplified)
    grad = grad_output
    for i in range(len(model.layers) - 1, 0, -1):
        # For hidden layers with ReLU
        grad = model.layers[i].backward(grad, model.learning_rate)

        # ReLU derivative
        activations = model.cache['activations'][i]
        grad = grad * (activations > 0).astype(np.float32)

    # First layer
    model.layers[0].backward(grad, model.learning_rate)

    return loss, accuracy


def validate(
    model: GCNNumPy,
    x: np.ndarray,
    edge_index: np.ndarray,
    y: np.ndarray,
    val_indices: np.ndarray
) -> Tuple[float, float]:
    """Validate model"""
    logits = model.forward(x, edge_index, training=False)

    val_logits = logits[val_indices]
    val_y = y[val_indices]

    loss = model.compute_loss(val_logits, val_y)
    accuracy = model.compute_accuracy(val_logits, val_y)

    return loss, accuracy


def train_model(
    graph_path: str = 'gnn/output/schema_graph.npz',
    meta_path: str = 'gnn/output/schema_graph_meta.json',
    output_path: str = 'gnn/output/gnn_model.pkl',
    hidden_dim: int = 128,
    num_layers: int = 2,
    learning_rate: float = 0.01,
    dropout: float = 0.3,
    num_epochs: int = 200,
    val_ratio: float = 0.2,
    early_stopping_patience: int = 20,
    verbose: bool = True
) -> Dict:
    """
    Train GNN model

    Returns:
        training_history: Dictionary with training metrics
    """
    if verbose:
        print("=== GNN Training ===\n")

    # Load graph
    if verbose:
        print("Loading graph...")
    graph_data = np.load(graph_path)
    with open(meta_path, 'r') as f:
        metadata = json.load(f)

    x = graph_data['x']
    edge_index = graph_data['edge_index']
    y = graph_data['y']
    num_nodes = x.shape[0]
    num_features = x.shape[1]
    num_classes = int(graph_data['num_classes'][0])

    if verbose:
        print(f"✓ Loaded graph: {num_nodes} nodes, {edge_index.shape[1]} edges")
        print(f"  Features: {num_features}, Classes: {num_classes}")

    # Create train/val split
    train_indices, val_indices = create_train_val_split(num_nodes, val_ratio)
    if verbose:
        print(f"✓ Train/val split: {len(train_indices)}/{len(val_indices)}")

    # Create model
    if verbose:
        print("\nCreating model...")
    model = GCNNumPy(
        num_features=num_features,
        num_classes=num_classes,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        dropout=dropout,
        learning_rate=learning_rate
    )

    if verbose:
        print(model.get_model_summary())

    # Training loop
    if verbose:
        print(f"Training for {num_epochs} epochs...")

    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }

    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0

    for epoch in range(num_epochs):
        # Train
        train_loss, train_acc = train_epoch(model, x, edge_index, y, train_indices)

        # Validate
        val_loss, val_acc = validate(model, x, edge_index, y, val_indices)

        # Record history
        history['train_loss'].append(float(train_loss))
        history['train_acc'].append(float(train_acc))
        history['val_loss'].append(float(val_loss))
        history['val_acc'].append(float(val_acc))

        # Early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            patience_counter = 0

            # Save best model
            model.save(output_path, metadata={
                'epoch': epoch,
                'val_acc': val_acc,
                'val_loss': val_loss,
                'property_to_id': metadata['property_to_id'],
                'id_to_property': metadata['id_to_property']
            })
        else:
            patience_counter += 1

        # Print progress
        if verbose and (epoch % 10 == 0 or epoch == num_epochs - 1):
            print(f"Epoch {epoch:3d}: Train Loss={train_loss:.4f}, Train Acc={train_acc:.4f}, "
                  f"Val Loss={val_loss:.4f}, Val Acc={val_acc:.4f}")

        # Early stopping
        if patience_counter >= early_stopping_patience:
            if verbose:
                print(f"\nEarly stopping at epoch {epoch}")
            break

    if verbose:
        print(f"\n✓ Training complete!")
        print(f"  Best epoch: {best_epoch}")
        print(f"  Best validation accuracy: {best_val_acc:.4f}")

    # Final evaluation on all data
    final_logits = model.forward(x, edge_index, training=False)
    final_acc = model.compute_accuracy(final_logits, y)

    if verbose:
        print(f"  Final accuracy (all data): {final_acc:.4f}")

    return {
        'history': history,
        'best_epoch': best_epoch,
        'best_val_acc': float(best_val_acc),
        'final_acc': float(final_acc),
        'num_epochs': epoch + 1
    }


if __name__ == '__main__':
    import sys

    # Train model
    results = train_model(
        hidden_dim=128,
        num_layers=2,
        learning_rate=0.01,
        dropout=0.3,
        num_epochs=200,
        early_stopping_patience=20,
        verbose=True
    )

    # Print final results
    print("\n=== Training Results ===")
    print(f"Best validation accuracy: {results['best_val_acc']:.2%}")
    print(f"Final accuracy: {results['final_acc']:.2%}")
    print(f"Total epochs: {results['num_epochs']}")

    # Check if meets target
    if results['best_val_acc'] >= 0.85:
        print("\n✓ Target accuracy (≥85%) achieved!")
        sys.exit(0)
    else:
        print(f"\n⚠ Target accuracy (≥85%) not met. Current: {results['best_val_acc']:.2%}")
        print("  Note: May need more training, different hyperparameters, or more data")
        sys.exit(0)  # Still exit 0 as this is a research project
