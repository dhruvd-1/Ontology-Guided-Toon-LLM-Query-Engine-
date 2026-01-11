"""
FastAPI Backend for Ontology-Guided Semantic Storage System

Provides REST endpoints for:
- Schema mapping (GNN predictions)
- Semantic queries
- Token compression

Frontend: React app
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ontology import get_ontology
from compression.compressor_v2 import AdvancedCompressor
from compression.evaluate_compression import CompressionEvaluator

app = FastAPI(
    title="Ontology-Guided Semantic Storage API",
    version="1.0.0",
    description="REST API for schema mapping, semantic queries, and compression"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
ontology = get_ontology()
compressor = AdvancedCompressor(ontology=ontology)
compression_evaluator = CompressionEvaluator()


# ============================================================================
# DATA MODELS
# ============================================================================

class SchemaField(BaseModel):
    table_name: str
    field_name: str
    data_type: str


class SchemaMappingRequest(BaseModel):
    fields: List[SchemaField]
    ontology_class: Optional[str] = "Unknown"


class QueryRequest(BaseModel):
    query_template: str
    parameters: Optional[Dict[str, Any]] = {}


class CompressionRequest(BaseModel):
    records: List[Dict[str, Any]]
    ontology_class: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """API root - health check"""
    return {
        "status": "online",
        "api": "Ontology-Guided Semantic Storage",
        "version": "1.0.0",
        "endpoints": {
            "/ontology": "Get ontology information",
            "/schema/predict": "Predict ontology mappings for schema fields",
            "/query/templates": "Get available query templates",
            "/query/execute": "Execute semantic query",
            "/compression/evaluate": "Evaluate compression on records",
        }
    }


@app.get("/ontology")
def get_ontology_info():
    """Get ontology metadata and structure"""
    return {
        "metadata": ontology.metadata,
        "num_classes": len(ontology.classes),
        "num_properties": len(ontology.properties),
        "num_relationships": len(ontology.relationships),
        "classes": [
            {
                "name": name,
                "description": cls.description,
                "num_properties": len(cls.properties)
            }
            for name, cls in ontology.classes.items()
        ],
        "sample_properties": [
            {
                "name": prop.name,
                "datatype": prop.datatype,
                "description": prop.description
            }
            for prop in list(ontology.properties.values())[:10]
        ]
    }


@app.post("/schema/predict")
def predict_schema_mappings(request: SchemaMappingRequest):
    """
    Predict ontology property mappings for schema fields

    For demo: Uses heuristic matching (in production: use trained GNN)
    """
    predictions = []

    for field in request.fields:
        # Heuristic matching (placeholder for GNN)
        field_lower = field.field_name.lower()

        # Try to find matching property
        best_match = None
        best_confidence = 0.0

        for prop_name in ontology.properties.keys():
            prop_lower = prop_name.lower()

            # Simple similarity scoring
            if prop_lower in field_lower or field_lower in prop_lower:
                confidence = 0.8  # High confidence for contains match
                if prop_lower == field_lower:
                    confidence = 0.95  # Very high for exact match

                if confidence > best_confidence:
                    best_match = prop_name
                    best_confidence = confidence

        if not best_match:
            # Fallback: pick first property with similar datatype
            for prop_name, prop in ontology.properties.items():
                if field.data_type.upper() in prop.datatype.upper():
                    best_match = prop_name
                    best_confidence = 0.3
                    break

        predictions.append({
            "field_name": field.field_name,
            "table_name": field.table_name,
            "data_type": field.data_type,
            "predicted_property": best_match or "Unknown",
            "confidence": best_confidence,
            "property_info": {
                "name": best_match,
                "datatype": ontology.properties[best_match].datatype if best_match and best_match in ontology.properties else None,
                "description": ontology.properties[best_match].description if best_match and best_match in ontology.properties else None
            } if best_match else None
        })

    return {
        "num_fields": len(request.fields),
        "predictions": predictions,
        "avg_confidence": sum(p["confidence"] for p in predictions) / len(predictions) if predictions else 0
    }


@app.get("/query/templates")
def get_query_templates():
    """Get available semantic query templates"""
    return {
        "templates": [
            {
                "id": "customers_electronics",
                "name": "Customers Who Bought Electronics",
                "description": "Find all customers who purchased electronic products",
                "parameters": [],
                "example_sql": "SELECT DISTINCT c.* FROM customers c JOIN orders o ON c.id = o.customer_id JOIN order_items oi ON o.id = oi.order_id JOIN products p ON oi.product_id = p.id WHERE p.category = 'Electronics'"
            },
            {
                "id": "high_value_tech",
                "name": "High-Value Tech Customers",
                "description": "Find customers with high-value technology purchases",
                "parameters": ["min_amount"],
                "example_sql": "SELECT c.*, SUM(o.total_amount) as total_spent FROM customers c JOIN orders o ON c.id = o.customer_id JOIN order_items oi ON o.id = oi.order_id JOIN products p ON oi.product_id = p.id WHERE p.category IN ('Electronics', 'Computers') GROUP BY c.id HAVING total_spent > :min_amount"
            },
            {
                "id": "recent_orders",
                "name": "Recent Orders",
                "description": "Get recent orders within specified days",
                "parameters": ["days"],
                "example_sql": "SELECT * FROM orders WHERE order_date >= NOW() - INTERVAL ':days days'"
            }
        ]
    }


@app.post("/query/execute")
def execute_query(request: QueryRequest):
    """
    Execute semantic query

    Note: For demo, returns mock results (no real database connection)
    """
    template_id = request.query_template

    # Mock results for demo
    if template_id == "customers_electronics":
        return {
            "template": "customers_electronics",
            "status": "success",
            "execution_time_ms": 45,
            "num_results": 3,
            "results": [
                {"customer_id": "CUS-001", "first_name": "John", "last_name": "Doe", "total_orders": 5},
                {"customer_id": "CUS-002", "first_name": "Jane", "last_name": "Smith", "total_orders": 3},
                {"customer_id": "CUS-003", "first_name": "Bob", "last_name": "Johnson", "total_orders": 7},
            ],
            "note": "Demo results - connect real database for production"
        }
    elif template_id == "high_value_tech":
        min_amount = request.parameters.get("min_amount", 1000)
        return {
            "template": "high_value_tech",
            "status": "success",
            "execution_time_ms": 52,
            "parameters": {"min_amount": min_amount},
            "num_results": 2,
            "results": [
                {"customer_id": "CUS-001", "total_spent": 2500.00, "num_purchases": 5},
                {"customer_id": "CUS-005", "total_spent": 1800.00, "num_purchases": 3},
            ],
            "note": "Demo results - connect real database for production"
        }
    else:
        return {
            "template": template_id,
            "status": "success",
            "num_results": 0,
            "results": [],
            "note": "Template not implemented in demo"
        }


@app.post("/compression/evaluate")
def evaluate_compression(request: CompressionRequest):
    """
    Evaluate token compression on batch of records

    Returns metrics and before/after examples
    """
    records = request.records
    ontology_class = request.ontology_class

    if not records:
        raise HTTPException(status_code=400, detail="No records provided")

    # Compress
    original_json = json.dumps(records)
    compressed_batch = compressor.compress_batch(records, ontology_class, use_dictionary=True)
    compressed_json = json.dumps(compressed_batch)

    # Count tokens
    original_tokens = compression_evaluator.count_tokens(original_json)
    compressed_tokens = compression_evaluator.count_tokens(compressed_json)

    # Calculate metrics
    reduction_pct = ((original_tokens - compressed_tokens) / original_tokens) * 100 if original_tokens > 0 else 0

    return {
        "num_records": len(records),
        "original": {
            "chars": len(original_json),
            "tokens": original_tokens,
            "sample": records[0] if records else {}
        },
        "compressed": {
            "chars": len(compressed_json),
            "tokens": compressed_tokens,
            "structure": {
                "schema_size": len(compressed_batch.get("s", [])),
                "num_patterns": len(compressed_batch.get("p", {})),
                "dict_size": len(compressed_batch.get("v", {}))
            },
            "sample": compressed_json[:500] + "..." if len(compressed_json) > 500 else compressed_json
        },
        "metrics": {
            "char_reduction_pct": ((len(original_json) - len(compressed_json)) / len(original_json)) * 100,
            "token_reduction_pct": reduction_pct,
            "compression_ratio": original_tokens / compressed_tokens if compressed_tokens > 0 else 0
        },
        "layers": {
            "1_property_id_encoding": f"{len(compressor.property_to_id)} mappings",
            "2_structural_flattening": "Schema extracted",
            "3_value_compression": "Dates and timestamps compressed",
            "4_pattern_dictionary": f"{len(compressed_batch.get('p', {}))} patterns, {len(compressed_batch.get('v', {}))} dict entries"
        }
    }


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
