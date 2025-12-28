import React from 'react';
import './FeatureImportance.css';

const FeatureImportance = ({ featureImportance }) => {
  const maxImportance = Math.max(...Object.values(featureImportance));

  return (
    <div className="feature-importance-section">
      <h3>📈 Feature Importance</h3>
      <div className="importance-bars">
        {Object.entries(featureImportance).map(([feature, importance], index) => (
          <div key={index} className="importance-item">
            <span className="feature-name">{feature.replace(/_/g, ' ')}</span>
            <div className="importance-bar-container">
              <div 
                className="importance-bar" 
                style={{ width: `${(importance / maxImportance) * 100}%` }}
              />
            </div>
            <span className="importance-value">{importance.toFixed(4)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeatureImportance;
