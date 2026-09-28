import React, { useState } from 'react';

export default function ExtractedTextCard({ ocr }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const fullText = ocr?.full_text || 'No text extracted.';

  const handleCopy = () => {
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="card text-card">
      <div className="card-header collapsible-header" onClick={() => setIsOpen(!isOpen)}>
        <div>
          <h2 className="card-title">2. Extracted Label Text (Raw OCR)</h2>
          <span className="card-subtitle">
            {ocr?.line_count || 0} lines identified • Click to {isOpen ? 'hide' : 'expand'}
          </span>
        </div>
        <div className="header-actions" onClick={(e) => e.stopPropagation()}>
          <button className="btn-secondary btn-sm" onClick={handleCopy}>
            {copied ? 'Copied!' : 'Copy Text'}
          </button>
          <button className="icon-toggle-btn" onClick={() => setIsOpen(!isOpen)}>
            {isOpen ? '▲' : '▼'}
          </button>
        </div>
      </div>

      {isOpen && (
        <div className="card-body">
          <div className="raw-text-container">
            <pre className="raw-text-block">{fullText}</pre>
          </div>

          <div className="lines-breakdown">
            <h4>Line-by-Line Recognition & Confidence:</h4>
            <div className="line-table-wrap">
              <table className="compact-table">
                <thead>
                  <tr>
                    <th>Line #</th>
                    <th>Extracted Text</th>
                    <th>Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {ocr?.lines?.map((line, idx) => (
                    <tr key={idx}>
                      <td className="line-num">{idx + 1}</td>
                      <td className="line-content">{line.text}</td>
                      <td>
                        <span className={`mini-badge ${line.confidence >= 0.8 ? 'conf-high' : line.confidence >= 0.6 ? 'conf-med' : 'conf-low'}`}>
                          {Math.round(line.confidence * 100)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
