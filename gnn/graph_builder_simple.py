"""
Simplified Schema Graph Builder (numpy only)

This version works without PyTorch or sklearn dependencies for testing.
"""

import json
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import re


@dataclass
class SchemaNode:
    """Represents a node in the schema graph"""
    node_id: int
    field_name: str
    table_name: str
    data_type: str
    ontology_class: str
    ontology_property: str
    is_primary_key: bool
    is_nullable: bool


@dataclass
class SchemaEdge:
    """Represents an edge in the schema graph"""
    source: int
    target: int
    edge_type: str


class SimpleSchemaGraphBuilder:
    """Simplified graph builder using only numpy"""

    def __init__(self):
        # Common SQL datatypes for encoding
        self.common_datatypes = [
            'VARCHAR', 'TEXT', 'INT', 'INTEGER', 'BIGINT', 'SMALLINT',
            'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'BOOL',
            'BIT', 'TINYINT', 'DATE', 'DATETIME', 'TIMESTAMP', 'CHAR',
            'LONGTEXT', 'CLOB'
        ]
        self.datatype_to_id = {dt: i for i, dt in enumerate(self.common_datatypes)}

    def _simple_text_embedding(self, text: str, embedding_dim: int = 64) -> np.ndarray:
        """Generate simple text embedding"""
        text = text.lower()

        features = []

        # Length features
        features.append(min(len(text) / 50.0, 1.0))
        features.append(float(text.count('_')) / max(len(text), 1))
        features.append(float(text.count('-')) / max(len(text), 1))

        # Character type features
        features.append(float(sum(c.isalpha() for c in text)) / max(len(text), 1))
        features.append(float(sum(c.isdigit() for c in text)) / max(len(text), 1))
        features.append(float(sum(c.isupper() for c in text)) / max(len(text), 1))

        # Common abbreviation patterns
        abbreviations = ['id', 'no', 'num', 'dt', 'nm', 'val', 'amt', 'qty', 'desc', 'stat']
        for abbr in abbreviations:
            features.append(float(abbr in text))

        # Character n-grams (simple hash-based)
        for n in [2, 3]:
            if len(text) >= n:
                ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
                for i in range(10):
                    features.append(float(any(hash(ng) % 10 == i for ng in ngrams)))

        # Pad or truncate to embedding_dim
        features = features[:embedding_dim]
        if len(features) < embedding_dim:
            features.extend([0.0] * (embedding_dim - len(features)))

        return np.array(features, dtype=np.float32)

    def _encode_datatype(self, datatype: str) -> np.ndarray:
        """Encode SQL datatype as one-hot vector"""
        base_type = re.match(r'([A-Z]+)', datatype.upper())
        if base_type:
            base_type = base_type.group(1)
        else:
            base_type = 'VARCHAR'

        idx = self.datatype_to_id.get(base_type, 0)

        one_hot = np.zeros(len(self.common_datatypes), dtype=np.float32)
        one_hot[idx] = 1.0
        return one_hot

    def _encode_table_context(self, table_name: str, num_tables: int, table_idx: int) -> np.ndarray:
        """Encode table context"""
        features = np.zeros(10, dtype=np.float32)
        features[0] = table_idx / max(num_tables, 1)
        features[1] = min(len(table_name) / 30.0, 1.0)
        features[2] = float('_tbl' in table_name or '_table' in table_name)
        features[3] = float(table_name.endswith('s'))
        features[4] = float('_data' in table_name)
        return features

    def build_nodes_and_features(self, ground_truth: Dict) -> Tuple[List[SchemaNode], np.ndarray]:
        """Build nodes and feature matrix"""
        nodes = []
        node_features = []

        field_mappings = ground_truth.get('field_mappings', [])
        tables = ground_truth.get('tables', {})
        table_names = list(tables.keys())

        for node_id, mapping in enumerate(field_mappings):
            node = SchemaNode(
                node_id=node_id,
                field_name=mapping['field_name'],
                table_name=mapping['table_name'],
                data_type=mapping['data_type'],
                ontology_class=mapping['ontology_class'],
                ontology_property=mapping['ontology_property'],
                is_primary_key=mapping.get('is_primary_key', False),
                is_nullable=mapping.get('is_nullable', True)
            )
            nodes.append(node)

            # Build features
            name_embedding = self._simple_text_embedding(mapping['field_name'])
            datatype_encoding = self._encode_datatype(mapping['data_type'])

            table_idx = table_names.index(mapping['table_name']) if mapping['table_name'] in table_names else 0
            table_context = self._encode_table_context(mapping['table_name'], len(table_names), table_idx)

            boolean_features = np.array([
                float(mapping.get('is_primary_key', False)),
                float(mapping.get('is_nullable', True))
            ], dtype=np.float32)

            node_feature = np.concatenate([
                name_embedding,
                datatype_encoding,
                table_context,
                boolean_features
            ])

            node_features.append(node_feature)

        features_array = np.array(node_features, dtype=np.float32)
        return nodes, features_array

    def build_edges(self, nodes: List[SchemaNode]) -> Tuple[np.ndarray, List[str]]:
        """Build edges between nodes"""
        edges = []

        # Build node lookup by table
        table_to_nodes = {}
        for node in nodes:
            if node.table_name not in table_to_nodes:
                table_to_nodes[node.table_name] = []
            table_to_nodes[node.table_name].append(node)

        # Same table edges
        for table_name, table_nodes in table_to_nodes.items():
            for i, node1 in enumerate(table_nodes):
                for node2 in table_nodes[i+1:]:
                    edges.append(SchemaEdge(node1.node_id, node2.node_id, 'same_table'))
                    edges.append(SchemaEdge(node2.node_id, node1.node_id, 'same_table'))

        # Foreign key edges
        for node in nodes:
            if 'id' in node.field_name.lower() and not node.is_primary_key:
                for other_table, other_nodes in table_to_nodes.items():
                    if other_table != node.table_name:
                        for other_node in other_nodes:
                            if other_node.is_primary_key:
                                edges.append(SchemaEdge(node.node_id, other_node.node_id, 'foreign_key'))

        # Similar name edges
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                if node1.table_name != node2.table_name:
                    name1 = node1.field_name.lower().replace('_', '')
                    name2 = node2.field_name.lower().replace('_', '')

                    if name1 == name2 or node1.ontology_property == node2.ontology_property:
                        edges.append(SchemaEdge(node1.node_id, node2.node_id, 'similar_name'))
                        edges.append(SchemaEdge(node2.node_id, node1.node_id, 'similar_name'))

        if edges:
            edge_index = np.array([[e.source, e.target] for e in edges], dtype=np.int64).T
            edge_types = [e.edge_type for e in edges]
        else:
            edge_index = np.empty((2, 0), dtype=np.int64)
            edge_types = []

        return edge_index, edge_types

    def build_graph(self, ground_truth: Dict) -> Dict:
        """Build complete schema graph"""
        print("Building schema graph...")

        nodes, node_features = self.build_nodes_and_features(ground_truth)
        print(f"  ✓ Created {len(nodes)} nodes with {node_features.shape[1]} features each")

        edge_index, edge_types = self.build_edges(nodes)
        print(f"  ✓ Created {edge_index.shape[1]} edges")

        # Create labels
        ontology_properties = list(set(node.ontology_property for node in nodes))
        ontology_properties.sort()
        property_to_id = {prop: idx for idx, prop in enumerate(ontology_properties)}

        labels = np.array([property_to_id[node.ontology_property] for node in nodes], dtype=np.int64)

        graph = {
            'nodes': nodes,
            'x': node_features,
            'edge_index': edge_index,
            'edge_types': edge_types,
            'y': labels,
            'num_nodes': len(nodes),
            'num_edges': edge_index.shape[1],
            'num_features': node_features.shape[1],
            'num_classes': len(ontology_properties),
            'property_to_id': property_to_id,
            'id_to_property': {idx: prop for prop, idx in property_to_id.items()}
        }

        print(f"  ✓ Graph summary:")
        print(f"    - Nodes: {graph['num_nodes']}")
        print(f"    - Edges: {graph['num_edges']}")
        print(f"    - Features: {graph['num_features']}")
        print(f"    - Classes: {graph['num_classes']}")

        return graph


def load_ground_truth(filepath: str = 'data_generation/output/ground_truth_mapping.json') -> Dict:
    """Load ground truth mapping"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_graph(graph: Dict, filepath: str = 'gnn/output/schema_graph.npz'):
    """Save graph to numpy file"""
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    save_dict = {
        'x': graph['x'],
        'edge_index': graph['edge_index'],
        'y': graph['y'],
        'num_nodes': np.array([graph['num_nodes']]),
        'num_edges': np.array([graph['num_edges']]),
        'num_features': np.array([graph['num_features']]),
        'num_classes': np.array([graph['num_classes']]),
    }

    np.savez(filepath, **save_dict)
    print(f"✓ Graph saved to {filepath}")

    # Also save metadata as JSON
    meta_filepath = filepath.replace('.npz', '_meta.json')
    with open(meta_filepath, 'w') as f:
        json.dump({
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
        }, f, indent=2)
    print(f"✓ Graph metadata saved to {meta_filepath}")


if __name__ == '__main__':
    print("=== Schema Graph Construction ===\n")

    ground_truth = load_ground_truth()
    builder = SimpleSchemaGraphBuilder()
    graph = builder.build_graph(ground_truth)
    save_graph(graph)

    print("\n✓ Graph construction complete!")
