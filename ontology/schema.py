"""
Ontology Schema Loader and Manager

This module provides functionality to load, access, and work with the e-commerce ontology.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Property:
    """Represents an ontology property with its datatype and description"""
    name: str
    datatype: str
    description: str


@dataclass
class Constraint:
    """Represents a constraint on a class property"""
    property_name: str
    constraint_type: str
    constraint_value: Any


@dataclass
class OntologyClass:
    """Represents a class in the ontology"""
    name: str
    description: str
    parent: Optional[str]
    properties: List[str]
    constraints: Dict[str, Dict[str, Any]]

    def get_all_properties(self, ontology: 'Ontology') -> List[str]:
        """Get all properties including inherited ones from parent classes"""
        props = self.properties.copy()
        if self.parent:
            parent_class = ontology.get_class(self.parent)
            if parent_class:
                props.extend(parent_class.get_all_properties(ontology))
        return list(set(props))  # Remove duplicates


@dataclass
class Relationship:
    """Represents a relationship between two classes"""
    name: str
    source: str
    target: str
    cardinality: str
    description: str
    through: Optional[str] = None


@dataclass
class Ontology:
    """Main ontology container"""
    metadata: Dict[str, str]
    classes: Dict[str, OntologyClass]
    relationships: List[Relationship]
    properties: Dict[str, Property]

    def get_class(self, class_name: str) -> Optional[OntologyClass]:
        """Get a class by name"""
        return self.classes.get(class_name)

    def get_property(self, property_name: str) -> Optional[Property]:
        """Get a property by name"""
        return self.properties.get(property_name)

    def get_relationships_for_class(self, class_name: str) -> List[Relationship]:
        """Get all relationships where class is source or target"""
        return [
            rel for rel in self.relationships
            if rel.source == class_name or rel.target == class_name
        ]

    def get_class_hierarchy(self, class_name: str) -> List[str]:
        """Get the full hierarchy for a class (from root to class)"""
        hierarchy = [class_name]
        current_class = self.get_class(class_name)

        while current_class and current_class.parent:
            hierarchy.insert(0, current_class.parent)
            current_class = self.get_class(current_class.parent)

        return hierarchy

    def get_subclasses(self, class_name: str) -> List[str]:
        """Get all direct subclasses of a class"""
        return [
            name for name, cls in self.classes.items()
            if cls.parent == class_name
        ]

    def get_all_descendants(self, class_name: str) -> List[str]:
        """Get all descendants (recursive subclasses) of a class"""
        descendants = []
        direct_children = self.get_subclasses(class_name)

        for child in direct_children:
            descendants.append(child)
            descendants.extend(self.get_all_descendants(child))

        return descendants

    def is_subclass_of(self, child_class: str, parent_class: str) -> bool:
        """Check if child_class is a subclass of parent_class"""
        hierarchy = self.get_class_hierarchy(child_class)
        return parent_class in hierarchy

    def get_properties_by_class(self, class_name: str, include_inherited: bool = True) -> List[str]:
        """Get all properties for a class"""
        cls = self.get_class(class_name)
        if not cls:
            return []

        if include_inherited:
            return cls.get_all_properties(self)
        else:
            return cls.properties

    def validate_property_value(self, class_name: str, property_name: str, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a property value against ontology constraints"""
        cls = self.get_class(class_name)
        if not cls:
            return False, f"Class {class_name} not found"

        if property_name not in cls.constraints:
            return True, None  # No constraints defined

        constraints = cls.constraints[property_name]

        # Check type
        if 'type' in constraints:
            expected_type = constraints['type']
            if expected_type == 'string' and not isinstance(value, str):
                return False, f"Expected string, got {type(value).__name__}"
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                return False, f"Expected number, got {type(value).__name__}"
            elif expected_type == 'integer' and not isinstance(value, int):
                return False, f"Expected integer, got {type(value).__name__}"
            elif expected_type == 'boolean' and not isinstance(value, bool):
                return False, f"Expected boolean, got {type(value).__name__}"
            elif expected_type == 'enum' and value not in constraints.get('values', []):
                return False, f"Value must be one of {constraints['values']}"

        # Check range constraints
        if 'min' in constraints and isinstance(value, (int, float)):
            if value < constraints['min']:
                return False, f"Value {value} is less than minimum {constraints['min']}"

        if 'max' in constraints and isinstance(value, (int, float)):
            if value > constraints['max']:
                return False, f"Value {value} exceeds maximum {constraints['max']}"

        # Check pattern for strings
        if 'pattern' in constraints and isinstance(value, str):
            import re
            if not re.match(constraints['pattern'], value):
                return False, f"Value does not match required pattern"

        # Check required
        if constraints.get('required') and value is None:
            return False, f"Property {property_name} is required"

        return True, None


class OntologyLoader:
    """Loader for ontology from JSON file"""

    @staticmethod
    def load_from_file(filepath: str) -> Ontology:
        """Load ontology from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return OntologyLoader.load_from_dict(data)

    @staticmethod
    def load_from_dict(data: Dict) -> Ontology:
        """Load ontology from dictionary"""
        # Load metadata
        metadata = data.get('metadata', {})

        # Load classes
        classes = {}
        for class_name, class_data in data.get('classes', {}).items():
            classes[class_name] = OntologyClass(
                name=class_name,
                description=class_data.get('description', ''),
                parent=class_data.get('parent'),
                properties=class_data.get('properties', []),
                constraints=class_data.get('constraints', {})
            )

        # Load relationships
        relationships = []
        for rel_data in data.get('relationships', []):
            relationships.append(Relationship(
                name=rel_data['name'],
                source=rel_data['source'],
                target=rel_data['target'],
                cardinality=rel_data['cardinality'],
                description=rel_data['description'],
                through=rel_data.get('through')
            ))

        # Load properties
        properties = {}
        for prop_name, prop_data in data.get('properties', {}).items():
            properties[prop_name] = Property(
                name=prop_name,
                datatype=prop_data['datatype'],
                description=prop_data['description']
            )

        return Ontology(
            metadata=metadata,
            classes=classes,
            relationships=relationships,
            properties=properties
        )

    @staticmethod
    def load_default() -> Ontology:
        """Load the default ontology from the package"""
        current_dir = Path(__file__).parent
        ontology_path = current_dir / 'ontology.json'
        return OntologyLoader.load_from_file(str(ontology_path))


# Global ontology instance
_ontology_instance: Optional[Ontology] = None


def get_ontology() -> Ontology:
    """Get or load the global ontology instance"""
    global _ontology_instance
    if _ontology_instance is None:
        _ontology_instance = OntologyLoader.load_default()
    return _ontology_instance


def reload_ontology():
    """Reload the ontology from file"""
    global _ontology_instance
    _ontology_instance = OntologyLoader.load_default()


# Convenience functions
def get_class(class_name: str) -> Optional[OntologyClass]:
    """Get a class from the ontology"""
    return get_ontology().get_class(class_name)


def get_property(property_name: str) -> Optional[Property]:
    """Get a property from the ontology"""
    return get_ontology().get_property(property_name)


def get_all_classes() -> List[str]:
    """Get all class names"""
    return list(get_ontology().classes.keys())


def get_all_properties() -> List[str]:
    """Get all property names"""
    return list(get_ontology().properties.keys())


def get_relationships() -> List[Relationship]:
    """Get all relationships"""
    return get_ontology().relationships


if __name__ == '__main__':
    # Test loading
    ontology = get_ontology()
    print(f"Loaded ontology: {ontology.metadata['name']}")
    print(f"Classes: {len(ontology.classes)}")
    print(f"Properties: {len(ontology.properties)}")
    print(f"Relationships: {len(ontology.relationships)}")

    # Test hierarchy
    print("\n=== Class Hierarchy Examples ===")
    for class_name in ['Phones', 'Laptops', 'Customer']:
        hierarchy = ontology.get_class_hierarchy(class_name)
        print(f"{class_name}: {' -> '.join(hierarchy)}")

    # Test property inheritance
    print("\n=== Property Inheritance ===")
    phones_class = ontology.get_class('Phones')
    if phones_class:
        all_props = phones_class.get_all_properties(ontology)
        print(f"Phones properties (including inherited): {len(all_props)}")
        print(f"Direct properties: {phones_class.properties}")
