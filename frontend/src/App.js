import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';
import CampaignForm from './components/CampaignForm';
import Results from './components/Results';
import Footer from './components/Footer';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [formData, setFormData] = useState({
    caption: '',
    content: '',
    platform: 'Facebook',
    post_date: '',
    post_time: '',
    followers: '',
    ad_boost: 0
  });

  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImageFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Extract text from image
    setExtracting(true);
    setError(null);

    try {
      const base64Image = await convertToBase64(file);
      const response = await axios.post(`${API_BASE_URL}/extract-text`, {
        image: base64Image
      });

      if (response.data.success) {
        setFormData(prev => ({
          ...prev,
          content: response.data.text
        }));
      }
    } catch (err) {
      console.error('Error extracting text:', err);
      setError('Failed to extract text from image. You can enter content manually.');
    } finally {
      setExtracting(false);
    }
  };

  const convertToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/predict`, formData);
      
      if (response.data.success) {
        setResults(response.data);
      }
    } catch (err) {
      console.error('Prediction error:', err);
      setError(err.response?.data?.error || 'Failed to make prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      caption: '',
      content: '',
      platform: 'Facebook',
      post_date: '',
      post_time: '',
      followers: '',
      ad_boost: 0
    });
    setImageFile(null);
    setImagePreview(null);
    setResults(null);
    setError(null);
  };

  return (
    <div className="App">
      <Header />

      <div className="container">
        <CampaignForm
          formData={formData}
          imageFile={imageFile}
          imagePreview={imagePreview}
          extracting={extracting}
          loading={loading}
          error={error}
          onInputChange={handleInputChange}
          onImageUpload={handleImageUpload}
          onSubmit={handleSubmit}
          onReset={resetForm}
        />

        <Results results={results} />
      </div>

      <Footer />
    </div>
  );
}

export default App;
