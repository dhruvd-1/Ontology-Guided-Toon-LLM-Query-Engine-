"""
Build schema graph from balanced dataset
"""

import json
import numpy as np
import os
from gnn.graph_builder_simple import SimpleSchemaGraphBuilder


def build_graph_from_balanced_dataset():
    """Build graph from new balanced dataset"""
    print("=== Building Graph from Balanced Dataset ===\n")

    # Load balanced ground truth
    with open('data_generation/balanced_output/ground_truth.json', 'r') as f:
        ground_truth = json.load(f)

    print(f"Loaded {len(ground_truth['field_mappings'])} field mappings")
    print(f"Properties: {ground_truth['metadata']['num_properties']}")

    # Convert to format expected by graph builder
    # Group by tables
    tables = {}
    for mapping in ground_truth['field_mappings']:
        table_name = mapping['table_name']
        if table_name not in tables:
            tables[table_name] = {
                'table_name': table_name,
                'ontology_class': mapping['ontology_class'],
                'fields': []
            }
        tables[table_name]['fields'].append(mapping)

    # Create ground truth structure
    gt_formatted = {
        'tables': tables,
        'field_mappings': ground_truth['field_mappings']
    }

    # Build graph
    builder = SimpleSchemaGraphBuilder()
    graph = builder.build_graph(gt_formatted)

    # Save graph
    output_dir = 'gnn/balanced_output'
    os.makedirs(output_dir, exist_ok=True)

    graph_path = f'{output_dir}/schema_graph.npz'
    meta_path = f'{output_dir}/schema_graph_meta.json'

    # Save numpy arrays
    np.savez(
        graph_path,
        x=graph['x'],
        edge_index=graph['edge_index'],
        y=graph['y'],
        num_nodes=np.array([graph['num_nodes']]),
        num_edges=np.array([graph['num_edges']]),
        num_features=np.array([graph['num_features']]),
        num_classes=np.array([graph['num_classes']])
    )
    print(f"✓ Graph saved to {graph_path}")

    # Save metadata
    metadata = {
        'property_to_id': graph['property_to_id'],
        'id_to_property': graph['id_to_property'],
        'node_info': [
            {
                'node_id': n.node_id,
                'field_name': n.field_name,
                'table_name': n.table_name,
                'ontology_property': n.ontology_property
            }
            for n in graph['nodes']
        ]
    }

    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved to {meta_path}")

    # Print statistics
    print(f"\n=== Graph Statistics ===")
    print(f"Nodes: {graph['num_nodes']}")
    print(f"Edges: {graph['num_edges']}")
    print(f"Features: {graph['num_features']}")
    print(f"Classes: {graph['num_classes']}")
    print(f"Avg degree: {graph['num_edges'] / graph['num_nodes']:.2f}")

    # Class distribution
    unique, counts = np.unique(graph['y'], return_counts=True)
    print(f"\nClass distribution:")
    print(f"  Min samples: {counts.min()}")
    print(f"  Max samples: {counts.max()}")
    print(f"  Mean samples: {counts.mean():.1f}")
    print(f"  Imbalance: {counts.max() / counts.min():.2f}:1")

    return graph


if __name__ == '__main__':
    graph = build_graph_from_balanced_dataset()
    print("\n✓ Graph construction complete!")
