import React from 'react';

export default function AiExplanation({ aiExplanation }) {
  const sections = aiExplanation?.summary_paragraphs || [];

  return (
    <div className="card ai-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">10. Grounded AI Safety & Ingredient Explanation</h2>
          <span className="card-subtitle">
            Synthesized strictly from extracted packaging facts and official food databases
          </span>
        </div>
        <span className="badge badge-accent">AI Synthesizer</span>
      </div>

      <div className="card-body">
        <div className="ai-intro-banner">
          <span className="ai-sparkle-icon">✨</span>
          <span>
            This intelligence summary transforms raw technical label data into clear, evidence-based health and regulatory insights.
          </span>
        </div>

        <div className="ai-sections-list">
          {sections.map((sec, idx) => (
            <div key={idx} className="ai-section-block">
              <h3 className="ai-section-title">{sec.title}</h3>
              <p className="ai-section-summary">{sec.summary}</p>
              {sec.details && sec.details.length > 0 && (
                <ul className="ai-details-list">
                  {sec.details.map((d, dIdx) => (
                    <li key={dIdx}>{d}</li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>

        <div className="ai-disclaimer-footer">
          <small>
            🛡️ {aiExplanation?.disclaimer}
          </small>
        </div>
      </div>
    </div>
  );
}
