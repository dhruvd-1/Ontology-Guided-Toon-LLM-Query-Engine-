"""
Ontology Reasoner

Uses ontology to resolve concepts and expand queries semantically.
"""

from typing import List, Dict, Set
from ontology import Ontology


class OntologyReasoner:
    """Reasons about ontology to expand and resolve queries"""

    def __init__(self, ontology: Ontology):
        self.ontology = ontology

    def expand_concept(self, concept: str) -> List[str]:
        """
        Expand a concept to include related concepts

        Args:
            concept: Class or property name

        Returns:
            List of related concepts (subclasses, related properties, etc.)
        """
        expanded = [concept]

        # If it's a class, include subclasses
        if concept in self.ontology.classes:
            subclasses = self.ontology.get_all_descendants(concept)
            expanded.extend(subclasses)

        # Include related concepts from relationships
        relationships = self.ontology.get_relationships_for_class(concept)
        for rel in relationships:
            if rel.target not in expanded:
                expanded.append(rel.target)

        return expanded

    def find_path_between_classes(self, source: str, target: str) -> List[str]:
        """
        Find path between two classes through relationships

        Returns:
            List of classes in the path from source to target
        """
        # Simple BFS to find path
        visited = set()
        queue = [(source, [source])]

        while queue:
            current, path = queue.pop(0)

            if current == target:
                return path

            if current in visited:
                continue

            visited.add(current)

            # Get related classes
            rels = self.ontology.get_relationships_for_class(current)
            for rel in rels:
                next_class = rel.target if rel.source == current else rel.source
                if next_class not in visited:
                    queue.append((next_class, path + [next_class]))

        return []  # No path found

    def get_join_path(self, classes: List[str]) -> List[Dict]:
        """
        Get join path for multiple classes

        Returns:
            List of join specifications
        """
        if len(classes) < 2:
            return []

        joins = []

        # Find paths between consecutive classes
        for i in range(len(classes) - 1):
            source = classes[i]
            target = classes[i + 1]

            # Find relationship
            rels = self.ontology.get_relationships_for_class(source)
            for rel in rels:
                if rel.target == target or rel.source == target:
                    joins.append({
                        'source': source,
                        'target': target,
                        'relationship': rel.name,
                        'cardinality': rel.cardinality
                    })
                    break

        return joins

    def resolve_property_to_class(self, property_name: str) -> List[str]:
        """
        Find which classes have this property

        Returns:
            List of class names that have this property
        """
        classes = []

        for class_name, cls in self.ontology.classes.items():
            all_props = self.ontology.get_properties_by_class(class_name, include_inherited=True)
            if property_name in all_props:
                classes.append(class_name)

        return classes

    def semantic_similarity(self, concept1: str, concept2: str) -> float:
        """
        Compute semantic similarity between two concepts (simple version)

        Returns:
            Similarity score between 0 and 1
        """
        # Simple similarity based on hierarchy and relationships

        # Same concept
        if concept1 == concept2:
            return 1.0

        # Check if they're in same hierarchy
        if concept1 in self.ontology.classes and concept2 in self.ontology.classes:
            hierarchy1 = self.ontology.get_class_hierarchy(concept1)
            hierarchy2 = self.ontology.get_class_hierarchy(concept2)

            # Common ancestors
            common = set(hierarchy1) & set(hierarchy2)
            if common:
                # Similarity based on how close they are
                return 0.7

            # Check if one is subclass of other
            if self.ontology.is_subclass_of(concept1, concept2):
                return 0.8
            if self.ontology.is_subclass_of(concept2, concept1):
                return 0.8

        # Check if they're related through relationships
        rels1 = self.ontology.get_relationships_for_class(concept1)
        rels2 = self.ontology.get_relationships_for_class(concept2)

        related = False
        for rel in rels1:
            if rel.target == concept2 or rel.source == concept2:
                related = True
                break

        if related:
            return 0.6

        # No relationship found
        return 0.0


if __name__ == '__main__':
    from ontology import get_ontology

    print("=== Ontology Reasoner Test ===\n")

    ontology = get_ontology()
    reasoner = OntologyReasoner(ontology)

    # Test concept expansion
    print("Concept expansion for 'Electronics':")
    expanded = reasoner.expand_concept('Electronics')
    print(f"  {expanded}\n")

    # Test path finding
    print("Path from Customer to Product:")
    path = reasoner.find_path_between_classes('Customer', 'Product')
    print(f"  {' -> '.join(path)}\n")

    # Test property resolution
    print("Classes with 'email' property:")
    classes = reasoner.resolve_property_to_class('email')
    print(f"  {classes}\n")

    # Test semantic similarity
    print("Semantic similarity:")
    print(f"  Customer <-> Order: {reasoner.semantic_similarity('Customer', 'Order'):.2f}")
    print(f"  Product <-> Category: {reasoner.semantic_similarity('Product', 'Category'):.2f}")
    print(f"  Customer <-> Shipment: {reasoner.semantic_similarity('Customer', 'Shipment'):.2f}")

    print("\n✓ Ontology reasoner working!")
