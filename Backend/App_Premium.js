
import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import FrameworkDetail from './components/FrameworkDetail';

// --- PLACEHOLDER COMPONENT FOR NEW ROUTES ---
const PlaceholderPage = ({ title }) => (
    <div className="p-8 animate-fade-in">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">{title}</h1>
        <div className="bg-white p-16 rounded-xl border border-gray-200 shadow-sm text-center">
            <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-6">
                <span className="text-3xl">🚧</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Under Construction</h3>
            <p className="text-gray-500 max-w-md mx-auto">
                The <b>{title}</b> module is linked and ready for development.
                Detailed views for this section will be implemented in the next phase.
            </p>
        </div>
    </div>
);

const ProtectedRoute = ({ children }) => {
    const { token, loading } = useAuth();

    if (loading) {
        return <div className="flex h-screen items-center justify-center text-gray-500">Loading verification...</div>;
    }

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

const ProtectedLayout = ({ children }) => {
    return (
        <div className="flex h-screen bg-gray-50">
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

                    {/* DASHBOARD */}
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

                    {/* FRAMEWORKS DETAIL */}
                    <Route
                        path="/frameworks/:id"
                        element={
                            <ProtectedRoute>
                                <ProtectedLayout>
                                    <FrameworkDetail />
                                </ProtectedLayout>
                            </ProtectedRoute>
                        }
                    />

                    {/* --- NEW PREMIUM ROUTES --- */}
                    {/* OVERVIEW */}
                    <Route path="/controls" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Controls" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/monitors" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Monitors" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/get-started" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Get Started" /></ProtectedLayout></ProtectedRoute>} />

                    {/* DOCUMENTS */}
                    <Route path="/documents" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Documents" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/policies" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Policies" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/risk" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Risk Management" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/vendors" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Vendors" /></ProtectedLayout></ProtectedRoute>} />

                    {/* REPORTS */}
                    <Route path="/frameworks" element={<ProtectedRoute><ProtectedLayout><Dashboard /></ProtectedLayout></ProtectedRoute>} /> {/* List View -> Dashboard for now */}
                    <Route path="/trust-report" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Trust Report" /></ProtectedLayout></ProtectedRoute>} />

                    {/* MANAGE */}
                    <Route path="/people" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="People" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/groups" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Groups" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/computers" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Computers" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/checklists" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Checklists" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/access" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Access" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/access-reviews" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Access Reviews" /></ProtectedLayout></ProtectedRoute>} />
                    <Route path="/settings" element={<ProtectedRoute><ProtectedLayout><PlaceholderPage title="Settings" /></ProtectedLayout></ProtectedRoute>} />

                    {/* FALLBACK */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
