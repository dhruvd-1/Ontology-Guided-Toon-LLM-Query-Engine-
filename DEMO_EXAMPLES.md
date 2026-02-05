# Demo Examples - Copy & Paste During Presentation

Use these examples during your live demo to show real functionality.

---

## 📋 For Schema Mapping Demo (Step 2)

### Example 1: E-commerce Fields
Copy and paste this into the Schema Mapping interface:

```
cust_id
cust_nm
cust_email
ord_id
ord_dt
ord_val
ord_status
prod_id
prod_name
prod_desc
prod_price
cat_name
ship_addr
payment_method
```

**Expected mappings:**
- `cust_nm` → `customerName` (high confidence)
- `ord_dt` → `orderDate` (high confidence)
- `prod_price` → `productPrice` (high confidence)

---

### Example 2: More Cryptic Names
```
c_id
c_fn
c_ln
c_em
o_id
o_date
o_total
p_id
p_nm
p_val
cat_id
cat_desc
```

**What to say:**
"See how cryptic these are? But the GNN can still figure out that `c_fn` is probably `customerFirstName`, `o_total` is `orderTotal`, etc."

---

## 📊 For Compression Demo (Step 4)

### Example 1: Small Dataset (10 records)
Copy this into the Compression interface:

```json
[
  {
    "customerFirstName": "John",
    "customerLastName": "Doe",
    "customerEmail": "john.doe@email.com",
    "orderDate": "2024-01-15",
    "orderTotal": 1299.99,
    "productName": "iPhone 15 Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Phones"
  },
  {
    "customerFirstName": "Jane",
    "customerLastName": "Smith",
    "customerEmail": "jane.smith@email.com",
    "orderDate": "2024-01-16",
    "orderTotal": 1599.99,
    "productName": "MacBook Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Laptops"
  },
  {
    "customerFirstName": "Bob",
    "customerLastName": "Johnson",
    "customerEmail": "bob.j@email.com",
    "orderDate": "2024-01-17",
    "orderTotal": 899.99,
    "productName": "iPad Air",
    "productCategory": "Electronics",
    "productSubcategory": "Tablets"
  },
  {
    "customerFirstName": "Alice",
    "customerLastName": "Williams",
    "customerEmail": "alice.w@email.com",
    "orderDate": "2024-01-18",
    "orderTotal": 1299.99,
    "productName": "iPhone 15 Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Phones"
  },
  {
    "customerFirstName": "Charlie",
    "customerLastName": "Brown",
    "customerEmail": "charlie.b@email.com",
    "orderDate": "2024-01-19",
    "orderTotal": 2499.99,
    "productName": "MacBook Pro M3",
    "productCategory": "Electronics",
    "productSubcategory": "Laptops"
  },
  {
    "customerFirstName": "Diana",
    "customerLastName": "Martinez",
    "customerEmail": "diana.m@email.com",
    "orderDate": "2024-01-20",
    "orderTotal": 1299.99,
    "productName": "iPhone 15 Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Phones"
  },
  {
    "customerFirstName": "Edward",
    "customerLastName": "Garcia",
    "customerEmail": "edward.g@email.com",
    "orderDate": "2024-01-21",
    "orderTotal": 599.99,
    "productName": "AirPods Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Audio"
  },
  {
    "customerFirstName": "Fiona",
    "customerLastName": "Lee",
    "customerEmail": "fiona.l@email.com",
    "orderDate": "2024-01-22",
    "orderTotal": 1599.99,
    "productName": "MacBook Air",
    "productCategory": "Electronics",
    "productSubcategory": "Laptops"
  },
  {
    "customerFirstName": "George",
    "customerLastName": "Taylor",
    "customerEmail": "george.t@email.com",
    "orderDate": "2024-01-23",
    "orderTotal": 1299.99,
    "productName": "iPhone 15 Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Phones"
  },
  {
    "customerFirstName": "Hannah",
    "customerLastName": "Anderson",
    "customerEmail": "hannah.a@email.com",
    "orderDate": "2024-01-24",
    "orderTotal": 899.99,
    "productName": "iPad Pro",
    "productCategory": "Electronics",
    "productSubcategory": "Tablets"
  }
]
```

**Expected result:** ~33% compression

**What to say:**
"Notice we have 10 records. The system will:
1. Extract the schema once (all field names)
2. Use ontology IDs (single characters) for properties
3. Find patterns - 'iPhone 15 Pro' appears 4 times, 'Electronics' appears 10 times
4. Compress dates

Result: About 33% token reduction on this batch."

---

### Example 2: Large Dataset (50 records) - Better Compression

If you want to show better compression, use this script to generate 50 records:

```python
# Run this in Python to generate 50 records
import json

products = [
    ("iPhone 15 Pro", 1299.99, "Phones"),
    ("MacBook Pro", 1599.99, "Laptops"),
    ("iPad Air", 899.99, "Tablets"),
    ("AirPods Pro", 599.99, "Audio"),
    ("Apple Watch", 799.99, "Wearables")
]

first_names = ["John", "Jane", "Bob", "Alice", "Charlie", "Diana", "Edward", "Fiona", "George", "Hannah"]
last_names = ["Doe", "Smith", "Johnson", "Williams", "Brown", "Martinez", "Garcia", "Lee", "Taylor", "Anderson"]

records = []
for i in range(50):
    fn = first_names[i % 10]
    ln = last_names[i % 10]
    prod, price, cat = products[i % 5]

    records.append({
        "customerFirstName": fn,
        "customerLastName": ln,
        "customerEmail": f"{fn.lower()}.{ln.lower()}@email.com",
        "orderDate": f"2024-01-{(i % 28) + 1:02d}",
        "orderTotal": price,
        "productName": prod,
        "productCategory": "Electronics",
        "productSubcategory": cat
    })

print(json.dumps(records, indent=2))
```

**Expected result:** ~47% compression

**What to say:**
"With 50 records, we see the power of batch compression. The system extracts:
- 'Electronics' appears 50 times → becomes pattern @0
- 'customerEmail' → single character ID
- Date compression saves 2 chars per date

Result: Nearly 48% token reduction!"

---

## 🔍 For Semantic Query Demo (Step 3)

### Recommended Queries to Show

1. **"Customers Who Bought Electronics"**
   - Shows basic ontology reasoning
   - Demonstrates join generation

2. **"High-Value Customers"**
   - Shows aggregation
   - Demonstrates threshold filtering

3. **"Customers With Multiple Orders"**
   - Shows COUNT aggregation
   - Demonstrates grouping logic

**What to say for each:**

**Query 1:**
"This query finds all customers who bought electronics. The system:
- Recognizes 'Customer' and 'Electronics' as ontology classes
- Knows Electronics is a Category
- Generates joins: Customer → Order → Product → Category
- Filters where category = 'Electronics'"

**Query 2:**
"This finds high-value customers. The system:
- Aggregates all orders per customer
- Sums the total purchase value
- Filters for customers with total > $5000 (or whatever threshold)
- Returns sorted by total value"

**Query 3:**
"This finds repeat customers. The system:
- Groups orders by customer
- Counts orders per customer
- Filters for count > 1
- Shows only loyal customers"

---

## 🎯 Quick-Fire Comparisons

Use these to emphasize the value:

### Without This System:
```sql
-- Manual SQL - you need to know exact schema
SELECT c.cust_nm, c.cust_em
FROM cust_tbl c
JOIN ord_tbl o ON c.cust_id = o.cust_id_fk
JOIN prod_tbl p ON o.ord_id = p.ord_id_fk
JOIN cat_tbl ct ON p.cat_id = ct.cat_id
WHERE ct.cat_name = 'Electronics'
```

**Problems:**
- Need to know table abbreviations (cust_tbl, ord_tbl)
- Need to know field abbreviations (cust_nm, cust_em)
- Need to know foreign key relationships
- No semantic understanding

### With This System:
```
Query: "Customers who bought electronics"
↓
System automatically:
- Maps concepts to tables
- Generates proper joins
- Returns results
```

**Benefits:**
- Natural language concepts
- Automatic schema mapping
- Ontology-guided reasoning
- No SQL knowledge needed

---

## 💡 Talking Points for Each Component

### Ontology Viewer
"This is our semantic foundation - 18 classes, 99 properties, 20 relationships. Everything else builds on this."

### Schema Mapping
"The GNN uses graph structure to learn mappings. 65 nodes, 433 edges, 96-dimensional features. Automatically maps messy names to clean ontology."

### Semantic Queries
"Template-based for security, but uses ontology reasoning for intelligence. Understands class hierarchies and relationships."

### Compression
"Not just text compression - ontology-aware. Uses semantic IDs, structural flattening, and pattern extraction. 48% reduction at scale."

---

## 🎬 Demo Flow Cheat Sheet

1. **Landing** → Explain problem & solution
2. **Guided Demo** → Walk through 4 steps
3. **Step 1** → Show ontology (2 min)
4. **Step 2** → Demo schema mapping with example data (3 min)
5. **Step 3** → Run 2-3 semantic queries (3 min)
6. **Step 4** → Demo compression with JSON (2 min)
7. **Pipeline View** → Show animated flow (1 min)
8. **Wrap up** → Emphasize "one unified system" (1 min)

**Total:** 12-15 minutes

---

Good luck! 🚀
