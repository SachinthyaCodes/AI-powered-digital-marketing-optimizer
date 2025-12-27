import { useState, useEffect } from 'react';
import { MessageSquare, Settings, FileQuestion, Package, FileText, Save, Plus, Trash2, Edit, Upload, X, FolderOpen } from 'lucide-react';
import api from '../services/api';
import DocumentManager from './DocumentManager';
import SimpleChatWidget, { ChatButton } from '../components/SimpleChatWidget';
import { useAuth } from '../context/AuthContext';

export default function BotManagement() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('config');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Bot Configuration State
  const [config, setConfig] = useState({
    welcome_message: { en: '', si: '' },
    fallback_message: { en: '', si: '' },
    language_support: ['en', 'si'],
    rag_enabled: true,
    nlp_enabled: true,
    response_mode: 'hybrid', // 'documents_only' or 'hybrid'
    documents_only_message: { en: '', si: '' },
    use_general_knowledge: true,
    business_hours: { start: '09:00', end: '18:00' },
    offline_message: { en: '', si: '' }
  });

  // FAQs State
  const [faqs, setFaqs] = useState([]);
  const [editingFaq, setEditingFaq] = useState(null);
  const [newFaq, setNewFaq] = useState({ question: '', answer: '', language: 'en', category: '' });

  // Products State
  const [products, setProducts] = useState([]);
  const [editingProduct, setEditingProduct] = useState(null);
  const [newProduct, setNewProduct] = useState({
    name: '', description: '', price: '', stock: '', category: '', images: []
  });
  const [uploadingImages, setUploadingImages] = useState(false);

  // Policies State
  const [policies, setPolicies] = useState([]);
  const [editingPolicy, setEditingPolicy] = useState(null);
  const [newPolicy, setNewPolicy] = useState({ title: '', content: '', policy_type: 'general' });

  // Upload states
  const [uploadingFile, setUploadingFile] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadType, setUploadType] = useState(''); // 'faq', 'product', 'policy'

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'config') {
        const res = await api.get('/api/bot/config');
        if (res.data) {
          // Ensure all nested objects exist
          setConfig({
            welcome_message: res.data.config?.welcome_message || { en: '', si: '' },
            fallback_message: res.data.config?.fallback_message || { en: '', si: '' },
            language_support: res.data.config?.language_support || ['en', 'si'],
            rag_enabled: res.data.config?.rag_enabled !== undefined ? res.data.config.rag_enabled : true,
            nlp_enabled: res.data.config?.nlp_enabled !== undefined ? res.data.config.nlp_enabled : true,
            response_mode: res.data.config?.response_mode || 'hybrid',
            documents_only_message: res.data.config?.documents_only_message || { en: '', si: '' },
            use_general_knowledge: res.data.config?.use_general_knowledge !== undefined ? res.data.config.use_general_knowledge : true,
            business_hours: res.data.config?.business_hours || { start: '09:00', end: '18:00' },
            offline_message: res.data.config?.offline_message || { en: '', si: '' }
          });
        }
      } else if (activeTab === 'faqs') {
        const res = await api.get('/api/bot/faqs');
        setFaqs(Array.isArray(res.data.faqs) ? res.data.faqs : (Array.isArray(res.data) ? res.data : []));
      } else if (activeTab === 'products') {
        const res = await api.get('/api/bot/products');
        setProducts(Array.isArray(res.data.products) ? res.data.products : (Array.isArray(res.data) ? res.data : []));
      } else if (activeTab === 'policies') {
        const res = await api.get('/api/bot/policies');
        setPolicies(Array.isArray(res.data.policies) ? res.data.policies : (Array.isArray(res.data) ? res.data : []));
      }
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to load data');
      // Ensure arrays are set even on error
      if (activeTab === 'faqs') setFaqs([]);
      if (activeTab === 'products') setProducts([]);
      if (activeTab === 'policies') setPolicies([]);
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 5000);
  };

  // Configuration Handlers
  const handleSaveConfig = async () => {
    setLoading(true);
    try {
      await api.put('/api/bot/config', config);
      showMessage('success', 'Configuration saved successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  // File Upload Handlers
  const handleFileUpload = async (file, documentType) => {
    setUploadingFile(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', documentType);

      await api.post('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });

      showMessage('success', `${documentType.toUpperCase()} file uploaded and processed successfully`);
      
      // Reload the current tab data
      loadData();
    } catch (error) {
      showMessage('error', error.response?.data?.error || 'Failed to upload file');
    } finally {
      setUploadingFile(false);
    }
  };

  const openUploadModal = (type) => {
    setUploadType(type);
    setShowUploadModal(true);
  };

  // FAQ Handlers
  const handleAddFaq = async () => {
    if (!newFaq.question || !newFaq.answer) {
      showMessage('error', 'Question and answer are required');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/api/bot/faqs', newFaq);
      setFaqs([...faqs, res.data]);
      setNewFaq({ question: '', answer: '', language: 'en', category: '' });
      showMessage('success', 'FAQ added successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to add FAQ');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateFaq = async (id) => {
    setLoading(true);
    try {
      const res = await api.put(`/api/bot/faqs/${id}`, editingFaq);
      setFaqs(faqs.map(f => f._id === id ? res.data : f));
      setEditingFaq(null);
      showMessage('success', 'FAQ updated successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to update FAQ');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFaq = async (id) => {
    if (!confirm('Are you sure you want to delete this FAQ?')) return;
    setLoading(true);
    try {
      await api.delete(`/api/bot/faqs/${id}`);
      setFaqs(faqs.filter(f => f._id !== id));
      showMessage('success', 'FAQ deleted successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to delete FAQ');
    } finally {
      setLoading(false);
    }
  };

  // Product Handlers
  const handleImageUpload = async (e, productId = null) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploadingImages(true);
    const formData = new FormData();
    files.forEach(file => formData.append('images', file));

    try {
      let res;
      if (productId) {
        res = await api.post(`/api/bot/products/${productId}/images`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setProducts(products.map(p => p._id === productId ? res.data : p));
      } else {
        res = await api.post('/api/bot/upload-image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        setNewProduct({ ...newProduct, images: res.data.urls });
      }
      showMessage('success', 'Images uploaded successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to upload images');
    } finally {
      setUploadingImages(false);
    }
  };

  const handleAddProduct = async () => {
    if (!newProduct.name || !newProduct.price) {
      showMessage('error', 'Name and price are required');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/api/bot/products', {
        ...newProduct,
        price: parseFloat(newProduct.price),
        stock: parseInt(newProduct.stock) || 0
      });
      setProducts([...products, res.data]);
      setNewProduct({ name: '', description: '', price: '', stock: '', category: '', images: [] });
      showMessage('success', 'Product added successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to add product');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProduct = async (id) => {
    setLoading(true);
    try {
      const res = await api.put(`/api/bot/products/${id}`, {
        ...editingProduct,
        price: parseFloat(editingProduct.price),
        stock: parseInt(editingProduct.stock) || 0
      });
      setProducts(products.map(p => p._id === id ? res.data : p));
      setEditingProduct(null);
      showMessage('success', 'Product updated successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to update product');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProduct = async (id) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    setLoading(true);
    try {
      await api.delete(`/api/bot/products/${id}`);
      setProducts(products.filter(p => p._id !== id));
      showMessage('success', 'Product deleted successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to delete product');
    } finally {
      setLoading(false);
    }
  };

  // Policy Handlers
  const handleAddPolicy = async () => {
    if (!newPolicy.title || !newPolicy.content) {
      showMessage('error', 'Title and content are required');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/api/bot/policies', newPolicy);
      setPolicies([...policies, res.data]);
      setNewPolicy({ title: '', content: '', policy_type: 'general' });
      showMessage('success', 'Policy added successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to add policy');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePolicy = async (id) => {
    setLoading(true);
    try {
      const res = await api.put(`/api/bot/policies/${id}`, editingPolicy);
      setPolicies(policies.map(p => p._id === id ? res.data : p));
      setEditingPolicy(null);
      showMessage('success', 'Policy updated successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to update policy');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePolicy = async (id) => {
    if (!confirm('Are you sure you want to delete this policy?')) return;
    setLoading(true);
    try {
      await api.delete(`/api/bot/policies/${id}`);
      setPolicies(policies.filter(p => p._id !== id));
      showMessage('success', 'Policy deleted successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to delete policy');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6 mb-6">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-8 h-8 text-purple-600" />
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-800">Bot Management</h1>
              <p className="text-sm sm:text-base text-gray-600">Configure your AI assistant</p>
            </div>
          </div>
        </div>

        {/* Message Alert */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6 overflow-x-auto">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('config')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'config' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <Settings className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">Configuration</span>
            </button>
            <button
              onClick={() => setActiveTab('faqs')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'faqs' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <FileQuestion className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">FAQs</span>
            </button>
            <button
              onClick={() => setActiveTab('products')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'products' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <Package className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">Products</span>
            </button>
            <button
              onClick={() => setActiveTab('policies')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'policies' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <FileText className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">Policies</span>
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-3 sm:py-4 font-medium transition-colors whitespace-nowrap ${
                activeTab === 'documents' ? 'border-b-2 border-purple-600 text-purple-600' : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <FolderOpen className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="text-sm sm:text-base">Documents</span>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6">
          {loading && <div className="text-center py-8">Loading...</div>}

          {/* Configuration Tab */}
          {activeTab === 'config' && !loading && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-4">Welcome Messages</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">English</label>
                    <textarea
                      value={config.welcome_message?.en || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        welcome_message: { ...config.welcome_message, en: e.target.value }
                      })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      rows="3"
                      placeholder="Welcome! How can I help you today?"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Sinhala</label>
                    <textarea
                      value={config.welcome_message?.si || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        welcome_message: { ...config.welcome_message, si: e.target.value }
                      })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      rows="3"
                      placeholder="ආයුබෝවන්! මම ඔබට උදව් කරන්නේ කෙසේද?"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Fallback Messages</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">English</label>
                    <textarea
                      value={config.fallback_message?.en || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        fallback_message: { ...config.fallback_message, en: e.target.value }
                      })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      rows="3"
                      placeholder="I'm sorry, I didn't understand that."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Sinhala</label>
                    <textarea
                      value={config.fallback_message?.si || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        fallback_message: { ...config.fallback_message, si: e.target.value }
                      })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      rows="3"
                      placeholder="සමාවන්න, මට එය තේරුම් ගත නොහැකි විය."
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Features</h3>
                <div className="space-y-3">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={config.rag_enabled || false}
                      onChange={(e) => setConfig({ ...config, rag_enabled: e.target.checked })}
                      className="w-5 h-5 text-purple-600 rounded"
                    />
                    <span className="font-medium">Enable RAG System (Retrieval Augmented Generation)</span>
                  </label>
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={config.nlp_enabled || false}
                      onChange={(e) => setConfig({ ...config, nlp_enabled: e.target.checked })}
                      className="w-5 h-5 text-purple-600 rounded"
                    />
                    <span className="font-medium">Enable NLP (Natural Language Processing)</span>
                  </label>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Response Mode</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">How should the bot respond to questions?</label>
                    <select
                      value={config.response_mode || 'hybrid'}
                      onChange={(e) => setConfig({ ...config, response_mode: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="hybrid">Hybrid - Use uploaded documents + general knowledge</option>
                      <option value="documents_only">Documents Only - Only answer from uploaded documents</option>
                    </select>
                    <p className="text-sm text-gray-600 mt-1">
                      Choose how the bot should respond when customers ask questions
                    </p>
                  </div>

                  {config.response_mode === 'documents_only' && (
                    <div>
                      <h4 className="text-md font-medium mb-3">Documents-Only Messages</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">English</label>
                          <textarea
                            value={config.documents_only_message?.en || ''}
                            onChange={(e) => setConfig({
                              ...config,
                              documents_only_message: { ...config.documents_only_message, en: e.target.value }
                            })}
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                            rows="3"
                            placeholder="I can only answer based on the documents uploaded by the business."
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium mb-2">Sinhala</label>
                          <textarea
                            value={config.documents_only_message?.si || ''}
                            onChange={(e) => setConfig({
                              ...config,
                              documents_only_message: { ...config.documents_only_message, si: e.target.value }
                            })}
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                            rows="3"
                            placeholder="මට ව්‍යාපාරය විසින් උඩුගත කරන ලද ලේඛන පදනම් කර ගෙන පමණක් පිළිතුරු දිය හැක."
                          />
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">
                        This message will be shown when the bot cannot find relevant information in uploaded documents
                      </p>
                    </div>
                  )}

                  {config.response_mode === 'hybrid' && (
                    <div>
                      <label className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={config.use_general_knowledge !== undefined ? config.use_general_knowledge : true}
                          onChange={(e) => setConfig({ ...config, use_general_knowledge: e.target.checked })}
                          className="w-5 h-5 text-purple-600 rounded"
                        />
                        <span className="font-medium">Use general knowledge when documents don't have answers</span>
                      </label>
                      <p className="text-sm text-gray-600 ml-8">
                        Allow the bot to use its general knowledge when uploaded documents don't contain relevant information
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-4">Business Hours</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Time</label>
                    <input
                      type="time"
                      value={config.business_hours?.start || '09:00'}
                      onChange={(e) => setConfig({
                        ...config,
                        business_hours: { ...config.business_hours, start: e.target.value }
                      })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Time</label>
                    <input
                      type="time"
                      value={config.business_hours?.end || '18:00'}
                      onChange={(e) => setConfig({
                        ...config,
                        business_hours: { ...config.business_hours, end: e.target.value }
                      })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={handleSaveConfig}
                disabled={loading}
                className="w-full sm:w-auto flex items-center justify-center gap-2 bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
              >
                <Save className="w-5 h-5" />
                Save Configuration
              </button>
            </div>
          )}

          {/* FAQs Tab */}
          {activeTab === 'faqs' && !loading && (
            <div className="space-y-6">
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
                  <h3 className="text-lg font-semibold">Add New FAQ</h3>
                  <button
                    onClick={() => openUploadModal('faq')}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 mt-2 sm:mt-0"
                  >
                    <Upload className="w-4 h-4" />
                    Upload FAQ Document
                  </button>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Language</label>
                      <select
                        value={newFaq.language}
                        onChange={(e) => setNewFaq({ ...newFaq, language: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="en">English</option>
                        <option value="si">Sinhala</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Category</label>
                      <input
                        type="text"
                        value={newFaq.category}
                        onChange={(e) => setNewFaq({ ...newFaq, category: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                        placeholder="e.g., Shipping, Products"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Question</label>
                    <input
                      type="text"
                      value={newFaq.question}
                      onChange={(e) => setNewFaq({ ...newFaq, question: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      placeholder="What are your shipping hours?"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Answer</label>
                    <textarea
                      value={newFaq.answer}
                      onChange={(e) => setNewFaq({ ...newFaq, answer: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                      rows="3"
                      placeholder="We ship Monday to Friday, 9 AM to 6 PM"
                    />
                  </div>
                  <button
                    onClick={handleAddFaq}
                    className="flex items-center gap-2 bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700"
                  >
                    <Plus className="w-5 h-5" />
                    Add FAQ
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Existing FAQs ({Array.isArray(faqs) ? faqs.length : 0})</h3>
                {Array.isArray(faqs) && faqs.map((faq) => (
                  <div key={faq._id} className="border rounded-lg p-4">
                    {editingFaq?._id === faq._id ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <select
                            value={editingFaq?.language || 'en'}
                            onChange={(e) => setEditingFaq({ ...editingFaq, language: e.target.value })}
                            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                          >
                            <option value="en">English</option>
                            <option value="si">Sinhala</option>
                          </select>
                          <input
                            type="text"
                            value={editingFaq?.category || ''}
                            onChange={(e) => setEditingFaq({ ...editingFaq, category: e.target.value })}
                            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                            placeholder="Category"
                          />
                        </div>
                        <input
                          type="text"
                          value={editingFaq?.question || ''}
                          onChange={(e) => setEditingFaq({ ...editingFaq, question: e.target.value })}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                          placeholder="Question"
                        />
                        <textarea
                          value={editingFaq?.answer || ''}
                          onChange={(e) => setEditingFaq({ ...editingFaq, answer: e.target.value })}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
                          rows="3"
                          placeholder="Answer"
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleUpdateFaq(faq._id)}
                            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                          >
                            <Save className="w-4 h-4" />
                            Save
                          </button>
                          <button
                            onClick={() => setEditingFaq(null)}
                            className="flex items-center gap-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                          >
                            <X className="w-4 h-4" />
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex gap-2">
                            {faq.language && (
                              <span className="text-xs font-medium bg-purple-100 text-purple-800 px-2 py-1 rounded">
                                {faq.language.toUpperCase()}
                              </span>
                            )}
                            {faq.category && (
                              <span className="text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded">
                                {faq.category}
                              </span>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => setEditingFaq(faq)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteFaq(faq._id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <h4 className="font-semibold text-gray-800 mb-2">{faq.question}</h4>
                        <p className="text-gray-600 text-sm">{faq.answer}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Products Tab */}
          {activeTab === 'products' && !loading && (
            <div className="space-y-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
                  <h3 className="text-lg font-semibold">Add New Product</h3>
                  <button
                    onClick={() => openUploadModal('product')}
                    className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 mt-2 sm:mt-0"
                  >
                    <Upload className="w-4 h-4" />
                    Upload Product Catalog
                  </button>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Product Name</label>
                      <input
                        type="text"
                        value={newProduct.name}
                        onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Fresh Apples"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Category</label>
                      <input
                        type="text"
                        value={newProduct.category}
                        onChange={(e) => setNewProduct({ ...newProduct, category: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Fruits"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Description</label>
                    <textarea
                      value={newProduct.description}
                      onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows="3"
                      placeholder="Fresh, organic apples from local farms"
                    />
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Price (LKR)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={newProduct.price}
                        onChange={(e) => setNewProduct({ ...newProduct, price: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="450.00"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Stock Quantity</label>
                      <input
                        type="number"
                        value={newProduct.stock}
                        onChange={(e) => setNewProduct({ ...newProduct, stock: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="100"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Product Images</label>
                    <input
                      type="file"
                      multiple
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      disabled={uploadingImages}
                    />
                    {uploadingImages && <p className="text-sm text-gray-600 mt-2">Uploading images...</p>}
                    {newProduct.images.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {newProduct.images.map((url, idx) => (
                          <img key={idx} src={url} alt={`Preview ${idx + 1}`} className="w-20 h-20 object-cover rounded" />
                        ))}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleAddProduct}
                    className="flex items-center gap-2 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
                  >
                    <Plus className="w-5 h-5" />
                    Add Product
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Existing Products ({Array.isArray(products) ? products.length : 0})</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Array.isArray(products) && products.map((product) => (
                    <div key={product._id} className="border rounded-lg overflow-hidden">
                      {product.images && product.images.length > 0 && (
                        <img src={product.images[0]} alt={product.name} className="w-full h-48 object-cover" />
                      )}
                      <div className="p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-semibold text-gray-800">{product.name}</h4>
                          <div className="flex gap-2">
                            <button
                              onClick={() => setEditingProduct(product)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteProduct(product._id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{product.description}</p>
                        <div className="flex justify-between items-center">
                          <span className="text-lg font-bold text-green-600">LKR {product.price}</span>
                          <span className="text-sm text-gray-600">Stock: {product.stock}</span>
                        </div>
                        {product.category && (
                          <span className="inline-block mt-2 text-xs font-medium bg-blue-100 text-blue-800 px-2 py-1 rounded">
                            {product.category}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Policies Tab */}
          {activeTab === 'policies' && !loading && (
            <div className="space-y-6">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4">
                  <h3 className="text-lg font-semibold">Add New Policy</h3>
                  <button
                    onClick={() => openUploadModal('policy')}
                    className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 mt-2 sm:mt-0"
                  >
                    <Upload className="w-4 h-4" />
                    Upload Policy Document
                  </button>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Policy Title</label>
                      <input
                        type="text"
                        value={newPolicy.title}
                        onChange={(e) => setNewPolicy({ ...newPolicy, title: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                        placeholder="Return Policy"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Policy Type</label>
                      <select
                        value={newPolicy.policy_type}
                        onChange={(e) => setNewPolicy({ ...newPolicy, policy_type: e.target.value })}
                        className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                      >
                        <option value="general">General</option>
                        <option value="return">Return Policy</option>
                        <option value="shipping">Shipping Policy</option>
                        <option value="privacy">Privacy Policy</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Policy Content</label>
                    <textarea
                      value={newPolicy.content}
                      onChange={(e) => setNewPolicy({ ...newPolicy, content: e.target.value })}
                      className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                      rows="6"
                      placeholder="Enter your policy details here..."
                    />
                  </div>
                  <button
                    onClick={handleAddPolicy}
                    className="flex items-center gap-2 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700"
                  >
                    <Plus className="w-5 h-5" />
                    Add Policy
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Existing Policies ({Array.isArray(policies) ? policies.length : 0})</h3>
                {Array.isArray(policies) && policies.map((policy) => (
                  <div key={policy._id} className="border rounded-lg p-4">
                    {editingPolicy?._id === policy._id ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <input
                            type="text"
                            value={editingPolicy.title}
                            onChange={(e) => setEditingPolicy({ ...editingPolicy, title: e.target.value })}
                            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                            placeholder="Policy Title"
                          />
                          <select
                            value={editingPolicy.policy_type}
                            onChange={(e) => setEditingPolicy({ ...editingPolicy, policy_type: e.target.value })}
                            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                          >
                            <option value="general">General</option>
                            <option value="return">Return Policy</option>
                            <option value="shipping">Shipping Policy</option>
                            <option value="privacy">Privacy Policy</option>
                          </select>
                        </div>
                        <textarea
                          value={editingPolicy.content}
                          onChange={(e) => setEditingPolicy({ ...editingPolicy, content: e.target.value })}
                          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-500"
                          rows="6"
                        />
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleUpdatePolicy(policy._id)}
                            className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                          >
                            <Save className="w-4 h-4" />
                            Save
                          </button>
                          <button
                            onClick={() => setEditingPolicy(null)}
                            className="flex items-center gap-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
                          >
                            <X className="w-4 h-4" />
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h4 className="font-semibold text-gray-800 text-lg">{policy.title}</h4>
                            <span className="text-xs font-medium bg-green-100 text-green-800 px-2 py-1 rounded mt-1 inline-block">
                              {policy.policy_type}
                            </span>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => setEditingPolicy(policy)}
                              className="text-blue-600 hover:text-blue-800"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeletePolicy(policy._id)}
                              className="text-red-600 hover:text-red-800"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <p className="text-gray-600 text-sm whitespace-pre-wrap mt-3">{policy.content}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <DocumentManager />
          )}
        </div>

        {/* File Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl max-w-md w-full">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold">Upload {uploadType.toUpperCase()} Document</h3>
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Select File (PDF, DOCX, XLSX, TXT)
                    </label>
                    <input
                      type="file"
                      accept=".pdf,.docx,.xlsx,.xls,.txt"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          handleFileUpload(file, uploadType);
                          setShowUploadModal(false);
                        }
                      }}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      disabled={uploadingFile}
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      The file will be processed and automatically added to your {uploadType} knowledge base.
                    </p>
                  </div>

                  {uploadingFile && (
                    <div className="flex items-center justify-center py-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                      <span className="ml-2 text-gray-600">Processing file...</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chat Widget */}
        {user && user.service_id && (
          <>
            {isChatOpen && (
              <SimpleChatWidget 
                serviceId={user.service_id}
                isOpen={isChatOpen}
                onClose={() => setIsChatOpen(false)}
              />
            )}
            {!isChatOpen && (
              <ChatButton onClick={() => setIsChatOpen(true)} />
            )}
          </>
        )}
      </div>
    </div>
  );
}
