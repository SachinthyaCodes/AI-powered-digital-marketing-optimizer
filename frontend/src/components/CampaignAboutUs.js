import React from 'react';
import './CampaignAboutUs.css';

const CampaignAboutUs = ({ onNavigate }) => {
  return (
    <div className="about-us-container">
      <div className="about-us-content">
        <h1 className="about-us-title">
          Predicting Social Media Campaign Success Before Publishing
        </h1>
        <p className="about-us-description">
          Our AI-powered system helps Sri Lankan SMEs optimize social media campaigns 
          by predicting engagement, analyzing content in Sinhala and English, and 
          providing smart recommendations saving time, money, and effort.
        </p>
        <button className="btn-try-now" onClick={onNavigate}>
          Try Now
        </button>
      </div>
    </div>
  );
};

export default CampaignAboutUs;
