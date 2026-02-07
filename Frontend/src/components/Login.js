import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import config from '../config';
import SecurityStatusBadge from './SecurityStatusBadge';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login, user, loading: authLoading } = useAuth();

  useEffect(() => {
    if (user && !authLoading) {
      if (window.location.pathname !== '/login') return;

      if (user.username === 'admin') {
        navigate('/super-admin', { replace: true });
      } else {
        const tenantId = user.tenant_id || 'default';
        navigate(`/t/${tenantId}/dashboard`, { replace: true });
      }
    }
  }, [user, authLoading, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(username, password);

      if (result.success) {
        if (username === 'admin') {
          navigate('/super-admin');
        } else {
          const tenantId = result.user?.tenant_id || 'default';
          const target = localStorage.getItem('target_tenant_redirect');
          if (target) {
            localStorage.removeItem('target_tenant_redirect');
            navigate(target);
          } else {
            navigate(`/t/${tenantId}/dashboard`);
          }
        }
      } else {
        setError(result.error || 'Login failed');
        setLoading(false);
      }
    } catch (err) {
      setError('An error occurred. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AssuRisk</h1>
          <p className="text-gray-500 mt-2 font-medium">Multi-Tenant Secure Access</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded break-words text-sm">
              <strong>Error: </strong> {error}
              {(error?.includes("Network") || error?.includes("failed")) && (
                <div className="mt-2 text-xs text-gray-500">
                  Target: {config.API_BASE_URL}
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter username"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-gray-700 uppercase mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Enter password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
          >
            {loading ? 'Authenticating...' : 'Secure Login'}
          </button>
        </form>

        <SecurityStatusBadge />
      </div>
    </div>
  );
};

export default Login;