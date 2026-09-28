import React from 'react';

export default function AdditivesCard({ additivesData }) {
  const additives = additivesData?.detected_additives || [];
  const functions = additivesData?.additive_functions_summary || [];

  return (
    <div className="card additives-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">5. Additives & E-Number Classification</h2>
          <span className="card-subtitle">
            {additives.length} additive substances recognized by international codex
          </span>
        </div>
        <span className="badge badge-info">
          {additives.length} Additive{additives.length !== 1 ? 's' : ''} Identified
        </span>
      </div>

      <div className="card-body">
        {functions.length > 0 && (
          <div className="functions-summary-bar">
            <span className="functions-label">Technological Roles:</span>
            <div className="function-badges">
              {functions.map((fn, idx) => (
                <span key={idx} className="badge badge-accent">{fn}</span>
              ))}
            </div>
          </div>
        )}

        {additives.length === 0 ? (
          <p className="empty-text">No standardized food additives (E-numbers or INS codes) were identified.</p>
        ) : (
          <div className="additives-table-wrap">
            <table className="standard-table">
              <thead>
                <tr>
                  <th>Code / INS</th>
                  <th>Additive Name</th>
                  <th>Functional Role</th>
                  <th>Origin & Dietary</th>
                  <th>Scientific & Safety Profile</th>
                </tr>
              </thead>
              <tbody>
                {additives.map((ad, idx) => (
                  <tr key={idx}>
                    <td>
                      <span className="additive-code-pill">
                        {ad.code} {ad.ins ? `/ INS ${ad.ins}` : ''}
                      </span>
                      <small className="match-tag">{ad.matched_by}</small>
                    </td>
                    <td>
                      <strong>{ad.name}</strong>
                    </td>
                    <td>
                      <span className="function-pill">{ad.function}</span>
                    </td>
                    <td>
                      <div className="dietary-info">
                        <span>{ad.origin}</span>
                        <small>{ad.dietary}</small>
                      </div>
                    </td>
                    <td className="profile-cell">
                      <p>{ad.description}</p>
                      <small className="notes-text">
                        <strong>Regulatory Note:</strong> {ad.notes}
                      </small>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="evidence-footer">
          <small>
            ℹ️ {additivesData?.disclaimer || 'Food additives are regulated technological substances evaluated for safety and technological necessity by national food authorities.'}
          </small>
        </div>
      </div>
    </div>
  );
}
