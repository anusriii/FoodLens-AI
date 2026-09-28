import React from 'react';

export default function IngredientsCard({ ingredientsData }) {
  const items = ingredientsData?.structured_ingredients || [];
  const hasIngredients = ingredientsData?.has_ingredients;

  return (
    <div className="card ingredients-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">3. Structured Ingredients Analysis</h2>
          <span className="card-subtitle">
            {items.length} individual ingredients extracted and normalized
          </span>
        </div>
        <span className={`badge ${hasIngredients ? 'badge-success' : 'badge-danger'}`}>
          {hasIngredients ? 'Ingredients Found' : 'Not Detected'}
        </span>
      </div>

      <div className="card-body">
        {ingredientsData?.raw_text && (
          <div className="raw-snippet-box">
            <strong>Extracted Block: </strong>
            <span>{ingredientsData.raw_text}</span>
          </div>
        )}

        {items.length === 0 ? (
          <p className="empty-text">No structured ingredients could be parsed from the image.</p>
        ) : (
          <div className="ingredients-grid">
            {items.map((item, idx) => (
              <div key={idx} className="ingredient-item-card">
                <div className="ingredient-header">
                  <span className="ingredient-num">#{idx + 1}</span>
                  <div className="ingredient-names">
                    <h3 className="ingredient-name">{item.normalized_name}</h3>
                    {item.raw_name !== item.normalized_name && (
                      <span className="ingredient-raw-tag">Declared as: "{item.raw_name}"</span>
                    )}
                  </div>
                  <span className={`quantity-badge ${item.quantity.includes('%') ? 'has-qty' : 'no-qty'}`}>
                    {item.quantity}
                  </span>
                </div>

                <div className="ingredient-meta-row">
                  <span className="meta-tag category-tag">{item.category}</span>
                  <span className="meta-tag dietary-tag">{item.dietary}</span>
                  {item.additive_code && (
                    <span className="meta-tag code-tag">{item.additive_code}</span>
                  )}
                </div>

                <p className="ingredient-purpose">
                  <strong>Functional Purpose:</strong> {item.purpose}
                </p>

                {item.sub_ingredients && item.sub_ingredients.length > 0 && (
                  <div className="nested-box">
                    <span className="nested-label">Nested Sub-ingredients:</span>
                    <div className="nested-pills">
                      {item.sub_ingredients.map((sub, sIdx) => (
                        <span key={sIdx} className="nested-pill">{sub}</span>
                      ))}
                    </div>
                  </div>
                )}

                {item.allergen_relationship && (
                  <div className="allergen-relation-alert">
                    <span className="alert-icon">⚠️</span> Allergen origin: <strong>{item.allergen_relationship}</strong>
                  </div>
                )}

                <div className="ingredient-notes">
                  <small>{item.concerns}</small>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
