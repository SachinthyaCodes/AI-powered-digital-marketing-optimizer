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
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Enhanced Header/Navbar */}
      <header className="bg-white/80 backdrop-blur-lg sticky top-0 z-50 border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 sm:h-20">
            {/* Logo and Brand */}
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 hover:rotate-3 transition-all duration-300">
                <ShieldCheck className="w-6 h-6 sm:w-7 sm:h-7 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  MarketMatic
                </h1>
                <p className="text-xs text-gray-500">{user?.company_name || 'Admin Dashboard'}</p>
              </div>
            </div>

            {/* Navigation Actions */}
            <div className="flex items-center gap-2 sm:gap-4">
              {/* User Info (Desktop) */}
              <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-gray-50 rounded-xl border border-gray-200">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">
                    {user?.full_name?.charAt(0) || 'A'}
                  </span>
                </div>
                <div className="text-left">
                  <p className="text-sm font-semibold text-gray-900">{user?.full_name}</p>
                  <p className="text-xs text-gray-500">Administrator</p>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-xl hover:from-red-600 hover:to-pink-600 transition-all shadow-md hover:shadow-lg transform hover:scale-105"
              >
                <LogOut className="w-4 h-4 sm:w-5 sm:h-5" />
                <span className="hidden sm:inline font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Welcome Section */}
        <div className="mb-8 animate-fade-in">
          <h2 className="text-2xl sm:text-3xl font-bold mb-2 text-gray-900">
            Welcome back, <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">{user?.full_name}</span>!
          </h2>
          <p className="text-gray-600 text-base">
            Manage your AI-powered digital marketing assistant
          </p>
        </div>

        {/* Service Info Card */}
        {loading ? (
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-10 w-10 border-4 border-indigo-200 border-t-indigo-600"></div>
            </div>
          </div>
        ) : serviceInfo ? (
          <div className="bg-gradient-to-br from-white to-indigo-50 rounded-2xl shadow-xl border border-indigo-100 p-6 sm:p-8 mb-8 transform hover:scale-[1.01] transition-all duration-300">
            <div className="flex flex-col sm:flex-row items-start justify-between gap-4 mb-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <Store className="w-7 h-7 text-white" />
                </div>
                <div>
                  <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-1">
                    {serviceInfo.shop_name}
                  </h3>
                  <p className="text-sm text-gray-600 font-medium">Service Information</p>
                </div>
              </div>
              {subscriptionStatus && (
                <div className={`px-4 py-2 rounded-full text-sm font-semibold shadow-md ${
                  subscriptionStatus.color === 'green' ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' :
                  subscriptionStatus.color === 'orange' ? 'bg-gradient-to-r from-orange-500 to-amber-500 text-white' :
                  subscriptionStatus.color === 'red' ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white' :
                  'bg-gray-200 text-gray-700'
                }`}>
                  {subscriptionStatus.text}
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start gap-3 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-100">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-md">
                  <Mail className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Email</p>
                  <p className="text-sm font-semibold text-gray-900">{serviceInfo.email}</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-100">
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-md">
                  <Phone className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Phone</p>
                  <p className="text-sm font-semibold text-gray-900">{serviceInfo.phone}</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-100">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md">
                  <MapPin className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Address</p>
                  <p className="text-sm font-semibold text-gray-900">{serviceInfo.address}</p>
                </div>
              </div>
              <div className="flex items-start gap-3 p-4 bg-white/60 backdrop-blur-sm rounded-xl border border-gray-100">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-xl flex items-center justify-center shadow-md">
                  <Calendar className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium mb-1">Subscription</p>
                  <p className="text-sm font-semibold text-gray-900">
                    {serviceInfo.subscription_duration} {serviceInfo.subscription_unit}
                    {serviceInfo.subscription_duration > 1 ? 's' : ''}
                    {subscriptionStatus?.days > 0 && ` (${subscriptionStatus.days} days left)`}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-2xl p-6 mb-8">
            <p className="text-yellow-800 font-medium">Unable to load service information</p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-8">
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl shadow-xl p-6 transform hover:scale-105 hover:-translate-y-1 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6" />
              </div>
              <TrendingUp className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-sm font-semibold opacity-90 mb-1">Total Customers</p>
            <p className="text-4xl font-bold">{stats.totalCustomers}</p>
          </div>

          <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-2xl shadow-xl p-6 transform hover:scale-105 hover:-translate-y-1 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6" />
              </div>
              <Activity className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-sm font-semibold opacity-90 mb-1">Active Chats</p>
            <p className="text-4xl font-bold">{stats.activeChats}</p>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-2xl shadow-xl p-6 transform hover:scale-105 hover:-translate-y-1 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6" />
              </div>
              <Clock className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-sm font-semibold opacity-90 mb-1">Monthly Messages</p>
            <p className="text-4xl font-bold">{stats.monthlyMessages}</p>
          </div>

          <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-2xl shadow-xl p-6 transform hover:scale-105 hover:-translate-y-1 transition-all duration-300">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <CheckCircle className="w-6 h-6" />
              </div>
              <TrendingUp className="w-5 h-5 opacity-70" />
            </div>
            <p className="text-sm font-semibold opacity-90 mb-1">Response Rate</p>
            <p className="text-4xl font-bold">{stats.responseRate}%</p>
          </div>
        </div>

        {/* Demo Chatbot Button */}
        {user?.service_id && (
          <div className="mb-8">
            <button
              onClick={() => navigate(`/demo/chat/${user.service_id}`)}
              className="w-full bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white rounded-2xl shadow-2xl px-6 sm:px-8 py-6 sm:py-7 hover:from-indigo-700 hover:via-purple-700 hover:to-pink-700 transition-all duration-300 flex items-center justify-between group border-none transform hover:scale-[1.02]"
            >
              <div className="flex items-center gap-4 sm:gap-6">
                <div className="w-14 h-14 sm:w-16 sm:h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all duration-300">
                  <MessageSquare className="w-7 h-7 sm:w-8 sm:h-8" />
                </div>
                <div className="text-left">
                  <div className="font-bold text-xl sm:text-2xl mb-1 flex items-center gap-2">
                    View Chatbot Demo
                    <Sparkles className="w-5 h-5 animate-pulse" />
                  </div>
                  <div className="text-sm text-white/90">See your AI assistant in action with SinLlama</div>
                </div>
              </div>
              <svg className="w-6 h-6 sm:w-7 sm:h-7 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mb-8">
          <button 
            onClick={() => navigate('/admin/bot-management')}
            className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl hover:border-indigo-200 transition-all duration-300 group text-left transform hover:scale-105 hover:-translate-y-1"
          >
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all shadow-lg">
                <MessageSquare className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1 text-base sm:text-lg group-hover:text-indigo-600 transition-colors">Chatbot Manager</h3>
                <p className="text-sm text-gray-600 leading-relaxed">Configure and train your AI chatbot</p>
              </div>
            </div>
          </button>

          <button className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl hover:border-green-200 transition-all duration-300 group text-left transform hover:scale-105 hover:-translate-y-1">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all shadow-lg">
                <Users className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1 text-base sm:text-lg group-hover:text-green-600 transition-colors">Customer Database</h3>
                <p className="text-sm text-gray-600 leading-relaxed">View and manage customer data</p>
              </div>
            </div>
          </button>

          <button 
            onClick={() => navigate('/admin/chat-analytics')}
            className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl hover:border-purple-200 transition-all duration-300 group text-left transform hover:scale-105 hover:-translate-y-1">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all shadow-lg">
                <BarChart3 className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1 text-base sm:text-lg group-hover:text-purple-600 transition-colors">Chat Analytics</h3>
                <p className="text-sm text-gray-600 leading-relaxed">Track chatbot performance and insights</p>
              </div>
            </div>
          </button>

          <button className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl hover:border-orange-200 transition-all duration-300 group text-left transform hover:scale-105 hover:-translate-y-1">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-red-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all shadow-lg">
                <Settings className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1 text-base sm:text-lg group-hover:text-orange-600 transition-colors">Service Settings</h3>
                <p className="text-sm text-gray-600 leading-relaxed">Customize your service preferences</p>
              </div>
            </div>
          </button>

          <button 
            onClick={() => navigate('/admin/vector-database')}
            className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl hover:border-blue-200 transition-all duration-300 group text-left transform hover:scale-105 hover:-translate-y-1">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all shadow-lg">
                <Activity className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1 text-base sm:text-lg group-hover:text-blue-600 transition-colors">Vector Database</h3>
                <p className="text-sm text-gray-600 leading-relaxed">Manage AI semantic search</p>
              </div>
            </div>
          </button>

          <button className="bg-white rounded-2xl shadow-lg border-2 border-gray-100 p-6 hover:shadow-2xl hover:border-pink-200 transition-all duration-300 group text-left transform hover:scale-105 hover:-translate-y-1">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-500 to-rose-600 rounded-2xl flex items-center justify-center group-hover:scale-110 group-hover:rotate-6 transition-all shadow-lg">
                <TrendingUp className="w-7 h-7 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-gray-900 mb-1 text-base sm:text-lg group-hover:text-pink-600 transition-colors">Marketing Tools</h3>
                <p className="text-sm text-gray-600 leading-relaxed">Engage and grow your audience</p>
              </div>
            </div>
          </button>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6 sm:p-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl flex items-center justify-center shadow-lg">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">Recent Activity</h3>
          </div>
          <div className="space-y-3">
            {[
              { action: 'New customer registered', time: '5 minutes ago', icon: Users, color: 'blue' },
              { action: 'Chatbot responded to 3 queries', time: '15 minutes ago', icon: MessageSquare, color: 'green' },
              { action: 'Service settings updated', time: '1 hour ago', icon: Settings, color: 'purple' },
              { action: 'Monthly report generated', time: '2 hours ago', icon: BarChart3, color: 'orange' },
            ].map((item, index) => (
              <div key={index} className="flex items-center gap-4 p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl hover:from-gray-100 hover:to-gray-50 transition-all cursor-pointer border border-gray-100 hover:border-gray-200 hover:shadow-md group">
                <div className={`w-12 h-12 bg-gradient-to-br ${
                  item.color === 'blue' ? 'from-blue-500 to-blue-600' :
                  item.color === 'green' ? 'from-green-500 to-green-600' :
                  item.color === 'purple' ? 'from-purple-500 to-purple-600' :
                  'from-orange-500 to-orange-600'
                } rounded-xl flex items-center justify-center shadow-md group-hover:scale-110 transition-transform`}>
                  <item.icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">{item.action}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{item.time}</p>
                </div>
                <svg className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
