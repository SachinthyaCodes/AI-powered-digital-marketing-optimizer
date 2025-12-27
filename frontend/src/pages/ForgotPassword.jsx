import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, AlertCircle, CheckCircle, Loader2, ArrowLeft } from 'lucide-react';
import api from '../services/api';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (!email) {
      setError('Please enter your email address');
      return;
    }

    setLoading(true);

    try {
      await api.post('/api/auth/forgot-password', { email });
      setSuccess(true);
      setEmail('');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
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
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">Forgot Password</h1>
          <p className="text-gray-600 text-sm sm:text-base">Enter your email to receive a password reset link</p>
        </div>

        {/* Form Card */}
        <div className="card">
          {success ? (
            <div className="text-center py-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Check Your Email</h3>
              <p className="text-sm text-gray-600 mb-6">
                If an account exists with that email, we've sent you a password reset link. 
                Please check your inbox and spam folder.
              </p>
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium text-sm"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-5">
              {/* Error Message */}
              {error && (
                <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <p className="text-sm">{error}</p>
                </div>
              )}

              {/* Info Message */}
              <div className="flex items-start gap-2 p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700">
                <Mail className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">
                  Enter the email address associated with your account and we'll send you a link to reset your password.
                </p>
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="input pl-11"
                    placeholder="john@company.com"
                    required
                    autoFocus
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
                    Sending...
                  </>
                ) : (
                  'Send Reset Link'
                )}
              </button>
            </form>
          )}

          {/* Back to Login */}
          {!success && (
            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Login
              </Link>
            </div>
          )}
        </div>

        {/* Help Text */}
        <p className="text-center text-xs text-gray-500 mt-6">
          Need help? Contact support at{' '}
          <a href="mailto:support@marketmatic.com" className="text-primary-600 hover:underline">
            support@marketmatic.com
          </a>
        </p>
      </div>
    </div>
  );
};

export default ForgotPassword;
