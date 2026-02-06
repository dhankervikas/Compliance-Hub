import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import SecurityStatusBadge from './SecurityStatusBadge';
import config from '../config';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const { login, user, loading: authLoading } = useAuth();

  // Redirect if already logged in or after successful login
  useEffect(() => {
    console.log("[Login] Auth state:", { user, authLoading });
    if (user && !authLoading) {
      const isTenantContext = window.location.pathname.includes('/t/');

      // Only redirect if we're actually on /login to prevent loops
      if (window.location.pathname !== '/login') return;

      if (user.username === 'admin' && !isTenantContext) {
        console.log("[Login] Superadmin detected. Redirecting to Workspace Selection...");
        navigate('/super-admin', { replace: true });
      } else if (!isTenantContext) {
        const tenantId = user.tenant_id || 'default';
        console.log("[Login] Standard user. Redirecting to Dashboard...");
        navigate(`/t/${tenantId}/dashboard`, { replace: true });
      }
    }
  }, [user, authLoading, navigate]);
        // Only redirect standard users if they are not already in deep link
        const tenantId = user.tenant_id || 'default';
        console.log("[Login] Standard user. Redirecting to Dashboard...");
        navigate(`/t/${tenantId}/dashboard`, { replace: true });
      }
    }
  }, [user, authLoading, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log("[Login] Submitting login...");
      const result = await login(username, password);
      console.log("[Login] Result:", result);

      if (result.success) {
        console.log("[Login] Login success. Checking role...");
        // Check if user is default tenant admin to redirect to workspaces
        // We need to parse the token or rely on user object if available immediately.
        // Assuming 'user' state updates or using result.user if passed back.
        // But context updates user asynchronously usually. 
        // Let's decode token or just basic check.
        // Actually, let's navigate to home, and let generic Auth redirection handle it?
        // No, AuthContext usually just sets state.

        if (username === 'admin') {
          console.log("[Login] Superadmin detected. Redirecting to Workspace Selection...");
          navigate('/super-admin');
        } else {
          // If user object has tenant_id, use it. Otherwise, fallback or check localStorage for target redirect.
          // For now, assuming standard users have tenant_id in their profile.
          const tenantId = result.user?.tenant_id || 'default';
          console.log(`[Login] Standard user. Redirecting to Tenant Dashboard (${tenantId})...`);

          // Check for deep link redirect
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
      console.error("[Login] Unexpected error:", err);
      setError('An error occurred. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AssuRisk</h1>
          <p className="text-gray-600 mt-2">Compliance Platform v2.1</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded break-words">
              <strong>Error: </strong> {error}
              {(error?.includes("Network") || error?.includes("failed")) && (
                <div className="mt-2 text-xs text-gray-500">
                  Target: {config.API_BASE_URL}
                </div>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <SecurityStatusBadge />

      </div>
    </div >
  );
};

export default Login;