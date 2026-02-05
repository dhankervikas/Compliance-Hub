import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import config from '../config';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

// Use environment variable for API URL, fallback to localhost for dev

const API_BASE_URL = config.API_BASE_URL.replace('/api/v1', ''); // AuthContext uses base URL without /api/v1 sometimes? Let's check usage.

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Configure axios defaults
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          console.log("[AuthContext] Loading user from token...");
          // Verify token and get user details
          const response = await axios.get(`${API_BASE_URL}/api/v1/auth/me`);
          console.log("[AuthContext] User loaded:", response.data);
          setUser(response.data);
        } catch (err) {
          console.error("[AuthContext] Failed to load user from existing token:", err);
          logout();
        }
      }
      setLoading(false);
    };

    // Global 401 Interceptor
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response && error.response.status === 401) {
          console.warn("[AuthContext] 401 Unauthorized detected. Logging out...");
          logout();
        }
        return Promise.reject(error);
      }
    );

    loadUser();

    // Cleanup interceptor on unmount/token change
    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [token]);

  const login = async (username, password) => {
    setError(null);
    console.log("[AuthContext] Attempting login for:", username);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      console.log(`[AuthContext] Sending POST to ${API_BASE_URL}/api/v1/auth/login...`);
      const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      console.log("[AuthContext] Login response received:", response);

      const { access_token } = response.data;
      if (!access_token) {
        console.error("[AuthContext] ERROR: No access_token in response data!", response.data);
        throw new Error("No access token received");
      }
      console.log("[AuthContext] Token extracted.");

      localStorage.setItem('token', access_token);
      setToken(access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      // Fetch user data immediately after login
      console.log("[AuthContext] Fetching user profile (/me)...");
      const userResponse = await axios.get(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      console.log("[AuthContext] User profile received:", userResponse.data);
      setUser(userResponse.data);

      return { success: true };
    } catch (err) {
      console.error("[AuthContext] Login process failed:", err);
      let msg = err.response?.data?.detail || "Login failed";
      if (typeof msg === 'object') {
        try {
          msg = JSON.stringify(msg);
        } catch (e) {
          msg = "Login failed (Complex Error)";
        }
      }
      console.error("[AuthContext] Error message:", msg);
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const logout = () => {
    console.log("[AuthContext] Logging out...");
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    login,
    logout,
    loading,
    error
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};