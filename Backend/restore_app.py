
import os

app_path = r"..\..\Frontend\src\App.js"

content = r"""import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';

const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  
  if (loading) {
    return <div className="flex h-screen items-center justify-center">Loading verification...</div>;
  }
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

const ProtectedLayout = ({ children }) => {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 overflow-auto ml-64">
        {children}
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <ProtectedLayout>
                  <Dashboard />
                </ProtectedLayout>
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
"""

try:
    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Updated {os.path.abspath(app_path)}")
except Exception as e:
    print(f"ERROR: Failed to update file. {e}")
