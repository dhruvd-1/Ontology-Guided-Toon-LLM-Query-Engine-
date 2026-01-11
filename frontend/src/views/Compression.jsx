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
      <div className="card">
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
          Token Compression
        </h2>
        <p style={{ color: '#6b7280', marginBottom: '24px' }}>
          Evaluate 4-layer ontology-aware compression on batch of records
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
          <div className="card">
            <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
              Compression Metrics
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
              <div style={{ textAlign: 'center', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#2563eb' }}>
                  {results.metrics.token_reduction_pct.toFixed(1)}%
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                  Token Reduction
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#059669' }}>
                  {results.metrics.compression_ratio.toFixed(2)}x
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                  Compression Ratio
                </div>
              </div>

              <div style={{ textAlign: 'center', padding: '16px', background: '#f9fafb', borderRadius: '8px' }}>
                <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#7c3aed' }}>
                  {results.num_records}
                </div>
                <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                  Records
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

            <div className="grid grid-2">
              {Object.entries(results.layers).map(([key, value]) => (
                <div key={key} style={{ padding: '12px', background: '#f9fafb', borderRadius: '6px' }}>
                  <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '4px' }}>
                    {key.replace(/_/g, ' ').replace(/\d+\s*/, '')}
                  </div>
                  <div style={{ fontSize: '13px', color: '#6b7280' }}>
                    {value}
                  </div>
                </div>
              ))}
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
