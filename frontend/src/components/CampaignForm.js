import React from 'react';
import ImageUpload from './ImageUpload';
import './CampaignForm.css';

const CampaignForm = ({
  formData,
  imageFile,
  imagePreview,
  extracting,
  loading,
  error,
  onInputChange,
  onImageUpload,
  onSubmit,
  onReset
}) => {
  return (
    <div className="form-section">
      <h2>Campaign Details</h2>
      <form onSubmit={onSubmit}>
        <div className="form-group">
          <label htmlFor="caption">Caption</label>
          <textarea
            id="caption"
            name="caption"
            value={formData.caption}
            onChange={onInputChange}
            placeholder="Enter your post caption..."
            required
            rows="3"
          />
        </div>

        <ImageUpload
          imageFile={imageFile}
          imagePreview={imagePreview}
          extracting={extracting}
          onImageUpload={onImageUpload}
        />

        <div className="form-group">
          <label htmlFor="content">Content (Image Text)</label>
          <textarea
            id="content"
            name="content"
            value={formData.content}
            onChange={onInputChange}
            placeholder="Extracted text from image or enter manually..."
            required
            rows="4"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="platform">Platform</label>
            <select
              id="platform"
              name="platform"
              value={formData.platform}
              onChange={onInputChange}
              required
            >
              <option value="Facebook">Facebook</option>
              <option value="Instagram">Instagram</option>
              <option value="TikTok">TikTok</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="post_date">Post Date</label>
            <input
              type="date"
              id="post_date"
              name="post_date"
              value={formData.post_date}
              onChange={onInputChange}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="post_time">Post Time</label>
            <input
              type="time"
              id="post_time"
              name="post_time"
              value={formData.post_time}
              onChange={onInputChange}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="followers">Followers</label>
            <input
              type="number"
              id="followers"
              name="followers"
              value={formData.followers}
              onChange={onInputChange}
              placeholder="Number of followers"
              required
              min="0"
            />
          </div>

          <div className="form-group checkbox-group">
            <label htmlFor="ad_boost" className="checkbox-label">
              <input
                type="checkbox"
                id="ad_boost"
                name="ad_boost"
                checked={formData.ad_boost === '1' || formData.ad_boost === 1}
                onChange={(e) => onInputChange({
                  target: {
                    name: 'ad_boost',
                    value: e.target.checked ? '1' : '0'
                  }
                })}
              />
              <span className="checkbox-text">Ad Boost</span>
            </label>
          </div>
        </div>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <div className="button-group">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Analyzing...' : '🔮 Predict Performance'}
          </button>
          <button type="button" onClick={onReset} className="btn btn-secondary">
            🔄 Reset
          </button>
        </div>
      </form>
    </div>
  );
};

export default CampaignForm;
