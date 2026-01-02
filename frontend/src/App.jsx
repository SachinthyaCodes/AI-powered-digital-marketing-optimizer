import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import SuperAdminDashboard from './pages/SuperAdminDashboard';
import SuperAdminLogin from './pages/SuperAdminLogin';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import SMEHomePage from './pages/SMEHomePage';
import BotManagement from './pages/BotManagement';
import ChatAnalytics from './pages/ChatAnalytics';
import CustomerChat from './pages/CustomerChat';
import VectorDatabaseManager from './pages/VectorDatabaseManager';
import BusinessChatDemo from './pages/BusinessChatDemo';
import './index.css';

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/superadmin/login" element={<SuperAdminLogin />} />
          <Route path="/demo" element={<SMEHomePage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/superadmin/dashboard"
            element={
              <ProtectedRoute>
                <SuperAdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/bot-management"
            element={
              <ProtectedRoute>
                <BotManagement />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/chat-analytics"
            element={
              <ProtectedRoute>
                <ChatAnalytics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin/vector-database"
            element={
              <ProtectedRoute>
                <VectorDatabaseManager />
              </ProtectedRoute>
            }
          />
          <Route
            path="/chat/:serviceId"
            element={<CustomerChat />}
          />
          <Route
            path="/demo/chat/:serviceId"
            element={
              <ProtectedRoute>
                <BusinessChatDemo />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
