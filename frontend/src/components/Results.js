import React from 'react';
import PredictionsGrid from './PredictionsGrid';
import Recommendations from './Recommendations';
import HashtagSuggestions from './HashtagSuggestions';
import TimingAnalysis from './TimingAnalysis';
import FeatureImportance from './FeatureImportance';
import './Results.css';

const Results = ({ results, predictionHistory, loadingHistory, onDelete }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="results-container">
      {/* Current Prediction Results */}
      {results && (
        <div className="results-section current-results">
          <h2>📊 Latest Prediction Results</h2>
          
          <PredictionsGrid predictions={results.predictions} />
          
          <Recommendations recommendations={results.recommendations} />
          
          <HashtagSuggestions hashtags={results.hashtag_suggestions} />
          
          <TimingAnalysis timingAnalysis={results.timing_analysis} />
          
          <FeatureImportance featureImportance={results.feature_importance} />
        </div>
      )}

      {/* Prediction History */}
      <div className="history-section">
        <h2>📜 Prediction History</h2>
        
        {loadingHistory ? (
          <div className="loading-history">
            <div className="spinner"></div>
            <p>Loading history...</p>
          </div>
        ) : predictionHistory && predictionHistory.length > 0 ? (
          <div className="history-grid">
            {predictionHistory.map((prediction, index) => (
              <div key={prediction._id || index} className="history-card">
                <div className="history-header">
                  <span className="history-number">#{index + 1}</span>
                  <span className="history-date">{formatDate(prediction.created_at)}</span>
                  <button 
                    className="delete-btn"
                    onClick={() => onDelete(prediction._id)}
                    title="Delete this prediction"
                  >
                    🗑️ Delete
                  </button>
                </div>

                <div className="history-content">
                  <div className="history-info">
                    <div className="info-row">
                      <span className="label">Platform:</span>
                      <span className="value">{prediction.platform || 'N/A'}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Caption:</span>
                      <span className="value caption-preview">{prediction.caption || 'No caption'}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Followers:</span>
                      <span className="value">{prediction.followers?.toLocaleString() || 'N/A'}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Ad Boost:</span>
                      <span className="value">{prediction.ad_boost ? '✅ Yes' : '❌ No'}</span>
                    </div>
                  </div>

                  {prediction.predictions && (
                    <div className="history-predictions">
                      <h4>Predicted Metrics:</h4>
                      <div className="metrics-grid">
                        <div className="metric-item">
                          <span className="metric-icon">👍</span>
                          <span className="metric-label">Likes</span>
                          <span className="metric-value">{prediction.predictions.likes?.toLocaleString() || 0}</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-icon">💬</span>
                          <span className="metric-label">Comments</span>
                          <span className="metric-value">{prediction.predictions.comments?.toLocaleString() || 0}</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-icon">🔄</span>
                          <span className="metric-label">Shares</span>
                          <span className="metric-value">{prediction.predictions.shares?.toLocaleString() || 0}</span>
                        </div>
                        <div className="metric-item">
                          <span className="metric-icon">🖱️</span>
                          <span className="metric-label">Clicks</span>
                          <span className="metric-value">{prediction.predictions.clicks?.toLocaleString() || 0}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  {prediction.hashtag_suggestions && prediction.hashtag_suggestions.length > 0 && (
                    <div className="history-hashtags">
                      <h4>Hashtags:</h4>
                      <div className="hashtags-preview">
                        {prediction.hashtag_suggestions.slice(0, 5).map((tag, i) => (
                          <span key={i} className="hashtag-mini">{tag}</span>
                        ))}
                        {prediction.hashtag_suggestions.length > 5 && (
                          <span className="more-tags">+{prediction.hashtag_suggestions.length - 5} more</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="no-history">
            <p>📭 No prediction history yet. Make your first prediction above!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;
