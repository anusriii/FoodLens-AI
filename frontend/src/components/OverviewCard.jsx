import React, { useState } from 'react';
import { getFullImageUrl } from '../services/api';

export default function OverviewCard({ data }) {
  const [showPreprocessed, setShowPreprocessed] = useState(false);
  const ocr = data?.ocr || {};
  const completeness = data?.completeness || {};
  const imageUrls = data?.image_urls || {};

  const confidencePct = Math.round((ocr.average_confidence || 0) * 100);
  const isLowConfidence = ocr.is_low_confidence;

  const originalUrl = getFullImageUrl(imageUrls.original);
  const preprocessedUrl = getFullImageUrl(imageUrls.preprocessed);

  return (
    <div className="card overview-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">1. Product & OCR Overview</h2>
          <span className="card-subtitle">File: {imageUrls.filename || 'Uploaded Label'}</span>
        </div>
        <div className="badges-group">
          <span className={`badge ${confidencePct >= 75 ? 'badge-success' : confidencePct >= 60 ? 'badge-warning' : 'badge-danger'}`}>
            OCR Confidence: {confidencePct}%
          </span>
          <span className={`badge ${completeness.completeness_score >= 70 ? 'badge-info' : 'badge-neutral'}`}>
            Completeness: {completeness.completeness_score || 0}%
          </span>
        </div>
      </div>

      {isLowConfidence && (
        <div className="alert-banner alert-warning">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <div>
            <strong>Low OCR Confidence Warning:</strong>
            <p>Some text may be slightly blurred or low-contrast. Please cross-check extracted ingredients and nutrition against the physical package.</p>
          </div>
        </div>
      )}

      <div className="overview-grid">
        <div className="image-view-pane">
          <div className="toggle-tabs">
            <button
              className={`toggle-tab ${!showPreprocessed ? 'active' : ''}`}
              onClick={() => setShowPreprocessed(false)}
            >
              Original Photo
            </button>
            {preprocessedUrl && (
              <button
                className={`toggle-tab ${showPreprocessed ? 'active' : ''}`}
                onClick={() => setShowPreprocessed(true)}
              >
                OpenCV Preprocessed
              </button>
            )}
          </div>

          <div className="preview-frame">
            <img
              src={showPreprocessed && preprocessedUrl ? preprocessedUrl : originalUrl}
              alt="Food label inspected"
              className="dashboard-img"
            />
          </div>
        </div>

        <div className="meta-stats-pane">
          <div className="stat-box">
            <span className="stat-label">Text Lines Recognized</span>
            <span className="stat-value">{ocr.line_count || 0}</span>
          </div>

          <div className="stat-box">
            <span className="stat-label">Deskew Angle Corrected</span>
            <span className="stat-value">
              {ocr.preprocessing?.skew_angle_detected !== undefined
                ? `${ocr.preprocessing.skew_angle_detected}°`
                : '0°'}
            </span>
          </div>

          <div className="stat-box">
            <span className="stat-label">Image Dimensions</span>
            <span className="stat-value">
              {ocr.preprocessing?.original_width} × {ocr.preprocessing?.original_height} px
            </span>
          </div>

          <div className="steps-pill-list">
            <span className="steps-title">CV Preprocessing Pipeline Applied:</span>
            <div className="pills">
              {ocr.preprocessing?.steps_applied?.map((step, idx) => (
                <span key={idx} className="pill">{step}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
