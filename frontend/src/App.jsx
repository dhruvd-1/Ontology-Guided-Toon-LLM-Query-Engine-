import React, { useState } from 'react'
import SchemaMapping from './views/SchemaMapping'
import SemanticQuery from './views/SemanticQuery'
import Compression from './views/Compression'

function App() {
  const [activeTab, setActiveTab] = useState('schema')

  return (
    <div className="container">
      <header style={{ marginBottom: '32px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '8px' }}>
          Ontology-Guided Semantic Storage System
        </h1>
        <p style={{ color: '#6b7280', fontSize: '14px' }}>
          Schema Mapping • Semantic Queries • Token Compression
        </p>
      </header>

      <nav className="tab-nav">
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
        {activeTab === 'schema' && <SchemaMapping />}
        {activeTab === 'query' && <SemanticQuery />}
        {activeTab === 'compression' && <Compression />}
      </main>

      <footer style={{ marginTop: '64px', textAlign: 'center', color: '#9ca3af', fontSize: '13px' }}>
        <p>Ontology-Guided Semantic Storage • Research Project 2026</p>
      </footer>
    </div>
  )
}

export default App
