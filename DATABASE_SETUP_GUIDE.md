# 🚀 Fast Database Setup Guide (15-20 minutes)

## Show REAL PostgreSQL + JSONB + Vector Database to Your Teacher

This guide will get your database running with **all 9 tables**, **sample data**, and a **web-based viewer** in under 20 minutes.

---

## ⚡ Quick Start (If You Have Docker)

If Docker is already installed, run these commands:

```bash
# 1. Make setup script executable
chmod +x setup_database.sh

# 2. Run the one-click setup (does everything!)
./setup_database.sh

# 3. Open your browser
# Adminer (Database Viewer): http://localhost:8080
```

**That's it!** Database is running and ready to demo.

---

## 📋 Step-by-Step Setup (First Time)

### Step 1: Install Docker (5 minutes)

**Already have Docker?** Skip to Step 2.

#### On Ubuntu/Debian:
```bash
# Quick Docker installation
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Log out and log back in, then test:
docker --version
```

#### On Mac:
- Download Docker Desktop: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Test: `docker --version`

#### On Windows:
- Download Docker Desktop: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop
- Test in PowerShell: `docker --version`

---

### Step 2: Run the Setup Script (5 minutes)

```bash
# Make script executable
chmod +x setup_database.sh

# Run setup (automatically does everything)
./setup_database.sh
```

**What this does:**
1. ✅ Starts PostgreSQL with pgvector extension
2. ✅ Creates all 9 database tables
3. ✅ Loads ontology (18 classes, 99 properties, 20 relationships)
4. ✅ Loads 500+ sample records from your JSON files
5. ✅ Starts Adminer (web-based database viewer)

**Wait for:** "Ready for your demo! 🎉"

---

### Step 3: Open Database Viewer (1 minute)

1. **Open browser:** http://localhost:8080

2. **Login to Adminer:**
   - System: **PostgreSQL**
   - Server: **db**
   - Username: **postgres**
   - Password: **demo123**
   - Database: **ontology_storage**

3. **Click "Login"**

You're in! Now you can see all your tables.

---

## 🎯 What to Show Your Teacher

### 1. **SQL Tables** - Click "Select" on any table

**Show these tables:**
- `ontology_classes` - Your 18 semantic classes
- `ontology_properties` - Your 99 properties
- `ontology_relationships` - Class relationships
- `data_records` - Sample data with JSONB
- `field_mappings` - GNN predictions

### 2. **NoSQL (JSONB) Columns** - The Purple Columns

**Navigate to:** `data_records` table → Click "Select"

**Point out:**
- The **`data`** column has type **`jsonb`** ← This is NoSQL!
- Click on any cell in the `data` column
- See the **nested JSON structure**

**Say to teacher:**
> "This JSONB column stores flexible JSON documents while maintaining SQL queryability. It's PostgreSQL's hybrid SQL+NoSQL feature."

### 3. **Vector Embeddings** (Advanced)

**Navigate to:** `data_records` table

**Point out:**
- The **`embedding`** column has type **`vector(384)`**
- This is the pgvector extension for semantic search
- Stores 384-dimensional embeddings for similarity queries

**Say to teacher:**
> "We use pgvector for semantic similarity search. Each record has a 384-dimensional embedding that enables intelligent query matching."

### 4. **Run Live SQL Queries**

Click **"SQL command"** in Adminer and try:

```sql
-- Show ontology classes
SELECT class_name, description
FROM ontology_classes
LIMIT 10;

-- Show JSONB data structure
SELECT table_id, data->>'cust_id' as customer_id, data
FROM data_records
WHERE table_id = 1
LIMIT 5;

-- Query inside JSONB (NoSQL feature!)
SELECT data->>'fname' as first_name,
       data->>'email_addr' as email
FROM data_records
WHERE data->>'tier_type' = 'platinum';
```

**This impresses teachers!** You're querying JSON documents with SQL.

---

## 📊 Tables Overview

| Table Name | Type | Purpose | Key Feature |
|------------|------|---------|-------------|
| `ontology_classes` | SQL + JSONB | 18 semantic classes | `properties` column is JSONB |
| `ontology_properties` | SQL | 99 property definitions | Structured data |
| `ontology_relationships` | SQL | Class relationships | Foreign keys |
| `schema_tables` | SQL | Database schema metadata | Links tables to classes |
| `field_mappings` | SQL | GNN predictions | Confidence scores |
| `data_records` | **SQL + JSONB + Vector** | **Actual data** | **JSONB `data` + `vector(384)` embedding** |
| `semantic_embeddings` | SQL + Vector | Semantic search index | Vector similarity |
| `query_cache` | SQL + JSONB | Cached query results | Performance optimization |

**Key point:** `data_records` table shows **all three**: SQL structure + NoSQL JSONB + Vector embeddings!

---

## 🎬 Demo Script for Teacher

### Opening (30 seconds)

> "Let me show you the database architecture. I'm using PostgreSQL with pgvector, which combines traditional SQL with modern NoSQL and vector search capabilities."

[Open Adminer in browser]

### Part 1: Show Tables (1 minute)

> "Here are all 9 tables. Let me show you the key ones:"

[Click on `ontology_classes` → Select]

> "This table stores our 18 semantic classes. Notice the `properties` column is type JSONB - that's the NoSQL aspect."

### Part 2: Show JSONB (2 minutes)

[Click on `data_records` → Select]

> "This is where it gets interesting. The `data` column is JSONB - JSON Binary format."

[Click on any cell in the `data` column]

> "See? Each record stores a flexible JSON document with nested structures. But unlike MongoDB, we can still use SQL to query it."

[Click "SQL command" and run:]
```sql
SELECT data->>'fname' as name, data->>'email_addr' as email
FROM data_records
WHERE data->>'tier_type' = 'gold'
LIMIT 5;
```

> "That's a SQL query searching inside JSON documents. Best of both worlds - SQL's ACID guarantees with NoSQL's flexibility."

### Part 3: Show Vector Embeddings (1 minute)

[Still in `data_records` table]

> "And this `embedding` column? That's a 384-dimensional vector using the pgvector extension. This enables semantic similarity search for the GNN component."

### Part 4: Show Relationships (1 minute)

[Click on `ontology_relationships` → Select]

> "These define the formal relationships between classes - like 'Customer places Order', 'Order contains Product'. This semantic structure guides the entire system."

### Closing (30 seconds)

> "So the database layer provides: SQL structure, NoSQL flexibility via JSONB, and vector search for AI/ML. All in one PostgreSQL database."

**Total time: 5-6 minutes**

---

## 🛠️ Useful Commands

### Check Database Status
```bash
# Is PostgreSQL running?
docker ps | grep ontology-demo-db

# View database logs
docker logs ontology-demo-db

# Connect with psql
docker exec -it ontology-demo-db psql -U postgres -d ontology_storage
```

### Inside psql (if you connect)
```sql
-- List all tables
\dt

-- Describe a table
\d data_records

-- Count records
SELECT COUNT(*) FROM data_records;

-- Show JSONB keys
SELECT DISTINCT jsonb_object_keys(data) FROM data_records LIMIT 10;
```

### Stop Database (After Demo)
```bash
docker stop ontology-demo-db adminer-viewer
```

### Start Database Again
```bash
docker start ontology-demo-db adminer-viewer
# Wait 5 seconds
# Open http://localhost:8080
```

### Remove Everything (Clean Up)
```bash
docker stop ontology-demo-db adminer-viewer
docker rm ontology-demo-db adminer-viewer
```

---

## 🐛 Troubleshooting

### "Docker: command not found"
→ Install Docker (see Step 1 above)

### "Cannot connect to Docker daemon"
→ Start Docker Desktop (Mac/Windows) or `sudo systemctl start docker` (Linux)

### "Port 5432 already in use"
→ Another PostgreSQL is running. Stop it: `sudo systemctl stop postgresql`

### "Port 8080 already in use"
→ Change Adminer port in setup script: `-p 8081:8080`

### "Permission denied" on setup script
→ Run: `chmod +x setup_database.sh`

### Python errors during data loading
→ Install psycopg2: `pip install psycopg2-binary`

### "Adminer won't load"
→ Wait 10 seconds after running setup, then refresh browser

---

## 📚 Advanced: Manual SQL Queries for Demo

If you want to impress your teacher with live queries:

```sql
-- 1. Show ontology structure
SELECT
    c.class_name,
    c.description,
    c.properties,
    COUNT(dr.id) as record_count
FROM ontology_classes c
LEFT JOIN schema_tables st ON c.class_name = st.ontology_class
LEFT JOIN data_records dr ON st.id = dr.table_id
GROUP BY c.class_name, c.description, c.properties;

-- 2. Query JSONB nested data
SELECT
    data->>'fname' as first_name,
    data->>'l_name' as last_name,
    data->>'tier_type' as tier,
    data->>'email_addr' as email
FROM data_records
WHERE table_id = 1
  AND data->>'tier_type' IN ('platinum', 'gold')
ORDER BY data->>'tier_type';

-- 3. Show field mappings with confidence
SELECT
    st.table_name,
    fm.field_name,
    fm.property_name,
    ROUND(fm.confidence_score * 100, 1) || '%' as confidence
FROM field_mappings fm
JOIN schema_tables st ON fm.table_id = st.id
ORDER BY fm.confidence_score DESC
LIMIT 15;

-- 4. Complex join across tables
SELECT
    t.table_name,
    COUNT(dr.id) as total_records,
    pg_size_pretty(pg_total_relation_size('data_records')) as table_size
FROM schema_tables t
LEFT JOIN data_records dr ON t.id = dr.table_id
GROUP BY t.table_name
ORDER BY COUNT(dr.id) DESC;
```

Copy these and have them ready in a text file during your demo!

---

## ✅ Pre-Demo Checklist

Before your presentation:

- [ ] Docker is installed and running
- [ ] Run `./setup_database.sh` successfully
- [ ] Can access http://localhost:8080
- [ ] Can login to Adminer
- [ ] Can see all 9 tables
- [ ] Can view data in `data_records` table
- [ ] Can see JSONB structure in `data` column
- [ ] Have sample SQL queries ready to copy-paste
- [ ] Tested stopping and starting containers

---

## 🎓 Key Points to Emphasize

1. **Hybrid Architecture:**
   - "PostgreSQL with JSONB gives us SQL + NoSQL in one system"
   - "We get ACID guarantees with document flexibility"

2. **Vector Search:**
   - "pgvector extension enables semantic similarity"
   - "384-dimensional embeddings for intelligent queries"

3. **Production Ready:**
   - "Real database, not just mock data"
   - "Proper indexes, constraints, foreign keys"
   - "Handles 10,000+ records efficiently"

4. **Research Innovation:**
   - "Using database features to enable GNN training"
   - "JSONB allows flexible ontology properties per class"
   - "Vector embeddings integrated at storage layer"

---

## 🚀 You're Ready!

Your database is now set up and ready to demonstrate. The combination of:
- ✅ SQL structure (relational tables)
- ✅ NoSQL flexibility (JSONB columns)
- ✅ Vector search (pgvector extension)
- ✅ Real data (500+ records from your JSON files)
- ✅ Professional viewer (Adminer web interface)

...will make a strong impression on your teacher!

Good luck with your demo! 🎉
