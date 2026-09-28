import React from 'react';

export default function Navbar({ activeTab, setActiveTab, backendOnline }) {
  return (
    <header className="navbar">
      <div className="nav-container">
        <div className="brand" onClick={() => setActiveTab('upload')}>
          <div className="brand-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              <circle cx="12" cy="12" r="10"/>
            </svg>
          </div>
          <div>
            <div className="brand-title">FoodLens <span className="brand-highlight">AI</span></div>
            <div className="brand-subtitle">Global Food Label Intelligence & Safety System</div>
          </div>
        </div>

        <nav className="nav-links">
          <button
            className={`nav-btn ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            Label Analyzer
          </button>
          <button
            className={`nav-btn ${activeTab === 'compare' ? 'active' : ''}`}
            onClick={() => setActiveTab('compare')}
          >
            Product Comparison
          </button>
          <button
            className={`nav-btn ${activeTab === 'regulations' ? 'active' : ''}`}
            onClick={() => setActiveTab('regulations')}
          >
            Regulatory Guide
          </button>
        </nav>

        <div className="status-indicator">
          <span className={`status-dot ${backendOnline ? 'online' : 'offline'}`}></span>
          <span className="status-text">{backendOnline ? 'AI Engine Ready' : 'Connecting Engine...'}</span>
        </div>
      </div>
    </header>
  );
}
