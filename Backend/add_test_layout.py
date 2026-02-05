
import os

app_path = r"..\..\Frontend\src\App.js"

content = r"""import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';

// BYPASSING PROTECTED ROUTE FOR DEBUGGING
const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAuth();
  console.log("[ProtectedRoute] BYPASS MODE. Token:", token ? "Exists" : "Missing");
  return children; 
};

// SIMPLE TEST DASHBOARD
const TestDashboard = () => {
    return (
        <div style={{ padding: '50px', textAlign: 'center' }}>
            <h1>TEST DASHBOARD WORKS</h1>
            <p>If you see this, routing is fine.</p>
        </div>
    );
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

const DebugRouter = ({ children }) => {
  const location = useLocation();
  useEffect(() => {
    console.log("[Router] Route changed to:", location.pathname);
  }, [location]);
  return children;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <DebugRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            
            {/* REAL DASHBOARD */}
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

            {/* TEST 1: RAW TEST */}
            <Route path="/test" element={<TestDashboard />} />

            {/* TEST 2: SIDEBAR + TEST */}
            <Route path="/test-layout" element={
                <ProtectedLayout>
                    <TestDashboard />
                </ProtectedLayout>
            } />

            {/* Redirect root to dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </DebugRouter>
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
