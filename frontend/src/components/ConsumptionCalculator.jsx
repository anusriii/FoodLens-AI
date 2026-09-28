import React, { useState, useEffect } from 'react';
import { calculateConsumption } from '../services/api';

export default function ConsumptionCalculator({ nutritionData }) {
  const servingSize = nutritionData?.serving_size?.value || 30;
  const unit = nutritionData?.serving_size?.unit || 'g';

  const [consumedAmount, setConsumedAmount] = useState(servingSize);
  const [calculationResult, setCalculationResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [error, setError] = useState('');

  const runCalculation = async (amount) => {
    if (!amount || amount <= 0) return;
    setIsCalculating(true);
    setError('');
    try {
      const res = await calculateConsumption({
        nutrition: nutritionData,
        consumedAmount: amount,
        unit,
        servingSizeVal: nutritionData?.serving_size?.value,
      });
      setCalculationResult(res);
    } catch (err) {
      setError(err.message || 'Calculation error');
    } finally {
      setIsCalculating(false);
    }
  };

  useEffect(() => {
    if (nutritionData) {
      runCalculation(consumedAmount);
    }
  }, [nutritionData]);

  const handleAmountChange = (newAmount) => {
    setConsumedAmount(newAmount);
    runCalculation(newAmount);
  };

  const calculatedNutrients = calculationResult?.calculated_nutrients || {};

  return (
    <div className="card calculator-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">7. Serving Size & Consumption Calculator</h2>
          <span className="card-subtitle">
            Estimate your exact intake by entering the portion you plan to consume
          </span>
        </div>
        <span className="badge badge-accent">Interactive Calculator</span>
      </div>

      <div className="card-body">
        {/* Quick Serving Selector */}
        <div className="calculator-controls">
          <div className="control-group">
            <label className="input-label">Amount Consumed ({unit}):</label>
            <div className="input-with-button">
              <input
                type="number"
                min="1"
                max="2000"
                step="1"
                value={consumedAmount}
                onChange={(e) => handleAmountChange(Number(e.target.value))}
                className="number-input"
              />
              <span className="input-unit-tag">{unit}</span>
            </div>
          </div>

          <div className="quick-presets">
            <span className="preset-label">Quick Portions:</span>
            <button
              type="button"
              className={`preset-btn ${consumedAmount === servingSize ? 'active' : ''}`}
              onClick={() => handleAmountChange(servingSize)}
            >
              1 Serving ({servingSize} {unit})
            </button>
            <button
              type="button"
              className={`preset-btn ${consumedAmount === servingSize * 2 ? 'active' : ''}`}
              onClick={() => handleAmountChange(servingSize * 2)}
            >
              2 Servings ({servingSize * 2} {unit})
            </button>
            <button
              type="button"
              className={`preset-btn ${consumedAmount === 100 ? 'active' : ''}`}
              onClick={() => handleAmountChange(100)}
            >
              100 {unit}
            </button>
            <button
              type="button"
              className={`preset-btn ${consumedAmount === 50 ? 'active' : ''}`}
              onClick={() => handleAmountChange(50)}
            >
              50 {unit}
            </button>
          </div>
        </div>

        {calculationResult?.calculation_basis && (
          <div className="calc-formula-banner">
            <span className="formula-icon">📐</span>
            <span>
              <strong>Formula applied:</strong> (Declared Value / Reference Amount) × Consumed Amount ({consumedAmount} {unit})
            </span>
          </div>
        )}

        {error && <div className="alert-banner alert-error">{error}</div>}

        {/* Calculated Results Table */}
        <div className="consumption-table-wrap">
          <table className="standard-table">
            <thead>
              <tr>
                <th>Nutrient</th>
                <th>Declared Basis ({nutritionData?.declared_basis || 'per 100g'})</th>
                <th className="highlight-col">Estimated Intake ({consumedAmount} {unit})</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(calculatedNutrients).length === 0 ? (
                <tr>
                  <td colSpan="3" className="empty-cell">
                    No numerical nutrients declared on label to calculate intake.
                  </td>
                </tr>
              ) : (
                Object.entries(calculatedNutrients).map(([key, item]) => (
                  <tr key={key}>
                    <td>
                      <strong>{item.label}</strong>
                    </td>
                    <td>
                      {item.original_value} {item.unit}
                    </td>
                    <td className="highlight-col intake-val">
                      <strong>{item.consumed_value} {item.unit}</strong>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
