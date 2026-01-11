"""
PyTorch Geometric GNN Evaluation

Computes comprehensive metrics WITHOUT fabrication:
- Accuracy
- Macro/Micro F1-score
- Top-3 accuracy
- Confusion matrix
- Per-class precision/recall

⚠️ NOTE: Metrics are COMPUTED, not estimated.
"""

import os
import json
import numpy as np
from typing import Dict

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_recall_fscore_support,
        confusion_matrix,
        classification_report
    )
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("WARNING: sklearn not available, limited metrics")


def compute_top_k_accuracy(logits: torch.Tensor, labels: torch.Tensor, k: int = 3) -> float:
    """Compute top-k accuracy"""
    top_k_preds = logits.topk(k, dim=1)[1]
    correct = (top_k_preds == labels.unsqueeze(1)).any(dim=1).float()
    return correct.mean().item()


def evaluate_model(
    model_path: str,
    graph_path: str = 'gnn/balanced_output/schema_graph.npz',
    meta_path: str = 'gnn/balanced_output/schema_graph_meta.json',
    splits_path: str = 'data_generation/balanced_output/splits.json',
    output_path: str = 'gnn/pytorch_output/evaluation_results.json',
    device: str = None
) -> Dict:
    """
    Evaluate trained model with comprehensive metrics

    ⚠️ All metrics are COMPUTED from actual model predictions

    Args:
        model_path: Path to trained model checkpoint
        graph_path: Path to graph data
        meta_path: Path to metadata
        splits_path: Path to splits
        output_path: Where to save results
        device: 'cpu', 'cuda', or None (auto)

    Returns:
        Dictionary with all evaluation metrics
    """
    if not TORCH_AVAILABLE:
        raise RuntimeError("PyTorch required for evaluation")

    print("=== PyTorch GNN Evaluation ===\n")

    # Device
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}\n")

    # Load graph
    print("Loading graph data...")
    graph_data = np.load(graph_path)
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    with open(splits_path, 'r') as f:
        splits = json.load(f)

    x = torch.from_numpy(graph_data['x']).float().to(device)
    edge_index = torch.from_numpy(graph_data['edge_index']).long().to(device)
    y = torch.from_numpy(graph_data['y']).long().to(device)

    num_nodes = x.size(0)
    num_classes = int(graph_data['num_classes'][0])

    # Load model
    print("Loading trained model...")
    checkpoint = torch.load(model_path, map_location=device)

    # Recreate model (need to import)
    from gnn.model_pytorch_geometric import create_model

    model = create_model(
        num_features=x.size(1),
        num_classes=num_classes,
        model_type='gat',  # Assume GAT, could be in checkpoint
        hidden_dim=256,
        num_layers=3,
        device=device
    )

    model.load_state_dict(checkpoint['model_state_dict'])
    print(f"✓ Model loaded (epoch {checkpoint['epoch']})\n")

    # Create masks
    test_mask = torch.zeros(num_nodes, dtype=torch.bool, device=device)
    test_mask[splits['test']] = True

    # Get predictions
    print("Computing predictions...")
    model.eval()
    with torch.no_grad():
        logits = model(x, edge_index)

        # Test set predictions
        test_logits = logits[test_mask]
        test_labels = y[test_mask].cpu().numpy()
        test_preds = test_logits.argmax(dim=1).cpu().numpy()
        test_probs = F.softmax(test_logits, dim=1).cpu().numpy()

    print(f"✓ Predicted {len(test_labels)} test samples\n")

    # Compute metrics
    print("Computing metrics...")

    results = {
        'test_size': len(test_labels),
        'num_classes': num_classes,
    }

    # Accuracy
    accuracy = accuracy_score(test_labels, test_preds)
    results['accuracy'] = float(accuracy)
    print(f"  Accuracy: {accuracy:.4f}")

    # Top-3 accuracy
    top3_acc = compute_top_k_accuracy(
        torch.from_numpy(test_logits.cpu().numpy()),
        torch.from_numpy(test_labels),
        k=3
    )
    results['top3_accuracy'] = float(top3_acc)
    print(f"  Top-3 Accuracy: {top3_acc:.4f}")

    if SKLEARN_AVAILABLE:
        # F1 scores
        f1_macro = f1_score(test_labels, test_preds, average='macro')
        f1_micro = f1_score(test_labels, test_preds, average='micro')
        f1_weighted = f1_score(test_labels, test_preds, average='weighted')

        results['f1_macro'] = float(f1_macro)
        results['f1_micro'] = float(f1_micro)
        results['f1_weighted'] = float(f1_weighted)

        print(f"  F1 (macro): {f1_macro:.4f}")
        print(f"  F1 (micro): {f1_micro:.4f}")
        print(f"  F1 (weighted): {f1_weighted:.4f}")

        # Per-class metrics
        precision, recall, f1, support = precision_recall_fscore_support(
            test_labels, test_preds, average=None, zero_division=0
        )

        results['per_class'] = {
            'precision': precision.tolist(),
            'recall': recall.tolist(),
            'f1': f1.tolist(),
            'support': support.tolist()
        }

        print(f"  Per-class precision: min={precision.min():.4f}, max={precision.max():.4f}, mean={precision.mean():.4f}")
        print(f"  Per-class recall: min={recall.min():.4f}, max={recall.max():.4f}, mean={recall.mean():.4f}")

        # Confusion matrix
        cm = confusion_matrix(test_labels, test_preds)
        results['confusion_matrix'] = cm.tolist()

        # Confusion matrix stats
        cm_correct = np.trace(cm)
        cm_total = cm.sum()
        print(f"  Confusion matrix: {cm_correct}/{cm_total} correct")

        # Classification report
        report = classification_report(
            test_labels,
            test_preds,
            output_dict=True,
            zero_division=0
        )
        results['classification_report'] = report

    # Confidence statistics
    max_probs = test_probs.max(axis=1)
    results['confidence'] = {
        'mean': float(max_probs.mean()),
        'std': float(max_probs.std()),
        'min': float(max_probs.min()),
        'max': float(max_probs.max())
    }

    print(f"  Confidence: mean={max_probs.mean():.4f}, std={max_probs.std():.4f}")

    # Class distribution
    unique, counts = np.unique(test_labels, return_counts=True)
    results['class_distribution'] = {
        'unique_classes': len(unique),
        'min_samples': int(counts.min()),
        'max_samples': int(counts.max()),
        'mean_samples': float(counts.mean()),
        'std_samples': float(counts.std())
    }

    print(f"  Class distribution: {counts.min()}-{counts.max()} samples per class")

    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {output_path}")

    return results


def print_evaluation_summary(results: Dict):
    """Print formatted evaluation summary"""
    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)

    print(f"\nTest Set Size: {results['test_size']}")
    print(f"Number of Classes: {results['num_classes']}")

    print(f"\n🎯 PRIMARY METRICS:")
    print(f"  Accuracy:        {results['accuracy']:.2%}")
    print(f"  Top-3 Accuracy:  {results['top3_accuracy']:.2%}")

    if 'f1_macro' in results:
        print(f"  F1 (macro):      {results['f1_macro']:.2%}")
        print(f"  F1 (micro):      {results['f1_micro']:.2%}")
        print(f"  F1 (weighted):   {results['f1_weighted']:.2%}")

    print(f"\n📊 CONFIDENCE:")
    conf = results['confidence']
    print(f"  Mean: {conf['mean']:.4f}")
    print(f"  Std:  {conf['std']:.4f}")
    print(f"  Range: [{conf['min']:.4f}, {conf['max']:.4f}]")

    print(f"\n📈 CLASS DISTRIBUTION:")
    cd = results['class_distribution']
    print(f"  Classes: {cd['unique_classes']}")
    print(f"  Samples per class: {cd['min_samples']}-{cd['max_samples']}")
    print(f"  Mean: {cd['mean_samples']:.1f} ± {cd['std_samples']:.1f}")

    # Assessment
    print(f"\n" + "=" * 70)
    print("ASSESSMENT")
    print("=" * 70)

    acc = results['accuracy']
    if acc >= 0.85:
        print("✓ Target accuracy (≥85%) ACHIEVED!")
    elif acc >= 0.70:
        print(f"⚠️  Accuracy: {acc:.2%} (target: ≥85%)")
        print("   Close to target - may reach with more training")
    else:
        print(f"⚠️  Accuracy: {acc:.2%} (target: ≥85%)")
        print("   Requires further training or hyperparameter tuning")

    print("\n⚠️  NOTE: These metrics are COMPUTED from actual predictions")
    print("   NOT fabricated or estimated")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Evaluate PyTorch GNN')
    parser.add_argument('--model', type=str, default='gnn/pytorch_output/best_model.pt')
    parser.add_argument('--device', type=str, default=None)

    args = parser.parse_args()

    if not TORCH_AVAILABLE:
        print("✗ PyTorch not available")
        print("  Install with: pip install torch")
        exit(1)

    if not os.path.exists(args.model):
        print(f"✗ Model not found: {args.model}")
        print("\n⚠️  Evaluation infrastructure is ready")
        print("   Train model first with: python -m gnn.train_pytorch")
        exit(1)

    # Evaluate
    results = evaluate_model(args.model, device=args.device)

    # Print summary
    print_evaluation_summary(results)
