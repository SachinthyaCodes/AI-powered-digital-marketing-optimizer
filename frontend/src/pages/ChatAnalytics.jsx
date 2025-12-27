import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { MessageSquare, Users, Globe, TrendingUp, Clock, Star } from 'lucide-react';
import api from '../services/api';

const ChatAnalytics = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.service_id) {
      fetchAnalytics();
      fetchRecentSessions();
    }
  }, [user]);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get(`/chat/analytics?service_id=${user.service_id}`);
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics');
      console.error('Error fetching analytics:', err);
    }
  };

  const fetchRecentSessions = async () => {
    try {
      const response = await api.get(`/chat/sessions?service_id=${user.service_id}`);
      setSessions(response.data.sessions || []);
    } catch (err) {
      console.error('Error fetching sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const getIntentColor = (intent) => {
    const colors = {
      'product_inquiry': 'bg-blue-100 text-blue-800',
      'pricing': 'bg-green-100 text-green-800',
      'order_tracking': 'bg-yellow-100 text-yellow-800',
      'delivery_info': 'bg-purple-100 text-purple-800',
      'payment': 'bg-indigo-100 text-indigo-800',
      'complaint': 'bg-red-100 text-red-800',
      'greeting': 'bg-gray-100 text-gray-800',
      'general': 'bg-gray-100 text-gray-800'
    };
    return colors[intent] || colors.general;
  };

  const getLanguageFlag = (lang) => {
    const flags = {
      'en': '🇺🇸',
      'si': '🇱🇰',
      'ta': '🇱🇰',
      'mixed': '🌐'
    };
    return flags[lang] || '🌐';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-2">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Chat Analytics</h1>
          <p className="text-gray-600 mt-2">Monitor your chatbot performance and customer interactions</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Messages</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.total_messages || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Sessions</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.active_sessions || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Languages</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.language_distribution?.length || 0}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Intents</p>
                <p className="text-2xl font-bold text-gray-900">
                  {analytics?.intent_distribution?.length || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Language Distribution */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Language Distribution</h3>
            <div className="space-y-4">
              {analytics?.language_distribution?.map((item, index) => {
                const total = analytics.language_distribution.reduce((sum, lang) => sum + lang.count, 0);
                const percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0;
                
                return (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{getLanguageFlag(item._id)}</span>
                      <span className="font-medium text-gray-900">
                        {item._id === 'en' ? 'English' : 
                         item._id === 'si' ? 'Sinhala' : 
                         item._id === 'ta' ? 'Tamil' : 'Mixed'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">{item.count} messages</span>
                      <span className="text-sm font-medium text-gray-900">{percentage}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Intent Distribution */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Popular Topics</h3>
            <div className="space-y-3">
              {analytics?.intent_distribution?.map((item, index) => {
                const total = analytics.intent_distribution.reduce((sum, intent) => sum + intent.count, 0);
                const percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0;
                
                return (
                  <div key={index} className="flex items-center justify-between">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getIntentColor(item._id)}`}>
                      {item._id.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">{item.count}</span>
                      <span className="text-sm font-medium text-gray-900">{percentage}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Recent Sessions */}
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Chat Sessions</h3>
            
            {sessions.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <MessageSquare className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                <p>No chat sessions yet</p>
                <p className="text-sm">Start engaging with customers to see data here</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-2 text-sm font-medium text-gray-600">Customer</th>
                      <th className="text-left py-2 text-sm font-medium text-gray-600">Messages</th>
                      <th className="text-left py-2 text-sm font-medium text-gray-600">Last Activity</th>
                      <th className="text-left py-2 text-sm font-medium text-gray-600">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {sessions.slice(0, 10).map((session) => (
                      <tr key={session.session_id} className="hover:bg-gray-50">
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                              <span className="text-xs font-medium text-blue-600">
                                {session.user_name.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <span className="font-medium text-gray-900">
                              {session.user_name}
                            </span>
                          </div>
                        </td>
                        <td className="py-3 text-sm text-gray-600">
                          {session.message_count}
                        </td>
                        <td className="py-3 text-sm text-gray-600">
                          {new Date(session.last_activity).toLocaleString()}
                        </td>
                        <td className="py-3">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            session.status === 'active' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {session.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Period Note */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <Clock className="h-4 w-4 inline mr-1" />
          Data shown for the last 7 days
        </div>
      </div>
    </div>
  );
};

export default ChatAnalytics;