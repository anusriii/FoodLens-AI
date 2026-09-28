import React, { useState } from 'react';
import { uploadAndAnalyzeImage, compareProducts } from '../services/api';

export default function ProductComparison({ currentProduct }) {
  const [productA, setProductA] = useState(currentProduct || null);
  const [productB, setProductB] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [isLoadingB, setIsLoadingB] = useState(false);
  const [errorB, setErrorB] = useState('');

  const handleUploadB = async (file) => {
    if (!file) return;
    setIsLoadingB(true);
    setErrorB('');
    try {
      const res = await uploadAndAnalyzeImage(file);
      setProductB(res);
      if (productA) {
        const comp = await compareProducts(productA, res);
        setComparisonResult(comp);
      }
    } catch (err) {
      setErrorB(err.message || 'Failed to analyze second product');
    } finally {
      setIsLoadingB(false);
    }
  };

  // Helper to load sample Product B for immediate comparison
  const loadDemoProductB = () => {
    const canvas = document.createElement('canvas');
    canvas.width = 1000;
    canvas.height = 700;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#f8fafc';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#cbd5e1';
    ctx.lineWidth = 4;
    ctx.strokeRect(20, 20, canvas.width - 40, canvas.height - 40);

    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 28px sans-serif';
    ctx.fillText('ORGANIC OAT & HONEY GRANOLA BAR', 40, 70);

    ctx.font = 'bold 20px sans-serif';
    ctx.fillText('INGREDIENTS:', 40, 130);

    ctx.font = 'normal 18px sans-serif';
    ctx.fillText('Rolled Oats (50%), Honey (15%), Almonds (12%), Coconut Oil,', 40, 165);
    ctx.fillText('Chia Seeds, Sea Salt, Natural Cinnamon Extract.', 40, 195);

    ctx.fillStyle = '#b91c1c';
    ctx.font = 'bold 18px sans-serif';
    ctx.fillText('CONTAINS: Tree Nuts (Almonds), Oats (Gluten).', 40, 260);

    ctx.fillStyle = '#0f172a';
    ctx.font = 'bold 20px sans-serif';
    ctx.fillText('NUTRITIONAL INFORMATION (Per 100 g):', 40, 320);

    ctx.font = 'normal 18px monospace';
    ctx.fillText('Energy:              410 kcal', 40, 360);
    ctx.fillText('Protein:             9.2 g', 40, 390);
    ctx.fillText('Total Carbohydrate:  58.0 g', 40, 420);
    ctx.fillText('  Total Sugars:      14.0 g', 40, 450);
    ctx.fillText('Total Fat:           14.5 g', 400, 360);
    ctx.fillText('  Saturated Fat:     5.0 g', 400, 390);
    ctx.fillText('Dietary Fiber:       6.8 g', 400, 420);
    ctx.fillText('Sodium:              110 mg', 400, 450);

    ctx.font = 'bold 17px sans-serif';
    ctx.fillStyle = '#334155';
    ctx.fillText('Serving Size: 40 g   |   Net Quantity: 160 g', 40, 520);
    ctx.fillText('Manufactured by: Pure Naturals Inc. Best Before 12 Months', 40, 560);

    canvas.toBlob((blob) => {
      const file = new File([blob], 'sample_granola_bar.png', { type: 'image/png' });
      handleUploadB(file);
    }, 'image/png');
  };

  return (
    <div className="card comparison-page-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Side-by-Side Food Product Comparison</h2>
          <span className="card-subtitle">
            Objective, factual comparison across nutritional values, allergens, and additives
          </span>
        </div>
        <span className="badge badge-info">Comparison Studio</span>
      </div>

      <div className="card-body">
        {/* Upload Slots */}
        <div className="compare-slots-grid">
          {/* Product A */}
          <div className="compare-slot">
            <h3 className="slot-title">Product A (Primary Label)</h3>
            {productA ? (
              <div className="slot-summary">
                <span className="product-tag">{productA.image_urls?.filename || 'Current Product'}</span>
                <p><strong>Ingredients:</strong> {productA.ingredients?.count || 0} items</p>
                <p><strong>Confirmed Allergens:</strong> {productA.allergens?.detected_allergens?.length || 0}</p>
                <p><strong>Additives:</strong> {productA.additives?.total_additives_count || 0}</p>
              </div>
            ) : (
              <div className="empty-slot-msg">Please analyze Product A in the main Analyzer first.</div>
            )}
          </div>

          {/* Product B */}
          <div className="compare-slot">
            <h3 className="slot-title">Product B (Compare With)</h3>
            {productB ? (
              <div className="slot-summary">
                <span className="product-tag">{productB.image_urls?.filename || 'Second Product'}</span>
                <p><strong>Ingredients:</strong> {productB.ingredients?.count || 0} items</p>
                <p><strong>Confirmed Allergens:</strong> {productB.allergens?.detected_allergens?.length || 0}</p>
                <p><strong>Additives:</strong> {productB.additives?.total_additives_count || 0}</p>
              </div>
            ) : (
              <div className="upload-slot-b">
                <label className="btn-secondary btn-sm" style={{ cursor: 'pointer' }}>
                  Upload Product B Photo
                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
                    style={{ display: 'none' }}
                    onChange={(e) => e.target.files && handleUploadB(e.target.files[0])}
                  />
                </label>
                <button
                  type="button"
                  className="demo-chip"
                  onClick={loadDemoProductB}
                  disabled={isLoadingB}
                >
                  Or Load Sample Granola Bar
                </button>
                {isLoadingB && <div className="spinner-wrap"><span className="spinner"></span> Analyzing Product B...</div>}
                {errorB && <div className="alert-banner alert-error">{errorB}</div>}
              </div>
            )}
          </div>
        </div>

        {/* Comparison Tables */}
        {comparisonResult && (
          <div className="comparison-results-section">
            <h3 className="comp-heading">Nutritional Differences</h3>
            <div className="comp-table-wrap">
              <table className="standard-table">
                <thead>
                  <tr>
                    <th>Nutrient</th>
                    <th>Product A</th>
                    <th>Product B</th>
                    <th>Difference</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonResult.nutrition_comparison.map((item, idx) => {
                    const diff = (item.product_a !== null && item.product_b !== null)
                      ? (item.product_b - item.product_a).toFixed(1)
                      : null;
                    return (
                      <tr key={idx}>
                        <td><strong>{item.label}</strong></td>
                        <td>{item.product_a !== null ? `${item.product_a} ${item.unit}` : 'Not declared'}</td>
                        <td>{item.product_b !== null ? `${item.product_b} ${item.unit}` : 'Not declared'}</td>
                        <td>
                          {diff !== null ? (
                            <span className={Number(diff) > 0 ? 'diff-higher' : Number(diff) < 0 ? 'diff-lower' : 'diff-equal'}>
                              {Number(diff) > 0 ? `+${diff}` : diff} {item.unit}
                            </span>
                          ) : '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div className="side-by-side-details">
              <div className="comp-column">
                <h4>Product A Allergens</h4>
                {comparisonResult.allergens_a.length > 0 ? (
                  <ul>{comparisonResult.allergens_a.map((a, i) => <li key={i}>{a}</li>)}</ul>
                ) : <p>No allergens detected.</p>}
              </div>

              <div className="comp-column">
                <h4>Product B Allergens</h4>
                {comparisonResult.allergens_b.length > 0 ? (
                  <ul>{comparisonResult.allergens_b.map((a, i) => <li key={i}>{a}</li>)}</ul>
                ) : <p>No allergens detected.</p>}
              </div>
            </div>

            <div className="neutral-disclaimer">
              <small>
                ⚖️ {comparisonResult.summary || 'Factual differences presented without subjective commercial endorsement.'}
              </small>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
