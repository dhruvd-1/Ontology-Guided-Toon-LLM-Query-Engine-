"""
Storage module for PostgreSQL + pgvector
"""

try:
    from storage.db import (
        Database,
        DatabaseConfig,
        OntologyRepository,
        SchemaRepository,
        DataRepository,
        get_database
    )

    from storage.ingest import (
        ingest_ontology,
        ingest_schema_mappings,
        ingest_data_records,
        ingest_all
    )

    __all__ = [
        'Database',
        'DatabaseConfig',
        'OntologyRepository',
        'SchemaRepository',
        'DataRepository',
        'get_database',
        'ingest_ontology',
        'ingest_schema_mappings',
        'ingest_data_records',
        'ingest_all',
    ]
except ImportError as e:
    print(f"Warning: Storage module dependencies not fully available: {e}")
    __all__ = []
