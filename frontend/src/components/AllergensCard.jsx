import React from 'react';

export default function AllergensCard({ allergensData }) {
  const detected = allergensData?.detected_allergens || [];
  const possible = allergensData?.possible_allergens || [];
  const noAllergenDetected = allergensData?.no_allergen_detected;

  return (
    <div className="card allergens-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">4. Allergen Safety Detection</h2>
          <span className="card-subtitle">
            Cross-referenced with global priority allergen declarations
          </span>
        </div>
        <div className="badges-group">
          {detected.length > 0 && (
            <span className="badge badge-danger">
              {detected.length} Confirmed Allergen{detected.length > 1 ? 's' : ''}
            </span>
          )}
          {possible.length > 0 && (
            <span className="badge badge-warning">
              {possible.length} Precautionary Risk{possible.length > 1 ? 's' : ''}
            </span>
          )}
          {noAllergenDetected && (
            <span className="badge badge-neutral">No Priority Allergens Detected</span>
          )}
        </div>
      </div>

      <div className="card-body">
        {/* Mandatory Safety Alert */}
        <div className="alert-banner alert-warning safety-disclaimer">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <div className="alert-content">
            <strong>Important Allergen Notice:</strong>
            <p>{allergensData?.disclaimer}</p>
          </div>
        </div>

        {/* 1. Confirmed Detected Allergens */}
        {detected.length > 0 && (
          <div className="allergen-section">
            <h3 className="section-subtitle danger-text">
              🚨 Confirmed Detected Allergens ({detected.length})
            </h3>
            <div className="allergen-grid">
              {detected.map((al, idx) => (
                <div key={idx} className="allergen-item-card detected-item">
                  <div className="allergen-item-top">
                    <h4>{al.name}</h4>
                    <span className="severity-badge">{al.severity}</span>
                  </div>
                  <div className="allergen-source">
                    <strong>Evidence:</strong> {al.source}
                  </div>
                  <p className="allergen-desc">{al.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 2. Precautionary / Cross-Contact Allergens */}
        {possible.length > 0 && (
          <div className="allergen-section">
            <h3 className="section-subtitle warning-text">
              ⚠️ Precautionary Cross-Contact Risk ({possible.length})
            </h3>
            <div className="allergen-grid">
              {possible.map((al, idx) => (
                <div key={idx} className="allergen-item-card possible-item">
                  <div className="allergen-item-top">
                    <h4>{al.name}</h4>
                    <span className="severity-badge-subtle">Precautionary</span>
                  </div>
                  <div className="allergen-source">
                    <strong>Warning Type:</strong> {al.source}
                  </div>
                  <p className="allergen-desc">{al.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 3. Empty State */}
        {noAllergenDetected && (
          <div className="clean-allergen-state">
            <div className="check-icon">✓</div>
            <h4>No Priority Allergens Explicitly Identified</h4>
            <p>
              The system scanned for Milk, Wheat, Gluten, Soy, Peanuts, Tree Nuts, Eggs, Fish,
              Shellfish, Sesame, and Sulphites. None were explicitly declared or matched in the legible text.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
