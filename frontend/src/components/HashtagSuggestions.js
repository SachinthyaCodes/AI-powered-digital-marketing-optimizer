import React from 'react';
import './HashtagSuggestions.css';

const HashtagSuggestions = ({ hashtags }) => {
  return (
    <div className="hashtags-section">
      <h3>🏷️ Suggested Hashtags</h3>
      <div className="hashtags-container">
        {hashtags.map((tag, index) => (
          <span key={index} className="hashtag-badge">{tag}</span>
        ))}
      </div>
    </div>
  );
};

export default HashtagSuggestions;
