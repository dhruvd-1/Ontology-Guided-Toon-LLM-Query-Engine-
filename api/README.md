# FastAPI Backend - Ontology-Guided Semantic Storage

REST API for schema mapping, semantic queries, and token compression.

## Features

- **Schema Mapping:** Predict ontology property mappings for database fields
- **Semantic Queries:** Execute pre-defined query templates (research-safe)
- **Token Compression:** Evaluate 4-layer compression on batch records
- **Ontology API:** Get ontology metadata and structure

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **CORS** - Enabled for React frontend

## Installation

```bash
cd api

# Install dependencies
pip install fastapi uvicorn python-multipart
```

## Running

### Development Mode

```bash
python main.py
```

Server runs on: `http://localhost:8000`

### With Uvicorn Directly

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Endpoints

### Health Check

```
GET /
```

Returns API status and available endpoints.

### Ontology

```
GET /ontology
```

Get ontology metadata, classes, and properties.

**Response:**
```json
{
  "metadata": {...},
  "num_classes": 18,
  "num_properties": 99,
  "classes": [...],
  "sample_properties": [...]
}
```

### Schema Mapping

```
POST /schema/predict
```

Predict ontology property mappings for schema fields.

**Request:**
```json
{
  "fields": [
    {
      "table_name": "customers",
      "field_name": "cust_id",
      "data_type": "VARCHAR(50)"
    }
  ],
  "ontology_class": "Customer"
}
```

**Response:**
```json
{
  "num_fields": 1,
  "predictions": [
    {
      "field_name": "cust_id",
      "predicted_property": "customerId",
      "confidence": 0.85,
      "property_info": {...}
    }
  ],
  "avg_confidence": 0.85
}
```

### Query Templates

```
GET /query/templates
```

Get available semantic query templates.

**Response:**
```json
{
  "templates": [
    {
      "id": "customers_electronics",
      "name": "Customers Who Bought Electronics",
      "description": "...",
      "parameters": [],
      "example_sql": "SELECT ..."
    }
  ]
}
```

### Execute Query

```
POST /query/execute
```

Execute a semantic query template.

**Request:**
```json
{
  "query_template": "customers_electronics",
  "parameters": {}
}
```

**Response:**
```json
{
  "template": "customers_electronics",
  "status": "success",
  "num_results": 3,
  "results": [...]
}
```

### Compression Evaluation

```
POST /compression/evaluate
```

Evaluate token compression on batch of records.

**Request:**
```json
{
  "records": [
    {"id": "CUS-001", "name": "John", ...},
    {"id": "CUS-002", "name": "Jane", ...}
  ],
  "ontology_class": "Customer"
}
```

**Response:**
```json
{
  "num_records": 2,
  "original": {
    "chars": 150,
    "tokens": 45
  },
  "compressed": {
    "chars": 80,
    "tokens": 24
  },
  "metrics": {
    "token_reduction_pct": 46.7,
    "compression_ratio": 1.875
  },
  "layers": {...}
}
```

## CORS Configuration

CORS is enabled for React development servers:

```python
allow_origins=["http://localhost:3000", "http://localhost:5173"]
```

For production, update `allow_origins` to your frontend domain.

## Integration with Project Components

The API integrates with:

- **`ontology/`** - Ontology schema loader
- **`compression/compressor_v2.py`** - Advanced compressor
- **`compression/evaluate_compression.py`** - Compression evaluator
- **`semantic_query/`** - Query engine (placeholder for demo)
- **`gnn/`** - GNN models (placeholder for demo)

## Demo Mode

For demo purposes:
- Schema mapping uses heuristic matching (not trained GNN)
- Queries return mock results (no database connection)
- All compression is real and functional

## Production Deployment

### With Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### With Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY api/ /app/api/
COPY ontology/ /app/ontology/
COPY compression/ /app/compression/
RUN pip install fastapi uvicorn python-multipart
CMD ["python", "api/main.py"]
```

### Environment Variables

```bash
export API_PORT=8000
export API_HOST=0.0.0.0
export CORS_ORIGINS="https://yourfrontend.com"
```

## Testing

```bash
# Test with curl
curl http://localhost:8000/

# Test schema prediction
curl -X POST http://localhost:8000/schema/predict \
  -H "Content-Type: application/json" \
  -d '{
    "fields": [
      {"table_name": "customers", "field_name": "cust_id", "data_type": "VARCHAR"}
    ]
  }'
```

## Development Notes

### Adding New Endpoints

1. Define Pydantic model for request/response
2. Create endpoint function with decorator
3. Implement logic
4. Test with `/docs`

### Error Handling

```python
from fastapi import HTTPException

@app.post("/endpoint")
def endpoint():
    if error:
        raise HTTPException(status_code=400, detail="Error message")
    return {"result": "success"}
```

## License

MIT License - Research/College Project 2026
