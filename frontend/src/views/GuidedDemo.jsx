import React, { useState } from 'react'
import OntologyViewer from './OntologyViewer'
import SchemaMapping from './SchemaMapping'
import SemanticQuery from './SemanticQuery'
import Compression from './Compression'

function GuidedDemo({ onExit }) {
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    {
      id: 'ontology',
      title: 'Step 1: Define Formal Ontology',
      subtitle: 'The Semantic Foundation',
      description: 'Every intelligent system needs a formal understanding of its domain. Our ontology defines 18 classes (Customer, Order, Product, etc.) with 99 properties and 20 relationships. This is the semantic truth that guides everything else.',
      why: 'Why this matters: Without formal semantics, machines cannot understand what data means. The ontology provides a shared vocabulary and constraints.',
      component: OntologyViewer,
      color: '#4f46e5',
      icon: '🎯',
      dataFlow: null
    },
    {
      id: 'schema',
      title: 'Step 2: Map Messy Schema with GNN',
      subtitle: 'From Chaos to Structure',
      description: 'Real databases have cryptic field names like "cust_nm", "ord_dt", "prod_val". Our Graph Neural Network learns to map these messy fields to clean ontology properties automatically.',
      why: 'Why this matters: Manual schema mapping takes weeks. Our GNN does it in milliseconds with confidence scores, learning from patterns in field names, data types, and table relationships.',
      component: SchemaMapping,
      color: '#7c3aed',
      icon: '🧠',
      dataFlow: {
        input: 'Messy DB fields: cust_nm, ord_val, prod_desc',
        process: 'GNN analyzes → Graph of 65 nodes, 433 edges',
        output: 'Mapped to: customerName, orderValue, productDescription'
      }
    },
    {
      id: 'query',
      title: 'Step 3: Execute Semantic Queries',
      subtitle: 'Ask Questions Naturally',
      description: 'Now that we have semantic mappings, we can query data using natural concepts. Ask "Which customers bought electronics?" and the system uses ontology reasoning to find the right tables, joins, and filters.',
      why: 'Why this matters: Users think in concepts (customers, products), not SQL tables. Semantic queries bridge the gap while maintaining security through templates (no SQL injection risk).',
      component: SemanticQuery,
      color: '#2563eb',
      icon: '🔍',
      dataFlow: {
        input: 'Question: "High-value customers who bought phones"',
        process: 'Ontology reasoning → Expands to Product → Electronics → Phones',
        output: 'SQL with proper joins across 4 tables → Results'
      }
    },
    {
      id: 'compression',
      title: 'Step 4: Compress for LLM Efficiency',
      subtitle: 'Optimize Token Usage',
      description: 'Query results are verbose with repeated field names and structure. Our ontology-aware compressor reduces tokens by 48% using semantic IDs, structural flattening, and pattern extraction.',
      why: 'Why this matters: LLMs charge per token. On a 10,000-record result, we save 52,000 tokens. At $0.01/1K tokens, that\'s $0.52 per query. For enterprises running millions of queries: massive savings.',
      component: Compression,
      color: '#059669',
      icon: '⚡',
      dataFlow: {
        input: '200 records with full field names (100K tokens)',
        process: 'Layer 1: Property IDs → Layer 2: Flatten → Layer 3: Compress values → Layer 4: Extract patterns',
        output: '52K tokens (48% reduction)'
      }
    }
  ]

  const currentStepData = steps[currentStep]
  const ComponentToRender = currentStepData.component

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  return (
    <div>
      {/* Progress Bar */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
          {steps.map((step, idx) => (
            <div
              key={idx}
              style={{
                flex: 1,
                textAlign: 'center',
                position: 'relative',
                cursor: 'pointer'
              }}
              onClick={() => setCurrentStep(idx)}
            >
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '50%',
                background: idx <= currentStep ? step.color : 'var(--border)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                fontWeight: '700',
                fontSize: '18px',
                transition: 'all 0.3s',
                border: idx === currentStep ? `4px solid ${step.color}40` : 'none',
                transform: idx === currentStep ? 'scale(1.1)' : 'scale(1)'
              }}>
                {idx + 1}
              </div>
              <div style={{
                fontSize: '12px',
                marginTop: '8px',
                color: idx <= currentStep ? 'var(--text-primary)' : 'var(--text-muted)',
                fontWeight: idx === currentStep ? '700' : '500'
              }}>
                {step.icon} {step.title.replace('Step ' + (idx + 1) + ': ', '')}
              </div>
              {idx < steps.length - 1 && (
                <div style={{
                  position: 'absolute',
                  top: '20px',
                  left: 'calc(50% + 20px)',
                  width: 'calc(100% - 40px)',
                  height: '3px',
                  background: idx < currentStep ? step.color : 'var(--border)',
                  transition: 'all 0.3s'
                }} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Header */}
      <div className="card" style={{
        background: `linear-gradient(135deg, ${currentStepData.color}15 0%, ${currentStepData.color}05 100%)`,
        borderLeft: `4px solid ${currentStepData.color}`,
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'start', gap: '16px' }}>
          <div style={{
            fontSize: '48px',
            minWidth: '60px',
            height: '60px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: currentStepData.color,
            borderRadius: '12px'
          }}>
            {currentStepData.icon}
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '28px', fontWeight: '800', marginBottom: '8px', color: currentStepData.color }}>
              {currentStepData.title}
            </h2>
            <p style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '16px', fontWeight: '600' }}>
              {currentStepData.subtitle}
            </p>
            <p style={{ fontSize: '15px', color: 'var(--text-primary)', lineHeight: '1.7', marginBottom: '12px' }}>
              {currentStepData.description}
            </p>
            <div style={{
              padding: '12px 16px',
              background: 'white',
              borderRadius: '8px',
              borderLeft: `3px solid ${currentStepData.color}`
            }}>
              <strong style={{ color: currentStepData.color }}>💡 {currentStepData.why}</strong>
            </div>
          </div>
        </div>

        {/* Data Flow Visualization */}
        {currentStepData.dataFlow && (
          <div style={{
            marginTop: '20px',
            padding: '20px',
            background: 'white',
            borderRadius: '12px',
            border: '2px dashed var(--border)'
          }}>
            <h3 style={{ fontSize: '14px', fontWeight: '700', marginBottom: '16px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Data Flow in This Step
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>INPUT</div>
                <div style={{ padding: '12px', background: 'var(--surface-alt)', borderRadius: '8px', fontSize: '13px', fontFamily: 'monospace' }}>
                  {currentStepData.dataFlow.input}
                </div>
              </div>
              <div style={{ fontSize: '24px', color: currentStepData.color }}>→</div>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>PROCESS</div>
                <div style={{ padding: '12px', background: `${currentStepData.color}10`, borderRadius: '8px', fontSize: '13px' }}>
                  {currentStepData.dataFlow.process}
                </div>
              </div>
              <div style={{ fontSize: '24px', color: currentStepData.color }}>→</div>
              <div style={{ flex: 1, minWidth: '200px' }}>
                <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text-muted)', marginBottom: '6px' }}>OUTPUT</div>
                <div style={{ padding: '12px', background: '#dcfce7', borderRadius: '8px', fontSize: '13px', color: '#15803d', fontWeight: '600' }}>
                  {currentStepData.dataFlow.output}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Component Content */}
      <div className="card" style={{ minHeight: '400px' }}>
        <ComponentToRender />
      </div>

      {/* Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: '32px',
        padding: '20px',
        background: 'var(--surface)',
        borderRadius: '12px',
        border: '1px solid var(--border)'
      }}>
        <button
          className="button"
          onClick={handlePrev}
          disabled={currentStep === 0}
          style={{
            background: currentStep === 0 ? 'var(--text-muted)' : 'white',
            color: currentStep === 0 ? 'white' : 'var(--primary)',
            border: currentStep === 0 ? 'none' : '2px solid var(--primary)'
          }}
        >
          ← Previous Step
        </button>

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            Step {currentStep + 1} of {steps.length}
          </div>
          <button
            className="button"
            onClick={onExit}
            style={{ background: 'transparent', color: 'var(--text-secondary)', boxShadow: 'none', fontSize: '13px', padding: '6px 12px' }}
          >
            Exit Demo
          </button>
        </div>

        <button
          className="button"
          onClick={handleNext}
          disabled={currentStep === steps.length - 1}
          style={{
            background: currentStep === steps.length - 1 ? 'var(--text-muted)' : `linear-gradient(135deg, ${steps[currentStep + 1]?.color || currentStepData.color} 0%, ${steps[currentStep + 1]?.color || currentStepData.color}dd 100%)`
          }}
        >
          {currentStep === steps.length - 1 ? 'Complete ✓' : 'Next Step →'}
        </button>
      </div>

      {/* Connection to Next Step */}
      {currentStep < steps.length - 1 && (
        <div style={{
          marginTop: '24px',
          padding: '16px 24px',
          background: `linear-gradient(90deg, ${currentStepData.color}20 0%, ${steps[currentStep + 1].color}20 100%)`,
          borderRadius: '12px',
          border: '2px dashed var(--border)',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
            <strong>How this connects to the next step:</strong>
          </div>
          <div style={{ fontSize: '15px', color: 'var(--text-primary)' }}>
            {currentStep === 0 && 'The ontology you just saw provides the semantic vocabulary that the GNN will learn to map database fields to →'}
            {currentStep === 1 && 'The schema mappings you created enable the query engine to translate semantic concepts into SQL →'}
            {currentStep === 2 && 'The query results you generated will now be compressed to save LLM tokens →'}
          </div>
        </div>
      )}

      {/* Completion Message */}
      {currentStep === steps.length - 1 && (
        <div style={{
          marginTop: '24px',
          padding: '24px',
          background: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
          borderRadius: '12px',
          border: '3px solid #10b981',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '32px', marginBottom: '12px' }}>🎉</div>
          <h3 style={{ fontSize: '24px', fontWeight: '800', color: '#15803d', marginBottom: '12px' }}>
            Complete Pipeline Demonstrated!
          </h3>
          <p style={{ fontSize: '16px', color: '#166534', marginBottom: '20px' }}>
            You've seen how all 4 components work together: Ontology → GNN Mapping → Semantic Queries → Compression
          </p>
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="button"
              onClick={() => setCurrentStep(0)}
              style={{ background: 'white', color: '#15803d', border: '2px solid #15803d' }}
            >
              ↻ Restart Demo
            </button>
            <button
              className="button"
              onClick={onExit}
              style={{ background: '#15803d' }}
            >
              Explore Components Freely
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default GuidedDemo
