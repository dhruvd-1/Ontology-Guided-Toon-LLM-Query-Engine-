"""
Comprehensive test suite for ontology module
"""

import sys
from ontology import (
    get_ontology,
    validate_ontology,
    print_validation_report,
    get_class,
    get_all_classes,
    get_relationships,
)


def test_ontology_loading():
    """Test that ontology loads correctly"""
    print("TEST 1: Ontology Loading")
    print("-" * 50)

    ontology = get_ontology()
    print(f"✓ Ontology loaded: {ontology.metadata.get('name')}")
    print(f"✓ Classes: {len(ontology.classes)}")
    print(f"✓ Properties: {len(ontology.properties)}")
    print(f"✓ Relationships: {len(ontology.relationships)}")

    assert len(ontology.classes) >= 15, "Should have at least 15 classes"
    assert len(ontology.properties) >= 30, "Should have at least 30 properties"
    assert len(ontology.relationships) >= 5, "Should have at least 5 relationships"

    print("✓ All loading tests passed!\n")
    return True


def test_mandatory_classes():
    """Test that all mandatory classes exist"""
    print("TEST 2: Mandatory Classes")
    print("-" * 50)

    mandatory_classes = [
        'Customer', 'Order', 'Product', 'Category', 'Payment',
        'Address', 'Review', 'Vendor', 'Cart', 'Discount',
        'Shipment', 'Inventory', 'Transaction', 'SupportTicket', 'LoyaltyProfile'
    ]

    all_classes = get_all_classes()

    for class_name in mandatory_classes:
        assert class_name in all_classes, f"Missing mandatory class: {class_name}"
        cls = get_class(class_name)
        assert cls is not None, f"Class {class_name} should be loadable"
        print(f"✓ {class_name} - {len(cls.properties)} properties")

    print("✓ All mandatory classes present!\n")
    return True


def test_class_hierarchy():
    """Test class hierarchy functionality"""
    print("TEST 3: Class Hierarchy")
    print("-" * 50)

    ontology = get_ontology()

    # Test Electronics hierarchy
    electronics = get_class('Electronics')
    assert electronics is not None, "Electronics class should exist"
    assert electronics.parent == 'Category', "Electronics should inherit from Category"
    print(f"✓ Electronics parent: {electronics.parent}")

    # Test Phones hierarchy
    phones = get_class('Phones')
    assert phones is not None, "Phones class should exist"
    assert phones.parent == 'Electronics', "Phones should inherit from Electronics"

    hierarchy = ontology.get_class_hierarchy('Phones')
    print(f"✓ Phones hierarchy: {' -> '.join(hierarchy)}")
    assert 'Category' in hierarchy, "Phones should have Category in hierarchy"
    assert 'Electronics' in hierarchy, "Phones should have Electronics in hierarchy"

    # Test property inheritance
    phones_props = ontology.get_properties_by_class('Phones', include_inherited=True)
    phones_direct = ontology.get_properties_by_class('Phones', include_inherited=False)

    print(f"✓ Phones direct properties: {len(phones_direct)}")
    print(f"✓ Phones total properties (with inheritance): {len(phones_props)}")
    assert len(phones_props) > len(phones_direct), "Should inherit properties from parent"

    print("✓ All hierarchy tests passed!\n")
    return True


def test_relationships():
    """Test relationships between classes"""
    print("TEST 4: Relationships")
    print("-" * 50)

    relationships = get_relationships()

    # Check for key relationships
    rel_names = [rel.name for rel in relationships]

    key_relationships = ['places', 'contains', 'belongsTo', 'hasAddress']
    for rel_name in key_relationships:
        assert rel_name in rel_names, f"Missing relationship: {rel_name}"
        print(f"✓ Relationship '{rel_name}' exists")

    # Test relationship queries
    ontology = get_ontology()
    customer_rels = ontology.get_relationships_for_class('Customer')
    print(f"✓ Customer has {len(customer_rels)} relationships")

    order_rels = ontology.get_relationships_for_class('Order')
    print(f"✓ Order has {len(order_rels)} relationships")

    print("✓ All relationship tests passed!\n")
    return True


def test_constraints():
    """Test constraint validation"""
    print("TEST 5: Constraints")
    print("-" * 50)

    ontology = get_ontology()

    # Test valid email
    is_valid, msg = ontology.validate_property_value(
        'Customer', 'email', 'test@example.com'
    )
    print(f"✓ Valid email test: {is_valid}")
    assert is_valid, "Valid email should pass"

    # Test price constraint
    is_valid, msg = ontology.validate_property_value(
        'Product', 'price', 99.99
    )
    print(f"✓ Valid price test: {is_valid}")
    assert is_valid, "Valid price should pass"

    # Test negative price (should fail)
    is_valid, msg = ontology.validate_property_value(
        'Product', 'price', -10
    )
    print(f"✓ Invalid price test: {not is_valid} (correctly rejected)")
    assert not is_valid, "Negative price should fail"

    # Test enum constraint
    is_valid, msg = ontology.validate_property_value(
        'Customer', 'customerTier', 'gold'
    )
    print(f"✓ Valid enum test: {is_valid}")
    assert is_valid, "Valid enum value should pass"

    print("✓ All constraint tests passed!\n")
    return True


def test_validation():
    """Test ontology validation"""
    print("TEST 6: Ontology Validation")
    print("-" * 50)

    is_valid, issues = validate_ontology()

    errors = [i for i in issues if i.severity == 'error']
    warnings = [i for i in issues if i.severity == 'warning']

    print(f"✓ Validation completed")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    assert is_valid, "Ontology should be valid"
    assert len(errors) == 0, "Should have no errors"

    print("✓ Ontology validation passed!\n")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 50)
    print("ONTOLOGY TEST SUITE")
    print("=" * 50 + "\n")

    tests = [
        test_ontology_loading,
        test_mandatory_classes,
        test_class_hierarchy,
        test_relationships,
        test_constraints,
        test_validation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ TEST FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ TEST ERROR: {e}\n")
            failed += 1

    print("=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
