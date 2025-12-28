import React from 'react';
import './ImageUpload.css';

const ImageUpload = ({ imageFile, imagePreview, extracting, onImageUpload }) => {
  return (
    <div className="form-group">
      <label htmlFor="image-upload">Upload Content Image (Optional)</label>
      <div className="image-upload-container">
        <input
          type="file"
          id="image-upload"
          accept="image/*"
          onChange={onImageUpload}
          className="file-input"
        />
        <label htmlFor="image-upload" className="file-label">
          {imageFile ? '✓ Image Uploaded' : '📷 Choose Image'}
        </label>
        {extracting && <span className="extracting-text">Extracting text...</span>}
      </div>
      {imagePreview && (
        <div className="image-preview">
          <img src={imagePreview} alt="Preview" />
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
