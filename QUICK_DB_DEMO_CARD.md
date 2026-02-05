# 🎯 Quick Database Demo Card - Keep This Open!

## 🚀 Setup (Run Before Demo)
```bash
chmod +x setup_database.sh
./setup_database.sh
# Wait for "Ready for your demo! 🎉"
```

## 🌐 Access Points
- **Adminer URL:** http://localhost:8080
- **Login:** System=PostgreSQL, Server=db, User=postgres, Pass=demo123, DB=ontology_storage

## 📊 Tables to Show Teacher

| Table | What to Say | Column to Highlight |
|-------|-------------|---------------------|
| **ontology_classes** | "Our 18 semantic classes" | `properties` (JSONB) |
| **data_records** | "Actual data with JSONB" | `data` (JSONB) + `embedding` (VECTOR) |
| **ontology_relationships** | "Formal relationships between classes" | `source_class`, `target_class` |
| **field_mappings** | "GNN predictions with confidence" | `confidence_score` |

## 💬 Demo Script (5 minutes)

### 1. Show Tables (30 sec)
```
"I'm using PostgreSQL with pgvector for hybrid SQL+NoSQL+Vector search"
[Open Adminer, show table list]
```

### 2. Show JSONB (2 min)
```
Click: data_records → Select → Click any cell in 'data' column
"This JSONB column stores flexible JSON documents while maintaining SQL queryability"
```

### 3. Run Live Query (2 min)
```
Click: "SQL command" → Paste this:

SELECT
    data->>'fname' as name,
    data->>'email_addr' as email,
    data->>'tier_type' as tier
FROM data_records
WHERE data->>'tier_type' = 'platinum'
LIMIT 5;

"See? SQL querying inside JSON documents - best of both worlds!"
```

### 4. Show Vector Column (30 sec)
```
Back to data_records table structure
"The embedding column is vector(384) - for semantic similarity search"
```

## 🎤 Key Talking Points

### SQL Part
- "Traditional relational tables with foreign keys and indexes"
- "ACID guarantees for data consistency"
- "Proper normalization for ontology structure"

### NoSQL Part
- "JSONB columns for flexible document storage"
- "Each class can have different properties"
- "Query inside JSON with SQL: `data->>'field_name'`"

### Why Hybrid?
- "Ontology needs structure (SQL) but also flexibility (NoSQL)"
- "PostgreSQL JSONB gives us both in one database"
- "Plus vector search via pgvector extension"

## 📝 Backup Queries (If Teacher Asks)

### Show Ontology Count
```sql
SELECT
    'Classes' as type, COUNT(*) as count FROM ontology_classes
UNION ALL
SELECT 'Properties', COUNT(*) FROM ontology_properties
UNION ALL
SELECT 'Relationships', COUNT(*) FROM ontology_relationships;
```

### Show JSONB Keys
```sql
SELECT DISTINCT jsonb_object_keys(data) as field_names
FROM data_records
WHERE table_id = 1;
```

### Show Field Mappings
```sql
SELECT field_name, property_name,
       ROUND(confidence_score * 100, 1) || '%' as confidence
FROM field_mappings
ORDER BY confidence_score DESC
LIMIT 10;
```

## ❓ Expected Questions & Answers

**Q: "Why PostgreSQL instead of MongoDB?"**
**A:** "We need both structured relationships (SQL) and flexible documents (JSONB). Plus ACID guarantees and vector search. PostgreSQL gives us all of this."

**Q: "What's the vector column for?"**
**A:** "Semantic embeddings for the GNN. Each record has a 384-dimensional vector enabling similarity search for intelligent query matching."

**Q: "Can you show the NoSQL feature?"**
[Run the platinum customers query above]

**Q: "How much data is in here?"**
**A:** "500+ sample records across 10 tables, plus full ontology (18 classes, 99 properties, 20 relationships)."

## 🛠️ Emergency Commands

### If something breaks:
```bash
# Restart database
docker restart ontology-demo-db adminer-viewer

# Check if running
docker ps | grep ontology-demo-db

# View logs
docker logs ontology-demo-db
```

### If need to reload data:
```bash
python3 load_demo_data.py
```

## ✅ Pre-Demo Checklist

5 minutes before demo:
- [ ] Run `docker ps` - both containers running?
- [ ] Open http://localhost:8080 - Adminer loads?
- [ ] Login to Adminer - credentials work?
- [ ] Click on `data_records` - data visible?
- [ ] Run one SQL query - works?
- [ ] Keep this card open in another window

## 🎯 Close Strong

**Final statement:**
> "So our database layer provides the foundation for the entire semantic pipeline: structured ontology in SQL, flexible data storage in JSONB, and vector embeddings for intelligent queries. All production-ready with ACID guarantees."

---

**Remember:** Confidence is key! You built a sophisticated database architecture. Own it! 🚀
