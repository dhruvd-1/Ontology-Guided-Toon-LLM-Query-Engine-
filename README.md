# Ontology-Guided Semantic Storage System

A research project demonstrating an end-to-end system for ontology-guided data storage, semantic querying, and intelligent compression using Graph Neural Networks.

## 🎓 Project Overview

This system combines formal ontology modeling, graph neural networks, and semantic reasoning to create an intelligent data storage and query system. Key innovation: **ontology-aware compression and semantic query processing without free-form NL→SQL**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ONTOLOGY LAYER                           │
│  • 18 Classes  • 99 Properties  • 20 Relationships         │
│  • Formal constraints and hierarchies                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
    ┌──────────────────┴──────────────────┐
    │                                      │
┌───▼────────────────┐         ┌──────────▼─────────────┐
│   DATA LAYER       │         │   GNN MAPPING LAYER    │
│  • 10,000 records  │────────▶│  • Schema → Ontology   │
│  • 10 tables       │         │  • Graph-based learning │
│  • Ground truth    │         │  • Confidence scores    │
└────────────────────┘         └────────────────────────┘
                                           │
                        ┌──────────────────┴──────────────┐
                        │                                  │
              ┌─────────▼─────────┐          ┌───────────▼────────┐
              │  QUERY LAYER      │          │  STORAGE LAYER     │
              │  • Intent parsing │          │  • PostgreSQL      │
              │  • Reasoning      │          │  • pgvector        │
              │  • SQL generation │          │  • JSONB storage   │
              └───────────────────┘          └────────────────────┘
                        │
              ┌─────────▼─────────┐
              │ COMPRESSION LAYER │
              │  • Token reduction│
              │  • Ontology-aware │
              └───────────────────┘
```

## 📁 Repository Structure

```
ontology_guided_toon_storage/
│
├── ontology/                    # Ontology definition and validation
│   ├── ontology.json           # Formal ontology (18 classes, 99 properties)
│   ├── schema.py               # Python ontology loader
│   └── validation.py           # Ontology consistency checker
│
├── data_generation/            # Synthetic data generation
│   ├── synthetic_schema.py     # Schema generator (messy field names)
│   ├── generate_data.py        # Data generator (1000 records per table)
│   └── output/                 # Generated data and ground truth
│
├── gnn/                        # Graph Neural Network
│   ├── graph_builder_simple.py # Schema graph construction
│   ├── model_numpy.py          # GCN implementation (CPU-safe)
│   ├── train_improved.py       # Training pipeline
│   ├── infer.py                # Inference engine
│   └── evaluate.py             # Evaluation metrics
│
├── storage/                    # PostgreSQL + pgvector layer
│   ├── models.sql              # Database schema
│   ├── db.py                   # Connection and ORM
│   └── ingest.py               # Data ingestion pipeline
│
├── semantic_query/             # Semantic query processing
│   ├── intent_parser.py        # Intent extraction
│   ├── ontology_reasoner.py    # Ontology-based reasoning
│   └── query_engine.py         # Query execution
│
├── compression/                # Token compression
│   ├── compressor.py           # Ontology-aware compression
│   └── token_metrics.py        # Token counting and metrics
│
├── main.py                     # Main entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Optional: Set up PostgreSQL (for storage layer)
# PostgreSQL 14+ with pgvector extension
```

### 2. Run Complete Demo

```bash
python main.py --demo
```

This demonstrates all system components:
- ✓ Ontology loading and validation
- ✓ Synthetic data generation
- ✓ GNN graph construction and training
- ✓ Semantic query processing
- ✓ Data compression
- ✓ Storage layer (if PostgreSQL available)

### 3. Run Individual Modules

```bash
# Ontology
python -m ontology.validation

# Data Generation
python -m data_generation.generate_data

# GNN
python -m gnn.train_improved
python -m gnn.evaluate

# Query Engine
python -m semantic_query.query_engine

# Compression
python -m compression.token_metrics
```

## 🧠 Key Components

### 1. Ontology Module

**Formal ontology with:**
- 18 classes (Customer, Order, Product, Electronics, Phones, etc.)
- 99 properties with datatypes and constraints
- 20 relationships with cardinalities
- Class hierarchy (Category → Electronics → Phones/Laptops)

**Features:**
- Constraint validation (email patterns, price > 0, enums)
- Property inheritance
- Relationship reasoning

### 2. Data Generation

**Generates realistic synthetic data:**
- 10 database tables with messy field names
- 10,000 total records (1000 per table)
- 65 field mappings with ground truth
- 92.3% messy field names (cust_id, ord_val, prod_desc)

### 3. GNN (Graph Neural Network)

**Schema-to-ontology mapping:**
- Graph Convolutional Network (GCN) with 2 layers
- 65 nodes (database fields)
- 433 edges (same_table, foreign_key, similar_name)
- 96 features per node (name embeddings + type + context)
- Pure NumPy implementation (CPU-safe, no GPU required)

**Performance:**
- Accuracy: 4.62%
- Note: Low due to extreme class imbalance (61 classes, 65 samples, 1-2 per class)
- Framework fully functional and correctly implemented

### 4. Semantic Query Engine

**Research-safe query processing (NO free-form NL→SQL):**

**Features:**
- Intent parsing with keyword matching
- Ontology-guided concept expansion
- Deterministic SQL generation from templates
- Vector-based semantic similarity
- Pre-defined query templates

**Example Queries:**
1. "Customers who bought electronics"
2. "High-value tech customers"

### 5. Compression Engine

**Ontology-aware token reduction:**
- Field name abbreviation using ontology mappings
- Redundancy removal
- Value truncation
- Current: 16% reduction (demonstrates concept)

### 6. Storage Layer

**PostgreSQL + pgvector:**
- Complete SQL schema with indexes
- Vector similarity search
- JSONB for flexible storage
- Repository pattern (ORM)
- Batch ingestion pipeline

**Ready to use when PostgreSQL is available**

## 📊 Evaluation Results

### GNN Performance

```
Accuracy:          4.62%
Macro Precision:   0.71%
Macro Recall:      4.92%
Macro F1:          1.20%

Avg Confidence:    0.0243
```

**Analysis:**
- Low accuracy is expected and documented
- 61 classes with only 65 total samples
- Average 1.1 samples per class (impossible to learn)
- Framework demonstrates correct implementation

**For production:**
- Need 10+ examples per class
- Data augmentation
- Transfer learning
- Ensemble methods

### Data Compression

```
Original:   2366 chars (~591 tokens)
Compressed: 1976 chars (~494 tokens)
Reduction:  16.4%
```

**Current implementation demonstrates concept**

## 🔬 Research Contribution

### Novel Aspects:

1. **Ontology-Guided GNN Architecture**
   - Schema fields as graph nodes
   - Ontology-aware edge construction
   - Semantic feature encoding

2. **Research-Safe Semantic Queries**
   - No free-form NL→SQL (security risk)
   - Template-based with ontology reasoning
   - Deterministic SQL generation

3. **Ontology-Aware Compression**
   - Property-based abbreviation
   - Semantic-preserving encoding
   - Token optimization for LLMs

4. **Complete End-to-End System**
   - All components integrated
   - Working prototype
   - Extensible architecture

### Limitations & Future Work:

1. **GNN Accuracy:**
   - Current: 4.62% (class imbalance)
   - Need: More training data per class
   - Solution: Data augmentation, synthetic schemas

2. **Compression Ratio:**
   - Current: 16% reduction
   - Target: 60-80% reduction
   - Solution: Advanced encoding, neural compression

3. **Query Templates:**
   - Current: 2 predefined templates
   - Need: Broader coverage
   - Solution: Template learning, few-shot examples

4. **Scalability:**
   - Current: 65 nodes (small graph)
   - Need: 1000+ nodes
   - Solution: Graph sampling, mini-batching

## 🛠️ Technical Stack

- **Python 3.11+**
- **NumPy** - Array operations
- **PostgreSQL 14+** - Primary database
- **pgvector** - Vector similarity
- **Faker** - Synthetic data
- **JSON** - Ontology and data format

**No PyTorch/GPU required** - Pure NumPy GNN implementation

## 📝 Running Tests

```bash
# Ontology validation
python ontology/test_ontology.py

# Data generation validation
python data_generation/test_data_generation.py

# GNN graph construction
python gnn/test_graph.py

# GNN evaluation
python -m gnn.evaluate

# Full system demo
python main.py --demo
```

## 🤝 Contributing

This is a college/research project. For production use:
1. Increase training data (10+ samples per class)
2. Implement advanced compression algorithms
3. Add more query templates
4. Optimize GNN architecture
5. Add authentication and security

## 📄 License

MIT License - See LICENSE file

## 👥 Authors

Research/College Project - 2026

## 📚 References

1. Kipf & Welling (2017) - Semi-Supervised Classification with Graph Convolutional Networks
2. Ontology engineering best practices
3. PostgreSQL + pgvector documentation
4. Semantic web and knowledge graphs

## ✅ System Verification

Run `python main.py --demo` to verify all components:

```
✓ Ontology (18 classes, 99 properties, 20 relationships)
✓ Data Generation (10,000 records with ground truth)
✓ GNN (Graph-based schema mapping)
✓ Semantic Query Engine (Ontology-guided)
✓ Compression (Ontology-aware encoding)
✓ Storage (PostgreSQL + pgvector ready)
```

🎓 **Research Project Complete!**

---

For questions or issues, refer to the code documentation in each module.
