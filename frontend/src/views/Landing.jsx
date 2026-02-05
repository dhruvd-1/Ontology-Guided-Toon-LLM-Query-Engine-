import React from 'react'

function Landing({ onStartDemo }) {
  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: '60px' }}>
        <div style={{
          fontSize: '48px',
          fontWeight: '800',
          background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '20px',
          letterSpacing: '-0.02em'
        }}>
          From Messy Data to Intelligent Queries
        </div>
        <p style={{ fontSize: '20px', color: 'var(--text-secondary)', lineHeight: '1.6', marginBottom: '40px' }}>
          A complete semantic pipeline that transforms chaotic databases into intelligent, queryable knowledge
        </p>
        <button
          className="button"
          onClick={onStartDemo}
          style={{
            fontSize: '16px',
            padding: '14px 32px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)',
            boxShadow: '0 10px 25px rgba(79, 70, 229, 0.3)'
          }}
        >
          Start Guided Demo →
        </button>
      </div>

      {/* The Problem */}
      <div className="card" style={{ marginBottom: '32px', borderLeft: '4px solid #ef4444' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px', color: '#dc2626' }}>
          The Problem
        </h2>
        <div style={{ fontSize: '16px', color: 'var(--text-secondary)', lineHeight: '1.8' }}>
          <p style={{ marginBottom: '12px' }}>
            <strong>Real-world databases are a mess:</strong>
          </p>
          <ul style={{ marginLeft: '24px', marginBottom: '12px' }}>
            <li>Field names like <code>cust_nm</code>, <code>ord_val</code>, <code>prod_desc</code></li>
            <li>No semantic meaning - machines can't understand what data represents</li>
            <li>Querying requires knowing exact schema details</li>
            <li>Sending data to LLMs wastes 52% of tokens on redundant structure</li>
          </ul>
          <p>
            <strong>Result:</strong> Data silos, integration nightmares, and expensive LLM costs.
          </p>
        </div>
      </div>

      {/* The Solution */}
      <div className="card" style={{ marginBottom: '32px', borderLeft: '4px solid #10b981' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px', color: '#059669' }}>
          Our Solution: The 4-Stage Pipeline
        </h2>
        <p style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '24px', lineHeight: '1.8' }}>
          A complete semantic transformation system that turns chaos into intelligence:
        </p>

        <div style={{ display: 'grid', gap: '20px' }}>
          {[
            {
              step: '1',
              title: 'Formal Ontology',
              description: 'Define semantic truth: 18 classes, 99 properties with formal constraints. This is your semantic North Star.',
              color: '#4f46e5',
              icon: '🎯'
            },
            {
              step: '2',
              title: 'GNN Schema Mapping',
              description: 'Graph Neural Network automatically maps messy database fields to clean ontology properties with confidence scores.',
              color: '#7c3aed',
              icon: '🧠'
            },
            {
              step: '3',
              title: 'Semantic Queries',
              description: 'Ask questions naturally. The system uses ontology reasoning to generate intelligent, secure SQL queries.',
              color: '#2563eb',
              icon: '🔍'
            },
            {
              step: '4',
              title: 'Smart Compression',
              description: 'Compress results by 48% using ontology-aware encoding. Save LLM tokens and costs.',
              color: '#059669',
              icon: '⚡'
            }
          ].map((stage, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '16px',
                padding: '20px',
                background: 'var(--surface-alt)',
                borderRadius: '12px',
                border: '2px solid var(--border)',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = stage.color
                e.currentTarget.style.transform = 'translateX(8px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border)'
                e.currentTarget.style.transform = 'translateX(0)'
              }}
            >
              <div style={{
                fontSize: '32px',
                minWidth: '50px',
                height: '50px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: stage.color,
                borderRadius: '12px',
                color: 'white',
                fontWeight: '800'
              }}>
                {stage.step}
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '8px', color: stage.color }}>
                  {stage.icon} {stage.title}
                </h3>
                <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: '1.6' }}>
                  {stage.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Why This Matters */}
      <div className="card" style={{ marginBottom: '32px', background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)', border: '2px solid #f59e0b' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px', color: '#92400e' }}>
          Why This Matters
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          <div>
            <div style={{ fontSize: '32px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>48%</div>
            <div style={{ fontSize: '14px', color: '#78350f', fontWeight: '600' }}>Token Reduction</div>
            <div style={{ fontSize: '13px', color: '#92400e' }}>Massive LLM cost savings</div>
          </div>
          <div>
            <div style={{ fontSize: '32px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>100%</div>
            <div style={{ fontSize: '14px', color: '#78350f', fontWeight: '600' }}>Automated Mapping</div>
            <div style={{ fontSize: '13px', color: '#92400e' }}>No manual schema work</div>
          </div>
          <div>
            <div style={{ fontSize: '32px', fontWeight: '800', color: '#d97706', marginBottom: '8px' }}>15+</div>
            <div style={{ fontSize: '14px', color: '#78350f', fontWeight: '600' }}>Semantic Queries</div>
            <div style={{ fontSize: '13px', color: '#92400e' }}>Research-safe templates</div>
          </div>
        </div>
      </div>

      {/* Novel Contributions */}
      <div className="card" style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '24px', fontWeight: '700', marginBottom: '16px' }}>
          🚀 Novel Research Contributions
        </h2>
        <ul style={{ fontSize: '15px', color: 'var(--text-secondary)', lineHeight: '2', marginLeft: '24px' }}>
          <li><strong>Ontology-Guided GNN:</strong> First system to use graph neural networks with semantic features for schema mapping</li>
          <li><strong>Research-Safe Queries:</strong> Template-based approach prevents SQL injection while enabling semantic reasoning</li>
          <li><strong>Ontology-Aware Compression:</strong> Uses semantic structure for intelligent token reduction (not just text compression)</li>
          <li><strong>End-to-End Integration:</strong> Complete working system from ontology to compressed results</li>
        </ul>
      </div>

      {/* CTA */}
      <div style={{ textAlign: 'center', marginTop: '60px' }}>
        <p style={{ fontSize: '18px', color: 'var(--text-secondary)', marginBottom: '24px' }}>
          Ready to see how all 4 stages work together?
        </p>
        <button
          className="button"
          onClick={onStartDemo}
          style={{
            fontSize: '18px',
            padding: '16px 40px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)',
            boxShadow: '0 10px 25px rgba(79, 70, 229, 0.3)'
          }}
        >
          Launch Guided Demo →
        </button>
      </div>
    </div>
  )
}

export default Landing
