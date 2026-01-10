"""
GNN module for schema-to-ontology mapping
"""

# Import will be conditional based on dependencies
try:
    from gnn.graph_builder import (
        SchemaGraphBuilder,
        SchemaNode,
        SchemaEdge,
        load_ground_truth,
        save_graph,
    )
    __all__ = [
        'SchemaGraphBuilder',
        'SchemaNode',
        'SchemaEdge',
        'load_ground_truth',
        'save_graph',
    ]
except ImportError as e:
    print(f"Warning: Could not import gnn.graph_builder: {e}")
    __all__ = []
