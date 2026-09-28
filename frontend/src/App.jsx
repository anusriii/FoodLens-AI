import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ImageUploader from './components/ImageUploader';
import OverviewCard from './components/OverviewCard';
import ExtractedTextCard from './components/ExtractedTextCard';
import IngredientsCard from './components/IngredientsCard';
import AllergensCard from './components/AllergensCard';
import AdditivesCard from './components/AdditivesCard';
import NutritionCard from './components/NutritionCard';
import ConsumptionCalculator from './components/ConsumptionCalculator';
import RegulationTable from './components/RegulationTable';
import CompletenessCard from './components/CompletenessCard';
import AiExplanation from './components/AiExplanation';
import LabelChat from './components/LabelChat';
import ProductComparison from './components/ProductComparison';
import RegulatoryGuide from './components/RegulatoryGuide';

import { uploadAndAnalyzeImage, checkBackendHealth } from './services/api';
import './index.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [backendOnline, setBackendOnline] = useState(false);

  // Poll backend health status
  useEffect(() => {
    const verifyHealth = async () => {
      const isHealthy = await checkBackendHealth();
      setBackendOnline(isHealthy);
    };
    verifyHealth();
    const interval = setInterval(verifyHealth, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleAnalyze = async (file, onCompleteCallback) => {
    setIsLoading(true);
    setError('');
    try {
      const result = await uploadAndAnalyzeImage(file);
      setAnalysisResult(result);
      // Smooth scroll to results
      setTimeout(() => {
        window.scrollTo({ top: 380, behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setError(err.message || 'Error occurred while analyzing image.');
    } finally {
      setIsLoading(false);
      if (onCompleteCallback) onCompleteCallback();
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setError('');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="app-layout">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendOnline={backendOnline}
      />

      <main className="main-content">
        {activeTab === 'upload' && (
          <div className="tab-pane">
            <ImageUploader
              onAnalyze={handleAnalyze}
              isLoading={isLoading}
              error={error}
            />

            {analysisResult && (
              <div className="dashboard-results-container">
                <div className="results-toolbar">
                  <div className="results-title-group">
                    <h2>Label Intelligence & Safety Report</h2>
                    <span className="results-timestamp">Generated: {new Date().toLocaleTimeString()}</span>
                  </div>
                  <button className="btn-secondary" onClick={handleReset}>
                    Analyze Another Label ↺
                  </button>
                </div>

                {/* 1. Overview */}
                <OverviewCard data={analysisResult} />

                {/* 2. Raw Extracted Text */}
                <ExtractedTextCard ocr={analysisResult.ocr} />

                {/* 3. Ingredients */}
                <IngredientsCard ingredientsData={analysisResult.ingredients} />

                {/* 4. Allergens */}
                <AllergensCard allergensData={analysisResult.allergens} />

                {/* 5. Additives */}
                <AdditivesCard additivesData={analysisResult.additives} />

                {/* 6. Nutrition */}
                <NutritionCard nutritionData={analysisResult.nutrition} />

                {/* 7. Consumption Calculator */}
                <ConsumptionCalculator nutritionData={analysisResult.nutrition} />

                {/* 8. Global Regulations */}
                <RegulationTable regulationsData={analysisResult.regulations} />

                {/* 9. Label Completeness */}
                <CompletenessCard completenessData={analysisResult.completeness} />

                {/* 10. AI Explanation */}
                <AiExplanation aiExplanation={analysisResult.ai_explanation} />

                {/* 11. Ask About This Label */}
                <LabelChat analysisData={analysisResult} />
              </div>
            )}
          </div>
        )}

        {activeTab === 'compare' && (
          <div className="tab-pane">
            <ProductComparison currentProduct={analysisResult} />
          </div>
        )}

        {activeTab === 'regulations' && (
          <div className="tab-pane">
            <RegulatoryGuide />
          </div>
        )}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <p>
            <strong>FoodLens AI</strong> — AI-Powered Global Food Label Intelligence and Safety Analysis System.
          </p>
          <small>
            For educational and research evaluation. Consult licensed medical professionals for severe dietary allergies and official national gazettes for definitive statutory compliance.
          </small>
        </div>
      </footer>
    </div>
  );
}
