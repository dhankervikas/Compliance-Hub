// src/contexts/AuthContext.js
import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI } from '../services/api';

// Create the context
const AuthContext = createContext(null);

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (authAPI.isAuthenticated()) {
          // Try to fetch current user from API
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
        } else {
          // No token found
          setUser(null);
        }
      } catch (err) {
        console.error('Auth check failed:', err);
        // Token might be invalid
        authAPI.logout();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (username, password) => {
    try {
      setError(null);
      setLoading(true);
      const response = await authAPI.login(username, password);
      setUser(response.user);
      return { success: true };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (username, email, password) => {
    try {
      setError(null);
      setLoading(true);
      const user = await authAPI.register(username, email, password);
      // Auto-login after registration
      await login(username, password);
      return { success: true, user };
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    authAPI.logout();
    setUser(null);
  };

  // Refresh user data
  const refreshUser = async () => {
    try {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      console.error('Failed to refresh user:', err);
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};