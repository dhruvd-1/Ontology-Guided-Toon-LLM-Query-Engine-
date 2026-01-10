"""
Schema Graph Builder for GNN

Builds a graph representation of database schemas where:
- Nodes = database fields
- Edges = relationships (same table, foreign key, co-occurrence)
- Node features = name embeddings + data type + table context
"""

import json
import numpy as np
import torch
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
import re
from sklearn.preprocessing import LabelEncoder


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
    edge_type: str  # 'same_table', 'foreign_key', 'co_occurrence', 'similar_name'


class SchemaGraphBuilder:
    """Builds graph from schema and ground truth"""

    def __init__(self, use_simple_embeddings: bool = True):
        """
        Args:
            use_simple_embeddings: If True, use simple character-based embeddings.
                                  If False, use sentence transformers (requires model download)
        """
        self.use_simple_embeddings = use_simple_embeddings
        self.embedding_model = None
        self.datatype_encoder = LabelEncoder()

        # Common SQL datatypes for encoding
        self.common_datatypes = [
            'VARCHAR', 'TEXT', 'INT', 'INTEGER', 'BIGINT', 'SMALLINT',
            'DECIMAL', 'NUMERIC', 'FLOAT', 'DOUBLE', 'BOOLEAN', 'BOOL',
            'BIT', 'TINYINT', 'DATE', 'DATETIME', 'TIMESTAMP', 'CHAR',
            'LONGTEXT', 'CLOB'
        ]
        self.datatype_encoder.fit(self.common_datatypes)

    def _init_embedding_model(self):
        """Initialize sentence transformer model for embeddings"""
        if not self.use_simple_embeddings and self.embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ Loaded sentence transformer model")
            except Exception as e:
                print(f"Warning: Could not load sentence transformer: {e}")
                print("Falling back to simple embeddings")
                self.use_simple_embeddings = True

    def _simple_text_embedding(self, text: str, embedding_dim: int = 64) -> np.ndarray:
        """
        Generate a simple text embedding based on character features.
        This is a lightweight alternative to sentence transformers.
        """
        text = text.lower()

        # Character-level features
        features = []

        # Length features
        features.append(min(len(text) / 50.0, 1.0))  # Normalized length
        features.append(float(text.count('_')) / max(len(text), 1))  # Underscore ratio
        features.append(float(text.count('-')) / max(len(text), 1))  # Dash ratio

        # Character type features
        features.append(float(sum(c.isalpha() for c in text)) / max(len(text), 1))
        features.append(float(sum(c.isdigit() for c in text)) / max(len(text), 1))
        features.append(float(sum(c.isupper() for c in text)) / max(len(text), 1))

        # Common abbreviation patterns (for messy field names)
        abbreviations = ['id', 'no', 'num', 'dt', 'nm', 'val', 'amt', 'qty', 'desc', 'stat']
        for abbr in abbreviations:
            features.append(float(abbr in text))

        # Character n-grams (simple hash-based)
        for n in [2, 3]:
            if len(text) >= n:
                ngrams = [text[i:i+n] for i in range(len(text)-n+1)]
                # Simple hash features
                for i in range(10):
                    features.append(float(any(hash(ng) % 10 == i for ng in ngrams)))

        # Pad or truncate to embedding_dim
        features = features[:embedding_dim]
        if len(features) < embedding_dim:
            features.extend([0.0] * (embedding_dim - len(features)))

        return np.array(features, dtype=np.float32)

    def _get_text_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text (field name)"""
        if self.use_simple_embeddings:
            return self._simple_text_embedding(text)
        else:
            if self.embedding_model is None:
                self._init_embedding_model()

            if self.embedding_model:
                return self.embedding_model.encode(text, convert_to_numpy=True)
            else:
                return self._simple_text_embedding(text)

    def _encode_datatype(self, datatype: str) -> np.ndarray:
        """Encode SQL datatype as one-hot vector"""
        # Extract base datatype (e.g., VARCHAR(255) -> VARCHAR)
        base_type = re.match(r'([A-Z]+)', datatype.upper())
        if base_type:
            base_type = base_type.group(1)
        else:
            base_type = 'VARCHAR'

        try:
            idx = self.datatype_encoder.transform([base_type])[0]
        except:
            # Unknown datatype, use first category
            idx = 0

        # One-hot encoding
        one_hot = np.zeros(len(self.common_datatypes), dtype=np.float32)
        one_hot[idx] = 1.0
        return one_hot

    def _encode_table_context(self, table_name: str, num_tables: int, table_idx: int) -> np.ndarray:
        """Encode table context as features"""
        # Simple table index encoding
        features = np.zeros(10, dtype=np.float32)  # Fixed size context vector

        # Normalized table position
        features[0] = table_idx / max(num_tables, 1)

        # Table name length
        features[1] = min(len(table_name) / 30.0, 1.0)

        # Table name patterns
        features[2] = float('_tbl' in table_name or '_table' in table_name)
        features[3] = float(table_name.endswith('s'))  # Plural
        features[4] = float('_data' in table_name)

        return features

    def build_nodes_and_features(self, ground_truth: Dict) -> Tuple[List[SchemaNode], torch.Tensor]:
        """
        Build nodes and node feature matrix from ground truth mapping

        Returns:
            nodes: List of SchemaNode objects
            features: Tensor of shape [num_nodes, feature_dim]
        """
        nodes = []
        node_features = []

        field_mappings = ground_truth.get('field_mappings', [])
        tables = ground_truth.get('tables', {})
        table_names = list(tables.keys())

        for node_id, mapping in enumerate(field_mappings):
            # Create node
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

            # Build node features
            # 1. Field name embedding
            name_embedding = self._get_text_embedding(mapping['field_name'])

            # 2. Datatype encoding
            datatype_encoding = self._encode_datatype(mapping['data_type'])

            # 3. Table context
            table_idx = table_names.index(mapping['table_name']) if mapping['table_name'] in table_names else 0
            table_context = self._encode_table_context(mapping['table_name'], len(table_names), table_idx)

            # 4. Boolean features
            boolean_features = np.array([
                float(mapping.get('is_primary_key', False)),
                float(mapping.get('is_nullable', True))
            ], dtype=np.float32)

            # Concatenate all features
            node_feature = np.concatenate([
                name_embedding,
                datatype_encoding,
                table_context,
                boolean_features
            ])

            node_features.append(node_feature)

        # Convert to tensor
        features_tensor = torch.tensor(np.array(node_features), dtype=torch.float32)

        return nodes, features_tensor

    def build_edges(self, nodes: List[SchemaNode]) -> Tuple[torch.Tensor, List[str]]:
        """
        Build edges between nodes based on relationships

        Returns:
            edge_index: Tensor of shape [2, num_edges] (source, target pairs)
            edge_types: List of edge type names
        """
        edges = []

        # Build node lookup by table
        table_to_nodes = {}
        for node in nodes:
            if node.table_name not in table_to_nodes:
                table_to_nodes[node.table_name] = []
            table_to_nodes[node.table_name].append(node)

        # 1. Same table edges (all fields in same table are connected)
        for table_name, table_nodes in table_to_nodes.items():
            for i, node1 in enumerate(table_nodes):
                for node2 in table_nodes[i+1:]:
                    edges.append(SchemaEdge(node1.node_id, node2.node_id, 'same_table'))
                    edges.append(SchemaEdge(node2.node_id, node1.node_id, 'same_table'))  # Undirected

        # 2. Foreign key edges (fields with 'id' in name that reference other tables)
        for node in nodes:
            if 'id' in node.field_name.lower() and not node.is_primary_key:
                # Find potential foreign key references
                for other_table, other_nodes in table_to_nodes.items():
                    if other_table != node.table_name:
                        for other_node in other_nodes:
                            if other_node.is_primary_key:
                                # Potential foreign key relationship
                                edges.append(SchemaEdge(node.node_id, other_node.node_id, 'foreign_key'))

        # 3. Similar name edges (fields with similar names across tables)
        for i, node1 in enumerate(nodes):
            for node2 in nodes[i+1:]:
                if node1.table_name != node2.table_name:
                    # Check name similarity
                    name1 = node1.field_name.lower().replace('_', '')
                    name2 = node2.field_name.lower().replace('_', '')

                    if name1 == name2 or node1.ontology_property == node2.ontology_property:
                        edges.append(SchemaEdge(node1.node_id, node2.node_id, 'similar_name'))
                        edges.append(SchemaEdge(node2.node_id, node1.node_id, 'similar_name'))

        # Convert to PyTorch Geometric format
        if edges:
            edge_index = torch.tensor(
                [[e.source, e.target] for e in edges],
                dtype=torch.long
            ).t()
            edge_types = [e.edge_type for e in edges]
        else:
            edge_index = torch.empty((2, 0), dtype=torch.long)
            edge_types = []

        return edge_index, edge_types

    def build_graph(self, ground_truth: Dict) -> Dict:
        """
        Build complete schema graph

        Returns:
            graph: Dictionary containing nodes, features, edges, and labels
        """
        print("Building schema graph...")

        # Build nodes and features
        nodes, node_features = self.build_nodes_and_features(ground_truth)
        print(f"  ✓ Created {len(nodes)} nodes with {node_features.shape[1]} features each")

        # Build edges
        edge_index, edge_types = self.build_edges(nodes)
        print(f"  ✓ Created {edge_index.shape[1]} edges")

        # Create labels (ontology property IDs)
        ontology_properties = list(set(node.ontology_property for node in nodes))
        ontology_properties.sort()  # Consistent ordering
        property_to_id = {prop: idx for idx, prop in enumerate(ontology_properties)}

        labels = torch.tensor(
            [property_to_id[node.ontology_property] for node in nodes],
            dtype=torch.long
        )

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
    """Load ground truth mapping from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_graph(graph: Dict, filepath: str = 'gnn/output/schema_graph.pt'):
    """Save graph to file"""
    import os
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Convert non-serializable objects
    save_dict = {
        'x': graph['x'],
        'edge_index': graph['edge_index'],
        'y': graph['y'],
        'num_nodes': graph['num_nodes'],
        'num_edges': graph['num_edges'],
        'num_features': graph['num_features'],
        'num_classes': graph['num_classes'],
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

    torch.save(save_dict, filepath)
    print(f"✓ Graph saved to {filepath}")


if __name__ == '__main__':
    print("=== Schema Graph Construction ===\n")

    # Load ground truth
    print("Loading ground truth mapping...")
    ground_truth = load_ground_truth()

    # Build graph
    builder = SchemaGraphBuilder(use_simple_embeddings=True)
    graph = builder.build_graph(ground_truth)

    # Save graph
    save_graph(graph)

    print("\n✓ Graph construction complete!")
