import React, { useState } from 'react';

export default function RegulationTable({ regulationsData }) {
  const [selectedCountry, setSelectedCountry] = useState('All');
  const comparisonTable = regulationsData?.comparison_table || [];
  const countryReports = regulationsData?.country_reports || {};
  const countries = ['India', 'USA', 'European Union', 'UK', 'Canada'];

  const getStatusBadgeClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'allowed':
        return 'badge-status-allowed';
      case 'restricted':
        return 'badge-status-restricted';
      case 'not permitted':
        return 'badge-status-banned';
      case 'conditional':
        return 'badge-status-conditional';
      default:
        return 'badge-status-unknown';
    }
  };

  const getCountryFlag = (country) => {
    switch (country) {
      case 'India': return '🇮🇳';
      case 'USA': return '🇺🇸';
      case 'European Union': return '🇪🇺';
      case 'UK': return '🇬🇧';
      case 'Canada': return '🇨🇦';
      default: return '🌐';
    }
  };

  return (
    <div className="card regulations-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">8. Global Regulatory Intelligence Engine</h2>
          <span className="card-subtitle">
            Rule-based statutory compliance across India, USA, European Union, UK, and Canada
          </span>
        </div>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${selectedCountry === 'All' ? 'active' : ''}`}
            onClick={() => setSelectedCountry('All')}
          >
            All 5 Jurisdictions
          </button>
          {countries.map((c) => (
            <button
              key={c}
              className={`filter-btn ${selectedCountry === c ? 'active' : ''}`}
              onClick={() => setSelectedCountry(c)}
            >
              {getCountryFlag(c)} {c}
            </button>
          ))}
        </div>
      </div>

      <div className="card-body">
        {/* Statutory Disclaimer */}
        <div className="reg-disclaimer-box">
          <span className="disclaimer-badge">STATUTORY DATA NOTICE</span>
          <p>
            Regulatory status is determined deterministically from official public registers (FSSAI, FDA,
            EUR-Lex, UK FSA, Health Canada). The system never hallucinates banned statuses or limits.
            If specific food category classification or concentration is undeclared on the packaging,
            status is recorded as <em>"Unknown / Not enough data"</em>.
          </p>
        </div>

        {comparisonTable.length === 0 ? (
          <p className="empty-text">No regulated additives or specialized ingredients detected to evaluate.</p>
        ) : selectedCountry === 'All' ? (
          /* Multi-Country Comparison Table */
          <div className="reg-table-scroll">
            <table className="standard-table reg-matrix-table">
              <thead>
                <tr>
                  <th>Substance & Code</th>
                  {countries.map((c) => (
                    <th key={c}>
                      {getCountryFlag(c)} {c}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {comparisonTable.map((row, idx) => (
                  <tr key={idx}>
                    <td className="substance-col">
                      <strong>{row.substance}</strong>
                      <span className="code-subtag">{row.code}</span>
                    </td>
                    {countries.map((c) => {
                      const cData = row.countries[c] || {};
                      return (
                        <td key={c} className="reg-matrix-cell">
                          <span className={`status-pill ${getStatusBadgeClass(cData.status)}`}>
                            {cData.status || 'Unknown'}
                          </span>
                          <span className="limit-text">{cData.max_level || 'GMP'}</span>
                          {cData.source && (
                            <a
                              href={cData.source}
                              target="_blank"
                              rel="noreferrer"
                              className="source-link"
                            >
                              Official Ref ↗
                            </a>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          /* Single Country In-Depth View */
          <div className="country-detailed-grid">
            <h3 className="single-country-heading">
              {getCountryFlag(selectedCountry)} In-Depth Regulatory Assessment: {selectedCountry}
            </h3>
            <div className="rules-cards-list">
              {(countryReports[selectedCountry] || []).map((rule, idx) => (
                <div key={idx} className="rule-card">
                  <div className="rule-header">
                    <div>
                      <h4>{rule.substance} ({rule.code || 'N/A'})</h4>
                      <span className="jurisdiction-text">{rule.jurisdiction}</span>
                    </div>
                    <span className={`status-pill ${getStatusBadgeClass(rule.status)}`}>
                      {rule.status}
                    </span>
                  </div>

                  <div className="rule-body">
                    <div className="rule-field">
                      <strong>Food Category:</strong> {rule.food_category}
                    </div>
                    <div className="rule-field">
                      <strong>Maximum Permitted Level:</strong>{' '}
                      {rule.max_permitted_level !== null ? `${rule.max_permitted_level} ${rule.unit}` : (rule.unit || 'GMP')}
                    </div>
                    <div className="rule-field">
                      <strong>Statutory Condition:</strong> {rule.conditions_of_use}
                    </div>
                    {rule.regulation_version && (
                      <div className="rule-field">
                        <strong>Citation / Version:</strong> {rule.regulation_version} (Effective: {rule.effective_date})
                      </div>
                    )}
                    {rule.notes && (
                      <div className="rule-notes">
                        <strong>Notes:</strong> {rule.notes}
                      </div>
                    )}
                  </div>

                  <div className="rule-footer">
                    <a
                      href={rule.official_source_url}
                      target="_blank"
                      rel="noreferrer"
                      className="btn-link"
                    >
                      View Official {rule.jurisdiction} Regulation ↗
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
