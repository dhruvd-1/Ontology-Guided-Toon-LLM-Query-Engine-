#!/bin/bash

# One-Click Database Setup for Demo
# Sets up PostgreSQL with pgvector, loads schema and sample data
# Total time: ~5 minutes

set -e  # Exit on error

echo "🚀 Setting up PostgreSQL database for demo..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Start PostgreSQL with pgvector
echo -e "${BLUE}Step 1: Starting PostgreSQL with pgvector...${NC}"
docker run -d \
    --name ontology-demo-db \
    -e POSTGRES_PASSWORD=demo123 \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_DB=ontology_storage \
    -p 5432:5432 \
    ankane/pgvector:latest

echo -e "${GREEN}✓ PostgreSQL container started${NC}"
echo ""

# Step 2: Wait for PostgreSQL to be ready
echo -e "${BLUE}Step 2: Waiting for PostgreSQL to be ready...${NC}"
echo "This may take 10-15 seconds..."
sleep 5

for i in {1..30}; do
    if docker exec ontology-demo-db pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PostgreSQL is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}PostgreSQL is taking longer than expected. Continuing anyway...${NC}"
    fi
    sleep 1
done
echo ""

# Step 3: Load database schema
echo -e "${BLUE}Step 3: Loading database schema (9 tables)...${NC}"
docker exec -i ontology-demo-db psql -U postgres -d ontology_storage < storage/models.sql
echo -e "${GREEN}✓ Schema loaded successfully${NC}"
echo ""

# Step 4: Load sample data
echo -e "${BLUE}Step 4: Loading sample data from JSON files...${NC}"
python3 load_demo_data.py
echo -e "${GREEN}✓ Sample data loaded${NC}"
echo ""

# Step 5: Start Adminer (web-based database viewer)
echo -e "${BLUE}Step 5: Starting Adminer (database viewer)...${NC}"
docker run -d \
    --name adminer-viewer \
    --link ontology-demo-db:db \
    -p 8080:8080 \
    adminer:latest

echo -e "${GREEN}✓ Adminer started${NC}"
echo ""

# Success message
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓✓✓ Database setup complete! ✓✓✓${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📊 Database Info:${NC}"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: ontology_storage"
echo "   Username: postgres"
echo "   Password: demo123"
echo ""
echo -e "${BLUE}🌐 Open Database Viewer:${NC}"
echo "   URL: http://localhost:8080"
echo ""
echo -e "${YELLOW}📝 To login to Adminer:${NC}"
echo "   System: PostgreSQL"
echo "   Server: db"
echo "   Username: postgres"
echo "   Password: demo123"
echo "   Database: ontology_storage"
echo ""
echo -e "${BLUE}🔍 Quick commands:${NC}"
echo "   View tables: docker exec -it ontology-demo-db psql -U postgres -d ontology_storage -c '\dt'"
echo "   Stop database: docker stop ontology-demo-db adminer-viewer"
echo "   Remove database: docker rm ontology-demo-db adminer-viewer"
echo ""
echo -e "${GREEN}Ready for your demo! 🎉${NC}"
