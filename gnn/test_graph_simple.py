"""
Simple test for graph builder without torch dependency
"""

import json
import numpy as np
from gnn.graph_builder import SchemaGraphBuilder, load_ground_truth


def test_graph_building_numpy():
    """Test graph building with numpy only"""
    print("=== Testing Schema Graph Builder (numpy version) ===\n")

    # Load ground truth
    print("Loading ground truth mapping...")
    try:
        ground_truth = load_ground_truth()
        print(f"✓ Loaded {len(ground_truth['field_mappings'])} field mappings")
    except Exception as e:
        print(f"✗ Error loading ground truth: {e}")
        return False

    # Build graph
    print("\nBuilding graph...")
    try:
        builder = SchemaGraphBuilder(use_simple_embeddings=True)

        # Test node building
        nodes, node_features = builder.build_nodes_and_features(ground_truth)
        print(f"✓ Built {len(nodes)} nodes")
        print(f"✓ Node features shape: {node_features.shape if hasattr(node_features, 'shape') else len(node_features)}")

        # Check node features
        if hasattr(node_features, 'shape'):
            print(f"  Feature dimensions: {node_features.shape}")
        else:
            print(f"  Feature dimensions: ({len(node_features)}, {len(node_features[0]) if node_features else 0})")

        # Test edge building
        edge_index, edge_types = builder.build_edges(nodes)
        if hasattr(edge_index, 'shape'):
            print(f"✓ Built {edge_index.shape[1]} edges")
        else:
            print(f"✓ Built {len(edge_index[0]) if edge_index else 0} edges")

        print(f"  Edge types: {set(edge_types) if edge_types else 'none'}")

        # Sample nodes
        print("\nSample nodes:")
        for i in range(min(3, len(nodes))):
            node = nodes[i]
            print(f"  Node {i}: {node.field_name} ({node.table_name}) -> {node.ontology_property}")

        print("\n✓ Graph building test passed!")
        return True

    except Exception as e:
        print(f"✗ Error building graph: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = test_graph_building_numpy()
    sys.exit(0 if success else 1)
