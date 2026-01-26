import React, { useState, useEffect } from 'react'
import axios from 'axios'

const API_URL = '/api'

function OntologyViewer() {
  const [ontologyData, setOntologyData] = useState(null)
  const [selectedClass, setSelectedClass] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadOntology()
  }, [])

  const loadOntology = async () => {
    try {
      const response = await axios.get(`${API_URL}/ontology`)
      setOntologyData(response.data)
      if (response.data.classes && response.data.classes.length > 0) {
        setSelectedClass(response.data.classes[0].name)
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to load ontology')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="card">
        <p style={{ textAlign: 'center', color: '#6b7280' }}>Loading ontology...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">{error}</div>
      </div>
    )
  }

  if (!ontologyData) return null

  // Get properties for selected class
  const getPropertiesForClass = (className) => {
    if (!className || !ontologyData.classes) return []
    
    const classData = ontologyData.classes.find(c => c.name === className)
    if (!classData || !classData.properties) return []
    
    return classData.properties.map(propName => {
      const propDetails = ontologyData.properties?.[propName]
      return {
        name: propName,
        datatype: propDetails?.datatype || 'unknown',
        description: propDetails?.description || 'No description',
        constraints: classData.constraints?.[propName]
      }
    })
  }

  // Get relationships involving selected class
  const getRelationshipsForClass = (className) => {
    if (!className || !ontologyData.relationships) return []
    
    return ontologyData.relationships.filter(rel => 
      rel.source === className || rel.target === className
    )
  }

  // Get connected classes for graph visualization
  const getConnectedClasses = (className) => {
    if (!className || !ontologyData.relationships) return []
    
    const connections = new Set()
    ontologyData.relationships.forEach(rel => {
      if (rel.source === className) connections.add(rel.target)
      if (rel.target === className) connections.add(rel.source)
    })
    
    return Array.from(connections)
  }

  const selectedClassProperties = selectedClass ? getPropertiesForClass(selectedClass) : []
  const selectedClassRelationships = selectedClass ? getRelationshipsForClass(selectedClass) : []
  const connectedClasses = selectedClass ? getConnectedClasses(selectedClass) : []

  return (
    <div>
      {/* Header Card */}
      <div className="card">
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Ontology Structure
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '14px' }}>
          Domain ontology defining semantic relationships
        </p>

        <div style={{ display: 'flex', gap: '32px', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
              {ontologyData.num_classes}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px', fontWeight: '500' }}>
              Classes
            </div>
          </div>
          <div style={{ width: '1px', height: '50px', background: 'var(--border)' }} />
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
              {ontologyData.num_properties}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px', fontWeight: '500' }}>
              Properties
            </div>
          </div>
          <div style={{ width: '1px', height: '50px', background: 'var(--border)' }} />
          <div>
            <div style={{ fontSize: '36px', fontWeight: '700', color: 'var(--primary)', lineHeight: '1' }}>
              {ontologyData.num_relationships}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '6px', fontWeight: '500' }}>
              Relationships
            </div>
          </div>
        </div>

        {ontologyData.metadata && (
          <div style={{ padding: '14px 18px', background: 'var(--surface-alt)', borderRadius: '8px', borderLeft: '3px solid var(--primary)' }}>
            <div style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)', marginBottom: '4px' }}>
              {ontologyData.metadata.name} • v{ontologyData.metadata.version}
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
              {ontologyData.metadata.description}
            </div>
          </div>
        )}
      </div>

      {/* Ontology Classes */}
      <div className="card">
        <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
          Ontology Classes
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
          Click a class to view its properties and relationships
        </p>

        <table>
          <thead>
            <tr>
              <th>Class Name</th>
              <th>Description</th>
              <th>Properties</th>
            </tr>
          </thead>
          <tbody>
            {ontologyData.classes.map((cls, index) => (
              <tr 
                key={index}
                style={{ 
                  cursor: 'pointer',
                  background: selectedClass === cls.name ? 'var(--surface-alt)' : 'transparent'
                }}
                onClick={() => setSelectedClass(cls.name)}
              >
                <td>
                  <strong style={{ color: 'var(--primary)', fontWeight: '600' }}>{cls.name}</strong>
                </td>
                <td style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                  {cls.description}
                </td>
                <td>
                  <span style={{ fontSize: '13px', color: 'var(--text-muted)', fontWeight: '500' }}>
                    {cls.num_properties} properties
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Dynamic Properties Panel */}
      <div className="card">
        <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
          {selectedClass ? `${selectedClass} Properties` : 'Class Properties'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
          {selectedClass 
            ? `Semantic properties for ${selectedClass}`
            : 'Select a class above to view properties'
          }
        </p>

        {selectedClass && selectedClassProperties.length > 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px' }}>
            {selectedClassProperties.map((prop, index) => (
              <div 
                key={index}
                style={{ 
                  padding: '14px 16px', 
                  background: 'var(--surface-alt)', 
                  borderRadius: '8px',
                  border: '1px solid var(--border)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <strong style={{ fontSize: '14px', color: 'var(--text-primary)', fontWeight: '600' }}>
                    {prop.name}
                  </strong>
                  <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'monospace', background: 'var(--surface)', padding: '2px 8px', borderRadius: '4px' }}>
                    {prop.datatype}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                  {prop.description}
                </p>
                {prop.constraints && (
                  <div style={{ fontSize: '11px', color: 'var(--primary)', marginTop: '8px', fontWeight: '500' }}>
                    {prop.constraints.type === 'enum' && `Enum: ${prop.constraints.values.join(', ')}`}
                    {prop.constraints.pattern && `Pattern: ${prop.constraints.pattern}`}
                    {prop.constraints.required && '✓ Required'}
                    {prop.constraints.min !== undefined && `Min: ${prop.constraints.min}`}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ 
            padding: '40px', 
            textAlign: 'center', 
            background: 'var(--surface-alt)', 
            borderRadius: '8px',
            color: 'var(--text-muted)',
            fontSize: '14px'
          }}>
            {selectedClass 
              ? 'No properties defined'
              : 'Select a class to view properties'
            }
          </div>
        )}
      </div>

      {/* Dynamic Relationships Panel */}
      <div className="card">
        <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
          {selectedClass ? `${selectedClass} Relationships` : 'Class Relationships'}
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
          {selectedClass 
            ? `Semantic connections involving ${selectedClass}`
            : 'Select a class above to view relationships'
          }
        </p>

        {selectedClass && selectedClassRelationships.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {selectedClassRelationships.map((rel, index) => {
              const isSource = rel.source === selectedClass
              
              return (
                <div 
                  key={index}
                  style={{ 
                    padding: '14px 18px', 
                    background: 'var(--surface-alt)', 
                    borderRadius: '8px', 
                    border: '1px solid var(--border)',
                    borderLeft: `3px solid var(--primary)`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
                      {rel.source}
                    </span>
                    <span style={{ color: 'var(--primary)', fontSize: '16px' }}>→</span>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-primary)' }}>
                      {rel.target}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: 'auto' }}>
                      {rel.cardinality}
                    </span>
                  </div>
                  <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: 0 }}>
                    {rel.description}
                  </p>
                </div>
              )
            })}
          </div>
        ) : (
          <div style={{ 
            padding: '40px', 
            textAlign: 'center', 
            background: 'var(--surface-alt)', 
            borderRadius: '8px',
            color: 'var(--text-muted)',
            fontSize: '14px'
          }}>
            {selectedClass 
              ? 'No relationships defined'
              : 'Select a class to view relationships'
            }
          </div>
        )}
      </div>

      {/* 2D Relationship Graph */}
      {selectedClass && connectedClasses.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
            Semantic Neighborhood Graph
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
            Visual representation of {selectedClass} and connected classes
          </p>

          <div style={{ 
            padding: '24px', 
            background: 'var(--surface-alt)', 
            borderRadius: '8px',
            minHeight: '300px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            border: '1px solid var(--border)'
          }}>
            {/* SVG Layer for all connections */}
            <svg 
              viewBox="0 0 400 300"
              preserveAspectRatio="xMidYMid meet"
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                pointerEvents: 'none',
                zIndex: 1
              }}
            >
              {/* Define arrowhead marker */}
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon points="0 0, 10 3.5, 0 7" fill="#94a3b8" />
                </marker>
              </defs>

              {/* Draw all connection lines */}
              {connectedClasses.map((connectedClass, index) => {
                const angle = (index / connectedClasses.length) * 2 * Math.PI - Math.PI / 2
                const radius = 120
                const x = Math.cos(angle) * radius
                const y = Math.sin(angle) * radius
                
                // SVG center coordinates
                const centerX = 200
                const centerY = 150
                const targetX = centerX + x
                const targetY = centerY + y
                
                // Find relationship
                const relationship = selectedClassRelationships.find(rel => 
                  (rel.source === selectedClass && rel.target === connectedClass) ||
                  (rel.target === selectedClass && rel.source === connectedClass)
                )
                
                // Determine direction: arrow points from source to target
                const isOutgoing = relationship && relationship.source === selectedClass
                
                // Calculate midpoint for label
                const midX = centerX + (x / 2)
                const midY = centerY + (y / 2)
                
                return (
                  <g key={`line-${index}`}>
                    {/* Directed line with arrow */}
                    <line
                      x1={isOutgoing ? centerX : targetX}
                      y1={isOutgoing ? centerY : targetY}
                      x2={isOutgoing ? targetX : centerX}
                      y2={isOutgoing ? targetY : centerY}
                      stroke="#94a3b8"
                      strokeWidth="2"
                      strokeDasharray="6,4"
                      markerEnd="url(#arrowhead)"
                    />
                    
                    {/* Relationship label at midpoint */}
                    {relationship && (
                      <text
                        x={midX}
                        y={midY - 6}
                        fontSize="11"
                        fill="#475569"
                        fontWeight="500"
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        {relationship.cardinality}
                      </text>
                    )}
                  </g>
                )
              })}
            </svg>

            {/* Center Node - Selected Class */}
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              padding: '20px 32px',
              background: 'linear-gradient(135deg, #2563eb, #1e40af)',
              color: 'white',
              borderRadius: '12px',
              fontWeight: 'bold',
              fontSize: '18px',
              boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)',
              zIndex: 10,
              border: '3px solid #1e40af'
            }}>
              {selectedClass}
            </div>

            {/* Connected Classes in a Circle */}
            {connectedClasses.map((connectedClass, index) => {
              const angle = (index / connectedClasses.length) * 2 * Math.PI - Math.PI / 2
              const radius = 120
              const x = Math.cos(angle) * radius
              const y = Math.sin(angle) * radius
              
              // Find relationship to show label
              const relationship = selectedClassRelationships.find(rel => 
                (rel.source === selectedClass && rel.target === connectedClass) ||
                (rel.target === selectedClass && rel.source === connectedClass)
              )
              
              return (
                <React.Fragment key={index}>
                  {/* Connected Node */}
                  <div style={{
                    position: 'absolute',
                    top: `calc(50% + ${y}px)`,
                    left: `calc(50% + ${x}px)`,
                    transform: 'translate(-50%, -50%)',
                    padding: '12px 20px',
                    background: 'white',
                    border: '2px solid #cbd5e1',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    color: '#475569',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    zIndex: 5,
                    textAlign: 'center',
                    minWidth: '100px'
                  }}>
                    {connectedClass}
                  </div>
                </React.Fragment>
              )
            })}
          </div>

          <div style={{ 
            marginTop: '12px', 
            padding: '10px', 
            background: '#f0fdf4', 
            borderRadius: '4px',
            border: '1px solid #bbf7d0',
            fontSize: '12px',
            color: '#166534'
          }}>
            <strong>📊 Graph Legend:</strong> Center node (blue) = Selected class • Outer nodes (gray) = Directly connected classes • Arrows show semantic direction • Labels indicate cardinality
          </div>
        </div>
      )}

      {/* Sample Properties */}
      {ontologyData.sample_properties && ontologyData.sample_properties.length > 0 && false && (
        <div className="card">
          <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px' }}>
            Sample Ontology Properties
          </h3>
          <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '16px' }}>
            Examples of semantic properties used for schema mapping
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {ontologyData.sample_properties.map((prop, index) => (
              <div 
                key={index}
                style={{ 
                  padding: '12px', 
                  background: '#f9fafb', 
                  borderRadius: '6px',
                  border: '1px solid #e5e7eb'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <strong style={{ fontSize: '14px', color: '#1f2937' }}>
                    {prop.name}
                  </strong>
                  <span style={{ fontSize: '12px', color: '#6b7280', fontFamily: 'monospace' }}>
                    {prop.datatype}
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: '#6b7280', margin: 0 }}>
                  {prop.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default OntologyViewer
