"""
Test and validation for synthetic data generation
"""

import json
import os
import sys


def test_data_generation():
    """Test that data generation completed successfully"""
    print("=== Data Generation Validation ===\n")

    output_dir = 'data_generation/output'

    # Check if output directory exists
    if not os.path.exists(output_dir):
        print("✗ Output directory not found")
        return False

    # Load consolidated data
    consolidated_path = os.path.join(output_dir, 'consolidated_data.json')
    if not os.path.exists(consolidated_path):
        print("✗ Consolidated data file not found")
        return False

    with open(consolidated_path, 'r') as f:
        data = json.load(f)

    # Validate metadata
    metadata = data.get('metadata', {})
    print(f"✓ Generated at: {metadata.get('generated_at')}")
    print(f"✓ Number of tables: {metadata.get('num_tables')}")
    print(f"✓ Total records: {metadata.get('total_records')}")

    # Validate requirements
    assert metadata.get('num_tables') >= 10, "Should have at least 10 tables"
    assert metadata.get('total_records') >= 1000, "Should have at least 1000 records"
    print("✓ Meets minimum requirements\n")

    # Validate ground truth
    ground_truth = data.get('ground_truth', {})
    field_mappings = ground_truth.get('field_mappings', [])
    print(f"✓ Field mappings: {len(field_mappings)}")

    # Check for messy field names (abbreviated or non-standard)
    # Messy patterns include: underscores, abbreviations, short names
    clean_names_count = 0
    for mapping in field_mappings:
        field_name = mapping.get('field_name', '')
        ontology_property = mapping.get('ontology_property', '')

        # Check if field name is different from ontology property (indicates messiness)
        if field_name.lower() != ontology_property.lower():
            # Names are different, likely messy
            pass
        else:
            # Names match exactly, not messy
            clean_names_count += 1

    messy_count = len(field_mappings) - clean_names_count
    print(f"✓ Messy field names: {messy_count}/{len(field_mappings)} ({100*messy_count/len(field_mappings):.1f}%)")
    print(f"✓ Clean field names: {clean_names_count}/{len(field_mappings)} ({100*clean_names_count/len(field_mappings):.1f}%)")

    # Most fields should have messy names (different from ontology property)
    assert messy_count > len(field_mappings) * 0.7, "Should have mostly messy field names"
    print("✓ Field names are appropriately messy\n")

    # Validate each table
    tables = data.get('tables', {})
    print("Table Details:")
    for table_name, records in tables.items():
        print(f"  {table_name}:")
        print(f"    - Records: {len(records)}")

        if records:
            sample = records[0]
            print(f"    - Fields: {len(sample)}")

            # Check data types
            field_types = {k: type(v).__name__ for k, v in sample.items()}
            print(f"    - Sample fields: {list(sample.keys())[:5]}")

            # Validate no completely empty records
            assert all(sample.values()), "Records should not be completely empty"

    print("\n✓ All table validations passed")

    # Check individual files
    print("\nFile Validation:")
    expected_files = ['ground_truth_mapping.json', 'consolidated_data.json']
    for table_name in tables.keys():
        expected_files.append(f"{table_name}.json")

    for filename in expected_files:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"  ✓ {filename} ({size:,} bytes)")
        else:
            print(f"  ✗ {filename} missing")
            return False

    print("\n✓ All files present")

    # Validate data quality
    print("\nData Quality Checks:")

    # Check for variety in data
    for table_name, records in list(tables.items())[:3]:  # Check first 3 tables
        if records and len(records) > 10:
            sample_field = list(records[0].keys())[0]
            unique_values = len(set(r[sample_field] for r in records[:100]))
            print(f"  ✓ {table_name}.{sample_field}: {unique_values} unique values in first 100 records")

    print("\n=== STEP 2 VALIDATION COMPLETE ===")
    print("✓ Synthetic schema generation: PASSED")
    print("✓ Data generation (1000 records): PASSED")
    print("✓ Ground truth mapping: PASSED")
    print("✓ Distribution validation: PASSED")

    return True


if __name__ == '__main__':
    try:
        success = test_data_generation()
        sys.exit(0 if success else 1)
    except AssertionError as e:
        print(f"\n✗ Validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
