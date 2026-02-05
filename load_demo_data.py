#!/usr/bin/env python3
"""
Quick Data Loader for Demo Database
Loads ontology and sample data into PostgreSQL
"""

import json
import psycopg2
from psycopg2.extras import Json
import os
from pathlib import Path

# Database connection settings
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ontology_storage',
    'user': 'postgres',
    'password': 'demo123'
}

# Data files directory
DATA_DIR = Path('data_generation/output')
ONTOLOGY_FILE = Path('ontology/ontology.json')

def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Make sure PostgreSQL is running (docker ps)")
        exit(1)

def load_ontology(conn):
    """Load ontology classes, properties, and relationships"""
    print("📚 Loading ontology...")

    with open(ONTOLOGY_FILE, 'r') as f:
        ontology = json.load(f)

    cursor = conn.cursor()

    # Load classes
    print("  - Loading classes...")
    classes_loaded = 0
    for class_name, class_data in ontology.get('classes', {}).items():
        try:
            cursor.execute("""
                INSERT INTO ontology_classes (class_name, parent_class, properties, constraints, description)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (class_name) DO NOTHING
            """, (
                class_name,
                class_data.get('parent'),
                Json(class_data.get('properties', [])),
                Json(class_data.get('constraints', {})),
                class_data.get('description', '')
            ))
            classes_loaded += 1
        except Exception as e:
            print(f"    Warning: Could not load class {class_name}: {e}")

    print(f"  ✓ Loaded {classes_loaded} classes")

    # Load properties
    print("  - Loading properties...")
    props_loaded = 0
    for prop_name, prop_data in ontology.get('properties', {}).items():
        try:
            cursor.execute("""
                INSERT INTO ontology_properties (property_name, datatype, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (property_name) DO NOTHING
            """, (
                prop_name,
                prop_data.get('datatype', 'string'),
                prop_data.get('description', '')
            ))
            props_loaded += 1
        except Exception as e:
            print(f"    Warning: Could not load property {prop_name}: {e}")

    print(f"  ✓ Loaded {props_loaded} properties")

    # Load relationships
    print("  - Loading relationships...")
    rels_loaded = 0
    for rel_data in ontology.get('relationships', []):
        try:
            cursor.execute("""
                INSERT INTO ontology_relationships
                (source_class, target_class, relationship_type, cardinality, description)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                rel_data.get('source'),
                rel_data.get('target'),
                rel_data.get('type', 'has'),
                rel_data.get('cardinality', '1:N'),
                rel_data.get('description', '')
            ))
            rels_loaded += 1
        except Exception as e:
            print(f"    Warning: Could not load relationship: {e}")

    print(f"  ✓ Loaded {rels_loaded} relationships")

    conn.commit()
    cursor.close()

def load_schema_tables(conn):
    """Load schema table metadata"""
    print("📋 Loading schema tables...")

    cursor = conn.cursor()

    # Define schema tables based on JSON files
    tables = [
        ('customer_table', 'Customer', 'Customer information table'),
        ('order', 'Order', 'Order records'),
        ('product_data', 'Product', 'Product catalog'),
        ('category', 'Category', 'Product categories'),
        ('payment', 'Payment', 'Payment transactions'),
        ('review_data', 'Review', 'Customer reviews'),
        ('address_tbl', 'Address', 'Customer addresses'),
        ('vendor_table', 'Vendor', 'Vendor information'),
        ('discount_data', 'Discount', 'Discount and promotions'),
        ('carts', 'Cart', 'Shopping carts')
    ]

    tables_loaded = 0
    for table_name, ontology_class, description in tables:
        try:
            cursor.execute("""
                INSERT INTO schema_tables (table_name, ontology_class, description)
                VALUES (%s, %s, %s)
                ON CONFLICT (table_name) DO NOTHING
            """, (table_name, ontology_class, description))
            tables_loaded += 1
        except Exception as e:
            print(f"  Warning: Could not load table {table_name}: {e}")

    print(f"  ✓ Loaded {tables_loaded} schema tables")
    conn.commit()
    cursor.close()

def load_data_records(conn, limit_per_table=50):
    """Load sample data records from JSON files"""
    print(f"💾 Loading sample data ({limit_per_table} records per table)...")

    cursor = conn.cursor()

    # Get table IDs
    cursor.execute("SELECT id, table_name FROM schema_tables")
    table_map = {name: tid for tid, name in cursor.fetchall()}

    json_files = list(DATA_DIR.glob('*.json'))
    # Exclude consolidated and ground truth files
    json_files = [f for f in json_files if f.stem not in ['consolidated_data', 'ground_truth_mapping']]

    total_loaded = 0

    for json_file in json_files:
        table_name = json_file.stem

        if table_name not in table_map:
            print(f"  ⚠ Skipping {table_name} (not in schema_tables)")
            continue

        print(f"  - Loading {table_name}...")

        try:
            with open(json_file, 'r') as f:
                records = json.load(f)

            # Limit records for demo
            records = records[:limit_per_table]

            table_id = table_map[table_name]

            for record in records:
                try:
                    cursor.execute("""
                        INSERT INTO data_records (table_id, data)
                        VALUES (%s, %s)
                    """, (table_id, Json(record)))
                    total_loaded += 1
                except Exception as e:
                    # Skip duplicate or problematic records
                    pass

            print(f"    ✓ Loaded {len(records)} records")

        except Exception as e:
            print(f"    ❌ Error loading {table_name}: {e}")

    print(f"  ✓ Total: {total_loaded} records loaded")
    conn.commit()
    cursor.close()

def create_sample_field_mappings(conn):
    """Create sample field mappings for demo"""
    print("🔗 Creating sample field mappings...")

    cursor = conn.cursor()

    # Sample mappings (simplified for demo)
    mappings = [
        (1, 'cust_id', 'customerId', 0.95),
        (1, 'fname', 'customerFirstName', 0.92),
        (1, 'l_name', 'customerLastName', 0.93),
        (1, 'email_addr', 'customerEmail', 0.97),
        (1, 'ph_num', 'customerPhone', 0.90),
        (2, 'ord_id', 'orderId', 0.96),
        (2, 'ord_dt', 'orderDate', 0.94),
        (2, 'ord_val', 'orderTotal', 0.88),
        (3, 'prod_id', 'productId', 0.95),
        (3, 'prod_nm', 'productName', 0.93),
        (3, 'prod_price', 'productPrice', 0.97)
    ]

    mappings_loaded = 0
    for table_id, field_name, property_name, confidence in mappings:
        try:
            cursor.execute("""
                INSERT INTO field_mappings (table_id, field_name, property_name, confidence_score)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (table_id, field_name, property_name, confidence))
            mappings_loaded += 1
        except:
            pass

    print(f"  ✓ Created {mappings_loaded} field mappings")
    conn.commit()
    cursor.close()

def verify_data(conn):
    """Verify data was loaded correctly"""
    print("\n✅ Verifying data...")

    cursor = conn.cursor()

    # Count classes
    cursor.execute("SELECT COUNT(*) FROM ontology_classes")
    class_count = cursor.fetchone()[0]
    print(f"  - Ontology classes: {class_count}")

    # Count properties
    cursor.execute("SELECT COUNT(*) FROM ontology_properties")
    prop_count = cursor.fetchone()[0]
    print(f"  - Ontology properties: {prop_count}")

    # Count relationships
    cursor.execute("SELECT COUNT(*) FROM ontology_relationships")
    rel_count = cursor.fetchone()[0]
    print(f"  - Relationships: {rel_count}")

    # Count schema tables
    cursor.execute("SELECT COUNT(*) FROM schema_tables")
    table_count = cursor.fetchone()[0]
    print(f"  - Schema tables: {table_count}")

    # Count data records
    cursor.execute("SELECT COUNT(*) FROM data_records")
    record_count = cursor.fetchone()[0]
    print(f"  - Data records: {record_count}")

    # Show sample JSONB data
    cursor.execute("""
        SELECT st.table_name, dr.data
        FROM data_records dr
        JOIN schema_tables st ON dr.table_id = st.id
        WHERE st.table_name = 'customer_table'
        LIMIT 1
    """)
    result = cursor.fetchone()
    if result:
        print(f"\n  📋 Sample JSONB record from {result[0]}:")
        print(f"     Keys: {list(result[1].keys())}")
        print(f"     Sample: {dict(list(result[1].items())[:3])}")

    cursor.close()

def main():
    print("=" * 60)
    print("🚀 Demo Database Data Loader")
    print("=" * 60)
    print()

    # Connect to database
    print("🔌 Connecting to database...")
    conn = connect_db()
    print("  ✓ Connected!")
    print()

    try:
        # Load ontology
        load_ontology(conn)
        print()

        # Load schema tables
        load_schema_tables(conn)
        print()

        # Load data records
        load_data_records(conn, limit_per_table=50)
        print()

        # Create sample mappings
        create_sample_field_mappings(conn)
        print()

        # Verify
        verify_data(conn)
        print()

        print("=" * 60)
        print("✅ Data loading complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Open Adminer: http://localhost:8080")
        print("  2. Login with credentials from setup output")
        print("  3. Browse tables and see JSONB data!")
        print()

    except Exception as e:
        print(f"\n❌ Error during data loading: {e}")
        conn.rollback()
        exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
