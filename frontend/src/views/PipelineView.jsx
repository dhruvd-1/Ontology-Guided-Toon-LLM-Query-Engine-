import React, { useState } from 'react'

function PipelineView({ onStepClick }) {
  const [hoveredStep, setHoveredStep] = useState(null)
  const [animating, setAnimating] = useState(false)

  const runAnimation = () => {
    setAnimating(true)
    setTimeout(() => setAnimating(false), 4000)
  }

  const steps = [
    {
      id: 'ontology',
      title: 'Formal Ontology',
      icon: '🎯',
      color: '#4f46e5',
      metrics: ['18 Classes', '99 Properties', '20 Relationships'],
      description: 'Semantic foundation with formal constraints'
    },
    {
      id: 'gnn',
      title: 'GNN Mapping',
      icon: '🧠',
      color: '#7c3aed',
      metrics: ['65 Nodes', '433 Edges', '96-dim Features'],
      description: 'Graph Neural Network for schema-to-ontology mapping'
    },
    {
      id: 'query',
      title: 'Semantic Queries',
      icon: '🔍',
      color: '#2563eb',
      metrics: ['15+ Templates', 'Ontology Reasoning', 'SQL Generation'],
      description: 'Research-safe template-based query engine'
    },
    {
      id: 'compression',
      title: 'Token Compression',
      icon: '⚡',
      color: '#059669',
      metrics: ['48% Reduction', '4 Layers', 'Reversible'],
      description: 'Ontology-aware intelligent compression'
    }
  ]

  return (
    <div>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <h2 style={{ fontSize: '32px', fontWeight: '800', marginBottom: '12px' }}>
          Complete Semantic Pipeline
        </h2>
        <p style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
          Four integrated stages transforming chaos into intelligence
        </p>
        <button
          className="button"
          onClick={runAnimation}
          disabled={animating}
          style={{
            background: animating ? 'var(--text-muted)' : 'linear-gradient(135deg, #4f46e5 0%, #059669 100%)',
            fontSize: '16px',
            padding: '12px 28px'
          }}
        >
          {animating ? '⚡ Running Pipeline...' : '▶ Run Complete Pipeline'}
        </button>
      </div>

      {/* Pipeline Visualization */}
      <div style={{
        position: 'relative',
        padding: '40px 20px',
        background: 'var(--surface)',
        borderRadius: '16px',
        border: '2px solid var(--border)',
        marginBottom: '40px'
      }}>
        {/* Flow Line */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '10%',
          right: '10%',
          height: '4px',
          background: 'linear-gradient(90deg, #4f46e5 0%, #7c3aed 33%, #2563eb 66%, #059669 100%)',
          borderRadius: '2px',
          transform: 'translateY(-50%)',
          zIndex: 0
        }}>
          {/* Animated Data Flow */}
          {animating && (
            <div style={{
              position: 'absolute',
              top: '-6px',
              left: '-10px',
              width: '20px',
              height: '20px',
              background: 'white',
              border: '3px solid #4f46e5',
              borderRadius: '50%',
              boxShadow: '0 0 20px rgba(79, 70, 229, 0.6)',
              animation: 'flowData 4s ease-in-out'
            }} />
          )}
        </div>

        {/* Steps */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '20px',
          position: 'relative',
          zIndex: 1
        }}>
          {steps.map((step, idx) => (
            <div
              key={idx}
              style={{
                background: hoveredStep === idx || animating ? step.color : 'white',
                borderRadius: '16px',
                padding: '24px',
                border: `3px solid ${step.color}`,
                cursor: 'pointer',
                transition: 'all 0.3s',
                transform: hoveredStep === idx ? 'scale(1.05) translateY(-8px)' : 'scale(1)',
                boxShadow: hoveredStep === idx ? `0 12px 24px ${step.color}40` : '0 4px 12px rgba(0, 0, 0, 0.1)'
              }}
              onMouseEnter={() => setHoveredStep(idx)}
              onMouseLeave={() => setHoveredStep(null)}
              onClick={() => onStepClick(step.id)}
            >
              <div style={{
                fontSize: '48px',
                textAlign: 'center',
                marginBottom: '12px',
                filter: hoveredStep === idx || animating ? 'grayscale(0%)' : 'grayscale(30%)'
              }}>
                {step.icon}
              </div>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '800',
                textAlign: 'center',
                marginBottom: '8px',
                color: hoveredStep === idx || animating ? 'white' : step.color
              }}>
                {step.title}
              </h3>
              <p style={{
                fontSize: '12px',
                textAlign: 'center',
                marginBottom: '16px',
                color: hoveredStep === idx || animating ? 'rgba(255,255,255,0.9)' : 'var(--text-secondary)',
                lineHeight: '1.5'
              }}>
                {step.description}
              </p>
              <div style={{ borderTop: `2px solid ${hoveredStep === idx || animating ? 'rgba(255,255,255,0.3)' : step.color + '30'}`, paddingTop: '12px' }}>
                {step.metrics.map((metric, mIdx) => (
                  <div
                    key={mIdx}
                    style={{
                      fontSize: '11px',
                      fontWeight: '700',
                      color: hoveredStep === idx || animating ? 'rgba(255,255,255,0.95)' : 'var(--text-secondary)',
                      marginBottom: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    <span style={{
                      width: '6px',
                      height: '6px',
                      background: hoveredStep === idx || animating ? 'white' : step.color,
                      borderRadius: '50%'
                    }} />
                    {metric}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Flow Examples */}
      <div className="card">
        <h3 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '20px' }}>
          Example: End-to-End Data Flow
        </h3>

        <div style={{ display: 'grid', gap: '16px' }}>
          {[
            {
              stage: 'Input',
              icon: '📥',
              color: '#6b7280',
              content: 'Messy database with fields: cust_nm, ord_dt, prod_val, cat_name'
            },
            {
              stage: 'Stage 1: Ontology',
              icon: '🎯',
              color: '#4f46e5',
              content: 'Defines: Customer.name, Order.date, Product.value, Category.name (with constraints)'
            },
            {
              stage: 'Stage 2: GNN Mapping',
              icon: '🧠',
              color: '#7c3aed',
              content: 'Maps: cust_nm → Customer.name (98%), ord_dt → Order.date (95%), prod_val → Product.value (92%)'
            },
            {
              stage: 'Stage 3: Semantic Query',
              icon: '🔍',
              color: '#2563eb',
              content: 'Query: "High-value customers" → Generates SQL with ontology-guided joins → Returns 150 results'
            },
            {
              stage: 'Stage 4: Compression',
              icon: '⚡',
              color: '#059669',
              content: 'Compresses 150 records: 75,000 tokens → 39,000 tokens (48% reduction)'
            },
            {
              stage: 'Output',
              icon: '📤',
              color: '#10b981',
              content: 'Compressed, semantic-rich data ready for LLM consumption at half the cost'
            }
          ].map((stage, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '16px',
                background: `${stage.color}10`,
                borderRadius: '12px',
                border: `2px solid ${stage.color}40`,
                transition: 'all 0.2s'
              }}
            >
              <div style={{
                fontSize: '32px',
                minWidth: '40px',
                textAlign: 'center'
              }}>
                {stage.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '800',
                  color: stage.color,
                  marginBottom: '4px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  {stage.stage}
                </div>
                <div style={{
                  fontSize: '14px',
                  color: 'var(--text-primary)',
                  lineHeight: '1.6'
                }}>
                  {stage.content}
                </div>
              </div>
              {idx < 5 && (
                <div style={{ fontSize: '24px', color: stage.color }}>↓</div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Key Benefits */}
      <div className="card" style={{ marginTop: '24px', background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)', border: '2px solid #f59e0b' }}>
        <h3 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '20px', color: '#92400e' }}>
          🎯 Why This Pipeline Is Powerful
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>
              ✅ Fully Automated
            </div>
            <div style={{ fontSize: '14px', color: '#92400e' }}>
              Zero manual schema mapping. The GNN learns patterns automatically.
            </div>
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>
              🔒 Research-Safe
            </div>
            <div style={{ fontSize: '14px', color: '#92400e' }}>
              Template-based queries prevent SQL injection while enabling semantic reasoning.
            </div>
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>
              💰 Cost Efficient
            </div>
            <div style={{ fontSize: '14px', color: '#92400e' }}>
              48% token reduction = 48% lower LLM costs on every query.
            </div>
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>
              🔄 Fully Reversible
            </div>
            <div style={{ fontSize: '14px', color: '#92400e' }}>
              Compression is lossless. Decompress anytime without data loss.
            </div>
          </div>
        </div>
      </div>

      <style>
        {`
          @keyframes flowData {
            0% { left: -10px; }
            25% { left: 25%; border-color: #7c3aed; box-shadow: 0 0 20px rgba(124, 58, 237, 0.6); }
            50% { left: 50%; border-color: #2563eb; box-shadow: 0 0 20px rgba(37, 99, 235, 0.6); }
            75% { left: 75%; border-color: #059669; box-shadow: 0 0 20px rgba(5, 150, 105, 0.6); }
            100% { left: calc(100% + 10px); border-color: #10b981; box-shadow: 0 0 20px rgba(16, 185, 129, 0.6); }
          }
        `}
      </style>
    </div>
  )
}

export default PipelineView
