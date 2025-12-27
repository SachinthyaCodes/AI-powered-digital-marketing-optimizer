import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Role-based routing
  const userRole = user?.role;

  // Prevent non-superadmins from accessing superadmin routes
  if (location.pathname.startsWith('/superadmin') && userRole !== 'superadmin') {
    return <Navigate to={userRole === 'admin' ? '/admin/dashboard' : '/dashboard'} replace />;
  }

  // Prevent non-admins from accessing admin routes
  if (location.pathname.startsWith('/admin') && userRole !== 'admin') {
    return <Navigate to={userRole === 'superadmin' ? '/superadmin/dashboard' : '/dashboard'} replace />;
  }

  // Redirect users to their appropriate dashboard
  if (location.pathname === '/dashboard') {
    if (userRole === 'superadmin') {
      return <Navigate to="/superadmin/dashboard" replace />;
    } else if (userRole === 'admin') {
      return <Navigate to="/admin/dashboard" replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
