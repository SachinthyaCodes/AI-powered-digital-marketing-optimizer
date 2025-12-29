import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { 
  LogOut, Users, MessageSquare, TrendingUp, Settings,
  ShieldCheck, Store, Mail, Phone, MapPin, Calendar,
  BarChart3, Activity, Clock, CheckCircle, Sparkles
} from 'lucide-react';
import api from '../services/api';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [serviceInfo, setServiceInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  // Debug: Log user object
  useEffect(() => {
    console.log('Admin Dashboard - User object:', user);
    console.log('Service ID:', user?.service_id);
  }, [user]);
  const [stats, setStats] = useState({
    totalCustomers: 0,
    activeChats: 0,
    monthlyMessages: 0,
    responseRate: 0
  });

  useEffect(() => {
    fetchServiceInfo();
    // In a real app, fetch actual stats from backend
    setStats({
      totalCustomers: 127,
      activeChats: 8,
      monthlyMessages: 1543,
      responseRate: 94.5
    });
  }, []);

  const fetchServiceInfo = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/services/my-service');
      setServiceInfo(response.data.service);
    } catch (error) {
      console.error('Error fetching service info:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getSubscriptionStatus = () => {
    if (!serviceInfo?.subscription_end) {
      return { text: 'No Subscription', color: 'gray', days: 0 };
    }

    const endDate = new Date(serviceInfo.subscription_end);
    const today = new Date();
    const daysLeft = Math.ceil((endDate - today) / (1000 * 60 * 60 * 24));

    if (daysLeft < 0) {
      return { text: 'Expired', color: 'red', days: 0 };
    } else if (daysLeft < 7) {
      return { text: 'Expiring Soon', color: 'orange', days: daysLeft };
    } else {
      return { text: 'Active', color: 'green', days: daysLeft };
    }
  };

  const subscriptionStatus = serviceInfo ? getSubscriptionStatus() : null;

  return (
    <div className="min-h-screen gradient-bg">
      {/* Header */}
      <header className="glass-card sticky top-0 z-20 border-b border-gray-200/50 animate-slide-in-left" style={{ padding: '0' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-glow transform hover:scale-110 transition-all duration-300">
                <ShieldCheck className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div>
                <h1 className="text-base sm:text-lg font-bold">
                  <span className="text-gradient">Admin Panel</span>
                </h1>
                <p className="text-xs text-gray-600">{user?.company_name || 'Service Management'}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-white/60 rounded-xl transition-all hover:shadow-md"
            >
              <LogOut className="w-5 h-5" />
              <span className="hidden sm:inline font-medium">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-6 sm:mb-8 animate-fade-in-up">
          <h2 className="text-xl sm:text-2xl font-bold mb-2">
            Welcome back, <span className="text-gradient">{user?.full_name}</span>!
          </h2>
          <p className="text-gray-600">
            Manage your service and engage with your customers
          </p>
        </div>

        {/* Service Info Card */}
        {loading ? (
          <div className="card mb-8">
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          </div>
        ) : serviceInfo ? (
          <div className="glass-card mb-6 sm:mb-8 bg-gradient-to-r from-blue-50/50 to-indigo-50/50 border-blue-200/50 animate-slide-in-right">
            <div className="flex flex-col sm:flex-row items-start justify-between gap-3 sm:gap-0 mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Store className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-1">
                    {serviceInfo.shop_name}
                  </h3>
                  <p className="text-sm text-gray-600 font-medium">Service Information</p>
                </div>
              </div>
              {subscriptionStatus && (
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  subscriptionStatus.color === 'green' ? 'bg-green-100 text-green-700' :
                  subscriptionStatus.color === 'orange' ? 'bg-orange-100 text-orange-700' :
                  subscriptionStatus.color === 'red' ? 'bg-red-100 text-red-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {subscriptionStatus.text}
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-start gap-3">
                <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-xs text-gray-500">Email</p>
                  <p className="text-sm font-medium text-gray-900">{serviceInfo.email}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-xs text-gray-500">Phone</p>
                  <p className="text-sm font-medium text-gray-900">{serviceInfo.phone}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-xs text-gray-500">Address</p>
                  <p className="text-sm font-medium text-gray-900">{serviceInfo.address}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-xs text-gray-500">Subscription</p>
                  <p className="text-sm font-medium text-gray-900">
                    {serviceInfo.subscription_duration} {serviceInfo.subscription_unit}
                    {serviceInfo.subscription_duration > 1 ? 's' : ''}
                    {subscriptionStatus?.days > 0 && ` (${subscriptionStatus.days} days left)`}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card mb-8 bg-yellow-50 border-yellow-200">
            <p className="text-yellow-800">Unable to load service information</p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div className="stat-card border-l-blue-500 bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-glow animate-fade-in-up" style={{ animationDelay: '0.1s', opacity: 0, animationFillMode: 'forwards' }}>
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6" />
              </div>
              <TrendingUp className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-xs sm:text-sm font-semibold opacity-90 mb-1">Total Customers</p>
            <p className="text-3xl sm:text-4xl font-bold">{stats.totalCustomers}</p>
          </div>

          <div className="stat-card border-l-green-500 bg-gradient-to-br from-green-500 to-green-600 text-white shadow-glow animate-fade-in-up" style={{ animationDelay: '0.2s', opacity: 0, animationFillMode: 'forwards' }}>
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6" />
              </div>
              <Activity className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-xs sm:text-sm font-semibold opacity-90 mb-1">Active Chats</p>
            <p className="text-3xl sm:text-4xl font-bold">{stats.activeChats}</p>
          </div>

          <div className="stat-card border-l-purple-500 bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-glow-purple animate-fade-in-up" style={{ animationDelay: '0.3s', opacity: 0, animationFillMode: 'forwards' }}>
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6" />
              </div>
              <Clock className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-xs sm:text-sm font-semibold opacity-90 mb-1">Monthly Messages</p>
            <p className="text-3xl sm:text-4xl font-bold">{stats.monthlyMessages}</p>
          </div>

          <div className="stat-card border-l-orange-500 bg-gradient-to-br from-orange-500 to-orange-600 text-white shadow-glow animate-fade-in-up" style={{ animationDelay: '0.4s', opacity: 0, animationFillMode: 'forwards' }}>
            <div className="flex items-center justify-between mb-3">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6" />
              </div>
              <TrendingUp className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-xs sm:text-sm font-semibold opacity-90 mb-1">Response Rate</p>
            <p className="text-3xl sm:text-4xl font-bold">{stats.responseRate}%</p>
          </div>
        </div>

        {/* Demo Chatbot Button */}
        {user?.service_id && (
          <div className="mb-6 animate-fade-in-up" style={{ animationDelay: '0.5s', opacity: 0, animationFillMode: 'forwards' }}>
            <button
              onClick={() => navigate(`/demo/chat/${user.service_id}`)}
              className="w-full glass-card bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-5 hover:from-indigo-700 hover:to-purple-700 shadow-glow-purple flex items-center justify-between group border-none"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <MessageSquare className="w-7 h-7" />
                </div>
                <div className="text-left">
                  <div className="font-bold text-xl mb-1">View Chatbot Demo</div>
                  <div className="text-sm text-indigo-100">See your AI assistant in action with SinLlama</div>
                </div>
              </div>
              <svg className="w-6 h-6 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <button 
            onClick={() => navigate('/admin/bot-management')}
            className="feature-card group text-left"
          >
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all shadow-lg flex-shrink-0">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base group-hover:text-blue-600 transition-colors">Chatbot Manager</h3>
                <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">Configure and train your AI chatbot</p>
              </div>
            </div>
          </button>

          <button className="feature-card text-left">
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all shadow-lg flex-shrink-0">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base group-hover:text-green-600 transition-colors">Customer Database</h3>
                <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">View and manage customer data</p>
              </div>
            </div>
          </button>

          <button 
            onClick={() => navigate('/admin/chat-analytics')}
            className="feature-card text-left">
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all shadow-lg flex-shrink-0">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base group-hover:text-purple-600 transition-colors">Chat Analytics</h3>
                <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">Track chatbot performance and insights</p>
              </div>
            </div>
          </button>

          <button className="feature-card text-left">
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all shadow-lg flex-shrink-0">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base group-hover:text-orange-600 transition-colors">Service Settings</h3>
                <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">Customize your service preferences</p>
              </div>
            </div>
          </button>

          <button 
            onClick={() => navigate('/admin/vector-database')}
            className="feature-card text-left">
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all shadow-lg flex-shrink-0">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base group-hover:text-indigo-600 transition-colors">Vector Database</h3>
                <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">Manage AI semantic search</p>
              </div>
            </div>
          </button>

          <button className="feature-card text-left">
            <div className="relative z-10 flex items-center gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-pink-500 to-pink-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-3 transition-all shadow-lg flex-shrink-0">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div className="min-w-0">
                <h3 className="font-bold text-gray-900 mb-1 text-sm sm:text-base group-hover:text-pink-600 transition-colors">Marketing Tools</h3>
                <p className="text-xs sm:text-sm text-gray-600 leading-relaxed">Engage and grow your audience</p>
              </div>
            </div>
          </button>
        </div>

        {/* Recent Activity */}
        <div className="card animate-fade-in-up" style={{ animationDelay: '0.6s', opacity: 0, animationFillMode: 'forwards' }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-purple-500 rounded-xl flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <h3 className="text-base sm:text-lg font-bold text-gray-900">Recent Activity</h3>
          </div>
          <div className="space-y-3">
            {[
              { action: 'New customer registered', time: '5 minutes ago', icon: Users, color: 'blue' },
              { action: 'Chatbot responded to 3 queries', time: '15 minutes ago', icon: MessageSquare, color: 'green' },
              { action: 'Service settings updated', time: '1 hour ago', icon: Settings, color: 'purple' },
              { action: 'Monthly report generated', time: '2 hours ago', icon: BarChart3, color: 'orange' },
            ].map((item, index) => (
              <div key={index} className="flex items-center gap-3 p-4 bg-gradient-to-r from-gray-50 to-transparent rounded-xl hover:from-gray-100 transition-all cursor-pointer group">
                <div className={`w-10 h-10 bg-gradient-to-br from-${item.color}-500 to-${item.color}-600 rounded-xl flex items-center justify-center shadow-md group-hover:scale-110 transition-transform`}>
                  <item.icon className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">{item.action}</p>
                  <p className="text-xs text-gray-500">{item.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
