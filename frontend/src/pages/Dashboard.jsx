import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, Building2, Mail, Calendar } from 'lucide-react';
import SimpleChatWidget, { ChatButton } from '../components/SimpleChatWidget';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isChatOpen, setIsChatOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <span className="text-lg sm:text-xl font-bold text-white">M</span>
              </div>
              <h1 className="text-lg sm:text-xl font-bold text-gray-900">MarketMatic</h1>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 sm:px-4 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4 sm:w-5 sm:h-5" />
              <span className="hidden sm:inline text-sm sm:text-base">Logout</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-6 sm:mb-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name}!
          </h2>
          <p className="text-gray-600">
            Here's what's happening with your MarketMatic account today.
          </p>
        </div>

        {/* User Info Card */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6 mb-6 sm:mb-8">
          <div className="lg:col-span-2">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <User className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Full Name</p>
                    <p className="text-base font-medium text-gray-900">{user?.full_name}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Email Address</p>
                    <p className="text-base font-medium text-gray-900">{user?.email}</p>
                  </div>
                </div>
                {user?.company_name && (
                  <div className="flex items-start gap-3">
                    <Building2 className="w-5 h-5 text-gray-400 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-500">Company</p>
                      <p className="text-base font-medium text-gray-900">{user?.company_name}</p>
                    </div>
                  </div>
                )}
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Member Since</p>
                    <p className="text-base font-medium text-gray-900">
                      {new Date(user?.created_at).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="space-y-6">
            <div className="card bg-gradient-to-br from-primary-500 to-primary-600 text-white">
              <h4 className="text-sm font-medium opacity-90 mb-2">Account Status</h4>
              <p className="text-2xl font-bold">Active</p>
            </div>
            <div className="card">
              <h4 className="text-sm font-medium text-gray-500 mb-2">Chatbot Status</h4>
              <p className="text-2xl font-bold text-gray-900">Ready</p>
            </div>
          </div>
        </div>

        {/* Demo Chatbot Button */}
        {user?.service_id && (
          <div className="mb-6">
            <button
              onClick={() => navigate(`/demo/chat/${user.service_id}`)}
              className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-3 group"
            >
              <MessageSquare className="w-6 h-6 group-hover:scale-110 transition-transform" />
              <div className="text-left">
                <div className="font-bold text-lg">View Chatbot Demo</div>
                <div className="text-sm text-indigo-100">See your AI assistant in action with SinLlama</div>
              </div>
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        )}

        {/* Features Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          <div className="card hover:shadow-md transition-shadow cursor-pointer">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-primary-100 rounded-xl flex items-center justify-center mb-3 sm:mb-4">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-1 sm:mb-2">AI Chatbot</h3>
            <p className="text-gray-600 text-xs sm:text-sm">Engage with your customers using our intelligent chatbot</p>
          </div>

          <div className="card hover:shadow-md transition-shadow cursor-pointer">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-green-100 rounded-xl flex items-center justify-center mb-3 sm:mb-4">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-1 sm:mb-2">Analytics</h3>
            <p className="text-gray-600 text-xs sm:text-sm">Track your business performance and insights</p>
          </div>

          <div className="card hover:shadow-md transition-shadow cursor-pointer">
            <div className="w-10 h-10 sm:w-12 sm:h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-3 sm:mb-4">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-1 sm:mb-2">Settings</h3>
            <p className="text-gray-600 text-xs sm:text-sm">Customize your MarketMatic experience</p>
          </div>
        </div>
      </main>

      {/* Chat Widget */}
      {user?.service_id && (
        <>
          <SimpleChatWidget 
            serviceId={user.service_id} 
            isOpen={isChatOpen}
            onClose={() => setIsChatOpen(false)}
          />
          {!isChatOpen && (
            <ChatButton onClick={() => setIsChatOpen(true)} />
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;
