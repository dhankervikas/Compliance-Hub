
import os

login_path = r"..\..\Frontend\src\components\Login.js"

content = r"""import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const { login, user, token } = useAuth(); // Log token too

  // DISABLED AUTO-REDIRECT FOR DEBUGGING
  // useEffect(() => {
  //     if (user) {
  //         console.log("[Login] User already authenticated.", user);
  //         // navigate('/dashboard', { replace: true });
  //     }
  // }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log("[Login] Submitting form...");
      console.log("[Login] Current context state - User:", user, "Token:", token);
      
      const result = await login(username, password);
      console.log("[Login] Login result:", result);
      
      if (result.success) {
        console.log("[Login] Success! Navigating to dashboard...");
        navigate('/dashboard');
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      console.error("[Login] Error:", err);
      setError('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">AssuRisk</h1>
          <p className="text-gray-600 mt-2">1.0 Debug Mode</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
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
      </div>
    </div>
  );
};

export default Login;
"""

try:
    with open(login_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Updated {os.path.abspath(login_path)}")
except Exception as e:
    print(f"ERROR: Failed to update file. {e}")
