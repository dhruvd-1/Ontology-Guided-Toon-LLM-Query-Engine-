"""
Database Connection and ORM Layer

Handles PostgreSQL + pgvector connections and operations.
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager
import numpy as np


class DatabaseConfig:
    """Database configuration"""

    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'ontology_storage')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', 'postgres')

    def get_connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def get_connection_params(self) -> Dict:
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }


class Database:
    """Database connection manager"""

    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.connection = None

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = psycopg2.connect(**self.config.get_connection_params())
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()

    def execute_schema(self, schema_file: str = 'storage/models.sql'):
        """Execute SQL schema file"""
        with open(schema_file, 'r') as f:
            schema_sql = f.read()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(schema_sql)
            cursor.close()

        print(f"✓ Schema executed from {schema_file}")

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✓ Connected to PostgreSQL: {version[0][:50]}...")

                # Check pgvector extension
                cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
                if cursor.fetchone():
                    print("✓ pgvector extension available")
                else:
                    print("⚠ pgvector extension not installed")

                cursor.close()
                return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False


class OntologyRepository:
    """Repository for ontology data"""

    def __init__(self, db: Database):
        self.db = db

    def insert_ontology_class(self, class_data: Dict) -> int:
        """Insert ontology class"""
        query = """
        INSERT INTO ontology_classes (class_name, parent_class, description, properties)
        VALUES (%(class_name)s, %(parent_class)s, %(description)s, %(properties)s)
        ON CONFLICT (class_name) DO UPDATE
        SET parent_class = EXCLUDED.parent_class,
            description = EXCLUDED.description,
            properties = EXCLUDED.properties
        RETURNING class_id;
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, {
                'class_name': class_data['name'],
                'parent_class': class_data.get('parent'),
                'description': class_data.get('description', ''),
                'properties': json.dumps(class_data.get('properties', []))
            })
            return cursor.fetchone()['class_id']

    def insert_ontology_property(self, property_data: Dict) -> int:
        """Insert ontology property"""
        query = """
        INSERT INTO ontology_properties (property_name, datatype, description, constraints)
        VALUES (%(property_name)s, %(datatype)s, %(description)s, %(constraints)s)
        ON CONFLICT (property_name) DO UPDATE
        SET datatype = EXCLUDED.datatype,
            description = EXCLUDED.description,
            constraints = EXCLUDED.constraints
        RETURNING property_id;
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, {
                'property_name': property_data['name'],
                'datatype': property_data.get('datatype', 'string'),
                'description': property_data.get('description', ''),
                'constraints': json.dumps(property_data.get('constraints', {}))
            })
            return cursor.fetchone()['property_id']

    def insert_ontology_relationship(self, rel_data: Dict) -> int:
        """Insert ontology relationship"""
        query = """
        INSERT INTO ontology_relationships (name, source_class, target_class, cardinality, description)
        VALUES (%(name)s, %(source_class)s, %(target_class)s, %(cardinality)s, %(description)s)
        RETURNING relationship_id;
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, rel_data)
            return cursor.fetchone()['relationship_id']


class SchemaRepository:
    """Repository for schema mappings"""

    def __init__(self, db: Database):
        self.db = db

    def insert_schema_table(self, table_data: Dict) -> int:
        """Insert schema table mapping"""
        query = """
        INSERT INTO schema_tables (table_name, ontology_class, schema_metadata)
        VALUES (%(table_name)s, %(ontology_class)s, %(schema_metadata)s)
        ON CONFLICT (table_name) DO UPDATE
        SET ontology_class = EXCLUDED.ontology_class,
            schema_metadata = EXCLUDED.schema_metadata
        RETURNING table_id;
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, {
                'table_name': table_data['table_name'],
                'ontology_class': table_data.get('ontology_class'),
                'schema_metadata': json.dumps(table_data.get('metadata', {}))
            })
            return cursor.fetchone()['table_id']

    def insert_field_mapping(self, mapping_data: Dict) -> int:
        """Insert field mapping"""
        query = """
        INSERT INTO field_mappings (
            table_id, field_name, data_type, ontology_property, ontology_class,
            confidence_score, is_primary_key, is_nullable, mapping_metadata
        )
        VALUES (
            %(table_id)s, %(field_name)s, %(data_type)s, %(ontology_property)s, %(ontology_class)s,
            %(confidence_score)s, %(is_primary_key)s, %(is_nullable)s, %(mapping_metadata)s
        )
        ON CONFLICT (table_id, field_name) DO UPDATE
        SET ontology_property = EXCLUDED.ontology_property,
            confidence_score = EXCLUDED.confidence_score
        RETURNING mapping_id;
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, {
                'table_id': mapping_data['table_id'],
                'field_name': mapping_data['field_name'],
                'data_type': mapping_data.get('data_type', 'VARCHAR'),
                'ontology_property': mapping_data.get('ontology_property'),
                'ontology_class': mapping_data.get('ontology_class'),
                'confidence_score': mapping_data.get('confidence_score', 0.0),
                'is_primary_key': mapping_data.get('is_primary_key', False),
                'is_nullable': mapping_data.get('is_nullable', True),
                'mapping_metadata': json.dumps(mapping_data.get('metadata', {}))
            })
            return cursor.fetchone()['mapping_id']

    def get_table_mappings(self, table_name: str) -> Optional[Dict]:
        """Get field mappings for a table"""
        query = """
        SELECT
            st.table_id,
            st.table_name,
            st.ontology_class,
            fm.field_name,
            fm.ontology_property,
            fm.confidence_score
        FROM schema_tables st
        LEFT JOIN field_mappings fm ON st.table_id = fm.table_id
        WHERE st.table_name = %s;
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, (table_name,))
            return cursor.fetchall()


class DataRepository:
    """Repository for data records"""

    def __init__(self, db: Database):
        self.db = db

    def insert_record(self, table_id: int, record_data: Dict, embedding: Optional[np.ndarray] = None) -> int:
        """Insert data record with optional embedding"""
        query = """
        INSERT INTO data_records (table_id, record_data, embedding)
        VALUES (%(table_id)s, %(record_data)s, %(embedding)s)
        RETURNING record_id;
        """

        embedding_list = embedding.tolist() if embedding is not None else None

        with self.db.get_cursor() as cursor:
            cursor.execute(query, {
                'table_id': table_id,
                'record_data': json.dumps(record_data),
                'embedding': embedding_list
            })
            return cursor.fetchone()['record_id']

    def insert_records_batch(self, table_id: int, records: List[Dict]) -> List[int]:
        """Batch insert records"""
        query = """
        INSERT INTO data_records (table_id, record_data)
        VALUES %s
        RETURNING record_id;
        """

        values = [(table_id, json.dumps(record)) for record in records]

        with self.db.get_cursor() as cursor:
            result = execute_values(cursor, query, values, fetch=True)
            return [row['record_id'] for row in result]

    def find_similar_records(
        self,
        query_embedding: np.ndarray,
        limit: int = 10
    ) -> List[Dict]:
        """Find similar records using vector similarity"""
        query = """
        SELECT * FROM find_similar_records(%s::vector, %s);
        """

        with self.db.get_cursor() as cursor:
            cursor.execute(query, (query_embedding.tolist(), limit))
            return cursor.fetchall()


# Singleton database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get database singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == '__main__':
    print("=== Database Connection Test ===\n")

    db = get_database()

    # Test connection
    if db.test_connection():
        print("\n✓ Database connection successful!")

        # Try to execute schema
        try:
            db.execute_schema()
            print("✓ Schema initialized!")
        except Exception as e:
            print(f"⚠ Schema execution skipped (expected if DB not available): {e}")
    else:
        print("\n⚠ Database not available (expected in this environment)")
        print("  Database layer is implemented and ready to use when PostgreSQL is available")
