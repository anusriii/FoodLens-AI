import React from 'react';

export default function CompletenessCard({ completenessData }) {
  const score = completenessData?.completeness_score || 0;
  const status = completenessData?.overall_status || 'Evaluating';
  const criteria = completenessData?.criteria || [];

  const getStatusColor = (s) => {
    if (s === 'Complete') return '#10b981';
    if (s === 'Partially complete') return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="card completeness-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">9. Label Completeness Verification</h2>
          <span className="card-subtitle">
            Checks for mandatory regulatory declaration items present on the packaging
          </span>
        </div>
        <span
          className="badge"
          style={{
            backgroundColor: `${getStatusColor(status)}20`,
            color: getStatusColor(status),
            border: `1px solid ${getStatusColor(status)}40`,
          }}
        >
          Status: {status} ({score}%)
        </span>
      </div>

      <div className="card-body">
        {/* Progress Bar */}
        <div className="progress-section">
          <div className="progress-header">
            <span>Overall Label Legibility Score</span>
            <span className="progress-pct">{score}%</span>
          </div>
          <div className="progress-track">
            <div
              className="progress-fill"
              style={{
                width: `${score}%`,
                backgroundColor: getStatusColor(status),
              }}
            ></div>
          </div>
        </div>

        {/* 7 Criteria Checklist */}
        <div className="checklist-grid">
          {criteria.map((item, idx) => {
            const isDetected = item.status === 'Detected';
            return (
              <div key={idx} className={`checklist-item ${isDetected ? 'detected' : 'missing'}`}>
                <div className="check-icon-circle">
                  {isDetected ? '✓' : '✕'}
                </div>
                <div className="check-info">
                  <span className="check-name">{item.name}</span>
                  <span className="check-status-tag">
                    {item.status} ({item.weight}% weight)
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="completeness-disclaimer">
          <small>
            ⚠️ {completenessData?.disclaimer || 'Completeness evaluation is based on OCR optical detection within the uploaded image boundary and does not constitute statutory legal verification.'}
          </small>
        </div>
      </div>
    </div>
  );
}
