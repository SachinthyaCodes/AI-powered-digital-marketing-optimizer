import React, { useState } from 'react';
import PredictionsGrid from './PredictionsGrid';
import Recommendations from './Recommendations';
import HashtagSuggestions from './HashtagSuggestions';
import TimingAnalysis from './TimingAnalysis';
import FeatureImportance from './FeatureImportance';
import './Results.css';

const Results = ({ results, predictionHistory, loadingHistory, onDelete }) => {
  const [viewingPrediction, setViewingPrediction] = useState(null);
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
          <h2>Latest Prediction Results</h2>
          
          <div className="result-card fade-in">
            <PredictionsGrid predictions={results.predictions} />
          </div>
          
          <div className="result-card fade-in delay-1">
            <div className="ai-recommendations-highlight">
              
              <h3 className="recommendations-title">Smart Recommendations</h3>
            </div>
            <Recommendations recommendations={results.recommendations} />
          </div>
          
          <div className="result-card fade-in delay-2">
            <HashtagSuggestions hashtags={results.hashtag_suggestions} />
          </div>
          
          <div className="result-card fade-in delay-3">
            <TimingAnalysis timingAnalysis={results.timing_analysis} />
          </div>
          
          <div className="result-card fade-in delay-4">
            <FeatureImportance featureImportance={results.feature_importance} />
          </div>
        </div>
      )}

      {/* Full Prediction Details Modal */}
      {viewingPrediction && (
        <div className="modal-overlay" onClick={() => setViewingPrediction(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2> Prediction Details</h2>
              <button className="close-modal" onClick={() => setViewingPrediction(null)}>×</button>
            </div>
            
            <div className="modal-body">
              {/* Input Details */}
              <div className="detail-section">
                <h3>📝 Input Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Platform:</span>
                    <span className="detail-value">{viewingPrediction.platform || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Followers:</span>
                    <span className="detail-value">{viewingPrediction.followers?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Ad Boost:</span>
                    <span className="detail-value">{viewingPrediction.ad_boost ? '✅ Yes' : '❌ No'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Post Time:</span>
                    <span className="detail-value">{viewingPrediction.post_time || 'N/A'}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Post Date:</span>
                    <span className="detail-value">{viewingPrediction.post_date || 'N/A'}</span>
                  </div>
                  <div className="detail-item full-width">
                    <span className="detail-label">Caption:</span>
                    <span className="detail-value">{viewingPrediction.caption || 'No caption'}</span>
                  </div>
                  <div className="detail-item full-width">
                    <span className="detail-label">Content:</span>
                    <span className="detail-value">{viewingPrediction.content || 'No content'}</span>
                  </div>
                </div>
              </div>

              {/* Predictions */}
              {viewingPrediction.predictions && (
                <div className="detail-section">
                  <h3>Predictions</h3>
                  <PredictionsGrid predictions={viewingPrediction.predictions} />
                </div>
              )}

              {/* AI-Powered Recommendations */}
              {viewingPrediction.recommendations && (
                <div className="detail-section">
                  <h3>AI-Powered Recommendations</h3>
                  <Recommendations recommendations={viewingPrediction.recommendations} />
                </div>
              )}

              {/* Hashtag Suggestions */}
              {viewingPrediction.hashtag_suggestions && (
                <div className="detail-section">
                  <h3>Hashtag Suggestions</h3>
                  <HashtagSuggestions hashtags={viewingPrediction.hashtag_suggestions} />
                </div>
              )}

              {/* Optimal Posting Times Analysis */}
              {viewingPrediction.timing_analysis && (
                <div className="detail-section">
                  <h3>Optimal Posting Times Analysis</h3>
                  <TimingAnalysis timingAnalysis={viewingPrediction.timing_analysis} />
                </div>
              )}

              {/* Feature Importance */}
              {viewingPrediction.feature_importance && (
                <div className="detail-section">
                  <h3>Feature Importance</h3>
                  <FeatureImportance featureImportance={viewingPrediction.feature_importance} />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Prediction History */}
      <div className="history-section">
        <h2> Prediction History</h2>
        
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
                  <div className="history-actions">
                    <button 
                      className="view-btn"
                      onClick={() => setViewingPrediction(prediction)}
                      title="View full details"
                    >
                      👁️ View
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => onDelete(prediction._id)}
                      title="Delete this prediction"
                    >
                      🗑️ Delete
                    </button>
                  </div>
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
