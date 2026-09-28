/**
 * FoodLens AI - Frontend API Service
 * Connects React client to FastAPI backend endpoints.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function uploadAndAnalyzeImage(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorMsg = 'Failed to analyze label image';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errorMsg;
    } catch (e) {
      errorMsg = `Server error (${response.status}): ${response.statusText}`;
    }
    throw new Error(errorMsg);
  }

  return await response.json();
}

export async function calculateConsumption({ nutrition, consumedAmount, unit = 'g', servingSizeVal = null }) {
  const response = await fetch(`${API_BASE_URL}/api/calculate-consumption`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nutrition,
      consumed_amount: Number(consumedAmount),
      unit,
      serving_size_val: servingSizeVal ? Number(servingSizeVal) : null,
    }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Calculation error' }));
    throw new Error(err.detail || 'Calculation failed');
  }

  return await response.json();
}

export async function askLabelQuestion(question, analysis) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, analysis }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Chat error' }));
    throw new Error(err.detail || 'Failed to answer question');
  }

  return await response.json();
}

export async function compareProducts(productA, productB) {
  const response = await fetch(`${API_BASE_URL}/api/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_a: productA, product_b: productB }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Comparison error' }));
    throw new Error(err.detail || 'Comparison failed');
  }

  return await response.json();
}

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}

export function getFullImageUrl(relativePath) {
  if (!relativePath) return null;
  if (relativePath.startsWith('http')) return relativePath;
  return `${API_BASE_URL}${relativePath}`;
}
