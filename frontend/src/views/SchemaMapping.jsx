import React, { useState } from 'react'
import axios from 'axios'
  
const API_URL = '/api'

function SchemaMapping() {
  const [fields, setFields] = useState([
    { table_name: 'customers', field_name: 'cust_email', data_type: 'VARCHAR(255)' }
  ])
  const [predictions, setPredictions] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [expandedRows, setExpandedRows] = useState({})
  const [acceptedMappings, setAcceptedMappings] = useState({}) // Track accepted mappings per field

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

  const toggleRow = (index) => {
    setExpandedRows(prev => ({
      ...prev,
      [index]: !prev[index]
    }))
  }

  const acceptMapping = (predIndex, property) => {
    setAcceptedMappings(prev => ({
      ...prev,
      [predIndex]: {
        property: property,
        timestamp: new Date().toISOString()
      }
    }))
  }

  const getDecisionStatus = (confidence) => {
    if (confidence >= 0.7) {
      return {
        status: 'High-confidence semantic alignment',
        icon: '✔',
        className: 'badge-success',
        color: '#059669'
      }
    } else {
      return {
        status: 'Ambiguous – human review recommended',
        icon: '⚠',
        className: 'badge-warning',
        color: '#d97706'
      }
    }
  }

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 0.6) {
      return { className: 'badge-success', icon: '🟢', label: 'High' }
    } else if (confidence >= 0.3) {
      return { className: 'badge-warning', icon: '🟡', label: 'Medium' }
    } else {
      return { className: 'badge-error', icon: '🔴', label: 'Low' }
    }
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
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Schema-to-Ontology Mapping
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '28px', fontSize: '14px' }}>
          Align database schema fields to semantic ontology properties
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
                style={{ background: 'var(--accent)' }}
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
          style={{ marginTop: '16px', width: '100%' }}
        >
          {loading ? 'Analyzing...' : '🔍 Predict Ontology Mappings'}
        </button>
      </div>

      {predictions && (
        <div className="card" style={{ marginTop: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: 'var(--text-primary)' }}>
            Ontology Alignment Results
          </h3>

          <div style={{ marginBottom: '16px', display: 'flex', gap: '8px' }}>
            <span style={{ fontSize: '13px', padding: '5px 12px', background: 'var(--surface-alt)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontWeight: '500' }}>
              {predictions.num_fields} fields analyzed
            </span>
            <span style={{ fontSize: '13px', padding: '5px 12px', background: 'var(--surface-alt)', border: '1px solid var(--border)', borderRadius: '6px', color: 'var(--text-primary)', fontWeight: '500' }}>
              Avg confidence: {(predictions.avg_confidence * 100).toFixed(1)}%
            </span>
          </div>

          <div style={{ marginBottom: '20px', padding: '12px 16px', background: 'var(--surface-alt)', borderLeft: '3px solid var(--primary)', borderRadius: '6px', fontSize: '13px', color: 'var(--text-secondary)' }}>
            Each field shows Top-3 ontology candidates ranked by confidence. Click any row for details.
          </div>

          {predictions.predictions.map((pred, predIndex) => {
            const isAccepted = acceptedMappings[predIndex]
            const decisionStatus = pred.best_prediction 
              ? getDecisionStatus(pred.best_prediction.confidence)
              : null

            return (
              <div key={predIndex} style={{ marginBottom: '16px', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' }}>
                {/* Decision Outcome Section */}
                {pred.best_prediction && (
                  <div style={{ 
                    padding: '12px 16px', 
                    background: 'var(--surface-alt)',
                    borderBottom: '1px solid var(--border)'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text-primary)' }}>
                          Decision Status:
                        </span>
                        <span className={`badge ${decisionStatus.className}`} style={{ fontSize: '13px' }}>
                          {decisionStatus.icon} {decisionStatus.status}
                        </span>
                      </div>
                      
                      {/* Accept Mapping Button - Only for high confidence */}
                      {!isAccepted && pred.best_prediction && pred.best_prediction.confidence >= 0.7 && (
                        <button
                          className="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            acceptMapping(predIndex, pred.best_prediction.property)
                          }}
                          style={{ 
                            padding: '8px 16px',
                            fontSize: '13px',
                            fontWeight: '600'
                          }}
                        >
                          ✓ Accept "{pred.best_prediction.property}"
                        </button>
                      )}
                      
                      {/* For ambiguous cases - show instruction */}
                      {!isAccepted && pred.best_prediction && pred.best_prediction.confidence < 0.7 && (
                        <div style={{ 
                          padding: '8px 14px',
                          background: 'var(--surface-alt)',
                          border: '1px solid var(--border)',
                          borderRadius: '6px',
                          fontSize: '12px',
                          color: 'var(--text-secondary)',
                          fontStyle: 'italic'
                        }}>
                          ↓ Expand to review Top-3 candidates
                        </div>
                      )}
                      
                      {/* Accepted Status */}
                      {isAccepted && (
                        <div style={{ 
                          padding: '8px 14px',
                          background: 'var(--surface-alt)',
                          borderLeft: '3px solid var(--primary)',
                          borderRadius: '6px',
                          fontSize: '13px',
                          color: 'var(--text-primary)',
                          fontWeight: '600'
                        }}>
                          ✓ Accepted: <strong>"{isAccepted.property}"</strong>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Main Row */}
                <div 
                style={{ 
                  padding: '16px', 
                  background: expandedRows[predIndex] ? 'var(--surface-alt)' : 'var(--surface)',
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
                onClick={() => toggleRow(predIndex)}
              >
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 1fr auto', gap: '16px', alignItems: 'center' }}>
                  {/* Input Field Info */}
                  <div>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '4px' }}>
                      {pred.table_name}
                    </div>
                    <code style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
                      {pred.field_name}
                    </code>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {pred.data_type}
                    </div>
                  </div>

                  {/* Best Prediction */}
                  {pred.best_prediction && (
                    <div>
                      <div style={{ fontSize: '16px', fontWeight: '600', color: 'var(--primary)', marginBottom: '4px' }}>
                        {pred.best_prediction.property}
                      </div>
                      {pred.best_prediction.property_info && (
                        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                          {pred.best_prediction.property_info.datatype} • {pred.best_prediction.property_info.description}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Confidence Badge */}
                  <div>
                    {pred.best_prediction && (() => {
                      const badge = getConfidenceBadge(pred.best_prediction.confidence)
                      return (
                        <div style={{ textAlign: 'center' }}>
                          <span className={`badge ${badge.className}`} style={{ fontSize: '14px', padding: '6px 12px' }}>
                            {badge.icon} {badge.label}
                          </span>
                          <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1f2937', marginTop: '4px' }}>
                            {(pred.best_prediction.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      )
                    })()}
                  </div>

                  {/* Expand Icon */}
                  <div style={{ textAlign: 'center', color: '#6b7280', fontSize: '20px' }}>
                    {expandedRows[predIndex] ? '▼' : '▶'}
                  </div>
                </div>

                {/* Confidence Label */}
                <div style={{ marginTop: '12px', fontSize: '13px', color: '#6b7280', fontStyle: 'italic' }}>
                  {pred.confidence_label}
                </div>
              </div>

              {/* Expanded Details */}
              {expandedRows[predIndex] && (
                <div style={{ padding: '16px', background: '#fafafa', borderTop: '1px solid #e5e7eb' }}>
                  <h4 style={{ fontSize: '14px', fontWeight: '600', marginBottom: '12px', color: '#374151' }}>
                    Top-3 Ontology Candidates (Ranked)
                  </h4>

                  {pred.top_candidates && pred.top_candidates.map((candidate, candIndex) => (
                    <div 
                      key={candIndex} 
                      style={{ 
                        padding: '12px', 
                        marginBottom: '8px', 
                        background: candIndex === 0 ? 'var(--surface-alt)' : 'var(--surface)',
                        border: `2px solid ${candIndex === 0 ? 'var(--primary)' : 'var(--border)'}`,
                        borderRadius: '6px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <span style={{ 
                            fontSize: '14px', 
                            fontWeight: '700', 
                            color: 'var(--surface)',
                            background: 'var(--primary)',
                            width: '26px',
                            height: '26px',
                            borderRadius: '50%',
                            display: 'inline-flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            flexShrink: 0
                          }}>
                            {candIndex + 1}
                          </span>
                          <div>
                            <div style={{ fontSize: '15px', fontWeight: '600', color: 'var(--text-primary)' }}>
                              {candidate.property}
                              {candIndex === 0 && (
                                <span style={{ marginLeft: '8px', fontSize: '12px', color: 'var(--primary)', fontWeight: 'normal' }}>
                                  Best Match
                                </span>
                              )}
                            </div>
                            {candidate.property_info && (
                              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                {candidate.property_info.datatype} • {candidate.property_info.description}
                              </div>
                            )}
                          </div>
                        </div>
                        <div>
                          {(() => {
                            const badge = getConfidenceBadge(candidate.confidence)
                            return (
                              <span className={`badge ${badge.className}`}>
                                {badge.icon} {(candidate.confidence * 100).toFixed(0)}%
                              </span>
                            )
                          })()}
                        </div>
                      </div>

                      {/* Reasoning */}
                      {candidate.reasoning && (
                        <div style={{ 
                          fontSize: '12px', 
                          color: 'var(--text-secondary)', 
                          background: 'var(--surface-alt)', 
                          padding: '8px 12px', 
                          borderRadius: '4px',
                          border: '1px solid var(--border)',
                          marginTop: '8px',
                          fontStyle: 'italic'
                        }}>
                          {candidate.reasoning}
                        </div>
                      )}

                      {/* Accept Button for Each Candidate */}
                      {!isAccepted && (
                        <button
                          className="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            acceptMapping(predIndex, candidate.property)
                          }}
                          style={{ 
                            marginTop: '8px',
                            padding: '8px 14px',
                            fontSize: '13px',
                            width: '100%'
                          }}
                        >
                          ✔ Accept "{candidate.property}" as semantic mapping
                        </button>
                      )}

                      {/* Show if this candidate was accepted */}
                      {isAccepted && isAccepted.property === candidate.property && (
                        <div style={{ 
                          marginTop: '8px',
                          padding: '8px 12px',
                          background: '#d1fae5',
                          border: '2px solid #059669',
                          borderRadius: '6px',
                          fontSize: '13px',
                          color: '#065f46',
                          fontWeight: '600',
                          textAlign: 'center'
                        }}>
                          ✓ This mapping was accepted by you
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )})}

          {/* Mapping Usage Context Section */}
          <div style={{ 
            marginTop: '24px', 
            padding: '16px 18px', 
            background: 'var(--surface-alt)', 
            borderLeft: '3px solid var(--primary)', 
            borderRadius: '8px',
            border: '1px solid var(--border)'
          }}>
            <h4 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '10px', color: 'var(--text-primary)' }}>
              Where Mappings Are Used
            </h4>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '14px' }}>
              Accepted schema-to-ontology mappings affect downstream components:
            </p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
              <div style={{ 
                padding: '12px 14px', 
                background: 'var(--surface)', 
                borderRadius: '6px',
                border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--primary)', marginBottom: '4px' }}>
                  Semantic Queries
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Translate natural language to SQL using ontology properties
                </div>
              </div>
              <div style={{ 
                padding: '12px 14px', 
                background: 'var(--surface)', 
                borderRadius: '6px',
                border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--primary)', marginBottom: '4px' }}>
                  Ontology Validation
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Validate schema constraints against ontology rules
                </div>
              </div>
              <div style={{ 
                padding: '12px 14px', 
                background: 'var(--surface)', 
                borderRadius: '6px',
                border: '1px solid var(--border)'
              }}>
                <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--primary)', marginBottom: '4px' }}>
                  Token Compression
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  Schema-aware 4-layer compression for LLM cost reduction
                </div>
              </div>
            </div>
            <div style={{ 
              marginTop: '12px', 
              fontSize: '12px',
              color: 'var(--text-secondary)',
              fontStyle: 'italic'
            }}>
              Mappings persist in the ontology graph and are used by the GNN model for future predictions
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SchemaMapping
