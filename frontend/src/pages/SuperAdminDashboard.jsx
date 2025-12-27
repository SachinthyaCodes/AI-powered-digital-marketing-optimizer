import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  LogOut, Plus, Search, Edit2, Trash2, Calendar, 
  Shield, Store, User, Mail, Phone, MapPin, Key,
  Clock, CheckCircle, XCircle, Loader2
} from 'lucide-react';
import api from '../services/api';

const SuperAdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [modalMode, setModalMode] = useState('create'); // 'create' or 'edit'
  const [selectedService, setSelectedService] = useState(null);
  const [formData, setFormData] = useState({
    shop_name: '',
    owner_name: '',
    address: '',
    email: '',
    phone: '',
    subscription_duration: '',
    subscription_unit: 'month',
  });
  const [formError, setFormError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/services/');
      setServices(response.data.services);
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/superadmin/login');
  };

  const openCreateModal = () => {
    setModalMode('create');
    setFormData({
      shop_name: '',
      owner_name: '',
      address: '',
      email: '',
      phone: '',
      subscription_duration: '',
      subscription_unit: 'month',
    });
    setFormError('');
    setShowModal(true);
  };

  const openEditModal = (service) => {
    setModalMode('edit');
    setSelectedService(service);
    setFormData({
      shop_name: service.shop_name,
      owner_name: service.owner_name,
      address: service.address,
      email: service.email,
      phone: service.phone,
      subscription_duration: service.subscription_duration || '',
      subscription_unit: service.subscription_unit || 'month',
    });
    setFormError('');
    setShowModal(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setSubmitting(true);

    try {
      if (modalMode === 'create') {
        await api.post('/api/services/', formData);
      } else {
        await api.put(`/api/services/${selectedService.id}`, formData);
      }
      
      setShowModal(false);
      fetchServices();
    } catch (error) {
      setFormError(error.response?.data?.message || 'An error occurred');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (serviceId) => {
    if (!window.confirm('Are you sure you want to delete this service?')) {
      return;
    }

    try {
      await api.delete(`/api/services/${serviceId}`);
      fetchServices();
    } catch (error) {
      alert('Error deleting service: ' + (error.response?.data?.message || 'Unknown error'));
    }
  };

  const filteredServices = services.filter(service =>
    service.shop_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.owner_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    service.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getSubscriptionBadge = (service) => {
    if (!service.subscription_duration) {
      return <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">No Subscription</span>;
    }
    
    const unit = service.subscription_unit === 'week' ? 'Week' : 
                 service.subscription_unit === 'month' ? 'Month' : 'Year';
    return (
      <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded font-medium">
        {service.subscription_duration} {unit}{service.subscription_duration > 1 ? 's' : ''}
      </span>
    );
  };

  const getStatusBadge = (isActive) => {
    return isActive ? (
      <span className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 text-xs rounded">
        <CheckCircle className="w-3 h-3" /> Active
      </span>
    ) : (
      <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
        <XCircle className="w-3 h-3" /> Inactive
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-3">
              <Shield className="w-6 h-6 sm:w-8 sm:h-8" />
              <div>
                <h1 className="text-base sm:text-xl font-bold">Super Admin Portal</h1>
                <p className="text-xs text-purple-200">Service Management</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm opacity-90">Total Services</p>
                <p className="text-2xl sm:text-3xl font-bold mt-1">{services.length}</p>
              </div>
              <Store className="w-10 h-10 sm:w-12 sm:h-12 opacity-80" />
            </div>
          </div>
          <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm opacity-90">Active Services</p>
                <p className="text-2xl sm:text-3xl font-bold mt-1">
                  {services.filter(s => s.is_active).length}
                </p>
              </div>
              <CheckCircle className="w-10 h-10 sm:w-12 sm:h-12 opacity-80" />
            </div>
          </div>
          <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs sm:text-sm opacity-90">With Subscriptions</p>
                <p className="text-2xl sm:text-3xl font-bold mt-1">
                  {services.filter(s => s.subscription_duration).length}
                </p>
              </div>
              <Clock className="w-10 h-10 sm:w-12 sm:h-12 opacity-80" />
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="card mb-4 sm:mb-6">
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-center justify-between">
            <div className="relative flex-1 w-full sm:max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search services..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input pl-11 w-full"
              />
            </div>
            <button
              onClick={openCreateModal}
              className="btn btn-primary flex items-center gap-2 w-full sm:w-auto"
            >
              <Plus className="w-5 h-5" />
              Create New Service
            </button>
          </div>
        </div>

        {/* Services List */}
        <div className="card">
          <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6">All Services</h2>
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
            </div>
          ) : filteredServices.length === 0 ? (
            <div className="text-center py-12">
              <Store className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                {searchTerm ? 'No services found matching your search.' : 'No services yet. Create your first service!'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6 px-6 sm:mx-0 sm:px-0">
              <table className="w-full min-w-[800px]">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-2 sm:py-3 px-2 sm:px-4 text-xs sm:text-sm font-semibold text-gray-700">Shop Name</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Owner</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Contact</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Service Token</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Subscription</th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredServices.map((service) => (
                    <tr key={service.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <Store className="w-5 h-5 text-gray-400" />
                          <span className="font-medium text-gray-900">{service.shop_name}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-sm text-gray-600">{service.owner_name}</td>
                      <td className="py-4 px-4">
                        <div className="text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Mail className="w-3 h-3" />
                            {service.email}
                          </div>
                          <div className="flex items-center gap-1">
                            <Phone className="w-3 h-3" />
                            {service.phone}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <Key className="w-4 h-4 text-gray-400" />
                          <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                            {service.service_token}
                          </code>
                        </div>
                      </td>
                      <td className="py-4 px-4">{getSubscriptionBadge(service)}</td>
                      <td className="py-4 px-4">{getStatusBadge(service.is_active)}</td>
                      <td className="py-4 px-4">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => openEditModal(service)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Edit"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDelete(service.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-4 sm:p-6">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                {modalMode === 'create' ? 'Create New Service' : 'Edit Service'}
              </h3>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {formError && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                    {formError}
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Shop Name *
                    </label>
                    <input
                      type="text"
                      value={formData.shop_name}
                      onChange={(e) => setFormData({...formData, shop_name: e.target.value})}
                      className="input"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Owner Name *
                    </label>
                    <input
                      type="text"
                      value={formData.owner_name}
                      onChange={(e) => setFormData({...formData, owner_name: e.target.value})}
                      className="input"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      value={formData.email}
                      onChange={(e) => setFormData({...formData, email: e.target.value})}
                      className="input"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone *
                    </label>
                    <input
                      type="tel"
                      value={formData.phone}
                      onChange={(e) => setFormData({...formData, phone: e.target.value})}
                      className="input"
                      required
                    />
                  </div>

                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Address *
                    </label>
                    <textarea
                      value={formData.address}
                      onChange={(e) => setFormData({...formData, address: e.target.value})}
                      className="input"
                      rows="2"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subscription Duration
                    </label>
                    <input
                      type="number"
                      min="1"
                      value={formData.subscription_duration}
                      onChange={(e) => setFormData({...formData, subscription_duration: parseInt(e.target.value) || ''})}
                      className="input"
                      placeholder="e.g., 1, 3, 6"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Subscription Unit
                    </label>
                    <select
                      value={formData.subscription_unit}
                      onChange={(e) => setFormData({...formData, subscription_unit: e.target.value})}
                      className="input"
                    >
                      <option value="week">Week(s)</option>
                      <option value="month">Month(s)</option>
                      <option value="year">Year(s)</option>
                    </select>
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 btn btn-secondary"
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 btn btn-primary"
                    disabled={submitting}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin inline mr-2" />
                        {modalMode === 'create' ? 'Creating...' : 'Updating...'}
                      </>
                    ) : (
                      modalMode === 'create' ? 'Create Service' : 'Update Service'
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

export default SuperAdminDashboard;
