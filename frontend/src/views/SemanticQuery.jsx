import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = '/api'

function SemanticQuery() {
  const [templates, setTemplates] = useState([])
  const [selectedTemplate, setSelectedTemplate] = useState(null)
  const [parameters, setParameters] = useState({})
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const response = await axios.get(`${API_URL}/query/templates`)
      setTemplates(response.data.templates)
      if (response.data.templates.length > 0) {
        setSelectedTemplate(response.data.templates[0])
      }
    } catch (err) {
      setError('Failed to load query templates')
    }
  }

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
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
          Semantic Query Engine
        </h2>
        <p style={{ color: '#6b7280', marginBottom: '24px' }}>
          Execute ontology-guided query templates (research-safe, no free-form NL→SQL)
        </p>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontWeight: '500', marginBottom: '8px' }}>
            Select Query Template
          </label>
          <select
            className="select"
            value={selectedTemplate?.id || ''}
            onChange={(e) => setSelectedTemplate(templates.find(t => t.id === e.target.value))}
          >
            {templates.map(template => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
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
      )}
    </div>
  )
}

export default SemanticQuery
