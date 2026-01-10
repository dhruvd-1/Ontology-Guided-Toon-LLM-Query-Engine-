-- Ontology-Guided Storage Schema
-- PostgreSQL + pgvector for semantic similarity

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Ontology Classes Table
CREATE TABLE IF NOT EXISTS ontology_classes (
    class_id SERIAL PRIMARY KEY,
    class_name VARCHAR(100) UNIQUE NOT NULL,
    parent_class VARCHAR(100),
    description TEXT,
    properties JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ontology Properties Table
CREATE TABLE IF NOT EXISTS ontology_properties (
    property_id SERIAL PRIMARY KEY,
    property_name VARCHAR(100) UNIQUE NOT NULL,
    datatype VARCHAR(50),
    description TEXT,
    constraints JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ontology Relationships Table
CREATE TABLE IF NOT EXISTS ontology_relationships (
    relationship_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    source_class VARCHAR(100) NOT NULL,
    target_class VARCHAR(100) NOT NULL,
    cardinality VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schema Tables Mapping
CREATE TABLE IF NOT EXISTS schema_tables (
    table_id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    ontology_class VARCHAR(100),
    schema_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_name)
);

-- Field Mappings Table
CREATE TABLE IF NOT EXISTS field_mappings (
    mapping_id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES schema_tables(table_id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100),
    ontology_property VARCHAR(100),
    ontology_class VARCHAR(100),
    confidence_score FLOAT,
    is_primary_key BOOLEAN DEFAULT FALSE,
    is_nullable BOOLEAN DEFAULT TRUE,
    mapping_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(table_id, field_name)
);

-- Data Storage Table (JSONB for flexibility)
CREATE TABLE IF NOT EXISTS data_records (
    record_id SERIAL PRIMARY KEY,
    table_id INTEGER REFERENCES schema_tables(table_id) ON DELETE CASCADE,
    record_data JSONB NOT NULL,
    embedding vector(384),  -- Sentence transformer embedding dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Semantic Embeddings Table
CREATE TABLE IF NOT EXISTS semantic_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,  -- 'field', 'table', 'record', 'property'
    entity_id INTEGER NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entity_type, entity_id)
);

-- Query Cache Table
CREATE TABLE IF NOT EXISTS query_cache (
    cache_id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query_result JSONB,
    execution_time_ms FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_field_mappings_table ON field_mappings(table_id);
CREATE INDEX IF NOT EXISTS idx_field_mappings_property ON field_mappings(ontology_property);
CREATE INDEX IF NOT EXISTS idx_data_records_table ON data_records(table_id);
CREATE INDEX IF NOT EXISTS idx_data_records_jsonb ON data_records USING GIN (record_data);
CREATE INDEX IF NOT EXISTS idx_query_cache_hash ON query_cache(query_hash);

-- Vector similarity indexes (IVFFlat for pgvector)
CREATE INDEX IF NOT EXISTS idx_data_records_embedding
    ON data_records USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_semantic_embeddings_embedding
    ON semantic_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Helper function to compute cosine similarity
CREATE OR REPLACE FUNCTION cosine_similarity(a vector, b vector)
RETURNS FLOAT AS $$
BEGIN
    RETURN 1 - (a <=> b);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to find similar records by embedding
CREATE OR REPLACE FUNCTION find_similar_records(
    query_embedding vector,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE(
    record_id INTEGER,
    similarity FLOAT,
    record_data JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dr.record_id,
        cosine_similarity(dr.embedding, query_embedding) as similarity,
        dr.record_data
    FROM data_records dr
    WHERE dr.embedding IS NOT NULL
    ORDER BY dr.embedding <=> query_embedding
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Comments
COMMENT ON TABLE ontology_classes IS 'Stores ontology class definitions';
COMMENT ON TABLE ontology_properties IS 'Stores ontology property definitions';
COMMENT ON TABLE ontology_relationships IS 'Stores relationships between ontology classes';
COMMENT ON TABLE schema_tables IS 'Maps database tables to ontology classes';
COMMENT ON TABLE field_mappings IS 'Maps database fields to ontology properties (GNN predictions)';
COMMENT ON TABLE data_records IS 'Stores actual data records with semantic embeddings';
COMMENT ON TABLE semantic_embeddings IS 'Stores embeddings for semantic search';
COMMENT ON TABLE query_cache IS 'Caches frequently executed queries';
