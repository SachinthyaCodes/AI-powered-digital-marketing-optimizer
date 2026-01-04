import React, { useState } from 'react';
import './HashtagSuggestions.css';

const HashtagSuggestions = ({ hashtags }) => {
  const [copiedIndex, setCopiedIndex] = useState(null);

  const copyToClipboard = (tag, index) => {
    navigator.clipboard.writeText(tag);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const copyAllHashtags = () => {
    const allTags = hashtags.join(' ');
    navigator.clipboard.writeText(allTags);
    setCopiedIndex('all');
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="hashtags-section">
      <div className="hashtags-header">
        <h3>Suggested Hashtags ({hashtags?.length || 0})</h3>
        {hashtags && hashtags.length > 0 && (
          <button className="copy-all-btn" onClick={copyAllHashtags}>
            {copiedIndex === 'all' ? '✓ Copied!' : '📋 Copy All'}
          </button>
        )}
      </div>
      <div className="hashtags-container">
        {hashtags && hashtags.length > 0 ? (
          hashtags.map((tag, index) => (
            <span 
              key={index} 
              className="hashtag-badge"
              onClick={() => copyToClipboard(tag, index)}
              title="Click to copy"
            >
              {tag}
              {copiedIndex === index && <span className="copied-indicator">✓</span>}
            </span>
          ))
        ) : (
          <p className="no-hashtags">No hashtags available</p>
        )}
      </div>
    </div>
  );
};

export default HashtagSuggestions;
