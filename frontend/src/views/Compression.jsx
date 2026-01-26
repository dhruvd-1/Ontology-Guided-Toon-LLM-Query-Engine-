import React, { useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const API_URL = '/api'

const SAMPLE_DATA = [
  { cust_id: 'CUS-000001', fname: 'John', lname: 'Doe', email: 'john@example.com', tier: 'gold' },
  { cust_id: 'CUS-000002', fname: 'Jane', lname: 'Smith', email: 'jane@example.com', tier: 'silver' },
  { cust_id: 'CUS-000003', fname: 'Bob', lname: 'Johnson', email: 'bob@example.com', tier: 'bronze' }
]

function Compression() {
  const [jsonInput, setJsonInput] = useState(JSON.stringify(SAMPLE_DATA, null, 2))
  const [ontologyClass, setOntologyClass] = useState('Customer')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const evaluateCompression = async () => {
    setLoading(true)
    setError(null)

    try {
      const records = JSON.parse(jsonInput)

      if (!Array.isArray(records)) {
        throw new Error('Input must be a JSON array of records')
      }

      const response = await axios.post(`${API_URL}/compression/evaluate`, {
        records: records,
        ontology_class: ontologyClass
      })

      setResults(response.data)
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError('Invalid JSON format')
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to evaluate compression')
      }
    } finally {
      setLoading(false)
    }
  }

  const chartData = results ? [
    {
      name: 'Characters',
      Original: results.original.chars,
      Compressed: results.compressed.chars
    },
    {
      name: 'Tokens',
      Original: results.original.tokens,
      Compressed: results.compressed.tokens
    }
  ] : []

  return (
    <div>
      {/* Why This Matters Section */}
      <div className="card" style={{ background: 'var(--surface-alt)', borderLeft: '4px solid var(--primary)' }}>
        <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '12px', color: 'var(--text-primary)' }}>
          Why Token Compression?
        </h3>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.8' }}>
          <div style={{ marginBottom: '6px' }}>
            <strong>•</strong> Reduces LLM context size and inference cost
          </div>
          <div style={{ marginBottom: '6px' }}>
            <strong>•</strong> Preserves semantic meaning using ontology definitions
          </div>
          <div style={{ marginBottom: '6px' }}>
            <strong>•</strong> Enables large-batch semantic queries
          </div>
          <div>
            <strong>•</strong> Improves scalability of AI-driven analytics
          </div>
        </div>
      </div>

      {/* Compression Pipeline */}
      <div className="card">
        <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Compression Pipeline
        </h3>
        <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '18px' }}>
          Each step uses ontology metadata to remove redundancy
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {[
            { num: 1, title: 'Ontology Class Identification' },
            { num: 2, title: 'Schema Extraction from JSON Records' },
            { num: 3, title: 'Semantic Property ID Encoding' },
            { num: 4, title: 'Structural Flattening of Repeated Keys' },
            { num: 5, title: 'Value & Pattern Compression' }
          ].map(step => (
            <div 
              key={step.num}
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '14px',
                padding: '12px 16px',
                background: 'var(--surface-alt)',
                borderRadius: '8px',
                border: '1px solid var(--border)'
              }}
            >
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
                {step.num}
              </div>
              <div style={{ fontSize: '14px', fontWeight: '500', color: 'var(--text-primary)' }}>
                {step.title}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Compression Evaluator
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '14px' }}>
          Evaluate ontology-aware compression on batch records
        </p>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontWeight: '500', marginBottom: '8px' }}>
            Ontology Class
          </label>
          <select className="select" value={ontologyClass} onChange={(e) => setOntologyClass(e.target.value)}>
            <option value="Customer">Customer</option>
            <option value="Order">Order</option>
            <option value="Product">Product</option>
          </select>
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontWeight: '500', marginBottom: '8px' }}>
            JSON Records (Array)
          </label>
          <textarea
            className="textarea"
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            placeholder='[{"field1": "value1", "field2": "value2"}, ...]'
            style={{ minHeight: '200px', fontFamily: 'monospace', fontSize: '13px' }}
          />
          <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '4px' }}>
            Paste a JSON array of records to compress
          </div>
        </div>

        <button
          className="button"
          onClick={evaluateCompression}
          disabled={loading}
          style={{ width: '100%' }}
        >
          {loading ? 'Evaluating...' : 'Evaluate Compression'}
        </button>

        {error && (
          <div className="error" style={{ marginTop: '16px' }}>
            {error}
          </div>
        )}
      </div>

      {results && (
        <>
          {/* LLM Impact Summary */}
          <div className="card">
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px', color: 'var(--text-primary)' }}>
              Token Reduction Impact
            </h3>
            
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ flex: 1, textAlign: 'center', padding: '20px', background: 'var(--surface-alt)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: '500' }}>
                  Before
                </div>
                <div style={{ fontSize: '40px', fontWeight: '700', color: 'var(--accent)', lineHeight: '1' }}>
                  {results.original.tokens}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                  tokens
                </div>
              </div>

              <div style={{ fontSize: '24px', color: 'var(--primary)', fontWeight: '700' }}>
                →
              </div>

              <div style={{ flex: 1, textAlign: 'center', padding: '20px', background: 'var(--surface-alt)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '8px', fontWeight: '500' }}>
                  After
                </div>
                <div style={{ fontSize: '40px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
                  {results.compressed.tokens}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                  tokens
                </div>
              </div>
            </div>

            <div style={{ 
              padding: '14px 18px', 
              background: 'var(--surface-alt)', 
              borderRadius: '8px',
              textAlign: 'center',
              borderLeft: '4px solid var(--primary)'
            }}>
              <div style={{ fontSize: '18px', fontWeight: '600', color: 'var(--text-primary)' }}>
                {results.metrics.token_reduction_pct.toFixed(1)}% reduction
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Lower context size, reduced LLM costs
              </div>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '20px', color: 'var(--text-primary)' }}>
              Compression Metrics
            </h3>

            <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
              <div style={{ flex: 1, textAlign: 'center', padding: '18px', background: 'var(--surface-alt)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
                  {results.metrics.token_reduction_pct.toFixed(1)}%
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px', fontWeight: '500' }}>
                  Token Reduction
                </div>
              </div>

              <div style={{ flex: 1, textAlign: 'center', padding: '18px', background: 'var(--surface-alt)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
                  {results.metrics.compression_ratio.toFixed(2)}x
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px', fontWeight: '500' }}>
                  Compression Ratio
                </div>
              </div>

              <div style={{ flex: 1, textAlign: 'center', padding: '18px', background: 'var(--surface-alt)', borderRadius: '8px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
                  {results.num_records}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px', fontWeight: '500' }}>
                  Records Processed
                </div>
              </div>
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Original" fill="#2563eb" />
                <Bar dataKey="Compressed" fill="#059669" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card">
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Compression Layers
            </h3>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
              Four-layer semantic compression pipeline with ontology-guided transformations
            </p>

            <div className="grid grid-2">
              {(() => {
                const layerDescriptions = {
                  'property_id_encoding': {
                    title: 'Property ID Encoding',
                    description: 'Long ontology property names → compact semantic IDs'
                  },
                  'structural_flattening': {
                    title: 'Structural Flattening',
                    description: 'Removes repeated keys across records'
                  },
                  'value_compression': {
                    title: 'Value Compression',
                    description: 'Compact encoding of dates and timestamps'
                  },
                  'pattern_dictionary': {
                    title: 'Pattern Dictionary',
                    description: 'Reuse of repeated string patterns'
                  }
                }

                return Object.entries(results.layers).map(([key, value]) => {
                  const cleanKey = key.replace(/\d+\s*/, '').trim()
                  const layerInfo = layerDescriptions[cleanKey] || {
                    title: key.replace(/_/g, ' '),
                    description: value
                  }

                  return (
                    <div key={key} style={{ 
                      padding: '14px', 
                      background: '#f9fafb', 
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb'
                    }}>
                      <div style={{ fontSize: '15px', fontWeight: '600', marginBottom: '6px', color: '#1f2937' }}>
                        {layerInfo.title}
                      </div>
                      <div style={{ fontSize: '13px', color: '#059669', marginBottom: '8px', fontStyle: 'italic' }}>
                        {layerInfo.description}
                      </div>
                      <div style={{ fontSize: '13px', color: '#6b7280' }}>
                        {value}
                      </div>
                    </div>
                  )
                })
              })()}
            </div>
          </div>

          {/* FEATURE 4 - Where This Is Used */}
          <div className="card" style={{ background: '#f0fdf4', border: '1px solid #86efac' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px', color: '#166534' }}>
              🔗 Used By
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '14px', color: '#065f46' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>✔</span>
                <span><strong>Semantic query results</strong> - Compress large result sets before LLM processing</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>✔</span>
                <span><strong>Ontology-aware analytics</strong> - Efficient batch processing of domain records</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>✔</span>
                <span><strong>LLM-based summarization</strong> - Reduce token usage for cost optimization</span>
              </div>
            </div>
          </div>

          <div className="grid grid-2">
            <div className="card">
              <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
                Original Sample
              </h3>
              <pre style={{
                background: '#f9fafb',
                padding: '12px',
                borderRadius: '6px',
                fontSize: '12px',
                overflow: 'auto',
                maxHeight: '200px'
              }}>
                {JSON.stringify(results.original.sample, null, 2)}
              </pre>
              <div style={{ marginTop: '12px', fontSize: '13px', color: '#6b7280' }}>
                <strong>{results.original.tokens}</strong> tokens • <strong>{results.original.chars}</strong> chars
              </div>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '12px' }}>
                Compressed Structure
              </h3>
              <pre style={{
                background: '#f9fafb',
                padding: '12px',
                borderRadius: '6px',
                fontSize: '12px',
                overflow: 'auto',
                maxHeight: '200px'
              }}>
                {results.compressed.sample}
              </pre>
              <div style={{ marginTop: '12px', fontSize: '13px', color: '#6b7280' }}>
                <strong>{results.compressed.tokens}</strong> tokens • <strong>{results.compressed.chars}</strong> chars
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Compression
