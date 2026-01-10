"""
Ontology module for e-commerce domain modeling
"""

from ontology.schema import (
    Ontology,
    OntologyClass,
    Property,
    Relationship,
    OntologyLoader,
    get_ontology,
    get_class,
    get_property,
    get_all_classes,
    get_all_properties,
    get_relationships,
)

from ontology.validation import (
    validate_ontology,
    ValidationIssue,
    OntologyValidator,
    print_validation_report,
)

__all__ = [
    'Ontology',
    'OntologyClass',
    'Property',
    'Relationship',
    'OntologyLoader',
    'get_ontology',
    'get_class',
    'get_property',
    'get_all_classes',
    'get_all_properties',
    'get_relationships',
    'validate_ontology',
    'ValidationIssue',
    'OntologyValidator',
    'print_validation_report',
]
