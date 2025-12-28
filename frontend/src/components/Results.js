import React from 'react';
import PredictionsGrid from './PredictionsGrid';
import Recommendations from './Recommendations';
import HashtagSuggestions from './HashtagSuggestions';
import TimingAnalysis from './TimingAnalysis';
import FeatureImportance from './FeatureImportance';
import './Results.css';

const Results = ({ results }) => {
  if (!results) return null;

  return (
    <div className="results-section">
      <h2>📊 Prediction Results</h2>
      
      <PredictionsGrid predictions={results.predictions} />
      
      <Recommendations recommendations={results.recommendations} />
      
      <HashtagSuggestions hashtags={results.hashtag_suggestions} />
      
      <TimingAnalysis timingAnalysis={results.timing_analysis} />
      
      <FeatureImportance featureImportance={results.feature_importance} />
    </div>
  );
};

export default Results;
