"""
Test suite for schema graph construction
"""

import numpy as np
import json
import sys


def test_graph_construction():
    """Test that graph was built correctly"""
    print("=== Graph Construction Validation ===\n")

    # Load graph
    print("Loading graph data...")
    try:
        graph = np.load('gnn/output/schema_graph.npz')
        with open('gnn/output/schema_graph_meta.json', 'r') as f:
            metadata = json.load(f)
    except Exception as e:
        print(f"✗ Error loading graph: {e}")
        return False

    # Validate basic structure
    print("Validating graph structure...")

    x = graph['x']  # Node features
    edge_index = graph['edge_index']  # Edges
    y = graph['y']  # Labels
    num_nodes = graph['num_nodes'][0]
    num_edges = graph['num_edges'][0]
    num_features = graph['num_features'][0]
    num_classes = graph['num_classes'][0]

    print(f"✓ Nodes: {num_nodes}")
    print(f"✓ Edges: {num_edges}")
    print(f"✓ Features per node: {num_features}")
    print(f"✓ Classes: {num_classes}")

    # Validate shapes
    assert x.shape[0] == num_nodes, f"Feature matrix should have {num_nodes} rows"
    assert x.shape[1] == num_features, f"Feature matrix should have {num_features} columns"
    print(f"✓ Feature matrix shape: {x.shape}")

    assert edge_index.shape[0] == 2, "Edge index should have 2 rows"
    assert edge_index.shape[1] == num_edges, f"Edge index should have {num_edges} edges"
    print(f"✓ Edge index shape: {edge_index.shape}")

    assert y.shape[0] == num_nodes, f"Label vector should have {num_nodes} elements"
    print(f"✓ Label vector shape: {y.shape}")

    # Validate edge indices are valid
    max_node_id = edge_index.max()
    assert max_node_id < num_nodes, f"Edge indices should be < {num_nodes}"
    print(f"✓ All edge indices valid (max: {max_node_id})")

    # Validate features are numeric
    assert np.isfinite(x).all(), "All features should be finite"
    print(f"✓ All features are finite")

    # Validate labels
    assert y.min() >= 0 and y.max() < num_classes, "Labels should be in range [0, num_classes)"
    print(f"✓ Labels in valid range: [{y.min()}, {y.max()}]")

    # Check class distribution
    unique_labels, counts = np.unique(y, return_counts=True)
    print(f"\nClass distribution:")
    print(f"  Unique classes: {len(unique_labels)}")
    print(f"  Min instances: {counts.min()}")
    print(f"  Max instances: {counts.max()}")
    print(f"  Mean instances: {counts.mean():.2f}")

    # Validate metadata
    print("\nValidating metadata...")
    property_to_id = metadata['property_to_id']
    id_to_property = metadata['id_to_property']
    node_info = metadata['node_info']

    assert len(node_info) == num_nodes, "Node info should match number of nodes"
    print(f"✓ Node info entries: {len(node_info)}")

    assert len(property_to_id) == num_classes, "Property mapping should match number of classes"
    print(f"✓ Property mappings: {len(property_to_id)}")

    # Sample nodes
    print("\nSample nodes:")
    for i in range(min(5, len(node_info))):
        node = node_info[i]
        print(f"  Node {i}: {node['field_name']} ({node['table_name']}) -> {node['ontology_property']}")

    # Validate feature statistics
    print("\nFeature statistics:")
    print(f"  Mean: {x.mean():.4f}")
    print(f"  Std: {x.std():.4f}")
    print(f"  Min: {x.min():.4f}")
    print(f"  Max: {x.max():.4f}")

    # Connectivity analysis
    print("\nConnectivity analysis:")
    nodes_with_edges = np.unique(edge_index).size
    print(f"  Nodes with edges: {nodes_with_edges}/{num_nodes} ({100*nodes_with_edges/num_nodes:.1f}%)")

    # Average degree
    degrees = np.bincount(edge_index.flatten(), minlength=num_nodes)
    print(f"  Average degree: {degrees.mean():.2f}")
    print(f"  Max degree: {degrees.max()}")
    print(f"  Min degree: {degrees.min()}")

    # Check requirements
    print("\n=== STEP 3 VALIDATION ===")
    assert num_nodes >= 50, "Should have at least 50 nodes"
    print("✓ Sufficient nodes")

    assert num_edges >= 100, "Should have at least 100 edges"
    print("✓ Sufficient edges")

    assert num_features >= 50, "Should have at least 50 features per node"
    print("✓ Sufficient features")

    assert nodes_with_edges == num_nodes or nodes_with_edges >= num_nodes * 0.9, "Most nodes should have edges"
    print("✓ Graph is well-connected")

    print("\n✓ Graph construction validation PASSED")
    return True


if __name__ == '__main__':
    try:
        success = test_graph_construction()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n✗ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
