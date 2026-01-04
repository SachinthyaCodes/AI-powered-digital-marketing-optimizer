import React from 'react';
import './Recommendations.css';

const Recommendations = ({ recommendations }) => {
  return (
    <div className="insights-section">
      <h3>AI-Powered Recommendations</h3>
      
      
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
            
            {/* Display improvement metrics if available */}
            {rec.improvement_pct > 0 && (
              <div className="metrics-improvement">
                {/* Likes improvement */}
                {rec.current_likes !== undefined && rec.improved_likes && (
                  <div className="metric-row">
                    <span className="metric-icon">👍</span>
                    <span className="metric-label">Likes:</span>
                    <span className="current">{rec.current_likes.toLocaleString()}</span>
                    <span className="arrow">→</span>
                    <span className="improved">{rec.improved_likes.toLocaleString()}</span>
                    <span className="percentage">+{Math.round(((rec.improved_likes / Math.max(rec.current_likes, 1)) - 1) * 100)}%</span>
                  </div>
                )}
                
                {/* Comments improvement */}
                {rec.current_comments !== undefined && rec.improved_comments && (
                  <div className="metric-row">
                    <span className="metric-icon">💬</span>
                    <span className="metric-label">Comments:</span>
                    <span className="current">{rec.current_comments.toLocaleString()}</span>
                    <span className="arrow">→</span>
                    <span className="improved">{rec.improved_comments.toLocaleString()}</span>
                    <span className="percentage">+{Math.round(((rec.improved_comments / Math.max(rec.current_comments, 1)) - 1) * 100)}%</span>
                  </div>
                )}
                
                {/* Shares improvement */}
                {rec.current_shares !== undefined && rec.improved_shares && (
                  <div className="metric-row">
                    <span className="metric-icon">🔄</span>
                    <span className="metric-label">Shares:</span>
                    <span className="current">{rec.current_shares.toLocaleString()}</span>
                    <span className="arrow">→</span>
                    <span className="improved">{rec.improved_shares.toLocaleString()}</span>
                    <span className="percentage">+{Math.round(((rec.improved_shares / Math.max(rec.current_shares, 1)) - 1) * 100)}%</span>
                  </div>
                )}
                
                {/* Quality Score improvement */}
                {rec.current_quality !== undefined && rec.improved_quality && (
                  <div className="metric-row">
                    <span className="metric-icon">⭐</span>
                    <span className="metric-label">Quality:</span>
                    <span className="current">{rec.current_quality}%</span>
                    <span className="arrow">→</span>
                    <span className="improved">{rec.improved_quality}%</span>
                    <span className="percentage">+{rec.improvement_pct}%</span>
                  </div>
                )}
                
                {/* Overall improvement badge */}
                {!rec.current_likes && !rec.current_comments && !rec.current_shares && !rec.current_quality && (
                  <div className="overall-improvement">
                    <span className="improvement-badge">Potential: +{rec.improvement_pct}%</span>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {recommendations.length === 0 && (
        <div className="no-recommendations">
          <p>✨ Excellent! Your campaign is well-optimized. Keep up the great work!</p>
        </div>
      )}
    </div>
  );
};

export default Recommendations;
