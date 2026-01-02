import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Settings, FileQuestion, Package, FileText, Save, Plus, Trash2, Edit, Upload, X, FolderOpen, ArrowLeft } from 'lucide-react';
import api from '../services/api';
import DocumentManager from './DocumentManager';
import SimpleChatWidget, { ChatButton } from '../components/SimpleChatWidget';
import { useAuth } from '../context/AuthContext';

export default function BotManagement() {
  const { user } = useAuth();
  const navigate = useNavigate();
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
    offline_message: { en: '', si: '' },
    max_response_tokens: 300,
    response_temperature: 0.7,
    response_timeout: 30
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
            offline_message: res.data.config?.offline_message || { en: '', si: '' },
            max_response_tokens: res.data.config?.max_response_tokens || 300,
            response_temperature: res.data.config?.response_temperature !== undefined ? res.data.config.response_temperature : 0.7,
            response_timeout: res.data.config?.response_timeout || 30
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
      setFaqs(faqs.map(f => f.id === id ? res.data : f));
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
      setFaqs(faqs.filter(f => f.id !== id));
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
      setProducts(products.map(p => p.id === id ? res.data : p));
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
      setProducts(products.filter(p => p.id !== id));
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
      setPolicies(policies.map(p => p.id === id ? res.data : p));
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
      setPolicies(policies.filter(p => p.id !== id));
      showMessage('success', 'Policy deleted successfully');
    } catch (error) {
      showMessage('error', error.response?.data?.message || 'Failed to delete policy');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 sm:p-8 mb-6 transform hover:scale-[1.01] transition-all duration-300">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/admin')}
              className="group bg-gradient-to-br from-gray-100 to-gray-200 hover:from-purple-500 hover:to-indigo-600 p-3 rounded-xl shadow-lg transition-all duration-300 transform hover:scale-110 hover:-translate-x-1"
              title="Back to Dashboard"
            >
              <ArrowLeft className="w-6 h-6 text-gray-700 group-hover:text-white transition-colors" />
            </button>
            <div className="bg-gradient-to-br from-purple-500 to-indigo-600 p-4 rounded-2xl shadow-lg">
              <MessageSquare className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Bot Management
              </h1>
              <p className="text-sm sm:text-base text-gray-500 mt-1">Configure your AI assistant and manage chatbot settings</p>
            </div>
          </div>
        </div>

        {/* Message Alert */}
        {message.text && (
          <div className={`mb-6 p-4 rounded-xl shadow-lg border-l-4 animate-fade-in ${
            message.type === 'success' 
              ? 'bg-green-50 border-green-500 text-green-800' 
              : 'bg-red-50 border-red-500 text-red-800'
          }`}>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${message.type === 'success' ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
              <span className="font-medium">{message.text}</span>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 mb-6 overflow-hidden">
          <div className="flex border-b border-gray-200 overflow-x-auto scrollbar-hide">
            <button
              onClick={() => setActiveTab('config')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-4 font-medium transition-all duration-300 whitespace-nowrap relative group ${
                activeTab === 'config' 
                  ? 'text-purple-600 bg-purple-50' 
                  : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50/50'
              }`}
            >
              <Settings className={`w-5 h-5 transition-transform duration-300 ${activeTab === 'config' ? 'rotate-90' : 'group-hover:rotate-90'}`} />
              <span className="text-sm sm:text-base">Configuration</span>
              {activeTab === 'config' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-indigo-500"></div>}
            </button>
            <button
              onClick={() => setActiveTab('faqs')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-4 font-medium transition-all duration-300 whitespace-nowrap relative group ${
                activeTab === 'faqs' 
                  ? 'text-purple-600 bg-purple-50' 
                  : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50/50'
              }`}
            >
              <FileQuestion className={`w-5 h-5 transition-transform duration-300 ${activeTab === 'faqs' ? 'scale-110' : 'group-hover:scale-110'}`} />
              <span className="text-sm sm:text-base">FAQs</span>
              {activeTab === 'faqs' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-indigo-500"></div>}
            </button>
            <button
              onClick={() => setActiveTab('products')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-4 font-medium transition-all duration-300 whitespace-nowrap relative group ${
                activeTab === 'products' 
                  ? 'text-purple-600 bg-purple-50' 
                  : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50/50'
              }`}
            >
              <Package className={`w-5 h-5 transition-transform duration-300 ${activeTab === 'products' ? 'scale-110' : 'group-hover:scale-110'}`} />
              <span className="text-sm sm:text-base">Products</span>
              {activeTab === 'products' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-indigo-500"></div>}
            </button>
            <button
              onClick={() => setActiveTab('policies')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-4 font-medium transition-all duration-300 whitespace-nowrap relative group ${
                activeTab === 'policies' 
                  ? 'text-purple-600 bg-purple-50' 
                  : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50/50'
              }`}
            >
              <FileText className={`w-5 h-5 transition-transform duration-300 ${activeTab === 'policies' ? 'scale-110' : 'group-hover:scale-110'}`} />
              <span className="text-sm sm:text-base">Policies</span>
              {activeTab === 'policies' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-indigo-500"></div>}
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`flex items-center gap-2 px-4 sm:px-6 py-4 font-medium transition-all duration-300 whitespace-nowrap relative group ${
                activeTab === 'documents' 
                  ? 'text-purple-600 bg-purple-50' 
                  : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50/50'
              }`}
            >
              <FolderOpen className={`w-5 h-5 transition-transform duration-300 ${activeTab === 'documents' ? 'scale-110' : 'group-hover:scale-110'}`} />
              <span className="text-sm sm:text-base">Documents</span>
              {activeTab === 'documents' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 to-indigo-500"></div>}
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 sm:p-8">
          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-200 border-t-purple-600"></div>
              <p className="mt-4 text-gray-600 font-medium">Loading...</p>
            </div>
          )}

          {/* Configuration Tab */}
          {activeTab === 'config' && !loading && (
            <div className="space-y-8 animate-fade-in">
              <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-6 rounded-xl border border-purple-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-purple-500 to-indigo-500 rounded-full"></div>
                  Welcome Messages
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">English</label>
                    <textarea
                      value={config.welcome_message?.en || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        welcome_message: { ...config.welcome_message, en: e.target.value }
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                      rows="3"
                      placeholder="Welcome! How can I help you today?"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">Sinhala</label>
                    <textarea
                      value={config.welcome_message?.si || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        welcome_message: { ...config.welcome_message, si: e.target.value }
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                      rows="3"
                      placeholder="ආයුබෝවන්! මම ඔබට උදව් කරන්නේ කෙසේද?"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 p-6 rounded-xl border border-blue-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-blue-500 to-cyan-500 rounded-full"></div>
                  Fallback Messages
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">English</label>
                    <textarea
                      value={config.fallback_message?.en || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        fallback_message: { ...config.fallback_message, en: e.target.value }
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                      rows="3"
                      placeholder="I'm sorry, I didn't understand that."
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">Sinhala</label>
                    <textarea
                      value={config.fallback_message?.si || ''}
                      onChange={(e) => setConfig({
                        ...config,
                        fallback_message: { ...config.fallback_message, si: e.target.value }
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                      rows="3"
                      placeholder="සමාවන්න, මට එය තේරුම් ගත නොහැකි විය."
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border border-green-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-green-500 to-emerald-500 rounded-full"></div>
                  Features
                </h3>
                <div className="space-y-4">
                  <label className="flex items-center gap-3 p-4 bg-white rounded-lg hover:bg-green-50 transition-colors cursor-pointer border border-green-100">
                    <input
                      type="checkbox"
                      checked={config.rag_enabled || false}
                      onChange={(e) => setConfig({ ...config, rag_enabled: e.target.checked })}
                      className="w-5 h-5 text-green-600 rounded focus:ring-green-500"
                    />
                    <span className="font-medium text-gray-700">Enable RAG System (Retrieval Augmented Generation)</span>
                  </label>
                  <label className="flex items-center gap-3 p-4 bg-white rounded-lg hover:bg-green-50 transition-colors cursor-pointer border border-green-100">
                    <input
                      type="checkbox"
                      checked={config.nlp_enabled || false}
                      onChange={(e) => setConfig({ ...config, nlp_enabled: e.target.checked })}
                      className="w-5 h-5 text-green-600 rounded focus:ring-green-500"
                    />
                    <span className="font-medium text-gray-700">Enable NLP (Natural Language Processing)</span>
                  </label>
                </div>
              </div>

              <div className="bg-gradient-to-br from-teal-50 to-cyan-50 p-6 rounded-xl border border-teal-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-teal-500 to-cyan-500 rounded-full"></div>
                  Response Configuration
                </h3>
                <div className="space-y-6">
                  {/* Max Response Tokens */}
                  <div className="bg-white p-4 rounded-lg border border-teal-200">
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      Max Response Length
                      <span className="text-gray-500 font-normal ml-2">(100-1000 tokens)</span>
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="1000"
                      step="50"
                      value={config.max_response_tokens || 300}
                      onChange={(e) => setConfig({
                        ...config,
                        max_response_tokens: parseInt(e.target.value)
                      })}
                      className="w-full h-2 bg-teal-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                      <span>Short (100)</span>
                      <span className="font-bold text-teal-600 text-base">{config.max_response_tokens || 300}</span>
                      <span>Long (1000)</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 italic">
                      💡 Lower = Faster responses, Higher = More detailed answers
                    </p>
                  </div>

                  {/* Response Temperature */}
                  <div className="bg-white p-4 rounded-lg border border-teal-200">
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      Response Creativity
                      <span className="text-gray-500 font-normal ml-2">(0.0-1.0)</span>
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={config.response_temperature !== undefined ? config.response_temperature : 0.7}
                      onChange={(e) => setConfig({
                        ...config,
                        response_temperature: parseFloat(e.target.value)
                      })}
                      className="w-full h-2 bg-teal-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-2">
                      <span>Precise (0.0)</span>
                      <span className="font-bold text-teal-600 text-base">{config.response_temperature !== undefined ? config.response_temperature.toFixed(1) : '0.7'}</span>
                      <span>Creative (1.0)</span>
                    </div>
                    <p className="text-xs text-gray-600 mt-2 italic">
                      💡 Lower = More consistent, Higher = More varied responses
                    </p>
                  </div>

                  {/* Response Timeout */}
                  <div className="bg-white p-4 rounded-lg border border-teal-200">
                    <label className="block text-sm font-semibold text-gray-700 mb-3">
                      Response Timeout
                      <span className="text-gray-500 font-normal ml-2">(10-120 seconds)</span>
                    </label>
                    <select
                      value={config.response_timeout || 30}
                      onChange={(e) => setConfig({
                        ...config,
                        response_timeout: parseInt(e.target.value)
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-teal-500 focus:border-transparent transition-all shadow-sm hover:shadow-md bg-white"
                    >
                      <option value="10">⚡ 10 seconds (Very Fast)</option>
                      <option value="20">🚀 20 seconds (Fast)</option>
                      <option value="30">✅ 30 seconds (Normal - Recommended)</option>
                      <option value="45">⏱️ 45 seconds (Slow)</option>
                      <option value="60">🐌 60 seconds (Very Slow)</option>
                      <option value="90">⏳ 90 seconds (Maximum)</option>
                      <option value="120">🕐 120 seconds (Ultra Long)</option>
                    </select>
                    <p className="text-xs text-gray-600 mt-2 italic">
                      💡 Maximum wait time before giving up on response
                    </p>
                  </div>

                  {/* Current Settings Display */}
                  <div className="bg-gradient-to-br from-teal-100 to-cyan-100 p-4 rounded-lg border-2 border-teal-300">
                    <h4 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
                      <Settings className="w-4 h-4" />
                      Current Response Settings
                    </h4>
                    <div className="space-y-1 text-sm">
                      <p>• Max Length: <strong className="text-teal-700">{config.max_response_tokens || 300} tokens</strong></p>
                      <p>• Creativity: <strong className="text-teal-700">{config.response_temperature !== undefined ? config.response_temperature.toFixed(1) : '0.7'}</strong></p>
                      <p>• Timeout: <strong className="text-teal-700">{config.response_timeout || 30} seconds</strong></p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-orange-50 to-amber-50 p-6 rounded-xl border border-orange-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-orange-500 to-amber-500 rounded-full"></div>
                  Response Mode
                </h3>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">How should the bot respond to questions?</label>
                    <select
                      value={config.response_mode || 'hybrid'}
                      onChange={(e) => setConfig({ ...config, response_mode: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all shadow-sm hover:shadow-md bg-white"
                    >
                      <option value="hybrid">Hybrid - Use uploaded documents + general knowledge</option>
                      <option value="documents_only">Documents Only - Only answer from uploaded documents</option>
                    </select>
                    <p className="text-sm text-gray-600 mt-2">
                      Choose how the bot should respond when customers ask questions
                    </p>
                  </div>

                  {config.response_mode === 'documents_only' && (
                    <div className="bg-white p-4 rounded-lg border border-orange-200">
                      <h4 className="text-md font-semibold mb-3 text-gray-800">Documents-Only Messages</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium mb-2">English</label>
                          <textarea
                            value={config.documents_only_message?.en || ''}
                            onChange={(e) => setConfig({
                              ...config,
                              documents_only_message: { ...config.documents_only_message, en: e.target.value }
                            })}
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
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
                            className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-orange-500"
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
                    <div className="bg-white p-4 rounded-lg border border-orange-200">
                      <label className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={config.use_general_knowledge !== undefined ? config.use_general_knowledge : true}
                          onChange={(e) => setConfig({ ...config, use_general_knowledge: e.target.checked })}
                          className="w-5 h-5 text-orange-600 rounded focus:ring-orange-500"
                        />
                        <span className="font-medium">Use general knowledge when documents don't have answers</span>
                      </label>
                      <p className="text-sm text-gray-600 ml-8 mt-1">
                        Allow the bot to use its general knowledge when uploaded documents don't contain relevant information
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-gradient-to-br from-pink-50 to-rose-50 p-6 rounded-xl border border-pink-100">
                <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-pink-500 to-rose-500 rounded-full"></div>
                  Business Hours
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">Start Time</label>
                    <input
                      type="time"
                      value={config.business_hours?.start || '09:00'}
                      onChange={(e) => setConfig({
                        ...config,
                        business_hours: { ...config.business_hours, start: e.target.value }
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">End Time</label>
                    <input
                      type="time"
                      value={config.business_hours?.end || '18:00'}
                      onChange={(e) => setConfig({
                        ...config,
                        business_hours: { ...config.business_hours, end: e.target.value }
                      })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={handleSaveConfig}
                disabled={loading}
                className="w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-8 py-4 rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 disabled:opacity-50 shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
              >
                <Save className="w-5 h-5" />
                <span className="font-semibold">Save Configuration</span>
              </button>
            </div>
          )}

          {/* FAQs Tab */}
          {activeTab === 'faqs' && !loading && (
            <div className="space-y-6 animate-fade-in">
              <div className="bg-gradient-to-br from-purple-50 to-indigo-50 p-6 rounded-xl border border-purple-100 shadow-md">
                <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
                  <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                    <div className="w-1 h-6 bg-gradient-to-b from-purple-500 to-indigo-500 rounded-full"></div>
                    Add New FAQ
                  </h3>
                  <button
                    onClick={() => openUploadModal('faq')}
                    className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-cyan-600 text-white px-4 py-2.5 rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-all shadow-md hover:shadow-lg mt-2 sm:mt-0 transform hover:scale-105"
                  >
                    <Upload className="w-4 h-4" />
                    Upload FAQ Document
                  </button>
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-700">Language</label>
                      <select
                        value={newFaq.language}
                        onChange={(e) => setNewFaq({ ...newFaq, language: e.target.value })}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm hover:shadow-md bg-white"
                      >
                        <option value="en">English</option>
                        <option value="si">Sinhala</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="block text-sm font-semibold text-gray-700">Category</label>
                      <input
                        type="text"
                        value={newFaq.category}
                        onChange={(e) => setNewFaq({ ...newFaq, category: e.target.value })}
                        className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                        placeholder="e.g., Shipping, Products"
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">Question</label>
                    <input
                      type="text"
                      value={newFaq.question}
                      onChange={(e) => setNewFaq({ ...newFaq, question: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                      placeholder="What are your shipping hours?"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="block text-sm font-semibold text-gray-700">Answer</label>
                    <textarea
                      value={newFaq.answer}
                      onChange={(e) => setNewFaq({ ...newFaq, answer: e.target.value })}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm hover:shadow-md"
                      rows="3"
                      placeholder="We ship Monday to Friday, 9 AM to 6 PM"
                    />
                  </div>
                  <button
                    onClick={handleAddFaq}
                    className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-3 rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    <Plus className="w-5 h-5" />
                    Add FAQ
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <div className="w-1 h-6 bg-gradient-to-b from-purple-500 to-indigo-500 rounded-full"></div>
                  Existing FAQs ({Array.isArray(faqs) ? faqs.length : 0})
                </h3>
                {Array.isArray(faqs) && faqs.map((faq) => (
                  <div key={faq.id} className="border-2 border-gray-100 rounded-xl p-5 bg-white hover:shadow-lg transition-all duration-300 transform hover:scale-[1.01]">
                    {editingFaq?.id === faq.id ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <select
                            value={editingFaq?.language || 'en'}
                            onChange={(e) => setEditingFaq({ ...editingFaq, language: e.target.value })}
                            className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          >
                            <option value="en">English</option>
                            <option value="si">Sinhala</option>
                          </select>
                          <input
                            type="text"
                            value={editingFaq?.category || ''}
                            onChange={(e) => setEditingFaq({ ...editingFaq, category: e.target.value })}
                            className="px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            placeholder="Category"
                          />
                        </div>
                        <input
                          type="text"
                          value={editingFaq?.question || ''}
                          onChange={(e) => setEditingFaq({ ...editingFaq, question: e.target.value })}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="Question"
                        />
                        <textarea
                          value={editingFaq?.answer || ''}
                          onChange={(e) => setEditingFaq({ ...editingFaq, answer: e.target.value })}
                          className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          rows="3"
                          placeholder="Answer"
                        />
                        <div className="flex gap-3">
                          <button
                            onClick={() => handleUpdateFaq(faq.id)}
                            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-5 py-2.5 rounded-lg hover:from-green-700 hover:to-emerald-700 shadow-md hover:shadow-lg transform hover:scale-105 transition-all"
                          >
                            <Save className="w-4 h-4" />
                            Save
                          </button>
                          <button
                            onClick={() => setEditingFaq(null)}
                            className="flex items-center gap-2 bg-gradient-to-r from-gray-600 to-gray-700 text-white px-5 py-2.5 rounded-lg hover:from-gray-700 hover:to-gray-800 shadow-md hover:shadow-lg transform hover:scale-105 transition-all"
                          >
                            <X className="w-4 h-4" />
                            Cancel
                          </button>
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex gap-2 flex-wrap">
                            {faq.language && (
                              <span className="text-xs font-semibold bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 px-3 py-1.5 rounded-full border border-purple-200">
                                {faq.language.toUpperCase()}
                              </span>
                            )}
                            {faq.category && (
                              <span className="text-xs font-semibold bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-700 px-3 py-1.5 rounded-full border border-blue-200">
                                {faq.category}
                              </span>
                            )}
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => setEditingFaq(faq)}
                              className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 p-2 rounded-lg transition-all transform hover:scale-110"
                              title="Edit FAQ"
                            >
                              <Edit className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteFaq(faq.id)}
                              className="text-red-600 hover:text-red-800 hover:bg-red-50 p-2 rounded-lg transition-all transform hover:scale-110"
                              title="Delete FAQ"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                        <h4 className="font-bold text-gray-900 mb-2 text-lg">{faq.question}</h4>
                        <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
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
                    <div key={product.id} className="border rounded-lg overflow-hidden">
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
                  <div key={policy.id} className="border rounded-lg p-4">
                    {editingPolicy?.id === policy.id ? (
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
