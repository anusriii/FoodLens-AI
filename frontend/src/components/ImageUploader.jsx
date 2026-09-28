import React, { useState, useRef } from 'react';

export default function ImageUploader({ onAnalyze, isLoading, error }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const fileInputRef = useRef(null);

  const steps = [
    'Applying OpenCV preprocessing (denoising, contrast & deskew)...',
    'Executing OCR text recognition...',
    'Extracting & normalizing ingredients and nested additives...',
    'Scanning allergens & cross-contact declarations...',
    'Parsing nutritional panel & serving dimensions...',
    'Checking regulatory status across India, USA, EU, UK & Canada...',
    'Synthesizing AI safety explanations...'
  ];

  const handleFileChange = (file) => {
    setValidationError('');
    if (!file) return;

    // Validate type (JPG, JPEG, PNG, WEBP)
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    const isWebpByName = file.name && file.name.toLowerCase().endsWith('.webp');
    if (!validTypes.includes(file.type) && !isWebpByName) {
      setValidationError('Please upload a valid image file (JPG, JPEG, PNG, or WEBP).');
      return;
    }

    // Validate size (15 MB)
    if (file.size > 15 * 1024 * 1024) {
      setValidationError('Image size exceeds 15 MB limit. Please select a smaller photo.');
      return;
    }

    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = () => {
    if (!selectedFile) {
      setValidationError('Please select or upload a food label image first.');
      return;
    }
    
    // Cycle through steps during loading
    let stepIdx = 0;
    const interval = setInterval(() => {
      stepIdx = (stepIdx + 1) % steps.length;
      setCurrentStep(stepIdx);
    }, 1200);

    onAnalyze(selectedFile, () => clearInterval(interval));
  };

  // Helper to generate a realistic canvas demo label for 1-click testing
  const loadDemoLabel = (type = 'biscuit') => {
    const canvas = document.createElement('canvas');
    canvas.width = 1000;
    canvas.height = 700;
    const ctx = canvas.getContext('2d');

    // Clean packaging label background
    ctx.fillStyle = '#fbfbfa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 4;
    ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);

    ctx.fillStyle = '#111827';
    ctx.font = 'bold 28px sans-serif';
    ctx.fillText('CRUNCHY NUT BISCUITS - NUTRITION & INGREDIENT FACTS', 40, 70);

    ctx.font = 'bold 20px sans-serif';
    ctx.fillText('INGREDIENTS:', 40, 130);

    ctx.font = 'normal 18px sans-serif';
    ctx.fillStyle = '#1f2937';
    const ingLine1 = 'Wheat Flour (62%), Sugar (18%), Palm Oil, Skimmed Milk Powder (4%),';
    const ingLine2 = 'Emulsifier (INS 322 - Soy Lecithin), Leavening Agents [INS 500(ii), INS 503(ii)],';
    const ingLine3 = 'Preservative (INS 211 - Sodium Benzoate), Iodized Salt, Natural Vanilla Flavour.';
    ctx.fillText(ingLine1, 40, 165);
    ctx.fillText(ingLine2, 40, 195);
    ctx.fillText(ingLine3, 40, 225);

    ctx.fillStyle = '#b91c1c';
    ctx.font = 'bold 18px sans-serif';
    ctx.fillText('ALLERGEN INFORMATION: Contains Wheat (Gluten), Milk, and Soy.', 40, 280);
    ctx.fillText('May contain traces of Peanuts and Tree Nuts.', 40, 310);

    // Nutrition Table
    ctx.fillStyle = '#111827';
    ctx.font = 'bold 20px sans-serif';
    ctx.fillText('NUTRITION INFORMATION (Approximate values per 100 g):', 40, 370);

    ctx.font = 'normal 18px monospace';
    ctx.fillText('Energy:              465 kcal', 40, 410);
    ctx.fillText('Protein:             7.5 g', 40, 440);
    ctx.fillText('Total Carbohydrate:  68.0 g', 40, 470);
    ctx.fillText('  Total Sugars:      22.5 g', 40, 500);
    ctx.fillText('  Added Sugars:      18.0 g', 40, 530);
    ctx.fillText('Total Fat:           18.0 g', 400, 410);
    ctx.fillText('  Saturated Fat:     8.5 g', 400, 440);
    ctx.fillText('  Trans Fat:         0.1 g', 400, 470);
    ctx.fillText('Dietary Fiber:       3.2 g', 400, 500);
    ctx.fillText('Sodium:              320 mg', 400, 530);

    ctx.font = 'bold 17px sans-serif';
    ctx.fillStyle = '#374151';
    ctx.fillText('Serving Size: 25 g (approx. 3 biscuits)   |   Net Quantity: 200 g', 40, 590);
    ctx.fillText('Manufactured by: Golden Harvest Foods Ltd. FSSAI Lic. No. 10015022003890', 40, 625);
    ctx.fillText('Best Before 9 Months from Manufacture Date: 15/09/2026   |   Batch: B482', 40, 655);

    canvas.toBlob((blob) => {
      const file = new File([blob], 'sample_food_label.png', { type: 'image/png' });
      handleFileChange(file);
    }, 'image/png');
  };

  return (
    <div className="uploader-section">
      <div className="uploader-hero">
        <h1 className="hero-title">Analyze Any Food Product Label</h1>
        <p className="hero-desc">
          Upload a food label photo. FoodLens AI automatically extracts ingredients, allergens,
          additives, nutrition table, serving sizes, and compares regulations across 5 global jurisdictions.
        </p>
      </div>

      <div
        className={`dropzone ${dragActive ? 'drag-active' : ''} ${previewUrl ? 'has-preview' : ''}`}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => !previewUrl && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
          style={{ display: 'none' }}
          onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
        />

        {previewUrl ? (
          <div className="preview-container">
            <img src={previewUrl} alt="Label preview" className="image-preview" />
            <div className="preview-overlay">
              <span className="file-info">{selectedFile?.name} ({(selectedFile?.size / 1024).toFixed(1)} KB)</span>
              <button
                className="btn-change-image"
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                Choose Different Photo
              </button>
            </div>
          </div>
        ) : (
          <div className="dropzone-content">
            <div className="upload-icon-circle">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <h3>Drag & Drop Food Label Photo Here</h3>
            <p>Supports JPG, JPEG, PNG, WEBP (up to 15 MB)</p>
            <button
              type="button"
              className="btn-secondary"
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              Browse Files
            </button>
          </div>
        )}
      </div>

      <div className="demo-actions">
        <span>No image handy? Try our verified sample:</span>
        <button
          type="button"
          className="demo-chip"
          onClick={() => loadDemoLabel('biscuit')}
        >
          Load Sample Food Label (Biscuits)
        </button>
      </div>

      {(validationError || error) && (
        <div className="alert-banner alert-error">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{validationError || error}</span>
        </div>
      )}

      <div className="action-row">
        <button
          type="button"
          className="btn-primary btn-large"
          disabled={!selectedFile || isLoading}
          onClick={handleSubmit}
        >
          {isLoading ? (
            <span className="spinner-wrap">
              <span className="spinner"></span>
              Analyzing Label with AI...
            </span>
          ) : (
            'Analyze Food Label'
          )}
        </button>
      </div>

      {isLoading && (
        <div className="progress-status-box">
          <div className="pulse-bar"></div>
          <div className="step-text">{steps[currentStep]}</div>
        </div>
      )}
    </div>
  );
}
