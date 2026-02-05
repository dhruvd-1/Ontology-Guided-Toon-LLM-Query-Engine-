import React, { useState } from 'react'
import Landing from './views/Landing'
import GuidedDemo from './views/GuidedDemo'
import PipelineView from './views/PipelineView'
import OntologyViewer from './views/OntologyViewer'
import SchemaMapping from './views/SchemaMapping'
import SemanticQuery from './views/SemanticQuery'
import Compression from './views/Compression'

function App() {
  const [mode, setMode] = useState('landing') // 'landing', 'guided', 'pipeline', 'explore'
  const [activeTab, setActiveTab] = useState('ontology')

  const handleStartDemo = () => {
    setMode('guided')
  }

  const handleExitDemo = () => {
    setMode('explore')
  }

  const handleStepClick = (stepId) => {
    setMode('explore')
    const tabMap = {
      'ontology': 'ontology',
      'gnn': 'schema',
      'query': 'query',
      'compression': 'compression'
    }
    setActiveTab(tabMap[stepId] || 'ontology')
  }

  const handleBackToLanding = () => {
    setMode('landing')
  }

  return (
    <div className="container">
      {/* Header */}
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <div
          style={{
            display: 'inline-block',
            background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)',
            padding: '4px 20px',
            borderRadius: '24px',
            marginBottom: '16px',
            cursor: mode !== 'landing' ? 'pointer' : 'default'
          }}
          onClick={mode !== 'landing' ? handleBackToLanding : undefined}
        >
          <h1 style={{
            fontSize: '26px',
            fontWeight: '700',
            color: 'white',
            letterSpacing: '-0.02em'
          }}>
            Ontology-Guided Semantic Storage
          </h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', fontWeight: '500' }}>
          Schema Mapping • Semantic Queries • Token Compression
        </p>
        {mode !== 'landing' && (
          <button
            onClick={handleBackToLanding}
            style={{
              marginTop: '12px',
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '13px',
              cursor: 'pointer',
              textDecoration: 'underline'
            }}
          >
            ← Back to Home
          </button>
        )}
      </header>

      {/* Mode Selector for Explore */}
      {mode === 'explore' && (
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
          marginBottom: '24px'
        }}>
          <button
            className="button"
            onClick={handleStartDemo}
            style={{
              background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)',
              fontSize: '14px',
              padding: '10px 20px'
            }}
          >
            📚 Guided Demo
          </button>
          <button
            className="button"
            onClick={() => setMode('pipeline')}
            style={{
              background: 'linear-gradient(135deg, #7c3aed 0%, #2563eb 100%)',
              fontSize: '14px',
              padding: '10px 20px'
            }}
          >
            🔄 Pipeline View
          </button>
        </div>
      )}

      {/* Pipeline Mode Selector */}
      {mode === 'pipeline' && (
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
          marginBottom: '24px'
        }}>
          <button
            className="button"
            onClick={handleStartDemo}
            style={{
              background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)',
              fontSize: '14px',
              padding: '10px 20px'
            }}
          >
            📚 Guided Demo
          </button>
          <button
            className="button"
            onClick={() => setMode('explore')}
            style={{
              background: 'white',
              color: 'var(--primary)',
              border: '2px solid var(--primary)',
              fontSize: '14px',
              padding: '10px 20px'
            }}
          >
            🔍 Explore Components
          </button>
        </div>
      )}

      {/* Navigation for Explore Mode */}
      {mode === 'explore' && (
        <nav className="tab-nav">
          <button
            className={`tab-button ${activeTab === 'ontology' ? 'active' : ''}`}
            onClick={() => setActiveTab('ontology')}
          >
            🎯 Ontology
          </button>
          <button
            className={`tab-button ${activeTab === 'schema' ? 'active' : ''}`}
            onClick={() => setActiveTab('schema')}
          >
            🧠 Schema Mapping
          </button>
          <button
            className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
            onClick={() => setActiveTab('query')}
          >
            🔍 Semantic Queries
          </button>
          <button
            className={`tab-button ${activeTab === 'compression' ? 'active' : ''}`}
            onClick={() => setActiveTab('compression')}
          >
            ⚡ Compression
          </button>
        </nav>
      )}

      {/* Main Content */}
      <main>
        {mode === 'landing' && <Landing onStartDemo={handleStartDemo} />}
        {mode === 'guided' && <GuidedDemo onExit={handleExitDemo} />}
        {mode === 'pipeline' && <PipelineView onStepClick={handleStepClick} />}
        {mode === 'explore' && (
          <>
            {activeTab === 'ontology' && <OntologyViewer />}
            {activeTab === 'schema' && <SchemaMapping />}
            {activeTab === 'query' && <SemanticQuery />}
            {activeTab === 'compression' && <Compression />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer style={{
        marginTop: '64px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '13px',
        paddingBottom: '24px'
      }}>
        <p>Ontology-Guided Semantic Storage System • 2026 Research Project</p>
      </footer>
    </div>
  )
}

export default App
