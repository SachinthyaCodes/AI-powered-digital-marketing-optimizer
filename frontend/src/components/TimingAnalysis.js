import React from 'react';
import './TimingAnalysis.css';

const TimingAnalysis = ({ timingAnalysis }) => {
  return (
    <div className="timing-analysis-section">
      <h3>⏰ Optimal Posting Times</h3>
      <div className="timing-grid">
        <div className="timing-card">
          <h4>Best Days</h4>
          <ul>
            {timingAnalysis.best_days.map((day, index) => (
              <li key={index}>✅ {day}</li>
            ))}
          </ul>
        </div>

        <div className="timing-card">
          <h4>Best Hours</h4>
          <div className="hours-list">
            {timingAnalysis.best_hours.map((hour, index) => (
              <span key={index} className="hour-badge">{hour}:00</span>
            ))}
          </div>
        </div>

        <div className="timing-card">
          <h4>Avoid</h4>
          <ul>
            {timingAnalysis.worst_days.map((day, index) => (
              <li key={index}>❌ {day}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="timing-insights">
        <h4>Key Insights</h4>
        {Object.entries(timingAnalysis.insights).map(([key, value], index) => (
          <p key={index}><strong>{key.replace(/_/g, ' ')}:</strong> {value}</p>
        ))}
      </div>
    </div>
  );
};

export default TimingAnalysis;
