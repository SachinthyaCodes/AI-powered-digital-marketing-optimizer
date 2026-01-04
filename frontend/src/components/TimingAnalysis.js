import React from 'react';
import './TimingAnalysis.css';

const TimingAnalysis = ({ timingAnalysis }) => {
  const {
    best_days = [],
    best_hours = [],
    worst_days = [],
    insights = {},
    current_metrics = {},
    optimal_predictions = {},
    improvement_potential = {},
    timing_analysis: timingDetails = {}
  } = timingAnalysis || {};

  return (
    <div className="timing-analysis-section">
      <h3>Optimal Posting Times Analysis</h3>
      
      {/* Current vs Optimal Performance */}
      {current_metrics && optimal_predictions && (
        <div className="performance-comparison">
          <h4>Performance: Current vs Optimal Timing</h4>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">👍</span>
                <span className="metric-name">Likes</span>
              </div>
              <div className="metric-values">
                <div className="current-value">
                  <span className="label">Current</span>
                  <span className="value">{(current_metrics.likes || 0).toLocaleString()}</span>
                </div>
                <div className="arrow">→</div>
                <div className="optimal-value">
                  <span className="label">Optimal</span>
                  <span className="value">{(optimal_predictions.likes || 0).toLocaleString()}</span>
                </div>
              </div>
              {optimal_predictions.likes > current_metrics.likes && (
                <div className="improvement-badge">
                  +{Math.round(((optimal_predictions.likes / Math.max(current_metrics.likes, 1)) - 1) * 100)}%
                </div>
              )}
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">💬</span>
                <span className="metric-name">Comments</span>
              </div>
              <div className="metric-values">
                <div className="current-value">
                  <span className="label">Current</span>
                  <span className="value">{(current_metrics.comments || 0).toLocaleString()}</span>
                </div>
                <div className="arrow">→</div>
                <div className="optimal-value">
                  <span className="label">Optimal</span>
                  <span className="value">{(optimal_predictions.comments || 0).toLocaleString()}</span>
                </div>
              </div>
              {optimal_predictions.comments > current_metrics.comments && (
                <div className="improvement-badge">
                  +{Math.round(((optimal_predictions.comments / Math.max(current_metrics.comments, 1)) - 1) * 100)}%
                </div>
              )}
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">🔄</span>
                <span className="metric-name">Shares</span>
              </div>
              <div className="metric-values">
                <div className="current-value">
                  <span className="label">Current</span>
                  <span className="value">{(current_metrics.shares || 0).toLocaleString()}</span>
                </div>
                <div className="arrow">→</div>
                <div className="optimal-value">
                  <span className="label">Optimal</span>
                  <span className="value">{(optimal_predictions.shares || 0).toLocaleString()}</span>
                </div>
              </div>
              {optimal_predictions.shares > current_metrics.shares && (
                <div className="improvement-badge">
                  +{Math.round(((optimal_predictions.shares / Math.max(current_metrics.shares, 1)) - 1) * 100)}%
                </div>
              )}
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-icon">⭐</span>
                <span className="metric-name">Quality Score</span>
              </div>
              <div className="metric-values">
                <div className="current-value">
                  <span className="label">Current</span>
                  <span className="value">{Math.round((current_metrics.quality_score || 0) * 100)}%</span>
                </div>
                <div className="arrow">→</div>
                <div className="optimal-value">
                  <span className="label">Optimal</span>
                  <span className="value">{Math.round((optimal_predictions.quality_score || 0) * 100)}%</span>
                </div>
              </div>
              {optimal_predictions.quality_score > current_metrics.quality_score && (
                <div className="improvement-badge">
                  +{Math.round(((optimal_predictions.quality_score / Math.max(current_metrics.quality_score, 0.01)) - 1) * 100)}%
                </div>
              )}
            </div>
          </div>

          {improvement_potential && improvement_potential.percentage > 0 && (
            <div className="overall-improvement">
              <span className="improvement-icon"></span>
              <span className="improvement-message">
                With optimal timing, your metrics could improve by <strong>{improvement_potential.percentage}%</strong>
              </span>
            </div>
          )}
        </div>
      )}

      {/* Current Timing Status */}
      {timingDetails && timingDetails.current_hour !== undefined && (
        <div className="timing-status">
          <div className="status-card current-timing">
            <h5>📅 Your Selected Time</h5>
            <div className="timing-info">
              <div className="info-item">
                <span className="info-label">Day:</span>
                <span className="info-value">{timingDetails.current_day}</span>
                <span className="score-badge day-score">Score: {timingDetails.day_score}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Hour:</span>
                <span className="info-value">{timingDetails.current_hour}:00</span>
                <span className="score-badge hour-score">Score: {timingDetails.hour_score}</span>
              </div>
            </div>
          </div>
          <div className="status-card optimal-timing">
            <h5>🎯 Recommended Time</h5>
            <div className="timing-info">
              <div className="info-item">
                <span className="info-label">Day:</span>
                <span className="info-value">{timingDetails.optimal_day}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Hour:</span>
                <span className="info-value">{timingDetails.optimal_hour}:00</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Best Days, Hours, and Days to Avoid */}
      <div className="timing-grid">
        <div className="timing-card best-days-card">
          <h4>✅ Best Days</h4>
          <ul>
            {best_days.map((day, index) => (
              <li key={index}>
                <span className="rank">#{index + 1}</span>
                <span className="day-name">{day}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="timing-card best-hours-card">
          <h4>🕐 Best Hours</h4>
          <div className="hours-list">
            {best_hours.map((hour, index) => (
              <span key={index} className="hour-badge">
                {String(hour).padStart(2, '0')}:00
              </span>
            ))}
          </div>
        </div>

        <div className="timing-card avoid-card">
          <h4>❌ Days to Avoid</h4>
          <ul>
            {worst_days.map((day, index) => (
              <li key={index}>
                <span className="avoid-icon">⚠️</span>
                <span className="day-name">{day}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Key Insights */}
      <div className="timing-insights">
        <h4>Key Insights & Recommendations</h4>
        <div className="insights-container">
          {Object.entries(insights).map(([key, value], index) => (
            <div key={index} className="insight-item">
              <div className="insight-header">
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </div>
              <div className="insight-content">{value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TimingAnalysis;
