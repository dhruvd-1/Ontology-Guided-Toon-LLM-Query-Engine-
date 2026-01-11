"""
Ontology Validation Module

Validates ontology consistency, completeness, and correctness.
"""

from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from ontology.schema import Ontology, OntologyLoader


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: str  # 'error', 'warning', 'info'
    category: str
    message: str
    details: Dict = None

    def __str__(self):
        detail_str = f" - {self.details}" if self.details else ""
        return f"[{self.severity.upper()}] {self.category}: {self.message}{detail_str}"


class OntologyValidator:
    """Validates ontology structure and consistency"""

    def __init__(self, ontology: Ontology):
        self.ontology = ontology
        self.issues: List[ValidationIssue] = []

    def validate(self) -> Tuple[bool, List[ValidationIssue]]:
        """Run all validation checks"""
        self.issues = []

        # Run all validation checks
        self._validate_metadata()
        self._validate_classes()
        self._validate_properties()
        self._validate_relationships()
        self._validate_constraints()
        self._validate_hierarchy()
        self._validate_completeness()

        # Check if there are any errors
        has_errors = any(issue.severity == 'error' for issue in self.issues)

        return not has_errors, self.issues

    def _validate_metadata(self):
        """Validate ontology metadata"""
        required_fields = ['name', 'version', 'description']

        for field in required_fields:
            if field not in self.ontology.metadata:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='Metadata',
                    message=f"Missing metadata field: {field}"
                ))

    def _validate_classes(self):
        """Validate ontology classes"""
        if len(self.ontology.classes) < 15:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='Classes',
                message=f"Ontology has {len(self.ontology.classes)} classes, recommended minimum is 15"
            ))

        # Check for classes without properties
        for class_name, cls in self.ontology.classes.items():
            if not cls.properties:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='Classes',
                    message=f"Class '{class_name}' has no properties"
                ))

            # Check if parent exists
            if cls.parent and cls.parent not in self.ontology.classes:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Classes',
                    message=f"Class '{class_name}' has non-existent parent '{cls.parent}'"
                ))

            # Check for circular inheritance
            if self._has_circular_inheritance(class_name):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Classes',
                    message=f"Class '{class_name}' has circular inheritance"
                ))

    def _validate_properties(self):
        """Validate ontology properties"""
        if len(self.ontology.properties) < 30:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='Properties',
                message=f"Ontology has {len(self.ontology.properties)} properties, recommended minimum is 30"
            ))

        # Check for properties used in classes but not defined
        all_used_properties = set()
        for cls in self.ontology.classes.values():
            all_used_properties.update(cls.properties)

        for prop_name in all_used_properties:
            if prop_name not in self.ontology.properties:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Properties',
                    message=f"Property '{prop_name}' is used in classes but not defined in properties section"
                ))

        # Check for unused properties
        for prop_name in self.ontology.properties:
            if prop_name not in all_used_properties:
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='Properties',
                    message=f"Property '{prop_name}' is defined but not used in any class"
                ))

    def _validate_relationships(self):
        """Validate relationships"""
        for rel in self.ontology.relationships:
            # Check if source and target classes exist
            if rel.source not in self.ontology.classes:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Relationships',
                    message=f"Relationship '{rel.name}' has non-existent source class '{rel.source}'"
                ))

            if rel.target not in self.ontology.classes:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Relationships',
                    message=f"Relationship '{rel.name}' has non-existent target class '{rel.target}'"
                ))

            # Check if through class exists (if specified)
            if rel.through and rel.through not in self.ontology.classes:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Relationships',
                    message=f"Relationship '{rel.name}' has non-existent through class '{rel.through}'"
                ))

            # Validate cardinality format
            valid_cardinalities = ['one-to-one', 'one-to-many', 'many-to-one', 'many-to-many']
            if rel.cardinality not in valid_cardinalities:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='Relationships',
                    message=f"Relationship '{rel.name}' has unusual cardinality '{rel.cardinality}'"
                ))

    def _validate_constraints(self):
        """Validate constraints on class properties"""
        for class_name, cls in self.ontology.classes.items():
            for prop_name, constraints in cls.constraints.items():
                # Check if constrained property exists in class
                if prop_name not in cls.properties:
                    self.issues.append(ValidationIssue(
                        severity='error',
                        category='Constraints',
                        message=f"Class '{class_name}' has constraints for non-existent property '{prop_name}'"
                    ))

                # Validate constraint types
                if 'type' in constraints:
                    constraint_type = constraints['type']
                    valid_types = ['string', 'number', 'integer', 'boolean', 'enum', 'date', 'datetime', 'text', 'decimal']
                    if constraint_type not in valid_types:
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            category='Constraints',
                            message=f"Property '{prop_name}' in class '{class_name}' has unknown type '{constraint_type}'"
                        ))

                # Check enum constraints
                if constraints.get('type') == 'enum' and 'values' not in constraints:
                    self.issues.append(ValidationIssue(
                        severity='error',
                        category='Constraints',
                        message=f"Enum property '{prop_name}' in class '{class_name}' has no values defined"
                    ))

                # Check numeric constraints
                if 'min' in constraints and 'max' in constraints:
                    if constraints['min'] > constraints['max']:
                        self.issues.append(ValidationIssue(
                            severity='error',
                            category='Constraints',
                            message=f"Property '{prop_name}' in class '{class_name}' has min > max"
                        ))

    def _validate_hierarchy(self):
        """Validate class hierarchy"""
        # Check for orphaned hierarchies (classes with parents but no root)
        roots = [name for name, cls in self.ontology.classes.items() if cls.parent is None]

        if not roots:
            self.issues.append(ValidationIssue(
                severity='error',
                category='Hierarchy',
                message="No root classes found (all classes have parents)"
            ))

        # Check for classes that inherit from themselves
        for class_name in self.ontology.classes:
            hierarchy = self.ontology.get_class_hierarchy(class_name)
            if len(hierarchy) != len(set(hierarchy)):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Hierarchy',
                    message=f"Class '{class_name}' has duplicate classes in hierarchy"
                ))

    def _validate_completeness(self):
        """Validate ontology completeness"""
        # Check for mandatory classes
        mandatory_classes = [
            'Customer', 'Order', 'Product', 'Category', 'Payment',
            'Address', 'Review', 'Vendor', 'Cart', 'Discount',
            'Shipment', 'Inventory', 'Transaction', 'SupportTicket', 'LoyaltyProfile'
        ]

        for class_name in mandatory_classes:
            if class_name not in self.ontology.classes:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='Completeness',
                    message=f"Mandatory class '{class_name}' is missing"
                ))

        # Check for at least some relationships
        if len(self.ontology.relationships) < 5:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='Completeness',
                message=f"Ontology has only {len(self.ontology.relationships)} relationships, recommended minimum is 10+"
            ))

    def _has_circular_inheritance(self, class_name: str, visited: Set[str] = None) -> bool:
        """Check if a class has circular inheritance"""
        if visited is None:
            visited = set()

        if class_name in visited:
            return True

        visited.add(class_name)
        cls = self.ontology.get_class(class_name)

        if cls and cls.parent:
            return self._has_circular_inheritance(cls.parent, visited)

        return False


def validate_ontology(ontology: Ontology = None) -> Tuple[bool, List[ValidationIssue]]:
    """Validate an ontology and return results"""
    if ontology is None:
        ontology = OntologyLoader.load_default()

    validator = OntologyValidator(ontology)
    return validator.validate()


def print_validation_report(issues: List[ValidationIssue]):
    """Print a formatted validation report"""
    if not issues:
        print("✓ Ontology validation passed with no issues!")
        return

    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']
    info = [i for i in issues if i.severity == 'info']

    print(f"\n=== Ontology Validation Report ===")
    print(f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info)}\n")

    if errors:
        print("ERRORS:")
        for issue in errors:
            print(f"  {issue}")
        print()

    if warnings:
        print("WARNINGS:")
        for issue in warnings:
            print(f"  {issue}")
        print()

    if info:
        print("INFO:")
        for issue in info:
            print(f"  {issue}")
        print()


if __name__ == '__main__':
    # Load and validate the ontology
    print("Loading ontology...")
    ontology = OntologyLoader.load_default()

    print(f"Loaded: {ontology.metadata.get('name', 'Unknown')}")
    print(f"  Classes: {len(ontology.classes)}")
    print(f"  Properties: {len(ontology.properties)}")
    print(f"  Relationships: {len(ontology.relationships)}")

    print("\nValidating ontology...")
    is_valid, issues = validate_ontology(ontology)

    print_validation_report(issues)

    if is_valid:
        print("\n✓ Ontology is valid and ready to use!")
    else:
        print("\n✗ Ontology has errors that must be fixed!")

    exit(0 if is_valid else 1)
