import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import Header from './components/Header';
import CampaignAboutUs from './components/CampaignAboutUs';
import CampaignForm from './components/CampaignForm';
import Results from './components/Results';
import Footer from './components/Footer';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [currentPage, setCurrentPage] = useState('about');
  
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
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);

  // Load prediction history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoadingHistory(true);
      const response = await axios.get(`${API_BASE_URL}/history`);
      if (response.data.success) {
        setPredictionHistory(response.data.history);
      }
    } catch (err) {
      console.error('Error loading history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const deletePrediction = async (predictionId) => {
    if (!window.confirm('Are you sure you want to delete this prediction?')) {
      return;
    }

    try {
      const response = await axios.delete(`${API_BASE_URL}/history/${predictionId}`);
      if (response.data.success) {
        // Remove from local state
        setPredictionHistory(prev => prev.filter(p => p._id !== predictionId));
        // Show success message
        alert('Prediction deleted successfully!');
      }
    } catch (err) {
      console.error('Error deleting prediction:', err);
      alert('Failed to delete prediction. Please try again.');
    }
  };

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
        // Reload history to show the new prediction
        loadHistory();
        // Scroll to top smoothly after results are loaded
        setTimeout(() => {
          window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 100);
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

  const handleNavigateToCampaign = () => {
    setCurrentPage('campaign');
  };

  return (
    <div className={`App ${currentPage === 'about' ? 'fullscreen' : ''}`}>
      {currentPage !== 'about' && <Header />}

      <div className="container">
        {currentPage === 'about' ? (
          <CampaignAboutUs onNavigate={handleNavigateToCampaign} />
        ) : (
          <>
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

            <Results 
              results={results} 
              predictionHistory={predictionHistory}
              loadingHistory={loadingHistory}
              onDelete={deletePrediction}
            />
          </>
        )}
      </div>

      {currentPage !== 'about' && <Footer />}
    </div>
  );
}

export default App;
