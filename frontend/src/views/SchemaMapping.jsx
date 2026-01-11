import React, { useState } from 'react'
import axios from 'axios'

const API_URL = '/api'

function SchemaMapping() {
  const [fields, setFields] = useState([
    { table_name: 'customers', field_name: 'cust_id', data_type: 'VARCHAR(50)' },
    { table_name: 'customers', field_name: 'fname', data_type: 'VARCHAR(100)' },
    { table_name: 'customers', field_name: 'email_addr', data_type: 'VARCHAR(255)' }
  ])
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const addField = () => {
    setFields([...fields, { table_name: '', field_name: '', data_type: 'VARCHAR(255)' }])
  }

  const updateField = (index, key, value) => {
    const newFields = [...fields]
    newFields[index][key] = value
    setFields(newFields)
  }

  const removeField = (index) => {
    setFields(fields.filter((_, i) => i !== index))
  }

  const predictMappings = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/schema/predict`, {
        fields: fields,
        ontology_class: 'Customer'
      })

      setPredictions(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to predict mappings')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>
          Schema Mapping
        </h2>
        <p style={{ color: '#6b7280', marginBottom: '24px' }}>
          Map database schema fields to ontology properties using GNN predictions
        </p>

        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '500', marginBottom: '12px' }}>
            Database Fields
          </h3>

          {fields.map((field, index) => (
            <div key={index} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '12px', marginBottom: '12px' }}>
              <input
                type="text"
                className="input"
                placeholder="Table name"
                value={field.table_name}
                onChange={(e) => updateField(index, 'table_name', e.target.value)}
              />
              <input
                type="text"
                className="input"
                placeholder="Field name"
                value={field.field_name}
                onChange={(e) => updateField(index, 'field_name', e.target.value)}
              />
              <input
                type="text"
                className="input"
                placeholder="Data type"
                value={field.data_type}
                onChange={(e) => updateField(index, 'data_type', e.target.value)}
              />
              <button
                className="button"
                onClick={() => removeField(index)}
                style={{ background: '#ef4444' }}
              >
                Remove
              </button>
            </div>
          ))}

          <button className="button" onClick={addField} style={{ marginTop: '8px' }}>
            + Add Field
          </button>
        </div>

        <button
          className="button"
          onClick={predictMappings}
          disabled={loading || fields.length === 0}
          style={{ width: '100%' }}
        >
          {loading ? 'Predicting...' : 'Predict Ontology Mappings'}
        </button>

        {error && (
          <div className="error" style={{ marginTop: '16px' }}>
            {error}
          </div>
        )}
      </div>

      {predictions && (
        <div className="card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Prediction Results
          </h3>

          <div style={{ marginBottom: '16px' }}>
            <span className="badge badge-info">
              {predictions.num_fields} fields analyzed
            </span>
            <span className="badge badge-success" style={{ marginLeft: '8px' }}>
              Avg confidence: {(predictions.avg_confidence * 100).toFixed(1)}%
            </span>
          </div>

          <table>
            <thead>
              <tr>
                <th>Table</th>
                <th>Field Name</th>
                <th>Data Type</th>
                <th>Predicted Property</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {predictions.predictions.map((pred, index) => (
                <tr key={index}>
                  <td>{pred.table_name}</td>
                  <td><code>{pred.field_name}</code></td>
                  <td style={{ color: '#6b7280', fontSize: '13px' }}>{pred.data_type}</td>
                  <td>
                    <strong>{pred.predicted_property}</strong>
                    {pred.property_info && (
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
                        {pred.property_info.datatype} - {pred.property_info.description}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${pred.confidence > 0.7 ? 'badge-success' : 'badge-warning'}`}>
                      {(pred.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default SchemaMapping
