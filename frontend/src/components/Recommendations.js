import React from 'react';
import './Recommendations.css';

const Recommendations = ({ recommendations }) => {
  return (
    <div className="insights-section">
      <h3>💡 Recommendations to Improve Performance</h3>
      <div className="recommendations-list">
        {recommendations.map((rec, index) => (
          <div key={index} className={`recommendation-item impact-${rec.impact.toLowerCase()}`}>
            <div className="recommendation-header">
              <span className="recommendation-category">{rec.category}</span>
              <span className={`impact-badge impact-${rec.impact.toLowerCase()}`}>
                {rec.impact} Impact
              </span>
            </div>
            <p className="recommendation-text">{rec.suggestion}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Recommendations;
