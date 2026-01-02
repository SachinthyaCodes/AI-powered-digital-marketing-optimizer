import React, { useState, useEffect } from 'react';
import { 
  Upload, FileText, Image, Trash2, Eye, RefreshCw, 
  Download, Filter, Search, Plus, AlertCircle, 
  CheckCircle, XCircle, Clock, BarChart3, Settings,
  FileQuestion, Package, Scale, Store, Book
} from 'lucide-react';
import api from '../services/api';

const DocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({});
  const [stats, setStats] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [uploadData, setUploadData] = useState({
    files: [],
    document_type: 'general'
  });

  // Document type configurations
  const documentTypes = {
    all: { label: 'All Documents', icon: FileText, color: 'gray' },
    faq: { label: 'FAQs', icon: FileQuestion, color: 'blue' },
    product: { label: 'Products', icon: Package, color: 'green' },
    policy: { label: 'Policies', icon: Scale, color: 'purple' },
    store: { label: 'Store Info', icon: Store, color: 'orange' },
    general: { label: 'General', icon: Book, color: 'gray' }
  };

  const statusColors = {
    processing: 'yellow',
    completed: 'green',
    failed: 'red'
  };

  useEffect(() => {
    fetchDocuments();
    fetchStats();
  }, [page, selectedType, selectedStatus, searchTerm]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20'
      });
      
      if (selectedType !== 'all') params.append('type', selectedType);
      if (selectedStatus !== 'all') params.append('status', selectedStatus);
      
      const response = await api.get(`/api/documents/?${params}`);
      setDocuments(response.data.documents);
      setPagination(response.data.pagination);
    } catch (error) {
      console.error('Error fetching documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await api.get('/api/documents/stats');
      setStats(response.data || {});
    } catch (error) {
      console.error('Error fetching stats:', error);
      setStats({ total_documents: 0, processed_documents: 0, pending_documents: 0 });
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (uploadData.files.length === 0) {
      alert('Please select files to upload');
      return;
    }

    setUploadLoading(true);
    setUploadProgress({ current: 0, total: uploadData.files.length, messages: [] });
    
    try {
      const results = [];
      
      for (let i = 0; i < uploadData.files.length; i++) {
        const file = uploadData.files[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', uploadData.document_type);
        
        // Update progress
        setUploadProgress(prev => ({
          ...prev,
          current: i + 1,
          messages: [...prev.messages, `📤 Uploading ${file.name}...`]
        }));
        
        try {
          const response = await api.post('/api/documents/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
          
          const docData = response.data;
          
          // Add success message with details
          setUploadProgress(prev => ({
            ...prev,
            messages: [
              ...prev.messages,
              `✅ ${file.name} uploaded successfully!`,
              `   📝 Created ${docData.chunk_count || 0} text chunks`,
              `   🧠 Generated ${docData.embedding_count || 0} embeddings`,
              `   ✓ Ready for chatbot queries\n`
            ]
          }));
          
          results.push({ success: true, file: file.name });
        } catch (error) {
          // Add error message
          setUploadProgress(prev => ({
            ...prev,
            messages: [
              ...prev.messages,
              `❌ Failed to upload ${file.name}: ${error.response?.data?.error || error.message}\n`
            ]
          }));
          
          results.push({ success: false, file: file.name, error: error.message });
        }
        
        // Small delay to show progress
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      // Refresh data
      await fetchDocuments();
      await fetchStats();
      
      const successCount = results.filter(r => r.success).length;
      const failCount = results.filter(r => !r.success).length;
      
      setUploadProgress(prev => ({
        ...prev,
        messages: [
          ...prev.messages,
          `\n🎉 Upload Complete!`,
          `   ✅ ${successCount} file(s) processed successfully`,
          failCount > 0 ? `   ❌ ${failCount} file(s) failed` : ''
        ].filter(Boolean)
      }));
      
      // Auto-close after 3 seconds if all successful
      if (failCount === 0) {
        setTimeout(() => {
          setShowUploadModal(false);
          setUploadData({ files: [], document_type: 'general' });
          setUploadProgress(null);
        }, 3000);
      }
      
    } catch (error) {
      console.error('Error uploading documents:', error);
      setUploadProgress(prev => ({
        ...prev,
        messages: [...prev.messages, `❌ Upload failed: ${error.message}`]
      }));
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDelete = async (documentId) => {
    if (!confirm('Are you sure you want to delete this document?')) return;

    try {
      await api.delete(`/api/documents/${documentId}`);
      fetchDocuments();
      fetchStats();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Error deleting document');
    }
  };

  const handleReprocess = async (documentId) => {
    try {
      await api.post(`/api/documents/${documentId}/reprocess`);
      fetchDocuments();
      alert('Document reprocessing started');
    } catch (error) {
      console.error('Error reprocessing document:', error);
      alert('Error reprocessing document');
    }
  };

  const handleBulkSync = async () => {
    if (!confirm('This will sync all FAQs, Products, and Policies to the knowledge base. Continue?')) return;

    try {
      setLoading(true);
      await api.post('/api/documents/bulk/sync', {
        types: ['faq', 'product', 'policy']
      });
      fetchDocuments();
      fetchStats();
      alert('Bulk sync completed successfully!');
    } catch (error) {
      console.error('Error in bulk sync:', error);
      alert('Error in bulk sync');
    } finally {
      setLoading(false);
    }
  };

  const filteredDocuments = documents.filter(doc =>
    doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.document_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status) => {
    // Default to 'processing' if status is undefined/null
    const statusValue = status || 'processing';
    
    const colors = {
      processing: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-green-100 text-green-700',
      failed: 'bg-red-100 text-red-700'
    };

    const icons = {
      processing: Clock,
      completed: CheckCircle,
      failed: XCircle
    };

    const Icon = icons[statusValue] || Clock;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${colors[statusValue] || 'bg-gray-100 text-gray-700'}`}>
        <Icon className="w-3 h-3" />
        {statusValue.charAt(0).toUpperCase() + statusValue.slice(1)}
      </span>
    );
  };

  const getTypeBadge = (type) => {
    const config = documentTypes[type] || documentTypes.general;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-${config.color}-100 text-${config.color}-700`}>
        <Icon className="w-3 h-3" />
        {config.label}
      </span>
    );
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Management</h1>
          <p className="text-gray-600">Upload and manage documents for your chatbot knowledge base</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Documents</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_documents || 0}</p>
              </div>
              <FileText className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Processed</p>
                <p className="text-2xl font-bold text-green-600">{stats?.processed_documents || 0}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-yellow-600">{stats?.pending_documents || 0}</p>
              </div>
              <Clock className="w-8 h-8 text-yellow-500" />
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="bg-white rounded-lg p-4 shadow-sm border mb-6">
          <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
            {/* Search and Filters */}
            <div className="flex flex-col sm:flex-row gap-3 flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {Object.entries(documentTypes).map(([key, config]) => (
                  <option key={key} value={key}>{config.label}</option>
                ))}
              </select>
              
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="processing">Processing</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
              </select>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2">
              <button
                onClick={handleBulkSync}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                disabled={loading}
              >
                <RefreshCw className="w-4 h-4" />
                Bulk Sync
              </button>
              
              <button
                onClick={() => setShowUploadModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                Upload Documents
              </button>
            </div>
          </div>
        </div>

        {/* Documents Table */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size / Chunks
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center">
                      <div className="flex items-center justify-center">
                        <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
                        <span className="ml-2 text-gray-500">Loading documents...</span>
                      </div>
                    </td>
                  </tr>
                ) : filteredDocuments.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center">
                      <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                      <p className="text-gray-500">No documents found</p>
                    </td>
                  </tr>
                ) : (
                  filteredDocuments.map((doc) => (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          <FileText className="w-5 h-5 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900">{doc.filename}</div>
                            {doc.content_preview && (
                              <div className="text-sm text-gray-500 max-w-md truncate">
                                {doc.content_preview}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        {getTypeBadge(doc.document_type)}
                      </td>
                      
                      <td className="px-6 py-4">
                        {getStatusBadge(doc.status)}
                        {doc.error_message && (
                          <div className="text-xs text-red-500 mt-1 max-w-xs truncate">
                            {doc.error_message}
                          </div>
                        )}
                      </td>
                      
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div>{formatFileSize(doc.file_size)}</div>
                        <div className="text-xs text-gray-500">{doc.chunks_count} chunks</div>
                      </td>
                      
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </td>
                      
                      <td className="px-6 py-4 text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          {doc.file_url && (
                            <button
                              onClick={() => window.open(doc.file_url, '_blank')}
                              className="text-blue-600 hover:text-blue-900 p-1"
                              title="View Document"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                          )}
                          
                          {doc.status === 'failed' && (
                            <button
                              onClick={() => handleReprocess(doc.id)}
                              className="text-yellow-600 hover:text-yellow-900 p-1"
                              title="Reprocess"
                            >
                              <RefreshCw className="w-4 h-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={() => handleDelete(doc.id)}
                            className="text-red-600 hover:text-red-900 p-1"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {pagination && pagination.pages > 1 && (
            <div className="px-6 py-3 bg-gray-50 border-t flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing page {pagination.page} of {pagination.pages} ({pagination.total} total)
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(pagination.pages, page + 1))}
                  disabled={page === pagination.pages}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">Upload Documents</h3>
              
              <form onSubmit={handleUpload} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type
                  </label>
                  <select
                    value={uploadData.document_type}
                    onChange={(e) => setUploadData({...uploadData, document_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {Object.entries(documentTypes).filter(([key]) => key !== 'all').map(([key, config]) => (
                      <option key={key} value={key}>{config.label}</option>
                    ))}
                  </select>
                  <p className="text-sm text-gray-500 mt-1">
                    Choose the category that best describes your documents
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Files (PDF, DOCX, XLSX, TXT)
                  </label>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.docx,.xlsx,.xls,.txt"
                    onChange={(e) => setUploadData({...uploadData, files: Array.from(e.target.files)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    You can select multiple files. Supported formats: PDF, Word documents, Excel files, Text files
                  </p>
                </div>

                {uploadData.files.length > 0 && (
                  <div className="border border-gray-200 rounded-lg p-3">
                    <h4 className="font-medium text-gray-900 mb-2">Selected Files:</h4>
                    <ul className="space-y-1">
                      {uploadData.files.map((file, index) => (
                        <li key={index} className="flex items-center text-sm text-gray-600">
                          <FileText className="w-4 h-4 mr-2" />
                          {file.name} ({formatFileSize(file.size)})
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Upload Progress Display */}
                {uploadProgress && (
                  <div className="border-2 border-blue-200 rounded-lg p-4 bg-blue-50">
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-blue-900">
                          Processing {uploadProgress.current} of {uploadProgress.total} files
                        </span>
                        <span className="text-sm text-blue-700">
                          {Math.round((uploadProgress.current / uploadProgress.total) * 100)}%
                        </span>
                      </div>
                      <div className="w-full bg-blue-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${(uploadProgress.current / uploadProgress.total) * 100}%` }}
                        />
                      </div>
                    </div>
                    
                    <div className="max-h-60 overflow-y-auto bg-white rounded p-3 border border-blue-200">
                      <div className="font-mono text-xs space-y-1">
                        {uploadProgress.messages.map((msg, idx) => (
                          <div 
                            key={idx} 
                            className={`${
                              msg.includes('✅') ? 'text-green-600' : 
                              msg.includes('❌') ? 'text-red-600' : 
                              msg.includes('🎉') ? 'text-blue-700 font-bold' :
                              'text-gray-700'
                            }`}
                          >
                            {msg}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    disabled={uploadLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                    disabled={uploadLoading || uploadData.files.length === 0}
                  >
                    {uploadLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin inline mr-2" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4 inline mr-2" />
                        Upload Documents
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentManager;