"""
PyTorch Geometric GNN Training Pipeline

Features:
- Class-weighted loss for imbalanced data
- Early stopping with patience
- GPU support with CPU fallback
- Learning rate scheduling
- Comprehensive metrics logging

⚠️ NOTE: This requires manual execution on GPU for best results.
The script is CPU-safe but training will be slow.
"""

import os
import json
import numpy as np
import time
from typing import Dict, Optional

try:
    import torch
    import torch.nn.functional as F
    from torch.optim import Adam
    from torch.optim.lr_scheduler import ReduceLROnPlateau
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("ERROR: PyTorch not available. Install with: pip install torch")

try:
    from gnn.model_pytorch_geometric import create_model, get_model_summary
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    if TORCH_AVAILABLE:
        print("ERROR: Could not import model. PyTorch Geometric may not be installed.")


def compute_class_weights(labels: torch.Tensor, num_classes: int) -> torch.Tensor:
    """
    Compute class weights for imbalanced dataset

    Args:
        labels: Class labels [num_samples]
        num_classes: Total number of classes

    Returns:
        Class weights [num_classes]
    """
    counts = torch.bincount(labels, minlength=num_classes).float()
    weights = 1.0 / (counts + 1.0)  # Add 1 to avoid division by zero
    weights = weights / weights.sum() * num_classes  # Normalize
    return weights


def evaluate(
    model: torch.nn.Module,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    y: torch.Tensor,
    mask: torch.Tensor
) -> Dict[str, float]:
    """
    Evaluate model on given data

    Returns:
        Dictionary with metrics
    """
    model.eval()

    with torch.no_grad():
        logits = model(x, edge_index)
        preds = logits[mask].argmax(dim=1)
        labels = y[mask]

        # Accuracy
        acc = (preds == labels).float().mean().item()

        # Top-3 accuracy
        top3_preds = logits[mask].topk(3, dim=1)[1]
        top3_acc = (top3_preds == labels.unsqueeze(1)).any(dim=1).float().mean().item()

        # Per-class metrics (simplified)
        # For full confusion matrix, use sklearn in evaluation

        # Loss
        loss = F.cross_entropy(logits[mask], labels).item()

    return {
        'accuracy': acc,
        'top3_accuracy': top3_acc,
        'loss': loss
    }


def train_epoch(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    x: torch.Tensor,
    edge_index: torch.Tensor,
    y: torch.Tensor,
    train_mask: torch.Tensor,
    class_weights: Optional[torch.Tensor] = None
) -> float:
    """
    Train for one epoch

    Returns:
        Training loss
    """
    model.train()

    optimizer.zero_grad()

    # Forward
    logits = model(x, edge_index)

    # Loss
    if class_weights is not None:
        loss = F.cross_entropy(
            logits[train_mask],
            y[train_mask],
            weight=class_weights
        )
    else:
        loss = F.cross_entropy(logits[train_mask], y[train_mask])

    # Backward
    loss.backward()

    # Gradient clipping
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

    optimizer.step()

    return loss.item()


def train(
    graph_path: str = 'gnn/balanced_output/schema_graph.npz',
    meta_path: str = 'gnn/balanced_output/schema_graph_meta.json',
    splits_path: str = 'data_generation/balanced_output/splits.json',
    output_dir: str = 'gnn/pytorch_output',
    model_type: str = 'gat',
    hidden_dim: int = 256,
    num_layers: int = 3,
    learning_rate: float = 0.001,
    weight_decay: float = 5e-4,
    num_epochs: int = 500,
    patience: int = 50,
    device: str = None,
    verbose: bool = True
) -> Dict:
    """
    Train PyTorch Geometric GNN

    ⚠️ NOTE: For best results, run on GPU:
    python -m gnn.train_pytorch --device cuda

    Args:
        graph_path: Path to graph data
        meta_path: Path to metadata
        splits_path: Path to train/val/test splits
        output_dir: Output directory
        model_type: 'gat' or 'gcn'
        hidden_dim: Hidden dimension
        num_layers: Number of layers
        learning_rate: Learning rate
        weight_decay: L2 regularization
        num_epochs: Maximum epochs
        patience: Early stopping patience
        device: 'cpu', 'cuda', or None (auto-detect)
        verbose: Print training progress

    Returns:
        Training history and results
    """
    if not TORCH_AVAILABLE or not MODEL_AVAILABLE:
        raise RuntimeError(
            "PyTorch and PyTorch Geometric are required.\n"
            "Install with:\n"
            "  pip install torch\n"
            "  pip install torch-geometric"
        )

    # Device
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    if verbose:
        print("=== PyTorch Geometric GNN Training ===\n")
        print(f"Device: {device}")
        if device == 'cpu':
            print("⚠️  WARNING: Training on CPU will be slow")
            print("   For faster training, use GPU: python -m gnn.train_pytorch --device cuda")
        print()

    # Load graph
    if verbose:
        print("Loading graph data...")

    graph_data = np.load(graph_path)
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    with open(splits_path, 'r') as f:
        splits = json.load(f)

    # Convert to PyTorch
    x = torch.from_numpy(graph_data['x']).float().to(device)
    edge_index = torch.from_numpy(graph_data['edge_index']).long().to(device)
    y = torch.from_numpy(graph_data['y']).long().to(device)

    num_nodes = x.size(0)
    num_features = x.size(1)
    num_classes = int(graph_data['num_classes'][0])

    # Create masks
    train_mask = torch.zeros(num_nodes, dtype=torch.bool, device=device)
    val_mask = torch.zeros(num_nodes, dtype=torch.bool, device=device)
    test_mask = torch.zeros(num_nodes, dtype=torch.bool, device=device)

    train_mask[splits['train']] = True
    val_mask[splits['val']] = True
    test_mask[splits['test']] = True

    if verbose:
        print(f"✓ Graph loaded:")
        print(f"  Nodes: {num_nodes}")
        print(f"  Edges: {edge_index.size(1)}")
        print(f"  Features: {num_features}")
        print(f"  Classes: {num_classes}")
        print(f"  Train/Val/Test: {train_mask.sum()}/{val_mask.sum()}/{test_mask.sum()}")
        print()

    # Compute class weights
    class_weights = compute_class_weights(y[train_mask], num_classes).to(device)

    # Create model
    if verbose:
        print("Creating model...")

    model = create_model(
        num_features=num_features,
        num_classes=num_classes,
        model_type=model_type,
        hidden_dim=hidden_dim,
        num_layers=num_layers,
        device=device
    )

    if verbose:
        print(get_model_summary(model))

    # Optimizer and scheduler
    optimizer = Adam(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay
    )

    scheduler = ReduceLROnPlateau(
        optimizer,
        mode='max',
        factor=0.5,
        patience=20,
        verbose=verbose
    )

    # Training loop
    if verbose:
        print(f"Training for up to {num_epochs} epochs...")
        print()

    best_val_acc = 0.0
    best_epoch = 0
    patience_counter = 0

    history = {
        'train_loss': [],
        'train_acc': [],
        'val_acc': [],
        'val_loss': [],
        'test_acc': [],
        'lr': []
    }

    os.makedirs(output_dir, exist_ok=True)

    start_time = time.time()

    for epoch in range(num_epochs):
        # Train
        train_loss = train_epoch(
            model, optimizer, x, edge_index, y, train_mask, class_weights
        )

        # Evaluate
        train_metrics = evaluate(model, x, edge_index, y, train_mask)
        val_metrics = evaluate(model, x, edge_index, y, val_mask)
        test_metrics = evaluate(model, x, edge_index, y, test_mask)

        # Record
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_metrics['accuracy'])
        history['val_acc'].append(val_metrics['accuracy'])
        history['val_loss'].append(val_metrics['loss'])
        history['test_acc'].append(test_metrics['accuracy'])
        history['lr'].append(optimizer.param_groups[0]['lr'])

        # Learning rate scheduling
        scheduler.step(val_metrics['accuracy'])

        # Early stopping
        if val_metrics['accuracy'] > best_val_acc:
            best_val_acc = val_metrics['accuracy']
            best_epoch = epoch
            patience_counter = 0

            # Save best model
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_metrics['accuracy'],
                'val_loss': val_metrics['loss'],
                'metadata': metadata
            }, f'{output_dir}/best_model.pt')

        else:
            patience_counter += 1

        # Print progress
        if verbose and (epoch % 10 == 0 or epoch == num_epochs - 1):
            elapsed = time.time() - start_time
            print(
                f"Epoch {epoch:3d} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Train Acc: {train_metrics['accuracy']:.4f} | "
                f"Val Acc: {val_metrics['accuracy']:.4f} | "
                f"Test Acc: {test_metrics['accuracy']:.4f} | "
                f"Best: {best_val_acc:.4f} | "
                f"Time: {elapsed:.1f}s"
            )

        # Early stopping
        if patience_counter >= patience:
            if verbose:
                print(f"\nEarly stopping at epoch {epoch}")
            break

    if verbose:
        print(f"\n✓ Training complete!")
        print(f"  Best epoch: {best_epoch}")
        print(f"  Best val accuracy: {best_val_acc:.4f}")
        print(f"  Final test accuracy: {history['test_acc'][best_epoch]:.4f}")
        print(f"  Training time: {time.time() - start_time:.1f}s")

    # Save history
    with open(f'{output_dir}/training_history.json', 'w') as f:
        json.dump(history, f, indent=2)

    results = {
        'best_val_acc': best_val_acc,
        'best_epoch': best_epoch,
        'final_test_acc': history['test_acc'][best_epoch],
        'num_epochs': epoch + 1,
        'training_time': time.time() - start_time
    }

    return results


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Train PyTorch Geometric GNN')
    parser.add_argument('--model', type=str, default='gat', choices=['gat', 'gcn'])
    parser.add_argument('--hidden-dim', type=int, default=256)
    parser.add_argument('--num-layers', type=int, default=3)
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--epochs', type=int, default=500)
    parser.add_argument('--patience', type=int, default=50)
    parser.add_argument('--device', type=str, default=None)

    args = parser.parse_args()

    if not TORCH_AVAILABLE or not MODEL_AVAILABLE:
        print("\n✗ PyTorch or PyTorch Geometric not available")
        print("\nInstall with:")
        print("  pip install torch")
        print("  pip install torch-geometric")
        print("\n⚠️  Training infrastructure is ready")
        print("   Run this script after installing dependencies")
        exit(1)

    # Train
    results = train(
        model_type=args.model,
        hidden_dim=args.hidden_dim,
        num_layers=args.num_layers,
        learning_rate=args.lr,
        num_epochs=args.epochs,
        patience=args.patience,
        device=args.device
    )

    # Print final results
    print("\n=== FINAL RESULTS ===")
    print(f"Model: {args.model.upper()}")
    print(f"Best validation accuracy: {results['best_val_acc']:.2%}")
    print(f"Test accuracy: {results['final_test_acc']:.2%}")
    print(f"Training time: {results['training_time']:.1f}s")

    if results['best_val_acc'] >= 0.85:
        print("\n✓ Target accuracy (≥85%) achieved!")
    else:
        print(f"\n⚠️  Current accuracy: {results['best_val_acc']:.2%}")
        print("   For higher accuracy:")
        print("   - Train on GPU (--device cuda)")
        print("   - Increase epochs (--epochs 1000)")
        print("   - Try different hyperparameters")
