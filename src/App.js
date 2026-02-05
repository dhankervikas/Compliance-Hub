import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import FrameworkDetail from './components/FrameworkDetail';
import SystemEffectiveness from './components/SystemEffectiveness';
import ReportsDashboard from './components/ReportsDashboard';
// import Settings from './components/Settings'; // REMOVED: Unused and causes folder collision
import StatementOfApplicability from './components/StatementOfApplicability';
import InitiationWizard from './components/AuditorPortal/InitiationWizard';
import AuditorDashboard from './components/AuditorPortal/AuditorDashboard';
import Policies from './components/Policies';
import PolicyDetail from './components/PolicyDetail';
import PrintLayout from './components/PrintLayout';
import Evidence from './components/Evidence';
import SettingsLayout from './components/Settings/SettingsLayout';
import SettingsForm from './components/Settings/SettingsForm';
import ContextPage from './components/ContextPage';
import UserManagement from './components/UserManagement';

import ErrorBoundary from './components/ErrorBoundary'; // Import ErrorBoundary

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

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
    const { token, user, loading } = useAuth();

    if (loading) {
        return <div className="flex h-screen items-center justify-center text-gray-500">Loading verification...</div>;
    }

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // Role-Based Access Control
    if (user) {
        const role = user.role || 'admin'; // Default to admin if missing

        // 1. Auditors attempting to access non-auditor pages
        if (role === 'auditor' && !window.location.pathname.startsWith('/auditor-portal')) {
            return <Navigate to="/auditor-portal/dashboard" replace />;
        }

        // 2. Strict Role Check (if allowedRoles prop provided)
        if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
            // If Admin tries to access Auditor page, maybe allow? Or redirect?
            // For now, let's keep it simple.
            // If strict check fails:
            return <Navigate to="/unauthorized" replace />;
        }
    }

    return children;
};

const ProtectedLayout = () => {
    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar />
            <div className="flex-1 overflow-auto ml-64">
                <Outlet />
            </div>
        </div>
    );
};

function App() {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <Router>
                    <Routes>
                        <Route path="/login" element={<Login />} />

                        <Route path="/login" element={<Login />} />

                        {/* MAIN APP LAYOUT (With Sidebar) */}
                        <Route
                            element={
                                <ProtectedRoute>
                                    <ProtectedLayout />
                                </ProtectedRoute>
                            }
                        >
                            {/* DASHBOARD */}
                            <Route path="/dashboard" element={<Dashboard />} />

                            {/* EFFECTIVENESS */}
                            <Route path="/effectiveness" element={<SystemEffectiveness />} />

                            {/* FRAMEWORKS */}
                            <Route path="/frameworks/:id" element={<FrameworkDetail />} />

                            {/* OVERVIEW */}
                            <Route path="/controls" element={<PlaceholderPage title="Controls" />} />
                            <Route path="/monitors" element={<PlaceholderPage title="Monitors" />} />
                            <Route path="/get-started" element={<PlaceholderPage title="Get Started" />} />

                            {/* DOCUMENTS */}
                            <Route path="/documents" element={<Evidence />} />
                            <Route path="/policies" element={<Policies />} />
                            <Route path="/policies/:id" element={<PolicyDetail />} />
                            <Route path="/risk" element={<PlaceholderPage title="Risk Management" />} />
                            <Route path="/vendors" element={<PlaceholderPage title="Vendors" />} />

                            {/* GOVERNANCE */}
                            <Route path="/governance/context" element={<ContextPage />} />

                            {/* SETTINGS MODULE */}
                            <Route path="/settings" element={<SettingsLayout />}>
                                <Route path=":section" element={<SettingsForm />} />
                            </Route>

                            {/* REPORTS */}
                            <Route path="/reports" element={<ReportsDashboard />} />
                            <Route path="/trust-report" element={<ReportsDashboard />} />

                            {/* MANAGE */}
                            <Route path="/people" element={<PlaceholderPage title="People" />} />
                            <Route path="/groups" element={<PlaceholderPage title="Groups" />} />
                            <Route path="/computers" element={<PlaceholderPage title="Computers" />} />
                            <Route path="/checklists" element={<PlaceholderPage title="Checklists" />} />
                            <Route path="/access" element={<PlaceholderPage title="Access" />} />
                            <Route path="/access-reviews" element={<PlaceholderPage title="Access Reviews" />} />

                            {/* SOA PREVIEW */}
                            <Route path="/soa-preview" element={<StatementOfApplicability />} />

                            {/* ADMIN USER MANAGEMENT */}
                            <Route path="/admin/users" element={<UserManagement />} />
                        </Route>

                        {/* PRINT LAYOUT (No Sidebar) */}
                        <Route
                            path="/print/policy/:id"
                            element={
                                <ProtectedRoute>
                                    <PrintLayout />
                                </ProtectedRoute>
                            }
                        />

                        {/* AUDITOR PORTAL (No Sidebar) */}
                        <Route
                            path="/auditor-portal"
                            element={
                                <ProtectedRoute>
                                    <InitiationWizard />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/auditor-portal/dashboard"
                            element={
                                <ProtectedRoute>
                                    <AuditorDashboard />
                                </ProtectedRoute>
                            }
                        />

                        {/* FALLBACK */}
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                </Router>
            </AuthProvider>
        </ErrorBoundary>
    );
}

export default App;
