import React from 'react';

export default function NutritionCard({ nutritionData }) {
  const nutrients = nutritionData?.nutrients || {};
  const basis = nutritionData?.declared_basis || 'per 100 g';
  const servingSize = nutritionData?.serving_size || {};
  const netQty = nutritionData?.net_quantity || {};
  const detected = nutritionData?.nutrition_table_detected;

  const keyNutrientList = [
    { key: 'energy_kcal', label: 'Energy / Calories', icon: '⚡' },
    { key: 'protein', label: 'Protein', icon: '💪' },
    { key: 'carbohydrates', label: 'Total Carbohydrate', icon: '🌾' },
    { key: 'total_sugars', label: 'Total Sugars', icon: '🍬' },
    { key: 'added_sugars', label: 'Added Sugars', icon: '🧁' },
    { key: 'total_fat', label: 'Total Fat', icon: '🥑' },
    { key: 'saturated_fat', label: 'Saturated Fat', icon: '🧈' },
    { key: 'trans_fat', label: 'Trans Fat', icon: '⚠️' },
    { key: 'fiber', label: 'Dietary Fiber', icon: '🌱' },
    { key: 'sodium', label: 'Sodium', icon: '🧂' },
  ];

  return (
    <div className="card nutrition-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">6. Nutritional Facts & Serving Metrics</h2>
          <span className="card-subtitle">
            Declared basis: <strong>{basis}</strong>
          </span>
        </div>
        <span className={`badge ${detected ? 'badge-success' : 'badge-neutral'}`}>
          {detected ? 'Nutrition Table Found' : 'No Table Detected'}
        </span>
      </div>

      <div className="card-body">
        {/* Package & Serving Dimensions */}
        <div className="dimensions-row">
          <div className="dimension-box">
            <span className="dim-label">Serving Size</span>
            <span className="dim-val">
              {servingSize.detected
                ? (servingSize.value ? `${servingSize.value} ${servingSize.unit}` : servingSize.raw_text)
                : 'Not declared on visible label'}
            </span>
          </div>
          <div className="dimension-box">
            <span className="dim-label">Package Net Quantity</span>
            <span className="dim-val">
              {netQty.detected
                ? (netQty.value ? `${netQty.value} ${netQty.unit}` : netQty.raw_text)
                : 'Not declared on visible label'}
            </span>
          </div>
          <div className="dimension-box">
            <span className="dim-label">Standard Reporting Basis</span>
            <span className="dim-val highlight-val">{basis}</span>
          </div>
        </div>

        {/* Nutrients Grid */}
        <div className="nutrients-grid">
          {keyNutrientList.map(({ key, label, icon }) => {
            const nut = nutrients[key];
            const hasVal = nut && nut.value !== null && nut.value !== undefined;

            return (
              <div key={key} className={`nutrient-stat-box ${hasVal ? 'present' : 'missing'}`}>
                <div className="nutrient-icon-row">
                  <span className="nut-icon">{icon}</span>
                  <span className="nut-name">{label}</span>
                </div>
                <div className="nutrient-value-display">
                  {hasVal ? (
                    <>
                      <span className="num-val">{nut.value}</span>
                      <span className="num-unit">{nut.unit}</span>
                    </>
                  ) : (
                    <span className="num-missing">Not declared</span>
                  )}
                </div>
                <div className="nutrient-basis-sub">{basis}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
