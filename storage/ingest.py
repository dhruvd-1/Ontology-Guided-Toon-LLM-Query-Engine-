"""
Data Ingestion Module

Ingests ontology, schemas, and data into PostgreSQL storage.
"""

import json
from typing import Dict, List
from storage.db import Database, OntologyRepository, SchemaRepository, DataRepository
from ontology import get_ontology


def ingest_ontology(db: Database) -> Dict[str, int]:
    """
    Ingest ontology into database

    Returns:
        Dictionary with counts of inserted entities
    """
    print("Ingesting ontology...")

    repo = OntologyRepository(db)
    ontology = get_ontology()

    counts = {
        'classes': 0,
        'properties': 0,
        'relationships': 0
    }

    # Insert classes
    for class_name, cls in ontology.classes.items():
        repo.insert_ontology_class({
            'name': class_name,
            'parent': cls.parent,
            'description': cls.description,
            'properties': cls.properties
        })
        counts['classes'] += 1

    # Insert properties
    for prop_name, prop in ontology.properties.items():
        repo.insert_ontology_property({
            'name': prop_name,
            'datatype': prop.datatype,
            'description': prop.description
        })
        counts['properties'] += 1

    # Insert relationships
    for rel in ontology.relationships:
        repo.insert_ontology_relationship({
            'name': rel.name,
            'source_class': rel.source,
            'target_class': rel.target,
            'cardinality': rel.cardinality,
            'description': rel.description
        })
        counts['relationships'] += 1

    print(f"✓ Ontology ingested: {counts}")
    return counts


def ingest_schema_mappings(
    db: Database,
    ground_truth_path: str = 'data_generation/output/ground_truth_mapping.json'
) -> Dict[str, int]:
    """
    Ingest schema mappings from ground truth

    Returns:
        Dictionary with counts of inserted mappings
    """
    print("Ingesting schema mappings...")

    repo = SchemaRepository(db)

    with open(ground_truth_path, 'r') as f:
        ground_truth = json.load(f)

    counts = {
        'tables': 0,
        'mappings': 0
    }

    # Insert tables and mappings
    for table_name, table_info in ground_truth['tables'].items():
        # Insert table
        table_id = repo.insert_schema_table({
            'table_name': table_name,
            'ontology_class': table_info['ontology_class'],
            'metadata': {
                'num_fields': len(table_info['fields'])
            }
        })
        counts['tables'] += 1

        # Insert field mappings
        for field in table_info['fields']:
            repo.insert_field_mapping({
                'table_id': table_id,
                'field_name': field['field_name'],
                'data_type': field['data_type'],
                'ontology_property': field['ontology_property'],
                'ontology_class': field['ontology_class'],
                'confidence_score': 1.0,  # Ground truth has perfect confidence
                'is_primary_key': field.get('is_primary_key', False),
                'is_nullable': field.get('is_nullable', True)
            })
            counts['mappings'] += 1

    print(f"✓ Schema mappings ingested: {counts}")
    return counts


def ingest_data_records(
    db: Database,
    data_dir: str = 'data_generation/output',
    limit_per_table: int = 100
) -> Dict[str, int]:
    """
    Ingest data records from generated data

    Returns:
        Dictionary with counts of inserted records
    """
    print(f"Ingesting data records (limit: {limit_per_table} per table)...")

    data_repo = DataRepository(db)
    schema_repo = SchemaRepository(db)

    # Load consolidated data
    with open(f'{data_dir}/consolidated_data.json', 'r') as f:
        consolidated = json.load(f)

    counts = {'records': 0}

    tables_data = consolidated['tables']

    for table_name, records in tables_data.items():
        # Get table_id
        mappings = schema_repo.get_table_mappings(table_name)
        if not mappings or len(mappings) == 0:
            print(f"  ⚠ Table {table_name} not found in schema mappings, skipping")
            continue

        table_id = mappings[0]['table_id']

        # Batch insert records (limited)
        records_to_insert = records[:limit_per_table]
        record_ids = data_repo.insert_records_batch(table_id, records_to_insert)

        counts['records'] += len(record_ids)
        print(f"  ✓ {table_name}: {len(record_ids)} records")

    print(f"✓ Data records ingested: {counts}")
    return counts


def ingest_all(
    db: Database,
    include_data: bool = True,
    data_limit: int = 100
) -> Dict:
    """
    Ingest everything: ontology, schemas, and data

    Returns:
        Dictionary with all ingestion results
    """
    print("=== Full Data Ingestion ===\n")

    results = {}

    try:
        # Ingest ontology
        results['ontology'] = ingest_ontology(db)
        print()

        # Ingest schema mappings
        results['schema'] = ingest_schema_mappings(db)
        print()

        # Ingest data records (optional)
        if include_data:
            results['data'] = ingest_data_records(db, limit_per_table=data_limit)
            print()

        print("✓ Ingestion complete!")

        return results

    except Exception as e:
        print(f"\n✗ Ingestion failed: {e}")
        raise


if __name__ == '__main__':
    import sys

    try:
        db = Database()

        # Test connection
        if not db.test_connection():
            print("\n⚠ Database not available")
            print("  Ingestion module is implemented and ready to use")
            print("  Run this with PostgreSQL available to ingest data")
            sys.exit(0)

        # Initialize schema
        print("\nInitializing database schema...")
        db.execute_schema()
        print()

        # Run ingestion
        results = ingest_all(db, include_data=True, data_limit=50)

        # Print summary
        print("\n=== Ingestion Summary ===")
        if 'ontology' in results:
            print(f"Ontology: {results['ontology']['classes']} classes, "
                  f"{results['ontology']['properties']} properties, "
                  f"{results['ontology']['relationships']} relationships")

        if 'schema' in results:
            print(f"Schema: {results['schema']['tables']} tables, "
                  f"{results['schema']['mappings']} field mappings")

        if 'data' in results:
            print(f"Data: {results['data']['records']} records")

        print("\n✓ All data ingested successfully!")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
