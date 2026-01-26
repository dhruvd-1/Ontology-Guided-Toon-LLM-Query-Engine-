import React, { useState } from 'react'
import OntologyViewer from './views/OntologyViewer'
import SchemaMapping from './views/SchemaMapping'
import SemanticQuery from './views/SemanticQuery'
import Compression from './views/Compression'

function App() {
  const [activeTab, setActiveTab] = useState('ontology')

  return (
    <div className="container">
      <header style={{ marginBottom: '40px', textAlign: 'center' }}>
        <div style={{ 
          display: 'inline-block',
          background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)',
          padding: '4px 20px',
          borderRadius: '24px',
          marginBottom: '16px'
        }}>
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
      </header>

      <nav className="tab-nav">
        <button
          className={`tab-button ${activeTab === 'ontology' ? 'active' : ''}`}
          onClick={() => setActiveTab('ontology')}
        >
          Ontology
        </button>
        <button
          className={`tab-button ${activeTab === 'schema' ? 'active' : ''}`}
          onClick={() => setActiveTab('schema')}
        >
          Schema Mapping
        </button>
        <button
          className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          Semantic Queries
        </button>
        <button
          className={`tab-button ${activeTab === 'compression' ? 'active' : ''}`}
          onClick={() => setActiveTab('compression')}
        >
          Compression
        </button>
      </nav>

      <main>
        {activeTab === 'ontology' && <OntologyViewer />}
        {activeTab === 'schema' && <SchemaMapping />}
        {activeTab === 'query' && <SemanticQuery />}
        {activeTab === 'compression' && <Compression />}
      </main>

      <footer style={{ 
        marginTop: '64px', 
        textAlign: 'center', 
        color: 'var(--text-muted)', 
        fontSize: '13px',
        paddingBottom: '24px'
      }}>
        <p>Ontology-Guided Semantic Storage System</p>
      </footer>
    </div>
  )
}

export default App
