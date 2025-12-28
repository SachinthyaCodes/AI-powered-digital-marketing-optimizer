import React from 'react';
import PredictionCard from './PredictionCard';
import './PredictionsGrid.css';

const PredictionsGrid = ({ predictions }) => {
  return (
    <div className="predictions-grid">
      <PredictionCard
        icon="❤️"
        label="Likes"
        value={predictions.likes.toLocaleString()}
        className="likes"
      />
      <PredictionCard
        icon="💬"
        label="Comments"
        value={predictions.comments.toLocaleString()}
        className="comments"
      />
      <PredictionCard
        icon="🔄"
        label="Shares"
        value={predictions.shares.toLocaleString()}
        className="shares"
      />
      <PredictionCard
        icon="👆"
        label="Clicks"
        value={predictions.clicks.toLocaleString()}
        className="clicks"
      />
      <PredictionCard
        icon="⭐"
        label="Quality Score"
        value={predictions.timing_quality_score.toFixed(2)}
        className="quality"
      />
    </div>
  );
};

export default PredictionsGrid;
