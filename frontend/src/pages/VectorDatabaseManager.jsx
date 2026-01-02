import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  Database, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Trash2,
  Activity,
  Zap,
  Cloud,
  TrendingUp
} from 'lucide-react';
import api from '../services/api';

const VectorDatabaseManager = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [vectorStatus, setVectorStatus] = useState(null);
  const [syncHistory, setSyncHistory] = useState([]);
  const [lastSync, setLastSync] = useState(null);
  const [modalStatus, setModalStatus] = useState(null);

  useEffect(() => {
    fetchVectorStatus();
  }, []);

  const fetchVectorStatus = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/rag/status');
      const data = response.data;
      
      setVectorStatus(data);
      setSyncHistory(data.sync_history || []);
      setLastSync(data.last_sync);
      setModalStatus(data.modal_service_status);
    } catch (error) {
      console.error('Error fetching vector status:', error);
    } finally {
      setLoading(false);
    }
  };

  const syncVectorDatabase = async () => {
    try {
      setLoading(true);
      alert('RAG documents are automatically embedded when uploaded. Check the Documents page to upload new files.');
      await fetchVectorStatus();
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearVectorDatabase = async () => {
    if (!confirm('Are you sure you want to clear all vector embeddings? This will remove the RAG capabilities until you upload documents again.')) {
      return;
    }

    try {
      setLoading(true);
      // Delete all document embeddings
      const response = await api.delete('/api/rag/documents/all');
      
      alert('Vector database cleared successfully. Upload documents again to restore RAG capabilities.');
      await fetchVectorStatus();
    } catch (error) {
      console.error('Error clearing vectors:', error);
      alert('Error clearing vector database: ' + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'operational': return 'text-green-600 bg-green-100';
      case 'not_configured': return 'text-orange-600 bg-orange-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'operational': return <CheckCircle className="h-5 w-5" />;
      case 'not_configured': return <AlertCircle className="h-5 w-5" />;
      case 'error': return <AlertCircle className="h-5 w-5" />;
      default: return <Clock className="h-5 w-5" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Never';
    return new Date(timestamp).toLocaleString();
  };

  if (loading && !vectorStatus) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading vector database status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Database className="h-8 w-8 text-blue-600" />
            Vector Database Manager
          </h1>
          <p className="text-gray-600 mt-2">
            Manage semantic search and AI context for your MarketMatic Smart Assistant
          </p>
        </div>

        {/* Modal Service Status */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Cloud className="h-5 w-5 text-blue-600" />
            AI Service Status
          </h3>
          
          {modalStatus ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 ${getStatusColor(modalStatus.status)}`}>
                  {getStatusIcon(modalStatus.status)}
                  {modalStatus.status.charAt(0).toUpperCase() + modalStatus.status.slice(1)}
                </div>
                <span className="text-gray-600">{modalStatus.mode}</span>
              </div>
              
              <p className="text-gray-700">{modalStatus.message}</p>
              
              {modalStatus.status === 'not_configured' && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-800 mb-2">🚀 Setup Required</h4>
                  <p className="text-yellow-700 text-sm mb-3">
                    Deploy your Modal AI service to enable intelligent responses:
                  </p>
                  <div className="bg-gray-900 text-green-400 p-3 rounded text-sm font-mono">
                    cd backend<br/>
                    python deploy_modal_service.py
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-4">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-500 mt-2">Checking AI service status...</p>
            </div>
          )}
        </div>

        {/* Data Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">FAQs</p>
                <p className="text-2xl font-bold text-gray-900">
                  {vectorStatus?.data_counts?.faqs || 0}
                </p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 font-medium text-sm">Q</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Products</p>
                <p className="text-2xl font-bold text-gray-900">
                  {vectorStatus?.data_counts?.products || 0}
                </p>
              </div>
              <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 font-medium text-sm">P</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Policies</p>
                <p className="text-2xl font-bold text-gray-900">
                  {vectorStatus?.data_counts?.policies || 0}
                </p>
              </div>
              <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <span className="text-purple-600 font-medium text-sm">L</span>
              </div>
            </div>
          </div>
        </div>

        {/* Synchronization Controls */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <RefreshCw className="h-5 w-5 text-blue-600" />
            Vector Database Synchronization
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Last Synchronization</p>
                <p className="text-sm text-gray-600">
                  {lastSync ? formatTimestamp(lastSync.timestamp) : 'Never synchronized'}
                </p>
              </div>
              {lastSync && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  lastSync.status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {lastSync.status === 'success' ? 'Success' : 'Failed'}
                </div>
              )}
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-800 mb-2">📚 What gets synchronized?</h4>
              <ul className="text-blue-700 text-sm space-y-1">
                <li>• All active FAQs with questions and answers</li>
                <li>• Product catalog with descriptions and pricing</li>
                <li>• Company policies and procedures</li>
                <li>• Embeddings for semantic search capabilities</li>
              </ul>
            </div>

            <div className="flex gap-4">
              <button
                onClick={syncVectorDatabase}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <Zap className="h-4 w-4" />
                )}
                Sync Now
              </button>

              <button
                onClick={clearVectorDatabase}
                disabled={loading}
                className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Trash2 className="h-4 w-4" />
                Clear Vectors
              </button>

              <button
                onClick={fetchVectorStatus}
                disabled={loading}
                className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh Status
              </button>
            </div>
          </div>
        </div>

        {/* Sync History */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-600" />
            Synchronization History
          </h3>
          
          {syncHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Database className="h-12 w-12 mx-auto mb-2 text-gray-400" />
              <p>No synchronization history yet</p>
              <p className="text-sm">Click "Sync Now" to start building your AI knowledge base</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 text-sm font-medium text-gray-600">Date & Time</th>
                    <th className="text-left py-2 text-sm font-medium text-gray-600">Status</th>
                    <th className="text-left py-2 text-sm font-medium text-gray-600">FAQs</th>
                    <th className="text-left py-2 text-sm font-medium text-gray-600">Products</th>
                    <th className="text-left py-2 text-sm font-medium text-gray-600">Policies</th>
                    <th className="text-left py-2 text-sm font-medium text-gray-600">Total Chunks</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {syncHistory.map((sync, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="py-3 text-sm text-gray-900">
                        {formatTimestamp(sync.timestamp)}
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          sync.status === 'success' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {sync.status}
                        </span>
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {sync.results?.faqs || 0}
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {sync.results?.products || 0}
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {sync.results?.policies || 0}
                      </td>
                      <td className="py-3 text-sm text-gray-600">
                        {sync.results?.total_chunks || 0}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Help Section */}
        <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
          <h4 className="font-medium text-blue-800 mb-3 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            How Vector Database Improves Your Chatbot
          </h4>
          <div className="grid md:grid-cols-2 gap-6 text-blue-700 text-sm">
            <div>
              <h5 className="font-medium mb-2">🎯 Semantic Understanding</h5>
              <p>Finds relevant information even when customers don't use exact keywords</p>
            </div>
            <div>
              <h5 className="font-medium mb-2">⚡ Faster Responses</h5>
              <p>Pre-computed embeddings enable instant context retrieval</p>
            </div>
            <div>
              <h5 className="font-medium mb-2">🌍 Multilingual Support</h5>
              <p>Works across English, Sinhala, and Tamil languages</p>
            </div>
            <div>
              <h5 className="font-medium mb-2">📈 Better Accuracy</h5>
              <p>AI responses are more relevant and contextually appropriate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VectorDatabaseManager;