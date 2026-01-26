import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = '/api'

// Comprehensive query template catalog organized by semantic category
const QUERY_TEMPLATES = [
  // Customer-Centric Queries
  {
    id: 'customers_bought_electronics',
    name: 'Customers Who Bought Electronics',
    category: 'Customer-Centric Queries',
    description: 'Find all customers who have purchased products in the Electronics category',
    concepts: ['Customer', 'Order', 'Product', 'Category'],
    relationships: ['Customer → Order (one-to-many)', 'Order → Product (many-to-many)', 'Product → Category (many-to-one)'],
    mappings: [
      { concept: 'Customer', db: 'customers table' },
      { concept: 'Order', db: 'orders table' },
      { concept: 'Product', db: 'products table' },
      { concept: 'Category', db: 'categories.name = "Electronics"' }
    ],
    example_sql: `SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.email
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
WHERE cat.name = 'Electronics'`,
    parameters: []
  },
  {
    id: 'high_value_customers',
    name: 'High-Value Customers',
    category: 'Customer-Centric Queries',
    description: 'Identify customers with lifetime purchase value above threshold',
    concepts: ['Customer', 'Order', 'totalAmount'],
    relationships: ['Customer → Order (one-to-many)', 'Order has totalAmount property'],
    mappings: [
      { concept: 'Customer', db: 'customers table' },
      { concept: 'Order', db: 'orders table' },
      { concept: 'totalAmount', db: 'SUM(orders.total_amount)' }
    ],
    example_sql: `SELECT c.customer_id, c.first_name, c.last_name, 
       SUM(o.total_amount) as lifetime_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING SUM(o.total_amount) > 1000
ORDER BY lifetime_value DESC`,
    parameters: []
  },
  {
    id: 'customers_multiple_orders',
    name: 'Customers With Multiple Orders',
    category: 'Customer-Centric Queries',
    description: 'Find customers who have placed more than N orders',
    concepts: ['Customer', 'Order', 'orderCount'],
    relationships: ['Customer → Order (one-to-many)'],
    mappings: [
      { concept: 'Customer', db: 'customers table' },
      { concept: 'Order', db: 'orders table' },
      { concept: 'orderCount', db: 'COUNT(orders.order_id)' }
    ],
    example_sql: `SELECT c.customer_id, c.first_name, c.last_name,
       COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(o.order_id) > 3
ORDER BY order_count DESC`,
    parameters: []
  },
  {
    id: 'customers_no_recent_orders',
    name: 'Customers With No Recent Orders',
    category: 'Customer-Centric Queries',
    description: 'Identify inactive customers who have not ordered in the last 90 days',
    concepts: ['Customer', 'Order', 'orderDate'],
    relationships: ['Customer → Order (one-to-many)', 'Order has orderDate property'],
    mappings: [
      { concept: 'Customer', db: 'customers table' },
      { concept: 'Order', db: 'orders table' },
      { concept: 'orderDate', db: 'MAX(orders.order_date)' }
    ],
    example_sql: `SELECT c.customer_id, c.first_name, c.last_name, c.email,
       MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
HAVING MAX(o.order_date) < DATE_SUB(NOW(), INTERVAL 90 DAY) OR MAX(o.order_date) IS NULL`,
    parameters: []
  },
  {
    id: 'customers_by_tier',
    name: 'Customers By Membership Tier',
    category: 'Customer-Centric Queries',
    description: 'Retrieve customers filtered by membership tier level',
    concepts: ['Customer', 'CustomerTier'],
    relationships: ['Customer has customerTier property'],
    mappings: [
      { concept: 'Customer', db: 'customers table' },
      { concept: 'customerTier', db: 'customers.customer_tier column' }
    ],
    example_sql: `SELECT customer_id, first_name, last_name, email, customer_tier
FROM customers
WHERE customer_tier = 'gold'
ORDER BY registration_date DESC`,
    parameters: []
  },

  // Order & Transaction Queries
  {
    id: 'recent_orders',
    name: 'Recent Orders',
    category: 'Order & Transaction Queries',
    description: 'Retrieve all orders placed in the last 30 days',
    concepts: ['Order', 'orderDate', 'Customer'],
    relationships: ['Order has orderDate property', 'Customer → Order (one-to-many)'],
    mappings: [
      { concept: 'Order', db: 'orders table' },
      { concept: 'orderDate', db: 'orders.order_date column' },
      { concept: 'Customer', db: 'customers table' }
    ],
    example_sql: `SELECT o.order_id, o.order_date, o.total_amount, o.status,
       c.first_name, c.last_name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY o.order_date DESC`,
    parameters: []
  },
  {
    id: 'orders_above_threshold',
    name: 'Orders Above Value Threshold',
    category: 'Order & Transaction Queries',
    description: 'Find orders with total amount exceeding specified value',
    concepts: ['Order', 'totalAmount', 'Customer'],
    relationships: ['Order has totalAmount property', 'Customer → Order (one-to-many)'],
    mappings: [
      { concept: 'Order', db: 'orders table' },
      { concept: 'totalAmount', db: 'orders.total_amount column' },
      { concept: 'Customer', db: 'customers table' }
    ],
    example_sql: `SELECT o.order_id, o.order_date, o.total_amount,
       c.first_name, c.last_name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.total_amount > 500
ORDER BY o.total_amount DESC`,
    parameters: []
  },
  {
    id: 'orders_multiple_products',
    name: 'Orders Containing Multiple Products',
    category: 'Order & Transaction Queries',
    description: 'Identify orders with more than N distinct products',
    concepts: ['Order', 'Product', 'orderItems'],
    relationships: ['Order → Product (many-to-many via OrderItems)'],
    mappings: [
      { concept: 'Order', db: 'orders table' },
      { concept: 'Product', db: 'products table' },
      { concept: 'orderItems', db: 'order_items table (junction)' }
    ],
    example_sql: `SELECT o.order_id, o.order_date, o.total_amount,
       COUNT(DISTINCT oi.product_id) as product_count
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.order_date, o.total_amount
HAVING COUNT(DISTINCT oi.product_id) > 2
ORDER BY product_count DESC`,
    parameters: []
  },

  // Product & Category Queries
  {
    id: 'top_selling_products',
    name: 'Top-Selling Products',
    category: 'Product & Category Queries',
    description: 'Identify products with highest sales quantity',
    concepts: ['Product', 'orderItems', 'quantity'],
    relationships: ['Order → Product (many-to-many)', 'OrderItem has quantity property'],
    mappings: [
      { concept: 'Product', db: 'products table' },
      { concept: 'orderItems', db: 'order_items table' },
      { concept: 'quantity', db: 'SUM(order_items.quantity)' }
    ],
    example_sql: `SELECT p.product_id, p.product_name, p.price,
       SUM(oi.quantity) as total_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.price
ORDER BY total_sold DESC
LIMIT 10`,
    parameters: []
  },
  {
    id: 'products_by_category',
    name: 'Products By Category',
    category: 'Product & Category Queries',
    description: 'Retrieve all products within a specific category',
    concepts: ['Product', 'Category'],
    relationships: ['Product → Category (many-to-one)'],
    mappings: [
      { concept: 'Product', db: 'products table' },
      { concept: 'Category', db: 'categories table' }
    ],
    example_sql: `SELECT p.product_id, p.product_name, p.price, p.stock_quantity,
       c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE c.category_name = 'Electronics'
ORDER BY p.product_name`,
    parameters: []
  },
  {
    id: 'low_stock_products',
    name: 'Low-Stock Products',
    category: 'Product & Category Queries',
    description: 'Find products with inventory below reorder threshold',
    concepts: ['Product', 'stockQuantity'],
    relationships: ['Product has stockQuantity property'],
    mappings: [
      { concept: 'Product', db: 'products table' },
      { concept: 'stockQuantity', db: 'products.stock_quantity column' }
    ],
    example_sql: `SELECT product_id, product_name, stock_quantity, reorder_level
FROM products
WHERE stock_quantity < reorder_level
ORDER BY stock_quantity ASC`,
    parameters: []
  },

  // Revenue & Value Queries
  {
    id: 'revenue_by_category',
    name: 'Revenue By Category',
    category: 'Revenue & Value Queries',
    description: 'Calculate total revenue generated by each product category',
    concepts: ['Category', 'Product', 'Order', 'revenue'],
    relationships: ['Product → Category (many-to-one)', 'Order → Product (many-to-many)'],
    mappings: [
      { concept: 'Category', db: 'categories table' },
      { concept: 'Product', db: 'products table' },
      { concept: 'Order', db: 'orders table' },
      { concept: 'revenue', db: 'SUM(order_items.quantity * order_items.unit_price)' }
    ],
    example_sql: `SELECT c.category_name,
       SUM(oi.quantity * oi.unit_price) as total_revenue,
       COUNT(DISTINCT o.order_id) as order_count
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY c.category_name
ORDER BY total_revenue DESC`,
    parameters: []
  },
  {
    id: 'average_order_value',
    name: 'Average Order Value',
    category: 'Revenue & Value Queries',
    description: 'Calculate average order value across all transactions',
    concepts: ['Order', 'totalAmount', 'statistics'],
    relationships: ['Order has totalAmount property'],
    mappings: [
      { concept: 'Order', db: 'orders table' },
      { concept: 'totalAmount', db: 'orders.total_amount column' },
      { concept: 'statistics', db: 'AVG(), MIN(), MAX() aggregations' }
    ],
    example_sql: `SELECT 
       COUNT(*) as total_orders,
       AVG(total_amount) as avg_order_value,
       MIN(total_amount) as min_order_value,
       MAX(total_amount) as max_order_value,
       SUM(total_amount) as total_revenue
FROM orders
WHERE status = 'completed'`,
    parameters: []
  },

  // Operational / Temporal Queries
  {
    id: 'orders_last_n_days',
    name: 'Orders Placed in Last N Days',
    category: 'Operational / Temporal Queries',
    description: 'Retrieve orders within a specified time window',
    concepts: ['Order', 'orderDate', 'temporalFilter'],
    relationships: ['Order has orderDate property'],
    mappings: [
      { concept: 'Order', db: 'orders table' },
      { concept: 'orderDate', db: 'orders.order_date column' },
      { concept: 'temporalFilter', db: 'DATE_SUB(NOW(), INTERVAL N DAY)' }
    ],
    example_sql: `SELECT order_id, customer_id, order_date, total_amount, status
FROM orders
WHERE order_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY order_date DESC`,
    parameters: []
  },
  {
    id: 'customers_with_support_tickets',
    name: 'Customers With Recent Support Tickets',
    category: 'Operational / Temporal Queries',
    description: 'Find customers who have opened support tickets recently',
    concepts: ['Customer', 'SupportTicket', 'ticketDate'],
    relationships: ['Customer → SupportTicket (one-to-many)', 'SupportTicket has ticketDate property'],
    mappings: [
      { concept: 'Customer', db: 'customers table' },
      { concept: 'SupportTicket', db: 'support_tickets table' },
      { concept: 'ticketDate', db: 'support_tickets.created_date column' }
    ],
    example_sql: `SELECT c.customer_id, c.first_name, c.last_name, c.email,
       COUNT(st.ticket_id) as ticket_count,
       MAX(st.created_date) as last_ticket_date
FROM customers c
JOIN support_tickets st ON c.customer_id = st.customer_id
WHERE st.created_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY ticket_count DESC`,
    parameters: []
  }
]

// Define semantic reasoning details for each query template
const getSemanticPipeline = (templateId) => {
  const template = QUERY_TEMPLATES.find(t => t.id === templateId)
  if (!template) {
    // Default pipeline
    return {
      concepts: ['Customer', 'Order', 'Product'],
      relationships: ['Customer → Order', 'Order → Product'],
      mappings: [
        { concept: 'Customer', db: 'customers table' },
        { concept: 'Order', db: 'orders table' },
        { concept: 'Product', db: 'products table' }
      ]
    }
  }

  return {
    concepts: template.concepts,
    relationships: template.relationships,
    mappings: template.mappings
  }
}

function SemanticQuery() {
  const [templates] = useState(QUERY_TEMPLATES)
  const [selectedTemplate, setSelectedTemplate] = useState(QUERY_TEMPLATES[0])
  const [parameters, setParameters] = useState({})
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Group templates by category
  const templatesByCategory = templates.reduce((acc, template) => {
    const category = template.category
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(template)
    return acc
  }, {})

  const executeQuery = async () => {
    if (!selectedTemplate) return

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/query/execute`, {
        query_template: selectedTemplate.id,
        parameters: parameters
      })

      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to execute query')
    } finally {
      setLoading(false)
    }
  }

  const updateParameter = (param, value) => {
    setParameters({ ...parameters, [param]: value })
  }

  return (
    <div>
      <div className="card">
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Semantic Query Engine
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '20px', fontSize: '14px' }}>
          Execute ontology-guided query templates
        </p>
        <div style={{ 
          background: 'var(--surface-alt)', 
          padding: '12px 16px', 
          borderRadius: '6px', 
          borderLeft: '3px solid var(--primary)',
          fontSize: '13px',
          color: 'var(--text-secondary)',
          marginBottom: '24px'
        }}>
          Queries use ontology-guided reasoning, not free-form natural language
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontWeight: '600', marginBottom: '10px', color: 'var(--text-primary)', fontSize: '14px' }}>
            Query Template ({templates.length} available)
          </label>
          <select
            className="select"
            value={selectedTemplate?.id || ''}
            onChange={(e) => setSelectedTemplate(templates.find(t => t.id === e.target.value))}
          >
            {Object.entries(templatesByCategory).map(([category, categoryTemplates]) => (
              <optgroup key={category} label={category}>
                {categoryTemplates.map(template => (
                  <option key={template.id} value={template.id}>
                    {template.name}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {selectedTemplate && (
          <>
            <div className="card" style={{ background: '#f9fafb', marginBottom: '20px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
                Description
              </h4>
              <p style={{ fontSize: '14px', color: '#4b5563' }}>
                {selectedTemplate.description}
              </p>

              {selectedTemplate.example_sql && (
                <div style={{ marginTop: '16px' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
                    Generated SQL (Example)
                  </h4>
                  <pre style={{
                    background: 'white',
                    padding: '12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    overflow: 'auto',
                    border: '1px solid #e5e7eb'
                  }}>
                    {selectedTemplate.example_sql}
                  </pre>
                </div>
              )}
            </div>

            {selectedTemplate.parameters && selectedTemplate.parameters.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px' }}>
                  Parameters
                </h4>
                {selectedTemplate.parameters.map(param => (
                  <div key={param} style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>
                      {param}
                    </label>
                    <input
                      type="text"
                      className="input"
                      value={parameters[param] || ''}
                      onChange={(e) => updateParameter(param, e.target.value)}
                      placeholder={`Enter ${param}`}
                    />
                  </div>
                ))}
              </div>
            )}

            <button
              className="button"
              onClick={executeQuery}
              disabled={loading}
              style={{ width: '100%' }}
            >
              {loading ? 'Executing...' : 'Execute Query'}
            </button>
          </>
        )}

        {error && (
          <div className="error" style={{ marginTop: '16px' }}>
            {error}
          </div>
        )}
      </div>

      {results && (
        <>
          {/* Semantic Query Execution Pipeline */}
          {selectedTemplate && (
            <div className="card">
              <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                Query Execution Pipeline
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '24px' }}>
                How ontology-guided reasoning produces SQL
              </p>

              {(() => {
                const pipeline = getSemanticPipeline(selectedTemplate.id)
                
                return (
                  <>
                    {/* STEP 1 - User Intent */}
                    <div style={{ 
                      marginBottom: '16px', 
                      padding: '16px 18px', 
                      background: 'var(--surface-alt)', 
                      border: '1px solid var(--border)',
                      borderLeft: '3px solid var(--primary)',
                      borderRadius: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <div style={{ 
                          width: '28px', 
                          height: '28px', 
                          borderRadius: '50%', 
                          background: 'var(--primary)', 
                          color: 'white', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          fontWeight: '700',
                          fontSize: '14px',
                          flexShrink: 0
                        }}>
                          1
                        </div>
                        <h4 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)', margin: 0 }}>
                          User Intent (Semantic Level)
                        </h4>
                      </div>
                      
                      <div style={{ paddingLeft: '40px' }}>
                        <div style={{ 
                          padding: '10px 12px', 
                          background: 'var(--surface)', 
                          borderRadius: '6px',
                          marginBottom: '10px',
                          border: '1px solid var(--border)'
                        }}>
                          <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: '500', marginBottom: '4px' }}>
                            Selected Query:
                          </div>
                          <div style={{ fontSize: '15px', color: 'var(--text-primary)', fontWeight: '600' }}>
                            "{selectedTemplate.name}"
                          </div>
                        </div>
                        
                        <div style={{ 
                          fontSize: '12px',
                          color: 'var(--text-secondary)',
                          fontStyle: 'italic'
                        }}>
                          Query expressed using business meaning, not database schema
                        </div>
                      </div>
                    </div>

                    {/* STEP 2 - Ontology Reasoning */}
                    <div style={{ 
                      marginBottom: '16px', 
                      padding: '16px 18px', 
                      background: 'var(--surface-alt)', 
                      border: '1px solid var(--border)',
                      borderLeft: '3px solid var(--primary)',
                      borderRadius: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <div style={{ 
                          width: '28px', 
                          height: '28px', 
                          borderRadius: '50%', 
                          background: 'var(--primary)', 
                          color: 'white', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          fontWeight: '700',
                          fontSize: '14px',
                          flexShrink: 0
                        }}>
                          2
                        </div>
                        <h4 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)', margin: 0 }}>
                          Ontology-Guided Semantic Reasoning
                        </h4>
                      </div>
                      
                      <div style={{ paddingLeft: '40px' }}>
                        {/* Identified Concepts */}
                        <div style={{ marginBottom: '14px' }}>
                          <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                            Identified Ontology Concepts:
                          </div>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                            {pipeline.concepts.map((concept, idx) => (
                              <span 
                                key={idx}
                                style={{ 
                                  padding: '4px 10px',
                                  background: 'var(--surface)',
                                  border: '1px solid var(--border)',
                                  borderRadius: '4px',
                                  fontSize: '12px',
                                  color: 'var(--text-primary)',
                                  fontWeight: '500'
                                }}
                              >
                                {concept}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Relationships Traversed */}
                        <div style={{ marginBottom: '10px' }}>
                          <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                            Ontology Relationships:
                          </div>
                          <div style={{ 
                            padding: '10px 12px', 
                            background: 'var(--surface)', 
                            borderRadius: '6px',
                            border: '1px solid var(--border)'
                          }}>
                            {pipeline.relationships.map((rel, idx) => (
                              <div key={idx} style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: idx < pipeline.relationships.length - 1 ? '4px' : 0 }}>
                                → {rel}
                              </div>
                            ))}
                          </div>
                        </div>
                        
                        <div style={{ 
                          fontSize: '12px',
                          color: 'var(--text-secondary)',
                          fontStyle: 'italic'
                        }}>
                          Reasoning performed on ontology definitions, not database schema
                        </div>
                      </div>
                    </div>

                    {/* STEP 3 - SQL Compilation */}
                    <div style={{ 
                      marginBottom: '16px', 
                      padding: '16px 18px', 
                      background: 'var(--surface-alt)', 
                      border: '1px solid var(--border)',
                      borderLeft: '3px solid var(--primary)',
                      borderRadius: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        <div style={{ 
                          width: '28px', 
                          height: '28px', 
                          borderRadius: '50%', 
                          background: 'var(--primary)', 
                          color: 'white', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          fontWeight: '700',
                          fontSize: '14px',
                          flexShrink: 0
                        }}>
                          3
                        </div>
                        <h4 style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)', margin: 0 }}>
                          SQL Compilation (Derived from Ontology)
                        </h4>
                      </div>
                      
                      <div style={{ paddingLeft: '40px' }}>
                        {/* Mapping Table */}
                        <div style={{ marginBottom: '14px' }}>
                          <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                            Ontology → Database Mappings:
                          </div>
                          <table style={{ 
                            width: '100%', 
                            background: 'var(--surface)', 
                            borderRadius: '6px',
                            border: '1px solid var(--border)',
                            fontSize: '12px'
                          }}>
                            <thead>
                              <tr style={{ background: 'var(--surface-alt)' }}>
                                <th style={{ padding: '8px 10px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: '600', fontSize: '12px' }}>
                                  Ontology Concept
                                </th>
                                <th style={{ padding: '8px 10px', textAlign: 'left', color: 'var(--text-primary)', fontWeight: '600', fontSize: '12px' }}>
                                  Database Mapping
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {pipeline.mappings.map((mapping, idx) => (
                                <tr key={idx} style={{ borderTop: '1px solid var(--border)' }}>
                                  <td style={{ padding: '8px 10px', color: 'var(--text-primary)', fontWeight: '500' }}>
                                    {mapping.concept}
                                  </td>
                                  <td style={{ padding: '8px 10px', color: 'var(--text-secondary)', fontFamily: 'monospace', fontSize: '11px' }}>
                                    {mapping.db}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        {/* Generated SQL */}
                        {selectedTemplate.example_sql && (
                          <div style={{ marginBottom: '10px' }}>
                            <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '8px' }}>
                              Generated SQL:
                            </div>
                            <pre style={{
                              background: 'var(--secondary)',
                              color: 'var(--surface)',
                              padding: '12px',
                              borderRadius: '6px',
                              fontSize: '11px',
                              overflow: 'auto',
                              border: '1px solid var(--secondary-light)',
                              margin: 0
                            }}>
                              {selectedTemplate.example_sql}
                            </pre>
                          </div>
                        )}
                        
                        <div style={{ 
                          fontSize: '12px',
                          color: 'var(--text-secondary)',
                          fontStyle: 'italic'
                        }}>
                          SQL generated only after semantic reasoning is complete
                        </div>
                      </div>
                    </div>
                  </>
                )
              })()}
            </div>
          )}

          {/* Query Results */}
          <div className="card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Query Results
          </h3>

          <div style={{ marginBottom: '16px' }}>
            <span className="badge badge-success">
              {results.status}
            </span>
            <span className="badge badge-info" style={{ marginLeft: '8px' }}>
              {results.num_results} results
            </span>
            {results.execution_time_ms && (
              <span className="badge badge-info" style={{ marginLeft: '8px' }}>
                {results.execution_time_ms}ms
              </span>
            )}
          </div>

          {results.note && (
            <div style={{ background: '#fef3c7', border: '1px solid #fde68a', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '14px' }}>
              ℹ️ {results.note}
            </div>
          )}

          {results.results && results.results.length > 0 ? (
            <table>
              <thead>
                <tr>
                  {Object.keys(results.results[0]).map(key => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.results.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, i) => (
                      <td key={i}>
                        {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: '#6b7280' }}>No results found</p>
          )}
        </div>
        </>
      )}
    </div>
  )
}

export default SemanticQuery
