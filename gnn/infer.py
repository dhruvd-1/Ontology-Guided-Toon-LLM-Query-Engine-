"""
GNN Inference Module

Load trained model and make predictions on new schemas.
"""

import numpy as np
import json
import pickle
from typing import Dict, List, Tuple
from gnn.model_numpy import GCNNumPy


class GNNInference:
    """Inference wrapper for trained GNN model"""

    def __init__(self, model_path: str = 'gnn/output/gnn_model.pkl'):
        """Load trained model"""
        self.model = GCNNumPy(
            num_features=96,  # Will be updated from checkpoint
            num_classes=61,
            hidden_dim=64,
            num_layers=2
        )

        self.metadata = self.model.load(model_path)
        self.property_to_id = self.metadata['property_to_id']
        self.id_to_property = self.metadata['id_to_property']

        print(f"✓ Model loaded (Epoch {self.metadata['epoch']}, Acc: {self.metadata['accuracy']:.2%})")

    def predict_mapping(
        self,
        x: np.ndarray,
        edge_index: np.ndarray,
        field_names: List[str]
    ) -> List[Dict]:
        """
        Predict ontology mappings for schema fields

        Args:
            x: Node features [num_nodes, num_features]
            edge_index: Edge indices [2, num_edges]
            field_names: List of field names

        Returns:
            List of predictions with confidence scores
        """
        # Get predictions
        predicted_classes, confidence_scores = self.model.predict(x, edge_index)

        # Convert to ontology properties
        predictions = []
        for i, (pred_class, conf) in enumerate(zip(predicted_classes, confidence_scores)):
            property_name = self.id_to_property.get(str(pred_class), 'unknown')

            predictions.append({
                'field_name': field_names[i] if i < len(field_names) else f'field_{i}',
                'predicted_property': property_name,
                'confidence': float(conf),
                'class_id': int(pred_class)
            })

        return predictions

    def predict_with_top_k(
        self,
        x: np.ndarray,
        edge_index: np.ndarray,
        field_names: List[str],
        top_k: int = 3
    ) -> List[Dict]:
        """
        Predict top-k ontology mappings for schema fields

        Returns:
            List of predictions with top-k candidates
        """
        # Forward pass
        logits = self.model.forward(x, edge_index, training=False)

        # Softmax
        probs = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = probs / np.sum(probs, axis=1, keepdims=True)

        # Get top-k predictions
        predictions = []
        for i in range(len(field_names)):
            # Get top k indices
            top_k_indices = np.argsort(probs[i])[-top_k:][::-1]
            top_k_probs = probs[i][top_k_indices]

            candidates = []
            for idx, prob in zip(top_k_indices, top_k_probs):
                candidates.append({
                    'property': self.id_to_property.get(str(idx), 'unknown'),
                    'confidence': float(prob)
                })

            predictions.append({
                'field_name': field_names[i] if i < len(field_names) else f'field_{i}',
                'top_k_predictions': candidates
            })

        return predictions


def run_inference_demo():
    """Demo inference on test graph"""
    print("=== GNN Inference Demo ===\n")

    # Load test graph
    print("Loading test data...")
    graph_data = np.load('gnn/output/schema_graph.npz')
    with open('gnn/output/schema_graph_meta.json', 'r') as f:
        metadata = json.load(f)

    x = graph_data['x']
    edge_index = graph_data['edge_index']
    y_true = graph_data['y']

    node_info = metadata['node_info']
    field_names = [n['field_name'] for n in node_info]

    print(f"✓ Loaded {len(field_names)} fields\n")

    # Create inference engine
    print("Loading model...")
    inferencer = GNNInference()

    # Make predictions
    print("\nMaking predictions...")
    predictions = inferencer.predict_mapping(x, edge_index, field_names)

    # Show samples
    print("\nSample predictions:")
    for i, pred in enumerate(predictions[:10]):
        true_prop = node_info[i]['ontology_property']
        match = "✓" if pred['predicted_property'] == true_prop else "✗"
        print(f"  {match} {pred['field_name']:20s} -> {pred['predicted_property']:20s} (conf: {pred['confidence']:.3f}) [true: {true_prop}]")

    # Compute accuracy
    correct = sum(1 for i, pred in enumerate(predictions) if pred['predicted_property'] == node_info[i]['ontology_property'])
    accuracy = correct / len(predictions)

    print(f"\nOverall accuracy: {accuracy:.2%} ({correct}/{len(predictions)})")

    # Top-k predictions
    print("\nTop-3 predictions for first 5 fields:")
    top_k_preds = inferencer.predict_with_top_k(x, edge_index, field_names, top_k=3)
    for i, pred in enumerate(top_k_preds[:5]):
        print(f"\n  {pred['field_name']}:")
        for j, cand in enumerate(pred['top_k_predictions']):
            print(f"    {j+1}. {cand['property']:20s} ({cand['confidence']:.3f})")

    return {
        'accuracy': accuracy,
        'num_correct': correct,
        'num_total': len(predictions)
    }


if __name__ == '__main__':
    results = run_inference_demo()
    print(f"\n✓ Inference complete: {results['accuracy']:.2%} accuracy")
