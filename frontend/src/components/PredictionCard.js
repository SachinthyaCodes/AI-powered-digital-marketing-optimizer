import React from 'react';import './PredictionCard.css';
const PredictionCard = ({ icon, label, value, className }) => {
  return (
    <div className={`prediction-card ${className}`}>
      <div className="prediction-icon">{icon}</div>
      <div className="prediction-label">{label}</div>
      <div className="prediction-value">{value}</div>
    </div>
  );
};

export default PredictionCard;
