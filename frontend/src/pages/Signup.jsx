import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, User, Building2, AlertCircle, Loader2, Key, ShieldCheck } from 'lucide-react';

const Signup = () => {
  const navigate = useNavigate();
  const { signup } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    company_name: '',
    service_token: '',
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!formData.email || !formData.password || !formData.full_name) {
      setError('Please fill in all required fields');
      return;
    }

    if (isAdmin && !formData.service_token) {
      setError('Service token is required for admin registration');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);

    const result = await signup({
      email: formData.email,
      password: formData.password,
      full_name: formData.full_name,
      company_name: formData.company_name,
      service_token: isAdmin ? formData.service_token : undefined,
      is_admin: isAdmin,
    });

    setLoading(false);

    if (result.success) {
      // Redirect based on role
      if (result.user?.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/dashboard');
      }
    } else {
      setError(result.error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-50 px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
      <div className="max-w-md w-full">
        {/* Logo and Title */}
        <div className="text-center mb-6 sm:mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16 bg-primary-600 rounded-2xl mb-3 sm:mb-4">
            <span className="text-xl sm:text-2xl font-bold text-white">M</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
          <p className="text-gray-600">Join MarketMatic and grow your business</p>
        </div>

        {/* Signup Form */}
        <div className="card">
          {/* Admin Toggle */}
          <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className={`w-5 h-5 ${isAdmin ? 'text-blue-600' : 'text-gray-400'}`} />
                <span className="font-medium text-gray-900">Register as Admin</span>
              </div>
              <button
                type="button"
                onClick={() => setIsAdmin(!isAdmin)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  isAdmin ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    isAdmin ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            {isAdmin && (
              <p className="text-xs text-blue-700 mt-2">
                You'll need a valid service token provided by your service administrator
              </p>
            )}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
            {/* Error Message */}
            {error && (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {/* Full Name */}
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="john@company.com"
                  required
                />
              </div>
            </div>

            {/* Company Name */}
            <div>
              <label htmlFor="company_name" className="block text-sm font-medium text-gray-700 mb-2">
                Company Name (Optional)
              </label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  id="company_name"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="Your Company"
                />
              </div>
            </div>

            {/* Service Token (Only for Admin) */}
            {isAdmin && (
              <div>
                <label htmlFor="service_token" className="block text-sm font-medium text-gray-700 mb-2">
                  Service Token <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    id="service_token"
                    name="service_token"
                    value={formData.service_token}
                    onChange={handleChange}
                    className="input pl-11 font-mono text-sm"
                    placeholder="Enter your service token"
                    required={isAdmin}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Token provided by super administrator to verify service ownership
                </p>
              </div>
            )}

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="••••••••"
                  required
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Must be at least 6 characters</p>
            </div>

            {/* Confirm Password */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password <span className="text-red-500">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary py-3 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Terms */}
        <p className="text-center text-xs text-gray-500 mt-6">
          By creating an account, you agree to our{' '}
          <a href="#" className="text-primary-600 hover:underline">Terms of Service</a> and{' '}
          <a href="#" className="text-primary-600 hover:underline">Privacy Policy</a>
        </p>
      </div>
    </div>
  );
};

export default Signup;
